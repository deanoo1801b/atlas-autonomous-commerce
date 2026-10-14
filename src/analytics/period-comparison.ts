export interface PeriodMetrics {
  sessions: number;
  addToCarts: number;
  checkoutsStarted: number;
  orders: number;
  revenueGBP: number;
}

export interface MetricChange {
  metric: keyof PeriodMetrics;
  previous: number;
  current: number;
  absoluteChange: number;
  percentChange: number | null;
  direction: "up" | "down" | "unchanged" | "new-baseline";
}

export interface TrafficComparison {
  changes: MetricChange[];
  warnings: string[];
  requiresHumanReview: true;
}

/**
 * Compare two equal-length reporting periods. Pure/read-only: no API calls,
 * notifications, writes, or automated actions. A zero previous value yields
 * percentChange=null rather than a misleading infinite percentage.
 */
export function compareCommercePeriods(
  previous: PeriodMetrics,
  current: PeriodMetrics
): TrafficComparison {
  const keys: (keyof PeriodMetrics)[] = [
    "sessions", "addToCarts", "checkoutsStarted", "orders", "revenueGBP"
  ];
  const warnings: string[] = [];

  for (const [label, period] of [["previous", previous], ["current", current]] as const) {
    for (const key of keys) {
      const value = period[key];
      if (!Number.isFinite(value) || value < 0) {
        throw new Error(`${label} period metric ${key} must be a finite non-negative number.`);
      }
    }
  }

  const changes = keys.map(metric => {
    const before = previous[metric];
    const now = current[metric];
    const absoluteChange = now - before;
    const percentChange = before === 0 ? null : (absoluteChange / before) * 100;
    const direction: MetricChange["direction"] =
      before === 0 ? "new-baseline" :
      absoluteChange > 0 ? "up" :
      absoluteChange < 0 ? "down" : "unchanged";
    return { metric, previous: before, current: now, absoluteChange, percentChange, direction };
  });

  if (previous.sessions === 0) warnings.push("Previous period had no sessions; percentage comparisons are not meaningful for zero-baseline metrics.");
  if (current.sessions === 0) warnings.push("Current period has no sessions; verify analytics collection and date range before diagnosing a traffic collapse.");
  if (current.orders === 0) warnings.push("No orders in current period; verify order data and checkout tracking before drawing conclusions.");
  if (current.addToCarts > current.sessions) warnings.push("Add-to-cart count exceeds sessions; confirm metric definitions and reporting scope.");
  if (current.checkoutsStarted > current.sessions) warnings.push("Checkout starts exceed sessions; confirm metric definitions and reporting scope.");
  if (current.orders > current.checkoutsStarted && current.checkoutsStarted > 0) warnings.push("Orders exceed checkout starts; event windows or metric definitions may differ.");

  return { changes, warnings, requiresHumanReview: true };
}
