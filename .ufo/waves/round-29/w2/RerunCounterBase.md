# RerunCounterBase — round-29 attempt 2, wave 2 (kama lane)

Seat: `RerunCounterBase` (item: same as `RerunCounter` but `--tip 2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d` in a fresh clone).
Claim served: **C1 (calibration) — counter and receipts.**
Verdict: **PASS — the inherited base receipt reproduces byte-for-byte; no divergence in the receipt line; one cosmetic-only JSON key difference explained by a CLI flag.**

---

## 1. What I ran (exact commands)

Frozen counter (copied out of the fresh clone, sha256 unchanged):

```
fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383  count-c1-frozen.py
```

That hash is the one named in `preregistration.json` → `claims.C1.counter_sha256`, and equals the
blob of `.ufo/waves/round-29/count-c1.py` at the freeze commit:

```
$ git -C /home/vgpnk/Projects/shokunin/kama-shokunin show 827d136:.ufo/waves/round-29/count-c1.py | sha256sum
fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383  -
```

Fresh clones (scratch, under `/tmp/kama-r29-w2-RerunCounterBase/`, nothing outside it touched):

```
git clone --no-local --quiet /home/vgpnk/Projects/shokunin/kama-shokunin clone-local
git clone --no-local --quiet https://github.com/VeigaPunk/kama-shokunin.git clone-remote
```

Both clones carry base `2aa46e2…`, freeze `827d136…`, controls `35b9018…` and data `513eba3…`;
`clone-remote` additionally carries `49f849f…` (see §6).

Run (clean environment, `env -i`, HOME redirected to the scratch dir, so no ambient
`GIT_DIR`/`GIT_WORK_TREE`/`GIT_INDEX_FILE`/`GIT_ALTERNATE_OBJECT_DIRECTORIES`/`GIT_REPLACE_REF_BASE`
can leak in — the counter also strips these itself):

```
env -i PATH=/usr/bin:/bin HOME=/tmp/kama-r29-w2-RerunCounterBase \
  /usr/bin/python3 count-c1-frozen.py \
  --repo /tmp/kama-r29-w2-RerunCounterBase/clone-local \
  --tip 2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d \
  --out /tmp/kama-r29-w2-RerunCounterBase/rerun-base.json
```

Environment: `git version 2.56.0`, `/usr/bin/git` (the absolute path the frozen counter hard-codes).

## 2. Result — receipt line

```
statements 69 mismatched_at_base 11 append_only True valid_corrections 0 false_corrections 0 unresolved 11 met False tip 2aa46e2481d2
exit 0
```

This is **exactly** the line the assignment predicted, and **exactly** the line in the inherited
before-receipt `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/before/c1-base.out`
(sha256 `b008908c65bb561269d1d88d6f4157e5d28e24de264c326ec45c5c82794f1393`).

`diff -u` of the two `.out` files → **no output (identical)**, including the trailing `exit 0` line.

Exit status of the counter: **0** ("ran", whatever the count) — the docstring's exit 2 ("could not
evaluate") was not triggered.

## 3. Diff against the inherited before-receipt — the one divergence, and why it is not a defect

`before/c1-base.json` (sha256 `0cb6605249fb844e1ea085052a50adf84399e6d307c0f2c13b275a49cd55a323`)
vs my rerun JSON:

* **JSON without `--list`**: 3657 bytes; **JSON with `--list`**: 20322 bytes — the *same size as the
  inherited before-receipt*.
* `diff -u before/c1-base.json rerun-base-list.json` → **empty; identical.**
* `diff -u before/c1-base.json rerun-base.json` → the only delta is the presence of the
  `all_statements` key (69 entries) in the inherited receipt.
* Programmatic key comparison: `before only: ['all_statements']`, `rerun only: []`,
  and for every key present in both, **zero differences** — including
  `unresolved_ids` (order-sensitive list) and the full `mismatches` array.

**Conclusion:** the divergence is entirely the presence/absence of the `all_statements` debug key,
which `count-c1.py` emits only under `--list` (source: `if o.list: receipt["all_statements"] = ...`).
The inherited before-receipt was generated with `--list`; my first run was not. The counter's
**verdict-bearing fields are bit-identical**. This is a CLI-flag difference in how the receipt was
produced, not a numerical or logical divergence. Re-running with `--list` closes the gap completely.

Cross-check on the same axis: the lane's *final* tip receipts
(`.ufo/waves/round-29/final/c1-513eba3b-cleanenv.json`, `c1-513eba3b.json`) were produced
**without** `--list` — so the lane's own receipt set is internally inconsistent about the flag
(base receipt has the key, tip receipts do not). Harmless for the claim (the flag only adds
diagnostics), but the L1 may want to normalise it so a future diff of base-vs-tip receipts is
key-symmetric.

