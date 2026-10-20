VERDICT: partial — the round-16 build wave left `corpus/knowledge/cross-lane-scope.md` byte-identical, and that is right for every existing line but wrong as a complete handoff: two lanes the file never names (tsukuroi, souji) now own persistent round-16 host artifacts that `PROVINCE.md:51-53` explicitly delegates to this file, and two lanes it does name (kagi, kumitate) need one new boundary fact each. No existing line should be rewritten; the repair is one append at EOF.

# ConnectCrossLaneScope — attack on cross-lane-scope.md vs round-16

## Axes named

1. **Calibration** — does every lane-facing claim carry evidence and a stated owner?
2. **Operability** — can the next operator/lane find the round-16 host artifacts and know who may act on them?
3. **Contract fidelity** — append-only provenance (KQ7/KQ14), the `source:/verified-at:/recheck:` trio (KQ11), and `PROVINCE.md`'s "report, never absorb" delegation.
4. **Verification cost** — can the move be checked with read-only commands and no endpoint I/O?
5. **No harm** — no consumer row, verdict, registry entry, score, or receipt changes.

## What I ran (all read-only; no probe, no server, no measure.py)

| Command | Exit | Output / note |
|---|---|---|
| `git show --stat b8e485c` | 0 | 153 files; **`cross-lane-scope.md` is not among them** (the file is untouched by round 16). |
| `grep -n 'tsukuroi\|souji\|mori' corpus/knowledge/cross-lane-scope.md` | **1** | no matches — the file never names tsukuroi or souji. |
| `grep -c 'tsukuroi\|souji\|mori'` equivalent (same run) | 1 | zero hits, so the `PROVINCE.md:51-53` delegation has no destination for host artifacts. |
| `wc -l corpus/knowledge/cross-lane-scope.md` | 0 | `87`; last byte is `\n` (verified with `tail -c 80 \| od -c`), so an EOF append is clean. |
| `nl -ba PROVINCE.md \| sed -n '44,68p'` | 0 | `:51-53` "Out of province → report, never absorb … named in the round report for the owning lane (see `corpus/knowledge/cross-lane-scope.md`)"; `:55-66` round-16 note naming `~/.local/opt/llama-b11755`, `~/.local/bin/llama-server`, `~/.cache/kama-shokunin/`, and "The install tree and cache persist on the host; removal is the operator's call." |
| `nl -ba PROVINCE.md \| sed -n '13,16p'` | 0 | `:15` "endpoint-consumers cross-lane registry \| `consumer-registry.md`, `cross-lane-scope.md`". |
| `ls -1 ~/.local/opt/llama-b11755 \| wc -l` | 0 | `61` depth-1 entries. |
| `find ~/.local/opt/llama-b11755 -maxdepth 1 -type f \| wc -l` ; `… -type l \| wc -l` ; `… -type d \| wc -l` | 0 | `51` regular files, `10` symlinks, `0` subdirectories (51+10=61, consistent). |
| `du -sb ~/.local/opt/llama-b11755` | 0 | `56288736`. |
| `stat -c '%s %n' ~/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz` ; `sha256sum` same | 0 | `22240468`; `753bfa7327a75b477d4d14cde71e0e46a40acc3a1408c5504530b78c33a6e226` (equals the S038 asset digest in the round-16 evidence). |
| `readlink -f ~/.local/bin/llama-server` | 0 | `/home/vgpnk/.local/opt/llama-b11755/llama-server`. |
| `stat -c '%s %n' ~/.cache/kama-shokunin/models/stories260K.gguf` ; `sha256sum` | 0 | `1185376`; `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d` (matches the pinned S039 digest). |
| `find ~/.cache/kama-shokunin -maxdepth 2` | 0 | exactly `models/stories260K.gguf`; no other entry. |
| `pacman -Qo` on the install-tree binary, the `~/.local/bin` symlink and the GGUF | **1** each | "error: No package owns …" for all three — the persistent artifacts are outside package management (read-only query; no transaction). |
| `grep -c 'Authorization\|Bearer\|api-key\|api_key' tools/kama-probe.sh` | **1** | `0` — the probe carries and sends no credential. |
| `grep -c 'Authorization\|Bearer\|api-key\|api_key' tools/kama-llamacpp-live.py` | **1** | `0` — the harness passes no `--api-key`. |
| `read tools/kama-probe.sh:495-500` | — | `401) UNAUTHORIZED_SERVICE; http-401 ;; 403) … ;;` executes before the `503` loading branch (same file, 503 branch after), matching the probe's documented 401/403-before-loading order. |
| `cat .ufo/waves/round-16/live/controls.txt` | 0 | `digest_mismatch_exit=3`; `registered_port_34113_exit=2`; `registered_port_8080_exit=2`; `post_pgrep_llama_server=0`. |
| `grep -n 'stay \`DEAD\`' corpus/knowledge/llamacpp-loading-lifecycle.md` | 0 | `:120` "34113 were refused, never touched, and stay `DEAD` in `registry/history/latest.tsv`". |
| `grep -rl 'cross-lane-scope' tests/ tools/ .ufo/waves/round-16/*.py` | **1** | no mechanical parser — the append cannot break a gate. |
| `grep -n 'MODEL_LOADING' registry/endpoint-consumers.tsv` | 0 | `:32` vocabulary comment only; data rows are `:35-37` (3 consumers) and are unchanged. |
| `nl -ba corpus/knowledge/llamacpp-loading-lifecycle.md \| sed -n '28,45p'` | 0 | `:33-35` "**Before the API key.** … A loading server with `--api-key` therefore answers 503, not 401."; `:39-41` "**Router mode is different.** The router stores `is_ready = true` right after its listener starts … so it never emits this body. Its `/v1/models` is a catalog with per-model `status`." |
| `grep -n '## Round-16' SKILL.md` | 0 | `:507` round-16 section; `:538` "Use the binary's absolute path". |

