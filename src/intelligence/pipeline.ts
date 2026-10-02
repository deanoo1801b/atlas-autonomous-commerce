import { intelligenceAgents } from "./agent-registry.js";
import type { AggregatedTrend } from "./trend-scanner.js";

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
    order: [
      "global-trend-scanner",
      "global-trends",
      "product-opportunity",
      "market-validation",
      "profit-pricing"
    ],
    output: "approved-product-candidate"
  } as const;
}

export function trendToOpportunitySignal(trend: AggregatedTrend): OpportunitySignal {
  return {
    topic: trend.topic,
    demandEvidence: trend.sources.map(
      source => `${source}: signal count ${trend.signalCount}, score ${trend.score.toFixed(2)}`
    ),
    productFormats: ["ebook", "workbook", "planner", "checklist", "template", "guide", "bundle"],
    confidence: trend.confidence
  };
}

export function validateSignal(signal: OpportunitySignal): boolean {
  return signal.topic.trim().length > 0 &&
    signal.demandEvidence.length > 0 &&
    signal.productFormats.length > 0 &&
    signal.confidence >= 0 &&
    signal.confidence <= 1;
}
