# SC01Lesson — round-80 lesson draft (scribe)

Seat: SC01Lesson · lane kama · round 80 · wave w1 · base `c45fc7d1a8427e9c98a9dd7befa542c7b5caed38`
· lane tip observed `dea7c269446994de1e5e0cd8f34767e83207bd81` (master; tip moved from `fe7b9780`
mid-seat).

## Behavior

Drafted the round lesson at the seat path with the three required sections in order — `## Gate`,
`## Corrections`, `## Mistakes` — and the three frozen correction blocks byte-exact. Opened all three
Gate URLs myself with `curl` this round and recorded status, bytes, sha256 and the located lines in one
receipt per row. Read the round-79 record and its receipts at the sealed revision with `git show`
(read-only) to write one prose paragraph per correction stating what the record claimed and what its own
receipt prints. Wrote nothing outside the seat directory; no commit, no `git add`, no gate scored run.

## Gates (commands run, with exit codes)

| # | Command (as run) | Result | Exit |
|---|---|---|---|
| 1 | `curl -sS -o body -w '%{http_code} %{size_download}' https://raw.githubusercontent.com/ollama/ollama/v0.40.11/docs/api.md` | `200 54614`; sha256 `96db03080e385dbabf5d70e75f298d41b75983bc30975cae56f7119f848dd0f5` | 0 |
| 2 | `curl -sS -o body -w '%{http_code} %{size_download}' https://raw.githubusercontent.com/ggml-org/llama.cpp/39febd2adb947b70da35e95f9351b3bf58ad170a/tools/server/README.md` | `200 135608`; sha256 `8fd5abde2fb52de3b30f30a170631d4c0d92febecc8da44d0541e48b132b35c6` | 0 |
| 3 | `curl -sS -o body -w '%{http_code} %{size_download}' https://raw.githubusercontent.com/ggml-org/llama.cpp/39febd2adb947b70da35e95f9351b3bf58ad170a/docs/preset.md` | `200 4090`; sha256 `3e6643541e12ff3dfee2a23c23a57357403bf4500beced780f010eaebbbdfe13` | 0 |
| 4 | `cmp raw-preset-pinned.body raw-ca66ca13e4a4.body` (pinned `39febd2a` vs `master` copy) | identical bytes → `master==pinned bytes` | 0 |
| 5 | replica of the counter's `CORRECTION` regex over the draft (`python3 - <<'PY' …`) | `blocks=3 facts=['F4','F5','F6']`, `at_tokens_ok=True`, `sections=['## Gate','## Corrections','## Mistakes']` | 0 |
| 6 | `git show a9b4543f:…/measured/after/c2-gate.out \| tail -5` | `PRE_REPORT round=79 arms=10 failed=1 uncommitted=0`, `EXIT=1`; red arm `round75-instruments exit=1 FAIL … APPEND_ACCEPTED events=58 accepted=53 unaccepted=5 bad_rows=0` | 0 |
| 7 | `git show a9b4543f:…/measured/before/c2-gate-selftest.out \| grep -n "SELFTEST\|ARM_ORDER\|EXIT"` | last lines `PRE_REPORT_SELFTEST pass=22 fail=0`, `EXIT=0` | 0 |
| 8 | `git show {a9b4543f,master}:…/measured/before/c2-gate-arms.out \| wc -lc` and `grep -c PRE_REPORT_SELFTEST` | `3 300` at both revs; `0` selftest lines; `git diff --stat a9b4543f master -- .ufo/waves/round-79/measured/before/` empty | 0 |
| 9 | `git show a9b4543f:SCORECARD.md \| grep -n "\*\*verified\*\*"` / `grep -n "c2-gate.out"` | C2 claim row at line 4587 ends `**verified**`; banner line 6 reads "C2 operability verified"; receipt cited at 4587 and reproduced at 4662 | 0 |
| 10 | `git show a9b4543f:LOG.md \| grep -n "all verified"` | line 3172 "…all verified:"; line 3217 "…all verified on their receipts" | 0 |
| 11 | `grep -c "LOG-CORRECTION" LOG.md`; `git show master:LOG.md \| grep -c "LOG-CORRECTION"` | `0` (exit 1) at the worktree and `0` (exit 1) at the tip blob | 1 |
| 12 | `git cat-file -e master:.ufo/waves/round-80/w1/SC02Sources/curl.txt` (same for `…/SR02ScoutOllama`) | absent from the tip commit (present untracked on disk) | 128 |
| 13 | `python3 tools/round80-selfrecord-round79.py --repo .` | `SELFRECORD_R79 claims=6 mismatches=0 corrected=3 unbacked=0`, `EXIT=0` (observation only; worktree module was modified, `git status` → ` M tools/round80-selfrecord-round79.py`) | 0 |

## Touched surfaces

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-80/w1/SC01Lesson/round-80.md` (new, 68 lines, 9758 bytes, sha256 `6f7f964eaf4fd3863d37147d33c29172124f229c512a60ed2e6e87bceff14856`)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-80/w1/SC01Lesson/gate/ollama-api-tags.out` (37 lines)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-80/w1/SC01Lesson/gate/s553-router-models.out` (29 lines)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-80/w1/SC01Lesson/gate/preset-md.out` (29 lines)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-80/w1/SC01Lesson/c1-counter-observe.out` (12 lines; command, rev, UTC time, counter output, `EXIT=0`)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-80/w1/SC01Lesson.md` (this report)

No other path was written. No git mutation, no `git add`, no commit. Scratch root
`/fast/scratch/hyaku/kama-r80/SC01Lesson` was created, used and deleted after the receipts were copied.

