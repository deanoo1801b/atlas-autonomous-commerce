export type AuditSeverity = "info" | "warning" | "critical";

export interface AuditEvent {
  timestamp: string;
  agent: string;
  action: string;
  severity: AuditSeverity;
  outcome: "planned" | "completed" | "blocked" | "failed";
  details?: Record<string, unknown>;
}

export function createAuditEvent(
  event: Omit<AuditEvent, "timestamp">
): AuditEvent {
  return { timestamp: new Date().toISOString(), ...event };
}

export function audit(event: AuditEvent): void {
  // Structured JSON keeps the audit trail machine-readable and easy to ship
  // to persistent storage later. Never log credentials or access tokens.
  console.log(JSON.stringify(event));
}
