# S9Skill — round-49 SKILL.md instrument registry rows (kama-r49-w1)

**Verdict:** five registry rows and one how-to section drafted and proven on a scratch clone at `74558c71c38ceaeace15fd4cf8aa9d84977584b1` — `python3 tools/gate-registry-check.py --repo <clone>` goes from `registered 42 unregistered 2 defective 0` (exit 1) to `registered 44 unregistered 0 defective 0` (exit 0), the clone's `--selftest` matrix reports `GATE_SELFTEST pass=6 fail=0`, and every pinned value in the rows was measured here (not copied from the L1 dry run).

## Deliverable

`.ufo/waves/round-49/w1/out/S9Skill/skill.md` — the exact markdown to append after the round-48 sections (the file at `74558c71` ends at line 1484, inside `### Re-running live evidence (v5, round 48)`; the fragment starts with a blank line and a new `## Round-49 …` heading, so it closes that section cleanly). Contents:

1. `## Round-49 instrument registry (replay execution witness, append-only v4 definitions)` + intro naming seat, commit and what was measured.
2. `### Re-running live evidence (witnessed replay, round 49)` — five bullets: the witnessed-replay command, what the outside observer checks and that `witness.released` records only the tool's own view, that the witness is excluded from matching, the graded counter form, and the record-time archive bounds.

| # | Row | Source of every claim |
|---|---|---|
| 1 | Round-49 C1 replay-witness audit (`tools/round49-replay-witness-audit.py:1-100` docstring, argparse `:406-410`, output/exit `:461-471`) | ran it: exit 0, 12.7 s |
| 2 | Round-49 C2 append-audit v4 check (`tools/round49-append-audit-v4-check.py:1-100`, argparse `:365-369`, exit `:392-404`) | ran it: exit 0, 4.4 s |
| 3 | Round-49 append-only audit v4 (`tools/append-only-audit.py:1-27` v4 header, `binds()` `:212-232`, origin `:420-440`, `"definition": "v4"` `:504-506`, selftest cases `:908-931`) | ran `--selftest` on both revisions and the tool on the clone |
| 4 | Round-49 live lifecycle receipt v5 bounded archive + witness hold (`tools/kama-llamacpp-live.py:44-56`, `:208-295`, `hold_for_witness()` `:298-320`, flags `:1264-1270`, post-witness verify `:1860-1868`) | ran `--selftest`; read the diff |
| 5 | Round-49 witnessed live receipt replay (`tools/kama-live-replay.py:41-45`, `:234-282`, flags `:450-455`, `:481-482`) | ran `--selftest`; C1 drove it 3/3 |

## Evidence

All on the scratch clone `/fast/scratch/hyaku/kama-r49/S9Skill/lane` (`git clone --shared` of the lane, detached at `74558c71…`); the clone's working tree was clean before the fragment was applied.

**Gate, before and after** (`gate-registry-check.out` has the full transcript):

```
$ python3 tools/gate-registry-check.py --repo $S/lane --rev 74558c71c38ceaeace15fd4cf8aa9d84977584b1
unregistered tools/round49-append-audit-v4-check.py
unregistered tools/round49-replay-witness-audit.py
registered 42 unregistered 2 defective 0                       EXIT=1

$ cat skill.md >> $S/lane/SKILL.md
$ python3 tools/gate-registry-check.py --repo $S/lane
registered 44 unregistered 0 defective 0                       EXIT=0

$ git -c user.name=… commit -a -m "round-49: draft SKILL.md …"   -> 92c387e2 (clone only), SKILL.md | 20 +
$ python3 tools/gate-registry-check.py --repo $S/lane --rev HEAD
registered 44 unregistered 0 defective 0                       EXIT=0

$ python3 tools/gate-registry-check.py --selftest
PASS lane-tip 92c387e21c94: exit=0 line='registered 44 unregistered 0 defective 0'
GATE_SELFTEST pass=6 fail=0                                    EXIT=0
```

**Pinned values, each measured on the same clone** (`c1-check.out`, `c2-check.out` are the archived receipts):

- C1 `tools/round49-replay-witness-audit.py --repo $S/lane --tip 74558c71… --scratch $S/c1` → exit 0, 12.7 s: `witness=1 cap=1 newrow=1 witnessed=3/3 met=True`; `counter vocabulary: 512 tokens`; three witnesses `pid … port … exe+listen+model ok, nonce 'kama witness …' round-tripped`; `cap sparse-1e15: exit 2 setup_error 'provenance-member-sparse' executed=False seconds=0.1 ok`; control `cap member-is-server-control: … executed=True`; `newrow: 2 rows new since base; 1 name the README at caa8191df159 and /tokenize: ['| S494 |']`.
- C2 `tools/round49-append-audit-v4-check.py --repo $S/lane --tip 74558c71… --scratch $S/c2 --out …` → exit 0, 4.4 s: `fixture=1 lane=1 scenarios=8/8 met=True`, eight `detail: scenario … ok` lines, `lane: tool exit 0 events 5 bad_declarations 0 regressed 0 ungraded_lines 82`, `event dd9f5dc6c0e6 … ungraded 17 <= natively exempt 23`, `event 0718b6abbda6 … ungraded 65 <= natively exempt 65`.
- `tools/append-only-audit.py --selftest --scratch $S/ao` → `AOA_SELFTEST pass=30 fail=0`, exit 0. The round-48 tool (`git show 438127bc:tools/append-only-audit.py`) → `AOA_SELFTEST pass=28 fail=0`, so the two round-49 cases (`launder-through-head`, `binding-v4`) account for the delta.
- v4 on the clone with the tip contract: `event 0718b6abbda6 SCORECARD.md deleted=2421 graded=2356 ungraded=65 …`, `summary … ungraded_lines=82 …`; the round-48 tool on the same clone: `graded=2349 ungraded=72`, `summary … ungraded_lines=89` — so the row's "72 -> 65, 89 -> 82" is measured, not quoted.
- `tools/kama-live-replay.py --selftest --scratch $S/klr` → `KLR_SELFTEST pass=22 fail=0`, exit 0.
- `tools/kama-llamacpp-live.py --selftest` → `selftest: ok; closed tcp6 listeners ::1:35727, ::ffff:127.0.0.1:44609`, exit 0.

