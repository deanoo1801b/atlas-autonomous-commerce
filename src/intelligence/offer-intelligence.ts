export interface MarketOfferEvidence {
  source: string;
  url?: string;
  statement: string;
  observedAt: string;
  confidence: number;
}

export interface OfferPattern {
  pattern: string;
  evidence: MarketOfferEvidence[];
  interpretation: string;
}

export interface OfferIntelligenceReport {
  market: string;
  offerType: string;
  customerProblem: string;
  observedPatterns: OfferPattern[];
  facts: string[];
  assumptions: string[];
  gaps: string[];
  differentiationIdeas: string[];
  complianceNotes: string[];
  confidence: number;
}

export function createOfferIntelligenceReport(input: Omit<OfferIntelligenceReport, "confidence"> & { confidence?: number }): OfferIntelligenceReport {
  return {
    ...input,
    confidence: input.confidence ?? 0,
  };
}

export function validateOfferIntelligence(report: OfferIntelligenceReport): boolean {
  return report.market.trim().length > 0 &&
    report.offerType.trim().length > 0 &&
    report.customerProblem.trim().length > 0 &&
    report.observedPatterns.length > 0 &&
    report.facts.length > 0 &&
    report.assumptions.length > 0 &&
    report.gaps.length > 0 &&
    report.complianceNotes.length > 0 &&
    report.confidence >= 0 &&
    report.confidence <= 1;
}
