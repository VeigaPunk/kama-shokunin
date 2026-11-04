# EX03HostDrift — kama round 73, C3 (freshness)

Seat: EX03HostDrift (executor, C3 build). Claim graded: C3 of
`plans/round-73-claims.md` (frozen). No claim rule was edited; the plan's C3 predicate,
counter code and receipt label are one sentence, and the tool's `PREDICATE` constant is
byte-equal to the plan's C3 blockquote with `>` marks and line breaks removed (564 chars,
selftest arm `predicate`).

Revision at write time: `bc9e30599b6c6133bb094f0e7abd1a9f512778ec` (`git -C L rev-parse master`).

## Freeze-base observation (record note, not a disagreement)

The plan's freeze base is `6e9619963fef5a3f8899324e9497416a00eab7e6`; live `master` is
`bc9e3059…`. `git log --oneline -3` shows the delta is the round's own freeze commits
(`24bc96ad round-73: freeze three claims …`, `bc9e3059 round-73: freeze w1 wave spec (15 seats) …`)
on top of `6e961996 round-72 verifier spot-check`. No claim rule, predicate or control byte was
changed; every receipt here names the revision read when it was written (`bc9e3059…`).

## Built

`tools/round73-province-host-drift.py` (424 lines, sha256
`ec7bfd3fdf26be7338975c07443cdd15945f378d6f01774a70ef8e71934cd919`) — read-only counter that
grades PROVINCE.md's recorded host identity against the live host.

- CLI: `--repo PATH` (default `.`), `--file PATH` (default `PROVINCE.md`, resolved against
  `--repo`; an absolute path replaces it), `--selftest`, `--json`, and `--work PATH` for the
  selftest fixture root (a temporary root is created and removed when `--work` is omitted; a
  supplied root is left in place because the caller owns it).
- Block parse: a paragraph whose first line matches
  `^\s*\*{0,2}Round-(\d+) host-identity block \((\d{4}-\d{2}-\d{2})\)` and whose text carries
  `uname -s`, `uname -m` and the `/etc/os-release` `ID` tokens, each followed by `->` and a value
  (backticked or bare). The graded block is the LAST in file order (append-only file). A block
  whose triple cannot be parsed is a `stale-host` finding naming its line, never a skip.
- Live triple: `uname -s`, `uname -m`, and `ID=` parsed (not sourced) from `/etc/os-release`.
- Output: `PROVINCE_HOST_DRIFT_FINDING <no-block|stale-host> <detail>` per finding, then
  `PROVINCE_HOST_DRIFT blocks=<b> recorded=<s>/<m>/<id> live=<s>/<m>/<id> stale=<n>`; `recorded`
  is `-` per component with no block or an unparseable graded triple, and `stale=0` iff the
  graded triple equals the live triple.
- Exit map: 0 clean, 1 findings, 2 could-not-evaluate (PROVINCE.md unreadable or not UTF-8, a live
  probe failure, CLI misuse). CLI misuse exits 2 via argparse.
- Selftest, nine arms, plain-directory fixtures (never git): live-match green; Windows triple
  -> exit 1 `stale-host`; no block -> exit 1 `no-block`; two blocks where the newest matches ->
  exit 0; newest differs while an older matches -> exit 1; unparsable triple -> exit 1 naming
  `line=3`; missing file -> exit 2; CLI misuse -> exit 2; predicate arm comparing the constant to
  the plan's C3 blockquote.

`PROVINCE.md`: appended exactly one paragraph at end of file (now lines 309–310; block line 310).
`git diff --numstat -- PROVINCE.md` -> `2 0` (one blank separator line plus the block); no other
PROVINCE.md byte changed. The appended block, with the three live probe values:

    Round-73 host-identity block (2026-11-03). Host triple: `uname -s` -> `Linux`; `uname -m` -> `x86_64`; `/etc/os-release` `ID` -> `arch`. Graded by `tools/round73-province-host-drift.py`; a host move is answered by appending a later block, never by editing this one.

## Commands run, with observed output

Live probes (run before appending):

    $ uname -s
    Linux
    $ uname -m
    x86_64
    $ grep -m1 '^ID=' /etc/os-release
    ID=arch

Selftest (receipt `selftest.out`, exit 0):

    $ PYTHONDONTWRITEBYTECODE=1 python3 tools/round73-province-host-drift.py --selftest --work /fast/scratch/hyaku/kama-r73/EX03HostDrift/work
    [PASS] live-match: rc=0 PROVINCE_HOST_DRIFT blocks=1 recorded=Linux/x86_64/arch live=Linux/x86_64/arch stale=0
    [PASS] windows-stale: rc=1 PROVINCE_HOST_DRIFT blocks=1 recorded=Windows/AMD64/win live=Linux/x86_64/arch stale=1
    [PASS] no-block: rc=1 PROVINCE_HOST_DRIFT blocks=0 recorded=-/-/- live=Linux/x86_64/arch stale=1
    [PASS] newest-matches: rc=0 PROVINCE_HOST_DRIFT blocks=2 recorded=Linux/x86_64/arch live=Linux/x86_64/arch stale=0
    [PASS] newest-differs: rc=1 PROVINCE_HOST_DRIFT blocks=2 recorded=Windows/AMD64/win live=Linux/x86_64/arch stale=1
    [PASS] unparseable-triple: rc=1 PROVINCE_HOST_DRIFT blocks=1 recorded=-/-/- live=Linux/x86_64/arch stale=1
    [PASS] missing-file: rc=2 PROVINCE_HOST_DRIFT could-not-evaluate: cannot read …/f6-missing/PROVINCE.md: [Errno 2] No such file or directory
    [PASS] cli-misuse: rc=2 round73-province-host-drift.py: error: unrecognized arguments: --no-such-flag
    [PASS] predicate: plan_chars=564 constant_chars=564
    PROVINCE_HOST_DRIFT_SELFTEST pass=9 fail=0

