import type { ProductionPackage } from "../production/types.js";
import type { QCResult } from "../qc/qc.js";

export interface PublishingDecision {
  allowed: boolean;
  reasons: string[];
}

export function evaluatePublishing(pkg: ProductionPackage, qc: QCResult, humanApproved = false): PublishingDecision {
  const reasons: string[] = [];
  if (!qc.passed) reasons.push("QC has not passed.");
  if (pkg.publishingBlocked) reasons.push("Publishing is blocked by the production gate.");
  if (!humanApproved) reasons.push("Explicit human approval is required.");

  return { allowed: reasons.length === 0, reasons };
}
