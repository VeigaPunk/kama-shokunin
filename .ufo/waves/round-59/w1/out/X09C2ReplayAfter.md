# X09C2ReplayAfter — round 59, kama (leaf, advisory)

**Axes:** operability 8, calibration 7 (lowest assigned). **Milestone:** round59 claim falsification.
**Attacked claim/clause:** frozen C2 calibration 7→7 predicate/sentence in
`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-59/controls/freeze.txt` (base `8f7f58cd`, control commit `5d957d24`):
"At the measured lane tip the calibration row contains no literal spotcheck total or pinned 40-hex fleet revision, and
its latest outside-closure pointer/token/count are recomputed by a runnable checker from the lane tree plus the explicitly
named fleet HEAD; counter passes the genuine tip and rejects controls changing each individual field while preserving a
real outside admit/reject spot-check record for S517 and S518." Kill rule: "any shortcut control meets, any field mismatch
is accepted, no current external verdict available, or genuine cannot evaluate -> claim not met."

This is a falsification seat, not the judge. No source edit, no commit, no counter/fixture/target change. Scratch only:
`/fast/scratch/hyaku/kama-r59/X09C2ReplayAfter/` (TMPDIR set to it; removed at end). No installs or updates (python3 3.14.8 only).

## 1. Primary replay (frozen command form, live fleet HEAD)

```
cd /fast/scratch/hyaku/kama-r59/X09C2ReplayAfter && TMPDIR=/fast/scratch/hyaku/kama-r59/X09C2ReplayAfter \
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round59-c2-counter.py \
  --repo /home/vgpnk/Projects/shokunin/kama-shokunin \
  --tip 2c7443abb8d6edb8a5b0f91dfee9f81b824f6d35 --fleet-ref HEAD
```
exit `0`; stderr empty. Output verbatim:
```
tip=2c7443abb8d6edb8a5b0f91dfee9f81b824f6d35 fleet=0f99f606120d0c884656c6e7a290f0e8f33c2181 maxN=57 manifest=rejected-honest-stop
rows=44 mismatches=0 met=True
row_missing=0 typed_count=0 pinned_fleet_revision=0 pointer_missing=0 pointer_round=0 pointer_verdict=0 including_round=0 count_command=0
```
- **Full resolved fleet revision: `0f99f606120d0c884656c6e7a290f0e8f33c2181`** (`git -C /home/vgpnk/Projects/shokunin rev-parse HEAD` recorded immediately before and immediately after the run; both lines identical, so no HEAD drift during measurement).
- **Mismatch counts: all eight fields 0, total `mismatches=0`, `met=True`.** Derived values: `maxN=57`, `rows=44`.
- Counter bytes are tip-identical: `sha256(tools/round59-c2-counter.py)` = `1aa0cf055734c89f8b51d3cdc64ce5d1f50afaefd5dde070dfe37c541617e1b5` in the working tree, at `2c7443ab`, at `4a541190`, and at lane `HEAD`.
- Independent re-derivation from committed bytes at `2c7443ab`: `git ls-tree --name-only 2c7443ab corpus/lessons/ | grep -cE '^corpus/lessons/round-[0-9]+-verifier-spotcheck\.md$'` → `44`; highest number → `57`. Fleet MANIFEST at live HEAD carries `lane=kama, lane_round=57, verdict=rejected-honest-stop, admitted=false`; no kama r58 closure row exists (kama closures end 54 rejected-honest-stop, 55 admitted, 56 rejected-honest-stop, 57 rejected-honest-stop).
- Determinism: the same command run twice produced byte-identical output (`diff` empty).

## 2. Fleet-revision sweep (resolution is live, not pinned)

Same frozen command, `--fleet-ref` varied:

