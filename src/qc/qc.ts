import type { ProductionPackage } from "../production/types.js";

export interface QCResult {
  passed: boolean;
  checks: Record<string, boolean>;
  blockers: string[];
}

export function runProductionQC(pkg: ProductionPackage): QCResult {
  const checks = {
    hasBrief: Boolean(pkg.brief.title && pkg.brief.audience && pkg.brief.problem),
    hasSections: pkg.brief.sections.length > 0,
    hasKeywords: pkg.brief.keywords.length > 0,
    hasMarketEvidence: pkg.brief.marketEvidence.length > 0,
    assetsPlanned: pkg.assets.length >= 5,
    allAssetsApproved: pkg.assets.every(asset => asset.status === "approved"),
    publishingStillBlocked: pkg.publishingBlocked
  };

  const blockers = Object.entries(checks)
    .filter(([, passed]) => !passed)
    .map(([name]) => name);

  return { passed: blockers.length === 0, checks, blockers };
}
