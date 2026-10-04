export type ApprovalStatus = "pending" | "approved" | "rejected" | "expired";

export interface ApprovalRequest {
  id: string;
  createdAt: string;
  agent: string;
  action: string;
  rationale: string;
  status: ApprovalStatus;
  reversible: boolean;
  estimatedCost?: number;
}

export function createApprovalRequest(input: Omit<ApprovalRequest, "createdAt" | "status">): ApprovalRequest {
  return { ...input, createdAt: new Date().toISOString(), status: "pending" };
}