Not run, per the assignment contract: `.ufo/waves/round-16/measure.py` (rewrites L1 receipts), any probe, any llama-server. `pgrep -x llama-server` was **not** run because I started no server; no server can be mine.

## Ruling per candidate

| Candidate | Consumer-table row (`§Consumer ownership`)? | Handoff line (new EOF section)? | Reason |
|---|---|---|---|
| Persistent `~/.local/opt` install (tsukuroi) | **No** | **Yes — required** | The table is for baseURL consumer declarations (`PROVINCE.md:11,15`); an install tree and a PATH symlink are host artifacts, not consumers. But `PROVINCE.md:51-53` routes out-of-province facts to `cross-lane-scope.md`, and `:55-66` records that the tree persists. The file has zero tsukuroi mentions (grep exit 1): the delegation is currently dangling. The round's own role string is explicit — tsukuroi = "host operability/repair: `~/.local/opt` installs, binaries, pacman pause, service restarts" (`.ufo/waves/round-16/build/make_spec.py:172`). Additive and consistent with `ConnectTsukuroi.md:14-25,79-96`. |
| `~/.cache/kama-shokunin` GGUF cache (souji) | **No** | **Yes — required** | Same dangling delegation; souji's role is "workspace hygiene: `~/.cache/kama-shokunin` model cache and `~/.local/opt` install as preserved artifacts" (`make_spec.py:175`). The digest is checked before launch and a mismatch exits 3 (`live/controls.txt`), so calling the cache "debris" is not harmless — it would delete the fixture's identity anchor. `ConnectSouji.md:11-38,78-120` proposes the related Q20 tree-digest move. |
| `--api-key` (kagi) | **No** | **Yes — narrow boundary fact** | The fact is new and code-grounded: the loading gate runs before the API-key check, so a keyed loading server answers 503, not 401 (`llamacpp-loading-lifecycle.md:33-35`; probe mirrors 401/403-first at `kama-probe.sh:495-500`). The consequence is a scope statement, not a kagi-owned change: the probe sends no credential (grep count 0) so `MODEL_LOADING`/`MODEL_OK` are **auth-blind** in both directions. `ConnectKagi.md:110-131` already rules "report, do not adjudicate". The existing kagi bullet at `cross-lane-scope.md:38` must **not** be rewritten; round-10 correction A33 already marks it historical. |
| Router mode (kumitate) | **No** | **Yes — narrow routing consequence** | Router mode sets `is_ready` at listener start (`llamacpp-loading-lifecycle.md:39-41`; S037 `server.cpp:460`), so it never emits the loading envelope and its 200 `/v1/models` is a catalog with per-model `status`. The existing kumitate bullet at `:40` (OMP role map, no local route) is still true and stays; the new line only names the dispatch-facing consequence. Ownership matches the existing contested row `:28` ("Kumitate owns how a dispatch/alias resolves; kama owns what the resolved local baseURL serves"). |

**Placement ruling.** Not a mid-file insert. KQ7 (`corpus/QUALITY.md:29`) requires "every correction appended at the end of its file"; KQ14 keeps that append-only rule. Every external citation to this file that I found is at or below line 51 (`ConnectTsukuroi.md:9-18,49-51`; `ConnectKagi.md:32`; `ConnectKumitate.md:28`; `ConnectKake.md:42`), so an EOF append moves no cited anchor. The new section extends the "copy-pasteable handoff" list at `:38-45` without touching it, and the existing stale bullets stay as dated history exactly as round 10 left them.

