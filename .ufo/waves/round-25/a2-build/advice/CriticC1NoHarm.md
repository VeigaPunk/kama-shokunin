Verdict: two fixable harms, no rejection-grade harm. (1) The registered M17 changes from killed to surviving with no auditor change in this commit, because the round-23 path that F13 killed now lives at the new M33 site, and the docstring's "M17 keeps its round-23 element" hides that. (2) SKILL.md still says "27 retained literals"; the instrument now holds 28. The exit contract, every other mutant, the history and routed defects 1-5 are intact.

Seat: KamaR25a2.CriticC1NoHarm (critic, read-only, no llama-server started). Target: `git diff 5388b7cf 1fc41e346853afd98cbd7010af5db4e54dc877f7`, which touches one file only: `tests/report-audit/isolation-mutants.py` (30 insertions, 3 deletions, exit 0). The checks below ran in my own clone `/fast/scratch/hyaku/kama-r25a2/CriticC1NoHarm/clone`, detached at 1fc41e3, using git 2.56.0 and Python 3.14.8.

## Harm 1: M17 changes identity from killed to surviving; the F13 kill moves to M33 (axes: calibration, quality through false provenance; fixable)

Counterexample, observed by running `TMPDIR=<scratch>/tmp python3 tests/report-audit/isolation-mutants.py --json --only M11-listing-surrogates --only M17-ref-shadow --only M33-ref-shadow-bare-objects` in my clone. Run from 09:36:34Z to 09:38:46Z, exit 0, stderr empty:

- M11-listing-surrogates: killed, grid exit 1, failed row F20-quotepath-open-range.
- M17-ref-shadow: **survived**, grid exit 0, failed rows [].
- M33-ref-shadow-bare-objects: killed, grid exit 1, failed row **F13-ref-named-abbreviation**.

At round 23, `.ufo/waves/round-23/final/mutants.json` records M17-ref-shadow as killed with failed row F13-ref-named-abbreviation. SCORECARD.md:1166 lists only M20 as the survivor.

Why this happens (code and history):

- Round-23 auditor e876b95: `lookup()` with a peel recursively called itself without a peel for the bare query (`bare = lookup(repos, tokens)`, e876b95 tools/report-landing-audit.py:148-149). On that recursive call `peel` is empty, so the guard `if not peel and not parts[0].startswith(token):` at e876b95:170-172 fired for F13's abbreviation `deadbee1`. Round-23 M17 removed that raise, so F13 killed M17.
- Tip 1fc41e3: the bare query is now `bare_objects()`. It is called only with a peel, `here = bare_objects(store, tokens) if peel else None` (tools/report-landing-audit.py:246), and it carries an unguarded copy of the refusal at :212-214. That copy is M33's site.
- The `lookup()` site that M17 now targets (:275-277) is reached through the command line only by the no-peel call `full = lookup(stores, full_tokens)` (:538). Those tokens come from `FULL`, which is exactly 40 lowercase hex (:90). Abbreviated citations (:550) and errata (:630) both pass `"^{commit}"`.
- git never answers a full 40-hex name through a ref. The probe in `out/CriticC1NoHarm/git-ref-resolution-probe.txt` created a tag named by a 40-hex string with no such object; `cat-file --batch-check` answered `missing` (exit 0). A tag named by another commit's id answered that commit itself. Source: https://raw.githubusercontent.com/git/git/v2.56.0/object-name.c, opened 2026-10-22. Line 688, `if (len == r->hash_algo->hexsz && !get_oid_hex(str, oid)) {`, is followed by `return 0;` at line 700. Also https://raw.githubusercontent.com/git/git/v2.56.0/builtin/cat-file.c, opened 2026-10-22, lines 1111-1112: `cfg->warn_on_object_refname_ambiguity = 0;`. [INFERENCE from those lines, the probe and the call sites] The M17 raise cannot be reached from any audit input, so M17 is an equivalent mutant through the command line. The sibling report advice/MutationM17M33Kill.md reached the same survival result independently.

What the repair text says:

- isolation-mutants.py:30-32 says "M17 keeps its round-23 element, the peel-guarded check in lookup()". Amendment 2 (`repair_design`) says the "round-23 auditor e876b95 line 170-172 has the same guard".
- The line text is the same, but the behavior is not. At round 23 that guard was passed on the bare recursive query. At the tip the bare query runs in `bare_objects()`. The round-23 behavior and its kill evidence therefore carry over to M33, not M17.

This is not a dropped call site: both sites are registered, so the preregistration rule "no call site is silently dropped" is met. It is not narrowing either: M17 still weakens a ref-named-citation refusal. The harm is an unannounced identity change in the registered set. The killed and surviving lists that C1 cites as supporting evidence will show a new survivor M17 next to M20. Read without context, a closure could take that as an auditor regression, or as a defensive-only element, which the docstring at :9-10 forbids.

Smallest safe correction: one docstring sentence in the round-25 block (and the same in the round-25 report and lessons text). It should say that at the tip the `lookup()` site is reached only by full 40-hex citations, which git answers as object ids before refs (object-name.c:688-700), so M17 is expected to survive as unkillable through the command line, with no defensive-only claim. It should also say that the F13 kill which M17 carried at round 23 now belongs to M33, because the bare query moved to `bare_objects()` in round 24.

