import type { RiskLevel } from "../core/types.js";

export type OpportunityStatus =
  | "research-watch"
  | "validation"
  | "approved-opportunity"
  | "rejected"
  | "scaling";

export interface OpportunityReport {
  id: string;
  title: string;
  category: string;
  status: OpportunityStatus;
  whatItIs: string;
  whyItExists: string;
  evidence: string[];
  facts: string[];
  assumptions: string[];
  risks: string[];
  validationTest: string;
  scaleCriteria: string[];
  confidence: number;
  risk: RiskLevel;
  recommendedAction: string;
  createdAt: string;
}

export function createOpportunityReport(input: Omit<OpportunityReport, "createdAt">): OpportunityReport {
  return { ...input, createdAt: new Date().toISOString() };
}

export function isScaleReady(report: OpportunityReport): boolean {
  return report.status === "approved-opportunity" &&
    report.confidence >= 0.8 &&
    report.scaleCriteria.length > 0 &&
    report.validationTest.trim().length > 0 &&
    report.risks.length > 0;
}
