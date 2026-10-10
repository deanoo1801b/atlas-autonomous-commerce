import { audit, createAuditEvent } from "../audit.js";
import { AGENT_REGISTRY, type AgentDefinition } from "../agent-registry.js";
import { loadConfig } from "../config.js";
import { persistAuditEvent } from "./audit-store.js";

export interface AtlasTask {
  id: string;
  agentId: string;
  action: string;
  rationale: string;
  requiresWrite?: boolean;
  estimatedCost?: number;
}

export interface TaskResult {
  taskId: string;
  status: "planned" | "blocked";
  message: string;
}

export async function runTask(task: AtlasTask): Promise<TaskResult> {
  const config = loadConfig();
  const agent: AgentDefinition | undefined = AGENT_REGISTRY.find(
    (item) => item.id === task.agentId && item.enabled
  );

  let result: TaskResult;
  if (!agent) {
    result = { taskId: task.id, status: "blocked", message: "Agent is missing or disabled." };
  } else if (task.requiresWrite && config.requireApprovalForWrites) {
    result = { taskId: task.id, status: "blocked", message: "Write action requires explicit approval." };
  } else if (typeof task.estimatedCost === "number" && task.estimatedCost > 0 && config.requireApprovalForSpend) {
    result = { taskId: task.id, status: "blocked", message: "Spending requires explicit approval." };
  } else if (config.dryRun || config.mode === "observe" || config.mode === "recommend") {
    result = { taskId: task.id, status: "planned", message: "Dry-run: no external action was performed." };
  } else {
    // Deliberately do not execute external actions here. An approved adapter
    // and action-specific implementation must be registered before execution.
    result = { taskId: task.id, status: "blocked", message: "No executable action handler is registered." };
  }

  const event = createAuditEvent({
    agent: agent?.id ?? "atlas",
    action: task.action,
    severity: result.status === "blocked" ? "warning" : "info",
    outcome: result.status,
    details: { taskId: task.id, rationale: task.rationale, message: result.message }
  });
  audit(event);
  await persistAuditEvent(event);
  return result;
}
