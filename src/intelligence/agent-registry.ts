import type { AgentDefinition } from "../core/types.js";

export const intelligenceAgents: AgentDefinition[] = [
  {
    id: "global-trends",
    name: "Global Trends & Demand Intelligence",
    purpose: "Identify rising demand, seasonality, search intent and cross-platform trend signals.",
    risk: "low",
    status: "ready",
    requiresApproval: false,
    capabilities: ["trend-research", "seasonality", "demand-signals", "keyword-signals"],
    dependsOn: []
  },
  {
    id: "product-opportunity",
    name: "Digital Product Opportunity Hunter",
    purpose: "Turn demand signals into specific digital-product opportunities and briefs.",
    risk: "low",
    status: "ready",
    requiresApproval: false,
    capabilities: ["opportunity-discovery", "gap-analysis", "product-briefs"],
    dependsOn: ["global-trends"]
  },
  {
    id: "market-validation",
    name: "Market Validation",
    purpose: "Evaluate demand, competition, buyer intent and evidence quality before production.",
    risk: "low",
    status: "ready",
    requiresApproval: false,
    capabilities: ["competition-analysis", "demand-validation", "evidence-scoring"],
    dependsOn: ["global-trends", "product-opportunity"]
  },
  {
    id: "profit-pricing",
    name: "Profit & Pricing Intelligence",
    purpose: "Model price, fees, margin, bundles and commercial viability before launch.",
    risk: "medium",
    status: "ready",
    requiresApproval: false,
    capabilities: ["pricing", "margin-analysis", "bundle-economics"],
    dependsOn: ["market-validation"]
  }
];
