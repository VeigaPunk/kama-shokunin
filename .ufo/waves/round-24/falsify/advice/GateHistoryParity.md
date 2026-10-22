# GateHistoryParity — frozen r23 auditor vs pinned current auditor, real fleet

**Lane:** `GateHistoryParity` (KamaR23-2.GateHistoryParity) · **Role:** reviewer
**Base:** `0df800e896f6bce285a81e794ad4ae1d1e6c3a71` · **Pinned current:** `2e254a1763a9c08aa07fc53081287f506c447d84`
**Verdict: HOLD — byte-identical parity.** In every arm the frozen r23 auditor and the pinned
current auditor return the same exit code and the same stdout and stderr bytes, on the **real**
fleet and lane repositories, for rounds 10–23, with and without `--no-errata`. The round-24
rewrite of `tools/report-landing-audit.py` changes no verdict on the real fleet.

No production file was edited. The only writes are this report and
`.ufo/waves/round-24/falsify/out/GateHistoryParity/` (evidence copies).

---

## 1. The two auditors under comparison

Both are the *same file path* at two revisions; nothing was patched or reconstructed by hand.

| | frozen r23 | pinned current |
|---|---|---|
| commit | `0df800e896f6bce285a81e794ad4ae1d1e6c3a71` | `2e254a1763a9c08aa07fc53081287f506c447d84` |
| path | `tools/report-landing-audit.py` | `tools/report-landing-audit.py` |
| git blob id | `cf706c52233139920da60f8b55d06f031286c4f9` | `91518a9d661c1f97670fc588e724ce5f97c972ac` |
| sha256 | `da5041a8191e0e6ec385adc7c659ddc7544a835aff65dd45b34de623c5765af1` | `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220` |

The current blob's sha256 `ea51bc35…` matches the "source tool ea51bc35…" identifier named in
the wave context, confirming the pinned-current blob is the one under falsification.

Extraction (scratch only):

```
git -C /home/vgpnk/Projects/shokunin/kama-shokunin \
    show 0df800e896f6bce285a81e794ad4ae1d1e6c3a71:tools/report-landing-audit.py \
    > /fast/scratch/hyaku/kama-r24/falsify/GateHistoryParity/r23-audit.py
git -C /home/vgpnk/Projects/shokunin/kama-shokunin \
    show 2e254a1763a9c08aa07fc53081287f506c447d84:tools/report-landing-audit.py \
    > /fast/scratch/hyaku/kama-r24/falsify/GateHistoryParity/current-audit.py
```

`0df800e` is an ancestor of `2e254a1` (`git merge-base --is-ancestor` → exit 0), so the frozen
blob is a genuine ancestor of the pinned current blob, not a fork.

**Scratch:** `git clone --no-hardlinks /home/vgpnk/Projects/shokunin/kama-shokunin
/fast/scratch/hyaku/kama-r24/falsify/GateHistoryParity`, then `git checkout --detach
0df800e896f6bce285a81e794ad4ae1d1e6c3a71` (verified `git rev-parse HEAD` = `0df800e…`). The clone
is scratch only; production `kama-shokunin/.jj`, the fleet repo and every sibling were never
written. `TMPDIR` was set to `/fast/scratch/hyaku/kama-r24/falsify/GateHistoryParity/tmp` for
every subprocess.

---

## 2. Repository under audit (the real fleet)

Both auditors were pointed at the **production** repositories, read-only:

```
--lane-repo  /home/vgpnk/Projects/shokunin/kama-shokunin   (HEAD 2e254a1763a9c08aa07fc53081287f506c447d84)
--fleet-repo /home/vgpnk/Projects/shokunin                 (HEAD 13cd91dfebc51836732bea29b89ee2a51489d8cc
                                                            at the final run; 061fe170… at the first)
--branch master
```

Preconditions checked before measuring (all read-only):

