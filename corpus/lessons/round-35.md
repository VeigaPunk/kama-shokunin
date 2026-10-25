# kama round 35 lesson

author: Kimi fresh L1
date: 2026-10-24
base: 719655f12517a9ce6b1a5ca44316897fed8420b0

## Claims

C1 calibration 7 → 7. Predicate: A frozen r34 self-assessment statement is corrected iff corpus/lessons/round-35.md contains a correction row naming its id, the counter re-derives the cited committed-byte fact, and the r34 fleet report blob is unchanged. Counting command: `python3 tools/round35-statement-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin`.

C2 coverage 9 → 9. Predicate: The round-35 coverage block names knowledge/endpoint-health-probe-conventions.md, that file exists, and it cites an S-id present in corpus/SOURCES.md; none of those three hold at base 719655f12517a9ce6b1a5ca44316897fed8420b0. Counting command: `python3 tools/round35-coverage-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip <full-commit>`.

MISSION.md:29 still says operability + freshness. shokunin.conf and the prompt say operability + calibration. MISSION.md was not edited. C1 works calibration because it is the lowest non-retired numeric axis (7). The conflict is named and does not change either predicate.

## Corrections

| R34-MAP | false | README at 719655f lacks serving-alias-contract.md and served-model-id-resolution.md |
| R34-R33COUNT | false | the spot-check records 23 untracked and 1 modified |
| R34-LIVE | not carried forward | the r34 live-seat count is not a current fact |
| R34-MANIFEST | b784e1ab lacks Cannot combine --prompt with --auto |

The filed round-34 report is not rewritten. Its blob stays `7610d532696f5c6e214840fa2ec4112584589252`.

## Gate

Opened 2026-10-24. Theme: what a health-probe signal means. One admit, two rejects.

Admit S327. URL https://docs.vllm.ai/en/v0.32.0/configuration/engine_args/ section `--max-num-queued-reqs`. Quote: "When the limit is reached, new requests are rejected with HTTP 503 so the client can retry on another instance." 18 words. Used by `corpus/knowledge/endpoint-health-probe-conventions.md`. Recheck prose stripped from the staged row: re-run the curl grep for that sentence; the cell is `90d`.

Reject `hosted-health-route-configuration.md`. Reason: the entry is a Google Cloud deployment-spec field for a remote platform probe. README known gaps assign remote endpoint health to kake. Flip: a local container on this host whose configured health route differs from the engine route, observed by the lane probe, not a cloud vendor guide.

Reject the staged five-source `endpoint-health-probe-conventions.md` as a byte-copy. Reason: it cites S331, S332, S333 and S334, which this round did not re-open into the admitted entry. Adopting the file would cite unopened rows. Flip: re-open those four and admit only sentences whose quotes locate.

### Quarantine hand-check (register not edited)

| id | verdict | note |
|---|---|---|
| S200 | unverifiable | abs page reachable; quote cell `DOI not in Semantic Scholar` is a class label, not a located sentence. Not fabrication of the paper. Not appended. |
| S202 | present, not appended | Compose page contains "as indicated by healthcheck" before starting a dependent. No admitted entry cites S202. Flip: an admitted entry cites it. |
| S206 | present, already adopted | live page still contains the v1/models sentence. Not re-appended. |
| S210 | present, not appended | page is not "Page Not Found"; launch_server argv is on the page. Outside this round's admitted entry. Flip: an admitted entry cites the located command. |
| S211 | unreachable | fetch returned HTTP 429. Not fabrication. |
| S224 | quote not located | health page shows `check_health()` and 503 on EngineDeadError; the register's "render-only servers always return 200" clause was not in the extract. Not appended. |
| S230 | present, not appended | v0.5.22 http_server.py contains the `/get_model_info` deprecation sentence. No admitted entry cites S230. Flip: an admitted entry cites it. |

Id collision: registry 200 ids, staged 134 ids (S325–S458), collisions 0. Indent guard: column-zero pattern empty, 0–3-space pattern extracts S002. No renumber. S327 kept.

## Mistakes

| class | evidence | captured-by | fix |
|---|---|---|---|
| self-assessment | round-34 report says the coverage map gains two entries; README at 719655f names neither | none until this counter | `tools/round35-statement-audit.py` on a tree with no correction rows prints `uncorrected 4 met False` (`.ufo/waves/round-35/controls/c1-noop.out`, exit 1). The correction rows above are the fix. |
| dispatch | launcher refused a prompt that mentioned `--auto`, then a second launch spawned 32 seats and crashed on `NameError: name 'p' is not defined` before waiting | none | waiter `wait-seats.py` attached to the existing pids. No seat was replaced. The failed waiter is the shown failure. |

## Frontier

considerthese/2026-10-24.md proposal 1 was mined as KQ44. The file was not edited. Proposals 2–4 were not taken.

Operator commit `82ca9608f91882f228808ca1c37022a3e6722e5d` sits inside the round-34 range and is not lane identity. It is named, not rewritten.

The round-34 L2 floor delivered 5 of 33 reports. That shortfall is not a replacement. This round's seats are recorded from the dispatch manifest, not from a prepared spec alone.
