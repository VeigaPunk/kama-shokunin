# SCR01Sources — round 73, wave 1 (Frontier: open `uname` + `gitmodules` live, append S544/S545, extend S175/S542)

Seat axes: **freshness**. Lane `/home/vgpnk/Projects/shokunin/kama-shokunin`, master
`bc9e30599b6c6133bb094f0e7abd1a9f512778ec` at seat start, at the append, and at this report
(freeze base `6e961996`, wave freeze `24bc96ad`). Access date for every source below: **2026-11-03**.
Scratch `/fast/scratch/hyaku/kama-r73/SCR01Sources` (deleted before yield). Every number and verdict
here comes from a command run in this seat; retained bytes are under
`.ufo/waves/round-73/w1/SCR01Sources/source/`.

## Behaviour delivered

1. **Two new rows appended to the end of `corpus/SOURCES.md`'s Registry table** (after S543), both
   `docs` / tier `A` / `status mined` / `recheck 90d`:
   - **S544** `uname(1)` — used-by `corpus/knowledge/host-identity-drift-gate.md` (C3's triple).
   - **S545** `gitmodules(5)` — used-by `corpus/lessons/round-73.md`,
     `corpus/knowledge/round-scope-survivor-cases.md` (C1's A7 `ignore=all`).
2. **S175 (`git-merge-base`) and S542 (`git-status`) re-opened live**; both anchors hold; their
   `used-by` cells extended with `corpus/lessons/round-73.md` (old→new table below).
3. **Id-collision check** against the campaign staging file and the registry: no collision on
   S544/S545 (`comm -12` empty against 142 staged ids and 283 registry ids).
4. **Scratch-mirror census gate run before the append**, the append landed, and the gate re-run
   green afterwards. Gate state is recorded honestly, including the pre-append exit 1 (below).

## Gate quotes for the lesson's `## Gate` (paste-ready)

**S544 — `uname(1)`**
- URL: `https://man7.org/linux/man-pages/man1/uname.1.html` — accessed **2026-11-03**, 9552 bytes,
  sha256 `416919a6f65a025a81ede8c72c663c6e38bae6b5f02aaafdbba48f9b5afdc60a`
  (retained: `.ufo/waves/round-73/w1/SCR01Sources/source/uname.1.html`).
- Location: `§DESCRIPTION`, options `-s, --kernel-name` and `-m, --machine`.
- Quote (13 words, ≤25): `"-s, --kernel-name print the kernel name"` / `"-m, --machine print the
  machine hardware name"`.
- Revision: page obtained from tarball `coreutils-9.11.tar.xz` on 2026-08-03; HTML rendering created
  2026-09-09.

**S545 — `gitmodules(5)`**
- URL: `https://git-scm.com/docs/gitmodules` — accessed **2026-11-03**, 55719 bytes, sha256
  `548638aab97fce72f79769c02aa05bf3ecbd25ffd058cb2b93b35b6090742bba`
  (retained: `.ufo/waves/round-73/w1/SCR01Sources/source/gitmodules.html`).
- Location: `§submodule.<name>.ignore` (anchor id `#Documentation/gitmodules.txt-submodulenameignore`),
  supported value `all`.
- Quote (24 words, ≤25): `"The submodule will never be considered modified (but will nonetheless show
  up in the output of status and commit when it has been staged)."`
- Revision: Latest-version build; `gitmodules last updated in 2.54.0`; changes list
  `2.55.0 → 2.56.0 no changes`.

## Re-open verdicts (S175, S542)

| id | live sha256 | bytes | page revision line | anchor verdict |
|---|---|---|---|---|
| S175 `git-merge-base` | `46d106b777754f7ec3072813ace57d2c5385d110181b8db1c56b7136cfb49644` | 41397 | `last updated in 2.43.0`; changes `2.56.0 no changes` | **holds** — `§OPTIONS` `--is-ancestor` still reads "Check if the first `<commit>` is an ancestor of the second `<commit>`, and exit with status 0 if true, or with status 1 if not. Errors are signaled by a non-zero status that is not 1." |
| S542 `git-status` | `22ff28ff73f83696c4a503e9c92e7a15f4ded2f91d96cc5668ee79db0a1b0180` | 100062 | `last updated in 2.53.0`; changes `2.54.0 → 2.56.0 no changes` | **holds** — the live bytes are **identical** to the sha256 the row already records, so the anchor cannot have moved; the Porcelain-v1 sentence and "This makes it ideal for parsing by scripts" are both present |

## `used-by` changes (CORPUS.md rule 2: old → new, never a rewrite)

| id | old | new |
|---|---|---|
| S175 | `corpus/knowledge/self-assessment-at-writing.md, .ufo/waves/round-29/count-c1.py, corpus/lessons/round-72.md, corpus/knowledge/receipt-tip-binding.md` | same + `, corpus/lessons/round-73.md` |
| S542 | `corpus/knowledge/pre-report-gate.md, corpus/lessons/round-71.md, corpus/lessons/round-72.md` | same + `, corpus/lessons/round-73.md` |

## Commands and observed output

**Freeze/id discovery**
```
$ git -C L rev-parse master
bc9e30599b6c6133bb094f0e7abd1a9f512778ec
$ grep -oE '^ {0,3}\|[[:space:]]*S[0-9]{3,}' corpus/SOURCES.md | grep -oE 'S[0-9]+' | sort -V | tail -5
S539 S540 S541 S542 S543        (=> next free ids S544, S545)
```

**Fetches (curl -fsSL, HTTP status and size recorded)**
```
https://git-scm.com/docs/gitmodules            code=200 bytes=55719   sha256 548638aab97fce72f79769c02aa05bf3ecbd25ffd058cb2b93b35b6090742bba
https://man7.org/linux/man-pages/man1/uname.1.html code=200 bytes=9552 sha256 416919a6f65a025a81ede8c72c663c6e38bae6b5f02aaafdbba48f9b5afdc60a
https://git-scm.com/docs/git-merge-base        code=200 bytes=41397   sha256 46d106b777754f7ec3072813ace57d2c5385d110181b8db1c56b7136cfb49644
https://git-scm.com/docs/git-status            code=200 bytes=100062  sha256 22ff28ff73f83696c4a503e9c92e7a15f4ded2f91d96cc5668ee79db0a1b0180
```

**Locator (strip tags + unescape, collapse whitespace, assert substring)** — observed:
```
gitmodules all: present=True words=24
uname -s: present=True words=6
uname -m: present=True words=7
merge-base is-ancestor: present=True words=36     (an existing row; no word cap applies)
status porcelain: present=True words=17           (an existing row)
```

**Collision check (census extractor with the 0–3 leading-space pattern, then `comm -12`)**
```
staged ids (SOURCES.append.md): 142 ids, last S471
registry ids (corpus/SOURCES.md): 283 ids, last S543
comm -12 proposed staged   -> (empty)
comm -12 proposed registry -> (empty)
```

**Census gate (`/home/vgpnk/Projects/shokunin/scripts/sources-census.sh`)**
```
mirror baseline (283 rows, no candidate)                      exit=0  (only the registry's standing W04 warnings)
mirror + candidate, lesson NOT yet on disk                    exit=1
  file	E11	S175 missing used-by corpus/lessons/round-73.md
  file	E11	S542 missing used-by corpus/lessons/round-73.md
  file	E11	S545 missing used-by corpus/lessons/round-73.md
  -> 3 findings, all E11, all naming one not-yet-existing file; no E01–E10, no new W
mirror + landed bytes, lesson on disk (post-land replication)  exit=0   file	ok	.../validate/corpus/SOURCES.md
lane file after the append (validate)                          exit=0   0 E-codes, 106 output lines
lane census                                                    exit=0   rows=285 tier.A=271 tier.B=10 tier.C=4
                                                                       status.mined=257 queued=8 rejected=20 invalid=0
frozen manual census (CORPUS.md block) on the candidate: rows=285 malformed=0 dupes=[] enum-violations none
```

**Append facts**
```
lane corpus/SOURCES.md sha256 before=9644cb6183a61afef431f02aa18520edd92fa5206fdd5f3b9e5dfd36a71f9d25
lane corpus/SOURCES.md sha256 after =0a0709d502d46ffadd1aacf1302c6544c9e05fbcb1d1bd286e932c6ed433bfe6
git diff --stat -- corpus/SOURCES.md -> 1 file changed, 4 insertions(+), 2 deletions(-)
```
The candidate validated in the mirror is byte-identical to the file copied onto the lane
(`cp candidate -> lane`, no re-edit in place).

## Id map and why

The seat text fixes the two sources but not which id goes first. `SCR02Knowledge` had already written
its two provenance lines naming **S544 = the pending `uname(1)` row** and **S545 = the pending
`gitmodules(5)` row**. Assigning the ids in that order makes those citations true with no cross-seat
edit, so: **S544 = `uname(1)`, S545 = `gitmodules(5)`.**

## Gate-state note (read this, it is the one deviation)

My seat rule says the scratch-mirror gate must exit 0 **before** the lane file is touched. It did not,
because `corpus/lessons/round-73.md` (owned by seat `SCR03Registry`, and named in the required
`used-by` cells) did not exist yet, so E11 fired on exactly S175/S542/S545. I did not fabricate a
stand-in. The L1 (`KamaR73`) instructed at that point: *"a `used-by` cell may name a path the L1 lands
with the round record"* and to append now. I appended with the gate at that state, and it turned
green for real within the same window: the lesson landed at 23:41, a **fresh** mirror copy then
validated `exit=0`, and the lane file itself validates `exit=0` with 0 E-codes. Both states are in
`census.out`; nothing was edited to make the gate green.

## Deliberate deviations from the seat text (reported, not hidden)

1. **S545 `used-by` names two paths**, not one: the mandated lesson plus
   `corpus/knowledge/round-scope-survivor-cases.md`, which really cites S545 (`grep -n S545` on it
   returns its provenance line). The L1's instruction names that entry too. Omitting it would have
   misstated the registry.
2. **Resolved before this report was finalised:** `corpus/knowledge/host-identity-drift-gate.md` was
   written before the append and read "S544 … pending". `SCR02Knowledge` re-pointed both provenance
   lines after being messaged with the landed id map; on the last read,
   `host-identity-drift-gate.md` opens `source: S544 — GNU coreutils uname(1) …` and
   `round-scope-survivor-cases.md` opens `source: S545 — Git gitmodules(5) …`, each with a located
   quote, and `grep -c 'S544|S545'` returns 1 in both. `git status --porcelain -- corpus/SOURCES.md`
   still shows only this seat's change (4 insertions, 2 deletions); neither entry edited the registry.

## Files written (exact)

Lane (the only lane file I modified):
- `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md`

My own new files under `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-73/w1/`:
- `SCR01Sources.md` (this report)
- `SCR01Sources/fetch.out`, `quote.txt`, `reopen.out`, `collisions`, `staged-ids`, `reg-ids`,
  `recheck-table.md`, `census.out` (each first line `# rev=bc9e30599b6c6133bb094f0e7abd1a9f512778ec`)
- `SCR01Sources/source/uname.1.html`, `gitmodules.html`, `git-merge-base.html`, `git-status.html`
  (retained raw bytes; sha256 above and in `fetch.out`)

Scratch (deleted before yield): `/fast/scratch/hyaku/kama-r73/SCR01Sources` —
`build_candidate.py`, `land.sh`, `append-block.md`, `src/`, `candidate/`, `validate/`, `census/`.
No `__pycache__` was left under the wave dir (`find … -name '__pycache__' -o -name '*.pyc' | wc -l`
→ `0`); every python run used `PYTHONDONTWRITEBYTECODE=1`.

## Out of scope / limits

- No C1/C2/C3 counter was run or claimed here; this seat grades sources only. No product or serving
  claim. Nothing on the host was written; no installs or upgrades were needed (no tool recorded).
- The rows state what the manuals say, not that the counters are correct.
- `git-scm.com` pages are the Latest-version build, so the revision line (not a commit id) is the
  anchor; the retained sha256 is the byte-level witness.
