export type TrendSource =
  | "google-trends"
  | "tiktok"
  | "etsy"
  | "amazon"
  | "pinterest"
  | "youtube"
  | "instagram"
  | "reddit"
  | "google-search"
  | "ebay";

export interface TrendSignal {
  source: TrendSource;
  topic: string;
  keywords: string[];
  capturedAt: string;
  velocity: number;
  buyerIntent: number;
  engagement: number;
  saturation: number;
  seasonality: number;
  evidenceUrl?: string;
}

export interface AggregatedTrend {
  topic: string;
  sources: TrendSource[];
  keywords: string[];
  signalCount: number;
  velocity: number;
  buyerIntent: number;
  engagement: number;
  saturation: number;
  seasonality: number;
  score: number;
  confidence: number;
}

const clamp = (value: number) => Math.max(0, Math.min(1, value));

export const TREND_SOURCES: readonly TrendSource[] = [
  "google-trends", "tiktok", "etsy", "amazon", "pinterest",
  "youtube", "instagram", "reddit", "google-search", "ebay"
];

export function scoreTrendSignal(signal: TrendSignal): number {
  return clamp(
    signal.velocity * 0.30 +
    signal.buyerIntent * 0.25 +
    signal.engagement * 0.15 +
    (1 - signal.saturation) * 0.20 +
    signal.seasonality * 0.10
  );
}

function normalizeTopic(topic: string): string {
  return topic.trim().toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
}

export function aggregateTrendSignals(signals: TrendSignal[]): AggregatedTrend[] {
  const groups = new Map<string, TrendSignal[]>();

  for (const signal of signals) {
    if (!signal.topic.trim()) continue;
    const key = normalizeTopic(signal.topic);
    const existing = groups.get(key) ?? [];
    existing.push(signal);
    groups.set(key, existing);
  }

  return [...groups.entries()]
    .map(([topic, group]) => {
      const average = (selector: (s: TrendSignal) => number) =>
        group.reduce((sum, item) => sum + selector(item), 0) / group.length;
      const sources = [...new Set(group.map(item => item.source))];
      const score = clamp(
        average(scoreTrendSignal) * 0.75 +
        Math.min(1, sources.length / 4) * 0.25
      );

      return {
        topic,
        sources,
        keywords: [...new Set(group.flatMap(item => item.keywords))],
        signalCount: group.length,
        velocity: average(item => item.velocity),
        buyerIntent: average(item => item.buyerIntent),
        engagement: average(item => item.engagement),
        saturation: average(item => item.saturation),
        seasonality: average(item => item.seasonality),
        score,
        confidence: clamp(
          0.45 +
          Math.min(0.30, sources.length * 0.075) +
          Math.min(0.20, group.length * 0.02)
        )
      };
    })
    .sort((a, b) => b.score - a.score);
}

export function findEarlySignals(signals: TrendSignal[]): AggregatedTrend[] {
  return aggregateTrendSignals(signals).filter(
    trend => trend.velocity >= 0.60 &&
      trend.saturation <= 0.70 &&
      trend.confidence >= 0.60
  );
}
