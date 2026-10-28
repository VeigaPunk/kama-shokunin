# RV06Hygiene — round 63, kama (operability + calibration), review of build at tip 03a6a1d850902a66a13dfad33f89cf3a8b759a09

Seat: RV06Hygiene (leaf, advisory). Lane HEAD = tip (verified). Scratch: /fast/scratch/hyaku/kama-r63/w/RV06Hygiene (clone `--shared` of the lane; all runs at tip were against the clone's committed tree or `git show` blobs; C1 was pointed at the lane repo read-only). No commit, no lane edit, no lane-source touch. No tools installed (ruff 0.17.2 at ~/.local/bin was already present and only used). Evidence copied to `.ufo/waves/round-63/w1/out/RV06Hygiene/`.

## Summary

| item | verdict | one line |
|---|---|---|
| (a) hardcoded /tmp, mkdtemp w/o dir=, writes outside --work | PASS, with 2 caveats | No /tmp, no mkdtemp in the changed tools; counters write only under --work; C1 does not pin TMPDIR for children (C2 does). Pre-existing mkstemp/mkdtemp without dir= live in dependencies, off the v2 path. |
| (b) py_compile, three tools (+ two dependents) | PASS 6/6 | `-W error`, all compile at tip. |
| (c1) kama-llamacpp-live.py --selftest | PASS | rc=0, selftest ok. |
| (c2) kama-live-replay.py --selftest --scratch | PASS | KLR_SELFTEST pass=48 fail=0. |
| (c3) instrument-agreement.py --selftest | PASS | IA_SELFTEST pass=4 fail=0. |
| (c4) kama-completion-live.py selftest | N/A | No `--selftest` flag exists at tip; exercised only via the counters (see c5/c6). |
| (c5) round63-c1-counter.py at tip | PASS | met=True. |
| (c6) round63-c2-counter.py at tip | FAIL (met=False) — expected by freeze, see below | Only `selfdesc_mismatches=8` (frozen at 8 on purpose) and `host_busy=1` (legitimate context-capacity alternative) stop met. |
| (c7) round62-c1-counter.py (completion-tool importer) | REGRESSED at tip | met=True at base 7ee8cbdf; met=False at tip because the v2 receipt carries checks the frozen v1 counter does not know. |
| (c8) round62-c2-counter.py | non-green at base AND tip | Pre-existing (round-62 honest stop); mismatches 6 → 4 between base and tip, not caused by the v2 completion tool (it does not run it). |
| (d) .gitignore / untracked state | PASS with flags | Ignores are sane; one stray nested file at lane root; three tracked files modified outside the tip; wave evidence untracked as expected. |

## (a) Scratch discipline — grep at tip

Command: `grep -nE '/tmp|mkdtemp|mkstemp|TemporaryDirectory|tempfile|TMPDIR|gettempdir|/home/|/fast/'` over the completion tool, both r63 counters, and the two dependents (full output: out/RV06Hygiene/a-grep.txt).

- `tools/kama-completion-live.py` (v2 changed): zero `/tmp`. Writes are only: `--work/server.log` (line ~281-284, `os.makedirs(work)` + `open(log_path,'wb')`), `--hold-dir` (caller-supplied; `hold.json` line 490), and `--out` (caller-supplied, line 610). The `import tempfile` at line 55 is never used (see flag F1). `DEFAULT_MODEL` is `~/.cache/kama-shokunin/models/stories260K.gguf` (read-only input; unchanged from v1).
- `tools/round63-c1-counter.py` (new): every write is under `work`: `work/tip/tools/*` and `work/tip/registry/*` (tip blobs), `work/hold/` (hold.json, release), `work/tool-work/` (the tool's `--work`), `work/receipt.json`, `work/decoy-model.bin`. No tempfile, no /tmp. Witness/fake servers are loopback only.
- `tools/round63-c2-counter.py` (new): `checkout_tip` extracts under `work/tip`; `scratch = work/run`; child env sets `TMPDIR=scratch` explicitly (line 505). No tempfile. Reads `~/.cache/...` model (read-only). `pgrep -x llama-server` is a read-only host probe.
- Dependency `tools/kama-llamacpp-live.py` (unchanged since round 54; `git diff 7ee8cbdf 03a6a1d8 -- tools/kama-llamacpp-live.py` is empty): `main()` line 2209 `tempfile.mkstemp(prefix='kama-llamacpp-live-', suffix='.log')` has **no `dir=`** and lands in TMPDIR (or /tmp). `_emit` line 1979 does pass `dir=`. The v2 completion tool calls only `http_get`, `pick_port`, `prepare_witness_dir`, `hold_for_witness`, `_OPENER`, `_preexec_pdeathsig`, `_FORKED_PPID`, `refused_ports`, `port_owned_by`, `_listen_inodes`, `sha`, `_utc_now`, `SetupError` — none of which reach the no-`dir=` mkstemp. Pre-existing; not a v2 regression.
- `tools/instrument-agreement.py` (unchanged): selftest `tempfile.mkdtemp(prefix="ia-selftest-")` with no `dir=` (line 81). Pre-existing.
- `tools/kama-live-replay.py` (unchanged): `--scratch` defaults to `tempfile.gettempdir()` when omitted (line 917). I always passed `--scratch`.
- Host-specific absolute paths in registry: `registry/capability-claims-r63.tsv` row `live-llamacpp-lifecycle` embeds `--model /home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf` in its run template (read input only; a portability note, not a write).

Empirical check (not just grep): every run below had `TMPDIR` pinned to a scratch dir I then inspected.
- `tmp-c1/` after the C1 counter run: empty.
- `tmp-c2/` after the C2 counter run: empty.
- `tmp/` after the three selftests: empty (instrument-agreement's mkdtemp landed there and was cleaned up).
- `/tmp` scan for entries newer than my first run with names `ia-selftest-*`, `kama-*`, `.kama-*`, `r63*`: none.

Caveats (not failures):
- **C1 does not pin TMPDIR for its tool children**; C2 does (`env['TMPDIR']=scratch`). The C1 children inherit the operator's TMPDIR; the completion tool's child-env allow-list drops TMPDIR before llama-server starts, and nothing in the C1 path reaches a no-`dir=` mkstemp, so no write escapes in practice. Still a discipline gap against "counters must honour --work and TMPDIR" — recommend `env['TMPDIR']=work` in C1's witness Popen, as C2 does.
- Pre-existing no-`dir=` tempfile calls exist in two dependents (above); they are honoured only through TMPDIR. Not on the v2 path.

## (b) py_compile (`python3 -W error -m py_compile`, PYTHONPYCACHEPREFIX in scratch) — PASS 6/6

```
PASS tools/kama-completion-live.py
PASS tools/round63-c1-counter.py
PASS tools/round63-c2-counter.py
PASS tools/kama-llamacpp-live.py
PASS tools/kama-live-replay.py
PASS tools/instrument-agreement.py
```
(out/RV06Hygiene/b-py-compile.txt). Python 3.14.8.

## (c) Selftests and counters at tip

Lint context (ruff 0.17.2, `--select F,E3,E9,W6`): the counters are clean. The completion tool reports the same two F-findings at tip as at base 7ee8cbdf (so v2 added none): F401 `tempfile` unused (line 55), F841 `child_pre_dead` assigned never read (line 275; the real flag is `td['child_pre_dead']`, set ~line 523). Out/RV06Hygiene/ruff-tip.txt, ruff-base.txt.

(c1) `python3 tools/kama-llamacpp-live.py --selftest` (TMPDIR pinned) — PASS
```
selftest: ok; closed tcp6 listeners ::1:44351, ::ffff:127.0.0.1:39557
rc=0
```
(c2) `python3 tools/kama-live-replay.py --selftest --scratch <S>/replay` — PASS
```
... pass sealed-member-closes-on-refusal / sealed-member-short-writes / witness-passthrough / compare-instance-only / compare-stable-differs
KLR_SELFTEST pass=48 fail=0
rc=0
```
(c3) `python3 tools/instrument-agreement.py --selftest` — PASS
```
[PASS] deterministic: agree=3 disagree=0
[PASS] nondeterministic: agree=2 disagree=1
[PASS] declared-volatile: agree=3 disagree=0
[PASS] exit-disagreement: agree=2 disagree=1
IA_SELFTEST pass=4 fail=0
```
(c4) `kama-completion-live.py` has no `--selftest` (its argparse at tip has none). Its behaviour is exercised by the C1 counter (c5) and the round-62 C1 counter (c7).

(c5) `python3 tools/round63-c1-counter.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip 03a6a1d8… --work <S>/work-c1` — PASS, rc=0
```
tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=4/4 trunc=2/2 witness=6/6]
```

(c6) `python3 tools/round63-c2-counter.py --repo <clone> --tip 03a6a1d8… --work <S>/work-c2` — met=False, rc=1
```
population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 host_busy=1 mismatches=0 canonical=63 selfdesc_mismatches=8 sens_selftest=4/4 controls_rejected=12/12 errors=0 met=False
```
Reading of the non-green, from the counter's own `met` expression (`baseline and selfdesc == 0 and credited == total == 12 and st == 4 and …`): everything passes except `selfdesc_mismatches=8`, which the freeze fixes at 8 at this tip on purpose (re-derived by the L1 after measurement). `host_busy=1` is the context-capacity row returning its declared alternative `host-busy` because five foreign llama-server processes are live on this host (operator-owned, not touched); that row is conditional by design and is counted in `bound`, not as a mismatch. So: no hygiene defect in C2; it cannot read met=True until the L1 reconciles the self-description.

(c7) round-62 C1 counter (imports and pins the completion tool; frozen record, NOT amended)
- At base 7ee8cbdf: `tool_present=1 live_ok=1/1 fake_rejected=2/2 stale_rejected=1/1 tamper_rejected=8/8 log_rejected=1/1 predead_rejected=1/1 sigterm_rejected=1/1 hold_rejected=1/1 outside_rejected=1/1 errors=0 met=True`
- At tip 03a6a1d8: `tool_present=1 live_ok=0/1 fake_rejected=2/2 stale_rejected=1/1 tamper_rejected=8/8 log_rejected=1/1 predead_rejected=1/1 sigterm_rejected=1/1 hold_rejected=1/1 outside_rejected=1/1 errors=1 met=False`
  - stderr: `error: live: {"alltrue": true, "inconsistent": ["unexpected-checks"], "live": true, "met": false, "verdict_ok": true}`
- Cause (read from code): `tools/round62-c1-counter.py:40` pins `SCHEMA = 'kama-completion-live/v1'` and a fixed STORED check set; the v2 tool emits new checks (`completion_headers`, `completion_untruncated`, `completion_choice_shape`, `completion_id_created`, `completion_prompt_tokens`, `completion_request_bound`, …). The counter correctly flags the unknown checks as `unexpected-checks`.
- Assessment: this is the designed consequence of amending the completion tool to v2 while leaving the round-62 counter unamended, so the round-62 honest-stop record is preserved. But it is an operability regression for anyone who reproduces round 62 from the tip. Recommend the round-62 record cite the reproduction commit (7ee8cbdf), and say so in the L1's closure note.

(c8) round-62 C2 counter (runs `kama-llamacpp-live.py`, not the completion tool; registry `capability-claims-r62.tsv`)
- At base 7ee8cbdf: `population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 mismatches=6 canonical=62 controls_rejected=8/8 errors=0 met=False`
- At tip 03a6a1d8: `population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 mismatches=4 canonical=63 controls_rejected=8/8 errors=0 met=False`
- Non-green at base already (round-62 honest stop). The tip change (6 → 4, canonical 62 → 63) is not from the v2 completion tool, which this counter does not run; the only tip-side change near it is one appended row in `registry/hexrun-ledger.tsv` (+ the r63 registry, which this counter does not read). [INFERENCE] the canonical-count move and the mismatch shift are both effects of the round-63 ledger row; I did not dig into the 4 mismatch rows and do not claim a cause for them.

## (d) .gitignore and untracked state

Lane HEAD = 03a6a1d850902a66a13dfad33f89cf3a8b759a09 (= tip).

`.gitignore` (3 rules): `.ufo/interactive-sessions/`, `.ufo/state/`, `__pycache__/`. Nested `registry/history/.gitignore` (`*.json`, `.lock`) covers the two history JSONs and lock. `.jj/` is jj-managed ignored state. Checked: `tools/__pycache__/` and every wave `__pycache__` are ignored (`.gitignore:3`). My runs wrote no pycache into the lane (C1 loads its tool copy from `work/tip`; py_compile used a prefix in scratch).

`git ls-files --others --exclude-standard -- tools registry` → empty. No stray untracked file in the changed tools or registry.

Tracked modifications in the lane working tree that are NOT in the tip (not mine; the counters read tip blobs only, so they cannot affect the measurement):
- `PROVINCE.md`, `corpus/SOURCES.md`, `corpus/knowledge/completion-request-plane.md` (M).

Untracked, wave-owned (expected pre-commit; L1 commits):
- `.ufo/waves/round-63/source/` (144K), `.ufo/waves/round-63/w1.ready`, `w1.ready.partial`, `.ufo/waves/round-63/w1/` (384 files, 2.8M incl. `out/`).
- My own `.ufo/waves/round-63/w1/out/RV06Hygiene/` and this report.

**Flag D1 — stray nested file at lane root:** `kama-shokunin/.ufo/waves/round-62/w1/A04C1SchemaFuzz.md` (4230 bytes, mtime 09:27 today, untracked). The directory `kama-shokunin/` sits inside the lane root and is itself untracked. This is a doubled-path write from a relative-path mistake. Its content is a different revision of the tracked `.ufo/waves/round-62/w1/A04C1SchemaFuzz.md` (diff: reworded lines, plus an extra sentence naming `round62-c1-counter.py` as also loaded from the commit). I did not delete it (not mine). L1 should pick the canonical revision and remove `kama-shokunin/` from the lane root.

## Flags (ordered by weight)

1. **Round-62 C1 counter no longer reproducible at tip** (c7): met=False at 03a6a1d8 vs met=True at 7ee8cbdf. Designed by the SCHEMA pin; cite the reproduction commit in the round-62 record.
2. **C2 met=False at tip** (c6): only the frozen `selfdesc_mismatches=8` (plus the legitimate host-busy alternative). Expected; the L1 must reconcile after measurement.
3. **Stray nested `kama-shokunin/` at lane root** (D1).
4. **C1 does not pin TMPDIR for children** (a): add `env['TMPDIR']=work` in `witness_run`'s Popen, as C2 already does.
5. **v2 tool lint nits (pre-existing or minor, not behaviour):**
   - F1: `tools/kama-completion-live.py:55` `import tempfile` unused (F401; present at base too).
   - F2: `tools/kama-completion-live.py:275` `child_pre_dead = False` never read (F841; present at base too; the receipt's real flag is `teardown['child_pre_dead']`).
   - F3: `tools/kama-completion-live.py` has three blank lines before `def wait_ready` (line ~181; PEP 8 E303). Not flagged by ruff's default E3 selection; caught by a local AST/blank-line scan.
   - F4: `tools/round63-c1-counter.py` lines ~380 and ~404 use `json.load(open(...))` and `open(..., 'w').write(...)` without closing (CPython closes on refcount so behaviour is correct; cosmetic ResourceWarning).
6. **Pre-existing no-`dir=` mkstemp/mkdtemp** in `tools/kama-llamacpp-live.py:2209` and `tools/instrument-agreement.py:81` (off the v2 path; honoured only via TMPDIR).

## Verification gaps

- The C2 counter's full `mismatches` detail for the round-62 run (4 at tip, 6 at base) was not investigated; I give no cause beyond the [INFERENCE] above.
- Selftests run once each at tip; no mutation of the tools was attempted (not in my item).
- The lane repo is not exercised beyond read-only git blobs/status; no live server other than the counters' own loopback children.

## Tally lines (one per counter, as requested)

```
C1: tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True
C2: population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 host_busy=1 mismatches=0 canonical=63 selfdesc_mismatches=8 sens_selftest=4/4 controls_rejected=12/12 errors=0 met=False
```