No tool was installed or upgraded for this seat.

## Findings (contracts / instruments, not fixed in place)

1. **The gate's lane arm reads `master`, not HEAD or the working tree** — `tools/gate-registry-check.py:335` (`git rev-parse --verify master`). On a checkout of the build tip, `--selftest` therefore reports both round-49 counters unregistered (exit 1) even with the rows in the tree, while the plain and `--rev` invocations are clean. I passed the matrix by moving the *clone's* `master` to the clone-local commit `92c387e2`; the lane's `master` was not touched. Integration note for L1: use `python3 tools/gate-registry-check.py` (or `--rev <tip>`) for the round-49 receipt; run `--selftest` only once the rows are on `master`.
2. **A bare `host/org/…/file.ext` token in any row is graded a repository path** — `RE_PATH` (`tools/gate-registry-check.py:73-76`) + the `missing-path` arm (`:210-217`). Proven on the clone:
   `| probe | … | model huggingface.co/ggml-org/models-moved/resolve/499bc/tinyllamas/stories260K.gguf | read-only |` → `defective tools/round49-replay-witness-audit.py: missing-path:huggingface.co/…/stories260K.gguf`, `registered 44 unregistered 0 defective 1`, exit 1 (reverted; clean again afterwards). A scheme-prefixed URL in the same cell is harmless (the lookbehind blocks the match straight after `//`), which is why the round-48 rows could name `https://…` sources. The drafted rows keep every URL scheme-prefixed or placeholder-only (`<clone>`, `<dir>`, `<commit>`); if a later editor drops the scheme, the gate flips to exit 1.
3. **Corollary for the integration commit:** `corpus/lessons/round-49.md` does not exist at `74558c71`, so the rows deliberately do not cite it (that would be a `missing-path` defect). When S494/S495's `used-by` lesson lands, add the pointer in the same commit as the file, or the gate regresses.
4. **Both round-49 counters print `could-not-evaluate:` on stdout, not stderr** (`round49-replay-witness-audit.py:424`, `round49-append-audit-v4-check.py:392`), unlike the round-44/45 counters whose rows say stderr. The rows state stdout explicitly so a reader does not grep the wrong stream.
5. **A `|` line that is not part of a five-column table is ignored** — `registry_rows` requires a header/separator pair (`gate-registry-check.py:148-172`, `len(block) >= 2`). A stray row can neither register nor deregister a counter; the fragment therefore ships its own header, which is what moved `registered 42 -> 44`.
6. Row-order detail: both counters print `tip=<full>` **before** the summary line (`round49-replay-witness-audit.py:464-466`, `round49-append-audit-v4-check.py:399-401`). The round-48 rows describe the opposite order for those round's counters; the drafted rows follow the code.

## Out of scope / left to integration

- The two round-49 counters are registered only in the drafted fragment; the lane at `74558c71`/`master` still reports them unregistered until the L1 appends it.
- SCORECARD, LOG, QUALITY, README and the lesson entries for round 49 are other seats' items; nothing here writes them.
- The rows pin `74558c71` as the measured commit. If the L1 rewrites a row after hardening fixes, the measured values must be re-measured against the new tip (the round-47 precedent).

## Writes

- Lane: none (read-only; only `git log`, `git show`, `git diff`, `git cat-file`, `git ls-*` against it).
- Fleet root: none.
- Written: the three files under `.ufo/waves/round-49/w1/out/S9Skill/` and this report. Scratch `/fast/scratch/hyaku/kama-r49/S9Skill` removed; the `llama-server` children started by the C1 counter were torn down by it (checked with `pgrep -af llama-server`: no `S9Skill` path remains — the surviving ones belong to peers `X1Kill`, `X1Observe`, `Sen1Witness`).

## Artifacts

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/S9Skill.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/S9Skill/skill.md` (the fragment to append)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/S9Skill/gate-registry-check.out` (gate transcript, baseline → clean, probes)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/S9Skill/c1-check.out` (C1 counter output at 74558c71)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/S9Skill/c2-check.out` (C2 counter receipt at 74558c71, via `--out`)
