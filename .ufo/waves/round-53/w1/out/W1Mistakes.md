# W1Mistakes — round 53, lane kama (post-wave, build `c22602bd`)

**Verdict:** the round-53 `## Mistakes` draft is delivered — the four routed mistakes plus
**three defects found in this round's build**, each with an evidence pointer re-derived from
committed bytes (or a fetched URL) and a fix whose check is shown failing on the bad state;
the build's C1/C2 receipts and the ledger's disclosures were spot-checked and **two build
defects** stand (head-table hash stale, `untracked` note false), while the round-53 Gate's
own quotes/anchors are clean.

## What was done (behaviour)

Read-only mining of: preregistration, both counters' docstrings (the contract), both build
receipts, both base controls, the round-52 lesson and closure, the round-52 seat W3Mistakes
prototype and its real-history output, the C2 correction ledger, `SCORECARD.md` head and
appended section, `SKILL.md` diff, the four `SOURCES.md` rows and the committed C1 text
copies, the `tools/` diffs of both changed tools, and the fleet repo's `.ufo/l0-questions.md`
history. Nothing was rerun to decorate the report; the only executions are two small checks
written here and run against the base and the build.

## Gates (each with the command and its exit)

| Gate | Command | Result |
|---|---|---|
| Round-53 counter contract vs receipts | `read` of both docstrings + `measured/*.out`, `controls/*.out` | C1 target `bind=1 sealed=1 code=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 coderuns=3/3 met=True` and base `code=0 newrow=0 coderuns=0/3 met=False` (exit 1); C2 target `fixture=1 lane=1 scenarios=8/8 … undisclosed=0 … met=True` and base `lane=0 unresolved=16 undisclosed=16 met=False` (exit 1) — polarities match the preregistration |
| S505 anchor/word count (R1) re-derived | `sed -n '422,439p' reg.cpp \| grep -c 'default search paths'`; `sed -n '491p'`; word count | `0`; the comment at 491; `7` words (seat claimed 21, anchor 422–439) |
| S509 correction row re-derived | `.ufo/waves/round-53/w1/out/W1Mistakes/anchor-quote-check.py --row S505 / --row S509` (`checks.out`) | S505 `in_anchor=False met=False` exit 1; S509 `occurs_at=[491] in_anchor=True met=True` exit 0 |
| S509 copy provenance | `curl …/b11909/ggml/src/ggml-backend-reg.cpp \| sha256sum` vs committed copy | `1436b46b…` both; `get_executable_path` 401, `ggml_backend_load_best` 480, `GGML_BACKEND_DIR` 488–489, quote 491 |
| Round-53 Gate cells (S506–S508) | quotes located in the committed text copies; page dates from `curl` of the three man7 HTML pages | §52 / §1586-1588 (yama item `1 ("restricted ptrace")`) / §84-86, all verbatim; `man-pages-6.19`, dated 2026-02-08 / 2026-06-05 / 2026-02-08 — cells exact |
| Ledger disclosures vs the repositories | 6 `SCORECARD.md` line references read; 11 `ConfirmM*` dirs; round-40 `controls/c2-base.out`; round-31 `c2-*.json`; `git cat-file -e 9874e455^:…utils.hpp` / `9874e455:…`; 4 `curl`+`sha256` of the pinned `tools/server/*.cpp` | all accurate except the `.ufo/watchdog.log` note (finding 7); upstream digests `b4f4aae7/1f9d7b73/4c3f413b/91f48e09` equal `SKILL.md:1245-1248` |
| SCORECARD head re-derives at the build (KQ49) | `head-hash-check.py --tip 4229ea1b… / c22602bd…` (`checks.out`) | base `hash_facts=7 hash_bad=0 met=True` exit 0; build `hash_bad=1 met=False` exit 1, `detail: depth: SKILL.md sha256 want cfcc429130ed got a6a19d135801` |
| L0 line filed for the round-52 operator item | `git -C <fleet> show ee9f7341^:.ufo/l0-questions.md \| grep -c '^kama \| round-53'`; `… d2a6c59a:…` | `0` before, `2` after; `git -C kama-shokunin log -1 --format=%s ed135b3c` → `Revert "HOURS.md: …"` (the L0 line's first text called it the adding commit) |
| C1 statement vs code | prereg `claims[0].statement` ("dev and inode") vs `tools/kama-llamacpp-live.py:813` `(sdev != dev and st.st_uid != 0)` vs `corpus/lessons/round-53.md:11` | statement unconditional-dev is false for root-owned host files; the lesson omits dev for tree files; only the frozen `disclosure` and the tool docstrings state the exemption |

## Findings (the seven rows, in the draft)

1. S505's anchor `lines 422–439` and the seat's "21 words"/"line 431" were never checked
   against the source (KQ45 has had no instrument); fixed by S509, and the fix is checkable.
2. The round-52 prototype's 50 "pre-existing" misses were never examined; the round-53 C2
   counter now fails on them at the base and passes at the build.
3. The round-52 closure's operator item (`ed135b3c` restored history) was carried in the
   report only; round 53 filed it at fleet `ee9f7341`.
4. That L0 line as first filed misnamed `ed135b3c` (it is the `Revert` commit); corrected at
   fleet `d2a6c59a`, 392 s later.
5. **Build defect:** `SCORECARD.md:16` still pins SKILL.md `cfcc429130ed…`; the build's
   in-place SKILL.md corrections make it `a6a19d135801…`. Re-anchor after the §Round-53
   registry (which edits SKILL.md again) or record the mismatch line.
6. **Build defect:** the graded C1 statement and the lesson's C1 row each misstate the
   dev/inode comparison in opposite directions; an erratum next to the claim is owed.
7. **Build defect:** the C2 ledger calls `.ufo/watchdog.log` "never committed" — the fleet
   tracked it from `609ecb6e` (2026-09-28) to `7930399e` (2026-10-26) and gitignores it now
   (`.gitignore:10`); `git log --all -- .ufo/watchdog.log \| wc -l` → 557. Class is right
   under the frozen rule; the reason is false and the counter cannot see it.

Not raised as rows: the receipts run `--repo .` instead of the preregistered `<lane clone>`
(the counters read `git show <tip>:…`, so the named tip's bytes are the measured bytes);
`corpus/lessons/round-52.md:34`'s wrong "line 431" remains as committed history in an
append-only file, with S509 as the correction row the closure asked for.

## Touched surfaces

Wrote only under `.ufo/waves/round-53/w1/out/W1Mistakes/` and the report file
`.ufo/waves/round-53/w1/out/W1Mistakes.md`. No lane or fleet file edited, no git/jj
mutation anywhere, no clone created (read-only `git show/log/cat-file` in the lane and
fleet repos), no counter rerun, no service started or stopped, no subagent, no package
transaction. Scratch `/fast/scratch/hyaku/kama-r53/W1Mistakes` removed after the cited
inputs were copied out.

## Out of scope (not done here)

SCORECARD §Round-53 section and measured results, LOG entry, QUALITY rows, README frontier,
SKILL §Round-53 instrument registry, lesson integration of these rows, Planned (round 54),
and any fix of findings 5–7 (proposals only; the ledger row 7 change must be an appended
dated comment, never an in-place rewrite).

## Artifacts (absolute)

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/W1Mistakes.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/W1Mistakes/mistakes.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/W1Mistakes/checks.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/W1Mistakes/anchor-quote-check.py`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/W1Mistakes/head-hash-check.py`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/W1Mistakes/c1-build.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/W1Mistakes/c2-build.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/W1Mistakes/base.c1.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/W1Mistakes/base.c2.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/W1Mistakes/ggml-backend-reg.cpp.b11909`
