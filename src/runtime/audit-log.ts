import { appendFile, mkdir } from "node:fs/promises";
import { dirname } from "node:path";
import type { AuditEvent } from "./types.js";

const auditPath = process.env.ATLAS_AUDIT_LOG ?? "runtime-data/audit-events.jsonl";

export async function recordAudit(event: AuditEvent): Promise<void> {
  await mkdir(dirname(auditPath), { recursive: true });
  await appendFile(auditPath, JSON.stringify(event) + "\n", "utf8");
}