## 4. Field-by-field verification of the base receipt

Fields as re-measured in the fresh clone:

| field | value |
|---|---|
| `counter` | `kama round-29 count-c1 v1` |
| `counter_sha256` | `fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383` |
| `base` | `2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d` |
| `tip` | `2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d` (as instructed) |
| `statements` | 69 |
| `by_class` | `C:27, H:2, N:2, P:10, Q:25, T:3` (sums to 69) |
| `mismatched_at_base` | 11 |
| `append_only` | true |
| `correction_rows` | 0 (no `SA29:` rows exist at base — correct: corrections are a tip-side artifact) |
| `valid_corrections` | 0 |
| `false_corrections` | `[]` |
| `unresolved` | 11 |
| `target` | `mismatched_at_base >= 1 and unresolved == 0` |
| `met` | **false** |

The `by_class` census matches `preregistration.json` → `claims.C1.before.by_class` exactly
(`{C:27, H:2, N:2, P:10, Q:25, T:3}`).

The 11 false-at-writing statements, re-derived independently in the fresh clone (all in
`SCORECARD.md`; `SHONEN.md` contributes 0):

| sid | class | line | observed |
|---|---|---|---|
| `SCORECARD.md:Q:f4c42debcc:0` | Q | 20 | `q:no-artifact` |
| `SCORECARD.md:Q:f4c42debcc:2` | Q | 20 | `q:no-artifact` |
| `SCORECARD.md:P:980355388a:0` | P | 192 | `p:absent` |
| `SCORECARD.md:Q:4f8083e30a:0` | Q | 211 | `q:no-artifact` |
| `SCORECARD.md:P:312b3e69b1:0` | P | 740 | `p:absent` |
| `SCORECARD.md:Q:0ccd533544:0` | Q | 823 | `q:no-artifact` |
| `SCORECARD.md:Q:4c5d902830:0` | Q | 824 | `q:no-artifact` |
| `SCORECARD.md:Q:f1021c03db:0` | Q | 833 | `q:no-artifact` |
| `SCORECARD.md:Q:a7e98b1030:0` | Q | 834 | `q:no-artifact` |
| `SCORECARD.md:P:1c6c1f3e4c:0` | P | 1349 | `p:absent` |
| `SCORECARD.md:P:17a7db7c81:0` | P | 1375 | `p:absent` |

The canonical `unresolved_ids` list in the receipt (sorted) is exactly these 11 sids, byte-equal to
the inherited before-receipt's `unresolved_ids`.

Class distribution of the 11: 7 × Q, 4 × P, 0 × H/N/C/T. The C class (27 statements) and T class
(3 statements) are all true at their writing revisions — consistent with the claim narrative that
the round's false statements were pointer/quote errors, not commit/time errors.

## 5. Attack axes exercised beyond the plain rerun

All run in the scratch dir; no lane file, index, or jj state was touched.

1. **Determinism.** Two identical runs of the same command → `diff -q` reports the JSONs identical.
2. **Clone independence.** The same run against `clone-remote` (cloned from
   `https://github.com/VeigaPunk/kama-shokunin.git`) → JSON identical to the local-clone run
   (`REMOTE_SAME_AS_LOCAL`). The receipt does not depend on which clone produced it.
3. **Working-tree contamination.** The counter was pointed at the **dirty lane repo itself**
   (`/home/vgpnk/Projects/shokunin/kama-shokunin`, which carries the attempt-1 uncommitted edits to
   `LOG.md`, `SCORECARD.md`, `SHONEN.md`, `corpus/QUALITY.md`, `corpus/SOURCES.md`,
   `tools/prereg-time-check.py`) → receipt identical to the clean-clone run
   (`DIRTY_LANE_SAME`). Confirms the counter reads committed objects only, so the uncommitted
   attempt-1 leftovers cannot silently move the number.
4. **Replace-ref independence.** A third clone (`clone-replace`) was seeded with
   `git replace 2aa46e2… 513eba3…` and `git replace 827d136… 35b9018…` → receipt identical
   (`REPLACE_REF_INDEPENDENT`). The counter passes `--no-replace-objects` and scrubs
   `GIT_REPLACE_REF_BASE`; a grafted history cannot move the result. This also means the
   `CtlObjectStore` control genuinely fails for the reason the preregistration states.
5. **Clone completeness.** All 25 distinct writing revisions `W` referenced by the 69 statements are
   present as objects in the fresh clone (0 missing) — so the fresh clone is a faithful, complete
   substrate and no `p:absent` result is an artefact of a truncated clone.
