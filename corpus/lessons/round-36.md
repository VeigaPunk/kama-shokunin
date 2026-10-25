# kama round 36 lesson

author: Kimi fresh L1 (attempt 2; attempt 1's L1 died on a provider-route failure before committing anything)
date: 2026-10-24
base: e5a8ececf3d60fd53b36bb74299693a29e8f74b6

## Claims

C1 calibration 7 → 7. Predicate: A frozen r35 routed statement is corrected iff corpus/lessons/round-36.md contains a correction row naming its id, the counter re-derives the cited committed-byte fact, the correction row does not contain the token 429, and the r35 lesson blob and the r35 fleet report blob are unchanged. Counting command: `python3 tools/round36-statement-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip <full-commit>`.

C2 coverage 9 → 9. Predicate: The round-36 coverage block names knowledge/sglang-native-route-deprecation.md, that file exists, and it cites an S-id present in corpus/SOURCES.md at the tip and absent at base e5a8ececf3d60fd53b36bb74299693a29e8f74b6; none of those three hold at that base. Counting command: `python3 tools/round36-coverage-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip <full-commit>`.

Both predicates were frozen before scoring (`.ufo/waves/round-36/preregistration.json`). The do-nothing controls are `.ufo/waves/round-36/controls/c1-noop.out` (`uncorrected 4 false_corrections 0 lesson_unchanged 1 report_unchanged 1 met False`, exit 1) and `.ufo/waves/round-36/controls/c2-base.out` (`named 0 file_exists 0 cited_new 0 met False`, exit 1). A control that met its target would have retired the counter before data.

MISSION.md:29 still says operability + freshness; shokunin.conf and the round prompt say operability + calibration. MISSION.md was not edited and no duplicate L0 was filed; the r35 question (`kama | round-35 | MISSION.md:29 still says operability + freshness …`) stays open. C1 works calibration because it is the lowest non-retired numeric axis (7).

## Corrections

These four rows correct the statements the round-35 closure routed. The round-35 lesson file and the round-35 fleet report are not rewritten; their blobs are pinned by the C1 counter.

R35-S211: The round-35 lesson records this quarantine row as unreachable. That reason is wrong. The closure spot-check at corpus/lessons/round-35-verifier-spotcheck.md:95 and :118 records HEAD 200 for the same cited URL, and this round's own fetch of that URL on 2026-10-24 returned HTTP 200 as well. The seat report .ufo/waves/round-35/w1/out/ScoutQuarantineS211.md records that the page was fetched successfully and that the token still-live is absent from it. The row stays unappended: no located quote exists for it. corpus/lessons/round-35.md is not rewritten.

R35-WORDS: The S327 quote in corpus/lessons/round-35.md is 20 words, not the 18 words its own paragraph records. The count is re-derived from the committed lesson blob 428f1f8a0e8871022f7c1e8ea47e50ba5a8d6412 three ways — a whitespace split, `wc -w`, and the C1 counter's own `quote_words` extractor — and all three return 20. The located sentence is unchanged and stays inside the 25-word bound. corpus/lessons/round-35.md is not rewritten.

R35-MIRROR: The round-35 report calls the round-35 validate tree a symlink tree. The closure spot-check records it as a mixed mirror: 11 symlinks and 84 regular files. The round-35 fleet report is not rewritten. The mirror is not committed this round. The round-36 scratch mirror at .ufo/waves/round-36/assimilation/validate/ is a separate plain copy and is committed as wave evidence.

R35-KEEP: Seven r35 leftovers are classified and none of them is swept. seat-log-flush .ufo/waves/round-35/w1/out/ConnSibling/seat.log .ufo/waves/round-35/w1/out/ExecDisposition/seat.log .ufo/waves/round-35/w1/out/ScoutCoverageAbsence/seat.log; overwrite-not-committed .ufo/waves/round-35/w1/out/ExecDisposition.md — the working-tree file replaces the committed 1994-line thinking dump with a 125-line late write, and committing it would replace landed evidence; mixed-mirror-not-committed .ufo/waves/round-35/assimilation/validate/ — 11 symlinks and 84 regular files, including a recursive .ufo link, so it is not a safe commit; helper-skipped .ufo/waves/round-35/w1/out/ScribeGate/fetch/docker-dockerfile.html .ufo/waves/round-35/w1/out/ScribeGate/fetch/dockerfile.html — both 1066624 bytes, over 1 MiB, skipped by the lane helper and left unforced.

## Gate

Opened 2026-10-24 by the L1 (attempt 2) and re-opened by wave-2 seats. Theme: a published native route name is not the engine's current route. One theme, one admitted entry, two registry rows. The staged package under /home/vgpnk/Projects/shokuknow was read, never written.

Admit S328. URL https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/docs/docs/basic_usage/native_api.mdx. Opened 2026-10-24, HTTP 200, 17359 bytes. Anchor: line 6 and route-list line 9. Located quote (15 words): "Apart from the OpenAI compatible APIs, the SGLang Runtime also provides its native server APIs." Used by corpus/knowledge/sglang-native-route-deprecation.md. Recheck 90d. The staged package carried this document as S366; the id follows the document into the lane's own registry.

Admit S329. URL https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/python/sglang/srt/entrypoints/http_server.py. Opened 2026-10-24, HTTP 200, 110718 bytes. Anchor: lines 790-791 for the deprecation warning, lines 786 and 796 for the two route registrations. Located quote (16 words): "Endpoint '/get_model_info' is deprecated and will be removed in a future version. Please use '/model_info' instead." Used by corpus/knowledge/sglang-native-route-deprecation.md. Recheck 90d. The staged package carried this document as S359, S360, S372 and S391; one URL takes one row.

Reject `hosted-health-route-configuration.md` (staged, merge/kama/knowledge/corpus/knowledge/). Reason: it is a remote-platform deployment field — a Google Cloud `serving_container_health_route`, a `containerSpec.healthRoute` and an `AIP_HEALTH_ROUTE` — and the lane's README assigns remote endpoint health to kake. It is not local endpoint health. Flip: a local container on this host whose configured health route differs from the engine route, observed by the lane's own probe rather than a cloud vendor guide.

Reject the staged `sglang-native-api-deprecation-amendment-2026-10-23-r4.md` as a byte-copy, while adopting its theme. Reason: its rows (S366, S391) cite campaign-provisional ids and anchor cells this round did not re-ground, and its file was not re-opened line by line here; copying it would land anchors this lane did not verify. The theme is adopted instead as a lane-written entry that cites the two rows this lane opened. Flip: a later round that re-opens every anchor of that staged file may append it as its own entry.

Reject the staged rows S359, S360 and S372 (the same `http_server.py` URL). Reason: one URL, one row. A second row for it would duplicate the URL in the registry and the census's W04 duplicate-url check would flag it. Flip: an admitted entry that needs the readiness, model-card or OpenAI-compatible reading of that file may add its own row with its own anchor.

Reject the staged `endpoint-health-probe-conventions.md` as a byte-copy. Reason: it cites S331 to S334, which this round did not open; copying it would cite rows with no located quote. Flip: re-open those four and admit only the sentences whose quotes locate.

### Quarantine hand-check (register not edited)

Slice derived with the operator recipe: `awk -F'|' -v l='kama' '$2 ~ ("`" l "`") && $3 ~ /round[0-9]+/ && $4 ~ /S[0-9]+/ {print $4, $5}'` over the campaign register. Seven kama rows, each carrying an S-id; the class cell in every one of them reads `payload-absent`. Every row below was hand-checked by the L1 on 2026-10-24 with a direct fetch; wave-2 seats re-opened S211, S230, S224, S202 and S210 independently. The register was not edited.

| id | verdict | reason | flip |
|---|---|---|---|
| S200 | absent | https://arxiv.org/abs/2312.07104 returns HTTP 200. The quoted cell `DOI not in Semantic Scholar` does not occur in the page text read. The cell is a status fragment about the source, not a sentence from it. Not appended. | a located sentence from that page replaces the cell |
| S202 | present, not appended | https://docs.docker.com/reference/compose-file/services/ returns HTTP 200 and carries the span: `service_healthy : Specifies that a dependency is expected to be "healthy" (as indicated by healthcheck ) before starting`. The register's cell differs from the page in quote style, which is why the quote linter did not match it. No admitted entry cites S202 this round, and a row no admitted entry cites is not appended. | an admitted entry cites it |
| S206 | present, not appended | https://www.alibabacloud.com/help/zh/pai/deploy-an-llm/ returns HTTP 200 and carries the span `对于vLLM/SGLang，可通过模型列表接口 <EAS_ENDPOINT>/v1/models 获取。`. The material is a hosted Alibaba Cloud PAI EAS deployment guide, so it is also out of the lane's local-serving province. Not appended. | an in-province entry cites it |
| S210 | absent | https://unsloth.ai/docs/jp/ji-chu/inference-and-deployment/sglang-guide returns HTTP 200 and contains `python3 -m sglang.launch_server`, but the quoted cell `Page Not Found` does not occur on the page. The cell is a status fragment, not a page sentence. Not appended. | the cell is replaced by a located span from the page |
| S211 | absent | https://github.com/AaronYang238/llm/blob/35b83cee12ae26f10b58d4163298352384503907/chapters/06-推理引擎.md returns HTTP 200 and the token `still-live` occurs nowhere in the page text read. The register's class is a payload-absence class, so the quoted span is genuinely not in the source. Not appended, and not fabrication of the chapter. | a located span from that chapter replaces the cell |
| S224 | quote not located | https://docs.vllm.ai/en/v0.17.0/api/vllm/entrypoints/serve/instrumentator/health/ returns HTTP 200 and carries `check_health()` and a 503 on `EngineDeadError`. The register's compound span `render-only servers always return 200` does not occur: neither `render-only` nor `always return 200` is on the page. Not appended. | the compound cell is split and each half is re-quoted |
| S230 | present, covered by the lane's own row | https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/python/sglang/srt/entrypoints/http_server.py returns HTTP 200 and carries the register's quoted sentence at lines 790-791. The lane's row S329 carries the same URL and the same anchor for the admitted entry; a second row for one URL would duplicate it in the registry. Not appended separately. | a later round needs a second, differently-anchored row for that URL |

### Id collision (scratch, before any append)

Registry ids 201, staged ids 134 (S325 to S458), collisions 1: S327. The staged S327 is the same document the lane already holds — the r35 vLLM Engine Arguments row — so it is not re-appended and not renumbered; the collision is a re-append of an existing lane row, not two different documents sharing an id. The two rows this round adopts take the lane's next ids S328 and S329. Those ids sit inside the staged range: the staged ids are campaign-provisional and the lane registry is append-only, so an adopted id follows the lane's registry and never arithmetic on the staged set. Renumber map: none required, because no adopted row re-points a staged citation. Flip: a round that adopts staged rows re-points each adopted row by document, never by adding an offset.

### Validate-before-append (scratch)

The first mirror build failed with E12 on both new rows. Appended at the end of `corpus/SOURCES.md` they fell outside the Registry section, because that file carries further sections after the registry table. The rows were re-placed inside the table, immediately after the S327 row, and the gate then exited 0 with 93 pre-existing W04 duplicate-url warnings and no E finding. The gate caught the defect before the append reached the lane registry.

The mirror is a plain copy of the lane tree — not a symlink tree — plus the `.ufo/waves/` paths the registry's `used-by` cells name, because the census resolves those paths relative to the mirror root. Receipt: `.ufo/waves/round-36/assimilation/validate-census.out`, last line `file ok`.

Indent guard: the column-zero extraction pattern returns an empty collision list on the scratch fixture whose indented row is `  | S002 |`; the 0-3 leading-space pattern returns S002. The guard holds, so the collision check that produced `collisions = S327` is the one that can see an indented row.

## Mistakes

| class | evidence | captured-by | fix |
|---|---|---|---|
| false-grounded-reason | corpus/lessons/round-35.md:42 records the S211 quarantine row as unreachable, and that reason is contradicted by the closure spot-check's HEAD 200, by the seat report that fetched the page, and by this round's own fetch of the same URL | none — the round-35 row was written from a seat summary that carried no status code | the C1 counter's R35-S211 arm re-derives the row from committed bytes and refuses any correction row that carries the forbidden token, so a reason cannot be restated into a lesson unchecked; a quarantine verdict must name the status actually observed |
| number-drift | corpus/lessons/round-35.md:28 records "18 words" for a quote that is 20 words long | none — the count was written by hand beside the quote | the C1 counter's `quote_words` re-derives the count from the committed lesson blob, and the R35-WORDS arm refuses the row unless the re-derived count and the recorded count are compared; a counted quantity in a lesson is re-derived, never trusted |
| dispatch | 18 of the 32 wave-1 seats exited rc=1 with `provider.auth_error: 403` from the xai-oauth route, and 20 of the 32 wave-1 report files are stdout transcripts rather than seat-written reports | none | wave 2 routes every report-bearing item to a seat whose card carries Write or Bash, so a seat's own findings reach a report file; the wave's `seat-exit-codes.json` records the provider error text and the dead seats stay dead |

## Frontier

considerthese/2026-10-24.md proposal 2 was mined as KQ45. The file was not edited. Proposal 1 is already KQ44 and was not re-taken. Proposals 3 and 4 were not taken.

The round-35 L2 floor and this round's wave 2 are recorded from their dispatch manifests and exit files, not from a prepared spec alone.
