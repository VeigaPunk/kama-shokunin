VERDICT: partial — four of the five stale classes are corrected by appended supersession, but `SKILL.md:576` still says the append-only selftest has 14 cases (measured 42), `SKILL.md:574` still gives the old gate selftest counts, and `PROVINCE.md:73` still says the tool "now emits" v2.

# StaleDocs — sweep of current-tense docs for v2 / no-503-fails / BaseException-escapes / 14-case-selftest / Python3 path

Read-only scout at pushed lane master `1c325b2e58fcfdc6761f645b44cedfb1d65243e6`,
separate clone `/tmp/kama-r18-falsify-StaleDocs` (`rev-parse HEAD` = that hash,
`git status --porcelain` empty). No experiment was named in the item, so none was
executed: every behavioural statement below is a code read or a read of the
official raw runs under `.ufo/waves/round-18/runs/`, never a fresh run. No installs,
no upgrades, no listener, no port bound; `pgrep -af kama-r18-falsify-StaleDocs`
returned no process after the reads.

Files quoted (sha256 of the clone bytes):

```
c82fbbff52ad8f4a97f0eb1297e3ec3b91c16f171ae977cff46228139e498a36  SKILL.md
1b4dd89c6bca8c1f0adb1df492a2d603343700136f8c8c5b18138f13e67cd293  PROVINCE.md
665b1fd8e8b01895f7c3d18990f01d8e53c4130478a54adac8d62821e43b0055  SCORECARD.md
01a6818bf0e04a5890e1c91b4b9a77b713f89bc625a1fb20ed1a8d01e3a2cedf  corpus/README.md
54ae1d65f2629ed1df63136701c3c1ea5ebcdce9598cb2f3a6fb83bdfc160c1c  corpus/knowledge/llamacpp-loading-lifecycle.md
8eb5e414398f31b895d5fc806fb0dc67af537b9f6fb6a309a5225d243e972955  corpus/QUALITY.md
1ff9e2f363baedc09ae913c2036d79b53dcd270c851419ef33b8dc337a6d3fb5  SHONEN.md
dc036d7dcfe2933827c07f8bc0dedba68a24f7b099309871f6cb25ccb811a04b  tools/kama-llamacpp-live.py
4d7868564226b6caa5957e9d7f4f8910a1c459ec26462a52d42e802be6079c2d  tools/sources-append-only.py
c5715641f34fb9bffaf33ca3e0391dd5485a0a914462bf6540e519b566c78335  tests/llamacpp-live/check-receipt.py
e74918130d839a79a0d620dda9bfdac5faaced6762e78fbfe415d270ad729770  runs/append-only-selftest.stdout
da22d995d478ac6cf941e944e70cf365bb3507606e54664d9cf5c1a4391aca8f  runs/gate-selftest.stdout
4ec682e1b6a7790e59da608a15527640c018dd70b2a08cf634e0986a00d3d9d6  runs/tool-selftest.stdout
```

Scope of "current-tense docs": `SKILL.md`, `PROVINCE.md`, `corpus/README.md`,
`corpus/knowledge/*.md`, `corpus/QUALITY.md`, the current sections of
`SCORECARD.md`, `SHONEN.md`, `AGENTS.md`, `MINT.md`, and the current
tool/gate/controls docstrings and comments. Lessons and `LOG.md` entries are
dated records; they were read only to test whether an appended supersession
reaches the live statement. `.ufo/waves/round-1..17` frozen artifacts and the
nine probe matrix JSONs were not touched.

## A. Uncorrected live statements (the deliverable)

1. **`SKILL.md:576` — append-only selftest is stated as 14 cases; it is 42.**
   Row text: "`--selftest` 14 cases". The same command is described at
   `SKILL.md:612` as "42 selftest cases including immutable opened/kind/tier/scope
   and post-blank rows". Official raw run
   `runs/append-only-selftest.stdout` ends `42/42 selftest cases passed`
   (exit 0, hash above). The build seat itself routed this:
   `.ufo/waves/round-18/build/advice/C2AppendOnly.md:83` — "**Docs to refresh.**
   `SKILL.md:576` says \"`--selftest` 14 cases\". It is now 42 (39 cases + 3 checks).
   L1 or the ScribeSkillRound18 draft needs to update it." The delivered
   `SKILL.md:603` marks only "the round-17 v2 rows" historical; this row is the
   input-registry guard row, not a v2 receipt row, and it carries no supersession
   marker. A reader has two live counts for one command with no marker saying
   which is current.
