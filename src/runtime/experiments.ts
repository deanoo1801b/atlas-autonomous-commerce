import { appendFile, mkdir } from "node:fs/promises";
import { dirname } from "node:path";

export interface ExperimentRecord {
  experiment_id: string;
  created_at: string;
  hypothesis: string;
  primary_variable: string;
  metric: string;
  status: "DESIGNED" | "RUNNING" | "COMPLETED" | "CANCELLED";
  result?: string;
  confidence?: "LOW" | "MEDIUM" | "HIGH";
}

const file = "runtime-data/experiments.jsonl";

export async function persistExperiment(record: ExperimentRecord): Promise<void> {
  await mkdir(dirname(file), { recursive: true });
  await appendFile(file, JSON.stringify(record) + "\n", "utf8");
}
