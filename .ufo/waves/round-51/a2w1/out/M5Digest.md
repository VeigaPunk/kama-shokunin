# M5Digest — digest-ledger scope mutation test (round 51, build-fix 2)

**Verdict: the DISCLOSURES/selftest guard holds against every leak-direction mutant (4/4 killed by `selftest`), but a scope-cut mutant of `is_doc()` that hides 32 real digests (`scan` `tokens=132→100`) survives the selftest byte-identical green — and 5 further scope mutants are invisible to BOTH detectors on this tree; the round-51 exclusion is guarded by exactly one disarmable selftest assertion.** Coverage finding only; nothing in the lane was changed and no fix was applied in place.

## Setup

- Pristine: `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/digest-ledger.py`, sha256 `5f24e81d51a5d6fa53a6931f28bae19fb48108d46fb71e936655054b9cf49349`; identical to the build-rev copy (`git diff --stat 138af25b HEAD -- tools/digest-ledger.py` empty).
- Scratch clone: `git clone --shared <lane> $S/lane` (toplevel verified equal to `$S/lane`); all `scan` runs used it: `python3 <variant> scan --repo $S/lane --rev 138af25b963450b6520794995605fa7dbbcd87e0`.
- Working copy mutated one mutant at a time, restored to pristine bytes after **every** mutant.

## Baselines (pristine bytes)

| detector | command | exit | output |
|---|---|---|---|
| selftest | `python3 digest-ledger.py selftest` | 0 | `selftest pass=10 fail=0` |
| scan | `python3 digest-ledger.py scan --repo $S/lane --rev 138af25b…` | 0 | `tokens=132 blob=117 external_ok=8 external_absent=1 unverifiable=5 wrong_flagged=1 ledger_bad=0 wrong_unflagged=0 unknown=0` |

Independently cross-checked: union of tokens over all tracked non-`.ufo/` `.md`/`.tsv` docs minus the two excluded ledgers = 132 (`logs/token-distribution.tsv`).

## Mutant verdicts (full detail in `logs/mutant-verdicts.tsv`, diffs in `mutants/*.diff`)

| mutant | edit (target: `tools/digest-ledger.py`) | selftest | scan | verdict |
|---|---|---|---|---|
| M01 drop-disclosures-exclusion | `:80` `rel not in (LEDGER,)` | exit 1, `pass=9 fail=1` | exit 1, `tokens=298 … unknown=166` | KILLED (selftest) |
| M02 drop-ledger-exclusion | `:80` `rel not in (DISCLOSURES,)` | exit 0, identical stdout | identical | SURVIVED — **equivalent mutant** (see F3) |
| M03 exclude-registry | `:80` add `not rel.startswith("registry/")` | exit 0, identical stdout | identical | SURVIVED, inert on this tree (F4) |
| M04 tsv-blind | `:81` `.endswith(".md")` | exit 0, identical stdout | identical | SURVIVED, inert on this tree (F4) |
| M05 case-insensitive | `:80` `.lower()` compare | exit 0, identical stdout | identical | SURVIVED, inert on this tree (F4) |
| M06 disclosures-path-typo | `:73` constant → `.txt` | exit 1, `pass=9 fail=1` | exit 1, `unknown=166` | KILLED (selftest) |
| M07 ufo-typo | `:80` `.uf/` | exit 1, `pass=9 fail=1` | exit 1, `tokens=2488 … unknown=1111` | KILLED (selftest) |
| M08 prefix-boundary | `:80` startswith w/o boundary | exit 0, identical stdout | identical | SURVIVED, inert on this tree (F4) |
| M09 md-blind | `:81` `.endswith(".tsv")` | exit 1, `pass=0 fail=10` | exit 0, `tokens=1 blob=0 … external_ok=1` | KILLED (selftest) |
| M10 neuter-selftest-case+drop-exclusion | `:360` `if False and (…)` **and** M01 edit | **exit 0, stdout byte-identical** `pass=10 fail=0` | exit 1, `tokens=298 … unknown=166` | **SURVIVED-SELFTEST** (F2) |
| M11 exclude-corpus-lessons | `:80` add `not rel.startswith("corpus/lessons/")` | **exit 0, stdout byte-identical** `pass=10 fail=0` | exit 0, `tokens=100 blob=88 external_absent=0 unverifiable=3` | **SURVIVED-SELFTEST, hides real digests** (F1) |

