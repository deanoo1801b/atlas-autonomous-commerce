export type PropertyLeadCategory =
  | "listing"
  | "auction"
  | "public_distress_notice"
  | "finance_request"
  | "joint_venture"
  | "planning_or_development";

export type PropertyLeadInput = {
  leadId?: string;
  category: PropertyLeadCategory;
  sourceName: string;
  sourceUrl: string;
  discoveredAt: string;
  propertyOrProjectLocation?: string;
  postcode?: string;
  askingPriceGbp?: number;
  sourcePublishedAt?: string;
  evidenceSummary?: string;
};

export type PropertyLeadValidation = {
  acceptedForReview: boolean;
  sourceUrlValid: boolean;
  verifiedOwnership: false;
  verifiedDistress: false;
  contactPermissionEstablished: false;
  missingFields: string[];
  quarantineReasons: string[];
  normalizedPostcode?: string;
};

/**
 * Evidence gate for UK property research.
 * Passing this check only means a record is structurally suitable for human review.
 * It never proves ownership, distress, willingness to sell, or contact permission.
 */
export function validatePropertyLead(
  lead: PropertyLeadInput
): PropertyLeadValidation {
  const missingFields: string[] = [];
  const quarantineReasons: string[] = [];
  let sourceUrlValid = false;

  try {
    const url = new URL(lead.sourceUrl);
    sourceUrlValid =
      (url.protocol === "https:" || url.protocol === "http:") &&
      Boolean(url.hostname) &&
      !/\s/.test(lead.sourceUrl);

    if (!sourceUrlValid) {
      quarantineReasons.push("Source URL must be a valid HTTP(S) URL with a hostname.");
    }
  } catch {
    quarantineReasons.push("Source URL is missing or malformed.");
  }

  if (!lead.sourceName.trim()) missingFields.push("sourceName");
  if (!lead.discoveredAt.trim() || Number.isNaN(Date.parse(lead.discoveredAt))) {
    missingFields.push("discoveredAt");
  }
  if (!lead.propertyOrProjectLocation?.trim()) {
    missingFields.push("propertyOrProjectLocation");
  }
  if (!lead.evidenceSummary?.trim()) missingFields.push("evidenceSummary");
  if (
    lead.askingPriceGbp !== undefined &&
    (!Number.isFinite(lead.askingPriceGbp) || lead.askingPriceGbp < 0)
  ) {
    quarantineReasons.push("Asking price must be a finite, non-negative GBP amount.");
  }

  const normalizedPostcode = lead.postcode
    ?.trim()
    .toUpperCase()
    .replace(/\s+/g, " ");

  // A source URL is mandatory before a record can enter the review queue.
  // Missing optional evidence is flagged, not silently fabricated.
  const acceptedForReview = sourceUrlValid && quarantineReasons.length === 0;

  return {
    acceptedForReview,
    sourceUrlValid,
    verifiedOwnership: false,
    verifiedDistress: false,
    contactPermissionEstablished: false,
    missingFields,
    quarantineReasons,
    normalizedPostcode,
  };
}
