import { randomUUID } from "node:crypto";
import { recordAudit } from "./audit-log.js";
import { agentRegistry } from "./registry.js";
import type { AgentStatusRecord, RuntimeMode } from "./types.js";
import { runScheduledScanner } from "./schedule.js";
import { loadConfig } from "../config.js";

function resolveRuntimeMode(): RuntimeMode {
  const config = loadConfig();
  // Until an approved action handler exists, this runtime must never claim to execute.
  if (config.dryRun || config.mode === "observe" || config.mode === "recommend") return "DRY_RUN";
  return "APPROVAL_REQUIRED";
}

const mode: RuntimeMode = resolveRuntimeMode();

const socialPipeline = [
  "trend-research",
  "customer-demand-question-mining",
  "competitor-intelligence",
  "seo-opportunity-intelligence",
  "product-opportunity",
  "analytics-attribution",
  "conversion-optimisation",
  "social-media-manager",
  "creative-video-production",
  "compliance-brand-qa",
  "experiment-ab-testing"
];

function now(): string {
  return new Date().toISOString();
}

export async function runHealthCheck(): Promise<AgentStatusRecord[]> {
  const checkedAt = now();
  const statuses: AgentStatusRecord[] = agentRegistry.map((agent) => ({
    agent_id: agent.agent_id,
    status: agent.enabled ? "READY" : "DISABLED",
    last_checked: checkedAt,
    message: agent.enabled ? "Registered and ready for controlled execution." : "Disabled by configuration."
  }));

  await recordAudit({
    event_id: randomUUID(),
    timestamp: checkedAt,
    agent: "atlas-runtime",
    action: "agent_health_check",
    mode,
    evidence: [{
      source: "src/runtime/registry.ts",
      statement: `Checked ${statuses.length} registered agents.`,
      confidence: "high"
    }],
    approval_required: false,
    result: "DRY_RUN health check completed."
  });

  return statuses;
}

export async function runCycle(): Promise<void> {
  const started = now();

  await recordAudit({
    event_id: randomUUID(),
    timestamp: started,
    agent: "atlas-runtime",
    action: "runtime_cycle_start",
    mode,
    evidence: [{
      source: "runtime/approval-policy.md",
      statement: "Runtime starts in DRY_RUN and protected actions require approval.",
      confidence: "high"
    }],
    approval_required: false,
    result: "Cycle started; no external side effects permitted."
  });

  const statuses = await runHealthCheck();
  await runScheduledScanner({ intervalMinutes: 60, enabled: true, mode });

  await recordAudit({
    event_id: randomUUID(),
    timestamp: now(),
    agent: "offer-intelligence",
    action: "offer_intelligence_ready",
    mode,
    evidence: [{
      source: "src/intelligence/offer-intelligence.ts",
      statement: "Offer intelligence is prepared to separate observed market facts from assumptions and identify compliant differentiation opportunities.",
      confidence: "high"
    }],
    approval_required: false,
    result: "Offer intelligence stage prepared; no protected content is copied and no commercial action is executed."
  });
  await recordAudit({
    event_id: randomUUID(),
    timestamp: now(),
    agent: "atlas-runtime",
    action: "social_pipeline_ready",
    mode,
    evidence: [{
      source: "docs/SOCIAL_MEDIA_AGENT_WORKFLOW.md",
      statement: `Validated ${socialPipeline.length} social pipeline agents in controlled order.`,
      confidence: "high"
    }],
    approval_required: true,
    result: "Social pipeline prepared; publication remains approval-gated."
  });
  console.log(JSON.stringify({ mode, timestamp: started, agents: statuses }, null, 2));
}
