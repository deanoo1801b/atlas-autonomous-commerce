export interface SEOBrief {
  productId: string;
  primaryKeyword: string;
  secondaryKeywords: string[];
  searchIntents: string[];
  title: string;
  metaDescription: string;
  slug: string;
  audience: string;
  targetMarkets: string[];
  languages: string[];
}

export interface SEOPlan {
  brief: SEOBrief;
  contentAngles: string[];
  internalLinkTargets: string[];
  organicDistributionChannels: string[];
  requiresHumanReview: boolean;
}
