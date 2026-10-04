import type { AgentTask, RiskLevel } from "./types.js";

export type OpportunityRoute =
  | "research"
  | "digital-product"
  | "shopify"
  | "seo"
  | "social"
  | "video"
  | "creative"
  | "experiment"
  | "scale"
  | "reject";

export interface OpportunityReportInput {
  id: string;
  category: string;
  recommendation: string;
  confidence: number;
  risk: RiskLevel;
  evidence: string[];
  requestedAction?: string;
}

export interface CoordinatorDecision {
  route: OpportunityRoute;
  agentId: string;
  reason: string;
  requiresApproval: boolean;
}

const routes: Record<OpportunityRoute, { agentId: string; keywords: string[] }> = {
  research: { agentId: "global-trends", keywords: ["research", "watch", "trend"] },
  "digital-product": { agentId: "product-opportunity", keywords: ["digital", "ebook", "workbook", "planner", "template", "guide", "bundle"] },
  shopify: { agentId: "shopify-product", keywords: ["shopify", "store", "listing", "product"] },
  seo: { agentId: "seo-global-sales", keywords: ["seo", "search", "keyword", "organic"] },
  social: { agentId: "social-media", keywords: ["social", "tiktok", "instagram", "pinterest", "facebook"] },
  video: { agentId: "video-creation", keywords: ["video", "youtube", "short", "reel"] },
  creative: { agentId: "image-generation", keywords: ["image", "creative", "mockup", "visual"] },
  experiment: { agentId: "analytics-experimentation", keywords: ["test", "experiment", "validate"] },
  scale: { agentId: "orchestrator", keywords: ["scale", "scaling"] },
  reject: { agentId: "orchestrator", keywords: ["reject", "discard"] }
};

export function routeOpportunity(report: OpportunityReportInput): CoordinatorDecision {
  const text = `${report.category} ${report.recommendation} ${report.requestedAction ?? ""}`.toLowerCase();

  if (report.confidence < 0.45 || report.evidence.length === 0) {
    return { route: "research", agentId: routes.research.agentId, reason: "Evidence is insufficient for downstream execution.", requiresApproval: false };
  }

  if (report.recommendation.toLowerCase().includes("reject")) {
    return { route: "reject", agentId: routes.reject.agentId, reason: "Opportunity report recommends rejection.", requiresApproval: false };
  }

  if (report.recommendation.toLowerCase().includes("scale") && report.confidence >= 0.8) {
    return { route: "scale", agentId: routes.scale.agentId, reason: "Evidence and confidence meet the scaling threshold.", requiresApproval: true };
  }

  const ranked = (Object.entries(routes) as Array<[OpportunityRoute, typeof routes[OpportunityRoute]]>)
    .filter(([route]) => !["research", "scale", "reject"].includes(route))
    .map(([route, config]) => ({
      route,
      agentId: config.agentId,
      matches: config.keywords.filter(keyword => text.includes(keyword)).length
    }))
    .sort((a, b) => b.matches - a.matches);

  const best = ranked[0];
  if (!best || best.matches === 0) {
    return { route: "experiment", agentId: routes.experiment.agentId, reason: "No specialist route matched; send to controlled validation.", requiresApproval: true };
  }

  return {
    route: best.route,
    agentId: best.agentId,
    reason: `Matched ${best.matches} opportunity signals to the specialist route.`,
    requiresApproval: report.risk !== "low"
  };
}

export function coordinatorTask(report: OpportunityReportInput): AgentTask {
  const decision = routeOpportunity(report);
  return {
    id: `route-${report.id}`,
    agentId: decision.agentId,
    action: decision.route === "scale" ? "scale-opportunity" : `process-${decision.route}`,
    input: { opportunityReportId: report.id },
    risk: report.risk,
    requiresApproval: decision.requiresApproval
  };
}
