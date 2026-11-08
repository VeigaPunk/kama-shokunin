# SN01Bounds — kama round 100, wave 1: blast radius of the round-100 probe change

Seat: `SN01Bounds` (bounds / regression). Scope: the `tools/kama-probe.sh` change between the round-100
base `6776c667` and the freeze commit M `2e27e6f1`, i.e. the `router_autoload()` status rule.
Frozen claims: `plans/round-100-claims.md`, mirrored in `.ufo/waves/round-100/claims.json`.

The change under test (`git diff 6776c667 2e27e6f1 -- tools/kama-probe.sh`, `tools/kama-probe.sh:898-905`):

```bash
  local port=$1 pbody="$TMP_ROOT/props$1.body" state pcode
  pcode=$(curl -sS --noproxy '*' ... --max-filesize "$MAX_BODY" -o "$pbody" -w '%{http_code}' \
    "http://127.0.0.1:$port/props" 2>/dev/null) || return 2
  [ "$pcode" = 200 ] || return 2
```

## Verdict summary

| item | result |
|---|---|
| 1. Lane probe tests that exercise router mode / `/props`, base vs tip | **no regression** (77/77 matrix green at both; round90 hostile 13/13, round90 reason-capture 24/24, round93 repeat 10/10, round99 autoload-states 8/8, round99 router-budget 19 cells green) |
| 2. Plain-call subcommands (`listeners`, `consumers`, `check --port`) against a `/props` 401 router body | **no abort, no missing row** — matrix and registry mode, both probes, `bash -euo pipefail` |
| 3. `HAVE_PY=0` branch and curl exit 63 (oversize 200) still read unread | **confirmed** — `HAVE_PY=0` identical base vs tip; oversize 200 → `router-autoload-unread` on both |
| 4. Probe writes nothing outside TMPDIR | **confirmed** — `strace` shows every write-opened path under `$TMPDIR/kama-probe.*` (plus `/dev/null`, `/dev/tty`); `snapshot` writes only inside its explicit `--history` dir |

**One regression found, and it is NOT in the probe**: the freeze commit `2e27e6f1` edited `SKILL.md`
(+25 lines, +1 `## ` section) but did not update `SCORECARD.md`'s live `depth` row, which still
declares the round-99 `SKILL.md` digest/line-count/section-count. The lane's own
`tools/round97-self-assessment-audit.py` grades exactly that row and goes from `mismatches=1` at base to
`mismatches=4` at M (checks 1, 2 and 3 flip to mismatch). Details in F1 below — and F1's remediation
is already applied in the working tree by another seat, but not yet committed.

## F1 — REGRESSION (records, not the probe): `SCORECARD.md`'s live `depth` row is stale at M

**Severity:** high for the lane's calibration axis (C1 works calibration, the lowest axis at 7) — the
lane's own counter is redder at M than at base; the round-100 freeze is the commit that made it so.
It does not falsify either claim's wording (C1's nine checks do not read the `depth` row) and it does
not change any graded number, so it is **not** a `falsifies-number`.

**Evidence — the counter's own output, base vs tip:**

```
$ python3 tools/round97-self-assessment-audit.py --repo . --rev 6776c667
SELF_ASSESS97 checks=18 mismatches=1 met=False rev=6776c667... skill_sha256=f48f5c8e...
$ python3 tools/round97-self-assessment-audit.py --repo . --rev 2e27e6f1
SELF_ASSESS97 checks=18 mismatches=4 met=False rev=2e27e6f1... skill_sha256=7f8eed74...
```

**Which checks flipped.** An instrumented copy of the counter (scratch copy only; the tracked file was
not touched) printing the check index on each `mismatches += 1` gives:

```
=== 6776c667      CHECK_FAIL 16
=== 2e27e6f1      CHECK_FAIL 1   CHECK_FAIL 2   CHECK_FAIL 3   CHECK_FAIL 16
```