## Out of scope / deliberately not done

- Did not write `corpus/lessons/round-80.md`: the L1 files the draft. The tip commit `dea7c269` already
  carries a `corpus/lessons/round-80.md` (74 lines, 6724 bytes) that contains the identical three blocks
  — see finding 1.
- Did not edit `plans/round-80-claims.md`, `SCORECARD.md`, `LOG.md`, `corpus/QUALITY.md`, `corpus/SOURCES.md`,
  `tools/*`, `registry/*`, or any sibling seat's file.
- Did not run `tools/pre-report-gate.py` (scored or selftest); did not grade any claim.
- No tool installs or upgrades (host pacman paused; nothing needed).

## Findings

1. **Tip moved mid-seat and a lesson is already committed.** `git rev-parse master` returned
   `fe7b978013bd1aa6d67a7e0fbf6369b8d7a9b023` at the first read and `dea7c269446994de1e5e0cd8f34767e83207bd81`
   later; the commit message reads "round-80: the three claim instruments, the pin-relation and
   class-engine registers, and the round lesson with the round-79 corrections". The committed lesson has
   the same three correction blocks (lines 28/30/32), and the C1 counter at that tip prints
   `SELFRECORD_R79 claims=6 mismatches=0 corrected=3 unbacked=0`, `EXIT=0` (receipt
   `c1-counter-observe.out`, worktree module). My draft is therefore an alternative compliant form for
   the L1 to file or merge, not the only landing path.
2. **The committed lesson cites receipts its own commit does not carry.**
   `git cat-file -e dea7c269:.ufo/waves/round-80/w1/SC02Sources/curl.txt` and the same for
   `…/w1/SR02ScoutOllama` both fail (exit 128) while both exist untracked on disk (checked 2026-11-04).
   If the L1 commits them, no defect; if not, the committed record points at receipts no commit holds —
   the class round 79 routed as R79V2. I did not touch either path.
3. **F5 receipt path: plan and counter docstring disagree with the counter's code.** The plan's C1 fact
   table and the counter docstring (line 23) name `measured/before/c2-gate-arms.out` for the `pass=22`
   tally; the counter reads `measured/before/c2-gate-selftest.out` (line 187). The arms file is 3 lines /
   300 bytes at both the sealed revision and the tip and contains only `BASE_ARM_ORDER 9 [...]` — it
   cannot print a selftest tally at all. The value string (`before-selftest=pass=22`) is unaffected
   because the selftest receipt prints `pass=22 fail=0` / `EXIT=0`. The committed tip lesson already
   records this as "Freeze divergences" item 1; my draft states it inside the F5 paragraph.
4. **`LOG-CORRECTION` token absent at the tip.** `git show dea7c269:LOG.md | grep -c "LOG-CORRECTION"` → `0`
   (exit 1), and the worktree `LOG.md` → `0` (exit 1). The counter's F6 observation does not read that
   token (it derives `log=c2-not-verified` from the C2 receipt), so C1's green does not depend on it; the
   plan's F6 narrative and R79V2 still require the appended entry, which only the L1 can land.
5. **The heading's literal bytes carry backticks.** Line 2197 is ``### GET `/models`: List available
   models``; the plan's anchor text writes `### GET /models: List available models`. No claim turns on
   it, but the supersession row quotes the literal form and says so; the committed lesson's S555 row
   prints the unbackticked form.
6. **A second "all verified" sentence exists in LOG §Round 79.** Besides line 3217 ("all verified on
   their receipts", the phrase F6 keys on), line 3172 reads "Three claims, three distinct axes, all
   verified:" — a fourth site of the same class that no correction block answers, because F6's declared
   test matches only the longer phrase.
7. **`preset.md` bytes at `master` equal the pinned `39febd2a` bytes** (sha256 `3e664354…`), so the
   reject row's provenance does not depend on the pin being current.
8. **Draft vs committed lesson, for the L1's reconcile:** my draft has only the three required sections
   plus a header (no "Freeze divergences" / "Frontier position" sections); Gate rows carry a per-row
   `curl` receipt and explicit word counts; Corrections carries one prose paragraph per fact and states
   that the record itself printed the red arm; Mistakes carries one row whose class is
   `verdict-stated-from-intent` (the committed lesson's table carries two rows and the class
   `self-record-states-intent`). Both files carry the identical three blocks, so filing mine keeps
   `corrected=3` and adds no duplicate block (re-verified with the counter's regex: 3 matches).
9. **Counter observation used a modified module.** `git status --porcelain` showed
   ` M tools/round80-selfrecord-round79.py` during my run; receipt 13 names the worktree module, not the
   committed blob. That is an observation of state, not my verification of the C1 claim.

## Known limits

- Access timestamps are the host clock, 2026-11-04T10:42:58Z for the three Gate fetches; "the v0.40.11
  tag exists" is inferred from the HTTP 200 on the tag-scoped raw URL — no `git ls-remote` call was made.
- Quote lengths are whitespace-token counts. The preset quote is a 10-word fragment of a 28-word line
  (marked as such); the other two are complete clauses at 6 and 16 words.
- I did not grade C1, C2 or C3, and did not run the pre-report gate.
- The fetched bodies were kept only in scratch and deleted; each receipt carries the digest needed to
  re-fetch and compare.

## Artifact paths

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-80/w1/SC01Lesson/round-80.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-80/w1/SC01Lesson/gate/ollama-api-tags.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-80/w1/SC01Lesson/gate/s553-router-models.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-80/w1/SC01Lesson/gate/preset-md.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-80/w1/SC01Lesson/c1-counter-observe.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-80/w1/SC01Lesson.md`
