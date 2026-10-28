# WR06ProvinceDraft — PROVINCE / SKILL / README landing text (round 63)

Seat: WR06ProvinceDraft (leaf, no dispatch). Judged on: operability. Milestone: draft landing text.
Tip under test: `03a6a1d850902a66a13dfad33f89cf3a8b759a09` (base, no lane file changed).
Deliverable: `.ufo/waves/round-63/w1/out/WR06ProvinceDraft/province-append.md` (narrative, insertion
anchors, pinned-value consequences, open items, and the exact text as `province-append.patch`).

## Result

- **Missing province token at the tip: one.** `registry/ollama-live-claims-r61.tsv`, cited in the
  evidence cell of the canonical row `live-ollama-lifecycle` (round-63 list). The other 15 of 16 cited
  `tools/`/`registry/` tokens are already in PROVINCE.md.
- **Readme fact passes at the tip** (`readme=0`). No README change is needed; the draft refreshes two
  bullets as optional documentation.
- **Draft verified in a scratch clone** (`fbc3d006eac6485b9a33592246c3bdebcd616cd7`, not landed):
  `province=0`, `readme=0`, but **`r41` rises from 1 to 6 and the total from 8 to 12**. The `r41`
  counter pins SHA-256 values and line counts of SKILL.md and PROVINCE.md, and a `grep -c '^## '` count,
  in the SCORECARD round-41 head table. The draft changes both files, so those pins go stale. The L1 must
  re-derive those head values in the same landing (the freeze already assigns head re-derivation to the L1
  after measurement). Owns row alone: total 9. Full draft: total 12.
- **Base defect (PROVINCE.md round-60 note):** it cites `.ufo/l0-questions.md`. That path is absent at
  the tip (`git cat-file -e` fails) and in the working tree. The draft appends a correction and does not
  rewrite the note.

## Commands run

Lane access was read-only; the lane was never written to.

1. `git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse --show-toplevel` (lane root), `rev-parse HEAD` (`03a6a1d8…`), `cat-file -t 03a6a1d8…` (commit).
2. `python3 tools/round42-selfdesc-reconcile.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip 03a6a1d850902a66a13dfad33f89cf3a8b759a09 --out <out>/reconcile-base.out` → exit 1.
3. `git cat-file -p 03a6…:{PROVINCE.md,README.md,SKILL.md,SCORECARD.md}` and `git ls-tree --name-only 03a6…` (read-only) to read the documents and the top-level entries.
4. `canon_check.py` (scratch helper, copied to `<out>/canon_check.py`) run over the tip SCORECARD's round-63 canonical table and tip PROVINCE.md → `<out>/canon-tokens.out` (base: `in_PROVINCE=False` for the one token above; draft: 16 of 16 True, `canon-tokens-draft.out`).
5. `git cat-file -e 03a6…:<path>` for each cited round-61/62/63 path and for `.ufo/l0-questions.md`; `ls` of the working tree for the same l0 file.
6. Scratch clone: `git clone -q --shared <lane> <scratch>/clone`, toplevel asserted equal to the clone dir before every mutation. Edits made with the edit tool inside the clone only. Committed with `git -C <clone> -c user.name=seat -c user.email=seat@seat.invalid commit`.
7. On the draft tip: reconciler (`--out <out>/reconcile-draft.out`); `tools/round54-cited-path-check.py --repo <clone> --tip <base|draft> --scratch <scratch> --out <out>/cited-path-{base,draft}.json` (diffed); `tools/digest-ledger.py scan --rev <draft>`; `tools/hexrun-census.py scan --rev <draft>`; README top-level-name loop; `git apply --check <out>/province-append.patch` in a second fresh clone at the base tip.

No live server was started and no port was contacted. No tool was installed or upgraded. No pacman transaction was run.

## Findings

**F1 — missing token (the province fact).** Output of the reconciler at the base tip (exit 1):

    tip=03a6a1d850902a66a13dfad33f89cf3a8b759a09
    r41=1 banner=1 planned=2 retired=1 saturation=1 caps=1 receipts=0 readme=0 province=1 rel=0 mismatches=8 maxN=63 met=False
    detail: province: PROVINCE.md lacks registry/ollama-live-claims-r61.tsv (capability live-ollama-lifecycle)

The round-61 claim registry is cited by the round-63 canonical list but is not named in PROVINCE.md at
all. The round-60 note names `registry/ollama-live-pin.tsv` and `tools/kama-ollama-live.py` only.

**F2 — the draft (exact text in the patch; anchors in the landing doc).**
- PROVINCE.md Owns table: one new row after line 17 (lane instruments). It names the round-61 claim
  registry (closes F1), `tools/kama-completion-live.py` (schema v2), `tools/round63-c1-counter.py`,
  `tools/round63-c2-counter.py` and `registry/capability-claims-r63.tsv`.
- PROVINCE.md tail: a Round-61 note (live-ollama-lifecycle is in the round-62 canonical list at
  first-working round 61; it supersedes the round-60 "no capability admitted" sentence without deleting
  it), a correction line for the dangling l0 pointer, and a Round-63 note on the `POST /v1/completions`
  request plane and the round-63 counters. The Round-63 note is outcome-neutral. It states that
  `live-completion-request-plane` enters the canonical list only if the C1 counter reports `met=True`,
  and it records no verdict, since none is known to this seat.
- SKILL.md (new section at the end): the completion tool's options and exit map, a three-row table
  (question / command / exit-output / boundary) for the tool and both counters, the claim-registry
  columns and placeholder meanings, and the freeze pointer. No existing SKILL line is changed.