| `--fleet-ref` | resolved `fleet=` | mismatches | exit |
|---|---|---|---|
| `c071f0de…` (freeze `fleet-manifest-rev`) | `c071f0dea9d00d944690534ff8461653eb94df66` | 0, met=True | 0 |
| `58cffd1f…` (fleet ref at C2 measurement) | `58cffd1f42723048bcfe48eb0bc2f346caa9b77f` | 0, met=True | 0 |
| `3f3dd973…` (fleet HEAD stated at dispatch) | `3f3dd97345ef1aedfdaec818c9e58675d4f41e3f` | 0, met=True | 0 |
| `HEAD` (live) | `0f99f606120d0c884656c6e7a290f0e8f33c2181` | 0, met=True | 0 |
| `HEAD~5` | `0ffe92719142d9a4a645900fac7a2b819079058e` | 0, met=True | 0 |

Only the `fleet=` token changes across these runs; every other field is constant. This matches the previously recorded receipts (`.ufo/waves/round-59/controls/c2-after.out` at `58cffd1f`, `c2-after-current-head.out` at `3f3dd973`) and extends them to the fleet HEAD that exists now.

## 3. Fail-closed and discrimination controls

| control | observed | exit |
|---|---|---|
| base tip `8f7f58cd` @ live HEAD | `maxN=57 manifest=rejected-honest-stop rows=44 mismatches=3 met=False`, `typed_count=1 pinned_fleet_revision=1 count_command=1` | 1 |
| bogus `--tip deadbeef…` | `could-not-evaluate: unresolvable lane tip or fleet ref` | 2 |
| bogus `--fleet-ref nosuchref` | `could-not-evaluate: unresolvable lane tip or fleet ref` | 2 |
| `--fleet-repo` = non-repo scratch dir | `could-not-evaluate: unresolvable lane tip or fleet ref` | 2 |
| `--fleet-repo` = lane repo (no `MANIFEST.json`) | `could-not-evaluate: missing SCORECARD, lessons tree, or MANIFEST` | 2 |
| `--fleet-ref c9493ce5` (last fleet MANIFEST before the kama r57 closure row) | `manifest=None … mismatches=1 met=False`, `pointer_verdict=1` | 1 |
| abbreviated `--tip 2c7443` | output binds full `tip=2c7443abb8d6edb8a5b0f91dfee9f81b824f6d35` | 0 |
| `--tip HEAD` in the lane (HEAD `4a541190`) | `tip=4a541190b6d494a4e99116249632e99aab80adcc … mismatches=0 met=True` | 0 |

The `c9493ce5` row is the load-bearing one: with a named fleet revision that lacks the kama r57 closure, the same lane tip fails on `pointer_verdict` only. The outside-closure verdict is therefore genuinely re-derived from the named fleet ref, not hard-coded.

## 4. Per-field sensitivity (seat-authored fixtures, scratch clone of the lane at `2c7443ab`)

Fixture: `git clone --shared` of the lane into scratch, `git -C <clone> rev-parse --show-toplevel` asserted equal to the clone path, one SCORECARD calibration-row edit committed per fixture with an in-clone identity (`-c user.name=r59-fixture -c user.email=fixture@localhost`), then the frozen counter run with `--repo <clone> --tip <fixture commit> --fleet-ref HEAD`. No lane bytes touched.

Each of the seven enumerated fields was mutated alone; every fixture produced **exactly one** mismatch on the mutated field, `met=False`, exit 1:

```
SUMMARY typed_count:exit=1,mism=1,typed_count=1
        pinned_fleet_revision:exit=1,mism=1,pinned_fleet_revision=1
        pointer_missing:exit=1,mism=1,pointer_missing=1
        pointer_round:exit=1,mism=1,pointer_round=1
        pointer_verdict:exit=1,mism=1,pointer_verdict=1
        including_round:exit=1,mism=1,including_round=1
        count_command:exit=1,mism=1,count_command=1
```
Benign control (prose reword of `score round 1; evidence re-anchored round 58` → `… (wording refreshed)`, pointer/token untouched): `mismatches=0 met=True`, exit 0. The counter is field-sensitive for these spellings and not prose-brittle in the irrelevant parts.

## 5. Falsification: shortcut controls that MEET

Four fixtures express the *same* shortcut the predicate forbids, in spellings the counter's regexes do not see. Each was committed in the scratch clone exactly like the per-field fixtures above (anchor asserted unique, tip `06b010e2…`, `2309d9ae…`, `c3567c2d…`, `4443c2d9…`):

