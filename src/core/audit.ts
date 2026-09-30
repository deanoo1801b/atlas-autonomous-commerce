export interface AuditEvent { timestamp: string; event: string; taskId?: string; agentId?: string; details?: Record<string, unknown>; }
const events: AuditEvent[] = [];
export function audit(event: AuditEvent): AuditEvent { events.push(event); return event; }
export function getAuditEvents(): readonly AuditEvent[] { return events; }
