import type { ProductBrief, ProductAsset, ProductionPackage } from "./types.js";

const defaultAssetPlan: ProductAsset[] = [
  { type: "cover", filename: "cover.png", purpose: "Primary product cover", status: "planned" },
  { type: "interior", filename: "interior-pages.pdf", purpose: "Customer-facing product pages", status: "planned" },
  { type: "mockup", filename: "product-mockup.png", purpose: "Store/product presentation", status: "planned" },
  { type: "social", filename: "social-pack.png", purpose: "Organic promotion", status: "planned" },
  { type: "listing", filename: "listing-copy.md", purpose: "Store listing content", status: "planned" }
];

export function createProductionPackage(brief: ProductBrief): ProductionPackage {
  if (!brief.title.trim() || !brief.audience.trim() || !brief.problem.trim()) {
    throw new Error("Product brief requires title, audience and problem.");
  }

  return {
    brief,
    assets: defaultAssetPlan.map(asset => ({ ...asset })),
    qcRequired: true,
    publishingBlocked: true
  };
}

export function approveAsset(pkg: ProductionPackage, filename: string): ProductionPackage {
  return {
    ...pkg,
    assets: pkg.assets.map(asset =>
      asset.filename === filename ? { ...asset, status: "approved" } : asset
    )
  };
}

export function isProductionReady(pkg: ProductionPackage): boolean {
  return pkg.assets.every(asset => asset.status === "approved") && pkg.qcRequired;
}
