Verdict: A second executable memfd is reachable as non-root without LD_PRELOAD; the frozen C1 counter rejects it by dev+inode even when the live tool hides it from its own mapping receipt (`met=False`, exit 1).

## Evidence

- Host was non-root (`uid=1000`) and `/proc/sys/vm/memfd_noexec` read `0`. The b11909 release archive downloaded to scratch matched SHA-256 `bf94332a3001f3ee0b032cda37259f68460e28732ef9a579bfb1b918197e695b`; its `llama-server` matched the frozen `SERVER_SHA` `35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0`.
- Real-server `/proc/self/fd` attack, no LD_PRELOAD: launched the archive `llama-server` from a sealed memfd and set `LD_AUDIT=/proc/self/fd/N`, with N inherited and holding a minimal DSO exporting `la_version`. Server became ready. `/proc/<pid>/maps` contained executable rows for both `/memfd:llama-server (deleted)` (`00:01`, inode `239796`) and `/memfd:kama-audit (deleted)` (`00:01`, inode `239797`); `LD_PRELOAD present: False`, `LD_AUDIT present: True`; the audit DSO constructor wrote its marker. Thus an audit-capable DSO—not the non-audit `libexpat` case—does load from a memfd.
- Independent ggml route: `GGML_BACKEND_PATH=/proc/self/fd/N` with N an inherited memfd containing the real `libggml-cpu-zen4.so` made the real server ready and mapped an executable `/memfd:kama-backend (deleted)` row. An audit-only DSO without `ggml_backend_init` was rejected/unmapped (`load_backend: failed to find ggml_backend_init in /proc/self/fd/4`), while the real backend stayed mapped. Both routes avoid LD_PRELOAD.
- Exercised the frozen counter's actual `sealed_exe`, `code_observe`, and `env_leg` against the real server and release archive/tree. Honest control: 8 archive files, 13 host files, zero `code_observe`/sealed/env problems. With the second audit memfd: `sealed_exe own dev:ino = 00:01:225146`; `code_observe` reported twice (one per pass) `code: executable memfd /memfd:kama-audit (deleted) (00:01 225147) is not the sealed image`; `env_leg` had zero problems and names included `LD_AUDIT`. The differing inode is what the counter rejects.
- End-to-end frozen-counter verification used fixture-mutant commits in the scratch clone; each mutant deliberately hid the foreign memfd from the live tool's own `code_mappings` receipt. This isolates the counter's independent `/proc` observation:
  - GGML backend mutant tip `ce2bf2e1f8cc9cfea6c985257a104838d94d6d21`, counter exit **1**. Receipt `out/J3SecondMemfd/m-second-memfd-ggml.out:2` says `bind=1 ... code=0 ... envnames=3/3 ... met=False`; lines 5 and 7 show envnames passed and bind passed; lines 8-9 show `code: executable memfd /memfd:kama-backend (deleted) ... is not the sealed image`.
  - LD_AUDIT mutant tip `f3492a6200b4c4cbb00b15de55ff1d1476387317`, counter exit **1**. Receipt `out/J3SecondMemfd/m-second-memfd-ldaudit.out:2` likewise has `bind=1 ... code=0 ... envnames=3/3 ... met=False`; lines 5, 7-9 show envnames/bind passing while the counter flags `/memfd:kama-audit`.
  - Exact rerun commands and captured exits are in `out/J3SecondMemfd/counter-runs.txt`. Fixture diffs are in `fixture-mutant-ggml.patch` and `fixture-mutant-ldaudit.patch`; the latter's DSO source is `audit_min.c` (build with `gcc -shared -fPIC -Os -nostdlib -o tools/kama-audit-min.so audit_min.c`, then `strip -s tools/kama-audit-min.so`).

## Frozen counter behavior and interpretation

- `tools/round54-replay-code-audit.py:601` derives the running sealed image identity from `/proc/<pid>/exe` as `(dev, inode)`. At `:508-513`, every executable `/memfd:` mapping is admitted only if its maps `(dev, inode)` equals that identity; otherwise the counter appends `code: executable memfd ... is not the sealed image`. The two end-to-end receipts confirm this check is load-bearing even when the lane tool omits the mapping from its self-report.
- `BAD_ENV` at `:146` contains only `LD_PRELOAD` and `DYLD_INSERT_LIBRARIES`; `env_leg` at `:429-440` therefore does not flag `LD_AUDIT` or `GGML_BACKEND_PATH`. That is not a bypass in these tested in-process cases: the code leg independently rejects the second executable memfd. The relevant safeguard is `code_observe`, not envnames alone.
- No defect was found in the scoped `/memfd:` admission behavior, and no counter fix is proposed. The observation does show that a claim that LD_AUDIT is generally ineffective would be too broad: glibc ignored the tested non-audit DSO (`undefined symbol: la_version; ignored`) but loaded the audit-capable DSO used here. Both tests were non-root.
No project build, lint, formatter, or test suite was run. `gcc` built only the minimal LD_AUDIT probe DSO; remaining work was the requested live probes and frozen-counter measurements. The counter's teardown receipts report the server tree removed and its port refusing connections; a final `pgrep -af llama-server` found no leftovers.

## Written artifacts

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/J3SecondMemfd/m-second-memfd-ggml.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/J3SecondMemfd/m-second-memfd-ldaudit.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/J3SecondMemfd/counter-runs.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/J3SecondMemfd/fixture-mutant-ggml.patch`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/J3SecondMemfd/fixture-mutant-ldaudit.patch`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/J3SecondMemfd/audit_min.c`
