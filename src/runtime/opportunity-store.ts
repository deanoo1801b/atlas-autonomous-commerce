import { appendFile, mkdir } from "node:fs/promises";
import { dirname } from "node:path";
import type { OpportunityRecord } from "./opportunity-report.js";

const file = "runtime-data/opportunities.jsonl";

export async function persistOpportunity(record: OpportunityRecord): Promise<void> {
  await mkdir(dirname(file), { recursive: true });
  await appendFile(file, JSON.stringify(record) + "\n", "utf8");
}
