# K5LessonGate — round-55 Gate spot-check rehearsal

Verdict: **S511 admit stands (3 minor record inaccuracies, none overturning); the proc(5) `maps` reject's disposition stands but its stated reason is misattributed — it names S048/S050, which hold no `/proc/<pid>/maps` ground, and omits S496, the registry row that actually holds it.**

Seat: K5LessonGate (UFO-FSD critic, leaf). Scope: rehearse the outside closure's
round-55 Gate sampling — one admit (S511), one reject (proc(5) §maps). Lane read-only;
all commands against lane paths, no mutations. Evidence bundle: `K5LessonGate/evidence.txt`
in this directory.

## 1. S511 (git-config(1) GIT_CONFIG_COUNT) — ADMIT check: agree

Gate record: `corpus/lessons/round-55.md:32-38` (ADMITTED, tier B, mined).

**Quote located at the anchor: yes, with one transcription caveat.**
- HTML copy `.ufo/waves/round-55/sources/git-docs-git-config.html` is 830,605 bytes
  (matches the Gate's recorded fetch size) and holds `id="Documentation/git-config.txt-GITCONFIGCOUNT"`
  immediately before the definition passage (`evidence.txt`).
- Decoded passage (entities resolved, whitespace collapsed): "If GIT_CONFIG_COUNT is
  set to a positive number, all environment pairs GIT_CONFIG_KEY_<n> and
  GIT_CONFIG_VALUE_<n> up to that number will be added to the process's runtime
  configuration." — the quoted clause is present at the named anchor.
- Caveat: the quote as written is **not byte-exact** against the source bytes. The
  HTML holds `GIT_CONFIG_KEY_&lt;n&gt;` (entities) and `process&#8217;s` (U+2019 right
  single quote); the row/lesson quote uses decoded entities and an ASCII apostrophe
  (U+0027). The lane's round-54 precedent (S510's quote, same doc family) applies the
  same normalization (it drops the curly quotes around `.git`), and KQ45's byte-exact
  clause triggers only on quotes *labeled verbatim* — this one is a "located quote".
  A reader can locate it after entity decoding. Judgment: acceptable under lane
  convention; a strict KQ45 byte reading would flag it. Low severity.

**Word-count parenthetical: wrong.** The lesson says "(23 words…)"; the quoted string
is 18 whitespace-delimited words (`evidence.txt`). The Gate contract is ≤25 words, so
admissibility is unaffected, but the record is factually wrong. Trivial severity.

**Tier B: defensible by precedent, thinly recorded.** S511 is tier B with no explicit
rationale in the Gate or row; it mirrors the sibling S510 (git(1) env vars, tier B,
round 54). Both are official upstream git docs grounding the counters' `clean_env`
design. Acceptable; noting the absence of a stated justification.

**Used-by path exists: yes.** S511's used-by cell is `corpus/lessons/round-55.md`,
which exists and names S511 (Gate row). E11 checks path presence only
(`scripts/sources-census.sh:29-32`), which passes.

**"Cited by C1's newrow leg and both counters' clean_env": half-accurate.**
- C1: true. `tools/round54-replay-code-audit.py:129` sets
  `GITDOC_URL = "git-scm.com/docs/git-config#...GITCONFIGCOUNT"`, the `newrow_leg`
  (:863-873) requires a new row naming that URL, and its `clean_env` docstring
  (:168-169) names "S510 (git(1) env vars) and S511 (git-config(1) GIT_CONFIG_COUNT)".
  Build receipt `measured/c1-build.out` prints `newrow=1` at the landed tip.
- C2: false as written. `tools/round54-cited-path-check.py:198-202` `clean_env`
  docstring names only "Sen4Fixture" and the mechanism — it never names S510 or S511
  (grep for `S510|S511` in that counter returns nothing). Minor record inaccuracy.

## 2. proc(5) §maps candidate — REJECT check: disposition honest, stated reason not