## Proposed move (one, bounded)

Append exactly the block below at EOF of `corpus/knowledge/cross-lane-scope.md` (after the round-11 provenance supplement). It adds four lane handoffs, opens with the KQ11 provenance trio, states the negative claims it is entitled to, and changes nothing else. Axis impact: operability ↑ (both unowned persistent artifacts become routed), calibration ↑ (two new boundary facts are stated with owner and limit), contract fidelity ↑ (the `PROVINCE` delegation stops being dangling); no axis is harmed — no consumer row, verdict, registry entry, score or receipt changes, and no probe is authorized.

### Exact append text

```markdown

## Handoffs — round 16 (2026-10-20): persistent host artifacts and two boundary facts

source: lane round-16 commit `b8e485c` — `PROVINCE.md:51-66`, `SKILL.md:507-538`, `corpus/knowledge/llamacpp-loading-lifecycle.md:33-41,120`, `registry/endpoint-consumers.tsv:32`, and the four read-only overlap scans `.ufo/waves/round-16/build/advice/{ConnectTsukuroi,ConnectSouji,ConnectKagi,ConnectKumitate}.md`. The host paths below were re-observed read-only on 2026-10-20 with `ls`, `find`, `du -sb`, `stat`, `readlink -f` and `sha256sum`; no probe, server, unit, consumer config or registry row was touched for this append.
verified-at: 2026-10-20 — install tree, PATH symlink, retained release asset and model cache stat'ed and hashed; no registered consumer was probed here and their recorded status is unchanged (`llamacpp-loading-lifecycle.md:120`). The API-key ordering and router-mode facts are code reads at the pinned commit (S036, S037), not live runs.
recheck: on-request — repeat the read-only host commands named above and re-open the named build-advice files; no endpoint I/O is required. This section is appended at EOF, so no earlier line in this file moves.

This extends the `Round-report handoffs` list at lines 38-45 without moving it. The older bullets remain dated history; none is rewritten, and round-10 corrections A33-A37 still govern them.

- **tsukuroi:** Kama reports: round 16 left a persistent install outside package management — `~/.local/opt/llama-b11755` (61 depth-1 entries: 51 regular files, 10 symlinks, 0 subdirectories; 56,288,736 B), the symlink `~/.local/bin/llama-server` resolving to `~/.local/opt/llama-b11755/llama-server`, the retained release asset `~/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz` (22,240,468 B, sha256 `753bfa7327a75b477d4d14cde71e0e46a40acc3a1408c5504530b78c33a6e226`), and the lane-owned cache in the souji line below. It was installed from the official release tarball under the operator tooling directive; no package owns the tree, the symlink or the model (`pacman -Qo` exit 1 on each); no unit, `~/.config` or `~/.omp` file was written (`PROVINCE.md:55-66` — design statement, not a measured before/after here). Tsukuroi owns host-operability inventory if it declares an unowned-path arm; because its boundary is "never installs, upgrades, or removes packages", this line asks for inventory and a routing decision, not removal. Removal is the operator's call (`PROVINCE.md:65-66`). Kama will not add these paths to `registry/endpoint-consumers.tsv`: they are not baseURL consumers. **[INFERENCE]** Tsukuroi's ownership here is the roster boundary, not a lane observation. (`.ufo/waves/round-16/build/advice/ConnectTsukuroi.md:14-25,79-96`.)
- **souji:** Kama reports: `~/.cache/kama-shokunin/models/stories260K.gguf` (1,185,376 B, sha256 `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`) is a preserved lane artifact, not debris — it is the pinned model for the live receipt, whose digest is checked before launch and exits 3 on mismatch (`.ufo/waves/round-16/live/controls.txt`). The retained tarball above is likewise the asset-digest anchor for the install, not a leftover download. Kama owns the cache; souji should treat both as preserved and route any removal proposal to the operator rather than deleting by hygiene rule. The cache currently holds exactly one file below `models/` and no other entry. (`.ufo/waves/round-16/build/advice/ConnectSouji.md:11-38,78-120`.)
- **kagi:** Kama reports one endpoint fact and no authentication claim: at llama.cpp 704366d76 the pre-routing state gate runs before the API-key check, so a keyed server that is still loading answers 503 `Loading model`, not 401 (`llamacpp-loading-lifecycle.md:33-35`; the probe likewise grades 401/403 before the loading body, `tools/kama-probe.sh:495-500`). The probe sends no `Authorization` header and `tools/kama-llamacpp-live.py` passes no `--api-key`, so `MODEL_LOADING` and `MODEL_OK` are auth-blind: neither may be read as "unauthenticated" or "authenticated". Whether an unauthenticated caller should see the loading body at all is kagi's risk judgment and L0's decision; kama supplies, stores and validates no key. Round-10 correction A33 above already marks the old 8080 bullet as historical. (`.ufo/waves/round-16/build/advice/ConnectKagi.md:110-131`.)
- **kumitate:** Kama reports: router-mode llama.cpp stores `is_ready = true` when its listener starts, before any model loads, so it never emits the loading envelope, and its `/v1/models` is a catalog with per-model `status` rather than a readiness answer (`llamacpp-loading-lifecycle.md:39-41`; S037 `server.cpp:460`). So a 200 catalog from a router target is not model readiness, and `MODEL_LOADING` cannot fire there. Kumitate owns whether any dispatch or alias should target a router-mode server; kama owns what the resolved local baseURL serves. The OMP role-map statement in the kumitate bullet above is unchanged — round 16 wrote nothing under `~/.omp` (`PROVINCE.md:64`). (`.ufo/waves/round-16/build/advice/ConnectKumitate.md:71-98,172-179`.)

No consumer row, verdict, registry entry, score or receipt changes for these four lines. `registry/endpoint-consumers.tsv` already carries `MODEL_LOADING` in its vocabulary comment (`:32`) and no data row; nothing here authorizes a probe, a service start, a config edit or a removal.
```

