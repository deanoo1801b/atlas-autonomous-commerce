import { runCycle } from "./runner.js";

runCycle().catch((error) => {
  console.error("ATLAS runtime failed:", error);
  process.exitCode = 1;
});

// External Shopify/Metricool adapters are intentionally read-only contracts at this stage.\n