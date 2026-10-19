import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";

const topic = (process.env.VIDEO_TOPIC || "Atlas Goods Store: everyday essentials").trim().slice(0, 180);
const price = (process.env.VIDEO_PRODUCT_PRICE || "£14.99").trim().slice(0, 32);
const productUrl = (process.env.VIDEO_PRODUCT_URL || "https://atlasgoodsstore.co.uk/products/long-handle-floor-scrub-brush-with-squeegee").trim();
const imageUrl = (process.env.VIDEO_PRODUCT_IMAGE_URL || "").trim();
const brand = "ATLAS GOODS STORE";
const outDir = "video-output";
fs.mkdirSync(outDir, { recursive: true });
if (!/^https:\/\/atlasgoodsstore\.co\.uk\/products\/[a-z0-9-]+\/?$/i.test(productUrl)) throw new Error("Product URL must be an Atlas Goods Store product page.");
if (!/^https:\/\/cdn\.shopify\.com\//i.test(imageUrl)) throw new Error("Product image must be a public HTTPS Shopify CDN URL.");
const imageResponse = await fetch(imageUrl, { signal: AbortSignal.timeout(15000) });
if (!imageResponse.ok) throw new Error("Product image download failed: HTTP " + imageResponse.status);
const imageType = (imageResponse.headers.get("content-type") || "").toLowerCase();
const imageExt = imageType.includes("png") ? "png" : imageType.includes("webp") ? "webp" : "jpg";
const productImagePath = outDir + "/product-image." + imageExt;
fs.writeFileSync(productImagePath, Buffer.from(await imageResponse.arrayBuffer()));

function esc(s) {
  return s.replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;").replaceAll("'", "&apos;");
}
function wrap(text, max = 24) {
  const words = text.split(/\s+/);
  const lines = [];
  let line = "";
  for (const word of words) {
    if ((line + " " + word).trim().length > max && line) {
      lines.push(line);
      line = word;
    } else line = (line + " " + word).trim();
  }
  if (line) lines.push(line);
  return lines.slice(0, 4);
}
const scenes = [
  { heading: "A PRACTICAL EVERYDAY PICK", sub: topic },
  { heading: "DESIGNED FOR THE TASK", sub: "A handy option for your cleaning routine." },
  { heading: "CLEAR PRICE. SIMPLE SHOPPING.", sub: price },
  { heading: "SHOP ATLAS GOODS STORE", sub: "Free UK shipping." },
  { heading: "DISCOVER THIS PRODUCT", sub: "Tap through to view the details." }
];

const clipPaths = [];
for (let i = 0; i < scenes.length; i++) {
  const s = scenes[i];
  const lines = wrap(s.sub);
  const subtitle = lines.map((line, j) =>
    `<text x="540" y="${1370 + j * 54}" text-anchor="middle" font-family="DejaVu Sans" font-size="40" fill="#f5f5f5">${esc(line)}</text>`
  ).join("");
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920"><defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#101b36"/><stop offset="100%" stop-color="#80662b"/></linearGradient></defs><rect width="1080" height="1920" fill="url(#g)"/><circle cx="540" cy="540" r="240" fill="none" stroke="#d6bd75" stroke-width="3" opacity=".7"/><circle cx="540" cy="540" r="190" fill="none" stroke="#d6bd75" stroke-width="2" opacity=".45"/><text x="540" y="220" text-anchor="middle" font-family="DejaVu Sans" font-size="32" letter-spacing="8" fill="#d6bd75">${brand}</text><text x="540" y="720" text-anchor="middle" font-family="DejaVu Sans" font-size="54" font-weight="bold" fill="#ffffff">${esc(s.heading)}</text>${subtitle}<text x="540" y="1700" text-anchor="middle" font-family="DejaVu Sans" font-size="28" fill="#d6bd75">UK STORE • FREE UK SHIPPING</text><text x="540" y="1780" text-anchor="middle" font-family="DejaVu Sans" font-size="25" fill="#ffffff">ATLASGOODSSTORE.CO.UK</text><text x="1000" y="1850" text-anchor="end" font-family="DejaVu Sans" font-size="24" fill="#ffffff">${String(i + 1).padStart(2, "0")} / ${scenes.length}</text></svg>`;
  const svgPath = `${outDir}/scene-${i + 1}.svg`;
  const pngPath = `${outDir}/scene-${i + 1}.png`;
  const wavPath = `${outDir}/scene-${i + 1}.wav`;
  const mp4Path = `${outDir}/scene-${i + 1}.mp4`;
  fs.writeFileSync(svgPath, svg);
  execFileSync("rsvg-convert", ["-o", pngPath, svgPath]);
  execFileSync("espeak", ["-s", "145", "-w", wavPath, `${s.heading}. ${s.sub}`]);
  execFileSync("ffmpeg", ["-y", "-loop", "1", "-i", pngPath, "-loop", "1", "-i", productImagePath, "-i", wavPath, "-filter_complex", "[1:v]scale=700:520:force_original_aspect_ratio=decrease,pad=700:520:(ow-iw)/2:(oh-ih)/2:color=white[prod];[0:v][prod]overlay=(W-w)/2:800,format=yuv420p[v]", "-map", "[v]", "-map", "2:a", "-c:v", "libx264", "-tune", "stillimage", "-c:a", "aac", "-shortest", "-pix_fmt", "yuv420p", mp4Path], { stdio: "inherit" });
  clipPaths.push(mp4Path);
}
const listPath = `${outDir}/concat.txt`;
fs.writeFileSync(listPath, clipPaths.map(p => `file '${path.basename(p)}'`).join("\n"));
execFileSync("ffmpeg", ["-y", "-f", "concat", "-safe", "0", "-i", listPath, "-c", "copy", "-movflags", "+faststart", `${outDir}/atlas-video-draft.mp4`], { stdio: "inherit" });
fs.writeFileSync(outDir + "/CAPTION.txt", topic + " — " + price + "\n\nView product details: " + productUrl + "\n\nFree UK shipping from Atlas Goods Store.\n\n#AtlasGoodsStore #UKShopping #HomeEssentials\n\nDRAFT ONLY: Check current price, stock, delivery terms and final edit before publishing. This prototype uses the product image and synthetic speech; it does not auto-publish.\n");
console.log("Created video-output/atlas-video-draft.mp4");