2. **`SKILL.md:574` — gate selftest counts are the round-17 numbers and have no
   replacement.** Row text: "`--selftest`: 26 v1 + 13 v2 mutations rejected, 2
   valid receipts accepted". Official `runs/gate-selftest.stdout` (exit 0):
   "selftest: 5 VALID and 1 NOT-EVALUATED receipts accepted; 61 mutations +
   unreadable case rejected". The current gate row at `SKILL.md:610` gives no
   count, so the only quantified claim is stale and the current number is not
   resolvable from the docs. (`SKILL.md:603`'s "round-17 v2 rows" may cover this
   row's status, but it cannot supply the replacement count.)
3. **`PROVINCE.md:73` — present-tense wrong schema.** "tool now emits
   `kama-llamacpp-live/v2`". The later Round-18 note (`:82-89`) is headed "v3 and
   listener ownership" and says "V3 distinguishes…", but never says the tool now
   emits v3 and never names the v2 sentence as superseded. The clause is false as
   a current statement and is resolvable only by section-order inference.
   (Contrast `SKILL.md:565` "the tool now emits v2", which *is* explicitly
   resolved by `SKILL.md:603-604`: "Current lifecycle output is
   `kama-llamacpp-live/v3`.")
4. **Scope gap, not a false statement — `PROVINCE.md:89` and `corpus/QUALITY.md:122`
   state guaranteed containment.** `PROVINCE.md:89`: "Internal BaseException
   faults are contained into setup-error receipts". `corpus/QUALITY.md:122` (KQ21):
   "An internal fault still writes a receipt and exits 2." The delivered tool does
   contain such faults inside the guarded region (see C), but two unguarded
   windows remain (`tools/kama-llamacpp-live.py`):
   - the 46-line receipt-construction block `1148-1186` runs before `try:` at
     `1194`; `KeyboardInterrupt`/`SystemExit` raised there escape with no receipt
     (the tool's own handlers are installed later, inside the `try`);
   - statements inside the `finally:` that are outside any inner `try`
     (`:1404`, `:1460`, `:1462`, `:1527`, `:1565`) can raise the handler's
     `Terminated` (`class Terminated(Exception)`, `:162`) and leave `main`
     without the receipt the block already built.
   This is `[INFERENCE]` from code reading; no reproduction was run and no
   bounded experiment was assigned. `corpus/knowledge/llamacpp-loading-lifecycle.md:255-257`
   already states the correct scope ("Internal faults produce setup-error receipts
   and exit 2 where output remains writable"), and `SKILL.md:610` states "an
   unwritable output cannot promise a receipt file"; `PROVINCE.md:89` and KQ21 do
   not carry that qualifier.

Nothing else in the five classes is uncorrected. The next two sections enumerate
the sites that *are* corrected so L1 can stop re-checking them.

## B. v2 presented as current — resolved sites

| Site | Statement | Resolver (append/section) | Status |
|---|---|---|---|
| `SKILL.md:565` | "the tool now emits `kama-llamacpp-live/v2` with 11 checks" | `SKILL.md:603-604` "Current lifecycle output is `kama-llamacpp-live/v3`" | resolved (explicit) |
| `SKILL.md:573` | v2 row: exit 3 digest mismatch; "none observed fails" | `SKILL.md:609-610` v3 row: 0/1/2 incl. digest refusal; `:604` zero observation not-evaluated | resolved (v2 row marked historical) |
| `corpus/knowledge/llamacpp-loading-lifecycle.md:194` | "v1 limits … superseded for receipt v2" | `:239-242` "Receipt `kama-llamacpp-live/v3` retains … adds `evaluated`"; `:246-247` v3 schema floor | resolved |
| `corpus/README.md:238`, `:242` | round-17 coverage row; "receipt v2 grades every observed loading 503 body … fails a run that observed none" | `:255-257` "The v2 rule above … is historical. V3 makes zero … not-evaluated" | resolved |
| `SCORECARD.md:666`, `:694` | round-17 rows: "receipt v2 checks fail…"; "evidence pointer is now receipt v2" | `SCORECARD.md:744` round-18 C1 "receipt v3 separates no loading observation…" | resolved (dated section) |
| `SHONEN.md:8`, `LOG.md:1013` | "Round 17 adds graded v2 receipts" / "receipt v2" | dated assertions/log entries, not contract text | historical, not a live contract |
| `tools/kama-llamacpp-live.py:50` | `SCHEMA = 'kama-llamacpp-live/v3'` | — | current |
| `tests/llamacpp-live/check-receipt.py:2`, `:47`, `:2053` | gate accepts v1/v2/v3; `RECEIPT_SCHEMA_V3`; description | — | current |

`PROVINCE.md:73` is the one v2 site that does not meet the appended-supersession
bar (finding A3).

## C. "No loading 503 observed ⇒ fail" — fully resolved

| Site | Old statement | Resolver | Status |
|---|---|---|---|
| `SKILL.md:573` | "`loading_envelope_graded` … none observed fails" | `SKILL.md:604-605` "Zero loading observations no longer fail a healthy run; they remain non-accepted as NOT-EVALUATED"; `:609` "Only loading-envelope grading may be null … `no-loading-503-observed`" | resolved |
| `corpus/README.md:243` | "fails a run that observed none" | `:255-257` "V3 makes zero observed loading 503s not-evaluated (tool 2; gate 3…)" | resolved |
| `corpus/knowledge/llamacpp-loading-lifecycle.md:198` | "fails when no 503 was observed" | `:243` "the old … rule no longer describes current code"; `:239-242` tri-state | resolved |
| `corpus/knowledge/llamacpp-loading-lifecycle.md:226` | "1 of 60 real runs … observed no 503 and failed" | kept as a v2 observation; `:243-247` reclassifies the rule, not the record | historical, consistent |
| `SCORECARD.md:726-727` | round-17 falsify "1 of 60 … failed" | dated round-17 falsify block | historical |

Code and official evidence agree with the corrected docs:

- `tools/kama-llamacpp-live.py:136-152` `documented_by` now says "no `/v1/models`
  503 observed -> not evaluated with `{\"loading_observed\": false}`";
  `:1502-1513` builds `_check('loading_envelope_graded', None if not
  loading_observed else ...)` with reason `no-loading-503-observed`, and
  `_outcome_exit` (`:873-885`) returns fail/1 only when some check is `False`.
- `tests/llamacpp-live/check-receipt.py:1177+` has the separate v3 null branch;
  `:1871` selftest case `v3-no-loading-not-evaluated` expects exit 3; the v2-only
  `bad("… nothing graded")` at `:1148` is guarded by `if is_v2 and not is_v3`
  (`:1142`), so it no longer reaches a v3 receipt.
- `tests/llamacpp-live/controls.py:23` k16 is a "GOOD zero-loading server (never
  503): expected not-evaluated"; `:134` "k16 alone never answers 503".
- Official `runs/gate-selftest.stdout`: "5 VALID and 1 NOT-EVALUATED receipts
  accepted"; `runs/live-gate-1.exit` = 0 and `runs/live-1.exit` = 0.

## D. BaseException escape claims — one still true, containment bounded

- `SKILL.md:593` ("exit 1 can also come from a model rehash `OSError`, and a
  `BaseException` (e.g. KeyboardInterrupt) can escape without a receipt") is
  **still true** in the delivered tree: `parser.error`/`--help` exits via
  `SystemExit` before the receipt exists, the receipt-construction window
  `1148-1193` is outside `try:`, and `--out` write failure can leave no file.
  The rehash clause also still holds: `model_sha256_post` becomes
  `rehash-error:…` and `model_unchanged` then fails → exit 1
  (`tools/kama-llamacpp-live.py:1514-1522`, `_outcome_exit`).
- The delivered containment is real for the tested path: `:1137` guards the
  selftest, `:1401` guards the body, and every teardown/epilogue operation has
  its own `except BaseException` (`:1407-1586`). Control k18 injects
  `KeyboardInterrupt` into teardown and requires "receipt + exit 2"
  (`tests/llamacpp-live/controls.py:649-656`); the gate has
  `v3-internal-fault-not-mirrored` (`check-receipt.py:1913`). Official
  `runs/controls-selftest.stdout`: "selftest: 70 cases, 0 failure(s)".
- Therefore the docs are consistent on the tested path; the only defect is the
  unscoped normative sentence (finding A4), which no append currently scopes.

## E. Python3 path — no uncorrected site

- `tools/kama-llamacpp-live.py:59-61` now cites
  `https://docs.python.org/3.14/library/subprocess.html#subprocess.Popen.returncode`.
  `POPEN_RETURNCODE_DOC` is the only docs.python.org URL in the tool.
- All three round-18 own-work receipts embed the same `/3.14/` URL in
  `teardown_graceful.documented_by` (checked in
  `.ufo/waves/round-18/live/receipt-{1,2,3}.json`).
- No current-tense doc contains `docs.python.org/3/`; the remaining `/3/`
  mentions are `corpus/SOURCES.md:56` (which records that `/3/` serves 3.15) and
  the round-17 verifier spot-check, which *rejects* `/3/`.
- `corpus/SOURCES.md:63` (S051) cites `docs.python.org/3.14/builtins/exceptions.html`.
- The documented `python3` command resolves to the measured interpreter:
  `python3 -V` → `Python 3.14.8`, `/usr/bin/python3` → `/usr/bin/python3.14`;
  `runs/commands.json` records every command as `/usr/bin/python3` and
  `python` = `3.14.8 (main, Oct 2 2026…)`.

## F. Adjacent uncorrected docs found by the same sweep (outside the five classes)

1. **`SKILL.md:572` mutant-grid self-test cell says "`--selftest`, `--dry-run`".**
   A bare `--dry-run` is refused: `.ufo/waves/round-17/c1/mutants.py:1306`
   defines the flag, `:1325` prints `error: --check (or --grid) is required`.
   `ScribeSkillRound18.md` §Corrections already listed this row for repair
   ("It needs `--check PATH`"), and the delivered `SKILL.md` append omits it.
2. **`SCORECARD.md:767` (EOF) is an unfulfilled promise.** "Measured results,
   measured commit and exact commands are appended after execution." The file is
   767 lines and has no round-18 measured-results subsection; the numbers live in
   `corpus/lessons/round-18.md` and `LOG.md:1086-1090`.
3. **`SHONEN.md:8` has no round-18 assertion.** Its live-task evidence ends at
   "Round 17 adds graded v2 receipts … `tests/llamacpp-live/controls.py` (8 bad
   fake-server shapes rejected…)". The delivered controls are k0–k22
   (`controls.py:17-27`) and the receipts are v3. This is an omission, not a
   false sentence.
4. **`LOG.md:1093/1096` claims counter selftest "38/38" and "60/60" "in owner
   clone"; the committed runs are 36/36 and 57/57.** Official
   `runs/c1-counter-selftest.stdout` = "selftest: 36/36 cases passed" and
   `runs/c2-counter-selftest.stdout` = "selftest: 57/57 checks passed", both at
   measured commit `c6dc46f`. No committed artifact at `1c325b2` carries 38 or
   60. This is the same "number without its artifact" class; it belongs to the
   counting/provenance seats, not to this sweep's five classes.

## Limits

- No execution. The item named no bounded experiment, so no runtime/gate check was
  run even in the clone; all runtime facts are quoted from the committed raw runs.
  The `[INFERENCE]` window in D is a code-read, not a reproduction.
- The five-class distinction (historical vs current) was decided by section order
  and by whether a later text states the replacement truth. Where the replacement
  is a number (A1/A2) the doc is called uncorrected even though the count can be
  cross-read; that is the stricter reading demanded by "resolvable appended
  supersession".
- Not re-audited here: the probe/`kama-probe/v2` schema (genuinely v2, unchanged),
  the nine matrix JSONs, the registry census, and the `.ufo/waves/round-18/build`
  drafts except where cited as routing evidence.
- No installs or upgrades. No lane write except this report.

Report: .ufo/waves/round-18/falsify/advice/StaleDocs.md
