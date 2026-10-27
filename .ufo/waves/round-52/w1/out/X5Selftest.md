# Round 52 w1 — X5Selftest (selftest strength for the memfd code)

**Verdict: 4 of the 6 named sabotages are killed by `kama-live-replay.py --selftest`
(one of them only by an uncaught traceback that truncates the last four cases), and
2 of 6 survive because `kama-llamacpp-live.py --selftest` never calls `sealed_fd()`;
one self-contained selftest case (full text below, verified in both directions) kills
both survivors and a third blind spot it exposed (`sealed_fd` that refuses everything).**

Ticket scope: at build `5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8`, run both
`--selftest` entry points; then apply six sabotages one at a time to scratch copies and
report which selftest kills each, with a proposed selftest case (full text) for each
survivor. Everything below is measured on a `git clone --shared` of the lane checked out
at the build commit; the lane itself and both tools are untouched.

## 1. Environment and frozen inputs

| item | value |
|---|---|
| build | `5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8` (clone HEAD after `git checkout`) |
| replay tool blob | `1d3d8225dd5b01fa292f5b579c38c2ddd94263e4` (742 lines) — identical at lane `HEAD` `34d82600` |
| live tool blob | `0399d0cebca27761c08b49149bcdfe8fa901c779` (2313 lines) — identical at lane `HEAD` |
| python | `Python 3.14.8`; kernel `7.2.11-arch1-1`; x86_64 |
| run dir | `/fast/scratch/hyaku/kama-r52/X5Selftest` (removed before finishing) |
| installs | none — stdlib only; no pacman, no uv/npx/binary install was needed or run |
| services | none started; `pgrep -af "llama-server --"` → no match at finish |

Baseline at the build bytes (both from the clone, so the numbers are the committed
code, not the lane working tree):

```
$ python3 $S/lane/tools/kama-live-replay.py --selftest --scratch $S/run/base742
… pass=31 fail=0
KLR_SELFTEST pass=31 fail=0                                    exit 0
$ python3 $S/lane/tools/kama-llamacpp-live.py --selftest
selftest: ok; closed tcp6 listeners ::1:33711, ::ffff:127.0.0.1:45163   exit 0
```
(evidence: `00-replay-selftest-build.out`, `01-live-selftest-build.out`)

Observation (not mine, not a finding of this seat): during the wave the lane working
tree acquired an **uncommitted** edit to `tools/kama-live-replay.py` (742 → 752 lines,
an `MFD_EXEC` retry in `sealed_member` attributed to seat `S4NoExec`). All line numbers
and all sabotage results here are against the committed build blob; the working tree
version was not used.

## 2. Matrix

Each sabotage is one edit to a scratch copy (`sabotage-*.diff`, applied with `patch -o`);
the command column is what was run afterwards.

| # | sabotage (one at a time) | command | exit | killed by |
|---|---|---|---|---|
| a | `sealed_member`: no `F_ADD_SEALS` (replay:247 deleted) | replay `--selftest` | 1 | **crash only** — uncaught `Refused: memfd-not-sealed:0` out of the bare call at replay:594; 0 `FAIL` lines, no `KLR_SELFTEST` summary, last 4 cases never run |
| a2 | extra: `F_ADD_SEALS` **and** the `seals & SEALS_ALL` refusal removed (replay:247, 249-250; the read at 248 stays for the identity) | replay `--selftest` | 1 | `sealed-member-refuses-writes`, plus 3 replay cases (`pass=27 fail=4`) — clean |
| b | `sealed_member`: hash computed, comparison removed (replay:245) | replay `--selftest` | 1 | `FAIL sealed-member-digest-mismatch: no refusal` (`pass=30 fail=1`) |
| c | replay: `and se.get("nlink") == 0` removed (replay:435) | replay `--selftest` | 1 | `FAIL server-exe-linked: exit=0 refused=None mism=[]` |
| d | replay: `/memfd:` path test removed (replay:435) | replay `--selftest` | 1 | `FAIL server-exe-path: exit=0 refused=None mism=[]` |
| e | live `sealed_fd`: any seals accepted (live:796 → `if not stat.S_ISREG(...)`) | live `--selftest` | **0** | **survives** — `selftest: ok` |
| f | live `sealed_fd`: digest never compared (live:807 → `if False:`) | live `--selftest` | **0** | **survives** — `selftest: ok` |
| g | extra: `sealed_fd` refuses everything (live:791 `raise SetupError(...)`) | live `--selftest` | **0** | **survives** — `selftest: ok` |

