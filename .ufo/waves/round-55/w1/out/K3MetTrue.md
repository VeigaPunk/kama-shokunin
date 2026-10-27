# K3MetTrue — round 55 w1: "What met=True does not show" for C1 and C2

Verdict: both limits paragraphs are written and evidence-grounded; C1's five required
limits (plus the anon-leg design-only note) and C2's three are confirmed against the
frozen counters and the committed receipts, every named limit cites its receipt, and
the round-53/54 closure attributions check out — but the review surfaced one real
defect outside the paragraph: two stale `met=True` probe receipts
(`m-ldaudit-writable.out`, `m-extra-in-tree.out`) sit committed in the kill-battery
dir that the frozen kill rule reads.

Seat: K3MetTrue (UFO-FSD critic, leaf). Measured commit: `9c60eae6f7ed84f7da93d219a406aadc30958c6c`
(round-55 freeze); lane tip at review `8abadfedf89f35372645b1e5d6ce4a2109186f90`.
Base `3a600d2f729828419aaea34cc402c8b0d20fb720` (round-54 tip); C2 counter-internal
BASE `0b75a84c56e024cac1662e8ff81802f249acb410` (round-53 tip, deliberately — the
drop horizon must include the round-54 re-anchor).

Deliverables in this seat's out dir
(`.ufo/waves/round-55/w1/out/K3MetTrue/`):

- `limits-paragraph.md` — the SCORECARD-series continuation, ready to land as
  `### What `met=True` does not show (round 55)`.
- `receipts/` — copies of every receipt cited (sha256 recorded below).
- `proposed-fix-stale-battery-receipts.md` — the unified-diff-style fix for the
  defect below.

No tools were installed or upgraded this seat; no counter was run (this is a
receipts-and-code review seat; the frozen counters were read, not executed). No
llama-server processes were started (`pgrep -af llama-server` clean at review time).

## 1. The honest-limits paragraph (seat deliverable)

Full text in `limits-paragraph.md`. Summary of the named limits, each with its
evidence receipt and closure status:

### C1 (operability 8→8) — `tools/round54-replay-code-audit.py`

1. **Sampling window.** The counter observes each server's archive ranges in two
   `/proc/<pid>/mem` passes and re-stat's/re-hashes observed archive paths once
   post-exit (`tools/round54-replay-code-audit.py:64-69`, `:714-717`, `:779-803`);
   rewrite-and-restore between/after those instants is unobserved (`:87-90`).
   Receipts: `measured/c1-build.out` (`twopass=3/3 rehash=0` — only the sampled
   instants agree); battery `m-member-flip.out` (`rehash=3 met=False`) and
   `m-text-flip.out` (`code=0 met=False`) show only in-window mutations being caught.
   Round-53 closure: "a mutation after the counter's single memory read is not
   observed" is **closed in part** by the twopass + rehash legs; the inter-instant
   window (J7Late facets 2 and 4 in part) remains.
2. **hostlibs-by-basename.** `HOST_LIBS` is a frozenset of 13 basenames
   (`tools/round54-replay-code-audit.py:134-146`); admission is by name only
   (`:555-564`). Receipt: `measured/c1-build.out` `hostlibs=3/3` with the "13
   root-owned host files" detail — no byte reference for the 13 exists anywhere.
   Round-53 closure: "does not compare the 13 root-owned host executable libraries
   against a byte reference" is **partially closed** — J5Preload's new-name plant now
   fails the leg, but the frozen 13 stay content-uncompared (round 54 Planned asked
   for allowlist/provenance; the allowlist landed, provenance did not).
3. **byte-identical-host-install.** Predicate compares mapped bytes to the counter's
   own download — bytes, not provenance (`tools/round54-replay-code-audit.py:72-93`);
   a byte-identical host install still meets. Receipt: none can show origin; this is
   the round-53 disclosed limit, re-disclosed by round 54 Planned, **still open**.
4. **model bytes uncompared.** `mapped_model` (`tools/round54-replay-code-audit.py:362-392`)
   stat's + hashes the on-disk model file at the mapped path once during `observe`
   (`:412`), records dev/inode only; no `/proc/<pid>/mem` read of the model mapping,
   no two-pass, no model re-hash; the rerun cross-check compares dev/inode, not bytes
   (`:739-741`). Receipt: `measured/c1-build.out` bind lines record "mapping dev
   103:05 inode …" with no model-digest detail; the 16 two-pass range reads cover
   archive members only. Round-53 disclosure "Data/RELRO segments and the model's
   mapped bytes are not compared" is **not closed** — round 54 Planned's "explore the
   model's mapped bytes without relying on a pathname" did not land.
