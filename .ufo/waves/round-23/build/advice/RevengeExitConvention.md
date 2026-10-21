# RevengeExitConvention — round-23 build (findings only)

Seat: `RevengeExitConvention` (revenger, leaf, read-only, no dispatch). Base: `master` `4fe9339f8fc3a4a4a479d9c938a850da12f1124d`.
Line numbers are HEAD (`git archive 4fe9339 tools` into `/tmp/kama-r23/RevengeExitConvention/head/`). The lane has an uncommitted `M tools/report-landing-audit.py` (+26/−9) that I did not write; it is cited as **WT**. No `lsp` device is in this seat's tool set, so call sites are grep/read results, not semantic references. Tags: **[obs]** = I or the L1 artifact ran it; **[struct]** = static reading only, no trigger exercised.

## 1. Where the convention came from

**0/1/2 has two lineages that share digits and conflict.**

- **Probe family** (`tools/kama-probe.sh`). Introduced in `c6199a2` (round-1, 2026-09-28) as `exit: 0 reconciled | 2 drift | 1 probe error`, with `1 probe error … — never a verdict` (`c6199a2:tools/kama-probe.sh:27,89`). HEAD keeps it at `kama-probe.sh:40-41`, `:119-120`. `SKILL.md:303,306` map `2 failed/drift; 1 could-not-evaluate/probe error`. The first lane use of `could-not-evaluate` is `e246c40` (round-5) at that row.
- **Gate family** (all other tools). `0` clean / `1` failed / `2` could-not-evaluate. The normative source is the fleet protocol, not this lane: `/home/vgpnk/Projects/shokunin/PROTOCOL.md:375-384` (`## Gate standard`, added by fleet commit `dddb4ec`, 2026-09-28): "`0` = `clean` and `1` = `failed` fleet-wide; every other code … is declared … and an undeclared nonzero code reads as `could-not-evaluate`." The lane's first gate row with this map is `3285cdf` (round-11), `SKILL.md:373` at that revision. HEAD rows: `SKILL.md:373, 430, 470, 612, 652-659, 683, 723, 767`. The lane disclaims external precedents: `corpus/SOURCES.md:64` (S052 pytest, "not the lane's numbering") and `corpus/QUALITY.md:133` (KQ24, "not pytest's").

**The families conflict.** The fleet rule pins `1` = failed (`PROTOCOL.md:380`). The probe uses `1` for error and `2` for failed/drift (`SKILL.md:303,306`; `kama-probe.sh:40-41`). A reader applying the gate table reads a probe error as a failure and drift as could-not-evaluate.

**"Errors are never verdicts" is a docstring sentence, not a QUALITY rule.** It first appears in code at `a29bb84` (round-21) as `tools/report-landing-audit.py:45` (HEAD). `EvalError` is documented at `:75-76` as "never converted into a verdict". The idea is older: `c6199a2` `kama-probe.sh:27` ("— never a verdict"). The incident chain behind it:

| round | evidence | consequence |
|---|---|---|
| 1 | `c6199a2` `kama-probe.sh:27`: exit 1 is "probe error … never a verdict" | probe-family mapping |
| 11–12 | `3285cdf` `SKILL.md:373`; fleet `PROTOCOL.md:380` | gate-family `1` = failed |
| 16 | `corpus/lessons/round-16.md:157-158`: malformed probe output "ends in a traceback (exit 1, not 2)" | — |
| 17 | `corpus/lessons/round-17.md:21-23`: uncaught `AttributeError` → traceback, exit 1, "the exit-2 promise was false" (`54a2926`); the `tools/sources-append-only.py:308` comment "a traceback would exit 1, the violation code" was added later, in round-18 (`c6dc46f`) | KQ21 `QUALITY.md:122`: "An internal fault still writes a receipt and exits 2." |
| 18 | `corpus/lessons/round-18.md:88` (M2): unobserved state classified failed | KQ24 `QUALITY.md:133` |
| 20 | `QUALITY.md:142` KQ25: "Exit1 … alone earns kill credit" rejected; `corpus/knowledge/error-is-not-a-verdict.md:14-16` "Uncaught exceptions also produced 1"; `.ufo/waves/round-20/build/advice/SrcPySysExit.md:13` observed `uncaught RuntimeError("crash") -> exit 1` on 3.14.8 | rule scoped by `error-is-not-a-verdict.md:10` to "a scoped lane measurement rule" |
| 21 | `a29bb84` `report-landing-audit.py:35,45` "Errors are never verdicts." | docstring contract |
| 22 | `.ufo/waves/round-22/report-source-fix/ReportSourceCritic.md:29-31` ("a fault must give exit 2"); KQ30 `QUALITY.md:158` (non-OSError propagation controls); KQ32 `QUALITY.md:165` (audit scope limited "until UTF-8/error hardening is demonstrated separately") | the lane already names the audit's hardening as open |

