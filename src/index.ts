type AtlasMode = "observe" | "recommend" | "controlled-write" | "autonomous";

const mode = (process.env.ATLAS_MODE ?? "observe") as AtlasMode;

const allowedModes: AtlasMode[] = [
  "observe",
  "recommend",
  "controlled-write",
  "autonomous"
];

if (!allowedModes.includes(mode)) {
  throw new Error(`Invalid ATLAS_MODE: ${mode}`);
}

console.log("ATLAS initialised");
console.log(`Mode: ${mode}`);
console.log("Objective: build a measurable commerce engine toward £1,000,000 cumulative gross revenue.");
console.log("Default safety posture: observe first, execute only with explicit permissions.");
