import type { Plugin } from '@opencode-ai/plugin';
import type { OpencodeClient, Part } from '@opencode-ai/sdk';
import { Mutex } from 'async-mutex';
import { writeFileSync } from 'fs';
import assert from 'node:assert/strict';
const inspectorPaths = ['./lib/inspector_general', '../../inspector_general'];
let InspectorGeneral: any;
for (const p of inspectorPaths) {
  try { InspectorGeneral = (await import(p)).default; break; } catch { }
}

let lastMessageText: string | undefined = undefined;

const AmphimixisInspector: Plugin = async ({ client }) => {
  return {
    event: async ({ event }) => {
      if (event.type === 'message.part.updated') {
        const msgPart = event.properties.part;
        const sessionID = msgPart.sessionID;

        await WrapperForOpencode.inspectSubtaskSession(client, sessionID, msgPart);

        if (msgPart.type === 'text')
          lastMessageText = msgPart.text;

        await WrapperForOpencode.inspectMainSession(client, sessionID, msgPart);
      }
    }
  }
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
  parent?: string,
}

class WrapperForOpencode {
  static readonly DEFAULT_PROVIDER = 'opencode';
  static readonly DEFAULT_MODEL = 'big-pickle';
  private static readonly ORCHESTRATOR_AGENT_NAME = 'amphimixis';

  private static sessions: Record<string, SessionData> = {};
  private static sessionMtx: Mutex = new Mutex();
  private static readonly MAX_ATTEMPTS_FORMAL_INSPECTION_PER_SESSION: number = 5;

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
      // get subagent sessionID
      const subSessionID = String(msgPart.state.metadata?.sessionID);
      WrapperForOpencode.callInspectorForAgentSession(
        client,
        sessionID,
        subSessionID,
        String(msgPart.state.input.subagent_type)
      );
    }
  }

  static async inspectMainSession(
    client: OpencodeClient,
    sessionID: string,
    msgPart: Part,
  ) {
    if (
      msgPart.type === 'step-finish'
      && lastMessageText
      && lastMessageText.match('WORK ON THE .*? IS COMPLETED')
      && WrapperForOpencode.isAttemptAvailable(sessionID)
    ) {
      if (
        WrapperForOpencode.sessions[sessionID].inspectionStatus
        !== InspectionStatus.OK
      ) {
        WrapperForOpencode.callInspectorForAgentSession(
          client,
          sessionID,
          String(await WrapperForOpencode.getAllSessionText(
            client,
            sessionID,
          ))
        );
      }

      let [isSuccessful, inspectOutput] = InspectorGeneral.inspect();
      if (!isSuccessful) {
        WrapperForOpencode.sendPrompt(
          client,
          sessionID,
          'The work on the project has not been completed.'
          + ' Check yourself to completing all tasks.\n\n'
          + inspectOutput
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
    provider: string = WrapperForOpencode.DEFAULT_PROVIDER,
    model: string = WrapperForOpencode.DEFAULT_MODEL,
  ): void {
    let promptData: any = {
      path: {
        id: sessionID
      },
      body: {
        model: {
          providerID: provider,
          modelID: model,
        },
        parts: [
          {
            type: 'text',
            text: prompt,
          }
        ],
      },
    };

    if (agent !== undefined)
      promptData = { ...promptData, agent: agent }

    client.session.prompt(promptData);
  }

  static async callInspectorForAgentSession(
    client: OpencodeClient,
    sessionID: string,
    inspectedSessionID: string,
    model?: string,
    provider?: string,
  ): Promise<void> {
    WrapperForOpencode.sessionMtx.runExclusive(
      async () => {
        if (
          WrapperForOpencode.sessions[inspectedSessionID].inspectionStatus
          === InspectionStatus.OK
        )
          return;
      });

    const output = await WrapperForOpencode.getAllSessionText(
      client,
      inspectedSessionID
    );
    writeFileSync('.inspected-session', String(output), 'utf-8');

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

    const cmdOutput = String(WrapperForOpencode.getAllSessionText(
      client,
      String(
        (await client.session.command(commandData))
          .data?.info.sessionID
      )
    ));

    WrapperForOpencode.sessionMtx.runExclusive(
      async () => {
        if (cmdOutput.match(/INSPECTION IS PASSED/i)) {
          WrapperForOpencode.sessions[inspectedSessionID].inspectionStatus =
            InspectionStatus.OK;
        }
        else {
          WrapperForOpencode.sessions[inspectedSessionID].inspectionStatus =
            InspectionStatus.TO_FIX;
        }
      }
    );
  }

  private static isAttemptAvailable(sessionID: string): boolean {
    // lock to avoid race conditions in multi-session client
    WrapperForOpencode.sessionMtx.runExclusive(() => {
      if (WrapperForOpencode.sessions[sessionID] === undefined) {
        WrapperForOpencode.sessions[sessionID] = {
          attemptCount: 1,
          inspectionStatus: InspectionStatus.NOT_INSPECTED,
        };
      }
      else if (
        WrapperForOpencode.sessions[sessionID].attemptCount
        <= WrapperForOpencode.MAX_ATTEMPTS_FORMAL_INSPECTION_PER_SESSION
      )
        WrapperForOpencode.sessions[sessionID].attemptCount += 1;
    });
    return true;
  }
}
