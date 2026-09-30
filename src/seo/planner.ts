import type { SEOBrief, SEOPlan } from "./types.js";

export function createSEOPlan(brief: SEOBrief): SEOPlan {
  if (!brief.productId || !brief.primaryKeyword || !brief.audience) {
    throw new Error("SEO brief requires productId, primaryKeyword and audience.");
  }

  return {
    brief,
    contentAngles: [
      `How to solve: ${brief.audience}`,
      `Complete guide: ${brief.primaryKeyword}`,
      `Checklist/resources for ${brief.audience}`
    ],
    internalLinkTargets: [],
    organicDistributionChannels: ["blog", "Pinterest", "YouTube", "TikTok", "Instagram"],
    requiresHumanReview: true
  };
}
