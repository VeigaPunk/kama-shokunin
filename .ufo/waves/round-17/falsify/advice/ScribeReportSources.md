VERDICT: confirm — SOURCES 41→46 and zero changed old rows reproduce at 54a29268; M1 reproduces as a guard failure; S042–S045 quotes match pinned bytes or the cited page; frontier advanced one item to held, no new coverage ground.

# Sources & frontier

Attacked: the round-17 registry count (41→46), the append-only claim (KQ22), the mined mistake M1 (S041), the sourced C2 rows (S042–S044, with S045 vocabulary), the S046 receipt row, and the frontier-advance claim in `corpus/README.md` §Round-17. Everything was run in a clone pinned at 54a29268e2083caa2b1e0d54ee1e7d90961302f3; the lane was read only.

## Row counts (census)

- Command (fleet read-only script, `--file` pointed at the clone copy): `PYTHONDONTWRITEBYTECODE=1 bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh census --file <clone>/corpus/SOURCES.md kama`
- Before, `cff9e62:corpus/SOURCES.md` (`git show cff9e62:corpus/SOURCES.md`): rows 41; tier A 38, C 3; status mined 31, queued 5, rejected 5; missing 0; exit 0.
- After, `54a2926:corpus/SOURCES.md`: rows 46; tier A 43, C 3; status mined 36, queued 5, rejected 5; missing 0; exit 0.
- Independent row count, `grep -c '^| S0'`: 41 → 46.
- `validate --today 2026-10-20 --file corpus/SOURCES.md kama`: exit 0, no E-codes. Two W04 warnings: S031 (already in `.ufo/waves/round-17/sources-before-validate.txt`) and S043 (new). S043 shares S037's URL with a different scope and anchor, as `corpus/SOURCES.md:168` discloses. W-codes never change the exit code, so this is not a failure. [INFERENCE: the warning is the disclosed one.]

## Rows added by tier

- Tier A: +5 (S042–S046, `corpus/SOURCES.md:54-58`). Tier C: +0.
- Status: mined +5 (31→36). Queued 5→5. Rejected 5→5.
- All five new rows are `A | mined | 2026-10-20`.

## Rows touched, old→new: none

- `git diff cff9e62 54a2926 -- corpus/SOURCES.md`: 20 insertions, 0 deletions. Exactly five added `| S0` row lines (S042–S046). The other 15 added lines are the round-17 search-log supplement at `corpus/SOURCES.md:157-168`.
- `python3 tools/sources-append-only.py --from cff9e62 --to 54a29268e2083caa2b1e0d54ee1e7d90961302f3 --json`: exit 0, `violations: []`, `added: [S042..S046]`, `ok: true`.
- `python3 tools/sources-append-only.py --selftest`: 14/14 cases pass, exit 0.
- Only commit in the round touching SOURCES: `54a2926` (`git log cff9e62..54a2926 -- corpus/SOURCES.md`). `cff9e62` is not a SOURCES-touching commit; its last one is `ccc4bb3`, and SOURCES is byte-identical from `ccc4bb3` to `cff9e62`. So the round pair is equivalent to `ccc4bb3`→`54a2926`.

## Frontier rows advanced (`corpus/README.md` §Round-17, lines 234-246)

- Table rows 238-239: `knowledge/llamacpp-loading-lifecycle.md` §Round 17 "deepens the round-16 entry, no new ground" (lifecycle knowledge appended at `corpus/knowledge/llamacpp-loading-lifecycle.md:150`); and `lessons/round-17.md`.
- Frontier disposition, `corpus/README.md:241-246`: "live grading of a loading server by the receipt" is now held. Receipt v2 grades every observed 503 body and fails a run that observes none.
- Still open per the same paragraph: router mode and sleep, other engines, K05 declared-versus-served context, registered consumers (still DEAD).
- Count: 1 frontier item moved to held; 0 coverage-map rows advanced; 0 new coverage ground. The claim matches the text.

## Mined mistake M1 (S041)

- Claim, `corpus/lessons/round-17.md:85`: S041 `anchor` and `teaches` rewritten in place after first commit. The edit is in `ccc4bb3`, which is before the round start `cff9e62`.
- Reproduced: `python3 tools/sources-append-only.py --from b8e485c --to ccc4bb3 --json` exits 1. Violation on S041: `anchor` changed from `…13:49:38.170Z, port 32845, 10 checks` to `…14:06:27.974Z, port 37527, tool sha256 b8c5e8d4…`. `teaches` also changed (the loading-envelope sentence was added). The guard fails on the case it was built for, which supports KQ22.
- Round 17 itself is clean: `cff9e62`→`54a2926` shows no S041 change, and S041 is still at `corpus/SOURCES.md:53`.
- Limit [INFERENCE]: the guard compares commit pairs. An edit made inside the same commit where a row first appears (such as `54a2926` for S042–S046) is invisible to it. Only the non-author spot-check can catch that, which matches the M1 note at `corpus/lessons/round-17.md:85`.

