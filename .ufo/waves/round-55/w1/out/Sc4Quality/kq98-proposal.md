# KQ98 / KQ99 — QUALITY.md criterion proposal (round 55, lane kama)

Status: **proposal only, not a commit.** Nothing in this directory has been applied to
`corpus/QUALITY.md` or `corpus/lessons/round-55.md`; the lane tree was read-only for this
seat. Target is `corpus/QUALITY.md`, as an appended `## Criteria added — round 55`
section (append so no existing line moves).

Numbering: the last admitted row is KQ97 (`corpus/QUALITY.md:477`), so round 55 takes
KQ98 and KQ99 — one row per lesson, because the two admissions have different rules
(timing of a mutation vs. evidential status of an environment vector). If the integrator
wants a single composite row, take KQ98's admit cell and append KQ99's env-vector clause;
KQ99 then vanishes and later rows do not need renumbering.

Each row is written in the file's four-column voice. The two lessons they encode are not
yet in `corpus/lessons/round-55.md` Mistakes, so the admission has a prerequisite (§3):
a row whose Motivating lesson column names a lesson file that does not carry the lesson
repeats the round-51 closure D7 defect that produced KQ89/KQ90 (`corpus/QUALITY.md:458`).

---

## 1. Evidence read for this proposal

No counter was rerun; no lane file was edited. All facts below are receipt lines, counter
source lines, or one 1.6 s probe run in scratch (`receipts/` holds byte copies, sha256
listed in `receipts/SHA256SUMS`).

