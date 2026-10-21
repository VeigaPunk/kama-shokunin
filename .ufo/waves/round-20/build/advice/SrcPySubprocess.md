VERDICT: confirm - the Python 3.14 `returncode` text grounds signal-killed = error (could-not-evaluate); the same page's 3.14.8 `shell=True` note plus probe cells expose a new frozen-grid misclassification.

Axes: calibration 7 (C1 "errors are not verdicts" instruments). Move kept: validates clean, append-only clean, harms none.

## Located quote (<=25 words) and location
- "A negative value -N indicates that the child was terminated by signal N (POSIX only)." — 15 words; `Popen.returncode`, Doc/library/subprocess.rst lines 958-959 @ tag v3.14.8; rendered page `#subprocess.Popen.returncode`, HTML lines 1176-1177.
- Second fragment (8 words): a shell "may map signals to codes such as 128+N" — rst 962-963 / HTML 1178-1181; new in 3.14.x, absent at v3.14.0 and v3.13.0 (fetched both tags; grep).

## Page identity (fetched 2026-10-21T07:23:14Z)
- https://docs.python.org/3.14/library/subprocess.html — HTTP 200, 207127 B, sha256 68c0a3cb9253c697ab7a27f6d653c2d9eda061adfa9e1f8a702d872ed3603634; `<title>` line 20 "subprocess — Subprocess management — Python 3.14.8 documentation"; "Last updated on Oct 21, 2026 (06:47 UTC)" line 2022.
- Pin: CPython `Doc/library/subprocess.rst` @ v3.14.8 (tag commit 8e6e75d9102e39bed2a2b279203a396741180f12), 61603 B, sha256 05cd782c5181481ad961788dd678b99c903eb3ff53e0ebab3095c38b48c74dfd; byte-identical (`cmp`) to 3.14 branch head e152a82bf3bd68c5bb0831bd78901943c085e7f0. Host interpreter 3.14.8 (`python3 --version`; platform.python_revision() empty).
- Draft row (recommended Draft A, validated text): .ufo/waves/round-20/build/out/SrcPySubprocess-2/drafts-rows.md; alt Draft B adds `W04 S058 duplicate url docs.python.org/3.14/library/subprocess.html across scopes` (fragment-stripped collision with S044; warning only, exit still 0); optional Draft C (bash 128+N, queued tier A).

## New red cells (executed against frozen instrument bytes)
- `tests/llamacpp-live/install-tree-grid.py:110-111` at the pin (frozen blob sha256 6f51803c47db597e2f6778b492bfaba14735a23c599bc972f8d33ab477a68f05; `git show | sha256sum` == working-tree file): `status = ("rejected" if code == 1 else "error" if code in (2, 3) else "accepted")` — a gate killed by a signal has negative returncode; probe observed gate_exit -9 (SIGKILL) and -15 (SIGTERM) both reported as status "accepted", grid exit 1. A crashed gate run counts as "no mutant accepted".
- Line 92 `baseline = "VALID" if exit_code == 0 else "INVALID"` labels a signal-killed baseline run "INVALID" with grid exit 2 — a verdict word for a run that emitted none.
- Round-20 known cell refined: not only "exit 1 ⇒ rejected" — ANY exit outside {0,1,2,3} (e.g. 137/143/247) lands on "accepted".
- Honest control: gate exit 1 + stdout "INVALID stub verdict" → "rejected" (probe cell frozen-grid-mutant-honest-reject) — the stdout verdict prefix per check-receipt.py:2233/2242 ("INVALID …" / "VALID …") separates them.
- Caveat: red cells were driven by a stub gate reproducing the documented verdict contract, not by a run of the real check-receipt.py gate (wave forbids heavy gate runs); frozen grid bytes and its classify ternary are exact.

## Behavioral cells (host Python 3.14.8, probe exit 0, 12/12 ok, no leftover children)
- `Popen.kill`/`terminate` → returncode -9/-15; `run(check=True)` raises CalledProcessError "died with <Signals.SIGKILL: 9>.".
- `shell=True` grandchild SIGKILL → 137; shell itself SIGKILL → -9; `bash -c` child SIGTERM → 143 (bash EXIT STATUS: "the value of 128+N as the exit status", lines 5924-5925 of the decompressed bash.1, sha256 b68beb3e…; §Pipelines 583-585).
- `sys.exit(p.returncode)` re-exit (tests/probe-verdicts/fault-controls.py:432,443,506 idiom) turns -9 into exit 247 — a signal death re-encoded positive (byte truncation).
- A child that prints "INVALID would-be verdict" and is then SIGKILLed still returns -9; the printed prefix alone is not a verdict.

## Code-read (grep/read only; execution not run) [INFERENCE]
- `.ufo/waves/round-18/c2/survivors.py:931-956` selftest_arm: negative/unknown exits → "inconclusive" ("unexpected selftest exit") — honest today, worth a census cell to keep.
- `survivors.py:885-907` classify_a: a fully printed decision document plus a post-print signal death still reads "killed" — borderline under "errors are not verdicts" (decision is observed, death is too).
- `shell=True` appears nowhere in tools/, tests/, .ufo/waves/round-18/c{1,2} (grep with shell=True alternative pattern: no hit) — argv lists keep the sign test valid; only bash-wrapper `sys.exit(p.returncode)` relabels.

## Constraints for L1 integration
- Row used-by names `tools/error-verdict-census.py`; census validate E11 fires until that file exists (validated with a placeholder; row otherwise clean, rows 57→58, tier.A 54→55, status.mined 46→47, only the 3 pre-existing W04s).
- Append-only guard (lane's own tools/sources-append-only.py at the pin): "added S058 (allowed)", "no append-only violations", exit 0.
- Draft C cites the local man page as host copy; gnu.org timed out (25 s) — reopen before tier-A use.

Installs: none. Evidence: probe-signal-returncode.py, probe-signal-returncode.json, drafts-rows.md under .ufo/waves/round-20/build/out/SrcPySubprocess-2/. Scratch /tmp/kama-r20-SrcPySubprocess removed before yield.