6. **Freeze immutability.** `git log --oneline -- .ufo/waves/round-29/count-c1.py` returns only
   `827d136` (the freeze). `before/c1-base.out` and `before/c1-base.json` are also only touched by
   `827d136`; their working-tree blob hashes equal their freeze-commit blob hashes
   (`e6cdec616c8867057af0996f8a78141c70a7de84` / `4361ded43b71722e7b5d101a070cfc284820d2e0`),
   so the inherited before-receipt was not edited after the freeze.
7. **Ancestry.** Base `2aa46e2` is an ancestor of freeze `827d136`, controls `35b9018` and data
   `513eba3`; the three commits are the only ones between base and data. The base is therefore a
   clean pre-round substrate.
8. **Receipt-integrity guard.** The counter refuses to overwrite an existing `--out` file
   (`refusing to overwrite …`, exit 2) — a replay cannot silently clobber a stored receipt.
9. **Prereg command form.** Ran the exact form recorded in
   `preregistration.json` → `claims.C1.command` (counter invoked as
   `.ufo/waves/round-29/count-c1.py` from inside the clone with `--repo <clone>`): identical
   receipt line, exit 0.

## 6. Cross-check against the sibling `RerunCounter` slice (informational, not my verdict)

* At `--tip 513eba3ba51a142c9936553e3a85918345eb5c4c` (the data commit) in a fresh clone, the
  counter gives `statements 69 mismatched_at_base 11 append_only True valid_corrections 11
  false_corrections 0 unresolved 0 met True tip 513eba3ba51a`, and the JSON is **byte-identical**
  (`diff -u` empty) to the lane's stored
  `.ufo/waves/round-29/final/c1-513eba3b-cleanenv.json`. The lane's final receipts are therefore
  reproducible, not just asserted.
* **Note for the L1 (not a claim defect):** the actual pushed `origin/master` tip is now
  `49f849f292c338f5e4e2cc8a60eb1372a8f40412` ("considerthese: 2026-10-23 daily reflection"), which
  is a descendant of `513eba3` and touches only `considerthese/2026-10-23.md`. The stored final
  receipt names `tip 513eba3ba51a` (the commit it was measured at) while the *branch* has advanced
  one unrelated commit past it. Running the frozen counter at the true pushed tip in
  `clone-remote` gives
  `statements 69 mismatched_at_base 11 append_only True valid_corrections 11 false_corrections 0
  unresolved 0 met True tip 49f849f292c3` — the claim still holds at the pushed tip; only the tip
  hash string differs. If the L1 wants the receipt to name the pushed tip exactly, one more run at
  `refs/heads/master` in a fresh clone of the remote closes that wording; no number changes.

## 7. Findings, risks, blockers

**Findings (defects to fix): none in the counter or the base receipt.**

**Cosmetic / hygiene notes for the L1 (no action required for C1):**

* N1 — Receipt key asymmetry: `before/c1-base.json` was produced with `--list` (has
  `all_statements`, 69 entries) while `final/c1-513eba3b*.json` were produced without it. A naive
  `diff` of base-vs-tip receipts reports a large, spurious delta. Normalising both to the same
  flag (or neither) makes future diffs readable. Evidence: §3.
* N2 — The stored final receipts name `tip 513eba3ba51a` while `origin/master` has advanced to
  `49f849f292c3`. The claim is unaffected (re-measured met=True at the pushed tip), but the
  narrative "the fresh-clone receipt at the pushed tip" is literally true only for a tip one commit
  behind the current branch head. Evidence: §6.
* N3 — `preregistration.json` → `claims.C1.command` shows the counter invoked with `--tip
  refs/heads/master`, while the frozen `before` receipt was produced with `--tip` = base. Both are
  correct for their purpose (before = base; final = tip), but the prereg command string alone does
  not document how the base receipt was produced. Not a defect; noting for reproducibility.

**Risks:** none specific to this slice. The counter's numbers are stable across clone source
(local vs GitHub), working-tree dirtiness, replace-ref grafting, run repetition and invocation
form — i.e. the number 69/11/11 is not an artefact of any single substrate.

**Blockers:** none. No tool was installed for this seat (the frozen counter is pure stdlib
Python 3 + `/usr/bin/git` 2.56.0, both already present; no `pacman`, no `uv`, no `npx` — the
operator tooling authorisation was not needed).

## 8. Files written by this seat

* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w2/out/RerunCounterBase/report.md` (this file)
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w2/RerunCounterBase.md` (trailer path; identical content)

Scratch (outside the lane, disposable): `/tmp/kama-r29-w2-RerunCounterBase/`
(`clone-local/`, `clone-remote/`, `clone-replace/`, `count-c1-frozen.py`, `rerun-*.json`).

**No lane file was edited. No `git add`/`commit`/`checkout`/`reset` was run against the lane. No
`.ufo/state/`, `.ufo/watchdog.log`, `MANIFEST.json`, fleet script or template was touched.**
