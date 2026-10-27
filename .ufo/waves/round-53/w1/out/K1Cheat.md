# K1Cheat — round 53 C1 shortcut attack on the frozen counter

**Verdict: CONFIRMED SHORTCUT.** Two env-whitelist edits (4 lines) in a fixture clone plus a
2 KB root-owned host library make the frozen counter `tools/round53-replay-code-audit.py`
report `met=True` at a tree whose server executes code that is not the archive's: the
library's constructor maps an anonymous RWX page, writes shellcode into it, and executes it
*inside the observed server, inside the counter's own measurement window*. The frozen
predicate is satisfied in its letter ("every one of whose executable *file* mappings") while
its intent — the docstring question, "is every piece of code the replay's server executes
either the release archive's own bytes … or a root-owned host library" — is violated: an
anonymous executable page is not a file mapping at all, and the root-owned library's bytes
are never compared with anything.

## The fixture (cheapest change that meets the counter)

Fixture clone: `git clone --shared` of the lane at scratch, checked out at the build commit
`c22602bd8d83ab26349d1087e916ca537ee4f9d1`, then commit `cd34c183f0d6daf35d8f6aaea41068bf6b1a6dd6`
(identity `fx <fx@invalid>`; full diff in `K1Cheat/fixture.patch`):

1. `tools/kama-live-replay.py` `live_env()` — add two lines:
   `env["LD_PRELOAD"] = "/usr/local/lib/kama-r53-cheat.so"` and a marker path.
2. `tools/kama-llamacpp-live.py` `CHILD_ENV_KEYS` — add `"LD_PRELOAD"`, `"KAMA_CHEAT_MARKER"`
   so the server inherits the preload (the counter's own env passes neither; the injection
   lives entirely in the measured tree, which is what the counter archives and runs).

The library (`K1Cheat/cheat.c`, built with the system `gcc`, installed
`sudo install -o root -g root -m 0755` → `/usr/local/lib/kama-r53-cheat.so`,
sha256 `f70eada7e3850349c2a8569227d4f9eef22c2f6fcd0a9f4aa34a89b9a8284f00`, since removed):
its ELF constructor `mmap`s an anonymous `PROT_READ|PROT_WRITE|PROT_EXEC` page, copies
`mov $42,%eax; ret` into it, calls it, and writes a per-pid JSON marker.

Nothing else in the tree was touched; the archive, model, receipts, and all round-52 legs
are the frozen ones.

## Evidence

- Direct witnessed replay of the clone (driver `K1Cheat/evidence-run.sh`), server pid 3187650:
  `K1Cheat/maps-during-hold.txt:138` shows `7fc4c00fd000-7fc4c00fe000 rwxp 00000000 00:00 0`
  — an executable page with **no pathname**; lines 193–197 show
  `/usr/local/lib/kama-r53-cheat.so` with an `r-xp` mapping (line 194).
  `K1Cheat/cheat-marker.server-direct-run.json` (written by the server itself) records
  `"anon_rwx_page_mapped": true`, `"shellcode_call_result": 42`, and a `maps_line` whose
  address equals the server's actual rwx page. `K1Cheat/ev.json`: `match: True`,
  `mismatches: []`, `own_code.verified: true`.
- The frozen counter, run exactly as specified:
  `python3 tools/round53-replay-code-audit.py --repo <clone> --tip cd34c183… --scratch $S --out K1Cheat/c1-cheat.out`
  → exit 0, full receipt in `K1Cheat/c1-cheat.out`:
  `bind=1 sealed=1 code=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 coderuns=3/3 met=True`.
  Every code leg reports "8 archive files … byte-equal …, **14** root-owned host files" —
  the reference build receipt (`K1Cheat/c1-build-reference.out`) reports **13**; the +1 is
  the cheat library, counted as a benign host file.
- `K1Cheat/cheat-marker.server-counter-b{1,2,3}.json`: the three server pids the counter
  itself observed (3220597, 3234455, 3241289) each executed the anonymous shellcode
  (result 42) — the cheat ran inside the counter's own measurement window, not just mine.
- Cleanup verified: `/usr/local/lib/kama-r53-cheat.so` removed (`ls` → No such file),
  `pgrep -af llama-server` → none. Scratch removed after copying artifacts. No packages
  installed (pacman paused host-wide; system `gcc` used as-is; `sudo` used only to install
  and remove the fixture library).

## Why the counter passes it (code references)

