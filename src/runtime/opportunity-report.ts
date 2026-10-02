import { randomUUID } from "node:crypto";
import type { Evidence } from "./types.js";

export type OpportunityStatus = "NEW" | "TEST" | "HOLD" | "BLOCKED" | "ARCHIVED";

export interface OpportunityRecord {
  opportunity_id: string;
  created_at: string;
  updated_at: string;
  project: string;
  product_or_topic: string;
  product_type: "DIGITAL" | "GODROPSHIP" | "GELATO" | "OTHER";
  market: string;
  channel: string;
  status: OpportunityStatus;
  evidence: Evidence[];
  confidence: "LOW" | "MEDIUM" | "HIGH";
  eligibility_verified: boolean;
  availability_verified: boolean;
  url?: string;
  content_angle?: string;
  test_hypothesis?: string;
  approval_required: boolean;
}

export function createOpportunity(input: Omit<OpportunityRecord, "opportunity_id" | "created_at" | "updated_at">): OpportunityRecord {
  const now = new Date().toISOString();
  return { ...input, opportunity_id: randomUUID(), created_at: now, updated_at: now };
}
