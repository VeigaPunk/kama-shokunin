# Pasteable blocks — round 55 criterion proposal (KQ98, KQ99)

Two blocks: §1 appends to `corpus/QUALITY.md`; §2 appends two rows to the Mistakes section
of `corpus/lessons/round-55.md`. Admit §2 first: a Motivating lesson column that names a
lesson file not carrying the lesson repeats round-51 closure D7 (`corpus/QUALITY.md:458`).
Both blocks are append-only; no existing line moves.

## 1. For `corpus/QUALITY.md` (append at end of file)

```markdown
## Criteria added — round 55 (each cites `corpus/lessons/round-55.md`)

Same columns as the table above; appended at the end so no existing line moves. KQ98
records the timing rule a kill mutation must satisfy against a sampling counter; KQ99
records when an environment vector may be called a kill rather than a vector analysis.

| ID | Admit only when | Reject or limit when | Motivating lesson |
|---|---|---|---|
| KQ98 | A kill-battery receipt that is meant to fail a sampling leg applies its mutation synchronously at an instant the sampler is guaranteed to read — for a post-mapping file flip, on disk before the observation passes and before the post-exit re-hash — and the receipt names the leg, the changed path and the changed digest; a mutation whose timing is delayed or threaded is admitted only as a timing probe that reports its outcome over repeated runs, never as the named kill, and a superseded attempt's receipt stays beside the final one | a delayed/threaded post-mapping flip offered as the rehash-leg kill: it can fire after two back-to-back observation passes and after the post-exit re-hash, so the frozen counter prints `met=True` and the run is filed as a defect in the leg instead of a mutant that never landed; a passing first attempt deleted by the harness's `{name}.out` overwrite, leaving the lesson recorded only in a code comment | `corpus/lessons/round-55.md` Mistakes (timing-race row); `.ufo/waves/round-55/c1/battery/run-battery.py:66-68,107`; `battery/m-member-flip.out:2,9` and `battery/m-text-flip.out:2,17` (synchronous variants: `rehash=3`/`code=0`, `met=False`); `tools/round54-replay-code-audit.py:709-721,768-780` |
| KQ99 | An env-vector kill (`LD_PRELOAD`, `LD_AUDIT`, `LD_LIBRARY_PATH`, …) is admitted as exactly one of two kinds and the receipt says which: a name-presence kill, where the frozen leg fails on the variable name alone, or a load-effect kill, where the vector has first been shown — on the measured host's libc, before the freeze — to load the injected object into the child (the object appears in the child's maps; an audit DSO must export `la_version`) and the named leg fails on that object; a vector that reaches the child's environment but loads nothing is written into the preregistration as a passing vector analysis, never listed among the mutants whose receipts must print `met=False` | the `LD_AUDIT` hostlibs kill: glibc 2.44 refuses `LD_AUDIT` for a DSO that is not an audit module ("cannot be loaded as audit interface: undefined symbol: la_version; ignored"), so libexpat was never mapped — two receipts print `hostlibs=3/3 met=True` with 6 env names and the control's 13 host files while the frozen preregistration still names both as mutants whose receipts must print `met=False`, under a kill rule that falsifies on any passing battery mutant; a same-uid host library is not a substitute kill (the code/archive classification fails first), so the live hostlibs leg stays root-gated | `corpus/lessons/round-55.md` Mistakes (env-vector row); probe `kq99-ldaudit-probe.txt` (audit-capable DSO maps, non-audit DSO does not, `LD_PRELOAD` maps it); `battery/m-ldaudit-foreign.out:2,5,6`, `battery/m-ldaudit-writable.out:2,6`, `battery/control.out:5`, `battery/run-battery.py:50-63,137-138`, `preregistration.json:19,20,44` |
```

(The `battery/…` and `preregistration.json` refs are relative to
`.ufo/waves/round-55/`. The probe receipt lives in
`.ufo/waves/round-55/w1/out/Sc4Quality/kq99-ldaudit-probe.txt`.)

## 2. For `corpus/lessons/round-55.md` (append to the Mistakes list)

```markdown
- **class: unfalsified — a timing race filed as a kill (or as a broken leg).**
  Evidence: the first round-55 battery run applied the post-mapping flip on a delayed
  thread; the frozen counter printed `met=True` (`run-battery.py:66-68`, owner-recorded —
  no first-run receipt survives, because the harness writes every attempt to
  `{name}.out`, `run-battery.py:107`). The counter reads two back-to-back observation
  passes and writes its release marker immediately after
  (`tools/round54-replay-code-audit.py:709-721`), and re-hashes only after the replay
  exits (`:768-780`), so a flip that fires outside those instants is unobserved by
  construction — the sampling limit the preregistration already names, not a defect in
  the rehash leg. Captured-by: none — no criterion required a battery mutation to land
  inside the sampler's window, or a superseded attempt's receipt to be kept.
  Fix: the mutant flips synchronously at the receipt's `code_mappings` write, before both
  passes and the re-hash; `m-member-flip.out:2` (`rehash=3`, `met=False`) and
  `m-text-flip.out:2` (`code=0`, `met=False`) are the kills. Fix shown able to fail: the
  synchronous variants fail their named legs while the unmutated control passes
  (`control.out:2`).
- **class: preregistration — an env vector the host's loader ignores.**
  Evidence: the frozen preregistration lists `m-ldaudit-writable` (code leg) and
  `m-ldaudit-foreign` (hostlibs leg) among the battery mutants whose receipts must print
  `met=False` (`preregistration.json:44`, target `:19`) under a kill rule that falsifies
  on any passing battery mutant (`:20`); both receipts print `met=True`
  (`m-ldaudit-writable.out:2`, `m-ldaudit-foreign.out:2`) with 6 environment variable
  names (`:6`) and the control's 13 root-owned host files (`control.out:5`), so the DSO
  was never mapped. Direct probe (receipt `w1/out/Sc4Quality/kq99-ldaudit-probe.txt`):
  glibc 2.44 refuses `LD_AUDIT` for a DSO without `la_version` ("cannot be loaded as
  audit interface: undefined symbol: la_version; ignored") and maps one that exports it;
  the same non-audit DSO maps under `LD_PRELOAD`, so the probe distinguishes a void
  vector from a working one. The harness reclassifies `m-ldaudit-foreign` as a vector
  that must pass (`run-battery.py:50-63,137-138`) and the build commit reports "3 live
  kills + 1 vector analysis", but the frozen preregistration cannot be amended, so its
  mutant list and target no longer describe the battery that ran; whether that meets the
  kill rule's literal wording is the canonical judge's call, not this seat's.
  Captured-by: none — the freeze procedure did not require an env vector to be exercised
  on the host's libc before it was named a kill.
  Fix: exercise the vector before the freeze and, when it is void, write it into the
  preregistration as a passing vector analysis; the live hostlibs kill stays root-gated
  because a same-uid mapping fails the code/archive classification first
  (`run-battery.py:50-56`). Fix shown able to fail: the probe maps the audit-capable DSO,
  so "loads" and "void" are distinguishable.
```
