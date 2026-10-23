# ScoutMisroot — misroot and leftover sweep (kama r26, wave 2)

ATTACK C1 (misroot/leftover): holds — no leftover, stale counter, or stray file feeds the counted 17. Three low-severity hygiene defects and one transient, already self-corrected write-boundary violation are listed with corrections.

Scope: read-only. No server started, no counter run, no port used (no port block assigned to this seat). Nothing moved, deleted, or edited outside this report.

Method note on semantics: no LSP server applies to this question (shell/JSON/HTML sweep, not a symbol contract). Evidence below is literal file/process inspection with exact commands; every claim is a command output, not inference, unless marked [INFERENCE].

---

## 1. Fleet-repo untracked sweep (`git -C /home/vgpnk/Projects/shokunin status --porcelain`)

### 1.1 Snapshot A (first call, ~00:57 local)

```
$ git -C /home/vgpnk/Projects/shokunin status --porcelain
 M .ufo/state/chousa.report-baseline
 M .ufo/state/kagi.report-baseline
 M .ufo/state/kaidoku.report-baseline
 M .ufo/state/kake.report-baseline
 M .ufo/state/kama.report-baseline
 M .ufo/state/kengaku.report-baseline
 A .ufo/state/kotoba.report-baseline
 A .ufo/state/kotodama.report-baseline
 M .ufo/state/kumitate.report-baseline
 M .ufo/state/mado.report-baseline
 M .ufo/state/mori.report-baseline
 A .ufo/state/revenger.report-baseline
 M .ufo/state/tameshi.report-baseline
 M .ufo/state/tsukuroi.report-baseline
 M .ufo/watchdog.log
 A scripts/hyaku/__pycache__/append-closure.cpython-314.pyc
 A write
?? .omp/mcp.json
?? .ufo/reports/round-59/
?? AGENTS.md
?? bm.json
?? live_s228.html
?? nama.html
?? s395.txt
?? scripts/hyaku/__pycache__/wave-live.cpython-314.pyc
?? tf_bavelas.html
?? wb2.html
EXIT=0
```

(27 entries. `cat -A` confirms the codes are literal ` M`, ` A`, `??`; `git status --porcelain=v2` on the ` A` paths reports `.A N...` with zero index hashes = intent-to-add entries, and `git diff --cached --name-only` is empty.)

### 1.2 Content scan of every untracked path (binary-safe, `grep -aoiE 'kama|round.?26|r26'`)

| path | bytes | scan |
|---|---:|---|
| `.omp/mcp.json` | 285 | no match |
| `AGENTS.md` | 5921 | no match |
| `bm.json` | 5563 | no match |
| `live_s228.html` | 5196 | no match |
| `nama.html` | 68855 | no match |
| `s395.txt` | 0 | no match |
| `tf_bavelas.html` | 5583 | no match |
| `wb2.html` | 620 | no match |
| `scripts/hyaku/__pycache__/wave-live.cpython-314.pyc` | 10708 | no match |
| `scripts/hyaku/__pycache__/append-closure.cpython-314.pyc` | 10738 | no match |
| `write` | 25 | no match (content: `agent://U100N079H334f935b`) |
| `.ufo/state/kotoba.report-baseline` / `kotodama` / `revenger` | 68 each | no match |
| `.ufo/waves/round-26/w2-falsify/advice/AttackE2616.md` | 10654 | **match: kama x2, Kama x1, r26 x5, round 26 x1, round-26 x6** |

Only one fleet-root untracked file names kama/round 26 — see §4.1.

### 1.3 Snapshot B (final call, 01:02): the stray r26 file is gone

```
$ ls /home/vgpnk/Projects/shokunin/.ufo/waves/round-26/w2-falsify/advice/
ls: cannot access '.../w2-falsify/advice/': No such file or directory
$ git -C /home/vgpnk/Projects/shokunin status --porcelain=v1 -uall | wc -l
26
$ ... | grep -c '^??'
14
```

The fleet-root `.ufo/waves/round-26/` tree contained exactly one file and was empty of tracked content (`git ls-files .ufo/waves` shows no `round-26` path). No kama/round-26 stray survives in the fleet repo at 01:02.

## 2. `/tmp` files written today naming kama-r26

```
$ find /tmp \( -name '*kama*' -o -name '*r26*' \) -newermt '2026-10-23 00:00:00' \
    -printf '%TY-%Tm-%Td %TH:%TM %8s %y %p\n' | sort
2026-10-23 00:17      316 f /tmp/a2-guards-6zk1ioc8/fx/.ufo/waves/round-20/w2/AdvRecallShapes/fixtures/ar26-atexit-register.jsonl
2026-10-23 00:22    17692 f /tmp/kama-r26-frozen.py
2026-10-23 00:59      316 f /tmp/r24scratch/a2-guards-1kpsdq25/fx/.ufo/waves/round-20/w2/AdvRecallShapes/fixtures/ar26-atexit-register.jsonl
TODAY_COUNT=3
ALL_COUNT=834
```