Gate record: `corpus/lessons/round-55.md:39-47` (REJECTED, no row; "the lane already
holds the classification ground: S048/S050 (procfs decoding for listener ownership,
round 18) and the committed C1 observation receipts").

**The disposition is correct.** The registry already holds exactly this ground:
- **S496** (`corpus/SOURCES.md:249`) — Linux proc_pid_maps(5), man7, **tier A, mined**,
  scope: "what `/proc/<pid>/maps` lines report: per-mapping `dev` (major:minor), `inode`
  and `pathname` of the backing file, and that an inode of 0 means a memory region has
  no file", quoting "The pathname field will usually be the file that is backing the
  mapping." This is the same man-pages content the candidate proposes (proc(5) §maps
  == proc_pid_maps(5)); a new row would restate it. Both used-by paths exist.
- Committed C1 observation receipts (e. `.ufo/waves/round-53/measured/c1-build.out`
  detail lines; round-55 `measured/c1-build.out`) record the live classification the
  counter performs: archive-member mappings byte-equal in `/proc/<pid>/mem`, 13
  root-owned host files, and the sealed `/memfd:llama-server (deleted)` memfd by
  dev:inode. KQ12's reject condition ("row or field growth called new knowledge
  without a new sourced distinction") fits; the flip condition (maps row forms the
  receipts do not cover, e. `/dev/zero` exec mappings) is concrete and honest.
- Typo: "a maps row **form** the committed receipts" → "from". Trivial.

**The stated reason misattributes the ground.** S048/S050 hold no maps ground.
`corpus/knowledge/loopback-listener-ownership.md` (their used-by knowledge entry)
covers `/proc/net/tcp6` address encoding (`get_tcp6_sock` `%08X` words, S048), the
loopback/mapped address policy (S050 RFC 4291), and the LISTEN-inode → child-fd
ownership join — nothing about `/proc/<pid>/maps` pathname semantics. An outside
closure sampling this reject and verifying it against the *named* sources would find
the named ground irrelevant and could wrongly suspect a manufactured rejection. The
honest reason — which the record omits — is S496 (tier A, proc_pid_maps(5)) plus the
committed receipts; S496's omission is the defect's core, since it is the dispositive
held ground. The KQ6 citation is also loose (KQ6 governs vendor/spec claim admission
tiering, not source-row restatement).

**Smallest safe correction** (for the canonical judge / a lesson erratum, not an
in-place edit): in the Gate's proc(5) bullet, replace "S048/S050 (procfs decoding for
listener ownership, round 18)" with "S496 (proc_pid_maps(5), tier A, round 50) and
the committed C1 observation receipts (round-53/55 c1-build detail lines)", keeping
the KQ12 citation, the flip condition, and the disposition unchanged. Correct the
"form"→"from" typo, the S511 word count (23→18), and the "both counters' clean_env"
claim (only C1's clean_env names S511; C2's names Sen4Fixture). None of these changes
any score-bearing artifact; they repair the Gate record's evidence trail.

## Commands exercised (all read-only)

- `python3` entity-decode/verbatim/word-count check against
  `.ufo/waves/round-55/sources/git-docs-git-config.html` (output in `evidence.txt`)
- `sed -n 249,264p corpus/SOURCES.md` (S496/S510/S511 rows); used-by existence checks
- `grep -n "hermetic" corpus/lessons/round-55.md`; `grep -n "S510| S511" …/round-55.md`
- `grep -n "clean_env|GIT_" tools/round54-replay-code-audit.py` and
  `…/round54-cited-path-check.py`; `grep -n "GITDOC_URL" …`
- `grep "detail: code b1|detail: sealed b1" .ufo/waves/round-53/measured/c1-build.out`
- `read corpus/knowledge/loopback-listener-ownership.md`; `ls corpus/lessons/round-54.md` (absent);
  `ls .ufo/waves/round-55/sources/` (830,605-byte HTML present)
- E11 semantics: `scripts/sources-census.sh:29-32`

Impacted axes if uncorrected: calibration (the Gate record is the round's
source-admission evidence; a reject reason that cannot be verified against its named
sources is exactly what the outside closure samples for). No capability enters either way.
