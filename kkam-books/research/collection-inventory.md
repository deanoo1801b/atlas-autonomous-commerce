# KKAM BOOKS — n8n Collection Inventory

**Research date:** 2026-10-12  
**Source repository:** https://github.com/Zie619/n8n-workflows  
**Search dashboard:** https://zie619.github.io/n8n-workflows/

## Inventory result

A recursive Git tree request against the repository's current `main` branch returned tree SHA `94007c1445d9258a7da116646b79473e7c7c3282`, with `truncated=false`.

- Workflow JSON files under `workflows/`: **2,061**
- README-advertised collection: **4,343**
- Difference: **2,282 files** (the README may describe a different index/build, so the cause is not yet proven).
- Top-level workflow folders/categories observed: **over 100**; the repository README describes 15 organized categories, but the current tree is arranged primarily by node/integration folder.
- README also advertises 365 integrations and 29,445 nodes; these figures have not yet been independently recalculated from all JSON bodies.

**Full static scan completed:** GitHub Actions fetched and parsed all **2,061/2,061** workflow JSON bodies successfully (0 download/JSON parse failures) at tree SHA `94007c1445d9258a7da116646b79473e7c7c3282`. The scan was read-only; no workflows were imported or executed.

### Static scan findings

- 937 files contain at least one `noOp` node.
- 1,363 files have at least one connection reference that does not resolve to a node name or ID under the scanner's current graph check.
- 27,527 dangling source/target references were counted; the follow-up scan now separates source and target counts.
- 1,360 files use node IDs as connection-map source keys rather than node names. Standard n8n exports typically use node names as connection keys, so this is a major compatibility warning to validate against the target n8n version/schema.
- 895 files contain HTTP Request nodes.
- 657 files contain Code/Function nodes.
- 32 files contain shell/SSH-style node types.
- 267 files contain file/image/PDF processing node types.
- 1,155 files appear to contain write/publish/delete/send side-effect patterns under a conservative name/parameter heuristic.
- Keyword hits across all files: PDF/document 255; illustration/image 86; content production 919; catalogue/storage 830; commercial distribution 238; automation/reliability 2,047. These categories overlap and are keyword matches, not counts of usable workflows.

**Coverage caveat:** all current workflow JSON bodies have been fetched and JSON-parsed, and the repeatable scanner has been added to the repository. The results are static heuristic findings; graph checks can produce false positives and must be validated against n8n's import schema. A successful JSON parse is not proof of a valid or executable workflow. Deep audits are limited to the ranked candidates documented separately.

## Category counts observed in the current tree

The largest workflow folders include:
- Manual: 391
- Splitout: 194
- Code: 183
- HTTP: 176
- Telegram: 119
- Wait: 104
- Webhook: 65
- Sticky notes: 57
- Schedule: 52
- Google Sheets: 26
- NoOp: 24
- Extract from File: 21
- Error: 17
- Aggregate: 16

These are folder/file counts, not a count of workflows that use each node type.

## Key quality finding

The sample includes JSON files whose node names suggest AI or document generation, but whose corresponding nodes are `n8n-nodes-base.noOp`. Some multi-node files also have very few or zero connection edges. Such files are not safe to import as production-ready workflows without a full graph and node-parameter review.

The repository README describes the project itself as MIT-licensed. Each candidate's own metadata and any embedded third-party material must still be checked. A repository-level MIT notice does not grant rights to external APIs, example content, images, credentials or third-party services.

## Search strategy and next steps

1. Enumerate all `workflows/**/*.json` paths from the complete Git tree.
2. Search paths and JSON content for PDF/document conversion, image/illustration processing, storage, catalogue/database, content generation, Shopify, schedules, errors and approval gates.
3. Download and parse candidate JSONs; record node names/types, edge counts, noOp counts, code/shell nodes, credential types, HTTP destinations, file operations, hard-coded IDs and write side effects.
4. Rank by KKAM relevance and implementation risk, not popularity or labels.
5. Inspect the top ten in depth before recommending import.
6. Maintain a persistent coverage ledger and never label an uninspected file as audited.

## Initial evidence links

- Repository README: https://github.com/Zie619/n8n-workflows/blob/main/README.md
- MIT licence: https://github.com/Zie619/n8n-workflows/blob/main/LICENSE
- Recursive Git tree: https://api.github.com/repos/Zie619/n8n-workflows/git/trees/main?recursive=1
- Repository dashboard/API claims need independent comparison: https://zie619.github.io/n8n-workflows/