Extra rows `a2` and `g` are mine: `a2` separates "the seal was never applied" from
"the guard that notices it was removed" (the literal sabotage `a` trips the guard, so
`a` alone does not show whether the *selftest* can see an unsealed memfd — `a2` shows
it can, four times); `g` is the missing positive direction of the same test.

Evidence files: `02-sab-a-…out`, `03-sab-a2-…out`, `04`–`06`, `07`–`08`, `15-sab-g…out`,
`reproduce.log` (full re-run from a clean scratch: all eight rows reproduce).

## 3. Why (e) and (f) survive, and why the replay selftest cannot cover them

- `sealed_fd()` is defined at `tools/kama-llamacpp-live.py:786`; its seal guard is
  `:796` and its digest comparison `:807-808`. Its only caller is `:1955` (the run that
  execs the memfd server). `grep -n "sealed_fd" tools/kama-llamacpp-live.py` returns
  exactly two lines — `786:def sealed_fd(...)` and `1955:    receipt['server']['fd'] =
  sealed_fd(`: **no selftest case calls it**. The live selftest
  (`_selftest`, `:1630-1731`) covers procfs parsing, tcp6 rows, outcome mapping,
  install identity, v5 provenance, the atomic-publish interruption and handler restore —
  nothing about `--server-fd`.
- The replay selftest cannot make up for it: `run()` defaults `live=fake_live`
  (`tools/kama-live-replay.py:523`) and passes that `live` explicitly to `replay()`
  (`:524`); the witness case passes `witness_live` (`:643`); the one case that runs a
  live child over the *real* interface is `live-exit-nonzero` with `bad_live` (`:545`).
  `DEFAULT_LIVE` (`:106`) is only `replay()`'s default argument (`:339`) and the CLI
  default (`:683`). So both selftests are green on a live tool that would `exec` an
  unsealed or wrong-bytes fd.
- Residual coverage for (e)/(f) lives in the frozen counter, not the selftest: the
  counter opens `/proc/<pid>/exe` itself and re-checks `/memfd:`, `st_nlink`,
  `F_GET_SEALS` and the frozen digest
  (`tools/round52-replay-memfd-audit.py:373-390`). [INFERENCE] That catches a
  wrong-bytes fd (f) but not a live tool that stops *refusing*; I did not run the
  counter in this seat (out of scope, ~16 s × replay, and other seats own it).

## 4. Defects

**D1 — live selftest has no `sealed_fd` case at all (coverage hole; sabotages e, f, g
survive).** File `tools/kama-llamacpp-live.py`, `_selftest` `:1630-1731` (no reference
to `sealed_fd`, `--server-fd` or a memfd); function under test `:786-812`.
Show it: apply `sabotage-e.diff` / `sabotage-f.diff` / `sabotage-g.diff` to a copy and
run `--selftest` → exit 0, `selftest: ok` (files `07`, `08`, `15`). Fix: Proposal 1.

**D2 — replay selftest's `sealed_member` case is a bare call, so a broken
`sealed_member` aborts the run instead of failing a case.**
`tools/kama-live-replay.py:594` (`fd, ident = sealed_member(...)`, outside any
`try`). Show it: apply `sabotage-a.diff`, run the selftest →
`Refused: memfd-not-sealed:0` traceback, exit 1, **no `FAIL` line and no
`KLR_SELFTEST` line** (file `02`), and the four cases after it
(`sealed-member-digest-mismatch`, `witness-passthrough`, `compare-instance-only`,
`compare-stable-differs`) never execute. A CI check that greps `KLR_SELFTEST pass=`
therefore sees an empty result, not a failure. Fix: Proposal 2 (verified: sabotaged →
one `FAIL` line, `pass=15 fail=16`, exit 1; pristine → `pass=31 fail=0`, exit 0).

