import process from "node:process";

const now = new Date().toISOString();
const SHOPIFY_API_VERSION = process.env.SHOPIFY_API_VERSION || "2026-10";
const results = { checkedAt: now, shopify: null, metricool: null };

function missingFor(keys) {
  return keys.filter((key) => !process.env[key]);
}

async function checkShopify() {
  const required = ["SHOPIFY_STORE_DOMAIN", "SHOPIFY_ADMIN_ACCESS_TOKEN"];
  const missing = missingFor(required);
  if (missing.length) {
    return { status: "BLOCKED", reason: "Missing required GitHub Actions secrets", missing };
  }

  const domain = process.env.SHOPIFY_STORE_DOMAIN.replaceAll("https:", "").replaceAll("http:", "").replaceAll("/", "");
  const response = await fetch(`https://${domain}/admin/api/${SHOPIFY_API_VERSION}/graphql.json`, {
    method: "POST",
    signal: AbortSignal.timeout(15000),
    headers: {
      "Content-Type": "application/json",
      "X-Shopify-Access-Token": process.env.SHOPIFY_ADMIN_ACCESS_TOKEN
    },
    body: JSON.stringify({
      query: `query AtlasReadOnlyHealth { shop { name myshopifyDomain primaryDomain { url } currencyCode } productsCount(query: "status:active") { count } }`
    })
  });
  if (!response.ok) throw new Error(`Shopify HTTP ${response.status}`);
  const body = await response.json();
  if (body.errors?.length) throw new Error("Shopify GraphQL returned errors");
  const shop = body.data?.shop;
  if (!shop) throw new Error("Shopify response missing shop data");
  return {
    status: "CONNECTED",
    apiVersion: SHOPIFY_API_VERSION,
    shopName: shop.name,
    myshopifyDomain: shop.myshopifyDomain,
    primaryDomain: shop.primaryDomain?.url,
    currency: shop.currencyCode,
    activeProductCount: body.data?.productsCount?.count ?? null
  };
}

async function checkMetricool() {
  const required = ["METRICOOL_API_TOKEN", "METRICOOL_USER_ID"];
  const missing = missingFor(required);
  if (missing.length) {
    return { status: "BLOCKED", reason: "Missing required GitHub Actions secrets", missing };
  }

  const userId = process.env.METRICOOL_USER_ID;
  const response = await fetch(`https://app.metricool.com/api/admin/simpleProfiles?userId=${encodeURIComponent(userId)}`, {
    signal: AbortSignal.timeout(15000),
    headers: { "X-Mc-Auth": process.env.METRICOOL_API_TOKEN, "Accept": "application/json" }
  });
  if (!response.ok) throw new Error(`Metricool HTTP ${response.status}`);
  const body = await response.json();
  const brands = Array.isArray(body) ? body : (body.data ?? body.profiles ?? []);
  const target = brands.find((brand) => /atlas goods|atlasgoodsstore/i.test(String(brand.label ?? brand.name ?? "")));
  if (!target) {
    return {
      status: "BLOCKED",
      reason: "Authenticated Metricool account did not return an Atlas Goods brand",
      availableBrandNames: brands.map((brand) => String(brand.label ?? brand.name ?? "Unnamed brand"))
    };
  }
  return {
    status: "CONNECTED",
    brandId: target.id ?? target.blogId,
    brandName: target.label ?? target.name,
    networks: Object.keys(target.networksData ?? {}).filter((key) => target.networksData[key])
  };
}

try { results.shopify = await checkShopify(); }
catch (error) { results.shopify = { status: "ERROR", reason: String(error.message ?? error) }; }
try { results.metricool = await checkMetricool(); }
catch (error) { results.metricool = { status: "ERROR", reason: String(error.message ?? error) }; }

console.log(JSON.stringify(results, null, 2));
if (results.shopify.status !== "CONNECTED" || results.metricool.status !== "CONNECTED") process.exitCode = 1;
