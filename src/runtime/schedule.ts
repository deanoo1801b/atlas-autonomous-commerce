import { runOpportunityScanner } from "./scanner.js";

export interface ScheduleConfig {
  intervalMinutes: number;
  enabled: boolean;
}

export async function runScheduledScanner(config: ScheduleConfig): Promise<void> {
  if (!config.enabled) return;
  await runOpportunityScanner();
}
