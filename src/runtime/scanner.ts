import { randomUUID } from "node:crypto";
import { recordAudit } from "./audit-log.js";
import { createOpportunity } from "./opportunity-report.js";
import { persistOpportunity } from "./opportunity-store.js";

export async function runOpportunityScanner(): Promise<void> {
  const now = new Date().toISOString();
  const record = createOpportunity({
    project: "Atlas Goods Store",
    product_or_topic: "Evidence scan pending live connector snapshot",
    product_type: "OTHER",
    market: "UK",
    channel: "social",
    status: "NEW",
    evidence: [{
      source: "ATLAS runtime scanner",
      statement: "Scanner execution is active, but no live connector data is injected into this cycle.",
      confidence: "low"
    }],
    confidence: "LOW",
    eligibility_verified: false,
    availability_verified: false,
    approval_required: true
  });
  await persistOpportunity(record);
  await recordAudit({
    event_id: randomUUID(),
    timestamp: now,
    agent: "opportunity-scanner",
    action: "opportunity_scan",
    mode: "DRY_RUN",
    evidence: record.evidence,
    approval_required: true,
    result: "Opportunity record persisted without making a commercial recommendation."
  });
}