- `tools/round53-replay-code-audit.py:413` — `code_observe` examines only maps rows with a
  pathname: `len(f) < 6 or "x" not in f[1] or not f[5].startswith("/")`. Anonymous
  executable pages (`rwxp … 00:00 0` with no path) are skipped, never read from
  /proc/<pid>/mem, never cross-checked. Same filter in the live tool
  `tools/kama-llamacpp-live.py:793` (`code_mappings`), so the receipt is blind the same way.
- `tools/round53-replay-code-audit.py:447` — the host branch accepts any executable mapping
  with `st_uid == 0`, the row's inode, and `not os.access(path, W_OK)`. Bytes are never
  compared for host files (a declared preregistration limit), so a root-owned
  attacker-planted library is indistinguishable from libc. The receipt-side
  `verify_code` (`tools/kama-live-replay.py:332-335`) admits `uid==0` the same way; the
  counter's post-release cross-check only iterates the archive-member mappings it saw
  (`bind_one`), so the extra receipt entry is never compared against anything.
- The predicate's quantifier is "executable **file** mappings" (preregistration C1), so the
  anonymous page is outside the claim's wording altogether — a wording hole on top of the
  instrumentation hole.

## The four candidate attacks, cheapest first

1. **Root-owned LD_PRELOAD library — WINNER, demonstrated above.** Cost: two env lines +
   a tiny .so + one root install. The library's constructors run before `main` in the
   server; its mapping passes as a "root-owned host file"; arbitrary code executes. Note
   the preregistration's ablation control list anticipated "LD_PRELOAD of a *user-owned*
   copy" — the counter catches the user-owned case (`uid != 0` → problem), but a root-owned
   copy is trusted by design, and root (or any seat with sudo, as this attack used) is
   inside the counter's trust boundary.
2. **Anonymous executable page — demonstrated in the same artifact.** Strictly stronger as
   evidence: zero executable *file* mappings betray it. Independent of LD_PRELOAD: any
   loaded code path (including a compromised-but-byte-matching archive member, or a host
   lib) can create one. Invisible to both the counter and `code_mappings`.
3. **Path-text lie (` (deleted)` name) — FAILS, closed.** A deleted-path row under the tree
   is "not a regular member of the archive" (`code_observe` appends a problem, code=0); a
   host one is unstattable (problem too). The live tool records `opened: False`
   (`code_mappings`) and `verify_code` flags `code-mapping:unopened`. Verified by code
   reading; no run needed.
4. **dlopen after the counter's single read — real but weaker, and a declared limit
   ("C1: the counter reads memory once…").** It needs an execution vector already (idea 1)
   and only escapes the one read; idea 1 runs code *during* the observed window, so this
   adds nothing.

## Impact

- Axis: **operability** (C1). The measured claim's capability depth ("the code the server
  executes is the archive's own bytes") is met at the frozen predicate level by a server
  running arbitrary non-archive code. Against a non-root actor the counter stands (the
  user-owned LD_PRELOAD control fails as designed); against an operator-level actor (any
  seat with sudo — the lane's own tooling directive grants it) it does not. The judge
  should weigh whether "root can cheat" is in scope for operability 8→8; the anonymous-page
  gap, though, needs no root at all to *define* — it is a pure wording/instrumentation hole.
- False provenance: none — receipts are honest about what they saw; the predicate simply
  does not ask the right question.

## Smallest safe correction (proposal for L1/judge; nothing edited in place)

1. In `code_observe` (and `code_mappings` for symmetry), also enumerate anonymous
   executable mappings and fail the leg on any that is not the sealed memfd image (the
   image already names itself `/memfd:…`). A stock llama-server has no anonymous executable
   pages; JIT/hardening exceptions can be allowlisted by address range.
2. Bound the host-library set: record the server's environment variable *names* in the
   receipt and fail on `LD_PRELOAD`/`LD_LIBRARY_PATH`-style names, and/or require each
   root-owned host library to hash-match the host package database (`pacman -Qo` / file
   list), or at minimum diff the host-library set against a baseline so a *new* root-owned
   library is flagged rather than silently counted (14 vs 13 passed unnoticed).
3. Next round, tighten the predicate wording from "executable file mappings" to "every
   executable mapping" — the docstring question already says "every piece of code the
   replay's server executes".

## Artifacts (`.ufo/waves/round-53/w1/out/K1Cheat/`)

`fixture.patch` (the 4-line measured-tree change), `cheat.c`, `kama-r53-cheat.so`,
`cheat.so.sha256`, `evidence-run.sh`, `maps-during-hold.txt`, `maps-cheat-lines.txt`,
`cheat-marker.server-direct-run.json`, `cheat-marker.server-counter-b{1,2,3}.json`,
`ev.json`, `c1-cheat.out` (the counter's met=True receipt), `c1-build-reference.out`.