| check | command | result |
|---|---|---|
| no promisor remote in the fleet | `git -C /home/vgpnk/Projects/shokunin config --get-regexp 'promisor\|partialclone\|extensions'` | rc=1, no match |
| no promisor remote in the lane | same in `kama-shokunin` | rc=1, no match |
| no promisor pack markers | `find …/.git/objects/pack -name '*.promisor'` | none |
| not shallow | no `.git/shallow` | absent |
| no grafts | no `.git/info/grafts` | absent |
| no alternates | `objects/info/` has only `commit-graphs/` and `packs` | none |
| fleet reports exist | `git -C fleet cat-file -e HEAD:.ufo/reports/round-N/kama.md` for N=10..23 | 14/14 present |
| errata ledger identical at both lane tips | `git rev-parse 0df800e…:registry/report-landing-errata.tsv` vs `2e254a1…` | both `90d84c9d94a781e425c06c96f78467483b63be98` |

That last row matters: the `--no-errata` vs default-errata contrast is a **pure ledger toggle**,
the ledger content is byte-identical at the base and the current lane tip, so the two arms differ
only by the `apply_errata` step.

The fleet repo is a live repository (its HEAD moved from `061fe170…` to `13cd91df…` between my
first and last runs, from unrelated fleet activity). The parity conclusion is therefore asserted
only for runs whose **before/after HEAD snapshot matched**, which the final run does
(`fleet HEAD before=13cd91df… after=13cd91df…`, `lane HEAD before=2e254a1… after=2e254a1…`).
The reported verdict uses that final run.

---

## 3. The measurement, and its exact commands

The command shape (both auditors, both arms):

```
python3 <auditor> --lane-repo /home/vgpnk/Projects/shokunin/kama-shokunin \
                   --fleet-repo /home/vgpnk/Projects/shokunin \
                   --branch master --rounds 10-23 [--no-errata]
```

Comparison is on the triple **(returncode, stdout, stderr)**, byte-identically, via `cmp`
(exit 0 = identical) plus `sha256sum` of each stream.

### Arm 1 — default errata (ledger applied)

```
r23 : rc=0   stdout=1338 B  stderr=0 B   sha256(stdout)=e81d809b569660afaf7c31d986c6056dfa05f873a58373bfeb208960ea240a59
cur : rc=0   stdout=1338 B  stderr=0 B   sha256(stdout)=e81d809b569660afaf7c31d986c6056dfa05f873a58373bfeb208960ea240a59
cmp r23_errata.stdout cur_errata.stdout  → exit 0 (identical)
cmp r23_errata.stderr cur_errata.stderr  → exit 0 (identical)
```

### Arm 2 — `--no-errata`

```
r23 : rc=1   stdout=1357 B  stderr=0 B   sha256(stdout)=bccce1de2812a5a683bcd263583262630906472aca618ff31bbe4022a5f6081e
cur : rc=1   stdout=1357 B  stderr=0 B   sha256(stdout)=bccce1de2812a5a683bcd263583262630906472aca618ff31bbe4022a5f6081e
cmp r23_noerrata.stdout cur_noerrata.stdout  → exit 0 (identical)
cmp r23_noerrata.stderr cur_noerrata.stderr  → exit 0 (identical)
```

stderr sha256 in all four runs is `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
— the sha256 of the empty string. **No stderr output at all in any arm**: the refusal channel
(`could-not-evaluate: …`) that the round-24 work is about never fires on the real fleet.

### Verdict content (identical in both auditors, both arms)

`--rounds 10-23` selects 14 fleet reports. The full audit result:

```
round=10 required=2 post_report=0 defects=1     corrected   landed-omitted 40660352d4a9eb00a5d6195f0f064f5c64618143
round=11 required=2 post_report=0 defects=0
round=12 required=2 post_report=0 defects=0
round=13 required=2 post_report=0 defects=0
round=14 required=2 post_report=0 defects=0
round=15 required=3 post_report=0 defects=0
round=16 required=3 post_report=0 defects=0
round=17 required=2 post_report=0 defects=0
round=18 required=7 post_report=0 defects=3     corrected   landed-omitted 101f3991d…, 1c325b2e…, c6dc46fa…
round=19 required=8 post_report=4 defects=0
round=20 required=9 post_report=0 defects=5     corrected   unresolved-full-hash 0957ce619789d13d894ef21bc863486bcb35b56c
                                                                landed-omitted 846e366d…, 92b14625…, 0957ce619789d13bb5779606078fa1498114d2c7, 33a6777866d0f63d894ef21bc8632863b35b56c
