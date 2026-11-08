EX02RecordForge — C1 record forgeries beyond committed F1–F7

Method: extractor for `controls/c1_forgeries.py` pattern (scratch `git clone --shared
/home/vgpnk/Projects/shokunin/kama-shokunin`, checkout 6776c667, copy SCORECARD.md,
LOG.md and .ufo/waves/round-100/r99-measured.json from the lane working tree (= M bytes
for those files), apply ONE edit, commit with fixture identity, run
`python3 tools/round100-record-audit.py --repo <clone> --rev HEAD`). Harness:
`.ufo/waves/round-100/w1/out/EX02RecordForge/ex02_forgeries.py`; receipts:
`.ufo/waves/round-100/w1/out/EX02RecordForge/ex02_forgeries.out` and `ex02_forgeries.tsv`.

## Forgery results (14 cases)

Counter bytes verified at `tools/round100-record-audit.py`: checks 1–9; `PCT_RE`
line 66 (`\d+(?:\.\d+)?\s?%`), `BOUND_RE` line 63–64, heading logic lines 113–127,
presence checks lines 134–146, resolution lines 155–167.

| id | edit | rc | green? | why counter stays green / catches it |
|----|------|----|--------|--------------------------------------|
| G1 | SCORECARD block: insert "(seven attack seats, in words)" beside "12 seats, 0 dead" | 0 | YES | Check 5 scans only digit `%`; check 6 checks only `seat_s` presence. Words contradiction invisible. |
| G2 | Replace "CR01Records, MT01Mutants." with "CR01Records, DT01Desk (not an attack seat)." | 0 | YES | Counter never reads the seat-name lists; only the fraction strings. |
| G3 | Change bound-phrase `("58% attack")` to `("attack")` | 0 | YES | Check 8 is `phrase in lines[n-1]`: substring passes on same line. The weaker quote is not the claim wording's ("58% attack") quote. |
| G4 | Append a second `## Round 100 correction — round-99 records` heading at EOF in SCORECARD | 1 | caught | Block extraction requires exactly 1 heading: mismatches=5 (checks 1,3,5,6,7/8). |
| G5 | Insert `## Interlude` right after correction heading | 1 | caught | Block terminates at next `## `; empty block fails checks 3/4 (mismatches=2). |
| G6 | LOG: add "(50 %, spaced)" as an extra token beside `6 of 12 (50%)` | 0 | YES | `PCT_RE` matches `50 %`, stripped to `50%`, in allowed set. |
| G7 | LOG: change `6 of 12 (50%)` to `6 of 12 (50.0%)` | 1 | caught | `50.0%` not in allowed `{33%,50%}`; checks 4/5 fail (mismatches=2). DETAIL line printed. |
| G8 | r99-measured.json: add extra key `CX` | 1 | caught | Check 9 requires exact key set; mismatches=1. |
| G9 | LOG: "plus SN01Bounds and CN01Overlap" → "plus SC02Sources and TV01Tables." | 0 | YES | Seat-name list never cross-checked against spec roles. |
| G10 | Add bound pointer `SCORECARD.md@2e27e6f1:6549` ("58% attack") pointing at M itself | 0 | YES | The phrase is on that line at M; check 8 resolves it. A pointer that resolves to the very commit under test is mechanically fine but evidentially empty (self-attestation). |
| G11 | Change bound-phrase `("58% attack")` to `("e")` | 0 | YES (standalone re-run rc=0) | One character: non-empty and present on the line → resolves. Check 8 grades presence, not quotation identity/minimality (only whitespace-only phrases fail, cf. F7). |
| G12 | Append "see tools/round100-record-audit.py:999 (not a lane record)." to SCORECARD block | 0 | YES | `ANY_PTR_RE` only covers `SCORECARD.md`/`LOG.md`/`corpus/lessons/`; a `tools/...` pointer is ungraded (disclosed limit (b)). |
| G13 | Add `the old text said "58% attack" there.` outside any bound pointer | 1 | caught | Check 5 strips only `BOUND_RE` phrases; stray `58%` caught (DETAIL line, mismatches=1). |
| G14 | LOG: insert "(but two seats were dead in prose)" beside "0 dead" | 0 | YES | Check 6 is presence-only; prose contradiction invisible (same class as G1). |

Summary: 14 one-edit forgeries → 9 green, 5 caught. All 5 caught cases (G4, G5, G7,
G8, G13) break a *graded* surface (block extraction, digit-percentage rule, exact
JSON key set). All 9 green cases make the correction false or misleading **while
keeping the counter green**.

