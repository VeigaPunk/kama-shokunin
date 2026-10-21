VERDICT: partial — one live survivors `--out` claim (SCORECARD.md:755) is superseded by an appended erratum but stays in the body; citation tooling has no `--out` claim; seven historical advice files cite `runs/c2-survivors.json` for bytes that now sit under `runs/pre-repair/`.

Scope: lane read-only, checked live at f1790e2 (three round-19 commits landed during this audit; the audit snapshot was 8bf99ca). `c2/survivors.py` was not executed. Full inventory, per-command exits and hashes: `/tmp/kama-r19-OutRemnants/out/findings.md` and `receipt.txt`. Installs: none. Ports: none. Lane files written: this report only.

## 1. `--out` claims about survivors.py

| file:line | claim | status |
|---|---|---|
| SCORECARD.md:755 | declared C2 command `survivors.py --json --out PATH` | SUPERSEDED by erratum SCORECARD.md:809-813; body unrevised |
| SCORECARD.md:782 | official argv `--json`; exclusive `--out` never clobbered | current |
| corpus/lessons/round-18.md:377-380 | "its `--out` stays exclusive"; stdout is the official document | current |
| corpus/lessons/round-18.md:404-408 | defect-3 fix: official `--json`; `--out` wording superseded | current |
| corpus/lessons/round-18.md:420-421 | official document is the stdout (cite token, verified) | current |
| corpus/lessons/round-18-verifier-spotcheck.md:140-142 | the defect as filed | SUPERSEDED by round-18.md:404-408 |
| c2/survivors.py:78 | usage synopsis `--out PATH`, unbracketed | current flag; wording only, since argparse makes it optional (:1489-1490) |
| c2/survivors.py:100, 450-453, 1533-1536, 1611-1615, 1794-1802 | docstring, exclusive create, pre-existence refusal, write failure, selftest | current (grep-observed source) |
| runs/run.py:89 | `run('c2-survivors',[…,'--json'])` | current; matches commands.json:680-696 |
| build/spec.json:39; build/dispatch.json:522; build/dispatch-95.json:642; build/spawn-result.json:119-120; build/make_spec.py:101; build/advice/C2Survivors.md:15 | build-contract CLI text `survivors.py --json --out PATH` | historical; the flag is real; reading it as the official invocation is SUPERSEDED |
| falsify/advice/C2Admission.md:37; ConnectKumitate.md:101, :120; RerunC2Self.md:12; SimplifyC2.md:33; residual/advice/ResidCounterC2.md:9-10; build/advice/C2Survivors.md:25 | scratch `--out /tmp/…` runs | current flag; scratch records |
| citation-provenance.py | no `--out` anywhere; `--help` (exit 0) lists `--registry --docs --lane --json --selftest` | nothing to supersede |

## 2. Stale round-18 artifact paths

Durable docs (SCORECARD, LOG, SKILL, corpus, registry): every cited round-18 path resolves (24/24, `test -e`, exit 0).

Stale, in historical advice and runs/:

| file:line | cites | actual state | status |
|---|---|---|---|
| falsify/advice/LessonResiduals.md:110; ReportHandoff.md:69; ReportWork.md:43; RevFCDelta.md:45; RerunC2Self.md:52; ConnectKumitate.md:34 | `runs/c2-survivors.json` as the c6dc46f exit-2 run (sha256 bd217de0…, tool 2af03fed…) | the path now holds the 04:08Z run (tool 87cad1ca…, exit 0); bd217de0… is `runs/pre-repair/c2-survivors.json` | STALE-PATH; superseded by pre-repair move (SCORECARD.md:789-790) |
| falsify/advice/ReportNumbers.md:52-55 | same argv; `commands.json:674–690` | that 22:40:05Z entry is gone; commands.json holds only the 05:11Z `c2-survivors` (:680-696) | STALE-PATH and STALE-POINTER |
| falsify/advice/ConnectKumitate.md:33, :101; residual/advice/ResidCounterC2.md:12 | "delivered tool 87cad1ca…" | live tool and official run are ac934794… | SUPERSEDED (tool identity) |
| falsify/advice/ConnectKumitate.md:85-86, :149 | "87cad1ca has no committed full run; corrected.py produced no outputs" | `runs/c2-survivors.json` and `runs/c2-survivors.stdout` are both tracked | SUPERSEDED |
| falsify/advice/ConnectTameshi.md:131; falsify/advice/FrozenManifest.md:110 | "untracked `runs/corrected.py`" | tracked and clean | SUPERSEDED |
| runs/corrected.py:12, :16-17 | writes `corrected-commands.json`, `c1-measure-corrected.json`, `c2-survivors-corrected.json` | none exist; no durable doc cites them | ORPHAN |

## 3. True in part

- SCORECARD.md:812-813; corpus/lessons/round-18.md:407-408; round-18-verifier-spotcheck.md:141-142 say `runs/c2-survivors.json` and the stdout "agree". Counts and decisions do agree: 42 runs with identical ids, zero per-run exit differences, identical `counts`. The differences are scratch paths, PIDs, timings and diagnostic tails. The two documents were produced by different tool bytes (87cad1ca vs ac934794), and the 04:08Z run has no commands.json record and no recorded argv. The sentence should say so.
- [INFERENCE] The 04:08Z run was invoked by hand. The 87cad1ca → ac934794 change matches the arm-combination repair named in the lesson. `corrected.py` never produced outputs.

## 4. Recommended for L1 (not applied)

1. SCORECARD.md:755: keep the body (append-only), or add an inline pointer to the erratum.
2. Qualify "they agree" as in §3.
3. Delete `runs/corrected.py`, or record it as an abandoned attempt.
4. Leave §2 advice as historical, or add dated pointers to `runs/pre-repair/` and `runs/c2-survivors.stdout`.
5. Bracket `[--out PATH]` in c2/survivors.py:78 at the next counter change.

Checks executed: `python3 tools/citation-provenance.py --help` exit 0; `python3 tools/citation-provenance.py` exit 0 (`required=3 found=3 verified=3 missing=0 mismatch=0`). Hashes and run-level comparisons: receipt.txt items 6-13.
