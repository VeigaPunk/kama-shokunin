# EX03ProvinceClaims — kama r71 w1, C3 freshness (2026-11-03)

**Verdict: built and exercised.** `tools/round71-province-host-claims.py` re-derives every
PROVINCE.md host-surface claim on this host. Frozen before state reproduced exactly
(`contradicted=14 uncovered=14 exit=1`); tip state `contradicted=14 uncovered=0 exit=0`.
Selftest `pass=7 fail=0`; all three kill rules fire with the exact expected counts.

## Tool

`/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round71-province-host-claims.py` (new, 30.2 KB,
683 lines, called as `python3 tools/...` like every lane instrument).

CLI: `--repo PATH` (default `.`), `--base REV`, `--corrections PATH` (default `<repo>/PROVINCE.md`),
`--json`, `--draft PATH`, `--scratch DIR`, `--selftest`, `--keep`.

- **Marker grammar**: a paragraph opens `- absent-on-this-host (YYYY-MM-DD)` and continues over
  indented wrap lines until a blank line; every `province-host:TAG` in it declares TAG absent.
  The round-67 wrap naming `llama-b11755-install` / `llama-server-link` on two lines counts both.
  Base (f3ee44f4 blob, md5 `248e7de5b074550d04c53e9b0fe0902a`): **11 paragraphs, 12 distinct tags,
  13 tag occurrences** (kama-cache-gguf also cited inside the fixture-gguf paragraph).
- **Declared SURFACES** (12, one live probe each): path existence for omp-binary,
  llama-b11755-install, llama-server-link, kama-cache-gguf, llama-b11755-archive, qwen-coder-unit,
  opencode-json, janitor-md, ollama-v04011-install, fixture-gguf-model; `ufo-src` = a ufo-fsd
  checkout resolves in the declared order `$UFO_SRC` then `~/Projects/ufo-fsd-alpha` (dir carries
  `.git`); `python3-interpreter` = `python3 -c "import sys"` exits 0 (a real run, not a PATH hit).
  A marker tag with no declared probe fails closed with exit 2 (the declared table is the contract).
- **Declared EXTRA prose claims** (4, hardcoded with the round-65 note date 2026-10-31, tag namespace
  `province-host:<name>`): `host-identity` (Windows host vs `uname -s`), `python3-alias` (Store alias
  stub vs a real run), `ntfs-path` (`|`-path claim vs a scratch repo that commits and re-checks-out
  `pipe|name.txt`), `ss-flock` (`ss`/`flock` absence vs `command -v ss flock`). Claim verdict = the
  prose's implied subject state; contradiction = claim != live verdict.
- **Corrections**: `- correction-on-host (YYYY-MM-DD) `province-host:TAG` — present|absent: <evidence>`
  (em dash or `--` accepted). Covers TAG only when dated later than the claim, TAG is declared, and
  the verdict equals the live probe verdict. Wrong tag / flipped verdict / earlier date cover nothing.
- **`--base REV`**: `git show REV[:PROVINCE.md]` (an alternate `--corrections` file inside the repo
  is tried at its repo-relative path first, PROVINCE.md is the fallback), every base marker tag must
  still occur in a tip marker paragraph; otherwise `PROVINCE_HOST_CLAIMS_REWRITTEN <tag>` and exit 1.
- Exit 0 iff `uncovered=0` and nothing rewritten; 1 on uncovered/rewritten; 2 could-not-evaluate
  (unreadable corrections, git failure at `--base`, undeclared marker tag, NTFS probe setup failure).
  Read-only on the repo; the NTFS probe repo lives under the scratch root and is removed; `--draft`
  is the only write (to the path given — the L1, not the tool, appends it to PROVINCE.md).

## Frozen predicate — exact commands and outputs

Counter (frozen, run 21:41:40-03:00 on the lane worktree):

