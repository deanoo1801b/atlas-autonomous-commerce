import { runOpportunityScanner } from "./scanner.js";
import type { RuntimeMode } from "./types.js";

export interface ScheduleConfig {
  intervalMinutes: number;
  enabled: boolean;
  mode?: RuntimeMode;
}

export async function runScheduledScanner(config: ScheduleConfig): Promise<void> {
  if (!config.enabled) return;
  await runOpportunityScanner(config.mode ?? "DRY_RUN");
}
