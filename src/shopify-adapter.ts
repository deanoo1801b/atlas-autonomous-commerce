export interface ShopifyProductSummary {
  id: string;
  title: string;
  status?: string;
  vendor?: string;
  productType?: string;
  inventoryTotal?: number;
}

export interface ShopifyAdapter {
  listProducts(input?: { first?: number; query?: string }): Promise<ShopifyProductSummary[]>;
  runAnalytics(query: string): Promise<unknown>;
}

export class ReadOnlyShopifyAdapter implements ShopifyAdapter {
  async listProducts(): Promise<ShopifyProductSummary[]> {
    throw new Error("Shopify adapter not connected: configure an approved read-only connector.");
  }

  async runAnalytics(_query: string): Promise<unknown> {
    throw new Error("Shopify analytics adapter not connected: configure an approved read-only connector.");
  }
}
