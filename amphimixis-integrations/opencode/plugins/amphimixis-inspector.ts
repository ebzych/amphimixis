import type { Plugin } from '@opencode-ai/plugin';
import type { OpencodeClient, Part } from '@opencode-ai/sdk';
import { Mutex } from 'async-mutex';
import { writeFileSync } from 'fs';
import InspectorGeneral from 'inspector_general';
import assert from 'node:assert/strict';

const AmphimixisInspector: Plugin = async ({ client }) => {
  client.app.log({
    body: {
      service: 'amphimixis-inspector',
      level: 'info',
      message: 'AIP: Amphimixis-Inspector plugin (AIP) is initialized',
    }
  });
  return {
    event: async ({ event }) => {
      if (event.type === 'message.part.updated') {
        const msgPart = event.properties.part;
        const sessionID = msgPart.sessionID;

        WrapperForOpencode.inspectSubtaskSession(client, sessionID, msgPart);

        if (msgPart.type === 'text') {
          await WrapperForOpencode.sessionMtx.runExclusive(
            async () => {
              if (!(sessionID in WrapperForOpencode.sessions)) {
                WrapperForOpencode.sessions[sessionID] =
                {
                  attemptCount: 0,
                  inspectionStatus: InspectionStatus.NOT_INSPECTED,
                  lastMessageText: undefined,
                };
              }
              WrapperForOpencode.sessions[sessionID]
                .lastMessageText = msgPart.text;
            }
          )
        }

        WrapperForOpencode.inspectMainSession(client, sessionID, msgPart);
      }
    }
  };
};

export default AmphimixisInspector;

enum InspectionStatus {
  NOT_INSPECTED,
  OK,
  TO_FIX,
}

type SessionData = {
  attemptCount: number,
  inspectionStatus: InspectionStatus,
  lastMessageText: string | undefined,
  parent?: string,
}

class WrapperForOpencode {
  static readonly DEFAULT_PROVIDER = 'opencode';
  static readonly DEFAULT_MODEL = 'big-pickle';
  static readonly ORCHESTRATOR_AGENT_NAME = 'amphimixis';

  static sessions: Record<string, SessionData> = {};
  static sessionMtx: Mutex = new Mutex();
  static readonly MAX_ATTEMPTS_FORMAL_INSPECTION_PER_SESSION: number = 5;

  static {
    assert(
      WrapperForOpencode.MAX_ATTEMPTS_FORMAL_INSPECTION_PER_SESSION > 0,
      'Expected positive number of attempts'
    );
  }

  static async inspectSubtaskSession(client: OpencodeClient, sessionID: string, msgPart: Part) {
    if (
      msgPart.type === 'tool'
      && msgPart.tool === 'task'
      && String(msgPart.state.input.subagent_type).match(/^amphimixis-.*/i)
      && msgPart.state.input.subagent_type !== 'amphimixis-inspector'
      && msgPart.state.status === 'completed'
    ) {
      client.app.log({
        body: {
          service: 'amphimixis-inspector',
          level: 'debug',
          message: 'Subtask is been inspecting now',
        }
      });
      // get subagent sessionID
      const subSessionID = msgPart.state.metadata?.sessionID;
      if (subSessionID === undefined)
        return;
      WrapperForOpencode.callInspectorForAgentSession(
        client,
        sessionID,
        String(subSessionID),
        String(msgPart.state.input.subagent_type),
      );
    }
  }

  static async inspectMainSession(
    client: OpencodeClient,
    sessionID: string,
    msgPart: Part,
  ) {
    const isWorkFinished = await WrapperForOpencode.sessionMtx.runExclusive(
      () => {
        if (!(sessionID in WrapperForOpencode.sessions)) {
          WrapperForOpencode.sessions[sessionID] = {
            attemptCount: 0,
            inspectionStatus: InspectionStatus.NOT_INSPECTED,
            lastMessageText: undefined,
          };
        }
        return WrapperForOpencode.sessions[sessionID]
          .lastMessageText
          && WrapperForOpencode.sessions[sessionID]
            .lastMessageText.match('WORK ON THE .*? IS COMPLETED');
      });
    if (
      msgPart.type === 'step-finish'
      && isWorkFinished
      && await WrapperForOpencode.isAttemptAvailable(sessionID)
    ) {
      client.app.log({
        body: {
          service: 'amphimixis-inspector',
          level: 'debug',
          message: 'AIP: inspect main task',
        }
      });

      client.app.log({
        body: {
          service: 'amphimixis-inspector',
          level: 'debug',
          message: 'AIP: call Inspector for main task',
        }
      });
      WrapperForOpencode.callInspectorForAgentSession(
        client,
        sessionID,
        sessionID,
      );

      client.app.log({
        body: {
          service: 'amphimixis-inspector',
          level: 'debug',
          message: 'AIP: report content inspecting',
        }
      });
      const [isSuccessful, inspectOutput] = InspectorGeneral.inspect();
      if (!isSuccessful) {
        WrapperForOpencode.sendPrompt(
          client,
          sessionID,
          'The work on the project has not been completed.'
          + ' Check yourself to completing all tasks.\n\n'
          + inspectOutput,
          WrapperForOpencode.ORCHESTRATOR_AGENT_NAME,
        );
      }
    }
  }

