export interface MetricoolSnapshot {
  brandId: number;
  timezone: string;
  networks: string[];
  scheduledPosts: number;
  source: string;
  checkedAt: string;
}

export function buildMetricoolSnapshot(input: Omit<MetricoolSnapshot, "source">): MetricoolSnapshot {
  return { ...input, source: "Metricool connector/runtime adapter" };
}
