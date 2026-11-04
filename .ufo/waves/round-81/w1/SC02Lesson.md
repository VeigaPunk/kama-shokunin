# SC02Lesson — round 81 wave 1 report (kama)

Seat: **SC02Lesson** (scribe, leaf). Milestone kama r81 w1; judged on **calibration**. Item: draft
`corpus/lessons/round-81.md` in the seat dir for the L1 to file.

Base `e7d2fd729cf8204c89c32534303bc9f2a97fcee4`; sealed revision C1 grades
`a2af1af59faf6cf66fe854559293c4e4b441aff3`. Lane tip `2c1faed0354dbb3cb9f869cb1af4a9302dfcfd4e`
when drafting started, `f6cb5303171cc73dc570ace06f99125266e5b956` when the last check ran (the
C2 executor's late-row commit landed mid-seat).

## Behavior

Drafted the lessons file with the four required sections in the required order — `## Gate`
(4 candidates + `### Gate erratum — S557`), `## Corrections` (the plan's six blocks byte-exact, one
prose paragraph per fact), `## Mistakes` (one row, class · evidence · captured-by · fix),
`## Freeze divergences` (empty). Every URL was opened by this seat on 2026-11-04; no quote, status,
date or digest was copied from an earlier round. Nothing was filed, committed, or run in scored
mode.

## Checks run (read-only, no scored run)

1. `curl -sSL -o <body> -w '%{http_code} %{size_download} %{url_effective}' <url>` per candidate,
   2026-11-04 — `exit 0` for every fetch (no `-f`, so the 404s are statuses, not exits):

   | URL | HTTP | bytes | sha256 |
   |---|---|---|---|
   | `raw.githubusercontent.com/ollama/ollama/v0.40.11/docs/api/openai-compatibility.mdx` | 200 | 25472 | `44071a1277796b5ad28e51e561afd94ac75f6f76cd75c4b8d9d80b9dff760cd5` |
   | `raw.githubusercontent.com/ollama/ollama/v0.40.11/docs/api-openai-compatibility.mdx` (S557 filed) | 404 | 14 | `d5558cd419c8d46bdc958064cb97f963d1ea793866414c025906ec15033512ed` |
   | `git-scm.com/docs/git-merge-base` | 200 | 41397 | `46d106b777754f7ec3072813ace57d2c5385d110181b8db1c56b7136cfb49644` |
   | `git-scm.com/docs/git-diff-tree` | 200 | 256938 | `6473d8a3d1bc12fa2e0ce700664253db537f143a53d34d36313bbda0d9ef5000` |
   | `github.com/vllm-project/vllm/releases/tag/v0.33.0` | 200 | 163538 | `41b95980bc1fda7d4cdee47c76277f186b922475faf9c7026de25c80e3d34bda` |
   | `api.github.com/repos/vllm-project/vllm/releases/tags/v0.33.0` (auxiliary) | 404 | 147 | `e6fa3955395b2945df66f9729a57f8884e9388e275389539561dcb03aeb4f05b` |
   | `github.com/vllm-project/vllm/releases.atom` (auxiliary) | 200 | 733598 | `e968d03cba2c7b226f10e1cba8ee2d8bcbb49596e4674446ac39d63eaa43f585` |

2. `git show <rev>:<path>` reads of `SCORECARD.md`, `LOG.md`, `corpus/SOURCES.md` and the two
   round-80 selftest receipts at `a2af1af5` and at the tip; `git ls-tree --name-only <tip>
   corpus/lessons/` for the closure list; `git merge-base --is-ancestor` for the revision order
   (sealed → base → tip, all `exit 0`).
3. Counter integration, read-only: imported `tools/round81-selfrecord-round80.py` — present on disk
   but **uncommitted** at `f6cb5303`, sha256
   `ddeacbbe89709d06d192515662afaf79bb6de4088a77ce6031ae2c67798471db` — and called its `derive()`
   (no writes): the six facts return `pass=9→pass=11`, `pass=6→pass=12`, `pass=9→pass=11`,
   `pass=9→pass=11`, `round-79→round-80`, `round-79-verifier-spotcheck.md→
   round-80-verifier-spotcheck.md`, all `stale=True`. Parsed the six draft blocks with the counter's
   own `CORRECTION` regex over its `section(draft, "Corrections")`: 6 blocks, `old == declared`,
   `new == observed`, `at == sealed` for all six, `python3 exit 0`.
4. Format checks: H2 order `Gate → Corrections → Mistakes → Freeze divergences`; Gate table 6
   columns × (header + separator + 4 rows); quote word counts 9 / 25 / 20 / 2 (all ≤25); six plan
   lines present verbatim and each unique in the file and in `## Corrections`.

A first ad-hoc assertion anchored `corrected F` at line start and exited 1: the draft's blocks are
backticked, as the round-80 lesson was. That assertion was wrong, not the file; the counter's own
unanchored regex parses all six (check 3).

## Touched surfaces

- Written: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-81/w1/SC02Lesson/`
  (draft + receipts) and this report. Nothing else; no lane file, no fleet-root file, no git write.
- Scratch `/fast/scratch/hyaku/kama-r81/SC02Lesson/` created and removed before yield.

## Out of scope (not done, by rule)

Filing `corpus/lessons/round-81.md`; the appended SCORECARD `#### round-81 correction` block and
`LOG-CORRECTION` entry; the in-place Axes edits; SOURCES rows S558–S561; the knowledge entry; the
QUALITY criterion KQ133; every tool file; `pre-report-gate.py` in scored mode. All L1 / other seats.

## Findings

1. **S557's filed path is dead.** 404 / 14 bytes; the corrected path returns 200, 25472 bytes,
   `44071a12…760cd5` — the exact digest and size S557's own row states, so only the path was wrong.
   Its note anchor is also one line short (row says 293-294; `created` is 294, `owned_by` 295).
   Filed as S558, dead path left byte-intact; erratum records it per R80V3.
2. **vLLM v0.33.0 carries no note text.** The page body is the bare string `vLLM v0.33.0`
   (Atom `<content>` is `<p>vLLM v0.33.0</p>`; the REST by-tag lookup answers 404). Rejected: the
   lane's pin is `v0.32.0` (`registry/engine-pin-relations.tsv`: `behind 1` vs `v0.33.0`) and no
   round-81 claim reads vLLM behaviour. R80V4 warning inventory restated in the row.
3. **The sealed record's four tallies contradict its own receipts and its own erratum.**
   `SCORECARD.md:4781`, `:4783`, `:18` and `LOG.md:3288` state `pass=9`/`pass=6` while the cited
   receipts print `pass=11`/`pass=12`; `SCORECARD.md:4796` calls those tallies "the post-hardening
   measurements", and the same record's `LOG.md:3338` names them as pre-hardening ("was 9",
   "was 6"). This is the mined mistake, captured by F1–F4.
