import { audit } from "./audit.js";
import { buildTask } from "./orchestrator.js";
import type { AtlasMode } from "./types.js";

export function executePlannedAgent(agentId: string, action: string, input: Record<string, unknown>, mode: AtlasMode) {
  const task = buildTask(agentId, action, input, mode);
  audit({ timestamp: new Date().toISOString(), event: "task-created", taskId: task.id, agentId, details: { risk: task.risk, requiresApproval: task.requiresApproval } });
  if (task.requiresApproval) {
    audit({ timestamp: new Date().toISOString(), event: "approval-required", taskId: task.id, agentId });
    return { status: "awaiting-approval" as const, task };
  }
  audit({ timestamp: new Date().toISOString(), event: "task-authorized", taskId: task.id, agentId });
  return { status: "authorized" as const, task };
}
