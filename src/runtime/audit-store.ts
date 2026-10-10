import { appendFile, mkdir } from "node:fs/promises";
import { dirname } from "node:path";
import type { AuditEvent } from "../audit.js";

export async function persistAuditEvent(
  event: AuditEvent,
  filePath = process.env.ATLAS_AUDIT_PATH ?? "data/audit.jsonl"
): Promise<void> {
  await mkdir(dirname(filePath), { recursive: true });
  await appendFile(filePath, JSON.stringify(event) + "\n", { encoding: "utf8", mode: 0o600 });
}