round=21 required=7 post_report=1 defects=0
round=22 required=5 post_report=0 defects=0
round=23 required=5 post_report=0 defects=0
summary reports=14 defects=9 corrected=9 uncorrected=0 errata_unmatched=0 errata_invalid=0 status=clean
```

With `--no-errata` the same 9 defects appear with the marker flipped to `UNCORRECTED` and the
summary becomes `corrected=0 uncorrected=9 … status=failed` (exit 1). The two arms are the
ledger toggle and nothing else.

**This is a meaningful, non-degenerate comparison.** The `unresolved-full-hash` defect at round 20
(`0957ce619789d13d894ef21bc863486bcb35b56c`) is a token that *no* repository holds — verified
independently: `git cat-file --batch-check` answers `missing` in **both** the lane and the fleet,
and `git rev-list --objects --all --no-object-names | grep -c '^0957ce61…'` is `0` in both. So
the real fleet genuinely contains an absent citation, and the round-24 "absent is a proved
absence" rule is exercised for real, on the real fleet — and it yields exactly the r23 verdict.

---

## 4. The parity is not a trivial bypass — the new code paths really ran

Byte-identical output could also mean "the new code never executed". It did execute. I instrumented
a **scratch copy** of the pinned-current blob (`out/GateHistoryParity/trace_current.py`, which
imports the blob and wraps `missing_reachable`, `unknown_citation`, `opaque_hole`,
`refuse_unknown`, `required_read`, `root_tree` with counters) — production source untouched:

```
TRACE calls={"missing_reachable": 2, "opaque_hole": 1, "refuse_unknown": 28,
             "refuse_unknown_raise": 0, "required_read": 0, "root_tree": 0,
             "unknown_citation": 1}
TRACE missing_reachable repo=/home/vgpnk/Projects/shokunin/kama-shokunin missing=0 opaque=0
TRACE missing_reachable repo=/home/vgpnk/Projects/shokunin missing=0 opaque=0
TRACE unknown_citation token=0957ce619789d13d894ef21bc863486bcb35b56c -> None
TRACE opaque_hole -> (None, None)
TRACE refuse_unknown rnd=20 states={'found': 6, 'absent': 1}
```

Reading of the trace:

* `refuse_unknown` was entered **28 times** (14 rounds × 2 lookup sites) and **raised 0 times** —
  the new refusal channel was on the hot path for every round and every citation set, and it
  correctly declined to refuse.
* The two `missing_reachable` walks (the new `rev-list --objects --missing=print` diagnosis over
  the lane store and the fleet store) both ran and both returned `missing=0 opaque=0`: the real
  repositories reference nothing they cannot serve. This is the positive confirmation that the
  real fleet is *not* a promisor repository in substance, not only in configuration.
* `unknown_citation` was called once — for exactly the round-20 absent token — and returned
  `None`; `opaque_hole` was called once and returned `(None, None)`. Both then left the token as a
  **proved absence**, which is the round-24 contract's "no blanket metadata/unknown/full-closure
  refusal; actual required-unavailable ⇒ CNE2" behaving as specified on a repository where
  nothing is actually unavailable.
* `required_read` and `root_tree` count 0: no required read failed, so no
  `unavailable required object` reason was ever constructed.

The trace's own stdout is byte-identical to the uninstrumented run (`cmp` exit 0), so the
instrumentation did not perturb the audit.

---

## 5. Robustness arms (each one bounded, each a frozen-vs-current comparison)

| # | arm | what it varies | result |
|---|---|---|---|
| A | `--json` form, both errata arms | machine-readable output instead of `render()` | rc and stdout/stderr **byte-identical** (`r23_errata.json` vs `cur_errata.json`, `r23_noerrata.json` vs `cur_noerrata.json`) |
| B | base-era lane clone (`refs/heads/master` forced to `0df800e`) | the lane tip the auditor reads | both arms byte-identical, rc 0 / rc 1 |
| C | symlink path spelling (`--lane-repo …/lane-link --fleet-repo …/fleet-link`) | path normalization (`Path(...).resolve()`) | byte-identical, and identical to the real-path run |
| D | `--no-hardlinks` clone of the lane at the pinned `2e254a1` | clone vs. live repo as the lane source | byte-identical, and identical to the real-path run |
| E | `--rounds 10-` (tool's own open-ended form) | round-selection spelling | byte-identical, rc 0 / rc 1, same 14 reports |
| F | no-transport run: `GIT_ALLOW_PROTOCOL=none` + `HTTP(S)_PROXY=ALL_PROXY=http://127.0.0.1:1` | proves no transport is attempted | rc 0, stdout and stderr identical to the network-capable run |
| G | repeat run (determinism) | same command twice | byte-identical |
| H | read-only proof | `find` snapshot of both `.git` trees (all files: path/size/mtime) and of both `.ufo` worktrees, before and after a full run | **gitdir snapshot unchanged**, **worktree snapshot unchanged**, fleet and lane HEAD unchanged |

