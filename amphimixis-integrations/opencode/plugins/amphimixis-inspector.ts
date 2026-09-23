import type { Plugin } from '@opencode-ai/plugin';
import type { OpencodeClient, Part } from '@opencode-ai/sdk';
import { Mutex } from 'async-mutex';
import InspectorGeneral from 'inspector_general';
import assert from 'node:assert/strict';
import { writeFileSync } from 'node:fs';

const AmphimixisInspector: Plugin = async ({ client }) => {
  await WrapperForOpencode.log(
    client,
    'Amphimixis-Inspector plugin (AIP) is initialized',
  );
  return {
    event: async ({ event }) => {
      if (event.type === 'message.updated') {
        await WrapperForOpencode.handleMessageUpdated(event);
        return;
      }

      if (event.type !== 'message.part.updated') {
        return;
      }

      let agent = WrapperForOpencode.getAgentFromEvent(event);
      const msgPart = event.properties.part;
      const sessionId = msgPart.sessionID;

      if (msgPart.type === 'text' || agent) {
        await WrapperForOpencode.sessionMtx.runExclusive(
          async () => {
            if (!(sessionId in WrapperForOpencode.sessions)) {
              WrapperForOpencode.sessions[sessionId] =
              {
                attemptCount: 0,
                inspectionStatus: InspectionStatus.NOT_INSPECTED,
                lastMessageText: undefined,
                lastUsedAgent: agent,
              };
            }
            if (msgPart.type === 'text') {
              WrapperForOpencode.sessions[sessionId]
                .lastMessageText = msgPart.text;
            }
            if (agent) {
              WrapperForOpencode.sessions[sessionId]
                .lastUsedAgent = agent;
            }
          }
        );
      }

      if (!agent) {
        await WrapperForOpencode.sessionMtx.runExclusive(async () => {
          agent = sessionId in WrapperForOpencode.sessions
            ? WrapperForOpencode.sessions[sessionId].lastUsedAgent
            : undefined;
        });
      }

      await WrapperForOpencode.inspectSubtaskSession(client, sessionId, msgPart);
      await WrapperForOpencode.inspectMainSession(
        client,
        sessionId,
        msgPart,
        String(agent),
      );
    }
  };
};

export default AmphimixisInspector;

enum InspectionStatus {
  NO_NEED,
  NOT_INSPECTED,
  FAILED,
  TO_FIX,
  OK,
}

