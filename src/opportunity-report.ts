export interface Opportunity {
  id: string;
  title: string;
  category: string;
  evidence: string[];
  upside?: string;
  risks: string[];
  confidence: "low" | "medium" | "high";
  recommendedAction: string;
  approvalRequired: boolean;
}

export interface OpportunityReport {
  generatedAt: string;
  storeDomain: string;
  opportunities: Opportunity[];
}

export function createOpportunityReport(
  storeDomain: string,
  opportunities: Opportunity[] = []
): OpportunityReport {
  return { generatedAt: new Date().toISOString(), storeDomain, opportunities };
}