## Sourced claims, C2 (S042–S045) and S046 receipts

Pins: `.ufo/waves/round-17/sources/pins.json`. The on-disk raw copies under `.ufo/waves/round-17/sources/llama.cpp-704366d76/tools/server/` match the pinned sha256 values:
- `server-context.cpp` dd1de0f2…
- `server.cpp` 21439622…
- `server-http.cpp` 24ede172…
- `README.md` 714c067b…

- S042 (`server-context.cpp`): line 5297 `res->ok({{"status", "ok"}});` and the comment at line 5289 "error and loading states are handled by middleware". Both verified.
- S043 (`server.cpp`): line 33 "Received second interrupt, terminating immediately.", line 34 `exit(1);`, line 575 "this call blocks the main thread until queue_tasks.terminate() is called", line 590 `return 0;`. All verified.
- S044 (Python 3.14.8 `subprocess` page, fetched via `read`): "A negative value `-N` indicates that the child was terminated by signal `N` (POSIX only)." Verified. The row strips the backticks.
- S045 (PIT basic concepts, fetched via `read`): "Killed means a test caught the mutation successfully." Verified verbatim.
- S046 receipts `.ufo/waves/round-17/live/receipt-{1,2,3}.json` (schema `kama-llamacpp-live/v2`, 11 checks each). `gate.txt` reports VALID for all three, exit 0. `loading_envelope_graded.observed.total_503_responses` is 42, 45, 45, with `distinct_bodies` 1 in each. These match `knowledge/llamacpp-loading-lifecycle.md:187` and the README's "42–45 per run".

## Limitations

- The search-log counts at `corpus/SOURCES.md:157-168` ("identified 7, screened 7, included 4") are not reproducible from lane files; the search log is not in the lane. [INFERENCE: not checked.]
- Pinned line numbers were checked only at the quoted lines, not the full `[5288-5299]` span.
- The fleet census script lives outside the lane (`/home/vgpnk/Projects/shokunin/scripts/sources-census.sh`). It was read and run with `--file` only; nothing was written.

## Commands and exit codes

1. `git clone -q <lane> /tmp/ScribeReportSources-clone && git -C … checkout -q 54a29268…` → 0.
2. `git show cff9e62:corpus/SOURCES.md > /tmp/ScribeReportSources-scratch/SOURCES-cff9e62.md` → 0.
3. `sources-census.sh census --file …cff9e62… kama` → 0 (41 rows).
4. `sources-census.sh census --file corpus/SOURCES.md kama` → 0 (46 rows).
5. `sources-census.sh validate --today 2026-10-20 --file corpus/SOURCES.md kama` → 0 (W04 S031, S043).
6. `python3 tools/sources-append-only.py --from cff9e62 --to 54a2926 --repo <clone> --json` → 0, ok.
7. `python3 tools/sources-append-only.py --selftest` → 0, 14/14.
8. `python3 tools/sources-append-only.py --from b8e485c --to ccc4bb3 --repo <clone> --json` → 1 (M1 reproduced).
9. `git diff cff9e62 54a2926 -- corpus/SOURCES.md | grep -c '^-[^-]'` → 0 deletions; `grep -c '^+| S0'` → 5.
10. `git diff cff9e62 54a2926 --stat -- corpus | tail -1` → 7 files, 301 insertions.
11. `sha256sum` on the four raw llama.cpp copies → match `pins.json`.
12. Quote greps on the raw llama.cpp copies → each line found at the cited number.
13. `read` of the Python 3.14 subprocess page and the PIT basic-concepts page → quotes verified.
14. Receipt parsing (`json`) and `gate.txt` → VALID ×3; 42/45/45 loading 503s.
15. `ss -ltnp | grep -E '8080|34113'` → no output; no port bound or contacted.

Installs and updates: none. No llama-server was started. No lane file, MANIFEST, `.ufo/state/` or sibling repo was written. Scratch directories `/tmp/ScribeReportSources-clone` and `/tmp/ScribeReportSources-scratch` are removed after this report is written.

Integration status (for L1): [L1 fills after falsify]
