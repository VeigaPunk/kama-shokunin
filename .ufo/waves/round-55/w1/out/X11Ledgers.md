# X11Ledgers — round 55 ledger-regression at 9c60eae6f7ed84f7da93d219a406aadc30958c6c

**Verdict: the lane's own three frozen ledger/append-only counters are RED at the round-55 landed tip (all three `lane=0 met=False`, exit 1), and the hexrun census is RED (`unknown=1`, exit 1) — four standing red gates that round 55 did not repair; two one-line, evidence-backed repairs that I verified in a scratch clone turn three of the four green, while the fourth (round-50 v5) stays red for reasons set out in §5 (one round-55-specific, one pre-existing).**

Seat: X11Ledgers (leaf executor, `godspeed`). Lane tip measured: `9c60eae6f7ed84f7da93d219a406aadc30958c6c` (round-55 w0 freeze). Base: `3a600d2f729828419aaea34cc402c8b0d20fb720` (round-54 tip). All work read-only against the lane; the only mutations are in my own scratch clone.

---

## 1. Scope and method

The seat asked for six command families. **The literal `--selftest` flag in the seat text does not exist for any of the six tools** — every one of them uses a subcommand or a different flag spelling. I ran the form each tool actually implements and recorded both, so the exit codes below are the tools' real exits, not argparse errors.

| seat text | what the tool implements | evidence |
|---|---|---|
| `python3 tools/digest-ledger.py --selftest` | `python3 tools/digest-ledger.py selftest` (`--selftest` → argparse exit 2, "the following arguments are required: cmd") | `tools/digest-ledger.py:385` |
| `python3 tools/hexrun-census.py --selftest` | `python3 tools/hexrun-census.py selftest` (`--selftest` → exit 2) | `tools/hexrun-census.py:623` |
| `python3 tools/pin-watch.py selftest` | as written (correct) | `tools/pin-watch.py:240` |
| `python3 tools/round50-append-audit-v5-check.py --selftest` | no selftest exists; the counter is `--repo/--tip` | `tools/round50-append-audit-v5-check.py:500` |
| `python3 tools/round51-append-audit-v6-check.py --selftest` | same | `tools/round51-append-audit-v6-check.py:384` |
| `python3 tools/round52-append-restore-check.py --selftest` | same | `tools/round52-append-restore-check.py:500` |

`digest-ledger.py scan --repo .` **is** supported read-only (`tools/digest-ledger.py:388-392`); it uses `git rev-parse` / `git cat-file --batch` only and refuses a promisor clone rather than writing into it (`tools/digest-ledger.py:238-241`). I ran it against both my shared clone and the real lane tree, read-only, and both give identical output.

Clone: `git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane`, `S=/fast/scratch/hyaku/kama-r55/w1/X11Ledgers`; `git -C "$S/lane" rev-parse --show-toplevel` printed `$S/lane` before every commit. No lane file, index, jj state or `~/.local/bin` was touched; no `pacman` was run; no tool was installed.

---

## 2. Results — every exit and summary line

### 2.1 Selftests — all green (exit 0)

```
$ python3 tools/digest-ledger.py selftest
selftest pass=11 fail=0                      exit 0
$ python3 tools/hexrun-census.py selftest
selftest pass=18 fail=0                      exit 0
$ python3 tools/pin-watch.py selftest
PASS numeric-order / current / build-numbers / missing-pin / unreadable
PASS bad-header refused / option-repo refused / traversal-engine refused / quantified-group refused
selftest pass=9 fail=0                       exit 0
```
Receipts: `digest-ledger.selftest.out`, `hexrun-census.selftest.out`, `pin-watch.selftest.out` in my out dir.

### 2.2 `digest-ledger.py scan` — green (exit 0), unchanged by round 55

