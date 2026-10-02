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
    agent_id: "creative-video-production",
    name: "Creative & Video Production Agent",
    enabled: true,
    protected_actions: ["create_content"]
  },
  {
    agent_id: "compliance-brand-qa",
    name: "Compliance & Brand QA Agent",
    enabled: true,
    protected_actions: []
  },
  {
    agent_id: "experiment-ab-testing",
    name: "Experiment & A/B Testing Agent",
    enabled: true,
    protected_actions: []
  },
  {
    agent_id: "conversion-optimisation",
    name: "Conversion Optimisation Agent",
    enabled: true,
    protected_actions: []
  },
  {
    agent_id: "competitor-intelligence",
    name: "Competitor Intelligence Agent",
    enabled: true,
    protected_actions: []
  },
  {
    agent_id: "customer-demand-question-mining",
    name: "Customer Demand & Question Mining Agent",
    enabled: true,
    protected_actions: []
  },
  {
    agent_id: "seo-opportunity-intelligence",
    name: "SEO Opportunity Intelligence Agent",
    enabled: true,
    protected_actions: []
  },
  {
    agent_id: "email-retention",
    name: "Email Retention Agent",
    enabled: true,
    protected_actions: ["send_email"]
  },
  {
    agent_id: "customer-support-review-intelligence",
    name: "Customer Support & Review Intelligence Agent",
    enabled: true,
    protected_actions: []
  }
];