## What the green forgeries falsify (Amendment-59 gate)

The claim wording (plans/round-100-claims.md §C1; claims.json "C1.name") says the
correction "agrees with the committed round-99 wave evidence", "states the derived
... attack fractions and 12 seats, 0 dead", and "bind[s] every ... line pointer to a
revision where its quoted phrase sits on that line". The nine checks grade strictly
narrower properties:

1. **Presence-only contradictions (G1, G14, G2, G9)** — the counter grades that the
   derived strings are *present*, never that the block is *consistent* with them.
   "seven attack seats" / "two seats were dead" in words, or naming the wrong seats
   as attack seats, contradict the wording while staying green. *Narrowing sentence:*
   `checks[3] = sc is not None and led_s in sc and pol_s in sc` (line 134) and
   `checks[6] = ... all(seat_s in b for b in blocks)` (line 146) — presence-only.
   (Note: limit (a) discloses the words-contradiction case, but NOT the wrong-seat-
   names cases G2/G9, which are green for the same reason and not disclosed.)
2. **Quotation identity not graded (G3, G11)** — check 8 grades `phrase in line`,
   so a substring ("attack") or a single character ("e") grades the same as the real
   quote. The wording pins *the quoted phrase*; the counter pins *any non-empty
   substring present*. *Narrowing sentence:* `ok = 1 <= n <= len(lines) and
   phrase.strip() != "" and phrase in lines[n - 1]` (line 162) — no equality with
   the intended quotation.
3. **Self-resolving rev (G10)** — check 8 requires `git show <h>:<path>` to contain
   the phrase; a pointer to the commit under test itself satisfies it trivially.
   The wording's purpose ("every line pointer below is bound to the revision it was
   read at") is not graded as *prior* provenance.
4. **Non-lane pointers ungraded (G12)** — disclosed as limit (b); confirmed green.

The pre-file gate (Amendment 59) therefore has 3 narrowing classes above. G6 ("50 %")
is green but harmless: the spaced spelling is the same number, and check 5 strips
the space deliberately — not a falsification of wording, just the same value.

## Non-findings (counter behaving to wording)

- G7 `50.0%` **is** caught (check 5's allowed set is exact `{33%,50%}`). No number
  falsification found in the counter's numeric domain (F1/F5/F6 cover the digit
  surfaces; G13 confirms quoted-unbound percentages are caught).
- G4/G5 block-boundary attacks are caught. G8 extra-key caught.
- The committed F1–F7 are all exit 1 (per `c1-forgeries.out`); the positive P0 is
  green; `measured/c1.out` shows `checks=9 mismatches=0 met=True` at M. No
  `falsifies-number` evidence. `controls/c1-base.out` prints mismatches=9 at base.

## Scratch hygiene

Harness created its own `tempfile.mkdtemp(prefix="ex02-forge-", dir=<scratch>)`
root and deleted it in `finally: shutil.rmtree(root)`; G11 used a second temp dir,
also removed. No files left in `/fast/scratch/hyaku/kama-r100/EX02RecordForge/`
beyond the harness-created dir (removed by harness). One live clone at a time.

## Risks / residual

- G10's line choice (`SCORECARD.md@2e27e6f1:6549`) relied on the prose at M; the
  forgery itself only *adds* a pointer — the added pointer must resolve at the
  scratch commit's rev ancestry, which it does because 2e27e6f1 is in the clone's
  history. If the lane's history is later rewritten, G10's anchor line may move.
- G11's first in-harness attempt failed on an anchor mismatch (anchor string
  `"58% attack"` appears twice in the file, not once); the standalone re-run used
  the exact one-line snippet and printed the full counter output above (rc=0).
  Receipts keep both the harness line and the standalone observation.

VERDICT C1 falsifies-wording narrowing sentence: checks 3/4/6 are presence-only (`led_s in b`, `seat_s in b`, round100-record-audit.py:134,146) — G1 "seven attack seats" and G14 "two seats were dead" in words, G2/G9 wrong seat names, G3/G11 substring/single-char quotes (check 8 `phrase in lines[n-1]`, :162), G10 self-resolving rev, and G12 non-lane pointer (disclosed (b)) all grade green (9 of 14 one-edit forgeries) while contradicting the claim's "agrees with the committed round-99 wave evidence" wording.
VERDICT C2 neutral C2 was not attacked by this seat (depth claim on tools/kama-probe.sh; C1 forgery scope only) — no evidence either way.
