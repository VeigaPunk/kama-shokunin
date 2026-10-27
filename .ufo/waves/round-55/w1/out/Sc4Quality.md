# Sc4Quality — round 55 criterion proposal (KQ98/KQ99)

**Verdict:** two QUALITY.md rows are proposed — KQ98 (a kill mutation must land inside a
sampling counter's guaranteed observation window, synchronously; a delayed/threaded flip is
a timing probe, never the named kill) and KQ99 (an env-vector kill is admitted only as a
name-presence kill or as a load-effect kill *after* the object is shown to load on the
measured host's libc; a void vector belongs in the preregistration as a passing vector
analysis). Both are grounded in the round-55 battery receipts, the counter's source order,
and one direct glibc 2.44 probe; the proposal also reports a conflict between the frozen
preregistration's mutant list and the battery that ran, and does not adjudicate it.

Assignment: draft KQ98 wording for the battery's two design lessons, citing receipts.
Proposal only — no lane file was edited, no counter was rerun, no service was started, no
tool was installed.

## Evidence (read, not reproduced)

| Fact | Source |
|---|---|
| first battery run's delayed/threaded post-mapping flip printed `met=True`; counter "can observe and release inside 300 ms" | `.ufo/waves/round-55/c1/battery/run-battery.py:66-68` (owner comment; the authors' 300 ms is not measured by this seat) |
| every attempt writes the same receipt path, so the first-run receipt is gone | `run-battery.py:107` — `outp = os.path.join(OUT, f"{name}.out")`; `ls .ufo/waves/round-55/c1/battery/` shows one `m-member-flip.out` only |
| sampler instants: two back-to-back passes, then release; rehash only after the replay exits | `tools/round54-replay-code-audit.py:709-721` and `:768-780` |
| synchronous rehash mutant kills | `m-member-flip.out:2` → `... rehash=3 met=False`; `:9` same inode, different digest |
| synchronous code-leg mutant kills | `m-text-flip.out:2` → `bind=0 ... code=0 ... rehash=3 met=False`; `:17` names `libggml-rpc.so` |
| positive control passes | `control.out:2` → `met=True`, `rehash=0`; `:5` 8 archive files + 13 root-owned host files |
| `LD_AUDIT` mutant passed with the object never mapped | `m-ldaudit-foreign.out:2` → `hostlibs=3/3 met=True`; `:5` 13 host files (same as control); `:6` 6 env names (control has 5). Same shape in `m-ldaudit-writable.out:2,5,6` |
| mutant list still names both LD_AUDIT attempts as kills | `.ufo/waves/round-55/preregistration.json:44`; target `:19`; kill rule `:20` |
| harness reclassifies the foreign vector as one that must pass | `run-battery.py:50-63,137-138` (`ok = rc == 0 and met`) |
| libexpat cannot be an audit module | `nm -D --defined-only /usr/lib/libexpat.so.1.13.0 \| grep -c ' la_version$'` → `0` |
| glibc ignores `LD_AUDIT` of a non-audit DSO | `kq99-ldaudit-probe.txt` (this seat): non-audit DSO → 0 mapped rows, stderr "cannot be loaded as audit interface: undefined symbol: la_version; ignored"; audit-capable DSO → 5 mapped rows; `LD_PRELOAD` of the same DSO → 5 mapped rows |
| prereg identical to the freeze blob | `git show 9c60eae:.ufo/waves/round-55/preregistration.json \| diff - .ufo/waves/round-55/preregistration.json` → no output (`IDENTICAL`) |

Counter sha256 unchanged: `c81fe971…79af` (`tools/round54-replay-code-audit.py`); the
preregistration's `counter_sha256` matches. Receipt line numbers cited are the committed
files' lines; receipt mtimes in the lane are not evidence (working-copy materialisation
postdates the commit that contains them).

## Proposal

- `.ufo/waves/round-55/w1/out/Sc4Quality/kq98-proposal.md` — full proposal: evidence table,
  the two rows with clause-by-clause grounding, findings, limits, numbering note (append
  after KQ97 at `corpus/QUALITY.md:477`; if one composite row is preferred, merge KQ99's
  env-vector clause into KQ98 and later rows need no renumbering).