- README.md (optional): the `registry/` and `tools/` bullets gain the round-61/62/63 claim registries and
  the three live fixtures.

**F3 — the r41 coupling (see §4 of the landing doc).** The pinned values in the SCORECARD round-41 head,
at base and at the draft:

| Pin | Base | Draft |
|---|---|---|
| SKILL.md lines | 1641 | 1655 |
| `grep -c '^## ' SKILL.md` | 44 | 45 |
| PROVINCE.md lines | 188 | 197 |
| SKILL.md / PROVINCE.md sha256 (first 12 hex) | `ea303f2dcb84` / `a60591b77ac8` | `d02efe119d14` / `b65e31fe43dd` |

Five of the six `r41` details come from these pins. The sixth (`coverage run ... no stdout line == '36'`)
fails at base as well.

**F4 — facts checked against the tip sources for the SKILL section.** Hold window: the tool writes
`hold.json` into the hold dir, waits on the shared witness primitive, removes `hold.json` afterwards, and
records `hold.released` only if a release appeared inside the window (`tools/kama-completion-live.py`
≈ lines 478-502, 560). Arguments: `--work`, `--out`, `--hold-dir`, `--hold-timeout`, `--nonce`, `--port`,
`--model`, `--model-sha256` all exist in its argparse. Captures: health, models, props, completion,
tokenize, bad_request, completion2. Exit map 0/1/2 per its docstring. Counter output: one line, exit 0
iff met (both counters' docstrings; C2 prints `met=` on its result line). Registry columns: `cap quote
binding run pattern verdict observed note`; verdict is `true` everywhere except
`context-capacity-receipt` (`host-busy`), as read from `registry/capability-claims-r63.tsv`.

**F5 — allowlist detail (minor, no defect).** `round63-c2-counter.py` sets `ENV_KEYS = (PATH, HOME, LANG,
LC_ALL)` and sets `TMPDIR` to the scratch directory separately (code ≈ line 504-505). The SKILL text says
"`PATH`, `HOME`, `LANG`, `LC_ALL`, and `TMPDIR` set to the scratch directory", which matches the code.

**F6 — pre-existing failures, not caused by this draft (for the L1).**
- Head facts still failing at base: banner (`Latest measured round: 63`), `### Planned (round 64)`,
  Retired (`12 capabilities`), Saturation (`first-working rounds ...`), and the head Capabilities table,
  which has 11 names against the 12-row round-63 canon (`live-ollama-lifecycle` missing). Not drafted here.
- `tools/round54-cited-path-check.py` reports `met=False` at base (`bad=1`, `dropped=1`). The draft tip
  reports the same findings, with `cited` 744 → 749 and no new unresolved entries.
- Dangling `.ufo/l0-questions.md` (F-base above).

**F7 — the measured verdict sentence.** `live-completion-request-plane` is not in the round-63 canon by
freeze. After C1 and C2 are measured, the L1 may add one sentence with the measured verdicts. This seat
does not know those verdicts and wrote none.

## Verification output (tallies)

    base  03a6a1d8: r41=1 banner=1 planned=2 retired=1 saturation=1 caps=1 receipts=0 readme=0 province=1 rel=0 mismatches=8 maxN=63 met=False
    draft fbc3d006: r41=6 banner=1 planned=2 retired=1 saturation=1 caps=1 receipts=0 readme=0 province=0 rel=0 mismatches=12 maxN=63 met=False
    cited-path  base:  fixture=1 lane=0 scenarios=15/15 cited=744 unresolved=14 disclosed=14 undisclosed=0 bad=1 stale=0 dropped=1 met=False
    cited-path  draft: fixture=1 lane=0 scenarios=15/15 cited=749 unresolved=14 disclosed=14 undisclosed=0 bad=1 stale=0 dropped=1 met=False
    digest-ledger scan (draft): tokens=145 blob=126 external_ok=10 external_absent=1 unverifiable=7 wrong_flagged=1 ledger_bad=0 wrong_unflagged=0 unknown=0 (exit 0)
    hexrun-census scan (draft): tokens=2071 distinct=399 lane_oid=277 md5_blob=1 upstream_ok=109 unverifiable=9 wrong_flagged=3 ledger_bad=0 unknown=0 (exit 0)
    README top-level names at draft: 14 ok, 0 missing
    git apply --check province-append.patch at base 03a6a1d8: OK

Tally: `province_missing=1 (registry/ollama-live-claims-r61.tsv); draft province=0 readme=0 r41=6 mismatches=12 (base 8)`

## Receipts (<out>/)

canon_check.py, canon-tokens.out, canon-tokens-draft.out, reconcile-base.out, reconcile-draft.out,
cited-path-base.{out,json}, cited-path-draft.{out,json}, digest-scan-draft.out, hexrun-scan-draft.out,
readme-names.out, draft-tip.txt, province-append.patch, province-append.md.

Reconciler receipts and cited-path JSON contain full SHA-256 values printed by the tools. If the L1 commits
them, run `tools/digest-ledger.py scan` and `tools/hexrun-census.py scan` on the resulting tip. The draft
tip itself scanned clean (`unknown=0`).

## Out of scope / not done

- No lane file, lane index, lane commit or fleet file was changed. The draft is applied only in scratch.
- No measured C1/C2 verdict is stated (the counters were not run by this seat).
- The head re-derivation (SCORECARD banner, Planned, Retired, Saturation, Capabilities, Axes) is the L1's
  job after measurement and was not drafted.
