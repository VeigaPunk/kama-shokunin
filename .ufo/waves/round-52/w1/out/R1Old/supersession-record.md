# Supersession record: round-51 C1 (`round51-replay-exe-audit.py`) at the round-52 build

Seat: R1Old. Measured at lane commit `5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8`, base
`9ff76b1f763512be2f554cbbfd0b2213b63b0847`, on a `git clone --shared` of the lane.
Frozen counter bytes (identical to the lane's working copies):
`tools/round50-replay-bind-audit.py` sha256 `ff6ac2ace541ea35a4d240ceebb019653c11a2a08c025e514770f3f94a9c5e89`,
`tools/round51-replay-exe-audit.py` sha256 `e5753c453c30bd311e4c12fc962d324c7db482233b64b22795658b47b6ee5155`,
`tools/round52-replay-memfd-audit.py` sha256 `053ff50261812de3236697dd8dc847b3dff9507f8290b0d42aaf65c12e1121f5`
(= the round-52 preregistration's `counter_sha256`).

## Verdict

**Supersession, not harm.** The round-51 C1 counter's `own` leg is unsatisfiable by
construction at the build because the build replaced the mechanism that leg measured; the
capability it stood for is carried - strengthened - by round-52 C1's `sealed` leg, and every
operability observable that the lane had before still reads met at the build.

## Readings

| tip | instrument | result |
|---|---|---|
| `9ff76b1f` (base) | `round51-replay-exe-audit.py` | `bind=1 own=1 teardown=1 newrow=1 bound=3/3 owned=3/3 met=True`, exit 0 |
| `5dacf2c7` (build) | `round51-replay-exe-audit.py` | `bind=1 own=0 teardown=1 newrow=1 bound=3/3 owned=0/3 met=False`, exit 1 |
| `5dacf2c7` (build) | `round50-replay-bind-audit.py` | `bind=1 teardown=1 newrow=1 bound=3/3 met=True`, exit 0 |
| `5dacf2c7` (build) | `round52-replay-memfd-audit.py` | `bind=1 sealed=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 met=True`, exit 0 |

At the base the counter's own lines read `own b1: running image 103:05:279245079 is the
extracted member, recorded in server_exe and own_server` (and `b2`, `b3` likewise). At the
build they read `own b1: own: running image dev:inode 00:01:179308 is not the replay's
extracted member <work>/server/llama-b11909/llama-server (103:05:482904534)` and
`own b1: own: replay own_server {..., 'memfd': True, ..., 'seals': 15, 'dev': '00:01',
'inode': '179308'} does not name the observed member file` - the observed image and the
replay's own record agree with each other; they disagree with the extracted path, which is
the whole point of the build.

## Why this is a replacement and not a loss

The round-51 `own` leg conjoined two claims
(`tools/round51-replay-exe-audit.py:351-379` and `:493-498`):

1. the running image is the file **this replay produced and verified** - the replay's
   `own_server` (and the rerun receipt's `server_exe`) name the same dev and inode that the
   counter itself read from `/proc/<pid>/exe`, with the frozen digest; and
2. that image is **the extracted member at `<work>/server/<member>`** - its dev and inode
   equal `os.stat()` of the extracted file.

Clause 1 survives in round-52 C1 unchanged in strength
(`tools/round52-replay-memfd-audit.py:495-508`: `server_exe` opened, frozen digest, same
dev and inode as the counter's own `/proc/<pid>/exe` read, seals 15; the replay's
`own_server` has `memfd` true, the same dev and inode). Clause 2 is dropped, and it is
dropped **for cause**: round-51 closure D5 records that a byte-identical copy at the member
path met the round-51 counter (seat J3CopyDecoy) and a hardlink met its own leg (seat
J4Hardlink), i.e. path dev/inode was not a provenance proof. Round-52 C1 replaces it with
an image that has no path at all: `memfd_create` + `F_ADD_SEALS 15`
(`tools/kama-live-replay.py:222-256`), exec via `--server-fd`
(`tools/kama-llamacpp-live.py:786-811`), and the counter's own reading of an anonymous,
sealed, single-link `/memfd:` image (`tools/round52-replay-memfd-audit.py:363-395`).

The lane already states the retirement: `SKILL.md:1552` ("the round-51 member-links case
retired with the path binding") and the round-52 reading note at `SKILL.md:1557`.

## Evidence against "harm to operability"

- `round50-replay-bind-audit.py` at the build: bind 3/3 (running image digest, listener,
  nonce against the model's own vocabulary, process tree, canary-free environment, mapped
  model, child_pid join, released), `teardown: invoker SIGKILLed with 3 descendants; after
  0.10 s alive [] port refuses ok`, `newrow` 1 row.
- `round52-replay-memfd-audit.py` at the build (run by this seat, not quoted):
  `sealed b1: running image '/memfd:llama-server (deleted)' 00:01:174275 seals 15 is a
  sealed memfd with the frozen digest, recorded in server_exe and own_server` (b1, b2, b3),
  teardown in 0.10 s, `newrow` S500 (`memfd_create(2)`).
- `round51-replay-exe-audit.py` at the build still reads `bind=1`, 3/3: the running image's
  digest, listener, nonce, tree, environment and mapped model are unchanged; only the path
  identity is gone by design.

So no server behaviour got worse: the same tiny model is served, the same bytes execute,
the same tree dies in 0.10 s. What changed is that the instrument that asserted a *path*
identity no longer applies, and the instrument that asserts an *anonymous sealed image*
identity does.

## Consequences for the lane's instrument bookkeeping (proposal)

- Treat `tools/round51-replay-exe-audit.py` as a **retired live instrument**: its `met`
  target is unreachable at any tip >= `5dacf2c7`. Its round-51 measurement at its own tip
  stands as history; the `## Round-51 instrument registry` row (`SKILL.md:1530`) should gain
  one dated clause saying that (the row's `own` description stays as the round-51 shape).
- Keep `bind`/`teardown`/`newrow` of the round-51 counter usable as regression legs if the
  lane wants them, but read them without the `own` leg.
- Nothing re-runs the round-51 counter: `grep -rn "round51-replay" tools/` hits only its
  own docstring; the other hits are history (the round-51 preregistration/spec/build files,
  the round-51 lesson, the round-51 seats' scratch copies) and the registry row itself.

Ready-to-paste paragraph for the round-52 report / SCORECARD:

> **Round-51 C1 superseded (not harmed).** At the build `5dacf2c7`,
> `tools/round51-replay-exe-audit.py` reads `bind=1 own=0 teardown=1 newrow=1 bound=3/3
> owned=0/3 met=False`: each replay's running image is its own sealed memfd (dev `00:01`,
> `/memfd:` link, seals 15), not the extracted member (dev `103:05`); the same counter at
> the base `9ff76b1f` reads `own=1 met=True`. The round-51 `own` clause "the running image is
> the extracted member's dev and inode" is replaced by round-52 C1's `sealed` leg (own sealed
> memfd, `nlink` 0, `/memfd:`, seals 15, `own_server` and `server_exe` agreeing with the
> counter's own `/proc/<pid>/exe`), which reads `bind=1 sealed=1 teardown=1 newrow=1
> bound=3/3 sealedruns=3/3 met=True` at the same tip - the clause it replaces was the one
> closure D5 showed a copy or hardlink at the member path could meet. `round50-replay-bind-audit.py`
> still reads `met=True` at the build, so operability is intact; the round-51 counter is
> retired as a live instrument (its round-51 measurement stands as history).
