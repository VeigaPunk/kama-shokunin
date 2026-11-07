# CN01SiblingOverlap — sibling-lane overlap scan (kama round 91, wave 1)

## Scope

Read-only scan of the 21 sibling lane repos `/home/vgpnk/Projects/shokunin/*-shokunin` (kama excluded) for committed content on serving-engine timeouts, limits and ports, and for probes that loop per served id. Compared against C2's 14 rows (`SKILL.md:1870-1895`), C1's linear-time rule (`tools/kama-probe.sh:440-465`) and kama's ownership record (`corpus/knowledge/cross-lane-scope.md`, `PROVINCE.md`). Writes: this file and `.ufo/waves/round-91/w1/out/CN01SiblingOverlap/`; scratch `/fast/scratch/hyaku/kama-r91/CN01SiblingOverlap/` (removed). No endpoint contact, no git mutation, no tool installed. Load at start: `uptime` 0.71/0.37/0.79; no timing cell measured (all cells are file reads).

## Commands and outputs (exit codes)

Common filters: `--include='*.md' --include='*.sh' --include='*.py' --include='*.mjs'`, then `grep -v '^kama-shokunin/'` and `grep -v '/.ufo/'`.

| # | command (abridged) | exit | output |
|---|---|---|---|
| 1 | `grep -rIl -E 'OLLAMA_KEEP_ALIVE\|OLLAMA_LOAD_TIMEOUT\|OLLAMA_HOST\|VLLM_ENGINE_READY_TIMEOUT_S\|VLLM_HTTP_TIMEOUT_KEEP_ALIVE' */` | 1 | no file — no sibling holds any Ollama/vLLM knob |
| 2 | `grep -rIl -E '\b9931\b' */` | 1 | no file — 9931 exists only in kama |
| 3 | `grep -rIl -E 'data\[\]\.id\|\.data\.map\|served_ids' */tools */tests */scripts` | 0 | `mado/tools/mado-evidence-audit.py:249-255`, `souji/tools/souji-cert-evidence.py:1033-1061` — audit *finding* ids, not model ids |
| 4 | `grep -rn -E 'sse_ping\|cache_ram\|models_max\|n_parallel\|sleep_idle_seconds\|timeout_read\|timeout_write' */` | 0 | only `kengaku/.../torch-tensor-parallelism/tests/test_outputs.py:43,187,194` (`n_parallel` substring) — no sibling names a llama.cpp threshold parameter |
| 5 | `grep -rIl -E 'llama\.cpp\|llama-server' */` | 0 | kagi (7 files), kaidoku `EXAMPLE.kama.md`, kengaku (3+), kumitate, mado, tsukuroi — host observations and scope rows only; no flag/default table |
| 6 | `grep -rn -iE 'keep.?alive' */` | 0 | audio (GStreamer freeze), kake `freshening-304.md:194` (hop-by-hop header list), kengaku `round12-fleet/r12-endpoint-freshness.md:48` (HTTP header sample), kumitate `SCORECARD.md:2930` (S120: TCP keepalive ≠ worker liveness), tabi (browser sockets) — none is a serving-engine idle/keep-alive default |
| 7 | `grep -rn -E 'paste -sd\|paste -s -d' */` | 0 | chousa `tools/research-gate.sh:7054`; tsukuroi `tools/boot-chain-audit.sh:983,1075,1082`; kagi `corpus/scope-gate.sh:609`; kaidoku `tools/round-38/c1-run.sh:34`; revenger `reports/round-*/selftest_probe.sh:35` |
| 8 | `git log --oneline -3` (read-only) | 0 | `3f317ecd` / `3decfa36` / `9a41912a` — master at M2 |
| 9 | `git show <rev>:SKILL.md \| sha256sum` for B/F/M/M2 | 0 | `55ff738c…` at c06838c5, 9a41912a, 3decfa36; `98058b6b…` at 3f317ecd (1868 → 1895 lines) |
| 10 | scratch: `cp cross-lane-scope.md x; cat <append fragment> >> x; wc -l; grep -c '^|'` | 0 | 158 lines, 16 pipe lines, sha256 `f154087e708cd2ba12a0fb59a862cf939cceaeb97edb513b9a01b7f57a104f0f`; `diff <(head -148 x) cross-lane-scope.md` → empty, rc 0 |
| 11 | `grep -rn 'cross-lane-scope' --include='*.py' --include='*.sh'` (kama) | 1 | no counter reads it; prose cites only |

