export interface SEOPageSnapshot {
  url: string;
  html: string;
}

export interface SEOAuditFinding {
  id: string;
  severity: "critical" | "warning" | "info";
  message: string;
}

export interface SEOAuditReport {
  url: string;
  findings: SEOAuditFinding[];
  requiresHumanReview: true;
}

/**
 * Deterministic, read-only SEO checks adapted from the useful checklist idea
 * in the upstream On-Page SEO Audit template. This function does not fetch URLs,
 * call an AI model, email reports, or change Shopify content.
 */
export function auditSEOPage(snapshot: SEOPageSnapshot): SEOAuditReport {
  const url = validateAtlasUrl(snapshot.url);
  const html = snapshot.html;
  const findings: SEOAuditFinding[] = [];

  const title = html.match(/<title\\b[^>]*>([\\s\\S]*?)<\\/title>/i)?.[1]?.replace(/\\s+/g, " ").trim();
  const description = html.match(/<meta\\b[^>]*name=[\"']description[\"'][^>]*content=[\"']([^\"']*)[\"'][^>]*>/i)?.[1]?.trim()
    ?? html.match(/<meta\\b[^>]*content=[\"']([^\"']*)[\"'][^>]*name=[\"']description[\"'][^>]*>/i)?.[1]?.trim();
  const h1s = [...html.matchAll(/<h1\\b[^>]*>([\\s\\S]*?)<\\/h1>/gi)];
  const canonical = html.match(/<link\\b[^>]*rel=[\"']canonical[\"'][^>]*href=[\"']([^\"']+)[\"'][^>]*>/i)?.[1]
    ?? html.match(/<link\\b[^>]*href=[\"']([^\"']+)[\"'][^>]*rel=[\"']canonical[\"'][^>]*>/i)?.[1];
  const noindex = /<meta\\b[^>]*name=[\"']robots[\"'][^>]*content=[\"'][^\"']*noindex/i.test(html);
  const images = [...html.matchAll(/<img\\b[^>]*>/gi)].map(match => match[0]);
  const missingAlt = images.filter(tag => !/\\balt=[\"'][^\"']*[\"']/i.test(tag));

  if (!title) findings.push({ id: "missing-title", severity: "critical", message: "No HTML title tag found." });
  else if (title.length < 20 || title.length > 65) findings.push({ id: "title-length", severity: "warning", message: `Title is ${title.length} characters; review whether it is descriptive and concise (rough guide: 20–65).` });

  if (!description) findings.push({ id: "missing-meta-description", severity: "warning", message: "No meta description found." });
  else if (description.length < 70 || description.length > 170) findings.push({ id: "meta-description-length", severity: "info", message: `Meta description is ${description.length} characters; review its clarity and length (rough guide: 70–170).` });

  if (h1s.length === 0) findings.push({ id: "missing-h1", severity: "warning", message: "No H1 heading found." });
  if (h1s.length > 1) findings.push({ id: "multiple-h1", severity: "info", message: `Found ${h1s.length} H1 headings; check that the page hierarchy is intentional.` });
  if (!canonical) findings.push({ id: "missing-canonical", severity: "warning", message: "No canonical link found; confirm whether one is required." });
  else {
    try {
      const canonicalUrl = new URL(canonical, url);
      if (canonicalUrl.hostname !== "atlasgoodsstore.co.uk" && !canonicalUrl.hostname.endsWith(".atlasgoodsstore.co.uk")) {
        findings.push({ id: "external-canonical", severity: "critical", message: "Canonical points outside the Atlas Goods Store domain." });
      }
    } catch {
      findings.push({ id: "invalid-canonical", severity: "warning", message: "Canonical URL could not be parsed." });
    }
  }
  if (noindex) findings.push({ id: "noindex", severity: "critical", message: "Page contains a noindex directive; confirm this is intentional before publishing." });
  if (missingAlt.length) findings.push({ id: "image-alt-missing", severity: "warning", message: `${missingAlt.length} of ${images.length} images have no alt attribute; review meaningful alt text.` });
  if (!findings.length) findings.push({ id: "basic-checks-passed", severity: "info", message: "Basic static checks passed; this is not a complete SEO or ranking assessment." });

  return { url: url.toString(), findings, requiresHumanReview: true };
}

function validateAtlasUrl(input: string): URL {
  let url: URL;
  try {
    url = new URL(input);
  } catch {
    throw new Error("A valid absolute URL is required.");
  }
  if (url.protocol !== "https:") throw new Error("Only HTTPS URLs are accepted.");
  if (url.username || url.password) throw new Error("URLs containing credentials are not accepted.");
  if (url.hostname !== "atlasgoodsstore.co.uk" && !url.hostname.endsWith(".atlasgoodsstore.co.uk")) {
    throw new Error("SEO audit is restricted to atlasgoodsstore.co.uk URLs.");
  }
  return url;
}
