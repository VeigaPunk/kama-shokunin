# SB01LessonDraft — round-91 lesson draft + source re-open (kama r91 w1)

## Scope

Drafted the round-91 lesson sections the L1 integrates into `corpus/lessons/round-91.md`:
(a) `## Gate` rows for S592-S595 (admit, tier, URL, access 2026-11-06, located quote ≤25 words with line
numbers, each verified by my own fetch) plus REJECT rows for the GNU gawk manual pages and SGLang v0.5.22
`server_args.py`; (b) `## Mistakes` candidates: two new round-91 ones (the byte-cap/time miss and the fix's
own wrong cost mechanism) and six mined from rounds 86-90 lessons and verifier spotchecks, each with class,
evidence pointer, captured-by, fix and how the fix was shown able to fail. Read-only in the lane; nothing
committed or edited; no subagents; no POST/load/completion to :1234; no pacman, no tool installs.
Lane HEAD read: `3f317ecd211e80929c673e306e3230be287fdf20`.

## Commands and outputs

All in scratch `/fast/scratch/hyaku/kama-r91/SB01LessonDraft`, `TMPDIR` set there; removed before yield.
`uptime` during measurements: 19.5-45.8 (32 cores).

1. Source re-open, `curl -sfL --max-time 60` ×4, all `rc=0`:
   awk.html `6df7d077…`, common.h `c3010a3c…`, config.go `0b0ea669…`, envs.py `e963af06…` — **all four equal
   the committed `corpus/SOURCES.md` rows** (S592-S595). `awk.html:107-108`, `:185`, `:796-797`;
   `common.h:464,632,634,636,644,669,703`; `config.go:23,130,150,277,281`; `envs.py:26,111` — every SKILL
   T01-T14 literal is present verbatim on its declared line (exit 0 for each `sed -n 'Np'`).
2. `llama-server --version` → `build 12177, commit 6c01da627`; binary sha256 `ba272ee3…` = receipts'
   `server_sha256` (exit 0).
3. gawk pages, 5 paths (`Assignment-Options.html`, `Variable-Assignment-Options.html`, `Options.html`,
   `html_node/index.html`, `https://www.gnu.org/`), `curl --max-time 20|45`: **rc=28, http=000, 0 bytes** on
   every one; `getent hosts www.gnu.org` → `2001:470:142:5::116`; `curl -v` shows TCP connect timing out on
   both address families.
4. SGLang: `server_args.py` `http=200`, 35 396 B, sha256 `d1b9ffc7…`; `grep -n 'timeout\|keep_alive'` → no
   hits; imports from `sglang.srt.arg_groups.fields.*`; `arg_groups` listing `http=200`, 39 entries;
   `arg_groups/fields/serving.py` sha256 `66a9ab45…`, `stream_interval … ] = 1` at 256-260.
5. Cost bench (bash 5.3.20, C.UTF-8, one 1 800 000-byte comma list, single runs):
   `${s%","}` matching → `0.021 s`; `${s%X}` / `${s%"X"}` not matching → `68.568 s` / `62.946 s`;
   base-shaped `C_SERVED=$(printf '%s' "$ids" | tr '\n' ',')` then `${C_SERVED%,}` → `tr+cmdsub 0.045-0.062 s`,
   strip `55.960 / 69.868 / 56.393 / 65.086 s` (C.UTF-8, en_US.UTF-8); 11.704 s when `LC_ALL=pt_BR.UTF-8`
   falls back to C. Same string loaded from a file and stripped: `0.024-0.037 s` (why: see Finding 2).
6. Round-90 counter read: `tools/round90-hostile-answers.py:185` `timeout=90`, no seconds in any cell;
   `:311` largest list 20 001 ids; `plans/round-90-claims.md` §C1 names no time bound.
7. `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` → exit 0, `kama ok`;
   S592-S595 are `tier A`, `opened 2026-11-06`, `recheck on-release` (awk over `corpus/SOURCES.md`).
8. Receipts read: `controls/c1-base.out`, `c1-f1-count-cap.out`, `c1-f2-exact-match.out`, `c2-base.out`,
   `c2-forgeries.out`, `harm-base.out`, `measured/c1.out`, `c2.out`, `harm-M.out`, `controls/harm.sh`,
   `controls/c1-forgeries.sh`.

## Findings