No QUALITY row states "errors are never verdicts" as a universal rule. The operative rows are gate- or helper-scoped: KQ15/KQ16 (`:49`, `:61`), KQ17 (`:72`), KQ21, KQ24, KQ25 (`:142`), KQ28 (`:151`), KQ30, KQ32.

**Base fact [obs].** An uncaught exception exits 1 on this host (Python 3.14.8): `python3 -c 'raise ValueError("probe")'` → rc 1. `sys.exit("x")` → rc 1; `sys.exit(2)` → rc 2. Exit 1 is therefore also the *failed* code of every gate in §3.

## 2. Exit map by tool (HEAD)

| tool | 0 | 1 | 2 | other | docstring exit table |
|---|---|---|---|---|---|
| `kama-probe.sh` | reconciled (`:40`) | probe error: `die` `:90`, header `:41` | drift (`:40`; `eval_rows \|\| exit_code=$?` `:887-889`) | `set -euo pipefail` `:61` | yes `:35-41`, `:119-120` |
| `citation-provenance.py` | `:346-347` | missing/mismatch/off-ref `:346-347` | unusable registry/docs/git `:330-332`, `:344-345` | argparse 2 | yes `:14`, `:19-20` |
| `report-landing-audit.py` | `:425-428` | failed `:425-427` | could-not-evaluate `:835-843` | — | yes `:42-45` |
| `sources-append-only.py` | `:350` | violation `:350` | guard fault `:302-317` | argparse 2 | yes `:33-41` |
| `error-verdict-census.py` | `:463-464` | misclassified `:463-464`; selftest `:429` | unrun/witness/IO `:453-461` | — | no (`--arm` help `:441`) |
| `gguf-identity.py` | decoded / clean `:624` | bad_magic `:235`; identity/engine mismatch `:535,:541,:544,:624` | GGUFError default `:74`; `could_not_evaluate` `:470` | 3 unreadable `:967-969` | no (`SKILL.md:657-658`) |
| `kama-llamacpp-live.py` | pass (`:17`) | fail (`:18`) | not-evaluated / setup-error (`:19`, `:155`, `:938-941`, `:1791`) | — | yes `:16-19` |
| `kama-ollama-evidence.py` | loaded_same_digest `:92` | available_not_loaded, remote_inventory, identity_conflict `:93-95`; selftest `:294` | unknown, invalid_input `:96-97` | — | yes `:16-31`, `:58-61` |
| `test-snapshot.sh` | — | FAIL `:194` | — | `set -euo pipefail` `:3` | no |

## 3. Tools whose uncaught exceptions exit 1

Python exits 1 on any escaped exception, and every row below has exit 1 as a verdict code.

| tool | verdict on 1 | escape evidence | trigger |
|---|---|---|---|
| `citation-provenance.py` | missing/mismatch/off-ref `:346-347` | **[obs]** rc 1 | deep-nested registry → `RecursionError` at `:76` |
| `report-landing-audit.py` | failed `:425-427` | **[obs]** rc 1 | non-UTF-8 git output (`git()` `:89-93`) |
| `error-verdict-census.py` | misclassified `:463-464` | [struct] | `:456` and `:451-452` |
| `sources-append-only.py` | violation `:350` | [struct] | `:319-349`, `:611-612` |
| `gguf-identity.py` | bad_magic `:235`; mismatch `:535,:541,:544,:624` | [struct] | `:955-958`, `:962-963`, `:978`, `:982-990` |

**A. `tools/citation-provenance.py` — yes [obs].**
- Catch: `main` `:327-332` catches only `(OSError, ValueError, json.JSONDecodeError)` → 2. Verdict 1 at `:346-347`; docstring `:19-20`.
- Escape: `check()` runs `json.loads` at `:76` inside that try. `RecursionError` is not in the tuple. Observed: a registry of 200,000 `[` → `RecursionError: Stack overflow … while decoding a JSON array` traceback, rc **1**.
- Also outside the try: `:322-323` `return selftest()` (selftest returns 1 at `:307`) and `:333-343` output.

