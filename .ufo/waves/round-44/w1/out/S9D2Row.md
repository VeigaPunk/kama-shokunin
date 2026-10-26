# S9D2Row — Round-43 D2: register the code source behind the runtime-health entry's process claim

**Verdict:** D2 is closed at draft level — S483 (`vllm/entrypoints/cli/preload.py` @ v0.31.0, `code`/A) is drafted with a digest-verified anchor and a Gate line, the entry's `source:` edit is a one-line diff, and `sources-census.sh validate` on a lane-shaped copy with the row inserted exits **0** with output byte-identical to the pristine file (0 E, 93 W04, 1 W01 S481). Two findings, neither in the row: the round-43 closure's "clears validate W01" expectation is wrong about how W01 is computed, and `validate --file` silently requires a lane-shaped directory.

Axes: freshness (an `on-release` code source now has a row with a re-fetchable anchor) and calibration (the row's scope is narrower than S481's claim; it does not upgrade S481's tier-C description into runtime evidence).

## Provenance

- Lane working tree read at `/home/vgpnk/Projects/shokunin/kama-shokunin` (commit 77d1bbf55c62a1d5fc08fcbd682f22277a5cdb40 + round-44 drafts). No lane file was written: the candidate registry lives in `out/S9D2Row/SOURCES.candidate.md`, the entry edit only as `entry-source-line.proposed.txt` / `.diff`.
- Scratch: `S=/fast/scratch/hyaku/kama-r44/S9D2Row` (removed at the end; every receipt below was copied out first).
- No tool installs, no pacman, no service start/stop, no subagents. One `curl` GET and two `gh api` reads of the same file object.

## 1. Re-fetch and digest comparison (D2's first half)

```
$ curl -sS -w '\nHTTP %{http_code}\n' -o "$S/preload-refetched.py" \
    https://raw.githubusercontent.com/vllm-project/vllm/v0.31.0/vllm/entrypoints/cli/preload.py
HTTP 200
$ ls -l preload-refetched.py
-rw-r--r-- 1 vgpnk vgpnk 12631 … preload-refetched.py
$ sha256sum preload-refetched.py .ufo/waves/round-43/c3/vllm-v0.31.0-preload.py
d2704e80c08f49455c048724dce8d1eeb22bfa9bc97961ef567106425effa57d  preload-refetched.py
d2704e80c08f49455c048724dce8d1eeb22bfa9bc97961ef567106425effa57d  …/round-43/c3/vllm-v0.31.0-preload.py
$ cmp mergecommit-preload.py preload-refetched.py && echo 'CMP: identical'
CMP: identical
```

- Committed copy unchanged since round 43: same SHA-256 `d2704e80c08f49455c048724dce8d1eeb22bfa9bc97961ef567106425effa57d`, 12631 bytes.
- Response headers (`out/S9D2Row/fetch-head.txt`): `HTTP/2 200`, `content-length: 12631`, no redirect.
- Independent leg: `gh api repos/vllm-project/vllm/contents/vllm/entrypoints/cli/preload.py?ref=e7900156e130c9880eb03b7c1f2df32820e7a2be` → size `12631`, git blob sha1 `50734a052bb01b613a831f982c3ad0449951a123`; base64-decoded content has the **same** SHA-256 and `cmp` equals the tag copy. So the round-43 entry's sentence "byte-identical to the merge commit's" is reproduced, not merely inherited.

## 2. Route lines (D2's second half)

`/fast/scratch/hyaku/kama-r44/S9D2Row/preload-refetched.py` (339 lines):

| line | text |
|---|---|
| 63-67 | `@property` / `def is_ready(self) -> bool:` … line 67 `return ready and not any(proc.exitcode is not None for proc in self.processes)` |
| 70 | `def _build_health_app(state: _HealthState) -> FastAPI:` |
| 73 | `    @app.get("/health", include_in_schema=False)` |
| 74 | `    async def health() -> Response:` |
| 75 | `        return Response(status_code=200 if state.is_ready else 503)` |
| 133-138 | `--weight-cache-health-port`, `default=None`, line 137 `help="Port for the parent /health endpoint; disabled by default."` |
| 302 | `        health_state.mark_ready()` — after the startup loop; the dead-rank path 288-301 ends at `sys.exit(...)` |

Mechanical check: a python comparison of 10 expected line texts against the fetched file printed `OK` for each, `mismatches: 0`. The route is the preload CLI's own app (`_start_health_server` at line 80 is called only under `if args.weight_cache_health_port is not None:` at line 263), and the wire carries exactly two statuses: 200 while `is_ready`, 503 otherwise — `starting` and `failed` are not distinguishable. That is narrower than S481's three-name vocabulary and is written into the row's `teaches` cell.

## 3. Registry row S483 (drafted, not inserted)

Full row: `out/S9D2Row/row.tsv`, rendered in `out/S9D2Row/row.md`. Shape: `code` | `A` | scope limited to *which process answers `/health` and its 200/503 states at tag v0.31.0* | anchor = lines 63-67, 70-77, 133-138, 302 + tag + SHA-256 + byte-identity to the merge commit | status `mined` | opened `2026-10-26` | recheck `on-release` | used-by `corpus/knowledge/runtime-health-surface-processes.md`.

Mechanical shape facts: 12 `|` ⇒ 11 cells; no cell contains a pipe; `grep -c 'preload.py' corpus/SOURCES.md` → **0**, so URL and scope are new (no E04); insertion point is line 235, directly after S481 at line 234.

## 4. Gate line (drafted)

`out/S9D2Row/row.md` §Gate line: URL, `accessed 2026-10-26`, headers receipt, SHA-256, copy path, then two located quotes — line 73 `@app.get("/health", include_in_schema=False)` (process half, with line 70 and line 263 as the "whose app" context) and line 75 `return Response(status_code=200 if state.is_ready else 503)` (**11 words**, states half). The lesson consumer should paste it into `corpus/lessons/round-44.md`; this seat does not write lesson files.

## 5. Entry edit (one line)

`corpus/knowledge/runtime-health-surface-processes.md:1` is the `source:` line, 704 chars today; the proposed line 1 is 1234 chars and appends exactly one `; S483 — …` clause (proposed text `out/S9D2Row/entry-source-line.proposed.txt`, SHA-256 `758fc620396cc80397dd30cb715e5055c439772344e93aee7007308ed0f4c24e`; unified diff `out/S9D2Row/entry-source-line.diff`). No other line of the entry changes — the body already states the two-outcome reading, so the row grounds a claim that is already written rather than adding one.

## 6. Validation

Asked-for command, run twice on two copy shapes:

**A. Lane-shaped copy** (`$S/lane-copy/corpus/SOURCES.md`, every lane top-level tree and `.ufo` symlinked beside it, candidate row at line 235):

```
$ /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --file "$S/lane-copy/corpus/SOURCES.md"
… 94 warning lines (93 W04, 1 W01 S481) …
file	ok	/fast/scratch/hyaku/kama-r44/S9D2Row/lane-copy/corpus/SOURCES.md
exit 0        # 0 E
$ diff validate-baseline.out validate-candidate.out && echo IDENTICAL
IDENTICAL     # same run on the pristine SOURCES.md, same layout
```

`grep 'S483' validate-candidate.out` → no match: the row raises no E and no W. `census --file` before → after: rows 222 → 223, tier.A 211 → 212, status.mined 203 → 204, queued 8, rejected 11, missing 0, exit 0 both.

**B. Flat copy** (`$S/SOURCES.candidate.md`, nothing beside it) — the literal "<copy>" form:

```
$ /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --file "$S/SOURCES.candidate.md"
file	E11	S483 missing used-by corpus/knowledge/runtime-health-surface-processes.md
… 407 more E11 lines for pre-existing rows …   (94 W + 408 E = 502 lines)
exit 1
```

Run B's E11 lines are a path-resolution artifact, not row defects (see finding 2); every `used-by` in the file, including S480's and S481's, reports missing there.

## 7. Findings

**F1 — the round-43 closure's success criterion for D2 is wrong (calibration).**
`corpus/lessons/round-43-verifier-spotcheck.md:106` says registering the row "clears validate `W01`". It does not and cannot: W01 is emitted for any `tier=="C" && status=="mined" && usedby!="—"` (`/home/vgpnk/Projects/shokunin/scripts/sources-census.sh:669-670`), so S481 keeps its W01 as long as it is tier C with a used-by. Reproduction: `sources-census.sh validate --file $S/lane-copy/corpus/SOURCES.md | grep W01` → `file	W01	S481 tierC mined used-by=…`. The coordinator for D2 should expect "W01 still 1, but S481 is no longer the claim's sole support", not "W01 cleared". Proposed fix (lesson text only, not a lane edit): replace "clears validate `W01`" with "removes S481's role as sole support; W01 S481 persists until the row's tier or used-by changes".

**F2 — `validate --file` silently depends on the copy's directory shape (tooling).**
`/home/vgpnk/Projects/shokunin/scripts/sources-census.sh:497-503` sets `dir_abs=$(realpath "$(dirname "$file_abs")/..")` and `usedby_findings` tests each `used-by` path against that base, so a copy placed anywhere else reports E11 for every row in the registry (408 lines here, exit 1). A seat that follows the instruction "validate a scratch copy" literally gets exit 1 and can only conclude the row is broken. Proposed fix (fleet script, not mine to edit): in the `--file` branch, honour an explicit `--root` for the used-by base, or print a one-line stderr note when `dir_abs` contains no `corpus/` sibling. Reproduction command as in §6.B.

**F3 — S481's `W01` is the surviving hygiene cost of the entry, unchanged.** Out of scope for D2 as written; recorded so the lane does not read this seat's 0 E as "W01 gone". Clearing it needs a tier move or a used-by change on S481, both admission decisions the entry's own `Limits` section currently declines.

**F4 — no defect found in the frozen counters or preregistration.** Neither `tools/round44-release-recheck-audit.py` nor `tools/round44-verdict-ledger-audit.py` is touched by this item; the only frozen artifact this seat exercised is the fleet validator, read-only.

## 8. Limits

- One file at one tag. No vLLM process was run and no host contacted beyond three GitHub object reads; nothing here says the endpoint answers (KQ4).
- v0.32.0 and `main` are not read; the row's `on-release` cadence is the only recheck it promises.
- The row's `teaches` cell records what the code prints, not what a supervisor receives; rank readiness still arrives over a multiprocessing queue per S481 and is not re-verified here.
- The entry's own three-state sentence is left alone: this item registers a source, it does not amend prose.

## Artifacts written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/S9D2Row.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/S9D2Row/row.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/S9D2Row/row.tsv`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/S9D2Row/vllm-v0.31.0-preload.py`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/S9D2Row/mergecommit-e7900156-preload.py`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/S9D2Row/fetch-head.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/S9D2Row/sha256.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/S9D2Row/SOURCES.candidate.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/S9D2Row/entry-source-line.proposed.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/S9D2Row/entry-source-line.diff`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/S9D2Row/validate-baseline-lane-shaped.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/S9D2Row/validate-candidate-lane-shaped.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/S9D2Row/validate-candidate-exit.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/S9D2Row/validate-flat-copy.out`
