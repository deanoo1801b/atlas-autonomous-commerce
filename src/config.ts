export type AtlasMode = "observe" | "recommend" | "controlled-write" | "autonomous";

export interface AtlasConfig {
  mode: AtlasMode;
  storeDomain: string;
  currency: string;
  country: string;
  dryRun: boolean;
  requireApprovalForWrites: boolean;
  requireApprovalForSpend: boolean;
}

function bool(name: string, fallback: boolean): boolean {
  const value = process.env[name];
  if (value === undefined) return fallback;
  return ["1", "true", "yes", "on"].includes(value.toLowerCase());
}

export function loadConfig(): AtlasConfig {
  return {
    mode: (process.env.ATLAS_MODE as AtlasMode | undefined) ?? "observe",
    storeDomain: process.env.SHOPIFY_STORE_DOMAIN ?? "atlasgoodsstore.co.uk",
    currency: process.env.ATLAS_CURRENCY ?? "GBP",
    country: process.env.ATLAS_COUNTRY ?? "GB",
    dryRun: bool("ATLAS_DRY_RUN", true),
    requireApprovalForWrites: bool("ATLAS_REQUIRE_APPROVAL_FOR_WRITES", true),
    requireApprovalForSpend: bool("ATLAS_REQUIRE_APPROVAL_FOR_SPEND", true),
  };
}
