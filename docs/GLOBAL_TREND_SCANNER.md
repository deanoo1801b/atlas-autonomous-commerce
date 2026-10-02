# Global Trend Scanner Agent

The Global Trend Scanner is the early-signal layer of ATLAS.

## Sources

The scanner is designed for adapters covering Google Trends, TikTok, Etsy, Amazon, Pinterest, YouTube, Instagram, Reddit, Google Search and eBay.

The code intentionally separates **source adapters** from the scoring engine. A source is not treated as live or connected merely because it is listed. Credentials, API access and connector configuration must be verified before an adapter is enabled.

## Detection model

Each normalized signal records:

- trend velocity
- buyer intent
- engagement
- saturation / competition pressure
- seasonality
- keywords
- source and capture time

Signals are aggregated by topic. Cross-platform corroboration increases confidence.

## Commercial pipeline

Trend detected → cross-source corroboration → saturation check → buyer-intent check → market validation → profitability → product brief → production.

The scanner prioritizes **rising opportunities with manageable saturation**, rather than simply returning the biggest already-saturated trends.

## Safety

Trend evidence is an input to decision-making, not an automatic publishing instruction. Product creation and commercial publishing remain subject to ATLAS QC, risk controls and human approval gates.
