# R57Item43CounterRepair — item 43 (executor)

Axes: calibration + operability (lane `shokunin.conf` / SCORECARD; `MISSION.md:29` conflict not resolved).
Scope: prototype only, in `/fast/scratch/hyaku/kama-r57/R57Item43CounterRepair/`; no source-tree, SCORECARD, tool, fleet or sibling write. No installs or upgrades performed (`curl` fetch only, no package transaction).

## Result in one line

The frozen claim's "expected 46" is **falsified**: 46 is the hard-coded literal printed by the frozen no-op control (`controls/c1-noop.py`) and the historical round-46 measured value, not a tree-derived count. The counter's `maxN` is already derived and correct (56 at the frozen tip `b89bdab2`, 57 at live tips after a `## Round 57` heading landed mid-wave). The real repairable defect is that `maxN` had **no declared-vs-derived binding and no read witness**, so a literal summary line was indistinguishable from an executed run. A minimal prototype repair adds exactly that binding while leaving canonical heading selection byte-identical.

## Base receipt (frozen counter, unmodified)

```
python3 round42-selfdesc-reconcile.py --repo <lane> --tip b89bdab2cc114735ec5d331c6c610134258f7864 --out base.out
tip=b89bdab2cc114735ec5d331c6c610134258f7864
r41=1 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=1 maxN=56 met=False
detail: r41 calibration run `python3 -c "import glob;print(len(glob.glob('corpus/lessons/*verifier-spotcheck.md')))"` no stdout line == '42' (exit 0)
base_exit=1
```
Byte-identical to the frozen `controls/base-c1.out` (diff empty). The sole mismatch is the r41 head-table calibration expectation `42`; the executed command prints `43` at that tip. `maxN` itself is not implicated.

Live drift observed during the wave (same command, `--tip HEAD`): `7b74e2f2` → `mismatches=0 maxN=56 met=True` exit 0; `16efcf5e` → `mismatches=0 maxN=57 met=True` exit 0. A `## Round 57` heading entered SCORECARD while this seat ran, so any literal `maxN` (46, 56 or 57) is stale by construction within one edit.

## Prototype repair (minimal, semantics-preserving)

`measured/R57Item43/round42-selfdesc-reconcile.repaired.py`, sha256 `31d160fe60f289599163f420d4b368ead97c41e6598109f7d3fe79daf27da9ae`; frozen base `9736923ec3086c6e56512cd67fa7c00a22cbb8ac63022bef45a676f2200f9ef0`. Full diff at `measured/R57Item43/repair.diff` (97 lines):

- `derive_maxn(text)` lifts the existing expression verbatim (`^## Round (\d+)`, `max`) and additionally returns the number of headings read (the read witness).
- `evaluate()` calls it in place of the inline expression — same value, one call site.
- `--expect-maxn N` / `--claim FILE` add a `bind:` line only when used; the default report line and exit class are unchanged (proved below).

**Default output is unchanged.** `build-default.out` (repaired, frozen tip) diffs empty against `base.out`, exit 1; on the stale-46 fixture `stale46-repaired.out` diffs empty against `stale46-frozen.out`, exit 1.

## Build / no-op receipts (exact)

