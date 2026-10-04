import { appendFile, mkdir } from "node:fs/promises";
import { dirname } from "node:path";

export interface ApprovalRequest {
  request_id: string;
  created_at: string;
  action: string;
  agent: string;
  reason: string;
  payload_summary: string;
  status: "PENDING" | "APPROVED" | "REJECTED" | "EXPIRED";
}

const file = "runtime-data/approval-queue.jsonl";

export async function enqueueApproval(request: ApprovalRequest): Promise<void> {
  await mkdir(dirname(file), { recursive: true });
  await appendFile(file, JSON.stringify(request) + "\n", "utf8");
}