  static async getAllSessionText(
    client: OpencodeClient,
    sessionId: string,
    agent?: string,
  ) {
    const response = await client.session.messages({
      path: { id: sessionId }
    });

    let textContent: string = '';
    if (agent)
      textContent += `Agent: ${agent}\n\n`;

    // map through messages and extract text-based components
    textContent += response.data?.map(message => {
      if (!message.parts) return "";

      let output: string[] = [];
      for (const part of message.parts) {
        switch (part.type) {
          case 'text':
            output.push('# Text message\n');
            output.push(part.text + '\n');
            break;
          case 'reasoning':
            output.push('# Reasoning message\n');
            output.push(part.text + '\n');
            break;
          case 'tool':
            output.push('# Tool calling\n');
            output.push(JSON.stringify(part) + '\n');
            break;
        }
      }
      return output.join('\n');
    }).join("\n\n");

    return textContent;
  }

  static sendPrompt(
    client: OpencodeClient,
    sessionID: string,
    prompt: string,
    agent: string | undefined = WrapperForOpencode.ORCHESTRATOR_AGENT_NAME,
    provider?: string,
    model?: string,
  ): void {
    let modelData: any = {
      providerID: WrapperForOpencode.DEFAULT_PROVIDER,
      modelID: WrapperForOpencode.DEFAULT_MODEL
    };

    if (provider && model) {
      modelData = {
        providerID: provider,
        modelID: model,
      };
    }

    let bodyData: any = {
      model: modelData,
      parts: [
        {
          type: 'text',
          text: prompt,
        }
      ],
    };

    if (agent !== undefined)
      bodyData = { ...bodyData, agent: agent }

    client.session.prompt({
      path: {
        id: sessionID
      },
      body: bodyData,
    });
  }

  static async callInspectorForAgentSession(
    client: OpencodeClient,
    sessionID: string,
    inspectedSessionID: string,
    sessionAgent: string | undefined = undefined,
    model?: string,
    provider?: string,
  ): Promise<void> {
    const isInspected = await WrapperForOpencode.sessionMtx.runExclusive(
      async () =>
        inspectedSessionID in WrapperForOpencode.sessions
        && WrapperForOpencode.sessions[inspectedSessionID].inspectionStatus
        === InspectionStatus.OK
    );
    if (isInspected) {
      client.app.log({
        body: {
          service: 'amphimixis-inspector',
          level: 'debug',
          message: 'AIP: session already has been inspected',
        }
      });
      return;
    }

    const output = await WrapperForOpencode.getAllSessionText(
      client,
      inspectedSessionID
    );
    writeFileSync(
      '.inspected-session',
      `# Agent: ${sessionAgent}\n\n${String(output)}`,
      'utf-8'
    );

    let commandData: any = {
      path:
      {
        id: sessionID,
      },
      body:
      {
        command: 'amphimixis-inspect-session',
      },
    };

    if (
      model !== undefined
      && provider !== undefined
    ) {
      commandData = {
        path: commandData.path,
        body: {
          ...commandData.body,
          model: `${provider}/${model}`,
        }
      }
    }

    client.app.log({
      body: {
        service: 'amphimixis-inspector',
        level: 'debug',
        message: 'AIP: run command amphimixis-inspect-session',
      }
    });
    const cmdSessionID = (await client.session.command(commandData))
      .data?.info.sessionID;
    const cmdLastMsgText = await WrapperForOpencode.sessionMtx.runExclusive(
      () =>
        cmdSessionID && String(cmdSessionID) in WrapperForOpencode.sessions
          ? WrapperForOpencode.sessions[String(cmdSessionID)].lastMessageText
          : undefined
    );

    await WrapperForOpencode.sessionMtx.runExclusive(
      async () => {
        if (!(inspectedSessionID in WrapperForOpencode.sessions)) {
          WrapperForOpencode.sessions[inspectedSessionID] = {
            attemptCount: 0,
            inspectionStatus: InspectionStatus.NOT_INSPECTED,
            lastMessageText: undefined,
          };
        }
        if (String(cmdLastMsgText).match(/INSPECTION IS PASSED/i)) {
          WrapperForOpencode.sessions[inspectedSessionID].inspectionStatus =
            InspectionStatus.OK;
          client.app.log({
            body: {
              service: 'amphimixis-inspector',
              level: 'debug',
              message: 'AIP: inspection is passed',
            }
          });
        }
        else {
          WrapperForOpencode.sessions[inspectedSessionID].inspectionStatus =
            InspectionStatus.TO_FIX;
          client.app.log({
            body: {
              service: 'amphimixis-inspector',
              level: 'debug',
              message: 'AIP: inspection is failed',
            }
          });
        }
      }
    );
  }

  private static async isAttemptAvailable(sessionID: string): Promise<boolean> {
    // lock to avoid race conditions in multi-session client
    return await WrapperForOpencode.sessionMtx.runExclusive(() => {
      if (WrapperForOpencode.sessions[sessionID] === undefined) {
        WrapperForOpencode.sessions[sessionID] = {
          attemptCount: 1,
          inspectionStatus: InspectionStatus.NOT_INSPECTED,
          lastMessageText: undefined,
        };
      }
      else if (
        WrapperForOpencode.sessions[sessionID].attemptCount
        <= WrapperForOpencode.MAX_ATTEMPTS_FORMAL_INSPECTION_PER_SESSION
      )
        WrapperForOpencode.sessions[sessionID].attemptCount += 1;
      else
        return false;
      return true;
    });
  }
}