**D3 — the live selftest's failure line drops the message, so a failing case cannot be
identified.** `tools/kama-llamacpp-live.py:1765` prints
`f'kama-llamacpp-live selftest: {type(exc).__name__}'`. With Proposal 1 in place, all
three kills print the same `AssertionError`. Fix (one line, verified green on pristine
and showing the case on the sabotaged copy):
`proposal-live-failure-message.diff`; output becomes
`kama-llamacpp-live selftest: AssertionError: server-fd accepted, expected server-fd-not-sealed:0`
(file `14`).

Not a defect, method note: the live tool's selftest resolves
`LANE = Path(__file__).resolve().parent.parent` (`:92-94`) and reads
`registry/endpoint-consumers.tsv`, so a sabotage copy must keep the `tools/` + `registry/`
shape (that is why the live sabotage dirs are `sab-<t>/tools/…` with a `registry`
symlink). The counter does not have this constraint; the selftest could degrade to a
warning when the registry is absent, but that is a design call for the L1, not a
strength finding.

## 5. Proposals (full text)

### Proposal 1 — new live selftest case (kills e, f and g)

Insertion A: immediately before `def _selftest():` (`tools/kama-llamacpp-live.py:1630`).
Insertion B: `    _server_fd_selftest()` as the first statement of `_selftest()`.

```python
F_ADD_SEALS = 1033          # F_LINUX_SPECIFIC_BASE + 9 (fcntl(2)); round 52


def _server_fd_selftest():
    """Round 52 (X5Selftest): sealed_fd() accepts exactly one shape - a sealed memfd whose
    bytes and length are the --server file's - and refuses an unsealed memfd, a file that
    cannot be sealed at all, a partly sealed memfd, a length mismatch and a digest
    mismatch. No case called sealed_fd before this one, so deleting the seal test or the
    digest comparison from it (or making it refuse everything) left the selftest green."""
    def a_memfd(payload, seals):
        fd = os.memfd_create('server-fd-selftest',
                             os.MFD_CLOEXEC | os.MFD_ALLOW_SEALING)
        if payload:
            os.write(fd, payload)
        if seals:
            fcntl.fcntl(fd, F_ADD_SEALS, seals)
        return fd

    def refused(fd, want_sha, want_size, token):
        try:
            sealed_fd(fd, want_sha, want_size)
        except SetupError as exc:
            if not str(exc).startswith(token):
                raise AssertionError(
                    f'server-fd refusal {exc} != {token}') from None
            return
        raise AssertionError(f'server-fd accepted, expected {token}')

    payload = b'\x7fELF server-fd selftest'
    want = hashlib.sha256(payload).hexdigest()
    fd = a_memfd(payload, SEALS_ALL)
    try:
        try:
            ident = sealed_fd(fd, want, len(payload))
        except SetupError as exc:
            raise AssertionError(
                f'server-fd refused a sealed memfd: {exc}') from None
    finally:
        os.close(fd)
    if (ident['sha256'] != want or ident['nlink'] != 0
            or ident['seals'] & SEALS_ALL != SEALS_ALL):
        raise AssertionError(f'server-fd identity not a sealed memfd: {ident}')
    fd = a_memfd(payload, 0)                  # memfd, never sealed
    try:
        refused(fd, want, len(payload), 'server-fd-not-sealed:0')
    finally:
        os.close(fd)
    with tempfile.TemporaryDirectory(prefix='kama-server-fd-selftest-') as directory:
        path = os.path.join(directory, 'server')
        with open(path, 'wb') as fh:         # a directory file cannot be sealed
            fh.write(payload)
        fd = os.open(path, os.O_RDONLY)
        try:
            refused(fd, want, len(payload), 'server-fd-not-sealed:None')
        finally:
            os.close(fd)
    fd = a_memfd(payload, 3)                  # F_SEAL_SEAL|F_SEAL_SHRINK only
    try:
        refused(fd, want, len(payload), 'server-fd-not-sealed:3')
    finally:
        os.close(fd)
    fd = a_memfd(payload, SEALS_ALL)
    try:
        refused(fd, want, len(payload) + 1, 'server-fd-size:')
    finally:
        os.close(fd)
    fd = a_memfd(payload, SEALS_ALL)
    try:
        refused(fd, '0' * 64, len(payload), 'server-fd-digest-differs-from-server')
    finally:
        os.close(fd)
```

