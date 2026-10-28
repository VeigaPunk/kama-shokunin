# W04ScorecardDraft — SCORECARD round-62 measured-results paragraph template

Seat: advisory leaf, judged axis **calibration**. Assignment: draft the round-62
measured-results paragraph template — the two claim rows with placeholder counters, the
regression-list shape rounds 47–50 use, and the `What met=True does not show` section seeded
with the three disclosed limits. This is a **draft text**, not a verdict on C1/C2, not a commit,
and not an edit to any lane source outside this file.

Frozen context read first: `.ufo/waves/round-62/controls/freeze.txt` (base
`a959fd9022b1ac1f3cb4dc2475d9cded8b2b01c3`), `controls/c1-base.txt`, `controls/c2-base.txt`.
Tip at first read `65d7cad0…`; the L1 advanced `master` four commits while this seat ran
(`dc5e1010` → `a837c8f7` → `e092f2b6` → `a25dd0d9`), so every value below names the revision it
was measured at. All commands ran in `/fast/scratch/hyaku/kama-r62/w/W04ScorecardDraft/` with `TMPDIR` pointed
there; receipts copied to `.ufo/waves/round-62/w1/out/W04ScorecardDraft/receipts/`. The two
seat-spawned background jobs were allowed to finish (`bg_27272` 906.4 s, `bg_27352` 906.2 s) and
their results are §4.2/§4.5 below; the scratch tree was then removed.

---

## 1. The template

Paste target: append after the existing `## Round 62 — …` section. `SCORECARD.md` is A-corr
under `registry/append-only-contract.tsv` (dated round sections append-only; the five head
sections are the only ungraded region), so the measured block is **appended**, and any pending
cell it supersedes is restored by append, not rewritten (round-58 precedent). Placeholders are
`<NAME>` tokens; §3 maps each to its receipt.

