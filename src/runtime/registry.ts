import type { AgentDefinition } from "./types.js";

export const agentRegistry: AgentDefinition[] = [
  {
    agent_id: "product-opportunity",
    name: "Product Opportunity & Evidence Agent",
    enabled: true,
    protected_actions: ["create_content", "publish"]
  },
  {
    agent_id: "trend-research",
    name: "Trend Research Agent",
    enabled: true,
    protected_actions: []
  },
  {
    agent_id: "analytics-attribution",
    name: "Analytics & Attribution Agent",
    enabled: true,
    protected_actions: []
  },
  {
    agent_id: "social-media-manager",
    name: "Social Media Manager Agent",
    enabled: true,
    protected_actions: ["publish"]
  },
  {
    agent_id: "compliance-brand-qa",
    name: "Compliance & Brand QA Agent",
    enabled: true,
    protected_actions: []
  }
];
