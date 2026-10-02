# Runtime Data

This directory is reserved for local runtime evidence and audit output.

Rules:
- Read-only external adapters feed snapshots into the runtime.
- External writes remain blocked unless explicitly approved.
- Every snapshot should include source and timestamp.
- Never treat a partial catalogue scan as a complete catalogue.
- Never infer sales, bestseller status, or causal attribution without evidence.
