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
        const sessionId = msgPart.sessionID;

        WrapperForOpencode.inspectSubtaskSession(client, sessionId, msgPart);

        if (msgPart.type === 'text') {
          await WrapperForOpencode.sessionMtx.runExclusive(
            async () => {
              if (!(sessionId in WrapperForOpencode.sessions)) {
                WrapperForOpencode.sessions[sessionId] =
                {
                  attemptCount: 0,
                  inspectionStatus: InspectionStatus.NOT_INSPECTED,
                  lastMessageText: undefined,
                };
              }
              WrapperForOpencode.sessions[sessionId]
                .lastMessageText = msgPart.text;
            }
          )
        }

        WrapperForOpencode.inspectMainSession(client, sessionId, msgPart);
      }
    }
  };
};

export default AmphimixisInspector;

enum InspectionStatus {
  NOT_INSPECTED,
  OK,
  TO_FIX,
  FAILED,
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

  static async inspectSubtaskSession(client: OpencodeClient, sessionId: string, msgPart: Part) {
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
          message: 'AIP: subtask is been inspecting now',
        }
      });
      // get subagent sessionId
      const subSessionId = msgPart.state.metadata?.sessionId;
      if (subSessionId === undefined)
        return;
      WrapperForOpencode.callInspectorForAgentSession(
        client,
        sessionId,
        String(subSessionId),
        String(msgPart.state.input.subagent_type),
      );
    }
  }

  static async inspectMainSession(
    client: OpencodeClient,
    sessionId: string,
    msgPart: Part,
  ) {
    const isWorkFinished = await WrapperForOpencode.sessionMtx.runExclusive(
      () => {
        if (!(sessionId in WrapperForOpencode.sessions)) {
          WrapperForOpencode.sessions[sessionId] = {
            attemptCount: 0,
            inspectionStatus: InspectionStatus.NOT_INSPECTED,
            lastMessageText: undefined,
          };
        }
        return WrapperForOpencode.sessions[sessionId]
          .lastMessageText
          && WrapperForOpencode.sessions[sessionId]
            .lastMessageText.match('WORK ON THE .*? IS COMPLETED');
      });
    if (
      msgPart.type === 'step-finish'
      && isWorkFinished
      && await WrapperForOpencode.isAttemptAvailable(sessionId)
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
        sessionId,
        sessionId,
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
          sessionId,
          'The work on the project has not been completed.'
          + ' Check yourself to completing all tasks.\n\n'
          + inspectOutput.join('\n'),
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
    sessionId: string,
    prompt: string,
    agent: string | undefined = WrapperForOpencode.ORCHESTRATOR_AGENT_NAME,
    provider?: string,
    model?: string,
  ): void {
    let bodyData: any = {
      parts: [
        {
          type: 'text',
          text: prompt,
        }
      ],
    };

    if (provider && model) {
      bodyData = {
        ...bodyData,
        model: {
          providerId: provider,
          modelId: model,
        },
      };
    }

    if (agent !== undefined)
      bodyData = { ...bodyData, agent: agent }

    client.session.prompt({
      path: {
        id: sessionId
      },
      body: bodyData,
    });
  }

  static async callInspectorForAgentSession(
    client: OpencodeClient,
    sessionId: string,
    inspectedSessionId: string,
    sessionAgent: string | undefined = undefined,
    model?: string,
    provider?: string,
  ): Promise<void> {
    const isInspected = await WrapperForOpencode.sessionMtx.runExclusive(
      async () =>
        inspectedSessionId in WrapperForOpencode.sessions
        && WrapperForOpencode.sessions[inspectedSessionId].inspectionStatus
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
      inspectedSessionId
    );
    writeFileSync(
      '.inspected-session',
      `# Agent: ${sessionAgent}\n\n${String(output)}`,
      'utf-8'
    );

    let commandData: any = {
      path:
      {
        id: sessionId,
      },
      body:
      {
        command: 'amphimixis-inspect-session',
        arguments: '',
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
    const cmdSessionId = (await client.session.command(commandData))
      .data?.info.sessionID;
    const cmdLastMsgText = await WrapperForOpencode.sessionMtx.runExclusive(
      () =>
        cmdSessionId && String(cmdSessionId) in WrapperForOpencode.sessions
          ? WrapperForOpencode.sessions[String(cmdSessionId)].lastMessageText
          : undefined
    );

    await WrapperForOpencode.sessionMtx.runExclusive(
      async () => {
        if (!(inspectedSessionId in WrapperForOpencode.sessions)) {
          WrapperForOpencode.sessions[inspectedSessionId] = {
            attemptCount: 0,
            inspectionStatus: InspectionStatus.NOT_INSPECTED,
            lastMessageText: undefined,
          };
        }
        if (String(cmdLastMsgText).match(/INSPECTION IS PASSED/i)) {
          WrapperForOpencode.sessions[inspectedSessionId].inspectionStatus =
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
          WrapperForOpencode.sessions[inspectedSessionId].inspectionStatus =
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

  private static async isAttemptAvailable(sessionId: string): Promise<boolean> {
    // lock to avoid race conditions in multi-session client
    return await WrapperForOpencode.sessionMtx.runExclusive(() => {
      if (WrapperForOpencode.sessions[sessionId] === undefined) {
        WrapperForOpencode.sessions[sessionId] = {
          attemptCount: 1,
          inspectionStatus: InspectionStatus.NOT_INSPECTED,
          lastMessageText: undefined,
        };
      }
      else if (
        WrapperForOpencode.sessions[sessionId].attemptCount
        <= WrapperForOpencode.MAX_ATTEMPTS_FORMAL_INSPECTION_PER_SESSION
      )
        WrapperForOpencode.sessions[sessionId].attemptCount += 1;
      else
        return false;
      return true;
    });
  }
}