```
$ python3 tools/digest-ledger.py scan --repo <clone> --rev 9c60eae6f7ed84f7da93d219a406aadc30958c6c
tokens=137 blob=122 external_ok=8 external_absent=1 unverifiable=5 wrong_flagged=1 ledger_bad=0 wrong_unflagged=0 unknown=0   exit 0
$ ... --rev 3a600d2f729828419aaea34cc402c8b0d20fb720   (base)
tokens=137 blob=122 external_ok=8 external_absent=1 unverifiable=5 wrong_flagged=1 ledger_bad=0 wrong_unflagged=0 unknown=0   exit 0
$ python3 tools/digest-ledger.py scan --repo /home/vgpnk/Projects/shokunin/kama-shokunin --rev 9c60eae6...   (real lane tree, read-only)
tokens=137 blob=122 external_ok=8 external_absent=1 unverifiable=5 wrong_flagged=1 ledger_bad=0 wrong_unflagged=0 unknown=0   exit 0
```
Identical at base and tip: the round-55 freeze added no new 64-hex digest obligation. **No regression here.**

### 2.3 `hexrun-census.py scan` — RED (exit 1, `unknown=1`)

```
$ python3 tools/hexrun-census.py scan --repo <clone> --rev 9c60eae6f7ed84f7da93d219a406aadc30958c6c
tokens=1962 distinct=350 lane_oid=238 md5_blob=1 upstream_ok=98 unverifiable=9 wrong_flagged=3 ledger_bad=0 unknown=1   exit 1
detail: e2e2d10fe4801d7a846e22e5f84cc1a8e133c4e0 len=40 occurrences=1 class=unknown
```
Same red on the real lane tree and at HEAD `8abadfed`. The regression is **not** round 55's: the unknown is introduced at the round-54 base `3a600d2f` and is absent at the round-53 tip:

| rev | unknown | exit |
|---|---|---|
| `8551ba7f` (round-52 freeze) | 1 (`39877b17…`, since repaired) | 1 |
| `0b75a84c` (round-53 tip) | **0** | **0** |
| `3a600d2f` (round-54 tip = round-55 base) | 1 (`e2e2d10f…`) | 1 |
| `9c60eae6` (round-55 tip) | 1 (`e2e2d10f…`) | 1 |
| `8abadfed` (lane HEAD) | 1 (`e2e2d10f…`) | 1 |

KQ55 (`corpus/QUALITY.md:363`) binds the landed tip to `exit 0` with `unknown=0 ledger_bad=0`. The round-55 tip is red on that criterion and round 55 did not notice.

### 2.4 The three append-only counters — all RED (exit 1, `lane=0 met=False`)

```
$ python3 tools/round50-append-audit-v5-check.py --repo <clone> --tip 9c60eae6... --scratch $S
fixture=1 lane=0 scenarios=12/12 met=False                                    exit 1
$ python3 tools/round51-append-audit-v6-check.py --repo <clone> --tip 9c60eae6... --scratch $S
fixture=1 lane=0 scenarios=9/9 lost=10 disclosed=10 met=False                  exit 1
$ python3 tools/round52-append-restore-check.py --repo <clone> --tip 9c60eae6... --scratch $S
fixture=1 lane=0 scenarios=8/8 corr_lost=1 row_lost=10 disclosed=10 met=False  exit 1
```
All three are red at the base `3a600d2f` too (identical summary lines). **Every fixture scenario passes** in all three (`scenarios=12/12`, `9/9`, `8/8`); only the *lane* leg fails. The lane legs agree on one cause:

```
detail: lane: tool definition v6 threshold 1 exit 1 {'unrestored': 1, 'partial': 0, 'regressed': 0, 'bad_disclosures': 0, 'bad_declarations': 0}
detail: lane: unheld lines in A-corr files: {'SCORECARD.md': 1}
```

### 2.5 `pin-watch.py check` — exit 1 (one pin behind), not a defect

```
$ python3 tools/pin-watch.py check --pins registry/engine-pins.tsv
engine=sglang pin=v0.5.22 newest=v0.5.22 newer=0 status=current
engine=vllm pin=v0.32.0 newest=v0.32.0 newer=0 status=current
engine=llama.cpp pin=b11755 newest=b11933 newer=149 status=behind
pins=3 current=2 behind=1 missing=0 error=0                                exit 1
```
Exit 1 is the tool's documented "behind ⇒ recheck trigger" code (`tools/pin-watch.py:154-155`), not an error. Note `registry/engine-pins.tsv:4` still pins llama.cpp at `b11755` while the corpus rows S488/S494/S505/S509 pin `b11909`; that pin file is a recheck trigger the lane has not refreshed. **Not a round-55 regression and not in my write scope** — reported as an observation only.