**B. `tools/report-landing-audit.py` — yes [obs].**
- Catch: `main` `:835-843` catches only `EvalError` and `OSError`. Verdict 1 at `:425-428`; docstring `:42-45`.
- Escape: `git()` `:87-97` calls `subprocess.run(..., text=True)` `:89-91`. Its only handler is `except OSError` `:92-93`. A non-UTF-8 byte in git output raises `UnicodeDecodeError` inside `subprocess` and escapes. Unguarded callers: `lookup` `:114-115`; `round_commits` `:148-149`; `report_cutoff` `:166-167`; `audit_round` `:266` (its `except EvalError` `:267-269` does not catch it); `load_errata` `:339-340`.
- Guarded contrast (the authors knew): `load_source_urls` `:210-213`, `:221-224`; `read_report` `:176-177`.
- Observed: F1 (`i18n.logOutputEncoding=ISO-8859-1` + non-ASCII subject) → rc 1 `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe9`. F2 (`\xff` in committed report) → rc 1 `UnicodeDecodeError … 0xff`. Control → rc 0. Matches L1 `.ufo/waves/round-23/probe/probe-4fe9339f.stdout`.
- Structural: `selftest()` `:474-810` and `render()` `:832-833` are inside the same narrow catch.

**C. `tools/error-verdict-census.py` — yes [struct].**
- Catch `:453-455` `(OSError, CensusFault, subprocess.TimeoutExpired)` → 2, wrapping only `load_registry`, `selftest`, `census` `:448-452`.
- Escape: `:456` `emit(result, args.json)` (`:364-372`) is outside the try. Exceptions from `census()`/`selftest()` outside the tuple also escape.
- The same file's classifiers already map a traceback to `error` (`:180-181`, `:202-204`). Its own `main` does not apply that rule to itself.

**D. `tools/sources-append-only.py` — yes [struct], two paths.**
- The guard `:302-317` is `except Exception` → 2, commented "a traceback would exit 1, the violation code" (`:308`). It wraps only `git_show`/`parse_registry`/`diff_registries` `:303-307`.
- Escape 1: the output block `:319-349` (json/print) is outside the guard.
- Escape 2: `main` calls `run_selftest()` `:611-612` with no guard; `run_selftest` returns 1 on failure (`:587`).
- Docstring `:40-41` ("an internal fault also exits 2, never 1") is false for rendering faults.

**E. `tools/gguf-identity.py` — yes [struct]; no trigger found.**
- Catch `:961-969`: `GGUFError` → its `exit_code` (default 2 `:74`); `OSError` → 3. No catch-all.
- Escapes: any non-`GGUFError` from `inspect_path` `:962-963`; `run_selftest()` `:955-958`; `reconcile_receipt` `:978` (only `ReceiptError` is handled inside, `:528-529`, `:643-645`); output `:982-990`.
- Checked and guarded: receipt item types `:517-527`; `ArraySummary.as_json` `:91-92` (used at `:295`); decode guards `:158-160`; identity values are int/str only `:219-225`. Exposure is by construction; no concrete input found.

## 4. Checked and not in the list

- **`kama-llamacpp-live.py` main path.** `except BaseException` `:1611-1612`. Every `finally` sub-block is guarded (`:1618-1621`, `:1639-1658`, `:1662-1665`, `:1670-1731`). Exit `:1791`: `return exit_code if emitted else 2`. The pre-try region `:1332-1395` holds only argparse (2).
- **`kama-ollama-evidence.py` main.** `except Exception` `:517-527` → `invalid_input` = 2 (`FINDING_EXIT` `:97`). Negative control: its uncaught exceptions do not exit 1.
- **`kama-probe.sh`.** Exit 1 is its error code by design (`die` `:90`; header `:41`). Under `set -euo pipefail` (`:61`) an unguarded command exits with its own status: [obs] `bash -c 'set -euo pipefail; grep -q x /nonexistent/file'` → rc 2. The one unguarded command I found on the paths I read is `mktemp` at `:1128` (status 1). Not exhaustive. The EXIT trap (`:92-93`) does not change status.
- **`test-snapshot.sh`.** Harness; `FAIL` → 1 at `:194`. Not a verdict tool.

## 5. Caught errors that also exit 1 (deliberate; same collision)

- **`kama-ollama-evidence.py --selftest`.** An unavailable fixture → `run_selftest` `:347-351` → `selftest_payload` `:279-294` → `finding_id: selftest_failed`, `verdict_exit: 1`. [obs] Copy without `tests/`: rc 1, reasons `cases_input_unavailable`, `no_cases_executed`. Unexpected selftest exceptions → `:493-495` → same code 1.
- **`kama-llamacpp-live.py --selftest`.** Any `BaseException` → `return 1` `:1336-1344`. [struct]

## 6. Divergences (findings)

