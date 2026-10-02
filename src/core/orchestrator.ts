import type { AgentTask, AtlasMode, RiskLevel } from "./types.js";

const HIGH_IMPACT_ACTIONS = new Set([
  "publish-product",
  "publish-social",
  "change-price",
  "change-store-settings",
  "spend-budget"
]);

export function buildTask(
  agentId: string,
  action: string,
  input: Record<string, unknown>,
  mode: AtlasMode
): AgentTask {
  const risk: RiskLevel =
    HIGH_IMPACT_ACTIONS.has(action) ? "high" :
    action.includes("draft") || action.includes("recommend") ? "medium" : "low";

  const requiresApproval =
    mode !== "autonomous" || risk === "high";

  return {
    id: `task-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
    agentId,
    action,
    input,
    risk,
    requiresApproval
  };
}
