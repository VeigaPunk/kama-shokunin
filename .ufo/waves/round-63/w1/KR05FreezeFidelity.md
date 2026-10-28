# KR05FreezeFidelity — freeze fidelity audit, kama round 63 (attack item)

Seat: KR05FreezeFidelity (leaf, advisory). Tip under test: `03a6a1d850902a66a13dfad33f89cf3a8b759a09`
(= lane master HEAD). Original freeze commit: `675cac02c966b7db5429d335e6b91158c8dd59cf`. Base: `7ee8cbdf160f8c945954e4737e7a2f797e3b2987`.
Receipts: `.ufo/waves/round-63/w1/out/KR05FreezeFidelity/` (`freeze-fidelity.txt` holds the full diffs and hashes).
No tools installed or upgraded. No commit, edit or git mutation against the lane; the only mutation was in my scratch clone.

## 1. Post-freeze changes on the instrument paths (675cac02 → 03a6a1d8)

`git diff --stat 675cac02 03a6a1d8` touches exactly five files. Of the paths in the item:

| Path | Changed after freeze? | Predicate | Counter | Kill rule | Target | Disclosed |
|---|---|---|---|---|---|---|
| `tools/round63-c1-counter.py` | yes (+46/−10) | docstring predicate sentence rewritten | yes: `is_hit()` with collateral cap, `eval_selftest()`, `MAX_COLLATERAL=5`, `ENVELOPE_CAP=30`, `EXPECT_EVAL_SELFTEST=3`, `met` now also requires `eval_selftest==3` | text unchanged; credit rule redefined (see §4) | unchanged: 44 controls, same named checks, same families | freeze.txt AMENDMENT 1 only |
| `tools/round63-c2-counter.py` | no | no | no | no | no | n/a |
| `tools/kama-completion-live.py` | no | no | no | no | no | n/a |
| `registry/capability-claims-r63.tsv` | no | no | no | no | no | n/a |
| `tools/kama-llamacpp-live.py` (dependency), `tools/round42-selfdesc-reconcile.py`, `registry/`, `SCORECARD.md`, `LOG.md` | no | no | no | no | no | n/a |
| `.ufo/waves/round-63/controls/freeze.txt` | yes (+14/−2 net) | C1 predicate sentence extended: cap of 5 (30 envelope), 3-plant evaluator self-test; `Counter:` line extended; AMENDMENT 1 paragraph added | n/a | kill rule text unchanged | unchanged | self (AMENDMENT 1 paragraph) |
| `controls/c1-base.txt`, `c1-relabel.txt` | yes: header text and a new `eval_selftest=0/3` field only | n/a | n/a | n/a | n/a | receipt header says "amended" |
| `controls/c1-mutants-prewave.txt` | new file | n/a | n/a | n/a | n/a | self |

Working tree: none of the instrument paths is modified or untracked (`git status` lists only PROVINCE.md, corpus/SOURCES.md, corpus/knowledge/completion-request-plane.md, and untracked wave dirs). The C2 counter, the completion tool, the claims TSV, the reconciler, SCORECARD and LOG are byte-identical between the freeze commit and master, so C2 is unamended.

## 2. Freeze file byte identity

| Revision | sha256 of `freeze.txt` | blob |
|---|---|---|
| `675cac02` (original freeze) | `010be3822d6409f8d2c1285afba475d48664d2b10ac8ec5c6fa640e4c1204d5a` | `ebfdb9d9` |
| `03a6a1d8` (tip under test) | `5ceb243d7a51e36deeb22da591b1053999a97dcefe9dc6d0e55fb58da19952e9` | `e32c18bc` |
| working tree | `5ceb243d7a51e36deeb22da591b1053999a97dcefe9dc6d0e55fb58da19952e9` | — (clean) |