4. **F5/F6 have no receipt file.** Their witnesses are the coverage row's own evidence cell (names
   round 80) and the tip's closure listing (round-80-verifier-spotcheck.md); the draft says so
   rather than inventing a receipt.
5. **The in-flight C1 counter's record markers are exact strings** (`C1-selftest pass=9 -> pass=11`,
   `C3-selftest pass=6 -> pass=12`, `calibration-row pass=9 -> pass=11`,
   `coverage-last-change round 79 -> round 80`, `newest-closure round-79-verifier-spotcheck.md ->
   round-80-verifier-spotcheck.md`; LOG marker `selftest tallies pass=9/pass=6 -> pass=11/pass=12`).
   The draft names them so the L1's appended block can satisfy them; the counter file is uncommitted
   at `f6cb5303`, so these markers are dated to that file's sha256, not to the frozen plan.
6. **No freeze divergence.** The plan's six locations, value strings, witness paths and target line
   re-derive as written; the record's three defects are answered by the round, not by a plan change.

## Tooling

No installs, no pacman, no PATH writes (operator rule recorded: zero installs this seat).

## Artifacts (absolute)

- Draft: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-81/w1/SC02Lesson/round-81.md`
- Report: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-81/w1/SC02Lesson.md`
- Receipts: `…/w1/SC02Lesson/curl.txt`, `quotes.txt`, `body-ollama-openai-compatibility.mdx`,
  `body-git-merge-base.html`, `body-git-diff-tree.html`, `body-vllm-v0.33.0.html`,
  `s557-filed-404.txt`, `vllm-release-api-404.json`, `vllm-releases.atom`,
  `vllm-v0.33.0.atom-entry.xml`
