# KQ46 derivation receipt (scratch, seat dir)

Round 37 wave 1, ScribeKQ46. Read-only re-derivation of the ids the row cites.

## Defect source
- `corpus/lessons/round-36-verifier-spotcheck.md` §6 item 2 (D2), lines 179-190.
  Corrections it names: `S366` → `S371` (the `native_api.mdx` staged row);
  "`S359`, `S360`, `S372` and `S391`" → `S364`, `S365`, `S377`, `S396` (the
  `http_server.py` staged rows); "`cites S331-S334`" → `cites S332, S336, S337, S338, S339`.
  Every decision stands; only the id evidence is wrong.
- `corpus/lessons/round-36.md` lines 39, 41, 43 carry the three wrong citations.

## Artifact read (read-only package)
Artifact: `/home/vgpnk/Projects/shokuknow/merge/kama/SOURCES.append.md` (staged registry).

| id | line | row subject |
|---|---|---|
| S332 | 9 | vLLM Engine Arguments — https://docs.vllm.ai/en/v0.32.0/configuration/engine_args/ |
| S336 | 13 | SGLang in llm-d |
| S337 | 14 | Docker Compose file reference |
| S338 | 15 | Dockerfile reference |
| S339 | 16 | Prometheus blackbox_exporter README |
| S359 | 36 | vLLM health API (pinned source view) |
| S364 | 41 | SGLang `http_server.py` (released revision) |
| S365 | 42 | SGLang `http_server.py` (released revision) |
| S366 | 43 | AWS SageMaker custom inference code (zh_cn) |
| S371 | 48 | SGLang Native APIs — native_api.mdx at v0.5.22 |
| S372 | 49 | `lanes/kama/round4/evidence/gc-health-protocol-locale-diff.txt` (kama round-4 evidence artifact) |
| S377 | 54 | SGLang `http_server.py` at v0.5.22 |
| S391 | 68 | Azure ML custom-container deployment contract (BYOC) |
| S396 | 73 | SGLang `http_server.py` at v0.5.22 |

Second artifact: `/home/vgpnk/Projects/shokuknow/merge/kama/amendments/corpus/knowledge/endpoint-health-probe-conventions.md`
- `source:` lines 6-10 cite `S332`, `S336`, `S337`, `S338`, `S339`;
  `recheck:` line 12 lists the same five. The round-36 citation said "S331 to S334".

## Lane registry bound
`corpus/SOURCES.md` ends at S329 (`grep -o 'S3[0-9][0-9]' | sort -u` → S324, S327, S328, S329).
Every S330+ id above is staged/foreign to the lane at this revision, so the lane cannot resolve
them from its own `SOURCES.md` — the artifact read above is the only valid re-derivation.

## Self-checks on the draft row
- Every id in the row's reject and motivating-lesson cells resolves at the staged artifact to
  the document stated (table above); none of S359/S360/S366/S372/S391 is `http_server.py` or
  `native_api.mdx`.
- The five "misattributed" ids counted in the draft are exactly S366, S359, S360, S372, S391.
- The range correction matches the staged file's own `source:` lines, not its filename.
- No pipe characters in any cell; row is one physical line; heading uses the corpus em dash style.