Reads (file:line, no meaningful exit code): kama `SKILL.md:30-136,1870-1895`, `PROVINCE.md:1-33,245-262`, `SCORECARD.md:19,64-90,240`, `tools/kama-probe.sh:96-103,336-350,440-465,852-878,927-935`, `registry/endpoint-consumers.tsv`; kagi `handler-on-disk-state.md:108-136`, `SKILL.md:43`, `PROVINCE.md:95`, `LOG.md:102-104`; kengaku `PROVINCE.md:14,15,26,158`, `SCORECARD.md:65`, `LOG.md:7`; kake `PROVINCE.md:355`, `LOG.md:1966`; tsukuroi `PROVINCE.md:25,46,122,138`; tabi `PROVINCE.md:192`; kotoba `PROVINCE.md:66`; kumitate `PROVINCE.md:32,48`; mado `PROVINCE.md:15`, `MINT.md:14`; tameshi `PROVINCE.md:18`, `SKILL.md:3`, `corpus/knowledge/service-limits.md:50`; kotodama `tools/reopen-row.py:18-19,88-95`.

## Findings

**NOTE 1 — kagi holds the same 3600 s figure on a different clock.** `kagi/corpus/knowledge/handler-on-disk-state.md:112-124` measures a hung request wedging `start`/`stop` "for up to an hour" and names its bound as `THE_JANITOR_REQUEST_TIMEOUT` default **3600 s** (`client.py` L74, the client's prompt timeout); `LOG.md:102-104` repeats it. T02's 3600 s is llama.cpp's *server* `timeout_read` (S593 line 634). Numbers agree, clocks do not: neither proves the other, and the probe's own `--timeout` (5 s) is a third.

**NOTE 2 — the fleet's only measured inference unit overrides two rows.** kengaku `PROVINCE.md:14` pins `qwen-coder.service` argv: `--parallel 2` (no literal `-np`), `--ctx-size 16384`, `--kv-unified`, q4_0 KV ("**unstated premise of every r8/r9 number**"). T07's default is 1 and its cell says concurrency queues; that unit does not. Any kengaku latency/cache reading must cite its argv, never the row.

**NOTE 3 — kengaku's successor router is a different build, so the rows do not reach it.** `PROVINCE.md:15` records `:45669` absent (2026-11-04) and `:1234` (`lfm3-server.service`) answering 200 at build `b1-39ebd2` — not b12177. T01–T07 apply only after re-opening that build (the section's recheck line); T05/T06 on `:1234` without that read is an overreach.

**NOTE 4 — tuning authority is contested and unresolved.** kengaku `PROVINCE.md:158` names flag-change authority for `--kv-unified`, q4_0 KV and `--parallel` as "**unowned/integrator**"; T04, T06, T07 and `corpus/knowledge/serving-thresholds.md` §Limits say kama reports and never tunes ("operator-owned", "out of province", "kama does not read service units"). Both are true about a gap: no lane is authorised to change a serving flag and an L0/integrator ruling is owed. Kama must not absorb it by silence.

**NOTE 5 — no sibling states a llama.cpp default port; the 8080 record is configured-endpoint history.** kagi `SKILL.md:43`, `op-cli-surface.md:72-77` and kengaku `LOG.md:7` record 8080 as a *configured* baseURL that reached Jitsi/Jetty while `llama-server` listened on 34113; kama `SKILL.md:86` shows the unit passed `--port 34113` after an earlier `--port 8080` (`:121`, archives). T01's b12177 default (9931) contradicts none of them. The only 8080-as-default bytes in the fleet are kama's own `~/.local/bin/omp` builtin fallback (`PROVINCE.md:11`, `SKILL.md:103,117`) — the pre-b12177 default, already graded as a registry row, not a server default. Commands 1, 2 and 4 found no sibling default-port statement.

**NOTE 6 — kagi's endpoint verification step is weaker than kama's MODEL_OK rule.** kagi `SKILL.md:43` says `curl -fsS <endpoint-minus-/v1>/health` → `{"status":"ok"}` "verifies the model endpoint is real". kama's frozen v3 rule requires a model array: "MODEL_OK requires a model array; status code / Server header alone is not proof" (`tools/kama-probe.sh:927`). A foreign service answering a health-shaped 200 passes kagi's step and fails kama's. Method divergence in a sibling decision row, not a value conflict.

**NOTE 7 — the 4 MiB cap discipline is shared; only the verdict vocabulary differs.** kotodama `tools/reopen-row.py:18-19,88-95` caps at 4 MiB and returns `TRUNCATED` for a cut body (never ABSENT); mado `tools/mado-receipt-citecheck.py:18` skips and counts >4 MiB files. kama caps at 4 MiB and grades `FOREIGN_SERVICE`/`body-too-large` (`tools/kama-probe.sh:99-103,868-878`; `SKILL.md:1868`; counted round-90 cell, `SCORECARD.md:240`). Same discipline, different name; no contradiction. Vocabulary note only: kama's name asserts foreignness the probe cannot establish for an oversize legitimate list — frozen and disclosed.

**NOTE 8 — kengaku's freshness ceiling is not closed by C2.** `kengaku/SCORECARD.md:65`: "no in-repo pin exists to catch a silent `:34113` move". T01 pins the b12177 *default*, not a host listener; the ceiling stands.