```
$ python3 tools/round71-province-host-claims.py --repo . --base f3ee44f4; echo EXIT=$?
PROVINCE_HOST_CLAIMS markers=11 tags=12 extra=4 contradicted=14 uncovered=0 exit=0
EXIT=0
```
receipt: `.ufo/waves/round-71/w1/EX03ProvinceClaims/tip-frozen-command.out` (plus 14 per-claim
lines and the same summary in `tip.out`).

Before state: the worktree PROVINCE.md already carries a correction block written by another seat
during this wave (see "Concurrent change"), so the frozen before is reproduced from the base blob:

```
$ python3 tools/round71-province-host-claims.py --repo . --base f3ee44f4 \
      --corrections .ufo/waves/round-71/w1/EX03ProvinceClaims/PROVINCE-base.md; echo EXIT=$?
PROVINCE_HOST_CLAIMS markers=11 tags=12 extra=4 contradicted=14 uncovered=14 exit=1
EXIT=1
```
receipt: `before.out`; the base blob is retained at `.../EX03ProvinceClaims/PROVINCE-base.md`
(md5 `248e7de5b074550d04c53e9b0fe0902a`, identical to `git show f3ee44f4:PROVINCE.md`). This
matches `measured/before/province-markers.out` (11 markers, 12 tags, 0 corrections, `Linux`) and
the freeze's `contradicted=14 uncovered=14`.

Live verdicts (14 contradicted; 2 marker claims still hold, so they need no correction):
`omp-binary present`, `llama-b11755-install present`, `llama-server-link present`,
`kama-cache-gguf present`, `llama-b11755-archive present`, `qwen-coder-unit absent` (holds),
`opencode-json present`, `janitor-md absent` (holds), `ufo-src present` (checkout resolves at
`/home/vgpnk/Projects/ufo-fsd-alpha`; `UFO_SRC` unset), `ollama-v04011-install present`,
`fixture-gguf-model present`, `python3-interpreter present` (3.14.8, exit 0),
`host-identity absent` (`uname -s` → Linux), `python3-alias absent` (real run),
`ntfs-path absent` (`git checkout -- .` exit 0 with `pipe|name.txt`),
`ss-flock absent` (`/usr/bin/ss`, `/usr/bin/flock`).

## Kill rules — exact outputs

- (i) flipped verdict, one claim: `kill1-flipped.out` → `... contradicted=14 uncovered=1 exit=1`
  (fixture: the landed block with `province-host:omp-binary` `present`→`absent`).
- (ii) wrong tag clears nothing: `kill2-wrongtag.out` → `... contradicted=14 uncovered=14 exit=1`
  (base text + one line naming `province-host:not-a-declared-surface`).
- (iii) deleted marker line with `--base`: `kill3-rewrite.out` →
  `PROVINCE_HOST_CLAIMS_REWRITTEN qwen-coder-unit` then
  `PROVINCE_HOST_CLAIMS markers=10 tags=11 extra=4 contradicted=14 uncovered=14 exit=1`, EXIT=1.
  Fixture is a scratch git repo (`rev-parse --show-toplevel` asserted) at base text with the
  qwen-coder-unit paragraph deleted.
- Do-nothing control (tag-correct lines appended without probing, all 14 verdicts flipped):
  `shortcut-control.out` → `... contradicted=14 uncovered=14 exit=1`. This is selftest arm
  `shortcut-all-flipped`; the frozen control text names exactly this arm.

## Selftest — `python3 tools/round71-province-host-claims.py --selftest`

`selftest.out` (fixtures under `--scratch`, removed unless `--keep`):

