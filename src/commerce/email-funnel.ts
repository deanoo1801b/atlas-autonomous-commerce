export type FunnelStage =
  | "lead-capture"
  | "welcome"
  | "nurture"
  | "offer"
  | "post-purchase"
  | "win-back";

export interface FunnelStep {
  stage: FunnelStage;
  delayHours: number;
  objective: string;
  contentType: "email" | "lead-magnet" | "offer";
  requiresApproval: boolean;
}

export interface EmailFunnelPlan {
  name: string;
  audience: string;
  leadMagnet: string;
  steps: FunnelStep[];
  primaryOffer: string;
  successMetrics: string[];
}

export function buildDigitalProductFunnel(
  audience: string,
  leadMagnet: string,
  primaryOffer: string
): EmailFunnelPlan {
  return {
    name: "Digital Product Evergreen Funnel",
    audience,
    leadMagnet,
    primaryOffer,
    steps: [
      { stage: "lead-capture", delayHours: 0, objective: "Capture a qualified subscriber with a useful free asset.", contentType: "lead-magnet", requiresApproval: true },
      { stage: "welcome", delayHours: 0, objective: "Deliver the lead magnet and establish trust.", contentType: "email", requiresApproval: true },
      { stage: "nurture", delayHours: 24, objective: "Teach, demonstrate expertise and surface the buyer problem.", contentType: "email", requiresApproval: true },
      { stage: "offer", delayHours: 48, objective: "Present the relevant paid product with a clear value proposition.", contentType: "offer", requiresApproval: true },
      { stage: "post-purchase", delayHours: 168, objective: "Improve delivery, satisfaction and cross-sell opportunities.", contentType: "email", requiresApproval: true },
      { stage: "win-back", delayHours: 720, objective: "Re-engage inactive subscribers or customers with relevant value.", contentType: "email", requiresApproval: true }
    ],
    successMetrics: [
      "lead-capture conversion rate",
      "email open rate",
      "click-through rate",
      "lead-to-sale conversion rate",
      "revenue per subscriber",
      "unsubscribe rate",
      "refund rate"
    ]
  };
}