type SessionData = {
  attemptCount: number,
  inspectionStatus: InspectionStatus,
  lastMessageText: string | undefined,
  parent?: string,
  lastUsedAgent?: string | undefined,
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

  static async log(
    client: OpencodeClient,
    message: string,
    service: string = 'amphimixis-inspector',
    level: 'debug' | 'error' | 'info' | 'warn' = 'debug',
    tag: string = 'AIP',
  ): Promise<void> {
    await client.app.log({
      body: {
        service: service,
        level: level,
        message: `(${tag}) ${message}`,
      }
    });
  }

  static async inspectSubtaskSession(client: OpencodeClient, sessionId: string, msgPart: Part) {
    if (
      msgPart.type === 'tool'
      && msgPart.tool === 'task'
      && String(msgPart.state.input.subagent_type).match(/^amphimixis-.*/i)
      && msgPart.state.status === 'completed'
    ) {
      const subagent = String(msgPart.state.input.subagent_type);
      await WrapperForOpencode.log(
        client,
        `subtask is been inspecting now. Session=${sessionId},`
        + ` subagent=${subagent},`
        + ` status=${msgPart.state.status}`,
      );
      // get subagent sessionId
      const subSessionId = msgPart.state.metadata?.sessionId;
      if (subSessionId === undefined)
        return;
      await WrapperForOpencode.callInspectorForAgentSession(
        client,
        sessionId,
        String(subSessionId),
        subagent,
      );
    }
  }

  static async inspectMainSession(
    client: OpencodeClient,
    sessionId: string,
    msgPart: Part,
    agent: string,
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
      && agent === WrapperForOpencode.ORCHESTRATOR_AGENT_NAME
      && isWorkFinished
      && await WrapperForOpencode.isAttemptAvailable(sessionId)
    ) {
      // 1. call LLM inspection
      await WrapperForOpencode.log(
        client,
        `inspect main task. Call Inspector for main task.`
        + ` Session=${sessionId}, agent=${agent}`,
      );

      await WrapperForOpencode.callInspectorForAgentSession(
        client,
        sessionId,
        sessionId,
        agent,
      );

      // 2. formally inspect report content
      await WrapperForOpencode.log(
        client,
        `report content inspecting. Session=${sessionId}`,
      );
      const [isSuccessful, inspectOutput] = InspectorGeneral.inspect();
      if (!isSuccessful) {
        await WrapperForOpencode.sendPrompt(
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

  static async handleMessageUpdated(ev: unknown): Promise<void> {
    const e = ev as Record<string, any>;
    const info = e?.properties?.info;
    const sessionId = info?.sessionID;
    if (typeof sessionId !== 'string') {
      return;
    }
    const agent = WrapperForOpencode.getAgentFromEvent(ev);
    await WrapperForOpencode.sessionMtx.runExclusive(async () => {
      if (!(sessionId in WrapperForOpencode.sessions)) {
        WrapperForOpencode.sessions[sessionId] = {
          attemptCount: 0,
          inspectionStatus: InspectionStatus.NOT_INSPECTED,
          lastMessageText: undefined,
        };
      }
      if (agent) {
        WrapperForOpencode.sessions[sessionId].lastUsedAgent = agent;
      }
    });
  }

  static getAgentFromEvent(ev: unknown): string | undefined {
    if (!ev || typeof ev !== 'object') return undefined
    const e = ev as Record<string, any>

    // V1 API: EventMessageUpdated structure
    const info = e?.properties?.info

    if (info) {
      // V1 UserMessage has agent field
      if (typeof info.agent === 'string') return info.agent

      // V1 AssistantMessage uses 'mode' instead of 'agent'
      if (typeof info.mode === 'string') return info.mode
    }

    // Fallback for other event types or structures
    const payload = e.data ?? e.event?.data ?? e.event ?? e
    const msg = payload?.info ?? payload?.message ?? payload?.part ?? payload

    const candidate =
      msg?.agent ??
      msg?.mode ??  // V1 uses 'mode' for assistant messages
      (Array.isArray(msg?.agents) ? msg.agents[0] : undefined) ??
      msg?.request?.agent ??
      msg?.run?.agent ??
      msg?.metadata?.agent ??
      payload?.agent

    if (!candidate) return undefined
    if (typeof candidate === 'string') return candidate
    if (typeof candidate === 'number') return String(candidate)
    if (candidate && typeof candidate === 'object')
      return (candidate.id ?? candidate.name) as string | undefined

    return undefined
  }

  static async getAllSessionText(
    client: OpencodeClient,
    sessionId: string,
    agent?: string,
  ) {
    const response = await client.session.messages({
      path: { id: sessionId }
    });
    return WrapperForOpencode.textFromMessages(response.data ?? [], agent);
  }

  private static textFromMessages(
    messages: Array<{
      parts?: Array<{ type?: string; text?: string }>;
    }>,
    agent?: string,
  ): string {
    let textContent: string = '';
    if (agent)
      textContent += `Agent: ${agent}\n\n`;

    // map through messages and extract text-based components
    textContent += messages.map(message => {
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

  static async sendPrompt(
    client: OpencodeClient,
    sessionId: string,
    prompt: string,
    agent: string | undefined = WrapperForOpencode.ORCHESTRATOR_AGENT_NAME,
    provider?: string,
    model?: string,
  ): Promise<void> {
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

    await client.session.prompt({
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
    inspectedAgent: string | undefined = undefined,
    agent: string | undefined = WrapperForOpencode.ORCHESTRATOR_AGENT_NAME,
    model?: string,
    provider?: string,
  ): Promise<void> {
    const isNoNeedBeInspected = await WrapperForOpencode.sessionMtx.runExclusive(
      async () => {
        const inspectedSessionStats = (
          inspectedSessionId in WrapperForOpencode.sessions
            ? WrapperForOpencode.sessions[inspectedSessionId].inspectionStatus
            : InspectionStatus.NOT_INSPECTED
        );
        return inspectedSessionStats === InspectionStatus.OK
          || inspectedSessionStats === InspectionStatus.NO_NEED;
      }
    );
    if (isNoNeedBeInspected) {
      await WrapperForOpencode.log(
        client,
        `session already has been inspected. Session=${sessionId},`
        + ` inspectedSession=${inspectedSessionId}`,
      );
      return;
    }

    const output = await WrapperForOpencode.getAllSessionText(
      client,
      inspectedSessionId
    );
    writeFileSync(
      `.inspected-session-${inspectedSessionId}`,
      `# Agent: ${inspectedAgent}\n\n${String(output)}`,
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
        arguments: 'inspect session with ID=' + inspectedSessionId,
        agent: agent,
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

    await WrapperForOpencode.log(
      client,
      `run command amphimixis-inspect-session. Session=${sessionId},`
      + ` inspectedSession=${inspectedSessionId}, agent=${inspectedAgent}`,
    );
    const cmdSessionId = (await client.session.command(commandData))
      .data?.info.sessionID;

    if (cmdSessionId === undefined) {
      await WrapperForOpencode.log(
        client,
        `command session id is undefined. Session=${sessionId},`
        + ` inspectedSession=${inspectedSessionId}`,
      );
      return;
    }

    await WrapperForOpencode.sessionMtx.runExclusive(
      async () => {
        WrapperForOpencode.sessions[String(cmdSessionId)] = {
          attemptCount: 0,
          inspectionStatus: InspectionStatus.NO_NEED,
          lastMessageText: undefined,
        };

        if (!(inspectedSessionId in WrapperForOpencode.sessions)) {
          WrapperForOpencode.sessions[inspectedSessionId] = {
            attemptCount: 0,
            inspectionStatus: InspectionStatus.NOT_INSPECTED,
            lastMessageText: undefined,
          };
        }
      }
    );

    const passed = await WrapperForOpencode.waitForInspectionResult(
      client,
      String(cmdSessionId),
    );

    await WrapperForOpencode.sessionMtx.runExclusive(
      async () => {
        if (passed) {
          WrapperForOpencode.sessions[inspectedSessionId].inspectionStatus =
            InspectionStatus.OK;
          await WrapperForOpencode.log(
            client,
            `inspection is passed. Session=${sessionId},`
            + ` inspectedSession=${inspectedSessionId}`,
          );
        }
        else {
          WrapperForOpencode.sessions[inspectedSessionId].inspectionStatus =
            InspectionStatus.TO_FIX;
          await WrapperForOpencode.log(
            client,
            `inspection is failed. Session=${sessionId},`
            + ` inspectedSession=${inspectedSessionId}`,
          );
        }
      }
    );
  }

  private static async waitForInspectionResult(
    client: OpencodeClient,
    cmdSessionId: string,
    timeoutMs: number = 120_000,
  ): Promise<boolean> {
    const startedAt = Date.now();
    while (Date.now() - startedAt < timeoutMs) {
      const response = await client.session.messages({
        path: { id: cmdSessionId },
      });
      const messages = response.data ?? [];
      const text = WrapperForOpencode.textFromMessages(messages);
      if (String(text).match(/INSPECTION IS PASSED/i)) {
        return true;
      }
      if (String(text).match(/INSPECTION FAILED/i)
        || WrapperForOpencode.isSessionFinished(messages)) {
        return false;
      }
      await new Promise(resolve => setTimeout(resolve, 500));
    }
    return false;
  }

  private static isSessionFinished(
    messages: Array<{ parts?: Array<{ type?: string }> }>,
  ): boolean {
    return messages.some(message =>
      (message.parts ?? []).some(part => part.type === 'step-finish')
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