- **NOTE 1 — gawk is unreachable host-wide, so the reject is "not judgeable", not "absent".**
  Five paths including the bare `https://www.gnu.org/` return rc=28 with 0 bytes while DNS resolves and the
  TCP connect times out (`bench-suffix-removal.out` §2). The L1's rc=28 reproduces; no quote can be located,
  so no row. S592 (reachable POSIX spec) grounds the same awk rule, so C1 loses nothing. The Gate row must
  say "host unreachable", not "page does not exist" — otherwise a later reader will treat a network fault as
  a source judgement.
- **NOTE 2 — the "38 s `${C_SERVED%,}`" figure is corroborated in situ but the mechanism in the probe comment
  is wrong in kind.** `c1-f1-count-cap.out` T1 (per-id fork already removed, base join path intact) =
  `39.38 s`, matching the claim's 38 s; my bench reproduces 56-70 s at 1.8 MB and 11.7 s when the locale falls
  back to C. Exact 38 s: not reproduced (locale/load dependent). The probe comment at `3decfa36:934`
  ("bash suffix removal is quadratic there") is contradicted by the same string costing `0.021 s` when the
  pattern matches and `68.6 s` when it does not: it is an unmatched split-point scan, linear in bytes with a
  ~35 µs/char multibyte constant. And in the base probe the pattern never matched — `ids=$(served_ids …)`
  strips the trailing newline, so `tr` emits no trailing comma and the strip was a **no-op that still paid the
  scan**. Pointer: `tools/kama-probe.sh` at `3decfa36` lines 933-935; `bench-suffix-removal.out` §4.
  Label: DEFECT (in-code explanation), fix = reword the comment; the frozen counter grades wall time and is
  unaffected.
- **NOTE 3 — C1's time bound is load-bearing exactly once at base, and that cell is worth naming in the
  lesson.** `controls/c1-base.out` T3 is `ok=0 verdict=MODEL_OK reason=matched seconds=75.71`: right verdict,
  3.8× over budget. Under round-90 grading (verdict only) that cell is green; T1/T2/T4/T5 would fail anyway
  (killed). So a future round that drops the budget from the pass condition turns C1 green on the base probe.
- **NOTE 4 — C2 rows T13/T14 bind a `TYPE_CHECKING` annotation.** `envs.py:26` and `:111` sit inside
  `if TYPE_CHECKING:` (line 16); the executable defaults are `os.environ.get(..., "600")` at 812 and `"5"` at
  1143, with doc comments at 809-810 and 1142. The rows' name/value/decision do fit their line (value confirmed
  twice), but K2's reader should know the bound line is a type-checker mirror. No row is false.
- **NOTE 5 — round-90's cells could not see a cost of this shape.** No time condition anywhere
  (`:185` `timeout=90`), largest legit list 20 001 ids (`:311`) — two orders of magnitude below the
  pathological input, and a 39 s no-op strip on 20k ids stays inside the 90 s subprocess timeout. This is the
  mechanical reason the r90 cap "bounded bytes but not time" (lesson M1 / M4 lineage).
- **NOTE 6 — cosmetic, inside the anchor column:** S592-S595 anchor text reads `opened2026-11-06:` (no space)
  at `corpus/SOURCES.md:347-350`; the `opened` column itself is well-formed `2026-11-06` and the census
  accepts the file (exit 0).

No BLOCKER found in the material I reviewed: all four admits re-open with equal digests, all 14 literals are
on their lines, and both rejects are grounded in what I observed rather than in lane prose.

## Deliverables

- `.ufo/waves/round-91/w1/out/SB01LessonDraft/round-91-lesson-draft.md` — the `## Gate` table (S592-S595
  admits; gawk and SGLang rejects; two knowledge-entry admits) and `## Mistakes` M1-M8, each with class,
  evidence pointer, captured-by, fix and "shown able to fail".
- `.ufo/waves/round-91/w1/out/SB01LessonDraft/bench-suffix-removal.out` — source digests, the 14 literal line
  reads, the gawk rc=28 transcript, the SGLang observations, the suffix-removal bench and the round-90 counter
  pointers.

Scratch `/fast/scratch/hyaku/kama-r91/SB01LessonDraft` removed after copying these receipts; lane repo
unmodified (read-only git/show/grep/curl only).

VERDICT: holds — both frozen claims' lesson facts re-derive from my own fetches and receipts; one in-code
mechanism sentence is wrong in kind (M2) and one binding line in C2 is a type-checking annotation (NOTE 4),
neither of which falsifies a claim.