5. **root-gated hostlibs kill.** Battery entry `m-ldaudit-foreign` is graded
   `kind="vector"` and passes (`c1/battery/m-ldaudit-foreign.out` `met=True`; runner
   `run-battery.py:40-51`, grading `:127-130`): on this glibc a non-root actor cannot
   LD_AUDIT a root-owned foreign lib into staying mapped, and any same-uid foreign
   mapping fails the code/archive classification first. The hostlibs leg has **no
   live kill** in the battery; its root-actor coverage is by-design (`:563-564`) plus
   this void-vector receipt.
6. (also in the preregistration's own limits line) **anon-leg isolation is
   design-only**: `anon=0` in every receipt; no same-uid mutant injects an anonymous
   executable page without tripping another leg (`tools/round54-replay-code-audit.py:505`).

### C2 (calibration 7→7) — `tools/round54-cited-path-check.py`

1. **existence/disposition not truth.** The counter checks resolution + ledger
   disposition, never content (`tools/round54-cited-path-check.py:8-13`, `evaluate`
   `:640-678`). Receipt: `measured/c2-build.out` `cited=693 unresolved=14
   disclosed=14`. Round-53 disclosure stands **open**; the bundled J12Hide class is
   **closed** by the dropped leg guarding all three surfaces (`:648-658`) —
   `controls/base.c2.out` `dropped=1 met=False` is the red-before receipt — and by the
   new `superseded` class (`:461-477`, row `registry/cited-path-corrections.tsv:46`).
2. **upstream digest-not-content.** Full-40-hex ref, pinned owner/repo for inventory
   tokens, fetched bytes sha256-compared to the surface-stated digest or frozen pin
   (`tools/round54-cited-path-check.py:526-568`); M10/M11 fail closed, M12 contrast
   discloses (`measured/c2-build.out`). This **closes** round-53 J11BadFixed
   (mutable-ref and wrong-digest classes). Residual: bytes at the pinned commit are
   validated, semantic content is not; a surface stating a wrong digest discloses if
   the upstream serves those bytes (check is self-referential to the stated digest).
3. **prose-token advisory.** Prose root tokens surface as `advisory:` lines
   (`tools/round54-cited-path-check.py:51-52`, `:236-241`, `:587-600`) and never
   gate. Receipt: `measured/c2-build.out`'s four advisories (`SCORECARD.md:425`
   `.ufo/waves/round-13/frozen/expected.json--quality`, `SCORECARD.md:597`
   `tools/registry`, `SCORECARD.md:2171` `corpus/knowledge/...`, `SKILL.md:652`
   `registry/docs/git`). Round-53 K4Cheat "prose citations were invisible" is
   **closed invisibility-wise**; they remain non-gating.

Also confirmed closed by legs (round-53/54 disclosures): Sen4Fixture `GIT_*`
redirection → `clean_env` in both counters (C1 `:163-170`, C2 `:198-202`, grounded by
S510/S511 `corpus/SOURCES.md:263-264`; exercised by every run incl. both base
controls); K1Cheat LD_PRELOAD plant → envnames leg (BAD_ENV `:146`, `env_leg`
`:429-438`; battery `m-ldpreload.out` `envnames=0/3 met=False`); J7Late facets 1/3 →
twopass+rehash (battery `m-member-flip.out`); Sen1Mem F1–F3 → archive-reference
immutability legs (`:47-56`, `ROW_CAP` `:147`); frozen-counter `/memfd:` skip → sealed
memfd by dev+inode with any other executable memfd failing (`:508-512`, `sealed_exe`
`:579-607`); `untracked`-note falsity → classes re-derived from git history scoped
BASE..tip (`:63-65`, `:158`); the vacuous-kill-rule mistake (round-55 lesson
`corpus/lessons/round-55.md` Mistakes #1) → red base controls + battery + 15 fixture
scenarios committed before data.

## 2. Defect found: stale `met=True` receipts in the kill-battery dir

The frozen kill rule (preregistration, C1) falsifies the claim "if any battery mutant
prints met=True". The committed battery dir
(`.ufo/waves/round-55/c1/battery/`, lane tip `8abadfed`) contains two receipts that
print `met=True` but are **not** mutants of the landed `run-battery.py` (its MUTANTS
dict writes only `control`, `m-ldpreload`, `m-text-flip`, `m-ldaudit-foreign`,
`m-member-flip`):

- `m-ldaudit-writable.out` — `tip=23dc15dae61f04e86efb62ef2e622154bc4db36a … met=True`, mtime 10:30 (first code-leg attempt; LD_AUDIT of a writable lib is also a void vector);
- `m-extra-in-tree.out` — `tip=312530a9bcfad7bbd06130f4e7916e859182a7a7 … met=True`, mtime 10:37 (extra-in-tree DSO probe).

Evidence:

    $ git -C kama-shokunin ls-tree --name-only 8abadfed .ufo/waves/round-55/c1/battery/
    control.out  m-extra-in-tree.out  m-ldaudit-foreign.out  m-ldaudit-writable.out
    m-ldpreload.out  m-member-flip.out  m-text-flip.out  run-battery.py
    $ head -c 200 kama-shokunin/.ufo/waves/round-55/c1/battery/m-ldaudit-writable.out
    tip=23dc15dae61f04e86efb62ef2e622154bc4db36a
    bind=1 sealed=1 code=1 teardown=1 newrow=1 bound=3/3 … met=True
    $ grep -n "m-ldaudit-writable" kama-shokunin/.ufo/waves/round-55/c1/battery/run-battery.py
    (no output — the name appears nowhere in the landed runner)
    $ grep -n "m-extra-in-tree" kama-shokunin/.ufo/waves/round-55/c1/battery/run-battery.py
    36:    # round-53 J1SwapChecked vector; m-extra-in-tree showed the backend scan dlcloses
    (only a comment in the m-text-flip entry — the receipt is never written: the runner's
    sole writer is counter()'s open(os.path.join(OUT, f"{name}.out")) over MUTANTS' five names)

The preregistration's battery list also names `m-ldaudit-writable (code leg)`, whose
only committed receipt prints `met=True`, while the landed code-leg kill is
`m-text-flip`. A literal read of the frozen kill rule over the committed dir therefore
trips; the landed verdict ("3 live kills + 1 vector analysis", `8abadfed`) treats only
five receipts as the battery.

Smallest safe correction (full text + diff in
`proposed-fix-stale-battery-receipts.md`): move the two probe receipts out of the
battery dir into `c1/battery/probes/` (or delete them with a one-line lesson note),
and reconcile the preregistration's battery list (`m-text-flip` replaces
`m-ldaudit-writable` as the code-leg kill). The landed battery verdict is unchanged;
no frozen counter, predicate, or live-kill receipt is touched. I did not apply it —
lane files are frozen to this seat.