Kill rule, frozen control fixture `c3_stale` (receipt `kill-stale.out`, exit 1). Fixture bytes are
the round's own `controls/build-survivors.py` output:
`/fast/scratch/hyaku/kama-r73/controls-work/fixtures/c3_stale/PROVINCE.md`, sha256
`5ff29f867e56b5795103270fc823ca0481404eecc01d1c7770a1bdc287508dbe`:

    $ PYTHONDONTWRITEBYTECODE=1 python3 tools/round73-province-host-drift.py --repo /fast/scratch/hyaku/kama-r73/controls-work/fixtures/c3_stale
    PROVINCE_HOST_DRIFT_FINDING stale-host line=3 round=73: recorded=Windows/AMD64/win live=Linux/x86_64/arch
    PROVINCE_HOST_DRIFT blocks=1 recorded=Windows/AMD64/win live=Linux/x86_64/arch stale=1
    # exit=1

Kill rule, block-less fixture (receipt `kill-noblock.out`, exit 1). Fixture was
`$S/noblock/PROVINCE.md` = `# province fixture` + blank line + one prose line:

    $ PYTHONDONTWRITEBYTECODE=1 python3 tools/round73-province-host-drift.py --repo /fast/scratch/hyaku/kama-r73/EX03HostDrift/noblock
    PROVINCE_HOST_DRIFT_FINDING no-block no Round-<N> host-identity block in /fast/scratch/hyaku/kama-r73/EX03HostDrift/noblock/PROVINCE.md
    PROVINCE_HOST_DRIFT blocks=0 recorded=-/-/- live=Linux/x86_64/arch stale=1
    # exit=1

Live lane before the append (the do-nothing state; observed, not a receipt):

    $ PYTHONDONTWRITEBYTECODE=1 python3 tools/round73-province-host-drift.py --repo .
    PROVINCE_HOST_DRIFT_FINDING no-block no Round-<N> host-identity block in /home/vgpnk/Projects/shokunin/kama-shokunin/PROVINCE.md
    PROVINCE_HOST_DRIFT blocks=0 recorded=-/-/- live=Linux/x86_64/arch stale=1
    # exit 1

After appending the block (receipt `live.out`, exit 0):

    $ PYTHONDONTWRITEBYTECODE=1 python3 tools/round73-province-host-drift.py --repo .
    PROVINCE_HOST_DRIFT blocks=1 recorded=Linux/x86_64/arch live=Linux/x86_64/arch stale=0
    # exit=0

JSON mode (observed): `{"tool": "province-host-drift/v1", … "blocks": 1, "graded": {"line": 310,
"round": 73, "date": "2026-11-03", "triple": ["Linux", "x86_64", "arch"]}, "recorded": ["Linux",
"x86_64", "arch"], "live": ["Linux", "x86_64", "arch"], "stale": 0, "findings": [], … "exit": 0}`
(exit 0; the `predicate` field is the `PREDICATE` constant).

Cross-checks: selftest re-run from a second work root -> `PROVINCE_HOST_DRIFT_SELFTEST pass=9
fail=0`, exit 0; invocation from `/tmp` with absolute `--repo`/`--file` -> same green summary, exit
0; `find .ufo/waves/round-73 -name __pycache__` -> no output (0); every python invocation above ran
with `PYTHONDONTWRITEBYTECODE=1`.

## Files written

- `tools/round73-province-host-drift.py` (new; sha256 `ec7bfd3f…4934cd919`)
- `PROVINCE.md` (append-only: one blank line + one block; 2 insertions, 0 deletions)
- `.ufo/waves/round-73/w1/EX03HostDrift/selftest.out` (sha256 `a046e240…2bb1e8ed`)
- `.ufo/waves/round-73/w1/EX03HostDrift/kill-stale.out` (sha256 `674c047c…36639bb0`)
- `.ufo/waves/round-73/w1/EX03HostDrift/kill-noblock.out` (sha256 `f08c3731…af93578d`)
- `.ufo/waves/round-73/w1/EX03HostDrift/live.out` (sha256 `8e89cd15…3f3ee4b95`)
- this report

Every receipt's first line is `# rev=bc9e30599b6c6133bb094f0e7abd1a9f512778ec`. Scratch root
`/fast/scratch/hyaku/kama-r73/EX03HostDrift/` (selftest fixtures, `noblock` fixture, second work
root) was deleted after the receipts were copied into the wave dir.

## Risks and limits

- The counter grades identity, not serving surfaces: PROVINCE.md's round-71 claims remain graded
  by `tools/round71-province-host-claims.py`, which was not run and not touched (per assignment).
- `stale` counts the single graded block (0 or 1); with no block it is 1 because no recorded triple
  equals the live one. No block also emits `no-block`, so the two findings classes stay disjoint.
- The block grammar accepts optional `**` bold marks and bare (unbackticked) values as fallbacks;
  the canonical backticked form and the frozen `c3_stale` fixture both parse.
- No tools were installed or upgraded (none needed); no network, no git/jj mutation, no other lane
  byte touched. Untracked files observed in the lane but not mine
  (`.ufo/waves/round-73/measured/before/sources-census-start.out`, `w1.ready.dispatched`) were left
  alone.