| # | Evidence | Line / fact |
|---|---|---|
| E1 | `.ufo/waves/round-55/c1/battery/run-battery.py:66-68` | owner comment: "Synchronous: the counter can observe and release inside 300 ms, so a delayed threaded flip races the re-hash (the first battery run showed met=True for it)." |
| E2 | `.ufo/waves/round-55/c1/battery/run-battery.py:107` | `outp = os.path.join(OUT, f"{name}.out")` — every attempt of a mutant writes the same path, so a superseded attempt's receipt is overwritten |
| E3 | `tools/round54-replay-code-audit.py:709-721` | two `code_observe(..., collect=True)` passes back to back, then the `release` marker is written immediately; no sleep between them |
| E4 | `tools/round54-replay-code-audit.py:768-780` | the rehash (`J7Late facet 1`) runs only after `p.wait(...)`, i.e. after the replay exits; it stats and re-hashes each observed path |
| E5 | `.ufo/waves/round-55/c1/battery/m-member-flip.out:2` | final synchronous rehash mutant: `... rehash=3 met=False`; `:9` shows the change with equal inode and different digest (in-place rewrite of `libggml-cpu-zen4.so`) |
| E6 | `.ufo/waves/round-55/c1/battery/m-text-flip.out:2` | pre-Popen flip: `bind=0 ... code=0 ... rehash=3 met=False`; `:17` names `libggml-rpc.so` changed after the observation |
| E7 | `.ufo/waves/round-55/c1/battery/control.out:2,5` | unmutated positive control: `met=True`, "8 archive files ... 13 root-owned host files" |
| E8 | `.ufo/waves/round-55/c1/battery/m-ldpreload.out:2,9` | `envnames=0/3 met=False`, detail "server environment carries LD_PRELOAD" — the kill is the *name*, not a loaded object |
| E9 | `.ufo/waves/round-55/c1/battery/m-ldaudit-foreign.out:2,5,6` | `hostlibs=3/3 met=True`, "13 root-owned host files" (same as E7), "6 environment variable names" (one more than E7's 5) |
| E10 | `.ufo/waves/round-55/c1/battery/m-ldaudit-writable.out:2,5,6` | same shape: `met=True`, 13 host files, 6 env names |
| E11 | `.ufo/waves/round-55/preregistration.json:44` | mutants list still names `m-ldaudit-writable (code leg)` and `m-ldaudit-foreign (hostlibs leg)` |
| E12 | `.ufo/waves/round-55/preregistration.json:19,20` | target: "each named mutant receipt prints met=False (exit 1) with its named leg failing"; kill rule: "the claim is falsified if ... any battery mutant prints met=True" |
| E13 | `.ufo/waves/round-55/c1/battery/run-battery.py:50-63,137-138` | the harness reclassifies `m-ldaudit-foreign` as `"vector"` — `ok = rc == 0 and met`, i.e. the passing receipt *is* the finding — and records why the live hostlibs kill is root-gated |
| E14 | `nm -D --defined-only /usr/lib/libexpat.so.1.13.0` | 0 definitions of `la_version` (the DSO E9's mutant passed to `LD_AUDIT` via `run-battery.py:62`) |
| E15 | probe receipt `kq99-ldaudit-probe.txt` (this seat) | glibc 2.44: `LD_AUDIT=<DSO without la_version>` → not mapped, stderr "cannot be loaded as audit interface: undefined symbol: la_version; ignored"; `LD_AUDIT=<DSO exporting la_version>` → 5 mapped rows; `LD_PRELOAD=<same non-audit DSO>` → 5 mapped rows |

Inferences stated as such, not as observations:

- From E3+E4+E1 [INFERENCE]: the sampler's guaranteed instants are the two passes and the
  post-exit re-hash; a mutation that fires outside them is unobserved *by construction*
  and is exactly the sampling limit the preregistration already declares ("the counter
  samples state (two passes and a post-exit re-hash), so a library rewritten and restored
  between those instants is not observed", `preregistration.json` limits). The "300 ms"
  figure in E1 is the owner's number, not measured by this seat.
- From E9+E7+E14+E15 [INFERENCE, strong]: libexpat was never mapped into the replay's
  server — otherwise the counter would have counted 14 root-owned host files and failed
  the code leg with "root-owned host library" (`tools/round54-replay-code-audit.py:564`,
  hostlibs leg derived at `:825`), not 13.
- E10's DSO path is not recoverable: the counter records environment *names* only
  (`envkeys`, values never read), and the mutant no longer exists in the harness. The
  receipt shows *that* an LD_AUDIT mutant passed, not *which* object it named.

Timestamps are not evidence here: the receipts' mtimes (10:30–10:44) postdate the commit
that contains them (`8abadfed`, committer date 10:52:56, author date 10:24:22), because
the lane's working copy was materialised again after the commit. Every claim above is
therefore anchored to receipt *content* and to source line numbers.

---

## 2. Proposed rows (pasteable; also as a plain block in `kq98-rows.md`)

### KQ98 — a kill mutation must land inside the sampler's window

| ID | Admit only when | Reject or limit when | Motivating lesson |
|---|---|---|---|
| KQ98 | A kill-battery receipt that is meant to fail a sampling leg applies its mutation synchronously at an instant the sampler is guaranteed to read — for a post-mapping file flip, on disk before the observation passes and before the post-exit re-hash — and the receipt names the leg, the changed path and the changed digest; a mutation whose timing is delayed or threaded is admitted only as a timing probe that reports its outcome over repeated runs, never as the named kill, and a superseded attempt's receipt stays beside the final one | a delayed/threaded post-mapping flip offered as the rehash-leg kill: it can fire after two back-to-back observation passes and after the post-exit re-hash, so the frozen counter prints `met=True` and the run is filed as a defect in the leg instead of a mutant that never landed; a passing first attempt deleted by the harness's `{name}.out` overwrite, leaving the lesson recorded only in a code comment | `corpus/lessons/round-55.md` Mistakes (timing-race row); `.ufo/waves/round-55/c1/battery/run-battery.py:66-68,107`; `battery/m-member-flip.out:2,9` and `battery/m-text-flip.out:2,17` (synchronous variants: `rehash=3`/`code=0`, `met=False`); `tools/round54-replay-code-audit.py:709-721,768-780` |

### KQ99 — an env-vector kill must be shown to load before it is named a kill

| ID | Admit only when | Reject or limit when | Motivating lesson |
|---|---|---|---|
| KQ99 | An env-vector kill (`LD_PRELOAD`, `LD_AUDIT`, `LD_LIBRARY_PATH`, …) is admitted as exactly one of two kinds and the receipt says which: a name-presence kill, where the frozen leg fails on the variable name alone, or a load-effect kill, where the vector has first been shown — on the measured host's libc, before the freeze — to load the injected object into the child (the object appears in the child's maps; an audit DSO must export `la_version`) and the named leg fails on that object; a vector that reaches the child's environment but loads nothing is written into the preregistration as a passing vector analysis, never listed among the mutants whose receipts must print `met=False` | the `LD_AUDIT` hostlibs kill: glibc 2.44 refuses `LD_AUDIT` for a DSO that is not an audit module ("cannot be loaded as audit interface: undefined symbol: la_version; ignored"), so libexpat was never mapped — two receipts print `hostlibs=3/3 met=True` with 6 env names and the control's 13 host files while the frozen preregistration still names both as mutants whose receipts must print `met=False`, under a kill rule that falsifies on any passing battery mutant; a same-uid host library is not a substitute kill (the code/archive classification fails first), so the live hostlibs leg stays root-gated | `corpus/lessons/round-55.md` Mistakes (env-vector row); probe `kq99-ldaudit-probe.txt` (audit-capable DSO maps, non-audit DSO does not, `LD_PRELOAD` maps it); `battery/m-ldaudit-foreign.out:2,5,6`, `battery/m-ldaudit-writable.out:2,6`, `battery/control.out:5`, `battery/run-battery.py:50-63,137-138`, `preregistration.json:19,20,44` |

Why two rows rather than one: KQ98 is about *when* a mutation fires (a design rule for any
sampling counter); KQ99 is about *what a receipt may be called* (a preregistration rule for
environment vectors). Merging them would let a load-effect clause be satisfied by a timing
argument and vice versa, which is the failure each row exists to block.

---

## 3. Prerequisite: two Mistakes rows for `corpus/lessons/round-55.md`

Neither lesson is in that file's Mistakes section today (it has vacuous-kill-rule,
do-nothing-control and landing rows only). QUALITY rows cite lessons (round-51 closure D7,
`corpus/QUALITY.md:458`), so append these two rows *before* admitting KQ98/KQ99, or keep the
rows out until the round-55 lesson is amended. Pasteable text is in `kq98-rows.md` §2.

Second row's honesty constraint: it must report the frozen-prereg conflict and stop there.
Whether the literal kill rule ("if any battery mutant prints met=True") falsifies C1 when
the harness and the build commit call `m-ldaudit-foreign` a vector is **not** decided by
this seat; the row says so and leaves it to the canonical judge.

---

## 4. Findings (reported, not fixed)

F1 — **Frozen preregistration vs. shipped battery.** `preregistration.json:44` lists
`m-ldaudit-writable (code leg)` and `m-ldaudit-foreign (hostlibs leg)` as mutants;
`:19` requires each named mutant's receipt to print `met=False`; `:20` falsifies the claim
if any battery mutant prints `met=True`. `m-ldaudit-writable.out:2` and
`m-ldaudit-foreign.out:2` print `met=True`. The harness (`run-battery.py:50-63,137-138`)
declares `m-ldaudit-foreign` a vector that must pass, and the build commit
`8abadfed` says "3 live kills + 1 vector analysis"; the frozen file itself was not and
cannot be amended (it is identical to the freeze commit's blob — checked with
`git show 9c60eae:.ufo/waves/round-55/preregistration.json | diff - .ufo/waves/round-55/preregistration.json`).
Consequence: the target and kill-rule sentences no longer describe the battery that ran.
This is the motivating defect for KQ99; the adjudication is the judge's.

F2 — **Orphan receipt in the battery directory.** `m-ldaudit-writable.out` has no mutant
in `run-battery.py`: a reader walking `.ufo/waves/round-55/c1/battery/` grades it as a
named mutant and reads `met=True` as a missed kill. Either the receipt is labelled as a
retired vector attempt (it is the first-run LD_AUDIT attempt) or the directory gains a
one-line index stating which receipts belong to the current harness and which are
superseded attempts.

F3 — **A passing attempt leaves no receipt.** `run-battery.py:107` writes `{name}.out`
unconditionally, so the first `m-member-flip` attempt — the only artifact of the race —
was overwritten; E1's comment is now the sole record. Proposed minimal fix in
`proposed-fix-run-battery-receipts.diff` (suffix on collision; first-run names unchanged,
so the committed receipts stay valid).

F4 — **`m-extra-in-tree.out` is a legitimate pass, not a missed kill.** It is not in the
preregistration's mutant list and its receipt (`met=True`) shows the extra tree file never
stayed mapped (E7/E9-style 8 archive files). No action; named so a later reader does not
mistake it for a battery failure under the "any battery mutant" wording.

---

## 5. Limits of this proposal

- It does not re-derive C1's measurement and does not rerun either frozen counter
  (constraint). E1's "300 ms" and the first-run `met=True` are the owner's recordings;
  their receipt is gone (F3), so KQ98's race clause rests on a comment plus the counter's
  code order, not on a surviving pass receipt.
- It does not adjudicate F1.
- E10's vector is unattributable (path not recorded by design), so KQ99's load-effect
  clause is grounded on E9+E14+E15 only; the writable receipt is cited as a second
  passing LD_AUDIT attempt, not as proof of which object it named.
- The probe was run in this seat's scratch with the host's `cc`; it tests glibc's loader
  behavior, not the counter. It is the check KQ99 asks a future author to run before the
  freeze, demonstrated once.
