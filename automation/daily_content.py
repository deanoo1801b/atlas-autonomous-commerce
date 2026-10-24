"""Create one original, UK-focused Shopify blog draft from the live product catalogue.

Required GitHub Actions secrets:
  SHOPIFY_STORE_DOMAIN          e.g. atlasgoodsstore.co.uk
  SHOPIFY_ADMIN_ACCESS_TOKEN    Shopify Admin API token with product read + blog/article write scopes
  SHOPIFY_BLOG_ID               Numeric Shopify blog ID
  OPENAI_API_KEY                OpenAI API key

The bot deliberately creates drafts only. It does not publish automatically.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import sys
import time
from typing import Any

import requests

API_VERSION = "2025-10"
SHOP_DOMAIN = os.getenv("SHOPIFY_STORE_DOMAIN", "").strip().replace("https://", "").strip("/")
SHOP_TOKEN = os.getenv("SHOPIFY_ADMIN_ACCESS_TOKEN", "").strip()
BLOG_ID = os.getenv("SHOPIFY_BLOG_ID", "").strip()
OPENAI_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini").strip() or "gpt-4.1-mini"
PUBLISH_MODE = os.getenv("PUBLISH_MODE", "draft").lower()
TIMEOUT = 30


def require_config() -> None:
    missing = [name for name, value in {
        "SHOPIFY_STORE_DOMAIN": SHOP_DOMAIN,
        "SHOPIFY_ADMIN_ACCESS_TOKEN": SHOP_TOKEN,
        "SHOPIFY_BLOG_ID": BLOG_ID,
        "OPENAI_API_KEY": OPENAI_KEY,
    }.items() if not value]
    if missing:
        raise RuntimeError("Missing GitHub Actions secrets: " + ", ".join(missing))


def shopify_graphql(query: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
    url = f"https://{SHOP_DOMAIN}/admin/api/{API_VERSION}/graphql.json"
    response = requests.post(
        url,
        headers={
            "X-Shopify-Access-Token": SHOP_TOKEN,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        json={"query": query, "variables": variables or {}},
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    payload = response.json()
    if payload.get("errors"):
        raise RuntimeError("Shopify GraphQL error: " + json.dumps(payload["errors"])[:1500])
    return payload.get("data") or {}


def get_products() -> list[dict[str, Any]]:
    query = """
    query AtlasContentProducts {
      products(first: 100, sortKey: UPDATED_AT, reverse: true) {
        nodes {
          id title handle descriptionHtml productType status onlineStoreUrl
          tags
          variants(first: 1) { nodes { price } }
        }
      }
    }
    """
    data = shopify_graphql(query)
    nodes = data.get("products", {}).get("nodes", [])
    usable = []
    for product in nodes:
        if product.get("status") != "ACTIVE":
            continue
        title = (product.get("title") or "").strip()
        if not title:
            continue
        variant_nodes = (product.get("variants") or {}).get("nodes") or []
        price = variant_nodes[0].get("price") if variant_nodes else None
        usable.append({
            "id": product.get("id"),
            "title": title,
            "handle": product.get("handle"),
            "description": re.sub(r"<[^>]+>", " ", product.get("descriptionHtml") or "").strip()[:1200],
            "product_type": product.get("productType") or "",
            "tags": product.get("tags") or [],
            "price_gbp": price,
            "url": product.get("onlineStoreUrl") or f"https://{SHOP_DOMAIN}/products/{product.get('handle')}",
        })
    return usable


def blog_gid() -> str:
    # Accept either the Shopify GraphQL GID or the numeric blog ID from Admin.
    return BLOG_ID if BLOG_ID.startswith("gid://shopify/Blog/") else f"gid://shopify/Blog/{BLOG_ID}"


def existing_recent_titles() -> list[str]:
    query = """
    query AtlasRecentArticles($blogId: ID!) {
      blog(id: $blogId) {
        articles(first: 50, sortKey: CREATED_AT, reverse: true) {
          nodes { title }
        }
      }
    }
    """
    data = shopify_graphql(query, {"blogId": blog_gid()})
    blog = data.get("blog") or {}
    return [a.get("title", "") for a in (blog.get("articles") or {}).get("nodes", []) if a.get("title")]


def choose_product(products: list[dict[str, Any]], recent_titles: list[str]) -> dict[str, Any]:
    # Rotate deterministically by UK calendar date; title similarity is handled in the prompt.
    today = dt.datetime.now(dt.timezone.utc).date()
    offset = today.toordinal() % len(products)
    return products[offset]


def generate_article(product: dict[str, Any], recent_titles: list[str]) -> dict[str, str]:
    today = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
    prompt = f"""