**NOTE 9 — no sibling has a per-id loop over served ids.** The only sibling model-list reader is kengaku `corpus/evidence/round11-power/run_r11.py:94` (one GET, `timeout=10`, whole JSON kept as a descriptor). C1's defect class has no sibling analogue; its `paste -sd,` join is already lane-proven (command 7) and the old `${C_SERVED%,}` pattern has no sibling user — the defect was kama-local.

**NOTE 10 — adjacency census.** kama is routed endpoint/model-serving ownership by 10 lanes: kake `PROVINCE.md:47,355`, kagi `PROVINCE.md:95` (refuses to send kama credentials for authenticated health), kumitate `PROVINCE.md:32,48,75`, mado `PROVINCE.md:15`, tameshi `PROVINCE.md:18` + `service-limits.md:50`, tsukuroi `PROVINCE.md:25,46,122`, kotoba `PROVINCE.md:66`, kengaku `PROVINCE.md:158`, kagi `corpus/README.md:112`, kaidoku `EXAMPLE.kama.md:26`. Declared **none**: tabi `PROVINCE.md:192` ("no shared surface"). Kake's refusal of an Ollama OpenAPI source "as kama's province" (`PROVINCE.md:355`) independently assigns the T08–T12 sources.

**NOTE 11 — integration-side anchor duty (observed at M2).** The depth axis row cites `SKILL.md` sha256 `55ff738c…` (1868 lines); it held at B, F and M and moved at M2 to `98058b6b…` (1895 lines) — the C2 commit itself (`SCORECARD.md:19` vs command 9). The adjacency row cites `cross-lane-scope.md` sha256 `c45318b5…` (148 lines, 16 pipe lines) and re-derives today, but any edit moves it. Both rows need a same-commit re-anchor (pattern: `SCORECARD.md:3881`). Reported, not judged.

### Proposed move (one, bounded; no frozen predicate touched)

**Move.** Append a dated, append-only block (`out/.../cross-lane-scope-append.md`) to `corpus/knowledge/cross-lane-scope.md` at EOF: five one-line handoffs — (i) kagi's 3600 s client clock vs T02's 3600 s server clock; (ii) kengaku's `--parallel 2`/q4_0 unit is not T07's default; (iii) kengaku's `:1234` `b1-39ebd2` router is outside T01–T07 until re-opened; (iv) tuning authority is contested (kengaku "unowned/integrator" vs rows' "operator-owned") and no lane may claim it; (v) Ollama sources are kama's, already ruled by kake, and no sibling holds an Ollama/vLLM knob. Each names the sibling's committed words.

**Axes.** adjacency 7 → improves (makes the 14 rows usable by the lanes that route to kama; names the two contested clocks/authorities). Operability 8, depth 7, freshness 8, coverage 9, calibration 7 → unchanged: C1's counter never reads docs (command 11); C2's counter reads only `SKILL.md`'s section and `corpus/SOURCES.md` (`tools/round91-threshold-rows.py:10-22,191-192`), so the block cannot move `rows`/`bound`; no SKILL row, value or decision changes, so K2's reviewer read is untouched.

**Rejected alternatives** (each touches a frozen population): a witness row for `b1-39ebd2` changes C2's row population; renaming `body-too-large` changes round-90's counted `R-body-too-large` cell; rewriting kagi's `/health` rule is a sibling edit, out of province.

**Risks.** (a) The adjacency row's sha256/line count move → re-anchor in the same commit; bullets start with `-`, so the pipe count stays 16 and the diff is sha + line count only. (b) Sibling line numbers drift → the block cites file + quoted words and says to re-read live declarations (tsukuroi's rule, `PROVINCE.md:138`). (c) A K2 reviewer may read the block as a C2 claim → its first line says it adds no row, value or claim. (d) EOF-only append: lines 12–13 and 29 are cited by kotoba (`PROVINCE.md:66`) and kagi (`corpus/README.md:112`); command 10 shows the first 148 lines byte-identical.

**Verification (for the L1).** Branch-free: append the fragment, then re-derive (158 lines, 16 pipe lines, sha256 `f154087e…`); `diff <(head -148 file) <(git show <M2>:corpus/knowledge/cross-lane-scope.md)` empty; `python3 tools/round91-threshold-rows.py --repo . --rev <M2>` still `rows=14 bound=14 …`; if the depth row is also re-anchored, use the SKILL.md sha from command 9.

## Deliverables

- `.ufo/waves/round-91/w1/CN01SiblingOverlap.md` — this report.
- `.ufo/waves/round-91/w1/out/CN01SiblingOverlap/cross-lane-scope-append.md` — candidate append block (leading blank line so `cat file fragment` yields one separating blank line; 10 lines).
- `.ufo/waves/round-91/w1/out/CN01SiblingOverlap/sibling-overlaps.tsv` — 16-row overlap census: lane, path:line, what it says, relation to T01–T14, pin cited.

VERDICT: holds — no sibling lane states a conflicting default, port or timeout; the two contested items (tuning authority, kengaku's b1-39ebd2 unit) constrain how T01–T14 may be applied, not their values.
