import { intelligenceAgents } from "./agent-registry.js";

export interface OpportunitySignal {
  topic: string;
  demandEvidence: string[];
  seasonality?: string;
  audience?: string;
  productFormats: string[];
  confidence: number;
}

export function getIntelligencePipeline() {
  return {
    stages: intelligenceAgents.map(agent => agent.id),
    order: ["global-trends", "product-opportunity", "market-validation", "profit-pricing"],
    output: "approved-product-candidate"
  } as const;
}

export function validateSignal(signal: OpportunitySignal): boolean {
  return signal.topic.trim().length > 0 &&
    signal.demandEvidence.length > 0 &&
    signal.productFormats.length > 0 &&
    signal.confidence >= 0 &&
    signal.confidence <= 1;
}