## Risks (stated, not smoothed)

- **Ownership is roster-level [INFERENCE] for tsukuroi.** The append marks that line; without the marker it would overclaim. Do not drop the marker during integration.
- **Dated facts, not present state.** The install and cache facts are a 2026-10-20 filesystem sample. If the operator removes either, the line is stale until the `recheck` command is rerun; the `recheck:` line already says so.
- **Negative claims.** "No unit/`~/.config`/`~/.omp` write" comes from `PROVINCE.md:55-66` as a design statement, not from a before/after capture in this seat. The text labels it as such; upgrading it to a measured negative would be a calibration defect (the shape `ConnectTsukuroi.md:5` warns about).
- **Duplication, not substitution.** `ConnectTsukuroi.md:79-96` and `ConnectSouji.md:78-120` propose richer receipts (host-inventory packet; Q20 install-tree digest). The append is the durable lane-facing summary; if L1 adopts those receipts, keep the append pointer-based rather than restating their fields.
- **Do not "fix" it in the registry.** Adding install/cache paths to `registry/endpoint-consumers.tsv` would change that file's meaning (baseURL consumers, `PROVINCE.md:11`) and could make `check` evaluate a non-consumer path. The append says this explicitly.
- **Do not fold the kagi fact into the existing kagi bullet.** Rewriting `:38` violates KQ7/KQ14 and shifts the file's own anchors; A33 already handles the staleness.

## Verification L1 can run (read-only; no endpoint I/O)

1. Before: `wc -l corpus/knowledge/cross-lane-scope.md` → 87; `grep -c 'tsukuroi' …` and `grep -c 'souji' …` → 0 with exit 1.
2. Append, then: `git diff -U0 -- corpus/knowledge/cross-lane-scope.md` contains **no** `-` lines (append-only proof); `wc -l` equals 87 + appended lines.
3. `grep -c 'tsukuroi\|souji' corpus/knowledge/cross-lane-scope.md` → ≥ 2; `grep -c 'MODEL_LOADING' …` unchanged at 0 (this file still needs no verdict vocabulary).
4. Re-stat the four facts: `ls -1 ~/.local/opt/llama-b11755 | wc -l` = 61; `du -sb` = 56288736; tarball `stat -c %s` = 22240468; `sha256sum` the GGUF = `270cba1b…d256`.
5. Confirm nothing else moved: `git status --porcelain` shows only this knowledge file (plus the falsify advice dir).
6. Safety: `pgrep -x llama-server` empty; no listener on 8080/34113 created by this work.

## Limitations

- I did not re-read sibling lane repositories this seat; tsukuroi/souji/kagi/kumitate domain statements are taken from the round's own role strings (`.ufo/waves/round-16/build/make_spec.py:172-179`) and the committed overlapping build-advice files, which is the in-lane record for those declarations. [INFERENCE] where the append says so.
- The API-key ordering and router-mode behaviours are code reads at the pinned commit plus the lane's knowledge entry; no live keyed or router-mode server was started (and none may be, from this seat).
- I did not evaluate whether `consumer-registry.md` also needs a pointer; it received its own round-16 vocabulary correction and its subject is consumers, not host artifacts.
- No scratch directory was created; nothing under `/tmp/kama-r16-ConnectCrossLaneScope/` exists to clean up.

## Installs

None. No tool was installed or upgraded; no pacman transaction was attempted.
