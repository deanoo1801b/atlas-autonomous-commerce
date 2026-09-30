export type ProductFormat = "ebook" | "workbook" | "planner" | "checklist" | "template" | "guide" | "bundle";

export interface ProductBrief {
  id: string;
  title: string;
  audience: string;
  problem: string;
  promise: string;
  format: ProductFormat;
  sections: string[];
  keywords: string[];
  marketEvidence: string[];
  targetPrice?: number;
  currency?: string;
}

export interface ProductAsset {
  type: "cover" | "interior" | "mockup" | "social" | "listing";
  filename: string;
  purpose: string;
  status: "planned" | "generated" | "approved" | "rejected";
}

export interface ProductionPackage {
  brief: ProductBrief;
  assets: ProductAsset[];
  qcRequired: boolean;
  publishingBlocked: boolean;
}