| Receipt | Invocation | Output tail | Exit |
|---|---|---|---|
| `bind-56.out` | `--expect-maxn 56` @ `b89bdab2` | `bind: ... declared_maxn=56 derived_maxn=56 headings=57 reported_maxn=56 witness=None maxn_match=1 witnessed=1 executed=1 met=True`; counter `mismatches=1 maxN=56 met=False` | 1 |
| `bind-46.out` | `--expect-maxn 46` @ `b89bdab2` | `bind: ... declared_maxn=46 derived_maxn=56 ... maxn_match=0 ... met=False` | 1 |
| `claim-noop.out` | `--claim claims/noop-frozen.txt` @ `b89bdab2` | `bind: source=claims/noop-frozen.txt declared_maxn=46 derived_maxn=56 headings=57 reported_maxn=56 witness=0 maxn_match=0 witnessed=0 executed=1 met=False` | 1 |
| `claim-noop-c2.out` | `--claim claims/noop-c2-frozen.txt` @ `b89bdab2` | same shape, `witness=0`, `met=False` | 1 |
| `bind-57.out` | `--expect-maxn 57` @ `16efcf5e` | `bind: ... maxn_match=1 witnessed=1 executed=1 met=True`; counter `mismatches=0 maxN=57 met=True` | 0 |
| `claim-witness-57.out` | `--claim claims/match-witness-57.txt` @ `16efcf5e` | `bind: ... declared_maxn=57 derived_maxn=57 headings=58 witness=58 ... met=True` | 0 |
| `claim-nowitness-57.out` | `--claim claims/match-no-witness-57.txt` @ `16efcf5e` | `bind: ... maxn_match=1 witnessed=0 ... met=False` | 1 |
| `noop-frozen.out` | `python3 <lane>/.ufo/waves/round-57/controls/c1-noop.py` | `mismatches=0 maxN=46 met=True` (inputs read: none, as the script states) | 0 |

So: the frozen no-op still escapes when its stdout is taken at face value (exit 0, same summary grammar as a real run); the repaired checker refuses it on two independent grounds (declared 46 ≠ derived 56; `witness=0`), and refuses a matching declaration that carries no read witness. A matching declaration with a witness is accepted and then still must clear the counter's own facts.

## Canonical heading semantics preserved (measured)

`semantics-check.py` imports both modules unmodified, replicates the frozen inline expression literally, and compares heading list length, `maxN`, `canon()` round and row names over five texts (`semantics.out`, exit 0):

```
tip:b89bdab2: frozen_maxN=56 repaired_maxN=56 headings=57 frozen_canon_round=49 repaired_canon_round=49 canon_rows=11 same_names=1 same=True
tip:77e7f5ee: frozen_maxN=57 repaired_maxN=57 headings=58 frozen_canon_round=49 repaired_canon_round=49 canon_rows=11 same_names=1 same=True
fixture:canonical-noop: frozen_maxN=56 repaired_maxN=56 headings=57 frozen_canon_round=49 repaired_canon_round=49 canon_rows=11 same_names=1 same=True
fixture:no-canonical: frozen_maxN=56 repaired_maxN=56 headings=57 frozen_canon_round=48 repaired_canon_round=48 canon_rows=11 same_names=1 same=True
mutation:stale46: frozen_maxN=46 repaired_maxN=46 headings=48 frozen_canon_round=49 repaired_canon_round=49 canon_rows=11 same_names=1 same=True
semantics: cases=5 divergent=0 met=True
```

Selection rule is untouched: highest-numbered `**Capabilities — canonical list as of round N**` (49 where present, 48 in the sibling `no-canonical` fixture), 11 rows in every case.

## Where 46 comes from, and why it cannot be the expectation

- The frozen no-op prints `maxN=46` as a constant (script comment: no registry/self-description/canonical-table inspection).
- 46 is the historical value: SCORECARD's own round-46 regression text records `round-42 self-description counter mismatches=0 maxN=46 met=True`; the chain continues `maxN=47` (round 47), `maxN=50` (round 50). It was correct then, not now.
- Constructed stale-46 fixture (`fixtures/stale46`, commit `fd956dd1`, 9 headings ≥47 renamed, 48 headings left, max 46): frozen counter prints `banner=1 planned=1 ... mismatches=3 maxN=46 met=False` exit 1 — the counter itself flags a head that declares 56 while the headings stop at 46 (`detail: banner: head lacks 'Latest measured round: 46'`). The repaired copy is identical; `--expect-maxn 46` binds True *for that tree* (`stale46-bind46.out`), which is the correct tree-relative behaviour, not a licence to expect 46 on the live tree.

## Non-author source spot-check (advice only; this seat is a lane author)

S515 (Git config runtime environment pairs) re-opened this round at
`https://git-scm.com/docs/git-config#Documentation/git-config.txt-GITCONFIGCOUNT` (curl exit 0, 830,605 bytes; snapshot `measured/R57Item43/sources/git-config-live.html`, sha256 `706b1566467e9cd8c6cdda853a5fc82118a48fde3119777d18cefc014bcd3d5a`; page footer `last updated in 2.56.0`).
Located quote, §GIT_CONFIG_COUNT, **18 words**:

