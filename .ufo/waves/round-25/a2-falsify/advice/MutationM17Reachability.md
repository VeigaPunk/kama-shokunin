# MutationM17Reachability — advice, kama round 25, attempt 2, wave 2 (falsify)

**Verdict: the inference holds — no killing input exists.** Under git 2.56.0 the
`lookup()` refusal that mutant `M17-ref-shadow` weakens is unreachable from every audit
input; 14 hand-built inputs and the whole registered grid population were measured and
none changes the verdict. The same element is live at the other call site
(`bare_objects()`, mutant `M33-ref-shadow-bare-objects`), which grid row F13 kills.
`M17` is a structural survivor, not a coverage gap in the grid.

---

## 1. Target

`tools/report-landing-audit.py` at lane tip `fa3b62ae6475d111eb466d79af616aeebb08bbb9`:

- `lookup()` at line 219; the weakened element at lines 275-277:
  `if not peel and not parts[0].startswith(token):` →
  `raise EvalError(f"{store.path}: citation {token} names a ref")`.
- The non-peel caller is line 538 `full = lookup(stores, full_tokens)`; the two peel
  callers are line 550 (`"^{commit}"`, landed citations) and line 630 (`"^{commit}"`,
  errata corrections).
- `full_tokens` comes from `classify_full_hashes()` → `FULL` (line 90),
  `(?<![0-9A-Za-z])[0-9a-f]{40}(?![0-9A-Za-z])` — 40 lower-case hex only.
- The same element exists at `bare_objects()` lines 212-214; that site is mutant
  `M33-ref-shadow-bare-objects`.

Clone used: `git clone --no-hardlinks /home/vgpnk/Projects/shokunin/kama-shokunin
/fast/scratch/hyaku/kama-r25a2w2/MutationM17Reachability/clone`, checked out at
`fa3b62ae6475d111eb466d79af616aeebb08bbb9`; clone worktree clean (`git status
--porcelain` empty).

Auditor bytes, before and after all experiments (identical):

```
b9be4f428cd70842320c698794faffaa95571a60fc530df6a84d7d8cade3b26f  tools/report-landing-audit.py
```

The same digest is the lane tip blob:
`git -C <lane> show fa3b62ae...:tools/report-landing-audit.py | sha256sum` →
`b9be4f42…3b26f`. After all experiments the lane working copy is still
`sha256 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/report-landing-audit.py` →
`b9be4f428cd70842320c698794faffaa95571a60fc530df6a84d7d8cade3b26f`, i.e. byte-identical
to the tip blob: restoration verified. The lane working tree was never written to by
this seat (no production file touched, no git write command run).

## 2. Method

Three auditors were derived from the pristine committed bytes (all in
`/fast/scratch/hyaku/kama-r25a2w2/MutationM17Reachability/work/`, digests in
`sha256sums.txt`):

| name | change | sha256 (short) |
|---|---|---|
| `report-landing-audit-pristine.py` | none | `b9be4f42…` |
| `report-landing-audit-mutant.py` | the registered `M17` literal replaced by `pass` (literal taken from `tests/report-audit/isolation-mutants.py`, `MUTANTS` entry `M17-ref-shadow`) | `44099ab9…` |
| `report-landing-audit-probe2.py` | the same site instrumented to log every entry `(token, oid, peel, store)` to `$M17_PROBE_LOG` | `4e2c55f7…` |

The probe makes "the site was never reached" / "the site was reached but never
refused" a measured fact instead of an argument. The kill condition is a change of
verdict between pristine and mutant (exit code or stdout bytes).

## 3. Why the refusal cannot fire (measured, not argued)

**The site is reached, but never refuses.** Over the whole registered grid population
(46 rows, `tests/report-audit/repo-state-grid.py --arm current --current
…probe2.py --json`, grid exit 0, violations 0):

- 73 entries at the M17 site, 37 of them on the non-peel path (`peel=''`).
- Every token was 40 hex characters (histogram `{40: 73}`).
- Entries where `oid` does **not** start with `token` (i.e. where the refusal would
  fire): **0**.
- Raw log: `out/MutationM17Reachability/m17-site-log.txt`.

**The reason is git 2.56's resolution order.** The only non-peel token source is
`full_tokens`, i.e. 40-hex strings. Git always resolves a 40-hex name as an object id
and never through a same-named ref. Measured (`out/MutationM17Reachability/git-behaviour.out`,
script `git-behaviour.sh`, git 2.56.0):

```
branch-create: (ok)
tag-create: (ok)
--- cat-file --batch-check on the 40-hex ref name ---
batch: 1111111111111111111111111111111111111111 missing
batch: 2222222222222222222222222222222222222222 missing
--- rev-parse of the same names ---
rev-parse: warning: refname '1111111111111111111111111111111111111111' is ambiguous.
rev-parse: Git normally never creates a ref that ends with 40 hex characters
rev-parse: because it will be ignored when you just specify 40-hex. …
rev-parse: 1111111111111111111111111111111111111111
--- control: a 8-hex name that is a tag (F13 shape) ---
batch-short: 8d5fbcca62d992d2f407761cb98e9c99688e6648 commit 166
```

