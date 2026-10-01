export type PermissionTier = 0 | 1 | 2 | 3;

export interface AgentDefinition {
  id: string;
  name: string;
  domain: string;
  permissionTier: PermissionTier;
  enabled: boolean;
  purpose: string;
}

export const AGENT_REGISTRY: AgentDefinition[] = [
  { id: "atlas", name: "ATLAS", domain: "governance", permissionTier: 1, enabled: true, purpose: "Coordinate the commerce operating system and enforce controls." },
  { id: "market-research", name: "Market Research", domain: "intelligence", permissionTier: 1, enabled: true, purpose: "Identify evidence-backed market opportunities." },
  { id: "product-opportunity", name: "Product Opportunity & Evidence", domain: "product", permissionTier: 1, enabled: true, purpose: "Score product opportunities using evidence, economics and risk." },
  { id: "commerce-analytics", name: "Commerce Analytics", domain: "intelligence", permissionTier: 1, enabled: true, purpose: "Measure traffic, conversion, sales and profitability signals." },
  { id: "social-media-manager", name: "Social Media Manager", domain: "marketing", permissionTier: 1, enabled: true, purpose: "Monitor connected social channels and commerce signals." },
  { id: "compliance-risk", name: "Compliance & Risk", domain: "governance", permissionTier: 1, enabled: true, purpose: "Detect policy, legal, platform and operational risks." },
];
