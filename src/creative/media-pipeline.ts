export type MediaType = "image" | "video";

export interface MediaRequest {
  productId: string;
  type: MediaType;
  purpose: "cover" | "mockup" | "social" | "listing" | "short-form-video";
  prompt: string;
  aspectRatio: string;
}

export interface MediaJob {
  id: string;
  request: MediaRequest;
  status: "planned" | "queued" | "generated" | "approved" | "rejected";
}

export function createMediaJob(request: MediaRequest): MediaJob {
  if (!request.productId || !request.prompt) {
    throw new Error("Media request requires productId and prompt.");
  }

  return {
    id: `media-${Date.now()}`,
    request,
    status: "planned"
  };
}
