export type MediaType = "image" | "video";
export type SocialPlatform = "instagram" | "facebook" | "tiktok" | "youtube-shorts" | "pinterest";

export interface MediaRequest {
  productId: string;
  type: MediaType;
  purpose: "cover" | "mockup" | "social" | "listing" | "short-form-video";
  prompt: string;
  aspectRatio: string;
  platform?: SocialPlatform;
  fullPage?: boolean;
  minimumTextSizePx?: number;
  legibilitySafeArea?: boolean;
}

export interface MediaJob {
  id: string;
  request: MediaRequest;
  status: "planned" | "queued" | "generated" | "approved" | "rejected";
}

const PLATFORM_DEFAULTS: Record<SocialPlatform, {
  imageAspectRatio: string;
  videoAspectRatio: string;
  minimumTextSizePx: number;
}> = {
  instagram: { imageAspectRatio: "4:5", videoAspectRatio: "9:16", minimumTextSizePx: 44 },
  facebook: { imageAspectRatio: "4:5", videoAspectRatio: "9:16", minimumTextSizePx: 44 },
  tiktok: { imageAspectRatio: "9:16", videoAspectRatio: "9:16", minimumTextSizePx: 44 },
  "youtube-shorts": { imageAspectRatio: "9:16", videoAspectRatio: "9:16", minimumTextSizePx: 44 },
  pinterest: { imageAspectRatio: "2:3", videoAspectRatio: "9:16", minimumTextSizePx: 40 }
};

export function getMediaDefaults(
  platform: SocialPlatform,
  type: MediaType = "image"
): { aspectRatio: string; minimumTextSizePx: number; fullPage: boolean; legibilitySafeArea: boolean } {
  const defaults = PLATFORM_DEFAULTS[platform];
  return {
    aspectRatio: type === "video" ? defaults.videoAspectRatio : defaults.imageAspectRatio,
    minimumTextSizePx: defaults.minimumTextSizePx,
    fullPage: true,
    legibilitySafeArea: true
  };
}

export function createMediaJob(request: MediaRequest): MediaJob {
  if (!request.productId || !request.prompt) {
    throw new Error("Media request requires productId and prompt.");
  }

  if (request.platform) {
    const defaults = getMediaDefaults(request.platform, request.type);
    if (request.aspectRatio !== defaults.aspectRatio) {
      throw new Error(
        `Unsupported ${request.type} aspect ratio for ${request.platform}: ${request.aspectRatio}. Expected ${defaults.aspectRatio}.`
      );
    }
    if ((request.minimumTextSizePx ?? defaults.minimumTextSizePx) < defaults.minimumTextSizePx) {
      throw new Error(
        `Text is too small for ${request.platform}; use at least ${defaults.minimumTextSizePx}px in the source creative.`
      );
    }
    if (request.fullPage === false) {
      throw new Error("Social creatives must use a full-frame visual rather than a small inset image.");
    }
    if (request.legibilitySafeArea === false) {
      throw new Error("Social creatives must reserve a legibility-safe area for text and controls.");
    }
  }

  return {
    id: `media-${Date.now()}`,
    request: {
      ...request,
      fullPage: request.fullPage ?? true,
      legibilitySafeArea: request.legibilitySafeArea ?? true,
      minimumTextSizePx: request.minimumTextSizePx ?? (
        request.platform ? getMediaDefaults(request.platform, request.type).minimumTextSizePx : 44
      )
    },
    status: "planned"
  };
}