So `parts[0]` is always the token itself for a 40-hex token: the condition
`not parts[0].startswith(token)` is false, and the refusal is dead code on this path.
A ref can only shadow a name that is **not** a full object id (the F13 shape: an
8-hex tag), and such names never reach the non-peel path.

## 4. Attempts (all 14 fail to kill M17)

Harness: `out/MutationM17Reachability/probe_m17.py` (fixture builders + three
auditors). Raw results: `out/MutationM17Reachability/attempts.json` and
`attempts.txt`. Each attempt reports `verdict_changed` (pristine vs mutant) and the
site entries with their token lengths.

| # | input tried | pristine | mutant | verdict changed | site entries (all 40-hex, `oid == token`) |
|---|---|---|---|---|---|
| A1 | 40-hex citation; same-named lane branch; object absent | 1 | 1 | no | 2 |
| A2 | 40-hex citation of a real commit; same-named branch → another commit | 1 | 1 | no | 2 |
| A3 | 40-hex citation; same-named lane tag | 1 | 1 | no | 2 |
| A4 | 40-hex citation; same-named branch stored in `packed-refs` | 1 | 1 | no | 2 |
| A5 | 40-hex citation; same-named ref only in the fleet store (2nd store) | 1 | 1 | no | 2 |
| A6 | 8-hex citation + same-named lane tag (the F13 shape) | 2 | 2 | no | 1 |
| A7 | sha256 lane repo; 40-hex citation; same-named tag | 2 | 2 | no | 0 (refused earlier: "object format 'sha256', not sha1") |
| A8 | errata ledger whose correction is a 40-hex naming a ref | 0 | 0 | no | 2 |
| A9 | 40-hex citation; same-named remote-tracking ref `refs/remotes/origin/<40hex>` | 1 | 1 | no | 2 |
| A10 | reftable ref storage; 40-hex citation; same-named branch | 1 | 1 | no | 2 |
| A11 | 40-hex citation of a fleet object; same-named lane branch | 0 | 0 | no | 4 |
| A12 | uppercase 40-hex citation; same-named lower-case branch | 1 | 1 | no | 2 |
| A13 | bare lane repo (`clone --bare`); 40-hex citation; same-named branch | 1 | 1 | no | 2 |
| A14 | 40-hex citation; same-named branch; `core.warnAmbiguousRefs=false` | 1 | 1 | no | 2 |

Why each failed, in one line each:

- **A1-A5, A9-A14**: the ref exists under the citation's own 40-hex name, but git
  resolves the name as an object id, so the token is `missing` (never reaches the
  check) or resolves to itself (`oid == token`). The config and storage variants
  (A10 reftable, A14 `warnAmbiguousRefs`) do not change the resolution order.
- **A6**: this is the shape that *does* refuse — but the refusal comes from
  `bare_objects()` (the peel path, lines 212-214), not from `lookup()`; the M17
  mutant leaves the verdict unchanged (both exit 2, same stderr:
  `could-not-evaluate: …/lane: citation deadbee1 names a ref`).
- **A7**: a sha256 store is refused by `check_history_repo()` before any lookup
  ("object format 'sha256', not sha1"), so the site is never entered (0 entries).
- **A8**: errata corrections are looked up with the peel `"^{commit}"`, so
  `bare_objects()` answers first; the 40-hex correction is `missing` anyway.

## 5. Grid-style runs (the registered detector)

Full grid, `--arm current`, 46 rows:

```
current faults=26/26 contracts=4/4 controls=14/14 tracebacks=0 executed=0 timeouts=0 violations=0
```

| auditor | grid exit | violations | artifact |
|---|---|---|---|
| pristine | 0 | 0 | `out/MutationM17Reachability/grid-pristine.txt` |
| M17 mutant | 0 | 0 | `out/MutationM17Reachability/grid-M17-mutant.txt` |
| instrumented probe | 0 | 0 | `out/MutationM17Reachability/grid-probe-instrumented.txt`, `grid-probe2.json` |

Single-row control, F13 (`--case F13-ref-named-abbreviation`):

```
pristine: current F13-ref-named-abbreviation fault exit=2 kinds=None met      violations=0
M17    : current F13-ref-named-abbreviation fault exit=2 kinds=None met      violations=0
M33    : current F13-ref-named-abbreviation fault exit=0 kinds=[] NOT-MET     violations=1
```

So F13 does not kill M17 (it kills M33): the element is covered at the `bare_objects()`
site, not at the `lookup()` site.

Registered instrument, restricted to the two ids (run in the clone at the tip):

```
$ python3 tests/report-audit/isolation-mutants.py --json \
      --only M17-ref-shadow --only M33-ref-shadow-bare-objects
exit 0
pristine: passed  mutants: 2  killed: 1  surviving: ['M17-ref-shadow']
  M17-ref-shadow               grid_exit 0  killed false  failed_rows []
  M33-ref-shadow-bare-objects  grid_exit 1  killed true   failed_rows ['F13-ref-named-abbreviation']
```