| fixture edit inside the calibration row | counter result | exit |
|---|---|---|
| insert `44 verifier-spotcheck files` (literal outside-closure count) | `typed_count=0 … mismatches=0 met=True` | **0** |
| insert `spotchecks=44` | `typed_count=0 … mismatches=0 met=True` | **0** |
| insert `fleet c071f0de` (8-hex pinned fleet revision) | `pinned_fleet_revision=0 … mismatches=0 met=True` | **0** |
| insert `fleet sha256 d9b7737e…f0379f83` (64-hex pinned revision) | `pinned_fleet_revision=0 … mismatches=0 met=True` | **0** |

Cause read from the frozen source (no edit made): `typed_count` is `re.search(r"\b\d+`?\s+\(outside closures on record", row)` and `pinned_fleet_revision` is `re.search(r"\b[0-9a-f]{40}\b", row)`. Only the exact phrase-after-number and the exact 40-hex word form are caught. A literal count written as words or `spotchecks=N`, a short-hash pin, and a 64-hex (sha256) pin all leave both fields at 0, so the row can carry a hard-coded count or a pinned revision and still report `met=True`.

Under the frozen kill rule as written ("any shortcut control meets … -> claim not met"; also "any field mismatch is accepted"), these are shortcut controls against the count and revision fields that meet. Whether seat-authored, post-freeze fixtures of this spelling count as "shortcut controls" inside the frozen meaning is L1/closure's call, not mine; the measured behaviour is stated above with exact commands.

## 6. Clauses my replay could not establish

- "preserving a real outside admit/reject spot-check record for S517 and S518": the counter never reads spot-check file content — it only matches path shape (`corpus/lessons/round-<N>-verifier-spotcheck.md`), round number, and the verdict token against MANIFEST. No check binds S517/S518 admit-or-reject text. Separately, the round context states the external S517/S518 spot-check is **not recorded**; S517/S518 appear only as round-58 lane-side registry/admit rows. **I claim no discernment progress and no S517/S518 admit/reject verification.**
- "explicitly named fleet HEAD": the row names `--fleet-ref HEAD` but not the fleet repo; the fleet path is a hard-coded default (`/home/vgpnk/Projects/shokunin`) in the counter. On a different host this silently targets another tree — it fails closed (`exit 2`) if that tree lacks `MANIFEST.json`, but the repo identity itself is not bound by the row's command.
- `count_command` is a textual self-reference: the row passes if it merely contains the string `tools/round59-c2-counter.py` and `--fleet-ref`. It does not establish that the command, as written, runs.

## Verdict for this seat (bounded)

- The C2 frozen counter, replayed at the measured lane tip `2c7443abb8d6edb8a5b0f91dfee9f81b824f6d35` against the live fleet HEAD `0f99f606120d0c884656c6e7a290f0e8f33c2181`, **passes with `mismatches=0 met=True` exit 0**, and the same result holds for every fleet revision on record (`c071f0de`, `58cffd1f`, `3f3dd973`, `0f99f606`, `0ffe9271`). Resolution of both lane tip and fleet revision is printed in full; there is no ambiguity about which commits were read.
- Operability is strong on the exercised paths: exits distinguish met (0), not met (1) and could-not-evaluate (2); unresolvable/missing inputs fail closed; the base tip fails with the three fields the freeze names; a fleet revision without the kama r57 closure flips `pointer_verdict` alone.
- Calibration is **not** established by this replay: the count and pinned-revision fields fail open for ordinary alternate spellings (§5), and the S517/S518 record clause is unenforced and externally unrecorded (§6). This is a falsification, not an admission; no score movement is proposed.

**Evidence retained:** all commands and outputs above, run from `/fast/scratch/hyaku/kama-r59/X09C2ReplayAfter/` with `TMPDIR` set to it; the fixture clone and its seven plus four commits existed only there and under `/fast/scratch`, and the directory was removed after this file was written. Lane, fleet root and `shokuknow` were read-only throughout; no campaign tools were run in `shokuknow`. No tools installed or updated. **Blockers:** none.
