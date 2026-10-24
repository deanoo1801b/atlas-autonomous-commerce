# Atlas Daily Content Bot

This first version reads active products from Atlas Goods Store, generates one original UK-English article, and creates a **Shopify blog draft**. It does not publish automatically or post to social media.

## Required configuration

In GitHub, open **Settings → Secrets and variables → Actions** for this repository and add:

- `SHOPIFY_STORE_DOMAIN`: `atlasgoodsstore.co.uk`
- `SHOPIFY_ADMIN_ACCESS_TOKEN`: a Shopify Admin API token with the minimum permissions needed to read products and create/read blog articles. Confirm exact scopes in the Shopify app setup.
- `SHOPIFY_BLOG_ID`: the numeric ID of the blog that should receive drafts.
- `OPENAI_API_KEY`: an OpenAI API key with API billing enabled.

Optional repository variable:
- `OPENAI_MODEL`: defaults to `gpt-4.1-mini`.

Never put tokens or API keys in code, commits, issue comments, or logs. If a secret is exposed, revoke and replace it immediately.

## Run it

1. Add the required secrets.
2. Open **Actions → Atlas Daily Content**.
3. Choose **Run workflow** to test.
4. Inspect the run log and the new draft in Shopify Admin.
5. Keep the scheduled workflow disabled until a manual run succeeds and the output is reviewed.

The schedule uses 08:15 UTC. This corresponds to 08:15 UK time during winter and 09:15 during British Summer Time. Adjust the cron schedule seasonally if exact local time is required.

## Current limitations

- Drafts only; automatic publication is intentionally disabled.
- Product selection rotates deterministically through the first 100 active products returned by Shopify.
- Recent-title checking reduces exact duplicates; it does not guarantee topic-level uniqueness.
- No social media publishing, keyword research provider, analytics ingestion, image generation, or sales attribution is implemented yet.
- Review every article for factual accuracy, usefulness, links, accessibility and SEO before publishing.