Artifact: `out/MutationM17Reachability/registered-m17-m33.json`.

## 6. Conclusion and the smallest correction

**M17 is unkillable under git 2.56 with the registered detector.** The reason is
structural, not a gap in the grid: the only non-peel token source is `FULL` (40 hex)
and git never resolves a 40-hex name through a ref, so `parts[0].startswith(token)`
is always true there. The docstring's current wording — "[INFERENCE from source and a
probe] the lookup() check is reached only by full 40-hex tokens, which git does not
resolve through a ref, so M17 may be unkillable" — can now be stated as measured.

Smallest corrections, in the order I recommend them (the L1 is the only writer of
lane production files; this seat changed none):

1. **Wording only, no behaviour change (recommended, smallest):** in
   `tests/report-audit/isolation-mutants.py`, replace the "[INFERENCE from source and
   a probe] … may be unkillable" sentence with the measured statement and cite the
   evidence: git 2.56 resolves a 40-hex name as an object id; 73/73 site entries over
   the full grid population had `oid == token`; 14 constructed inputs changed no
   verdict. Keep `M17` registered and do **not** retire it: the code is still in the
   auditor, and the round-25 preregistration only allows retirement with proof that
   the element is gone (`preregistration.json` C1 `non_narrowing_rules`).
2. **Make the element live (two-part change, only if the L1 wants a kill):** the
   auditor's own selftest is the only place a non-40-hex token reaches a non-peel
   `lookup()` (`tools/report-landing-audit.py` lines 1170-1174, `lookup((store,),
   [short])` with a 4-hex prefix). Give the selftest's lane repo a ref whose name is
   a short hex token (a ref beats an abbreviation in git, so the token then resolves to
   the ref's oid, which does not start with the token) and assert the refusal with
   the existing `is_error` helper (`tools/report-landing-audit.py` line 930). Pristine
   → the refusal raises → `is_error` true → selftest exit 0; M17 mutant → `lookup`
   returns `{"<token>": "found"}` → `is_error` false → selftest exit 1 → killed. The
   instrument would then have to run `--selftest` as a second detector for M17, which
   changes the registered counting command and is therefore the L1's decision.
   Caveat to check when writing the fixture: pick a ref whose target oid does not
   accidentally start with the token (1 in 65536), or assert that property.
3. **Not recommended:** widening the non-peel `lookup()` to accept abbreviated names
   would be a behaviour change to the auditor, not an input.

A surviving mutant is a coverage finding, not permission to change the contract: the
"ref-named citation is refused" contract is unchanged and still enforced — at
`bare_objects()` (M33, killed by F13).

## 7. Files written

Under `.ufo/waves/round-25/a2-falsify/out/MutationM17Reachability/`:

- `probe_m17.py` — the attempt harness (14 fixtures × 3 auditors).
- `attempts.json`, `attempts.txt` — raw per-attempt results.
- `git-behaviour.sh`, `git-behaviour.out` — the git 2.56 resolution-order measurement.
- `grid-pristine.txt`, `grid-M17-mutant.txt`, `grid-probe-instrumented.txt`,
  `grid-probe2.json`, `m17-site-log.txt` — grid runs and the site-entry log.
- `registered-m17-m33.json` — registered-instrument run for the two ids.
- `sha256sums.txt` — digests of the pristine, mutant and probe auditors.

Scratch (not part of the lane): `/fast/scratch/hyaku/kama-r25a2w2/MutationM17Reachability/`
(clone + `work/` + `probe_m17.py`).

This report: `.ufo/waves/round-25/a2-falsify/advice/MutationM17Reachability.md`.

## 8. Honesty notes

- No llama-server child was started (the item forbids it); no port was touched.
- Tools: system `git 2.56.0`, system `python3 3.14.8`. No package was installed or
  upgraded by this seat, so there is nothing to record under the tooling directive.
- Every command above was run in the seat's own clone or scratch; the lane working
  tree holds only the untracked files listed in section 7. The lane's own
  `git status --porcelain` shows one deleted file under
  `.ufo/waves/round-25/a2-falsify/out/RerunC2Counter/`; that is another seat's file,
  not mine, and I did not touch it.
- Exit codes: harness `python3 probe_m17.py out.json` exit 0; full grid runs exit 0
  (pristine, M17 mutant, probe); single-row F13 grids exit 0 with `violations=0`
  (pristine, M17) and `violations=1` (M33); registered instrument exit 0.
- Unverified / out of scope: whether git versions other than 2.56.0 resolve a 40-hex
  name differently. The claim in this report is scoped to git 2.56.0 as the item
  requires; git's own warning ("Git normally never creates a ref that ends with 40 hex
  characters because it will be ignored when you just specify 40-hex") is the
  documented behaviour, but I did not test other git releases.