Checks 1–3 are `tools/round97-self-assessment-audit.py:131-147`: *"SCORECARD live `depth` row:
SKILL.md sha256, line count, `^## ` section count."* Recomputed from the two revisions:

```
rev 6776c667   check1 sha256 declared=f48f5c8e… observed=f48f5c8e…  OK
               check2 lines  declared=2511        observed=2511         OK
               check3 sects  declared=60           observed=60            OK
rev 2e27e6f1   check1 sha256 declared=f48f5c8e… observed=7f8eed74…  MISMATCH
               check2 lines  declared=2511        observed=2536         MISMATCH
               check3 sects  declared=60           observed=61            MISMATCH
```

`SCORECARD.md`'s `| depth |` row is unchanged by the freeze commit
(`git show 2e27e6f1 -- SCORECARD.md | grep -c '^[+-]| depth |'` → `0` removed, `0` added), while
`SKILL.md` gained the `## Round 100 \`/props\` status rule` section.

**The lane's own convention is that the live `depth` row tracks `SKILL.md`, and round 99 followed it.**
Round 99's freeze `00394f3b` changed `SKILL.md` and left the row declaring the *pre-freeze* digest
`3021fc5d…` (observed `f48f5c8e…`); the very next round-99 commit `71838fdd` ("round-99 measurements:
C1/C2/C3 receipts at 00394f3b …") repaired it in the same diff that recorded the receipts:

```
$ git show 71838fdd -- SCORECARD.md | grep "^[-+]| depth |"
-| depth | **7** | `SKILL.md` sha256 `3021fc5d7e8fb135236f1a9ff8ad9d32d3b764ddbdf664aca2fe807ecc1c2af7` (2484 …
+| depth | **7** | `SKILL.md` sha256 `f48f5c8ebaee86943165e7c6008d5333276f49e7f4339cc2ffc3b0866eee01bd` (2511 …
```

Round 100 has no such follow-up: `3626e06c` (the receipts commit) and `6d0e3abc` (lane HEAD) both
still report `mismatches=4`, i.e. the depth row is stale three commits later.

**Smallest remediation:** in `SCORECARD.md`, update the `| depth |` row to `SKILL.md` sha256
`7f8eed744a61388190be0ac295563000a9d817fe3d24b059f07519a0d48559f1` (2536 lines; 61 sections), or add
the matching row update to the freeze commit. No counter or probe change is needed.

**Status at the time of writing (20:52):** another wave-1 seat has already applied exactly this
remediation in the working tree — `git diff SCORECARD.md` shows

```
-| depth | **7** | `SKILL.md` sha256 `f48f5c8ebaee86943165e7c6008d5333276f49e7f4339cc2ffc3b0866eee01bd` (2511 lines); ru…
+| depth | **7** | `SKILL.md` sha256 `7f8eed744a61388190be0ac295563000a9d817fe3d24b059f07519a0d48559f1` (2536 lines); ru…
```

and recomputing checks 1–3 against the working-tree `SKILL.md` gives `OK / OK / OK`. The defect is
therefore **already fixed in the working tree but NOT in any commit** — `2e27e6f1`, `3626e06c` and
`6d0e3abc` all still carry the stale row. The fix must land in a commit, otherwise the next
`git show`-based re-run of `tools/round97-self-assessment-audit.py` at the tip still reports
`mismatches=4`.

## F2 — C2's counter does not grade the "final" in "a final HTTP 200"

**Severity:** medium. Not a wrong number; a narrowing of the graded property relative to the claim's
stated wording. This is the Amendment-59 class the wave is hunting, on the C2 side.

The claim's wording (`plans/round-100-claims.md:75`, `claims.json` `C2.name`) is *"the probe reads the
router's bare `/props` body only on a **final** HTTP 200"*, and the plan's "After" sentence says
*"curl does not follow redirects here (no `-L`), so a 3xx is graded by its own status."* The frozen
counter `tools/round100-props-status.py` serves each cell's status directly and grades
`(verdict, reason, exit)`. Nothing in it pins the **request path**.

Two independent probes show the counter is blind to the property:

**(a) A `/props?model=` request (not bare) grades green.** Mutant F changes only the request URL
(`tools/kama-probe.sh:903`, `"/props"` → `"/props?model=fixture-model"`), leaving every other byte
identical. llama.cpp routes `?model=` to an instance and may load it — the exact hazard the lane's own
`SKILL.md` warns about (*"`/props?model=` would route to, and may load, an instance"*, `SKILL.md:56-57`).

```
$ python3 tools/round100-props-status.py --repo . --rev 2e27e6f1 \
      --probe-file probes/probe-mutantF.sh --work <scratch>
ROUTER_PROPS_STATUS100 cells=9 mismatches=0 base_mismatches=6 flips=6 stable=3 met=True
```

The round-99 regression control is equally blind:

```
$ python3 tools/round99-autoload-states.py --repo . --rev 2e27e6f1 \
      --probe-file probes/probe-mutantF.sh --work <scratch>
AUTOLOAD_STATES99 cells=8 mismatches=0 base_mismatches=7 flips=7 stable=1 met=True
```

Every stub in the lane splits the query off before matching
(`tools/round100-props-status.py:103` `path = self.path.split("?")[0]`; likewise `round90-reason-capture.py:104`,
`round92-linear-paths.py:91`, `round93-router-repeat.py:95`), so a probe asking for
`/props?model=…` is answered exactly as if it asked for bare `/props`.

**(b) A status the nine cells never serve grades green.** Mutant A relaxes the rule to
`[ "$pcode" = 200 ] || [ "$pcode" = 404 ]`:

```
ROUTER_PROPS_STATUS100 cells=9 mismatches=0 base_mismatches=6 flips=6 stable=3 met=True
```

The nine cells cover 401, 500, 503, 403, 202, 302 and 200 only. The claim's wording is universal
(*"only on a final HTTP 200"*), so a probe that also reads a 404 body satisfies the wording's letter
nowhere but the counter's letter nowhere too. Disclosed limit (d) in the plan already concedes *"other
non-200 statuses follow the same line but are not each graded"* — so (b) is **disclosed**, and I record
it as a limit rather than a defect. (a) is **not** disclosed anywhere: no limit mentions the request
path, and the plan's `SKILL.md` edit adds a table whose first row is *"`/props` final status | 200"*
without a companion statement that the request must be bare.

**Narrowing sentence to name:** `tools/round100-props-status.py:103`
(`path = self.path.split("?")[0]`) — the counter answers a non-bare `/props?model=` request with the
bare `/props` body, so it grades a probe green that violates the claim's word *"bare"*.

**Smallest remediation:** in `tools/round100-props-status.py`'s `Handler.do_GET`, match the raw
`self.path` against `"/props"` exactly (no `split("?")`) and answer a non-bare path 404; then add one
cell whose `/props` answer is a router document with a **non-200** status that is not in the current
nine (404 or 405), so a mutant that widens the rule is caught. Same one-line shape in
`tools/round99-autoload-states.py` for the regression control.

## F3 — C2's counter does not grade the `router-model-missing` diagnostic the tip suppresses

**Severity:** low-medium; a real behaviour loss on a path the claim does not mention, invisible to the
nine cells.

The tip's `return 2` on a non-200 skips `router_file_states()` entirely
(`tools/kama-probe.sh:968-977` runs only when `ra -eq 0`), so the *file* half of the diagnosis is lost
whenever `/props` is not a 200. Measured, with `/v1/models` listing one `unloaded`, not-failed entry
whose `status.args` name a **missing** model file and `/props` answering 401 with a router-`true` body:

```
MISSING_MODEL status=401 probe=base rc=2 verdict=MODEL_UNLOADED reason=router-model-missing
MISSING_MODEL status=401 probe=tip  rc=2 verdict=MODEL_UNLOADED reason=router-autoload-unread
MISSING_MODEL status=200 probe=base rc=2 verdict=MODEL_UNLOADED reason=router-model-missing
MISSING_MODEL status=200 probe=tip  rc=2 verdict=MODEL_UNLOADED reason=router-model-missing   (control)
```

The verdict and exit code are unchanged (`MODEL_UNLOADED`, exit 2) — the claim's predicate holds — but
the operator-facing reason changes from *"your model file is missing"* to *"I could not read the flag"*.
The C2 counter's nine cells use a **present** model file
(`tools/round100-props-status.py:181`, `(work / "model.gguf").write_bytes(b"GGUF\x03\x00\x00\x00" + b"\x00" * 64)`),
so the file check passes on every cell and this divergence is unobservable to it. Disclosed limit (c)
says *"Only the `/props` read in `router_autoload()` changes"* — the file check's reachability is a
second-order effect of that read and is not disclosed.

**Smallest remediation (disclosure, not code):** add one sentence to `SKILL.md`'s round-100 table note
and to the plan's limit (c): a non-200 `/props` also suppresses the model-file check, so
`router-model-missing` / `router-model-invalid` are unreachable for that answer.

## F4 — C1's counter grades string presence, not agreement with the wave evidence

**Severity:** medium-high for the calibration axis (C1's assigned axis, lowest at 7). Independent
reproduction of the sibling `EX02RecordForge` finding, on my own harness.

The C1 claim's wording (`plans/round-100-claims.md:31`, `claims.json` `C1.name`) is *"the round-100
correction of the round-99 records **agrees with the committed round-99 wave evidence** on nine
enumerated checks"*, and the blocks name the seats they count. The counter derives the fractions from
`.ufo/waves/round-99/w1-spec.json` roles but grades only the *presence* of the derived fraction
strings (`tools/round100-record-audit.py:134` `checks[3] = sc is not None and led_s in sc and pol_s in sc`;
`:146` `checks[6] = len(blocks) == 2 and all(seat_s in b for b in blocks)`). It never cross-checks the
*seat names* the blocks enumerate, nor the seat count in prose.

My own battery (`work/sn01_seatnames.py`: scratch `git clone --shared` of the lane, checkout
`6776c667`, copy the three M-byte record files, apply one edit, commit with fixture identity, run
`python3 tools/round100-record-audit.py --repo <clone> --rev HEAD`; the clone's
`git rev-parse --show-toplevel` asserted equal to the clone path before every mutating call):

```
SN01_C1_SEATS P0-positive          rc=0 mismatched=- :: 'checks=9 mismatches=0 met=True'
SN01_C1_SEATS H1-wrong-policy-seat rc=0 mismatched=- :: 'checks=9 mismatches=0 met=True'   # "…, KagiR69a2 (not an attack seat)." instead of MT01Mutants
SN01_C1_SEATS H2-wrong-ledger-seat  rc=0 mismatched=- :: 'checks=9 mismatches=0 met=True'   # "…, CR02Depth (not a ledger seat)." instead of CN01Overlap
SN01_C1_SEATS H3-wrong-count-words  rc=0 mismatched=- :: 'checks=9 mismatches=0 met=True'   # "12 seats, 0 dead (earlier reports said 10 seats, 0 dead)"
```

H1 and H2 name a seat that is **not** in the round-99 spec at all (the spec's 12 items are
`SC01Recon, SC02Sources, EX01Counter, EX02Records, EX03Autoload, SB01Entry, RV01Wording, RV02Counter,
CR01Records, MT01Mutants, SN01Bounds, CN01Overlap`), while the *count* and *fraction* stay correct — so
the correction reads as agreement with the wave evidence but names the wrong seats.

Plan limit (a) discloses that a block which "also says 'seven attack seats' in words" is not caught, and
that checks 3/4/6 are presence checks. H1/H2 are **not** that case: they state the correct fraction
*and* the correct count, and misattribute which seats were attack seats — the enumeration is what the
plan's own C1 text calls *"the four above plus SN01Bounds and CN01Overlap"*. H3 is a prose contradiction
of the seat count, which limit (a) covers only in the "share"/"seven attack seats" wording.

**Narrowing sentence to name:** `tools/round100-record-audit.py:134` — `led_s in sc and pol_s in sc`
grades the two fraction strings, never the seat roster the blocks enumerate alongside them.

**Smallest remediation:** derive the expected seat-name list from the same `w1-spec.json` roles the
counter already reads and require each block to carry it (a fourth presence check on the enumerated
names), or fold the roster into checks 3/4 as a string equality rather than a substring test.

## Item 1 detail — lane probe tests, base vs tip

All commands run from the lane root with `--repo .`; the probe bytes come from `git show <rev>:tools/kama-probe.sh`
unless noted. Every counter that exists at both revisions was run at both.

| instrument | base `6776c667` | tip `2e27e6f1` | note |
|---|---|---|---|
| `tests/probe-verdicts/check.py` (77 rows, incl. 5 `RouterUnloaded.json` `/props` rows) | 77/77, exit 0 | **77/77, exit 0** | receipts `out/SN01Bounds/probe-verdicts-{base,tip}.json`; probe sha differs (`05ebee88…` vs `23b26d76…`) so the same rows were graded by different bytes |
| `tests/probe-verdicts/fault-controls.py` | — | `detected=17 accepted=0` | the 17 injected probe faults are all still caught with the tip probe |
| `tools/round99-autoload-states.py` (the declared regression control) | `cells=8 mismatches=0 base_mismatches=7 flips=7 stable=1 met=True` | **same** | matches the committed `.ufo/waves/round-100/controls/c2-regression-r99.out` byte-for-byte on the summary line |
| `tools/round100-props-status.py` | `cells=9 mismatches=6 base_mismatches=6 flips=0 stable=9 met=False` (exit 1) | **`cells=9 mismatches=0 base_mismatches=6 flips=6 stable=3 met=True`** (exit 0) | matches the committed `controls/c2-base.out` and `measured/c2.out` |
| `tools/round90-hostile-answers.py` (incl. H3 `/props` oversize) | 13 cells, 0 mismatches | **13 cells, 0 mismatches** | |
| `tools/round90-reason-capture.py` (24 `/props` reason cells) | 24 cells | **24 cells, identical reasons** | e.g. `router-unloaded`, `router-unloaded-autoload`, `router-sleeping` unchanged |
| `tools/round93-router-repeat.py` (10 router cells × 3 runs) | `cells=10 mismatches=0` | **`cells=10 mismatches=0`** | |
| `tools/round99-router-budget.py --skip-load --burners 0` | — | all 19 natural cells `ok=1` | the counter's own `could-not-evaluate` is the host clock (`W03 natural pass 44.9 s < 1.25 × 60 s`), not a probe defect; no burner was started |
| `tools/round97-router-budget.py --skip-load --burners 0 --cells new` | — | all 4 new cells `ok=1` | same host-clock note |
| `tools/round99-record-audit.py` | `checks=12 mismatches=0 met=True` | **`checks=12 mismatches=0 met=True`** | |
| `tools/round99-control-population.py` | `met=True` | **`met=True`** | |
| `tools/round96-depth-audit.py` | `checks=14 mismatches=0 met=True` | **`checks=14 mismatches=0 met=True`** | |
| `tools/round98-depth-boundary-audit.py` | `rows=8 checks=13 mismatches=0 met=True` | **`rows=8 checks=13 mismatches=0 met=True`** | |
| `tools/round92-linear-paths.py` | `cells=15 mismatches=1` (D3) | `cells=15 mismatches=1` (D3) | **pre-existing, not round 100** — see below |
| `tools/round97-depth-boundary-audit.py` | `rows=8 checks=12 mismatches=1` | `rows=8 checks=12 mismatches=1` | pre-existing at both revisions |
| `tools/round97-self-assessment-audit.py` | `checks=18 mismatches=1` | **`checks=18 mismatches=4`** | **F1 — a round-100 regression** |

**D3 attribution (`round92-linear-paths.py`).** The differential cell `D3-router-50-unloaded-wild` is red
at M. It is red at the round-100 **base** too, and it was introduced by round 99, not round 100:
`ok=1` at `f6e7ccc2` (round-99 freeze) and at the round-92 frozen base `ed018ca0`; `ok=0` from
`00394f3b` (round-99 amendment 1) onward. The cause is the round-99 reason rename
(`router-unloaded` → `router-autoload-unread`), which the round-92 differential cell compares byte-wise
against `ed018ca0`. Round 100 neither caused nor repaired it. Note it is *not* listed among round-100's
regression controls, and the round-100 plan's disclosed limits do not mention it.

## Item 2 detail — plain-call subcommands under `bash -euo pipefail`

One-cell loopback stub (`out/SN01Bounds/` harness, scratch only): `/v1/models` 200 with one
`unloaded`, not-failed entry; `/props` 401 with a router-shaped body
`{"role":"router","models_autoload":false}` (and the `models_autoload:true` variant). The probe was
run as `bash -euo pipefail <probe> <subcommand> …` with `TMPDIR` pointed at a scratch dir.

```
PLAIN_CALL label=p401 probe=base sub=listeners rc=0 json=ok n_rows=1 rows=[{"port":34781,"verdict":"MODEL_UNLOADED","reason":"router-unloaded","served_model":"fixture-model"}]
PLAIN_CALL label=p401 probe=base sub=consumers rc=0 json=ok n_rows=1 rows=[{"id":"cli-override","verdict":"MODEL_UNLOADED","reason":"router-unloaded","served_model":"fixture-model"}]
PLAIN_CALL label=p401 probe=base sub=check    rc=2 json=ok n_rows=1 rows=[{"verdict":"MODEL_UNLOADED","reason":"router-unloaded","drift":true}]
PLAIN_CALL label=p401 probe=tip  sub=listeners rc=0 json=ok n_rows=1 rows=[{"port":34781,"verdict":"MODEL_UNLOADED","reason":"router-autoload-unread","served_model":"fixture-model"}]
PLAIN_CALL label=p401 probe=tip  sub=consumers rc=0 json=ok n_rows=1 rows=[{"id":"cli-override","verdict":"MODEL_UNLOADED","reason":"router-autoload-unread","served_model":"fixture-model"}]
PLAIN_CALL label=p401 probe=tip  sub=check    rc=2 json=ok n_rows=1 rows=[{"verdict":"MODEL_UNLOADED","reason":"router-autoload-unread","drift":true}]
```

**No abort, no missing row** on either probe: every subcommand printed exactly one row, every JSON
document parsed, and the exit codes are the documented ones (`listeners` 0, `consumers` 0, `check` 2 on
drift). The only difference base→tip is the *reason* (`router-unloaded` → `router-autoload-unread`),
which is the claim's own subject.

This matters because the tip's new line `pcode=$(curl … ) || return 2` is inside a function called
under `set -euo pipefail`; `router_refine` calls it as `if router_autoload "$port"; then ra=0; else ra=$?; fi`
(`tools/kama-probe.sh:965`), so the nonzero return is captured rather than aborting. Verified on the
plain-call paths, which are the ones the round-99 amendment 1 receipt cared about.

Registry mode (the mode the lane actually runs — `read_registry` over a scratch registry and a scratch
consumer file, both pointing at the same stub) was exercised too:

```
REG_MODE label=reg401 probe=base sub=check     rc=2 n_rows=1 first={'id':'stub-row','verdict':'MODEL_UNLOADED','reason':'router-unloaded','drift':True}
REG_MODE label=reg401 probe=tip  sub=check     rc=2 n_rows=1 first={'id':'stub-row','verdict':'MODEL_UNLOADED','reason':'router-autoload-unread','drift':True}
REG_MODE label=reg401 probe=base sub=consumers rc=0 n_rows=1 first={'id':'stub-row','verdict':'MODEL_UNLOADED','reason':'router-unloaded'}
REG_MODE label=reg401 probe=tip  sub=consumers rc=0 n_rows=1 first={'id':'stub-row','verdict':'MODEL_UNLOADED','reason':'router-autoload-unread'}
REG_MODE label=reg401 probe=base sub=snapshot  rc=2 n_rows=1 …
REG_MODE label=reg401 probe=tip  sub=snapshot  rc=2 n_rows=1 …
history_files=['hist/.lock','hist/20261108T232647Z.json','hist/DELTA.md','hist/latest.tsv']   (both probes)
```

## Item 3 detail — `HAVE_PY=0` and curl exit 63

**`HAVE_PY=0`** — the probe was run with `PATH` reduced to a sandbox holding `bash curl ss mktemp rm cat
sed grep head wc awk tr sort uniq dirname basename touch date sleep cut tail timeout` and **no**
`python3` (verified: `command -v python3` → not found). The probe takes its documented fallback path
(`tools/kama-probe.sh:120`, `HAVE_PY=0`) and, crucially, `router_autoload()` returns 2 before curl
(`tools/kama-probe.sh:899`, `[ "$HAVE_PY" -eq 1 ] || return 2`) — the status rule cannot fire without
python. Base and tip are byte-identical in behaviour:

```
HAVE_PY=0 probe=base rc=0 verdict=MODEL_OK reason=matched
HAVE_PY=0 probe=tip  rc=0 verdict=MODEL_OK reason=matched
```

(One caveat, pre-existing and identical on both probes: with no `python3` the probe also loses `paste`,
so the served-model list is empty and `body_has_model_array` falls back to grep. `paste` is not in the
probe's dependency check at `tools/kama-probe.sh:1739-1741`, which checks only `ss` and `curl`. Not a
round-100 change — the base probe behaves the same.)

**curl exit 63 (oversize 200)** — an 8 MiB `/props` body, once with `Content-Length` and once
close-delimited, against a 200 status:

```
OVERSIZE mode=close  probe=base rc=2 verdict=MODEL_UNLOADED reason=router-autoload-unread
OVERSIZE mode=close  probe=tip  rc=2 verdict=MODEL_UNLOADED reason=router-autoload-unread
OVERSIZE mode=length probe=base rc=2 verdict=MODEL_UNLOADED reason=router-autoload-unread
OVERSIZE mode=length probe=tip  rc=2 verdict=MODEL_UNLOADED reason=router-autoload-unread
```

Both read **unread**; the tip's `|| return 2` on curl's nonzero exit preserves the base's oversize
behaviour exactly. The tip adds the status check *after* that, so exit 63 still short-circuits to
unread and never reaches the 200-only read.

## Item 4 detail — writes confined to TMPDIR

`strace -f -y -e trace=openat,open,creat,unlink,unlinkat,rename,renameat,mkdir,mkdirat` around each
subcommand, then every path opened with a write flag (`O_WRONLY|O_RDWR|O_CREAT|O_APPEND|O_TRUNC`):

```
== tip: 6 write-opened paths
    /dev/null
    /dev/tty
    <TMPDIR>/kama-probe.h9B66x/m37713.body
    <TMPDIR>/kama-probe.h9B66x/m37713.err
    <TMPDIR>/kama-probe.h9B66x/m37713.hdr
    <TMPDIR>/kama-probe.h9B66x/props37713.body
   OUTSIDE TMPDIR: ['/dev/tty', '/dev/null']      # device nodes, not lane files
== base: identical set
```

`/dev/null` and `/dev/tty` are character devices opened by the shell/curl, not files the probe creates.
Repeated for `listeners`, `consumers` and `snapshot` on both probes with the same result
(receipts `out/SN01Bounds/strace-*.txt`). The probe's own `TMP_ROOT` is
`mktemp -d "${KAMA_PROBE_TMPDIR:-${TMPDIR:-/tmp}}/kama-probe.XXXXXX"` (`tools/kama-probe.sh:1744`) and
is removed by the EXIT trap. `snapshot` writes only inside its explicit `--history` dir (verified with
a scratch history dir: only `.lock`, the dated JSON, `DELTA.md`, `latest.tsv`).

## What I could not verify

- No live llama.cpp router or proxy was contacted: every stub was a loopback server started by this
  seat on an ephemeral port. Disclosed limit (a) of C2 is unchanged by this report.
- `tools/round99-router-budget.py` and `tools/round97-router-budget.py` could not reach their load
  discriminators on this host (their own `could-not-evaluate` message: the natural pass was faster than
  the round-94 constant wrapper would have truncated). Their **natural** passes are green. No synthetic
  CPU burn was started (`--burners 0 --skip-load`).
- `tools/round97-depth-boundary-audit.py` is red (`mismatches=1`) at both base and tip — pre-existing,
  out of the round-100 blast radius, and I did not attribute it further.
- The `round92-linear-paths.py` D3 cell is red at both base and tip (round-99 attribution above); I did
  not repair it, since that would edit a tracked lane file.

## Files

- Report: `.ufo/waves/round-100/w1/SN01Bounds.md` (this file).
- Receipts: `.ufo/waves/round-100/w1/out/SN01Bounds/` — `probe-verdicts-{base,tip}.json`,
  `strace-{base,tip}.txt`, `strace-{base,tip}-{listeners,consumers}.txt`.
- Scratch (deleted before yield): `/fast/scratch/hyaku/kama-r100/SN01Bounds/` — probe copies at base and
  tip, the stub harnesses, the mutant probes A/C/F, the instrumented counter copy, and the forgery
  harnesses. No clone or work tree remains; the lane working tree and the lane Git index were not
  modified by this seat (the two `corpus/knowledge/*.md` edits visible in `git status` are this wave's
  other seats' work, not mine).

## Verdict lines

VERDICT C1 falsifies-wording the round-100 correction counter grades only the *presence* of the derived
fraction strings and of `12 seats, 0 dead`, never their agreement with the wave evidence: a block that
names a seat that is not in the round-99 spec (my H1/H2 battery: `KagiR69a2` for `MT01Mutants`,
`CR02Depth` for `CN01Overlap`) or contradicts the seat count in prose (H3) grades
`checks=9 mismatches=0 met=True`, while the claim says the correction "agrees with the committed
round-99 wave evidence" — narrowing sentence `tools/round100-record-audit.py:134`
(`led_s in sc and pol_s in sc`) and `:146` (`all(seat_s in b for b in blocks)`). Independently
reproduced on my own clone harness (F4); no wrong number found: at M the counter prints exactly
`checks=9 mismatches=0 met=True` and at base `checks=9 mismatches=9 met=False`, matching the committed
`measured/c1.out` and `controls/c1-base.out`.

VERDICT C2 falsifies-wording the frozen C2 counter grades verdict/reason/exit on nine stub answers and
cannot see the request path — a probe that asks for `/props?model=…` instead of the bare `/props`
(llama.cpp would route it to an instance and may load it) grades `mismatches=0 met=True`, as does the
round-99 regression control, so the claim's word "bare" is ungraded and undisclosed; narrowing sentence
`tools/round100-props-status.py:103` (`path = self.path.split("?")[0]`). No wrong number was found:
at M the counter prints exactly `cells=9 mismatches=0 base_mismatches=6 flips=6 stable=3 met=True`,
matching `measured/c2.out`, and the base prints `mismatches=6 met=False`, matching `controls/c2-base.out`.