## 3. Verification commands run (read-only on the lane)

- `git -C kama-shokunin log --oneline -6` / `git rev-parse HEAD` → HEAD
  `8abadfedf89f35372645b1e5d6ce4a2109186f90`; freeze `9c60eae6f7`.
- `git show --stat 9c60eae6f7` → the freeze's 10 files (counters, preregistration,
  controls, S511 source, lesson, superseded ledger row).
- Receipt reads (copied to `receipts/` before citation; sha256 in §4):
  `measured/c{1,2}-build.out`, `controls/base.c{1,2}.out`,
  `c1/battery/{control,m-ldpreload,m-text-flip,m-member-flip,m-ldaudit-foreign,m-ldaudit-writable,m-extra-in-tree}.out`,
  `c1/battery/run-battery.py`.
- Code reads: `tools/round54-replay-code-audit.py` (legs/limits `:45-146`, `:355-438`,
  `:469-607`, `:681-963`), `tools/round54-cited-path-check.py` (`:1-60`, `:198-202`,
  `:236-254`, `:402-588`, `:640-703`), `registry/cited-path-corrections.tsv:46`,
  `corpus/SOURCES.md:263-264`, `corpus/lessons/round-55.md`, `SCORECARD.md:3044-3053`
  (round-53 disclosure + round-54 Planned).
- `pgrep -af llama-server` → no leftovers (no server started by this seat).

## 4. Receipt copies (sha256)

    4f8f277b04b11861b5e45664db6c97fea9a078431c4e450ae89b846e893331b6  receipts/c1-build.out
    bc59e5e186c3168a6783531d08cbd4c545de859cb4e1afac994357c396ed3bc  receipts/c2-build.out
    3d6736a39a5ef881c23e63da3e21cf6246aa4a37739d6d45cff0316f0fdf0794  receipts/base.c1.out
    d6a6f550e558156b16d69fb88196a51b61b913df043e68032172f3f6a5a53828  receipts/base.c2.out
    8f8bbf60bffd90a27c8e4ca6b844309026d2151fe534a5a762d64cc9b27a85b9  receipts/control.out
    ea80b60c8052a44b75cfd50485cc5e56a017226931f521c1c233b3a89d121c76  receipts/m-ldpreload.out
    a71864026f119c145cc847625e5fa6afaa6937516138a2fc3901ab55835d6e47  receipts/m-text-flip.out
    3177300bf5b984ff729f655e5e6b0bb33fe0b1b5a1771f3fb5043ee76a790036  receipts/m-member-flip.out
    4ef002955c60b91c0b0d7c57f27687fda00801d3e568654c86d65759eb589d35  receipts/m-ldaudit-foreign.out
    ead1173777919775974f5172673c423c8045d4a04307f5f274f7a04395ab949  receipts/m-ldaudit-writable.out
    0ff496d245be1c4af01a80b255a1d69a17724e193a1c107cc793439234efefca  receipts/m-extra-in-tree.out
    49a57a155cd6b31034d9c0a35ef8cdbd99c701d110c7fd662f222e0bdcda2945  receipts/run-battery.py