- **Byte-identical to the file committed at the tip under test: yes** (working tree = blob at 03a6a1d8, clean).
- **Byte-identical to the original freeze commit: no.** The file was edited by AMENDMENT 1. Anyone citing "the freeze" must cite either the 675cac02 text (`git show 675cac02:.ufo/waves/round-63/controls/freeze.txt`) or the amended 03a6a1d8 text. The file's header still reads "frozen 2026-10-28 before any measured tip data" above the amended text.

## 3. What AMENDMENT 1 claims versus what the bytes show

The paragraph says "the instrument was the only thing that moved" and "Nothing else in C1 or C2 changed."

- **Second half: holds.** Verified in §1.
- **First half: does not hold as written.** The frozen C1 *predicate sentence* in freeze.txt was rewritten (cap and self-test added to the claim text), not only the instrument. The predicate-of-record changed. Disclosure of that is in the same file, so it is not hidden, but the sentence "the instrument was the only thing that moved" is inaccurate.
- **Timing claim "committed before the wave was dispatched": weakly supported.** Commit 03a6a1d8 has author date 19:05:56 and committer date 19:15:45. The dispatch artifacts `w1-spec.json` and `w1-dispatch.json` are mtime 19:16:07, after the committer date. But `w1.ready` (mtime 19:09:31, payload pointing at the dispatch file) predates the amendment's committer date by six minutes. Git timestamps are self-reported, so this is not a clean establishment. It is consistent, not proven.
- **Pre-wave mutant receipt is not reproducible from the lane.** `c1-mutants-prewave.txt` cites L1 scratch commit `785f77096e19e2dc28e9f262e0116fa82de1406c`. `git -C lane cat-file -t` on it fails: it is not in the lane object store. It exists only in `/fast/scratch/hyaku/kama-r63/L1/cl1` (authored 19:15:00). The claim that the pre-amendment counter left "44/44 standing" for the un-resealed mutant has no receipt at all; it is narrated in the amendment only.

## 4. Verdict change at the tip, and what the amendment does to credit

Re-run at the tip, read-only against the lane (`--repo` = lane, `--tip 03a6a1d8`):

- Pre-amendment counter (blob at 675cac02): `tool_present=1 live_ok=1/1 controls_targeted=44/44 errors=0 met=True families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=4/4 trunc=2/2 witness=6/6]` (exit 0)
- Amended counter (blob at 03a6a1d8): `tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True families[…same…]` (exit 0)

So the amendment does not change the verdict at the tip; it is strictly tighter (no control newly credited; any control credited before is credited now only if within cap). Both verdicts are met=True.

Per-control failure-set sizes (instrumented wrapper around `is_hit`, unmodified amended module; `fail-sizes.tsv`):

- 43 non-envelope credited controls: raw failure sets 2–5 entries. Maximum 5 (`model_digest`, one control, sits exactly at the cap).
- `completion_envelope` (cap 30): raw failure set **26** entries. Cap headroom 4.
- The evaluator self-test refuses all three plants: stale nonce (1 entry, named `live_ptok`, not hit), envelope at cap 5 (26 entries, not hit), genuine receipt named against `nonce_match` (0 entries, not hit).

## 5. Calibration findings (attack)

**C-1. The envelope cap is a post-hoc fit with no derivation.** The freeze gives "30 for the envelope break" but no basis. The observed value at the tip is 26, so the cap is 26+4. Nothing in the freeze or amendment says whether 30 was chosen before or after that count was seen. The pre-wave receipt shows no envelope count, so the choice cannot be traced.

**C-2. The envelope exemption makes its collateral rule inoperative.** The envelope control's 26 entries comprise 13 distinct checks plus 13 `inconsistent:<name>` mirror entries. Any failure set up to 30 entries passes, so the control proves only that `completion_envelope` is among the failures. The amendment's stated rationale ("a mutation that breaks the whole receipt … proves nothing about the named one") is the very case the 30 bound admits. The self-test that refuses the envelope plant does so only at cap 5, which is a tautology of the chosen number. No plant exercises the upper bound of 30. I did not construct a whole-capture plant to test that bound; this is untested.