Arm F is the direct answer to "no promisor remote configured in realrepos" ⇒ nothing to fetch:
even with every protocol denied and every proxy black-holed, the audit completes with identical
bytes. The `--no-lazy-fetch` isolation in `GIT_ISOLATION` covers it.

Arm H is the direct answer to the read-only requirement: the auditor writes nothing into either
repository — not the object store, not the refs, not the worktree, not the `.jj` directory
(the lane's `.jj` has no `index` file to begin with; nothing created one).

---

## 6. What the source delta actually changes, and why the real fleet is unaffected

The pinned-current blob differs from the frozen r23 blob by 438 insertions / 73 deletions
(`git diff --stat`). The behavioural deltas are:

1. **`check_history_repo` no longer refuses a partial clone.** r23 refused on
   `extensions.partialclone`, on `remote.*.promisor`, and on a `.promisor` pack marker.
   The current blob refuses none of those; it keeps the shallow / grafted / non-sha1 /
   non-top-level refusals.
2. **`lookup` gained three states** (`unknown`, `wrongtype`, `absent`) in place of r23's binary
   `found` / `ambiguous` / `missing`, with a `RANK` ordering and a second `cat-file` pass for
   tokens that resolve bare but not under a peel.
3. **A new refusal channel** (`refuse_unknown`, `unknown_citation`, `opaque_hole`,
   `missing_reachable`): an absent citation is refused (exit 2) when the store references it but
   cannot serve it, or when a missing tree/commit could hide it.
4. **Error reasons became content-derived** (`required_read`, `root_tree`): a failed required read
   is reported as `unavailable required object: <what>: <exc>` instead of a generic message.

Every one of these deltas is **conditional on the repository actually having unavailable
objects**, and the real fleet has none (§2 and §4: `missing=0 opaque=0` in both stores, no
promisor config, no promisor packs). Hence identical verdicts.

The r23-era behaviour on a *promisor-marked* repository (blanket exit 2 with
`partial clone (remote.origin.promisor)`) is exactly the harm the round-24 change targets; the
real fleet never enters that branch, so this parity measurement neither confirms nor refutes
that repair — it confirms only that the repair is **no-harm** on the real fleet, which is the
claim it is capable of supporting.

---

## 7. Findings, by severity

**No finding.** This lane found no defect, no verdict drift and no behavioural difference
between the frozen r23 auditor and the pinned current auditor on the real fleet, rounds 10–23,
in either errata arm.

Specifically **not** found (each checked explicitly, each a negative result worth recording):

* **F1 — no verdict drift.** Exit code, stdout and stderr agree byte-for-byte in both arms.
* **F2 — no spurious refusal.** `refuse_unknown` ran 28 times and raised 0 times; stderr is
  empty in all four runs. The round-24 "unknown ⇒ exit 2" channel never misfires on a repository
  whose objects are all locally available.
* **F3 — no false absence.** The one genuinely absent citation (round 20,
  `0957ce619789d13d894ef21bc863486bcb35b56c`, independently confirmed absent from both repos and
  referenced by neither) is still reported as `unresolved-full-hash` — i.e. the new
  `absent`-vs-`unknown` distinction did **not** swallow a real defect into a refusal.
* **F4 — no changed defect kind.** `landed-unresolved` / `landed-ambiguous` / `landed-omitted` /
  `landed-section-missing` / `unresolved-full-hash` sets are identical; the `wrongtype` state
  added by the current blob produces no new finding here because no landed citation in rounds
  10–23 resolves to a non-commit object.
* **F5 — no transport, no lazy fetch, no mutation.** Proven by arms F and H.
* **F6 — no path-spelling sensitivity.** `--lane-repo`/`--fleet-repo` spelling (real path,
  symlink, `--no-hardlinks` clone) does not change a single byte; the tool's
  `Path(...).resolve()` normalises it, as the contract requires. **Raw mismatch: none — there
  was no mismatch to hide.**
* **F7 — no error-message drift on the happy path.** The new `required_read` /
  `unavailable required object` reasons are constructed 0 times on the real fleet, so no stderr
  text changed.

---

## 8. Residual risk and verification gaps

1. **This lane proves *no-harm*, not *repair*.** The real fleet has no promisor metadata and no
   unavailable objects, so the round-24 machinery is inert here. The promisor-marked cases
   (`CaseCompleteLane`, `CaseCompleteFleet`, `CaseMarkerLane`, `CaseHydratedLane`, …) are the
   rows that actually exercise deltas 1–4; this lane makes no claim about them.
2. **The fleet repo is live.** Its HEAD moved during the wave. The verdict is asserted for the
   final run, whose before/after HEAD snapshot matched; earlier runs at a different fleet HEAD
   produced the same bytes, but that is not a guarantee for arbitrary future fleet states.
3. **Rounds 10–23 only.** Rounds outside that window (e.g. round 1–9, and the tool's open-ended
   `--rounds 10-` form, which resolved to the same 14 reports) were not compared. The open-ended
   form was checked and selects exactly the same 14 reports.
4. **Lane-history variants other than the base tip were not enumerated** — only the two tips
   (base `0df800e`, current `2e254a1`) and the spelling variants.
5. **The instrumented trace is a scratch copy of the blob, not the blob.** The wrappers change
   the module's function table; the wrapper bodies are pure counters plus writes to stderr. The
   trace's stdout was verified byte-identical to the uninstrumented run, and the stderr written
   by the wrappers is unambiguously separated by the `TRACE ` prefix.
6. **Git floor.** git 2.56.0 is installed on this host, above the inherited `>= 2.45`
   prerequisite; the floor itself remains open at L0 (`CritGitFloor`), and no part of this
   measurement depends on it — the real fleet audit never reaches the version gate.

---

## 9. Files written

| path | content |
|---|---|
| `.ufo/waves/round-24/falsify/advice/GateHistoryParity.md` | this report |
| `.ufo/waves/round-24/falsify/out/GateHistoryParity/parity-summary.json` | machine-readable parity record (blob ids, sha256s, arms, trace counters, read-only/no-transport flags) |
| `.ufo/waves/round-24/falsify/out/GateHistoryParity/r23-audit.py` | frozen r23 blob (`sha256 da5041a8…`) |
| `.ufo/waves/round-24/falsify/out/GateHistoryParity/current-audit.py` | pinned current blob (`sha256 ea51bc35…`) |
| `.ufo/waves/round-24/falsify/out/GateHistoryParity/trace_current.py` | scratch instrumentation wrapper (counters only) |
| `.ufo/waves/round-24/falsify/out/GateHistoryParity/{r23,cur}_{errata,noerrata}.{stdout,stderr,rc}` | the four primary arm captures |
| `…/fin_{r23,cur}_{errata,noerrata}.{stdout,stderr,rc}` | the final run, with matched before/after HEAD snapshot |
| `…/{r23,cur}_{errata,noerrata}.json` | `--json` form captures (arm A) |
| `…/base_{r23,cur}_{errata,noerrata}.{stdout,stderr,rc}` | base-era lane clone (arm B) |
| `…/link_{r23,cur}.{stdout,stderr,rc}` | symlink path spelling (arm C) |
| `…/cl_{r23,cur}_{errata,noerrata}.{stdout,stderr,rc}` | `--no-hardlinks` lane clone (arm D) |
| `…/all_{r23,cur}_{errata,noerrata}.{stdout,stderr,rc}` | `--rounds 10-` form (arm E) |
| `…/trace_{errata,noerrata}.stderr` | the code-path trace (arm: instrumentation) |

Scratch (not part of the deliverable, disposable):
`/fast/scratch/hyaku/kama-r24/falsify/GateHistoryParity/` — the `--no-hardlinks` clone, the two
extracted blobs, the instrumentation wrapper, `tmp/` (TMPDIR) and `out/` (the working copies of
the evidence above).

## 10. Tooling

No tool was installed, updated or removed by this lane; no pacman transaction was performed; no
system upgrade, service change or config mutation occurred. The only tool versions relied upon
were the pre-existing `git 2.56.0` and the system `python3`. Everything else was `cmp`,
`sha256sum`, `find`, `stat` and `git` plumbing already present.

## 11. Exact commands, exit codes and findings

```
# extraction (scratch)
git show 0df800e…:tools/report-landing-audit.py > …/r23-audit.py          ; exit 0
git show 2e254a1…:tools/report-landing-audit.py > …/current-audit.py       ; exit 0
git merge-base --is-ancestor 0df800e… 2e254a1…                            ; exit 0 (ancestor)

# the four primary runs (each: exit code in the table)
python3 …/r23-audit.py     --lane-repo …/kama-shokunin --fleet-repo … --branch master --rounds 10-23            ; exit 0
python3 …/current-audit.py --lane-repo …/kama-shokunin --fleet-repo … --branch master --rounds 10-23            ; exit 0
python3 …/r23-audit.py     --lane-repo …/kama-shokunin --fleet-repo … --branch master --rounds 10-23 --no-errata ; exit 1
python3 …/current-audit.py --lane-repo …/kama-shokunin --fleet-repo … --branch master --rounds 10-23 --no-errata ; exit 1

# comparisons
cmp r23_errata.stdout   cur_errata.stdout    ; exit 0
cmp r23_errata.stderr   cur_errata.stderr    ; exit 0
cmp r23_noerrata.stdout cur_noerrata.stdout  ; exit 0
cmp r23_noerrata.stderr cur_noerrata.stderr  ; exit 0
cmp r23_errata.json     cur_errata.json      ; exit 0
cmp r23_noerrata.json   cur_noerrata.json    ; exit 0
sha256sum *.stdout *.stderr                    ; exit 0

# findings
git config --get-regexp 'promisor|partialclone|extensions'   ; exit 1 (no match, both repos)
git cat-file --batch-check <<< 0957ce61…                      ; "missing" in both repos
git rev-list --objects --all --no-object-names | grep -c '^0957ce61…' ; 0 in both repos
git rev-parse 0df800e…:registry/report-landing-errata.tsv 2e254a1…:registry/report-landing-errata.tsv ; both 90d84c9d…
```

Finding tokens: `40660352d4a9eb00a5d6195f0f064f5c64618143`,
`101f3991d3570bc9350fbf9c5561f4be1185699d`,
`1c325b2e58fcfdc6761f645b44cedfb1d65243e6`,
`c6dc46fabc51eb1dd0e91647f2e5e6b2b8ae4d6d`,
`846e366dc9dbac58463494a7e05ad060ae3ed3b0`,
`92b146253fd3a8c4bfade94c909dc63b13d6f4a8`,
`0957ce619789d13bb5779606078fa1498114d2c7`,
`33a6777866d0f63d894ef21bc8632863b35b56c`,
`0957ce619789d13d894ef21bc863486bcb35b56c` — nine defects, identical in both auditors, both arms.

Report: .ufo/waves/round-24/falsify/advice/GateHistoryParity.md