> all environment pairs GIT_CONFIG_KEY_<n> and GIT_CONFIG_VALUE_<n> up to that number will be added to the process's runtime configuration

Matches the registry quote verbatim (live page uses a typographic apostrophe in "process's"). **Advice: the S515 mined/admit decision stands** — the quote is present, located, ≤25 words and revision-anchored.

S513 reject decision (the round-56 outside defect), re-opened at `https://man7.org/linux/man-pages/man8/ld.so.8.html` (snapshot `measured/R57Item43/sources/ld.so.8.html`, sha256 `d9b7737e6c9a38f6c7ce11a4feec834704d6ad5139dc790afa9798faf0379f83`). The live page documents `LD_AUDIT` both in §Dynamic string tokens and in §Secure-execution mode, i.e. the topics named by the row's flip are present. **Advice: the reject is scoped, not a redundancy claim** ("overlaps … for the claim's only need"), and its flip is consistent with those sections; the round-56 outside disagreement appears to read the reject as a global redundancy verdict. Recommend the round-57 lesson record that the S513 reject is retained with its per-claim scope, and correct the round-56 outside finding rather than the row. This seat does not resolve it.

## Round-56 outside defects — how this item touches them

- *Strengthen C2-style gates; a literal roster/no-op harness must fail* → addressed for the `maxN` surface: declaration must equal a tree-derived value and carry a read witness (`claim-noop*.out`, `claim-nowitness-57.out`).
- *SCORECARD/SHONEN disagreement* → **not addressed** here (out of item scope; SHONEN.md was not read into a control).
- *MISSION axis-authority conflict* → **not resolved**; reported only.
- *Inherited append-only audit exit 1 / invalid `declared_at`-SCORECARD bindings* → **not addressed** by this item; routes onward.
- Claim-label ordering: `controls/freeze.txt` and the seat prompt label C1 = calibration (stale count), `controls/freeze-amendment.txt` labels C1 = operability (prereg no-op) and C2 = calibration. Observed, not resolved; my evidence is label-independent (it measures both the count and the no-op binding).

## Risks / limits

- Claim-file mode trusts a declared read witness; it proves the *claimant* asserted a read, not that it executed. Only the counter's own run supplies an executed witness (`executed=reported==derived`), and a full fix should bind to the claimant's process/file evidence.
- The prototype is evidence, not a landed change: `tools/round42-selfdesc-reconcile.py` in the tree is untouched and still lacks the binding.
- `maxN` still counts any `## Round N` heading in the file, including out-of-order retained history (`## Round 30 — self-assessment corrections (recall population)` after round 51). Today that cannot inflate the maximum; a future heading written with a higher N for a non-current section would. Detecting that needs a canonical-round declaration, which is a separate predicate.
- Fixture construction wrote only inside scratch; `git rev-parse --show-toplevel` asserted the fixture dir before `git init`/commit.

## Artifacts (all under `.ufo/waves/round-57/measured/R57Item43/`)

`base.out`, `build-default.out`, `bind-56.out`, `bind-46.out`, `bind-57.out`, `claim-noop.out`, `claim-noop-c2.out`, `claim-witness-57.out`, `claim-nowitness-57.out`, `head.out`, `noop-frozen.out`, `stale46-frozen.out`, `stale46-repaired.out`, `stale46-bind46.out`, `semantics.out`, `repair.diff`, `runs.tsv`, `fixture.txt`, `sha256sums.txt`, `round42-selfdesc-reconcile.repaired.py`, `semantics-check.py`, `claims/*.txt`, `sources/{git-config-live.html,ld.so.8.html,sha256sums.txt}`.
Separate case-64 evidence: `.ufo/waves/round-57/reports/R57Item43CounterRepair-case64.md`.

Report: .ufo/waves/round-57/w1/out/R57Item43CounterRepair.md