(With `--tags-dir .ufo/tags`, which does not exist, all three pins read `status=error`, exit 2 — the tool's documented missing-tag-list path. Receipt `pin-watch.check.tagsdir-missing.out`.)

### 2.6 Source census — green (exit 0)

```
$ bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama
kama	W01	S481 tierC mined used-by=…
(no E11)                                                                            exit 0
```
The round-55 freeze's S510 `used-by` re-point did land: the `E11 S510 missing used-by corpus/lessons/round-54.md` error recorded at `.ufo/waves/round-55/census/start.out` is gone. Receipt `sources-census.validate.out`.

---

## 3. Defect 1 (primary) — the round-52 authority banner was dropped in place and never restored

**File and line:** `SCORECARD.md:6` (the live banner line) and `SCORECARD.md:2736-2764` (§"Superseded head banners (kept verbatim; round 48)").

**What happened.** The round-53 integration `e81d90e6` ("round-53: integrate code identity, curation, falsification and report evidence", 2026-10-27T03:30:21-03:00) rewrote the authority banner at `SCORECARD.md:6` from "round 52" to "round 53" **without appending the superseded round-52 banner** to the §Superseded head banners section. Every prior round did append it — the section holds the round-45, 46, 47, 42, 43, 44, 48, 49, 50 and 51 banners at `SCORECARD.md:2740,2742,2744,2748,2750,2752,2756,2760,2762,2764` — but the round-52 banner is absent from the whole file:

```
$ git show 9c60eae6:SCORECARD.md | grep -c "Current authority (round 52)"
0
$ git show 35e3b1dc:SCORECARD.md | grep -c "Current authority (round 52)"   # round-52 integration
1
$ git show 0b75a84c:SCORECARD.md | grep -c "Current authority (round 52)"   # round-53 tip
0
```

The lane itself documents this rule at `SCORECARD.md:2738` (round-48 C1 build finding): *"rounds 46 and 47 rewrote the banner in place without keeping the superseded text … from round 48 on, each round appends the banner it replaces here."* Round 53 broke it; rounds 54 and 55 inherited it silently.

**The command that shows it:**

```
$ python3 tools/append-only-audit.py --repo <clone> --to 9c60eae6f7ed84f7da93d219a406aadc30958c6c
event e81d90e64b04 SCORECARD.md deleted=3 graded=1 ungraded=2 permitted=0 restored_max=0 held_at_to=0 disclosed=0 status=unrestored
summary commits=368 files=104 events=114 restored=68 partial=0 unrestored=1 ungraded=40 disclosed=5 permitted_lines=59 disclosed_lines=10 bad_disclosures=0 ungraded_lines=218 regressed=0 …
```
`status=unrestored` on the one graded line (the banner) is exactly what makes the v6 audit exit 1, and it propagates into `round51-append-audit-v6-check.py` (`lane=0`) and `round52-append-restore-check.py` (`lane=0`, `corr_lost=1`).

**Bisect** (each commit measured with the frozen `round52-append-restore-check.py`):

| commit | lane leg | exit |
|---|---|---|
| `35e3b1dc` (round-52 integration) | `lane=1 corr_lost=0 met=True` | 0 |
| `c22602bd` (round-53 build) | `lane=1 corr_lost=0 met=True` | 0 |
| **`e81d90e6` (round-53 integration)** | **`lane=0 corr_lost=1 met=False`** | **1** |
| `93333d98`, `2f88b357`, `0b75a84c`, `3a600d2f`, `9c60eae6` | `lane=0 corr_lost=1 met=False` | 1 |

The break is exactly at `e81d90e6`. Round 53's own committed measurement receipt `.ufo/waves/round-53/measured/r52c2-build.out` was taken at the **build** commit `c22602bd` (`met=True`), so the integration regression was never re-measured — and no round-53/54/55 receipt re-runs it at a tip.

**Proposed fix** (`proposed-fix-banner-restore.diff`, verified):

```diff
--- a/SCORECARD.md
+++ b/SCORECARD.md
@@ -2761,6 +2761,7 @@
 **Current authority (round 50):** …
 
+**Current authority (round 52):** the assigned axes are operability + calibration (`shokunin.conf` kama row; `MISSION.md:29` still says operability + freshness, an open L0 question since round 35). …
 **Current authority (round 51):** …
```
(the added line is `git show 35e3b1dc:SCORECARD.md | sed -n 6p`, byte-exact).

**Verification** — after committing that one line in my scratch clone (fixture identity `fx <fx@invalid>`), on tip `d1f06d26`:

```
round52-append-restore-check.py   exit=0  fixture=1 lane=1 scenarios=8/8 corr_lost=0 row_lost=10 disclosed=10 met=True
round51-append-audit-v6-check.py   exit=0  fixture=1 lane=1 scenarios=9/9 lost=10 disclosed=10 met=True
```

**Risk / scope.** This restores a line the lane already deleted; it does not rewrite any score, claim or evidence pointer. The banner text is byte-exact from the round-52 integration, so no new bytes are asserted. It is a lane-file edit and therefore **outside my write scope** — the diff is a proposal for the lane's owner.

---

## 4. Defect 2 — the round-54 fleet report commit is cited with no hexrun ledger row

**File and line:** `corpus/lessons/round-54-verifier-spotcheck.md:6` cites the fleet commit `e2e2d10fe4801d7a846e22e5f84cc1a8e133c4e0`; `registry/hexrun-ledger.tsv` has **no row** for it (114 rows, last is the round-52 report commit at line 114).

```
$ git show 9c60eae6:registry/hexrun-ledger.tsv | grep -c e2e2d10f
0
```

**The command that shows it:**

```
$ python3 tools/hexrun-census.py scan --repo <clone> --rev 9c60eae6f7ed84f7da93d219a406aadc30958c6c
tokens=1962 distinct=350 lane_oid=238 md5_blob=1 upstream_ok=98 unverifiable=9 wrong_flagged=3 ledger_bad=0 unknown=1   exit 1
detail: e2e2d10fe4801d7a846e22e5f84cc1a8e133c4e0 len=40 occurrences=1 class=unknown
```
`hexrun-census.py` classifies a token absent from the ledger and absent from the lane object store as `unknown` and exits 1 (`tools/hexrun-census.py:258-266, 396-404`). The token is a real fleet commit (`git -C /home/vgpnk/Projects/shokunin cat-file -t e2e2d10f…` → `commit`; `round-54: kama honest-stop report + ed135b3c L0 forward`), it is on fleet `main`, and it is absent from the lane — the identical situation the lane already ledgered for the round-49, 50, 51 and 52 report commits at `registry/hexrun-ledger.tsv:110,111,112,114`, each with an evidence file under `.ufo/waves/round-NN/hexrun-evidence/`.

**This is a step-change in lane behaviour**: round 54's spot-check was written by the *outside closure* (`3a600d2f`, author `protocol-shokunin`), so the round-54 lane had no integration commit that could add the row; round 55 inherited the red and did not repair it, while round 53 had done exactly this for `39877b17…` (row added at `e81d90e6`).

**Proposed fix** (`proposed-fix-hexrun-ledger-row.diff`, verified): add `.ufo/waves/round-55/hexrun-evidence/e2e2d10f….txt` (same evidence shape as the round-53 file) and one ledger row.

**Verification** — after committing both in my clone, tip `a7c8341f`:
```
hexrun-census.py scan   exit=0  tokens=1962 distinct=350 lane_oid=238 md5_blob=1 upstream_ok=99 unverifiable=9 wrong_flagged=3 ledger_bad=0 unknown=0
```
`unknown` 1 → 0, `upstream_ok` 98 → 99, exit 1 → 0. The round-51 and round-52 counters stay green at that tip (`lane=1 met=True`).

---

## 5. Defect 3 (reported, not fixed here) — `round50-append-audit-v5-check.py` stays red after both fixes

With both fixes applied the round-50 v5 counter is still `lane=0 met=False` exit 1. Its lane leg has two independent causes, only one of which round 55 owns:

1. **Round-55's own new event** — the S510 `used-by` in-place cell edit in the freeze commit:
```
detail: lane: event 9c60eae6f7ed corpus/SOURCES.md graded 0 + ungraded 0 != deleted 1
```
This appears **only at the round-55 tip** — it is the single line that differs between the base and tip receipts of that counter (base `events 113`, tip `events 114`). The v5 checker requires `graded + ungraded == deleted` for every event (`tools/round50-append-audit-v5-check.py:468-471`), but the lane's contract row for `corpus/SOURCES.md` is `A-row` with note *"only status, recheck and used-by change in place (KQ22)"* (`registry/append-only-contract.tsv:6`), and the v6 audit classifies exactly this event as `permitted=1`:
```
event 9c60eae6f7ed corpus/SOURCES.md deleted=1 graded=0 ungraded=0 permitted=1 … status=ungraded
```
So the v5 counter and the v6 tool disagree about the same, contract-permitted edit. **The v5 counter is frozen and is a superseded generation (the lane moved to v6 in round 51); this is a finding, not something to fix in place.** Note it is *not* a real append-only violation — v6 says `permitted=1`, and the round-51/52 (v6) counters do not flag it.

2. **Pre-existing and unrelated to round 55** — the counter was already red at the round-52 build `5dacf2c7` and at the base, over 100+ historical events (`corpus/SOURCES.md` mass edits, `corpus/knowledge/consumer-registry.md` ungraded regions). It is not a round-55 regression.

**Recommendation:** the round-55 freeze's S510 `used-by` re-point is legitimate under KQ22 and under the v6 tool; the lane should either re-point the `corpus/SOURCES.md` contract note so v5 and v6 agree, or record that the v5 counter is retired. Neither is in my scope.

---

## 6. What round 55 did not check

The round-55 lesson (`corpus/lessons/round-55.md`) closes on "census exit 0" and on the two round-54 counters. It records nothing about:

- `hexrun-census.py` at the landed tip (red, `unknown=1`), despite KQ55 binding it to exit 0;
- `round51-append-audit-v6-check.py` / `round52-append-restore-check.py` / `round50-append-audit-v5-check.py` at the landed tip (all three red, `lane=0`), despite round 53 having measured them green at its own build commit and the round-53 integration having broken them;
- the dropped round-52 banner, which is the single graded line behind all three reds.

The round-55 lesson's own "Mistakes" section names the *class* of defect ("vacuous — a kill rule the counter's own controls never exercise") but the lane's standing counter reds were not re-measured at the round-55 tip, which is how the round-53 integration regression survived three rounds.

---

## 7. Risks and blockers

- **My fixes are fixture commits in a scratch clone**, not lane edits. The lane is read-only for this seat, so the two diffs in my out dir are proposals; the lane owner must apply and re-measure them at a tip.
- **`round50-append-audit-v5-check.py` remains red** after both fixes, for the two reasons in §5. Only the second (pre-existing) is out of round-55's reach; the first is a v5-vs-v6 vocabulary disagreement about a KQ22-permitted edit and needs an owner decision.
- **`pin-watch` reports llama.cpp 149 tags behind** (`b11755` pinned vs `b11933` newest) — a recheck trigger, not a defect, and outside my scope.
- No `llama-server` was started by this seat; `pgrep -af llama-server` returns nothing (exit 1). No tool was installed, so there is no tool/version/channel record to report.

---

## 8. Artifacts written

All under `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/X11Ledgers/`:

```
digest-ledger.selftest.out              digest-ledger.scan.tip.out        digest-ledger.scan.base.out
digest-ledger.scan.lanetree.out         hexrun-census.selftest.out        hexrun-census.scan.tip.out
hexrun-census.scan.base.out             hexrun-census.scan.r52.out        hexrun-census.scan.r52.details.out
hexrun-census.scan.r53.out              hexrun-census.scan.head.out       hexrun-census.scan.lanetree.out
hexrun-census.scan.fixboth.out          round50-append-audit-v5-check.{tip,base,fixbanner,fixboth}.out
round51-append-audit-v6-check.{tip,base,fixbanner,fixboth}.out
round52-append-restore-check.{tip,base,fixbanner,fixboth}.out
pin-watch.selftest.out                  pin-watch.check.network.out       pin-watch.check.tagsdir-missing.out
sources-census.validate.out             exit-codes.txt
proposed-fix-banner-restore.diff        proposed-fix-hexrun-ledger-row.diff
```

Scratch `/fast/scratch/hyaku/kama-r55/w1/X11Ledgers` removed at the end of the seat.