Keep the registered `repair_design` (do not swap ids). Do not retire M17: its literal is still present at the tip, so the retirement rule does not apply.

## Harm 2: the documented mutant count is now false (axis: calibration; fixable)

- SKILL.md:871 says "27 retained literals,4 retired IDs without reuse".
- SKILL.md:988-990 says "`tests/report-audit/isolation-mutants.py` holds 27 retained literals with 4 retired ids".

The registered counting command in my clone printed `registered 28 stale 0 []` (exit 0). `git diff --stat 147f5bdd 1fc41e3 -- SKILL.md SCORECARD.md LOG.md README.md corpus/ tools/ tests/ .ufo/reports` lists only isolation-mutants.py, so the repair left both SKILL lines stale. SKILL.md:865 also names M17 without mentioning M33.

Smallest safe correction: change both lines to 28 retained literals (M33 added in round 25, no id reused). Report the denominator as measured, 27 to 28. This is L1 integration work.

## Checked and found no harm

- **Exit contract and code paths unchanged.** The bytecode of `main` and `grid` is equal between 5388b7cf and 1fc41e3, and `RETIRED` is equal (out/CriticC1NoHarm/static-checks.txt). The docstring statements at :34-37 on exit 0 and exit 2 still match :176-230.
- **No dropped mutant, no reused id.**
  - The old file has 27 ids and the new one 28. Nothing was dropped; the only addition is M33-ref-shadow-bare-objects, and the order of the existing ids is preserved.
  - The label `M33-now-fallback-removed` exists only in a different round-21 seat harness (.ufo/waves/round-21/falsify/out/C1SelftestReview/mutation-harness.py:151). `--only` matches full names, so the two cannot be confused when selecting mutants.
  - M08 has never existed in this instrument (`git log -S'"M08'` is empty), so its absence is not new.
- **Unrelated replacements unchanged.** Only the M11 and M17 tuples differ. All 28 literals match exactly once in the tip auditor. Every mutated source compiles, and each changes only its own pristine lines (M11 :682-683, M17 :277, M33 :214; full table in static-checks.txt).
- **M11 targets the same element.** Its round-23 site was the open-range `ls-tree ... ".ufo/reports", errors="surrogateescape"` call in `parse_rounds` (e876b95:429-430); the tip site is the same call in `parse_rounds` (:681-683). The kill row matches round 23, F20-quotepath-open-range.
- **M33 is not a duplicate of M17.** The two sites run on disjoint paths: :246 runs only with a peel, and :275 is guarded by `not peel`. The M33 literal is not a substring of the M17 literal.
- **History not rewritten.**
  - 147f5bdd, efe58e9 and 5388b7c are all ancestors of 1fc41e3 (`merge-base --is-ancestor`, exit 0 each). The parent of 1fc41e3 is 5388b7cf. master and origin/master both equal 1fc41e3.
  - `git diff --stat efe58e9 1fc41e3` for preregistration.json and amendment-1 is empty.
  - The round-24 spot-check blob is unchanged: 5604fa86 at both 147f5bdd and 1fc41e3.
- **Routed defects 1-5 not contradicted.** The diff touches no report, original-view cell, lineage note, SKILL, SCORECARD or LOG. The commit message is the subject line only. The diff and the commit message claim no PM08 credit, no full isolation, no deadline or legacy parity, and no Git >=2.45 approval. Preregistration `open_l0` keeps R23-H2 open.
  - Watch item, not a harm in this diff: M02-lazy-fetch removes `"--no-lazy-fetch"` from `GIT_ISOLATION` (auditor :138), the same flag that PM08 reviews (promisor-mutants.py:57-63). An M02 kill in the C1 supporting run must not be reported as PM08 execution credit (preregistration C1 `not_claimed`).
- **Docstring statements versus code.**
  - "drifted from two literals": true. At the unchanged auditor, the old M11 literal has 0 occurrences and the old M17 literal has 2.
  - "M11 keeps its element": true.
  - "bare_objects() since round 24": true. `def bare_objects` first appears at 92063cf (round 24), not at ed1cc3a or e876b95.
  - "No id is reused or retired": true.
  - "M17 keeps its round-23 element": true for the text only; see Harm 1.
- **Tradeoff, not a harm.** The M17 and M33 literals include the comment line. A comment-only edit to the auditor would make them stale, but the instrument then fails fast with exit 2, so the failure is visible, not silent.

## Files written

- .ufo/waves/round-25/a2-build/advice/CriticC1NoHarm.md (this report)
- .ufo/waves/round-25/a2-build/out/CriticC1NoHarm/static-checks.txt (mutant tuple comparison, counts, compile and changed-line table)
- .ufo/waves/round-25/a2-build/out/CriticC1NoHarm/targeted-M11-M17-M33.json, .rc, .err (targeted mutant run, exit 0)
- .ufo/waves/round-25/a2-build/out/CriticC1NoHarm/git-ref-resolution-probe.txt (git probe and source quotes)

Scratch: /fast/scratch/hyaku/kama-r25a2/CriticC1NoHarm/ (clone, tmp, probe repo, fetched git sources). I started a full mutant run in my clone and stopped it after M05, because three other seats were already running the full list. No full-run result is claimed. No tools were installed and no llama-server was started.

Report: .ufo/waves/round-25/a2-build/advice/CriticC1NoHarm.md