Only `/tmp/kama-r26-frozen.py` names kama-r26 (the other two are copied round-20/round-24 fixture trees whose names happen to contain `r26`-like tokens). No `/tmp/kama-r26-c1-*` junk dirs remain (the counter's own `junk.gguf` TMPDIRs are cleaned). No process holds the file open:

```
$ lsof /tmp/kama-r26-frozen.py ; echo $?
(no output) 1
```

Its identity is the **A0** counter revision, not the frozen A1 predicate:

```
$ sha256sum /tmp/kama-r26-frozen.py
f800865d8a99187b84bce9e5ff27c1f4bc40e748ad3bffec5c0ca4e9d543ba96  /tmp/kama-r26-frozen.py
$ sha256sum kama-shokunin/.ufo/waves/round-26/count-c1.py
6501737c749926be9d6b37761175d76f89876976c46bd5951fc1a3520c796588  ...
$ diff /tmp/kama-r26-frozen.py .../count-c1.py   # exit 1
19,20c19,21   (docstring: baseline clause reworded)
245a247,253   (missing: --help/--version informational baseline run)
248a257,260   (missing: squash() whitespace normaliser)
373c385,386   (missing: squash(sig) not in squash(baseline))
```

## 3. llama-server on 476xx/477xx

```
$ ss -ltn | grep -E ':(476[0-9][0-9]|477[0-9][0-9])\b' ; echo "SS_EXIT=$?"
SS_EXIT=1                      # no listener in the block
$ pgrep -af llama-server ; echo "PGREP_EXIT=$?"
PGREP_EXIT=1                   # no process
$ ls -l /proc/*/exe 2>/dev/null | grep -i llama ; echo $?
1                              # no running exe image
$ ss -tanp | grep -E ':(476|477)[0-9][0-9]\b'
TIME-WAIT 127.0.0.1:47740 <-> 127.0.0.1:37000/37016/37018/37020/37034/37038/37046/37064/37068/36986
TIME-WAIT 127.0.0.1:47570 <-> 127.0.0.1:47732
TIME-WAIT 127.0.0.1:47570 <-> 127.0.0.1:47722
TIME-WAIT 192.168.0.253:47764 -> 3.174.59.73:443   (ephemeral client port, unrelated)
```

No leftover server: 13 TIME-WAIT tuples are closed-connection residue from wave-2 runs on 47570/47740, with no LISTEN or ESTABLISHED socket and no owning process. Port block is clean and reusable.

## 4. Defects and smallest corrections

### 4.1 (transient, self-corrected) A lane advice report was written into the fleet repo

Observed at 00:59–01:00: `/home/vgpnk/Projects/shokunin/.ufo/waves/round-26/w2-falsify/advice/AttackE2616.md`, 10654 B, untracked, content `ATTACK E26-16: partial ...`. That directory existed only for this file: `find .ufo/waves/round-26 -printf ...` printed the file plus three synthetic directories, all mtime 01:00.

Resolved by the owner: at 01:01:28 the lane copy appeared (`.ufo/waves/round-26/w2-falsify/advice/AttackE2616.md`, 11175 B, sha256 `fac24d4b…`), and the fleet-root copy is gone (§1.3). The lane file is larger, so it is a rewrite, not a move.

Cause [INFERENCE, supported by the path shape]: the seat's `Report:` trailer is lane-relative and was resolved against cwd `/home/vgpnk/Projects/shokunin`.

Smallest correction (dispatcher): write every `Report:` path absolute under `/home/vgpnk/Projects/shokunin/kama-shokunin/`, and add one close-out check — `test ! -d /home/vgpnk/Projects/shokunin/.ufo/waves/round-26` — so a recurrence fails the wave instead of silently landing.

### 4.2 A stale A0 counter copy sits in `/tmp` under a "frozen" name

`/tmp/kama-r26-frozen.py` (17692 B, 00:22, sha `f800865d…`) is the pre-A1 counter. Its name advertises the opposite of its content, and it is executable-by-invocation from anywhere, outside both the flock and the `git archive` extract the contract requires.

Smallest correction: rename to `/tmp/kama-r26-A0-superseded.py` or delete it; if any seat wants the A0 bytes later, the authoritative copies already exist at `/fast/scratch/hyaku/kama-r26/before/.ufo/waves/round-26/count-c1.py` and in the `ctl/*/tree` extracts.

### 4.3 A0-labelled control directories call their measured counter "frozen"

`controls/KamaR26CtlAllFalse/REPORT.md:1` — `CONTROL KamaR26CtlAllFalse: counted 12 of 14 (frozen counter) -- BREAKS`, and its own restoration table pins the measured counter at `f800865d…`. Same for `controls/KamaR26CtlCounterMutants/REPORT.md:1` (`holds`) with `setup-commands.json` reading the lane counter as `f800865d…` at 00:35 and `restoration.json` asserting `lane_frozen_counter_sha256_after: 6501737c…` in the same receipt.

This is **not** a claim defect, and I am not reporting it as one:
- The AllFalse break is correctly attributed to A0 at `corpus/lessons/round-26.md:74` and in `preregistration.json:30` (`pre_data_amendment_A1`), with an explicit A1 re-score: `controls/A1-rescore/invalid-flag-usage-A1.out` = `registered 14 counted 0 … not-counted ['HT01:f_absent_from_baseline', …] exit=0`.
- `CounterMutants` and `Shortcut` both carry `HELD.md` (`HELD — not evidence.` provider refusal `code=cyber_policy`).
- The landed numbers were produced by A1, not A0: `/fast/scratch/hyaku/kama-r26/tip-7e5ff…/.ufo/waves/round-26/count-c1.py` = `6501737c…`, and `final/tip-counter-sha.txt` = `6501737c…`. All wave-2 extracts I enumerated also hash `6501737c…` (40 copies), while the 11 A0 copies are confined to `kama-r26/before` and `kama-r26/ctl/*/tree`.

Residual risk is only a reader citing the first line of a `HELD` directory as evidence. Smallest correction: prefix those two `REPORT.md` files with their `HELD` line, and add `measured counter f800865d (A0, superseded by A1)` to the AllFalse first line.

### 4.4 A control receipt records a live llama-server as a passing final check

`controls/KamaR26CtlCounterMutants/restoration.json` → `final_process_check`:

```
"command": ["pgrep","-af","llama-server"], "exit_code": 0,
"stdout": "3778099 timeout 120 ... --port 47654 -t 2\n3778102 .../llama-server ... --port 47654 -t 2\n"
```

`pgrep` exit 0 means *found*: a server was alive when the control closed, and the receipt files it as the final check rather than a failure. (Those pids are long gone; today's sweep finds none.) Smallest correction: treat any non-empty `pgrep` output as failure and require exit 1 before writing the receipt.

### 4.5 Fleet-repo noise, listed only (read-only, not touched)

`??` at fleet root: `.omp/mcp.json`, `AGENTS.md`, `bm.json`, `live_s228.html`, `nama.html`, `s395.txt` (0 B), `tf_bavelas.html`, `wb2.html`, `write` (25 B containing `agent://U100N079H334f935b` — a botched agent write), plus two `scripts/hyaku/__pycache__/*.pyc` and three `.ufo/state/*.report-baseline` intent-to-add entries. None names kama or round 26. The intent-to-add entries and `.ufo/state/*.report-baseline` churn between snapshots (A → `??`; `.ufo/reports/round-59/` was untracked at 00:57 and committed by 01:02), i.e. live peers are rewriting the fleet index while I read; HEAD moved to `0c2ad838 hyaku phase-4: directive 31 resume dispatch` (00:52:34) mid-sweep.

### 4.6 Lane-side ignored artifact (informational)

`.ufo/waves/round-26/__pycache__/count-c1.cpython-314.pyc`, 32727 B, mtime 00:59; header `srctime 2026-10-23 00:32:30`, `srcsize 18372` — i.e. compiled from the A1 counter in place in the lane, during wave 2, not from an extract. Ignored by `.gitignore:3` (`__pycache__/`), so it is not repo dirt; `git ls-files` shows it untracked/ignored. No action needed beyond awareness that at least one wave-2 seat loaded the counter from the lane path [INFERENCE: which seat, from mtime only].

## 5. Remaining unknowns

- Which seat produced `/tmp/kama-r26-frozen.py` at 00:22 is not recorded anywhere I could read (no owner field, no lane reference to that path).
- Whether the fleet-root `AttackE2616.md` was deleted or moved by its owner vs. another process cannot be distinguished from mtime alone; the lane copy differs in size, so it is not a move.
- `.ufo/state/*.report-baseline` and index churn belongs to live non-kama lanes; I did not attribute it.

## 6. Files written

- `.ufo/waves/round-26/w2-falsify/advice/ScoutMisroot.md` (this report)

No scratch directory was created; no tool was installed or updated; no server started; no port bound; no repo or index mutation.
