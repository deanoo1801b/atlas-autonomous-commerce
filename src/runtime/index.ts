import { runCycle } from "./runner.js";

runCycle().catch((error) => {
  console.error("ATLAS runtime failed:", error);
  process.exitCode = 1;
});