Note the structural asymmetry the table exposes: exit code can only fire on **over**-scanning (leaks create `unknown`); **under**-scanning is always exit 0 — silence.

## Findings

**F1 — answer to the seat question: YES.** M11 (`is_doc` drops `corpus/lessons/`, `tools/digest-ledger.py:79-81`) passes `selftest` with byte-identical stdout and exit 0 while `scan` drops from `tokens=132 blob=117 external_absent=1 unverifiable=5` to `tokens=100 blob=88 external_absent=0 unverifiable=3` — 32 distinct cited digests vanish, among them the 28 digests cited *exclusively* in `corpus/lessons/` (e.g. 16 in `round-18.md`, incl. the one `external_absent` and 2 `unverifiable` classifications). Exit stays 0. The selftest fixture (`:317-363`) only pins four tokens (`good, wrong, unk, ext`) in `doc.md`; any scope cut that keeps those four visible is invisible to it. Neither frozen round-51 counter runs digest-ledger `scan`, so detection depends on someone running it ad hoc.

**F2 — the round-51 DISCLOSURES exclusion is single-point guarded.** `tools/digest-ledger.py:356-363` is the only selftest case touching it; M10 disarms it with `if False and (…)`, preserving exit 0 AND stdout (`pass=10 fail=0`) while `:80` no longer excludes the ledger. Scan alone notices (`unknown=166` — exactly the 166 disclosed line keys of the build receipt, an independent corroboration). A reviewer diffing `selftest` output sees nothing.

**F3 — equivalent mutant (dead clause).** M02: the `LEDGER` member of the `:80` tuple can never act — both scanners test `rel == LEDGER` / `path == LEDGER` before `is_doc` (`:177-180`, `:254-256`). Harmless (defense-in-depth documentation), noted for maintainability.

**F4 — latent scope cuts, inert only by redundancy.** At 138af25b exactly one token lives in a `registry/` or `.tsv` doc: `3ad0df68…` in `registry/hexrun-ledger.tsv`, cited in 6 `.md` docs besides (round-38 wrong-digest story). So M03/M04/M05/M08 change nothing measurable today (`logs/token-distribution.tsv`: 0 exclusive tokens in `registry/`, 0 in `.tsv`). The first registry/`.tsv` doc to carry an exclusive digest makes this mutant class silently uncounted by selftest.

**F5 — advisory hardening, validated but NOT applied** (`mutants/proposed-selftest-hardening.diff`): one extra selftest case asserting four scope-probe docs are scanned — `registry/other.tsv`, `table.tsv`, `registry/append-only-disclosures2.tsv` (prefix sibling), `registry/Append-Only-Disclosures.tsv` (case variant). Pristine+patch: `selftest pass=11 fail=0` exit 0. Kills M03, M04, M05, M08 (each dies naming exactly the right missing tokens — `logs/hardened-selftest-evidence.txt`). Residual: M11-class subtree cuts of real-tree prefixes are not fixture-killable; the scan delta is their only detector.

**Harness honesty note:** a first M09 construct had a SyntaxError (unbalanced paren in my replacement, not in the tool); that run's empty outputs were discarded as invalid and M09 rerun cleanly — the table reflects only the valid run. One tool install: none. No pacman, no downloads, no llama-server started (`pgrep -af llama-server` → none).

## Restoration evidence

`logs/restoration-receipt.txt`: lane source sha256 `5f24e81d…` before and after all runs (never written); scratch working copy re-written to pristine bytes after every mutant, final sha256 `5f24e81d…`, post-restore `selftest` exit 0 `pass=10 fail=0`. Scratch clone used read-only (`rev-parse`/`rev-list`/`ls-tree`/`cat-file` only). Scratch removed after writing this report.