- **D1. Probe vs fleet rule.** `kama-probe.sh:40-41` and `SKILL.md:303,306` map 1 = could-not-evaluate. `PROTOCOL.md:380` fixes 1 = failed fleet-wide. [INFERENCE] the probe row conflicts with the protocol unless the protocol owner rules otherwise.
- **D2. Root cause of the collision.** `PROTOCOL.md:380` pins 1 = failed. The fallback at `:382` ("undeclared nonzero reads as could-not-evaluate") therefore cannot apply to 1. Every uncaught Python exception is a `failed` verdict under the fleet protocol unless the tool has its own catch-all. None of the five tools in §3 has one.
- **D3. Docstring vs code.** `report-landing-audit.py:45` ("Errors are never verdicts") is violated by F1/F2 [obs]. `sources-append-only.py:40-41` is violated for rendering faults [struct].
- **D4. Working-tree candidate (WT; sha1 `4b1a755c` at my last read, which moved during my run).** WT `git()` `:107-125` decodes strictly by default and raises `EvalError`; two callers pass `errors="surrogateescape"` (WT `:181`, `:418`). Replay on a read-only copy of that sha: F2 → rc 2 `could-not-evaluate: … output is not UTF-8`; F1 → rc 0, correct (no defect). WT `main` still catches only `EvalError`/`OSError` (WT `:909-915`) and has no `except Exception`/`BaseException`, so every other uncaught exception still exits 1 [struct].
- **D5. Lane already has the mitigation outside `tools/`.** `tests/llamacpp-live/install-tree-grid.py:18-22, 81-87` treats a traceback as ERROR and requires the `INVALID ` line for a rejection on exit 1. `tests/probe-verdicts/check.py:298-302, 403-404` decodes strictly and never emits a traceback. No `tools/` gate applies this to its own exit.
- **D6. Error → exit 0 path (not a verdict path).** `kama-probe.sh:341-345` `except Exception: sys.exit(0)` in `served_ids`. `MODEL_OK` requires `body_has_model_array` (`:522`, `:524`; `:407-415` fails closed), so it does not reach a verdict.
- **Out of scope, observed in L1 artifacts (not replicated):** F3 (`refs/replace` hides an omitted round commit) and F4 (fabricated full hash resolves) → rc 0 with `defects []`. F5 (promisor lazy fetch) → `MARKER CREATED`, i.e. a repo-configured command ran. Source: `.ufo/waves/round-23/probe/probe-4fe9339f.stdout`.

## 7. Evidence run

All runs used `/tmp` fixtures with `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1`. No lane or fleet repo was used as a fixture.

| # | command | observed |
|---|---|---|
| 1 | `python3 -c 'raise ValueError("probe")'`; `sys.exit("noninteger")`; `sys.exit(2)` | rc 1; rc 1; rc 2 (Python 3.14.8) |
| 2 | `bash -c 'set -euo pipefail; grep -q x /nonexistent/file; echo after'` | rc 2 |
| 3 | `citation-provenance.py --registry registry-deep.json --docs docs.md --lane <temp git repo>` (registry = 200,000 `[`) | rc 1; `RecursionError` traceback |
| 4 | `gguf-identity.py notgguf.bin` (`XXXXnot-gguf`) | rc 1; `gguf-identity: bad_magic` |
| 5 | `utf8-probe.sh <HEAD report-landing-audit.py>` | control 0; F1 1 (`UnicodeDecodeError`); F2 1 (`UnicodeDecodeError`) |
| 6 | same on a read-only copy of WT | control 0; F1 0; F2 2 (`could-not-evaluate: … not UTF-8`) |
| 7 | `kama-ollama-evidence.py --selftest` in a copy without `tests/` | rc 1; `selftest_failed` |
| 8 | `kama-ollama-evidence.py --selftest` in the lane (writes only temp dirs per `:62-63`) | rc 0; `clean`; 51/51 |
| 9 | `sources-append-only.py --selftest` | rc 0; 42/42 |

Replication script and output: `.ufo/waves/round-23/build/out/RevengeExitConvention/utf8-probe.sh` and `utf8-probe.out`.

## 8. Not verified

- Exhaustive exception enumeration. Items marked [struct] are static reads with no executed trigger.
- L1 faults F3–F6 were not replicated. I did not run `tests/` gates or `.ufo/waves/round-*` gates, which use the same 0/1/2 map; they are outside the assigned `tools/` surface.
- No install or update was performed. Tools used as found: `python3` 3.14.8, `git` 2.56.0, bash.
- The lane working tree changed during my run: `tools/report-landing-audit.py` went from sha1 `b5591fe0` to `4b1a755c`, and untracked `tests/report-audit/` appeared (not mine). I replayed only F1/F2 on the final sha and reviewed it only for D4.

## 9. Files written

- `.ufo/waves/round-23/build/advice/RevengeExitConvention.md` (this report)
- `.ufo/waves/round-23/build/out/RevengeExitConvention/utf8-probe.sh`
- `.ufo/waves/round-23/build/out/RevengeExitConvention/utf8-probe.out`
- Scratch outside the lane: `/tmp/kama-r23/RevengeExitConvention/{head,hist,fx,cand,cand2}` (snapshots, fixtures and read-only copies of WT).
No lane tracked file, index, or git state was changed. No commits, pushes or jj commands.
