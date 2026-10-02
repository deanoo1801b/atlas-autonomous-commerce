export type IntegrationId =
  | "github"
  | "shopify"
  | "canva"
  | "metricool"
  | "storage"
  | "research"
  | "translation"
  | "pod";

export interface IntegrationStatus {
  id: IntegrationId;
  configured: boolean;
  writeEnabled: boolean;
}

export const integrationRegistry: IntegrationStatus[] = [
  { id: "github", configured: true, writeEnabled: true },
  // Shopify connection is verified; commercial writes remain disabled until the publishing gate authorizes them.
  { id: "shopify", configured: true, writeEnabled: false },
  { id: "canva", configured: false, writeEnabled: false },
  { id: "metricool", configured: false, writeEnabled: false },
  { id: "storage", configured: false, writeEnabled: false },
  { id: "research", configured: false, writeEnabled: false },
  { id: "translation", configured: false, writeEnabled: false },
  { id: "pod", configured: false, writeEnabled: false }
];