Measured (`proposal-live-server-fd-selftest.diff`, `reproduce.log`, `16-*.trace`):

| tool under the case | exit | message |
|---|---|---|
| pristine | 0 | `selftest: ok` |
| sabotage (e) any seals | 1 | `AssertionError: server-fd accepted, expected server-fd-not-sealed:0` |
| sabotage (f) no digest | 1 | `AssertionError: server-fd accepted, expected server-fd-digest-differs-from-server` |
| sabotage (g) always refuses | 1 | `AssertionError: server-fd refused a sealed memfd: server-fd-unusable:sabotage-g` |

Which assertion does the work: (e) the unsealed-memfd case (`seals 0`), (f) the
wrong-digest case, (g) the positive branch; the plain-file case and the partial-seal
case cover the two remaining shape branches of the guard at live:796.

### Proposal 2 — make sabotage (a) a reported failure (replay)

Replace `tools/kama-live-replay.py:593-605` with:

```python
        # the sealed memfd is filled from the archive's member stream, not from the path
        # (round 52 X5Selftest: a bare call here turned a broken sealed_member into an
        # uncaught Refused that skipped the witness and compare cases and printed no
        # KLR_SELFTEST summary; record it as one failing case instead)
        try:
            fd, ident = sealed_member(arc, "build/bin/llama-server", ssha)
        except Refused as exc:
            cases.append(("sealed-member-refuses-writes", False,
                          f"sealed_member refused a good member: {exc}"))
        else:
            try:
                sealed = fcntl.fcntl(fd, F_GET_SEALS) & SEALS_ALL == SEALS_ALL
                try:
                    os.write(fd, b"x")
                    wrote = True
                except OSError:
                    wrote = False
            finally:
                os.close(fd)
            cases.append(("sealed-member-refuses-writes",
                          sealed and not wrote and ident["memfd"] is True,
                          f"sealed={sealed} wrote={wrote} ident={ident}"))
```

Measured (`proposal-replay-sealed-member-case.diff`): pristine → `KLR_SELFTEST pass=31
fail=0`, exit 0; sabotage (a) → `FAIL sealed-member-refuses-writes: sealed_member
refused a good member: memfd-not-sealed:0`, 16 `FAIL` lines, `pass=15 fail=16`, exit 1,
and the witness/compare cases now run (files `12`, `13`).

### Proposal 3 — name the failing case on the live tool

`tools/kama-llamacpp-live.py:1765`:

```python
                print(f'kama-llamacpp-live selftest: {type(exc).__name__}: {exc}',
                      file=sys.stderr)
```

(`proposal-live-failure-message.diff`; pristine stays `selftest: ok`, exit 0.)

## 6. What this does and does not establish

Established by measurement at the committed build: the four replay-side sabotages are
detected (a only as a crash), and the three live-side ones are not; the proposals above
close them with the tool's own selftest, verified in both directions (pristine green,
each sabotage red). Not established here: whether the frozen C1 counter kills (e)/(f)
(the counter's `sealed_exe()` re-checks the memfd independently, so (f) at least is
covered end-to-end — [INFERENCE], not run); whether the lane working tree's uncommitted
`MFD_EXEC` edit changes any of these line numbers (it shifts `sealed_member` by ~10
lines); nothing about C2, the integration items, or the claim verdict — this is a
selftest-strength seat only.

## 7. Files

Report: `.ufo/waves/round-52/w1/out/X5Selftest.md`
Deliverables: `.ufo/waves/round-52/w1/out/X5Selftest/`
- `00`/`01` build-byte baselines; `02`–`08`, `15` sabotage runs;
- `09` proposal on pristine; `12`/`13` replay proposal on pristine and on sabotage (a);
- `14` failure-message check; `16-*.trace` which assertion kills e/f/g;
- `sabotage-{a,a2,b,c,d,e,f,g}.diff` (each one edit, applied with `patch -o`);
- `proposal-live-server-fd-selftest.diff`, `proposal-replay-sealed-member-case.diff`,
  `proposal-live-failure-message.diff`, plus the full-text pair
  `proposed-live-server-fd-selftest.txt`, `proposed-replay-sealed-member-block.txt`;
- `reproduce.sh` + `reproduce.log` (re-runs the whole matrix from a clean scratch with
  the existing clone; exit 0).
