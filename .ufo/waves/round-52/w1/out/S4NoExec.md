# S4NoExec — memfd_noexec frontier

Verdict: **ADMIT, narrowly** the kernel documentation as evidence that `vm.memfd_noexec=2` prevents this replay's executable-memfd path from working. The replay omits both execution flags; at policy 2 the kernel supplies `MFD_NOEXEC_SEAL`, so creation succeeds non-executable, but executing the fd fails. Explicit `MFD_EXEC` is recommended to make intent explicit and produce an early, clear refusal under policy 2; it does not make that policy support this executable-memfd mechanism.

## Source

- URL: https://docs.kernel.org/next/userspace-api/mfd_noexec.html
- Accessed: 2026-10-27T05:11:50Z (UTC).
- Located quote, “2: `memfd_create()` without `MFD_NOEXEC_SEAL` will be rejected.” (Sysctl section; 13 words.) The same section defines value 2 as `MEMFD_NOEXEC_SCOPE_NOEXEC_ENFORCED`.
- Scope/judgment: Admit as a kernel primary source for documented sysctl and flag semantics, but **limit its wording**: this sentence must not be read as saying that a caller omitting both flags gets an immediate `memfd_create()` error. For exact call behavior, the kernel implementation is more specific.

## Effect on round-52 replay

Observed source: `tools/kama-live-replay.py:237` calls `os.memfd_create(..., os.MFD_CLOEXEC | os.MFD_ALLOW_SEALING)`, without `MFD_EXEC` or `MFD_NOEXEC_SEAL`. Kernel implementation evidence supplied by the security seat: `mm/memfd.c:345-366`, `check_sysctl_memfd_noexec`, first adds `MFD_NOEXEC_SEAL` when neither flag is supplied and the policy is at least `NOEXEC_SEAL`; the EACCES branch at `NOEXEC_ENFORCED` applies if `MFD_NOEXEC_SEAL` is absent. Thus at value 2 the current call creates a non-executable memfd (with F_SEAL_EXEC), rather than failing at creation. Executing it then fails with EACCES. The observed scratch probe reported mode 0666, F_GET_SEALS 47, and exec of `/proc/self/fd/N` failing with Permission denied (Sen1Exec `out/Sen1Exec/seals-and-third-party.json`). The current replay's later error path may be opaque; see the security-seat finding, not established by this scout's test.

The replay consequence is source/peer-evidence-grounded, not a run of the replay under a changed host sysctl.

## Recommendation

The replay SHOULD pass `MFD_EXEC` explicitly: its purpose is to execute the verified server image, and explicit intent avoids silently creating a non-executable fd under policies that default memfds to non-executable (notably value 1). At value 2, explicit `MFD_EXEC` is rejected at creation with EACCES because it lacks `MFD_NOEXEC_SEAL`; this gives an earlier failure than the current implicit non-executable fd followed by exec-time denial. It does not bypass policy 2; execution of the memfd is unavailable there for an unprivileged caller. Any claim of support at value 2 needs another execution mechanism or policy change. No code change was applied by this scout.

## Evidence boundaries

No host sysctl was changed and no replay was run with `vm.memfd_noexec=2`. The implementation and standalone probe evidence are reported by Sen1Exec, not independently exercised by this scout. No claim is made about a specific diagnostic emitted by the unmodified replay.