You are the UK ecommerce content editor for Atlas Goods Store (https://{SHOP_DOMAIN}).
Write one genuinely useful, original, UK-English blog article that helps a UK shopper make a decision.
Use British spelling, GBP only when price is supplied, and never invent product features, certifications,
stock claims, delivery times, discounts, reviews, test results, safety claims, or performance guarantees.
Do not claim the product has been independently tested. Avoid keyword stuffing and generic filler.
The article must provide useful advice beyond advertising. Naturally include one relevant internal product link.
Return STRICT JSON only with keys: title, meta_description, html.
- title: specific and useful, ideally under 65 characters; not clickbait.
- meta_description: compelling, factual, ideally 140-160 characters.
- html: valid Shopify article HTML, 700-1000 words, one H1 is not needed because Shopify renders the title.
  Use H2/H3 headings, short paragraphs, a practical checklist or numbered steps where useful,
  3-5 relevant FAQs, and a clear but non-pushy closing CTA with the supplied product link.
  Do not include JSON markdown fences.
Today's date: {today}
Product data (treat as facts only; do not infer missing details):
{json.dumps(product, ensure_ascii=False)}
Recent article titles to avoid repeating:
{json.dumps(recent_titles[-50:], ensure_ascii=False)}
Create a topic that fits the product and offers genuinely distinct informational value.
"""
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"},
        json={
            "model": OPENAI_MODEL,
            "temperature": 0.7,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": "You create accurate, useful UK ecommerce articles and return valid JSON only."},
                {"role": "user", "content": prompt},
            ],
        },
        timeout=90,
    )
    response.raise_for_status()
    payload = response.json()
    content = payload["choices"][0]["message"]["content"]
    article = json.loads(content)
    for key in ("title", "meta_description", "html"):
        if not isinstance(article.get(key), str) or not article[key].strip():
            raise RuntimeError(f"AI output missing required field: {key}")
    if len(article["html"]) < 1500:
        raise RuntimeError("Generated article failed minimum-length quality gate; refusing to create a draft.")
    if article["title"].strip().lower() in {t.strip().lower() for t in recent_titles}:
        raise RuntimeError("Duplicate article title detected; refusing to create a draft.")
    if "https://" + SHOP_DOMAIN not in article["html"]:
        raise RuntimeError("Article is missing a link to the store; refusing to create a draft.")
    return article


def create_draft(article: dict[str, str]) -> str:
    mutation = """
    mutation AtlasCreateArticle($article: ArticleCreateInput!) {
      articleCreate(article: $article) {
        article { id title handle isPublished }
        userErrors { field message }
      }
    }
    """
    variables = {
        "article": {
            "blogId": blog_gid(),
            "title": article["title"].strip(),
            "body": article["html"],
            "isPublished": False,
        }
    }
    data = shopify_graphql(mutation, variables)
    result = data.get("articleCreate") or {}
    errors = result.get("userErrors") or []
    if errors:
        raise RuntimeError("Shopify article creation errors: " + json.dumps(errors)[:1500])
    created = result.get("article") or {}
    if not created.get("id"):
        raise RuntimeError("Shopify did not return an article ID.")
    return f"https://{SHOP_DOMAIN}/admin/articles/{created['id'].split('/')[-1]}"


def main() -> int:
    require_config()
    products = get_products()
    if not products:
        raise RuntimeError("No active products found. Nothing was created.")
    titles = existing_recent_titles()
    product = choose_product(products, titles)
    print(f"Selected product: {product['title']!r} (details limited to Shopify catalogue data)")
    article = generate_article(product, titles)
    draft_url = create_draft(article)
    print("Created Shopify blog draft successfully.")
    print(f"Title: {article['title']}")
    print(f"Draft admin URL: {draft_url}")
    print("Publishing mode is draft; no public article was published.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
