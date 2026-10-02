export interface ShopifySnapshot {
  shop: string;
  activeProductCountObserved: number;
  catalogueScanComplete: boolean;
  sessions30d?: number;
  completedCheckouts30d?: number;
  productSalesRows?: number;
  source: string;
  checkedAt: string;
}

export function buildShopifySnapshot(input: Omit<ShopifySnapshot, "source">): ShopifySnapshot {
  return { ...input, source: "Shopify connector/runtime adapter" };
}
