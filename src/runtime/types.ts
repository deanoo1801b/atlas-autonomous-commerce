export type RuntimeMode = "DRY_RUN" | "APPROVAL_REQUIRED" | "EXECUTE";
export type AgentStatus = "READY" | "RUNNING" | "BLOCKED" | "ERROR" | "DISABLED" | "AWAITING_APPROVAL";

export interface Evidence {
  source: string;
  statement: string;
  confidence?: string;
}

export interface AuditEvent {
  event_id: string;
  timestamp: string;
  agent: string;
  action: string;
  mode: RuntimeMode;
  evidence: Evidence[];
  approval_required: boolean;
  result?: string;
  error?: string;
}

export interface AgentDefinition {
  agent_id: string;
  name: string;
  enabled: boolean;
  protected_actions: string[];
}

export interface AgentStatusRecord {
  agent_id: string;
  status: AgentStatus;
  last_checked: string;
  last_success?: string;
  message?: string;
  dependencies?: string[];
}