```markdown
### Round-62 measured results

Measured commit: `<TIP>` (fresh clone of the lane). Counters: `tools/round62-c1-counter.py`
sha256 `<C1_COUNTER_SHA>` (blob introduced at `<C1_COUNTER_COMMIT>`), `tools/round62-c2-counter.py`
sha256 `<C2_COUNTER_SHA>` (blob introduced at `<C2_COUNTER_COMMIT>`), `tools/kama-completion-live.py`
sha256 `<TOOL_SHA>`. `<COUNTER_BYTES_NOTE>`

| Claim | Base | Measured `<TIP_SHORT>` | Command | Receipt |
|---|---|---|---|---|
| C1 operability 8 → 8 | `<C1_BASE_LINE>` (exit 1) | `<C1_LINE>` (exit `<C1_EXIT>`) | `python3 tools/round62-c1-counter.py --repo <clone> --tip <full commit> --work <scratch>` | `.ufo/waves/round-62/controls/c1-base.txt`; `.ufo/waves/round-62/measured/c1.out` |
| C2 calibration 7 → 7 | `<C2_BASE_LINE>` (exit 1) | `<C2_LINE>` (exit `<C2_EXIT>`) | `python3 tools/round62-c2-counter.py --repo <clone> --tip <full commit> --work <scratch>` | `.ufo/waves/round-62/controls/c2-base.txt`; `.ufo/waves/round-62/measured/c2.out` |

Scores held: operability 8, calibration 7. Capabilities 12 → 13 only if C1 is admitted
(`live-completion-request-plane`, first-working round 62, outside the frozen 12-row C2
population); C2 adds no capability. No axis score delta is claimed by this paragraph.

Regressions at `<TIP_SHORT>` (`.ufo/waves/round-62/measured/*.out`, each with its `tip=` line):
gate `registered <R> unregistered <U> defective <D>`; capability census `listed <L> observed <O>
missing <M> unsubstantiated <N> met <True|False>`; round-41 head counter `<R41_LINE>`;
round-42 self-description `<R42_LINE>`; round-43 registry `<R43_LINE>`; pointer `met=<B>`;
digest-ledger `unknown=<K>`; hexrun-census `unknown=<K>`; `sources-append-only --from <BASE>`
exit `<rc>` (`<last line>`); `append-only-audit --to <TIP>` exit `<rc>` (`<summary tail>`);
selftests `AOA_SELFTEST pass=<n> fail=0`, `KLR_SELFTEST pass=<n> fail=0`, live `selftest: ok`,
`check-receipt` `<n> VALID / <n> mutations rejected`; prior-round counters `<…>`; then one clause
per red item naming whether it is **carried from the base** (with the base value) or **introduced
by this round** and which seat/closure owns it; end census exit `<rc>` (`<summary>`).

### What `met=True` does not show (round-62 wave attacks)

- **Disclosed before the wave** (freeze limits, not wave findings): the hold-window contact
  proves **one loopback port** — the counter POSTs to `127.0.0.1:<port>` read from the tool's
  `hold.json` (`tools/round62-c1-counter.py:67-75,239-252`) and never contacts a registered
  consumer (`registry/endpoint-consumers.tsv`: omp-llama-cpp-default 8080, ufo-fsd-thetick and
  ufo-fsd-local-helper 34113); C2's **sensitivity leg only mutates captured output**
  (`out.replace(pattern, MUT)`, lines 268-271) and never re-executes a check, so it is not a
  causal or semantic test; and the **scan bindings trust the real repository** — the
  `digest-ledger`/`hexrun-census` rows bind `--repo %R --rev TIPREV` (`%R` = the caller's
  repository, line 186), so their `unknown=0` is a statement about the named repo's objects plus
  host artifacts re-hashed at scan time, not about the extracted tip tree alone.
- **C1, wave findings.** `<…>`
- **C2, wave findings.** `<…>`
- **Integration fixes after the wave.** `<…>`
- **Separability holds** (seat `<…>`): `<…>`
```

Base cells are fixed by the freeze receipts and need no placeholder — copy verbatim:

```text
C1 base: tool_present=0 live_ok=0/1 fake_rejected=0/2 stale_rejected=0/1 tamper_rejected=0/8 log_rejected=0/1 predead_rejected=0/1 sigterm_rejected=0/1 hold_rejected=0/1 outside_rejected=0/1 errors=1 met=False
C2 base: population=12 rows=0 covered=0/12 bound=0 eval_lines=0 sensitive=0/0 dead=0 mismatches=0 canonical=49 controls_rejected=0/8 errors=3 met=False
```

---

## 2. Why the regression list reads the way it does

Rounds 47–50 all use one prose paragraph, not a table, opened by
`Regressions at \`<tip>\` (\`<receipts glob>\`, each with its \`tip=\` line):` and then
`instrument \`token line\`` pairs separated by semicolons (round 50 verbatim shape, SCORECARD.md
line 2902). Fixed properties of that shape, each of which the round-62 block must keep:

1. every receipt carries a `tip=` line, because `tools/round41-scorecard-reconcile.py`,
   `round42-selfdesc-reconcile.py` and `round43-registry-audit.py` emit it themselves while
   `gate-registry-check.py`, `digest-ledger.py`, `hexrun-census.py`, `sources-append-only.py` and
   `append-only-audit.py` do not (measured: `gate.out` has no `tip=`, `r42.out` starts
   `tip=a25dd0d9…`), so the measurement wrapper must stamp it;
2. red items are never dropped: round 47 wrote `hexrun-census unknown=1 ledger_bad=1` at the
   measured commit and `unknown=0` at the fix commit, round 50 wrote
   `hexrun-census unknown=1 (…, carried from base, documented by seat X15NoHarm2)`;
3. supersessions of prior-round counters are named with their reason (round 50: the round-49 C2
   counter reading `fixture=1 lane=0 … met=False` as an *expected* supersession);
4. the paragraph ends with the census receipt (`End census exit 0 (…: 93 W04, 1 W01, 1 ok)`).

---

## 3. Fill map (token → exact source)

| Token | Source command | Slot rule |
|---|---|---|
| `<TIP>` / `<TIP_SHORT>` | `git -C <lane> rev-parse master` | full 40-hex; never a moving ref |
| `<C1_LINE>` | `python3 tools/round62-c1-counter.py --repo <clone> --tip <TIP> --work <scratch>` | one line, key order fixed: `tool_present live_ok fake_rejected stale_rejected tamper_rejected log_rejected predead_rejected sigterm_rejected hold_rejected outside_rejected errors met` |
| `<C2_LINE>` | `python3 tools/round62-c2-counter.py --repo <clone> --tip <TIP> --work <scratch>` | key order fixed: `population rows covered bound eval_lines sensitive dead mismatches canonical controls_rejected errors met` |
| `<C1_COUNTER_SHA>` / `<C2_COUNTER_SHA>` / `<TOOL_SHA>` | `git show <TIP>:<path> \| sha256sum` | name the bytes that produced the number; see §4.1 |
| `<COUNTER_BYTES_NOTE>` | — | mandatory sentence if the graded counter is not the freeze-commit blob |
| `<R41_LINE>` | `python3 tools/round41-scorecard-reconcile.py --tip <TIP>` | verbatim line after `tip=` |
| `<R42_LINE>` | `python3 tools/round42-selfdesc-reconcile.py --tip <TIP>` | verbatim; `maxN` tracks the round number |
| `<R43_LINE>` | `python3 tools/round43-registry-audit.py --tip <TIP>` | verbatim |
| pointer | `python3 tools/planned-pointer-check.py SCORECARD.md` | `met=<B>` only |
| digest / hexrun | `… scan --repo <clone> --rev <TIP>` | the `tokens=… unknown=…` line |
| sao | `python3 tools/sources-append-only.py --from <BASE> --to <TIP>` | exit + last line |
| aoa | `python3 tools/append-only-audit.py --repo <clone> --to <TIP>` | exit + `summary … regressed=… bad_declarations=…` tail |
| selftests | `AOA --selftest --scratch <S>`, `kama-live-replay --selftest --scratch <S>`, `kama-llamacpp-live --selftest`, `tests/llamacpp-live/check-receipt.py --selftest` | last line verbatim |
| census | `bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate …` | exit + summary (fleet script; not run by this seat) |

---

## 4. Draft-time measurements (inputs for the fill, **not** the round's measurement)

All values below were produced by this seat, read-only, at the named revisions, with receipts in
`out/W04ScorecardDraft/receipts/`. They are offered so the closure can fill §1's slots and can
see which slots are already red.

### 4.1 C1 — instrument provenance is not the freeze blob

| item | value |
|---|---|
| freeze commit `6c25a77e` → `tools/round62-c1-counter.py` | blob `234341b8…`, sha256 **`275610b5…`** |
| tip `65d7cad0` (same blob) | sha256 `275610b5…` |
| post-freeze amendment `dc5e1010` onward (`a837c8f7`, `e092f2b6`, `a25dd0d9`) | blob `2ff510aa…`, sha256 **`a3498308…`** |
| running the freeze blob at tip `65d7cad0` | **crash**, exit 1, no token line: `AttributeError: 'NoneType' object has no attribute 'get'` at `grade()` line 130 (the tamper family's body-hash mismatch makes `cap()` return `None`; the fix is `(cj or {}).get(...)`) — receipt `c1-tipblob.out`; independently filed by the L1 in `measured/c1-before-fix.txt` |
| freeze blob grading the L1's own genuine receipt | `inconsistent=['unexpected-checks']` — the blob tests `'hold' in checks` while the tool emits `hold_released`, so `met=False` on a good receipt (probe with `receipts/c1_tip.py` `grade()` on `receipts/c1-fixed-receipt.json`) |
| fixed blob at tip `a25dd0d9` | `tool_present=1 live_ok=1/1 fake_rejected=2/2 stale_rejected=1/1 tamper_rejected=8/8 log_rejected=1/1 predead_rejected=1/1 sigterm_rejected=1/1 hold_rejected=1/1 outside_rejected=1/1 errors=0 met=True`, exit 0 — receipt `c1-tip-counter.out` (16/16 controls, `live_ok=1/1`) |

Consequence for the template: `<COUNTER_BYTES_NOTE>` must say which blob produced `met=True`, and
the receipt line must not read "counters the frozen bytes of `<freeze>`" — those bytes cannot
produce a token line at all.

### 4.2 C2 — the counter's own token line (L1 receipt, and what it means)

The L1's committed pre-wave receipt, at `65d7cad0`
(`.ufo/waves/round-62/measured/c2-prewave.out`, mirrored by seat E11 at 914.7 s):

```text
population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 mismatches=4 canonical=62 controls_rejected=8/8 errors=0 met=False
```

`mismatches=4` is **two failing rows, counted twice**, not four rows: `score()` adds one mismatch
for `verdict != want` and a second for `row['observed'] not in observed` when the decisive pattern
is absent (`tools/round62-c2-counter.py:228-241`). Verified with a one-row synthetic registry on
the tip blob: passing scorer → `mismatches=0`; failing scorer → `mismatches=2`. The SCORECARD
sentence must not read "four live-run mismatches".

**Independent reproduction by this seat** (committed counter blob, `--repo <lane> --tip
65d7cad0… --work <scratch>`, 906.4 s wall): byte-identical token line
`population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 mismatches=4
canonical=62 controls_rejected=8/8 errors=0 met=False`, exit 1 — receipt `c2-full-tipblob.out`.
An instrumented copy at `a25dd0d9` (same token line, same exit) names the two failing rows:

| row | computed verdict | observed output | cause |
|---|---|---|---|
| `context-capacity-receipt` | `False` | `TIMEOUT` | the row's own template waits `--host-idle-timeout 900` s while the counter's `subprocess.run(..., timeout=900)` (`round62-c2-counter.py:260`) caps the same budget — the idle wait and the harness timeout are the same 900 s, so a contended host loses the race |
| `live-ollama-lifecycle` | `False` | `{"schema": "kama-ollama-live/v2", … "setup_error": "nonce-invalid", "verdict": "SETUP_ERROR"}` | the frozen template passes `--nonce ctrun` (6 chars) but the tool's `NONCE_RE = ^[a-z0-9]{8,32}$` (`tools/kama-ollama-live.py:69,109,316`) rejects it — the row can never emit `"verdict": "MODEL_OK"`, so its recorded `verdict=true` is unreachable as frozen |

All other ten rows compute `verdict=True` with `obs_match=True` and `dead=False`; receipts
`c2-instr.out`, `ollama-row.out`.

### 4.3 C2 — sensitivity is by construction for the frozen 12 patterns

For each of the twelve frozen patterns, `pattern in MUT` is false with `MUT='__kama_mut__'`, so
`out.replace(pattern, MUT)` removes every occurrence and `sensitive` is `True` whenever the
pattern was present and `rc==0` (`tools/round62-c2-counter.py:269-271`). Measured for all 12
patterns, no exceptions. So `sensitive=12/12` demonstrates nothing about whether the check's
verdict depends on that output; it restates "pattern present, command exited 0". (Seat A05 is
right that the expression is not a universal tautology — a pattern contained in `MUT` would make
it false — but none of the frozen patterns is.)

### 4.4 C2 — two reproduced structural holes (tip blob, scratch only)

| probe | result | receipt |
|---|---|---|
| fenced canonical section: real round-62 heading + a ```` ```md ```` block holding `canonical list as of round 999` with the same 12 rows | `canonical_rows()` selects **(999, 12 rows)** — the parser is fence-blind, so "newest canonical list" can be a code sample | `c2_tip.py` probe (output in this seat's log; reproducible from `receipts/c2_tip.py`) |
| `%T` shell interpolation: `run_bound()` with `tip_tree` = `…/x; echo '45/45 selftest cases passed'; true #` | `(verdict=True, observed='45/45 selftest cases passed', sensitive=True, dead=False)` **without executing the tool** — the template is unquoted into `bash -c` (line 259-260) | same |

### 4.5 C2 — `--no-live` still executes the live legs

`main()` short-circuits the primary scoring pass under `--no-live`, but `controls()` re-scores
the eight mutated registries through `score_registry` → `run_bound`, so every bound template is
still executed once (`_EXEC_CACHE` key `(tip, cap)`). Instrumented run at `a25dd0d9`: four
`EXEC` lines within 45 s; the same command with a 120 s and with a 300 s cap both timed out
(receipts `c2-instr.out`, `c2-nolive.out`). Budget the C2 slot at ~15 min (E11 measured 914.7 s).

### 4.6 Regression slots measured by this seat

Base `a959fd90`, tip `a25dd0d9` (the tip current when these ran). `tip-*.out` receipts carry the
tool lines; `*-base.out` the base.

| slot | base `a959fd90` | tip `a25dd0d9` | classification |
|---|---|---|---|
| gate | `registered 54 unregistered 14 defective 0`, exit 1 | `registered 54 unregistered 16 defective 0`, exit 1 | **+2 introduced**: the two round-62 counters are unregistered |
| capability census | `listed 11 observed 11 missing 0 unsubstantiated 0 met True`, exit 0 | `listed 12 observed 12 missing 0 unsubstantiated 0 met True`, exit 0 | green; +1 row |
| round-41 head | `axes=6 … run_bad=1 … mismatches=1 met=False` | identical `mismatches=1 met=False` | **carried**: the coverage run fact states `36`; the committed tree holds 37 `corpus/knowledge/*.md` (engine-sides/processes excluded) |
| round-42 self-description | `r41=1 banner=0 planned=2 retired=0 saturation=0 caps=0 … province=0 … mismatches=3 maxN=61 met=False` | `r41=1 banner=1 planned=2 retired=1 saturation=1 caps=1 … province=1 … mismatches=8 maxN=62 met=False` | **+5 introduced** (banner, retired, saturation, caps, province); `planned=2` and `r41=1` carried |
| round-43 registry | `unreg=14 defect=0 … selftest=1 … spot=1 … pop=68 registered=54 mismatches=16 met=False` | `unreg=16 … pop=70 … mismatches=18 met=False` | **+2 introduced** (same unregistered counters); `selftest=1` and `spot=1` carried |
| pointer | `met=False`, dangling `§Round-53 measured results` | identical | **carried** (the `### Round-53 measured results` heading does not exist at either revision) |
| digest-ledger | `tokens=143 … unknown=3`, exit 1 | `tokens=145 … unknown=0`, exit 0 | **fixed this round** |
| hexrun-census | `tokens=2050 distinct=391 … unknown=9`, exit 1 | `tokens=2065 distinct=395 … unknown=0`, exit 0 | **fixed this round** |
| sources-append-only `--from base` | exit 0 `no append-only violations` | exit 0 `no append-only violations` | green |
| append-only-audit `--to tip` | exit 1, `commits=440 … unrestored=13 … regressed=0 … bad_declarations=5` | exit 1, `commits=446 files=118 events=159 restored=80 unrestored=16 … regressed=0 bad_declarations=5` | **+3 unrestored events**, all round-62: `a837c8f7 SCORECARD.md deleted=2 graded=2` and `corpus/lessons/round-62.md` deletions at `a837c8f7` (2) and `a25dd0d9` (5). `bad_declarations=5` carried (the contract's `declared_at` lines at `corpus/README.md:761`, `:1239`, `SKILL.md:578` do not say append-only at either revision) |
| selftests | — | `AOA_SELFTEST pass=51 fail=0`; `KLR_SELFTEST pass=48 fail=0`; `check-receipt selftest: 17 VALID and 1 NOT-EVALUATED receipts accepted; 108 mutations + unreadable case rejected`; live `selftest: ok`; `GATE_SELFTEST pass=5 fail=1`; `report-landing-audit selftest cases=79 failed=0`; `shortcut-tally` exit 0 | gate's lane-tip arm is the one failure; it is the same unregistered-counter cause |

Interpretation for the template: the regression paragraph for round 62 **cannot read all-green**.
Two of its slots are green only because this round added ledger rows (digest, hexrun), four are
red for causes this round introduced (gate, round-43, round-42 head facts, append-only unrestored),
and three are red carried from base (round-41, pointer, append-only `bad_declarations`).

### 4.7 Head facts the round-42 counter requires (repair list for the closure)

1. line 6 banner: `Latest measured round: 62` (currently 61).
2. `## Retired`: `12 capabilities` (currently 11).
3. `## Saturation`: `first-working rounds 10, 14, 16, 20, 25, 30, 41, 42, 43, 46, 47, 61`.
4. `## Capabilities` head mirror must equal the 12 canonical names (currently 11 — it lacks
   `live-ollama-lifecycle`).
5. `PROVINCE.md` must name `registry/ollama-live-claims-r61.tsv`.
6. `## Planned` must name `### Planned (round 63)` followed by a numbered item.

---

## 5. Findings (advisory, for the L1/closure)

1. **Frozen-instrument provenance.** The freeze commit's C1 counter cannot reach any verdict at
   the tip (crash in its tamper family) and rejects a genuine receipt when patched only for the
   crash (`unexpected-checks`, `'hold'` vs `hold_released`). The graded counter is a post-freeze
   amendment at `dc5e1010`. Any sentence of the form "the frozen bytes produce met=True" is
   false; name the blob sha256 and commit instead.
2. **`mismatches` semantics, and the two rows behind it.** `mismatches=4` = two failing rows × 2
   (verdict + stored observation), and the two rows are `context-capacity-receipt` (`TIMEOUT`,
   the row's 900 s idle wait racing the harness's 900 s subprocess cap) and
   `live-ollama-lifecycle` (`SETUP_ERROR` / `nonce-invalid`, `--nonce ctrun` fails the tool's
   `^[a-z0-9]{8,32}$` rule). The draft must state the row count and the causes, not the counter.
   The other ten rows compute green.
3. **Sensitivity conjunct is non-evidential for this population** (12/12 by construction, §4.3).
   `sensitive=12/12` may be quoted as a counter field but not as evidence of semantic sensitivity.
4. **Canonical-section provenance is fence-blind** (§4.4): a fenced "round 999" heading with the
   frozen 12 rows is selected as the newest canonical list, so the C2 counter's "newest canonical
   list" clause is not established by the text alone.
5. **Bound templates are shell-interpolated** (§4.4): a crafted `--work` path makes a row green
   without running its tool; a `bash -c` argv build would close it.
6. **`--no-live` is not execution-free** (§4.5); budget ~15 min for the C2 slot.
7. **In-place PENDING rewrite is now an audited loss.** The round-62 commit `a837c8f7` replaced
   the two PENDING claim rows in place; `append-only-audit` grades both lines `unrestored`
   (and the lesson corrections at `a837c8f7`/`a25dd0d9` likewise). If the block is finalized by
   append, state that the superseded rows are restored by append, or restore them verbatim in a
   fenced block (round-52 precedent), otherwise the audit keeps reading 16 unrestored.
8. **Carried reds must be repeated, not inherited silently**: round-41 `mismatches=1` (coverage
   fact 36 vs 37), pointer `met=False` (round-53 measured heading absent), append-only
   `bad_declarations=5`, gate selftest documented `pass=6 fail=0` vs run `pass=5 fail=1`,
   round-43 `spot` mismatch.
9. **One frozen bound row is unreachable by construction.** `live-ollama-lifecycle` binds
   `--nonce ctrun`, which `tools/kama-ollama-live.py:69,109,316` rejects (`^[a-z0-9]{8,32}$`), so
   the row emits `SETUP_ERROR`/`nonce-invalid` and can never match its recorded `verdict=true`.
   `context-capacity-receipt` binds `--host-idle-timeout 900`, equal to the counter's own
   `subprocess.run(..., timeout=900)` (`round62-c2-counter.py:260`), so a contended host times the
   row out. Both are template defects in `registry/capability-claims-r62.tsv`, not lane-wide
   failures: the other ten rows compute green at the tip measured here.
10. **No claim in this report is a verdict.** C2 reads `met=False` in the L1's own receipt and C1
   reads `met=True` only on post-freeze bytes; both are inputs to the closure, which owns the
   measurement and the admission decision.

---

## 6. Environment, tools, scratch

- Lane `/home/vgpnk/Projects/shokunin/kama-shokunin`; read-only git only (`rev-parse`, `show`,
  `ls-tree`, `log`, `cat-file`, `merge-base`, `archive`); no mutating git/jj anywhere; the lane
  index untouched (all tools ran read-only, `--rev`/`--tip` pinned; two counters write only into
  `<work>`).
- Scratch `/fast/scratch/hyaku/kama-r62/w/W04ScorecardDraft/` created with `mkdir -p`, passed
  explicitly as `--work`/`--scratch`/`TMPDIR`; receipts copied to
  `.ufo/waves/round-62/w1/out/W04ScorecardDraft/receipts/` (52 files) and the scratch tree removed
  after both seat-spawned jobs finished.
- Live runs executed: `tools/round62-c1-counter.py` (three times: freeze blob at `65d7cad0` →
  crash; fixed blob at `65d7cad0` → `met=True`; fixed blob at `a25dd0d9` → `met=True`);
  `tools/kama-llamacpp-live.py --selftest`; no registered consumer port contacted (the tool picks
  a free port refusing `registry/endpoint-consumers.tsv`); no process killed that this seat did
  not spawn.
- Two background jobs were allowed to finish (operator instruction) and both settled:
  `bg_27272` — the committed C2 counter on the tip blob, 906.4 s, token line reproducing the
  L1's `mismatches=4 … met=False`; `bg_27352` — the instrumented copy at `a25dd0d9`, 906.2 s,
  same token line, naming the two failing rows and their causes (§4.2).
- **Tool installs/upgrades: none.** Pacman untouched (paused host-wide); no `uv`/`npx`/binary
  install; nothing to record.

---

## 7. Tally

```text
W04ScorecardDraft template_sections=3 claim_rows=2 regression_slots=12 disclosed_limits=3 findings=10 receipts=52 base_tip=a959fd90 tip_measured=a25dd0d95ec5ca1014260466ed728e1ba3626559 installs=0
```

Report: `.ufo/waves/round-62/w1/W04ScorecardDraft.md`
Durable receipts: `.ufo/waves/round-62/w1/out/W04ScorecardDraft/receipts/`