- `.ufo/waves/round-55/w1/out/Sc4Quality/kq98-rows.md` — pasteable blocks: the
  `## Criteria added — round 55` table, and the two `Mistakes` rows for
  `corpus/lessons/round-55.md` (neither lesson is in that file today; a Motivating lesson
  column naming a lesson that does not carry the lesson repeats round-51 closure D7,
  `corpus/QUALITY.md:458`). Admit the lesson rows first.

## Findings (reported; nothing fixed in place)

1. **F1 — frozen prereg vs. shipped battery.** `preregistration.json:44` names
   `m-ldaudit-writable (code leg)` and `m-ldaudit-foreign (hostlibs leg)` as mutants; `:19`
   requires each named mutant's receipt to print `met=False`; `:20` falsifies the claim if
   any battery mutant prints `met=True`. Both receipts print `met=True`
   (`m-ldaudit-writable.out:2`, `m-ldaudit-foreign.out:2`) because the loader ignored the
   vector (probe above). The harness and build commit `8abadfed` ("3 live kills + 1 vector
   analysis") treat the foreign one as a vector that must pass. The prereg is frozen and
   unamended, so its mutant list and target no longer describe the battery that ran.
   Whether the literal kill rule is thereby triggered is the canonical judge's call.
2. **F2 — orphan receipt.** `m-ldaudit-writable.out` has no mutant in `run-battery.py`; a
   reader walking `.ufo/waves/round-55/c1/battery/` grades it as a named mutant and reads
   `met=True` as a missed kill. Label it as a retired first-run LD_AUDIT attempt, or add a
   directory index naming current vs. superseded receipts.
3. **F3 — a passing attempt leaves no receipt.** `run-battery.py:107` overwrites
   `{name}.out`, which is how the only artifact of the race was lost. Proposed minimal fix
   (suffix on collision, first-run names preserved):
   `.ufo/waves/round-55/w1/out/Sc4Quality/proposed-fix-run-battery-receipts.diff`.
   Validated in scratch only: `patch -p1 --dry-run` → `dry-run exit=0`; after applying,
   `python3 -m py_compile` → `compile exit=0`. The lane file was not touched.
4. **F4 — `m-extra-in-tree.out` is a legitimate pass, not a missed kill** (it is not in the
   mutant list; its receipt shows the extra tree file never stayed mapped). Named so the
   "any battery mutant prints met=True" wording is not read against it.

## Limits

- KQ98's race clause rests on the owner comment plus the counter's code order: the
  first-run receipt that would prove it was overwritten (F3), so the proposal says so
  rather than upgrading the comment into a receipt.
- The `m-ldaudit-writable` DSO path is unrecoverable (the counter records environment
  names only, values never read), so it is cited as a second passing LD_AUDIT attempt, not
  as proof of which object it named.
- The probe tests glibc's loader, not the counter; it is the pre-freeze check KQ99 asks a
  future author to run, demonstrated once on this host (glibc 2.44, Linux 7.2.11).

## Artifacts

- report: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Sc4Quality.md`
- proposal: `…/w1/out/Sc4Quality/kq98-proposal.md`
- pasteable rows: `…/w1/out/Sc4Quality/kq98-rows.md`
- proposed harness diff: `…/w1/out/Sc4Quality/proposed-fix-run-battery-receipts.diff`
- probe receipt + sources: `…/w1/out/Sc4Quality/kq99-ldaudit-probe.txt`, `…/probe/{probe.py,child.c,nonaudit.c,audit.c}`
- cited receipt copies (byte copies, digests in `SHA256SUMS`): `…/w1/out/Sc4Quality/receipts/` (7 battery `.out` files, `run-battery.py`, `preregistration.json`)

Scratch `/fast/scratch/hyaku/kama-r55/w1/Sc4Quality` removed after copying; no llama-server
was started and no process of this seat survives. No pacman; no installs.