```
[PASS] base-uncovered: rc=1 summary=PROVINCE_HOST_CLAIMS markers=11 tags=12 extra=4 contradicted=14 uncovered=14 exit=1
[PASS] corrected-covers: rc=0 contradicted=14 uncovered=0
[PASS] flipped-verdict: rc=1 tag=omp-binary uncovered=1
[PASS] shortcut-all-flipped: rc=1 contradicted=14 uncovered=14
[PASS] wrong-tag: rc=1 contradicted=14 uncovered=14
[PASS] rewritten-marker: rc=1 rewritten_line=yes
[PASS] no-contradiction: rc=0 uncovered=0 contradicted=4
PROVINCE_HOST_CLAIMS_SELFTEST pass=7 fail=0
EXIT=0
```

Arm 1 uses the frozen base blob (`git show f3ee44f4:PROVINCE.md`) as fixture; arm 2 appends
verdict-equal corrections for every contradicted claim; arm 3 flips one; arm 4 flips all (the
cheap shortcut); arm 5 uses a wrong tag; arm 6 commits base text to a scratch repo, deletes the
qwen-coder-unit paragraph and runs `--base <rev>`; arm 7 is a one-marker fixture with all extras
covered and exits 0.

## Concurrent change I did not make (adaptation, not a defect report)

`PROVINCE.md` became `M` (worktree-modified) mid-wave: a 20-line `## Host re-derivation — round 71
(2026-11-03; ...)` block with 12 marker corrections appeared at 21:40:18, then 4 extra-claim
corrections (16 lines total, lines 276–298) before my tip run. Another seat wrote it; the tool
accepts all 16 lines (`corrections_parsed=16`, `rewritten=[]`, `uncovered=0`). I did **not** edit
PROVINCE.md and did not revert anything. Hash before/after the frozen command is identical
(`province-before-run.sha256` = `province-after-run.sha256`), confirming the counters are read-only.

Draft: `.ufo/waves/round-71/w1/EX03ProvinceClaims/corrections-draft.md` carries the tool-generated
14-line block (one line per contradicted claim, probe command + live output in evidence; markers
whose absence still holds — qwen-coder-unit, janitor-md — deliberately absent). Its header states
that the landed worktree block already covers every claim, so appending is **not required**;
the block is the generated counterpart and is safe to append (duplicate verdict-equal lines) if
the worktree block is ever dropped. Generator: `--draft` against the base blob.

## Files changed / receipts

- New: `tools/round71-province-host-claims.py` (only tracked-path change by me).
- Reports: `.ufo/waves/round-71/w1/EX03ProvinceClaims.md` (this file),
  `.ufo/waves/round-71/w1/EX03ProvinceClaims/{corrections-draft.md, PROVINCE-base.md(+.md5),
  before.out, tip.out, tip-frozen-command.out, tip.json(+.exit/.err), selftest.out, draft-gen.out,
  kill1-flipped.out, kill2-wrongtag.out, kill3-rewrite.out, shortcut-control.out,
  province-{before,after}-run.sha256}`.
- Scratch: `/fast/scratch/hyaku/kama-r71/EX03ProvinceClaims/` (base blob copy, fixtures, draft
  source); deleted on exit after receipts were copied.
- Not touched: PROVINCE.md, SCORECARD.md, SKILL.md, corpus/, registry/, git history.

## Could not verify / carried risks

- The committed after-state: the correction block is uncommitted (`git status --porcelain
  PROVINCE.md` → ` M PROVINCE.md`) and only the L1 commits. The counter's target line is green on
  the worktree as it stands; if that block is dropped before commit, `uncovered` returns to 14.
- Registration of the new tool in SKILL.md/SCORECARD (gate registry, capability row) is scribe/L1
  scope; not done here and not verified.
- Extra-claim tag namespace (`province-host:host-identity` etc.) is tool-declared, not carried by
  any marker line in PROVINCE.md; the four worktree correction lines use exactly these names, and
  the tool accepts them. If the frozen checker expected different names, the four extras would
  stay uncovered — but the frozen predicate only requires `uncovered=0`, which this namespace
  reaches without touching marker lines.
- No tool installs/upgrades were needed; nothing was written to PATH dirs, `~/.config`, `~/.omp`,
  systemd, or any serving process/port.
