import type { AgentDefinition } from "../core/types.js";

export const intelligenceAgents: AgentDefinition[] = [
  {
    id: "global-trend-scanner",
    name: "Global Trend Scanner",
    purpose: "Collect and score early demand signals across major search, marketplace and social trend surfaces.",
    risk: "low",
    status: "ready",
    requiresApproval: false,
    capabilities: ["google-trends", "tiktok", "etsy", "amazon", "pinterest", "youtube", "instagram", "reddit", "google-search", "ebay"],
    dependsOn: []
  },
  {
    id: "global-trends",
    name: "Global Trends & Demand Intelligence",
    purpose: "Interpret corroborated trend signals, seasonality, search intent and demand patterns.",
    risk: "low",
    status: "ready",
    requiresApproval: false,
    capabilities: ["trend-analysis", "seasonality", "demand-signals", "keyword-signals"],
    dependsOn: ["global-trend-scanner"]
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
  }  ,{
    id: "email-funnel",
    name: "Email Funnel & Lifecycle Agent",
    purpose: "Turn qualified traffic into owned audiences and sales through lead magnets, automated nurture sequences, product offers and lifecycle optimisation.",
    risk: "medium",
    status: "ready",
    requiresApproval: true,
    capabilities: ["lead-magnets", "email-sequences", "welcome-series", "nurture", "segmentation", "conversion-testing", "lifecycle-analytics"],
    dependsOn: ["product-opportunity", "market-validation", "profit-pricing"]
  }
];