**C-3. The cap unit counts mirror entries.** `inconsistent:<name>` is added alongside the plain name (e.g. `model_digest` control: `inconsistent:model_digest, inconsistent:server_digest, live_server_sha, model_digest, server_digest` = 3 distinct, 5 raw). The freeze says "5 failing checks"; the counter counts set entries. The rule is therefore tighter than "5 distinct checks" for every control, and `model_digest` is at the raw boundary, so one more collateral entry would refuse a true-named control. Operability risk (false refusal), not a credit loophole. The freeze should state the unit.

**C-4. Mutant m2 reproduction (un-resealed capture; the amendment's motivating mutant).** Scratch clone commit `3d7f5a755b14ae42b9676d79b9c8850702a49685` (one line removed in `edit_body`, `reseal(c)` replaced by `pass`; diff in `m2-mutant.diff`). Unmutated tool, mutated counter, run from the clone path:
`tool_present=1 live_ok=1/1 controls_targeted=31/44 eval_selftest=3/3 errors=0 met=False families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=0/3 listener=1/1 log=1/1 outside=0/1 predead=1/1 ptok=1/2 reqbind=2/2 schema=1/1 shape=0/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=0/4 trunc=2/2 witness=6/6]`
**KILLED** (met=False, 31/44, reproduces `c1-mutants-prewave.txt` m2 exactly). The envelope control is credited under m2 with the same 26-entry set as the honest tip (`tamper=8/8`), so the m2 kill comes from other families, not from the envelope control. This is the C-2 consequence made concrete: the envelope credit is insensitive to the reseal defect.

**C-5. Hollowed-evaluator mutant m1 not re-run** (it is `met=False` by construction via `eval_selftest` and was not reproduced here).

## 6. Disclosure status of each change

| Change | freeze.txt | SCORECARD round-63 | LOG.md | corpus/lessons/round-63.md |
|---|---|---|---|---|
| Predicate sentence + cap + self-test (AMENDMENT 1) | yes | **no** (section mentions only the freeze path, "Claim rows … once measured") | **no** (no round-63 entry at tip) | file absent at tip |
| Counter `is_hit`, cap, eval_selftest | yes (in AMENDMENT 1 and Counter line) | no | no | no |
| c1-base / c1-relabel header and selftest field | receipt header | n/a | no | no |
| Pre-wave mutants | file only | no | no | no |

Not disclosed at the tip anywhere except the freeze file. SCORECARD, LOG and the lesson are the L1's close-out surfaces; they must carry AMENDMENT 1, the envelope cap value and its unit before close, or the scorecard will misstate the C1 kill rule.

## 7. Re-verification of receipts

- `controls/c1-base.txt`: re-ran the amended counter at base 7ee8cbdf. Stdout identical to the receipt line (`tool_present=1 live_ok=0/1 controls_targeted=0/0 eval_selftest=0/3 errors=1 met=False families[]`, exit 1). Stderr lines identical to the receipt's `error:` line.
- `controls/c1-relabel.txt`: not re-run (needs a constructed v1 clone; low value against C-1 to C-4).
- `controls/c1-mutants-prewave.txt` m1/m2 and the unmutated line: m2 reproduced (C-4); m1 not; the unmutated line reproduced as the tip verdict above (44/44 met=True).

## 8. Tally

Freeze fidelity: 0 post-freeze changes on C2 or the completion tool; 2 post-freeze changes on C1 (counter; freeze.txt predicate text) — both disclosed only in freeze.txt; freeze file identical to tip under test, not to original freeze commit; 0 tip-verdict changes from the amendment; 1 m2 mutant KILLED; 1 envelope-cap calibration defect (C-2) and 1 unit ambiguity (C-3) reported.

Final counter output (amended, tip 03a6a1d8):
`tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=4/4 trunc=2/2 witness=6/6]` (exit 0)
