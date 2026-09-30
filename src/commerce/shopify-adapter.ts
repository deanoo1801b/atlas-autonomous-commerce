export interface DigitalProductListing {
  title: string;
  description: string;
  price: number;
  currency: string;
  productType: string;
  tags: string[];
  seoTitle?: string;
  seoDescription?: string;
  slug?: string;
  filePath?: string;
}

export interface ShopifyAdapter {
  createDraft(listing: DigitalProductListing): Promise<{ id: string; status: "draft" }>;
}

export function createShopifyDraftAdapter(): ShopifyAdapter {
  return {
    async createDraft(listing) {
      if (!listing.title || !listing.description || listing.price < 0) {
        throw new Error("Invalid Shopify draft listing.");
      }
      return { id: `draft-${Date.now()}`, status: "draft" };
    }
  };
}
