# n8n Workflow Compatibility & Risk Matrix

Status labels describe initial static inspection only. No workflow has been imported or executed.

| Capability | Candidate pattern | Initial status | Main limitation |
|---|---|---|---|
| Read PDF text | Manual Read PDF 1048 | ADAPT CONCEPT | Zero connection edges recorded; local path assumptions |
| Email PDF intake | Read PDF 0298 | REJECT AS-IS | Multiple noOp nodes, sparse graph, Gmail/OpenAI/Drive credentials |
| Binary/text conversion | Convert to File 0508 | ADAPT NODE ONLY | One connection edge and noOp node |
| PDF/image page extraction | Extract PDF/image to CSV 1444 | REBUILD AROUND CONCEPT | AI node noOp, external API and Drive uploads |
| Image resize | Edit Image 0575 | ADAPT NODE ONLY | PDF-to-image API and model placeholders |
| Structured content generation | Generate Exam Questions 1134 | INVESTIGATE | AI placeholders and multiple service credentials |
| Asset management | Graphic Design Team 1985 | INVESTIGATE | Writes to Drive/Sheets, sends email, noOp nodes |
| Document generation | Google Docs 0524 | REJECT AS-IS | No trigger, noOp AI/output parser, document and email side effects |
| Catalogue intake | Drive/Sheets 1806 | ADAPT CONCEPT | Sparse graph and noOp node |
| PDF binary file read | Manual Read PDF 1048 | ADAPT CONCEPT | No end-to-end graph observed |
| Image pipeline | Manual Edit Image 0137 | REJECT AS-IS | Zero connection edges recorded; HTTP/function code requires review |
| Markdown generation | Manual Markdown 0213 | REJECT AS-IS | Zero connection edges recorded; email side effect |
| Cloud backup | Drive to S3 0151 | REJECT AS-IS | Zero connection edges recorded; cloud credentials |
| Social post from Drive | Drive to Instagram 0839 | REJECT FOR PDF FACTORY | Direct publishing side effect and noOp caption generation |
| Spreadsheet to file | Convert to File 0889 | ADAPT CONCEPT | NoOp model; Drive and Sheets writes |
| Report generation | Google Docs 1279 | REJECT AS-IS | RAG/LLM placeholders and unrelated stock-report purpose |
| Local compression/database | Compression 1294 | REJECT | NoOp AI and local filesystem/database operations |
| HR document intake | Extract File 1254 | REJECT AS-IS | NoOp AI nodes and personal CV data |
| PDF reader duplicate | Read PDF 1656 | COMPARE/DUPLICATE CHECK | Appears to repeat the 0298 workflow family |
| Image-edit candidate | Code/Edit Image 0577 | INVESTIGATE | Model placeholder; remote HTTP endpoint; code requires audit |

## Import decision policy

Before any import:
- Validate JSON schema and graph connections.
- Confirm every required node type exists in the target n8n version.
- Replace every noOp placeholder with an implemented node or remove the branch.
- Inspect all Code/Function/Execute Command/SSH nodes.
- Review every HTTP URL, credential type, file path and write/delete operation.
- Replace sample IDs, URLs and destination folders.
- Disable activation and side effects during first import.
- Test against disposable sample data.
- Record test results before use with commercial product assets.

No direct-import recommendation is approved by the current audit.
