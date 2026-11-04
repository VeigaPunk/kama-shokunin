source: S544 — GNU coreutils `uname(1)`, https://man7.org/linux/man-pages/man1/uname.1.html, §DESCRIPTION `-s, --kernel-name` / `-m, --machine` (docs, tier A, mined, accessed 2026-11-03; row in `corpus/SOURCES.md`): "`-s` prints the kernel name and `-m` the machine hardware name"; the row fixes what each field prints, not that the pair identifies a host. `plans/round-73-claims.md` §C3 (frozen predicate, block grammar, exit map); `tools/round73-province-host-drift.py` (the counter; seat EX03HostDrift builds it and appends the round's block).
verified-at: bc9e3059 — plan §C3, `PROVINCE.md`'s `## Host re-derivation — round 71`, and live probes run 2026-11-03: `uname -s` → `Linux`, `uname -m` → `x86_64`, `/etc/os-release` `ID` → `arch`, `uname -r` → `7.2.11-arch1-1`. No counter run is claimed here.
recheck: `python3 tools/round73-province-host-drift.py --repo .`; `uname -s; uname -m; grep '^ID=' /etc/os-release`

# Host-identity drift gate — grade the recorded host against the live one

A record can describe a host the lane has left. `PROVINCE.md`'s round-65/67 notes described a
Windows host; only a hand-written round-71 re-derivation (14 contradicted surfaces) corrected
them, because the round-71 surface counter catches a move only while a *marker* contradicts. A
third move would leave every correction reading `present`/`absent` correctly while the recorded
host stayed wrong. Round 73 adds the missing question as a counter: **is the host this record
describes the host we are on?**

## The block

`PROVINCE.md` carries one paragraph per observation, first line:

    Round-<N> host-identity block (YYYY-MM-DD)

and, in its text, three tokens: the `uname -s` value (kernel name), the `uname -m` value
(machine hardware name), and the `ID=` field of `/etc/os-release` (parsed, never sourced). The
live instance is found with:

    grep -n 'host-identity block' PROVINCE.md

The block is a record of identity, not an inventory: no paths, no services, no versions. The
round-73 block appended during this wave records `Linux` / `x86_64` / `arch`, the same triple
the live probes above returned.

## Why this triple

The plan freezes the stability claim: "a kernel-only update does not move the triple (`uname -s`,
`uname -m` and `/etc/os-release` `ID` are stable across it); a machine or OS change does." The
kernel release (`uname -r`) is deliberately not compared: a kernel bump is routine and must not
fail the gate. A different machine, or a different distribution on the same machine, moves at
least one component. [INFERENCE] A container sharing the host kernel reports the same `uname -s`
and `uname -m`; the triple names the kernel+userspace family, not a physical box.

## What the counter grades

`python3 tools/round73-province-host-drift.py --repo .` prints one line

    PROVINCE_HOST_DRIFT blocks=<b> recorded=<s>/<m>/<id> live=<s>/<m>/<id> stale=<n>

and exits 0 only when the **newest** block in file order carries all three tokens and they equal
the live triple. `blocks` counts parsed blocks; `recorded` shows the graded block (`-` per
component when none exists); `stale=0` iff the graded triple equals the live one.

| State | Output | Exit |
|---|---|---|
| newest block matches live | `PROVINCE_HOST_DRIFT ... stale=0` | 0 |
| newest block differs | `PROVINCE_HOST_DRIFT_FINDING stale-host <detail>` | 1 |
| no block | `PROVINCE_HOST_DRIFT_FINDING no-block <detail>` | 1 |
| unparsable triple in the newest block | `stale-host` naming the line, never a skip | 1 |
| `PROVINCE.md` unreadable, CLI misuse, live probe failure | no verdict | 2 |

The append-only rule follows: a move is answered by appending a later block, never by editing the
old one. A stale newest block is a finding even when an older block matches the live host — the
newest record is the claim.

## What it does not show

- **Not a serving surface.** `tools/round71-province-host-claims.py` stays unchanged and keeps
  grading the declared `province-host:` surfaces against live probes; this counter grades the host
  triple only. A green `PROVINCE_HOST_DRIFT` is not a green surface census.
- **Not a kernel version.** `uname -r` is not compared, so a kernel-only move is invisible here by
  design; the block's date records when someone looked, not when the host changed.
- **Not a correction of the r71 claims.** It does not re-derive the 14 surfaces and does not
  replace the round-71 re-derivation; it answers one separate question.
- **Not that the block was measured.** Like a receipt header (`receipt-tip-binding.md`), the block
  is self-declared text; only equality with the live triple at grading time is graded. A block
  copied from another host's notes fails; a host that moves away and back between appends passes.
- **Not a history.** `blocks=<b>` counts paragraphs, not host moves; appending the same triple
  twice raises `blocks` and changes nothing else.

## Limits

- `/etc/os-release` `ID` is distribution identity, not version: `ID_LIKE`, `VERSION_ID` and the
  build id are not read, so two versions of one distribution read as one host.
- The graded state is the file at grading time. An uncommitted block binds nothing, and a block
  appended after a run is not in that run's verdict.
- An unparsable triple is `stale-host`, never a skip, so a broken append turns the counter red
  instead of silently disabling it.

## Scope correction — round 73 L1 integration

The broad machine-change sentence above is false and is superseded here: two different machines
running the same kernel family, hardware architecture and distribution can share this triple.
Likewise a copied block passes whenever its triple matches; the counter does not authenticate
where that block was measured. The demonstrated capability detects differences in these three
fields only, not every physical-host move. Append-only history is a policy, not something this
counter enforces: deleting or editing the newest block can still pass when the resulting triple
matches. S544 supports what the uname fields print, not uniqueness of a host identifier.
