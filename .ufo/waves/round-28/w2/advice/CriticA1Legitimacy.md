# CriticA1Legitimacy — round 28, wave 2

**Verdict: partly.** The fixed-tip numerical target and the claim that A1 only refuses additional rows hold. A1's legitimacy as the pre-data frozen claim rule, and the phrase "before any data row was committed or scored", do not hold. This is a scoped critique, not a canonical admission judgment.

**Axes:** calibration (honest timing/provenance and self-assessment); depth (whether the measured evidence distinguishes field knowledge from a shortcut). No operability change is proposed or established by this review.

**Decisive evidence:** `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/w2/out/CriticA1Legitimacy/evidence.md` preserves the read-only Git output, timestamped session excerpts, and receipt values.

## Strongest counterexample: data really was evaluated before A1

At **08:35:53.929Z**, DataG01 imported `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/count-c1.py` using `importlib`, then applied its actual `REJECT_RE`, `literals`, `same` and `outcome_text` to four live data-row drafts. At **08:35:54.037Z**, the successful tool result printed all four rows `True` and **`all rows pass counter primitives: True`**. This is not merely a source read or data gathering. It evaluates row eligibility using the frozen counter's functions.

The L1's own timestamped transcript first implements A1 at **08:37:23.720Z** (successful write at 08:37:23.732Z), simplifies its refusal at 08:37:36.767Z, and lands it in **75b78bb4 at 08:38:16Z**. Thus the data-seat evaluation demonstrably predates both the amendment's writing and its commit. The preregistration's approximate `~08:45Z` is also inaccurate; the edit occurred around 08:37Z.

DataG11 additionally replayed copied comparison functions at 08:35:14Z; DataG15 replayed the live predicate offline and got `ALL FOUR ROW CHECKS PASS` at 08:36:53Z. These are corroboration, not falsely described as complete counter runs or direct imports. The direct-import counterexample is DataG01.

**Narrow boundary:** this evidence is not a pre-A1 run of the full integrated registry through `count-c1.main()`. The final table/registry first commits in e49b4cf7 at **08:55:40Z**, after A1. "Before data was committed" is supported; treating that as "before any seat scored data" is not. Even if "scored" were restricted to full counter invocations, the already scored A0 control seats at 5ebe7b1b precede A1, and the explicit freeze rule covers **any seat**.

## Chronology and authority

- A0 freezes in d8bf1804 at **08:14:03Z**; scored A0 controls land in 5ebe7b1b at **08:26:53Z**.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/w1/dispatched-at.txt:1` records 08:30:37.161106Z. `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/w1/spawn-result.txt:1-4` distinguishes the initial refused attempt from successful data dispatches at **08:31:50Z** and **08:32:50Z**; the remaining chunk starts at 08:33:50Z.
- A1 is explicitly motivated by returned DataG03/05/07/08 outcomes in `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/preregistration.json:41` and `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-28.md:38-45`. It is data-informed, not merely pre-commit.
- A1 controls land in fb10d9da at **08:53:48Z**; first committed table/registry data lands in e49b4cf7 at **08:55:40Z**. This ordering is real but does not undo earlier scoring or data exposure.

The binding rule is `/home/vgpnk/Projects/shokunin/.ufo/prompts/kama-round-28.md:357-360`: **"A rule changed after any seat has scored is not the claim's rule, whatever attacks it later passes"**. The preregistration's own kill rule at `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/preregistration.json:17` likewise forbids changing the predicate after any control or data seat scores. A later artifact's label `pre_data_amendment_A1` and its new freeze point cannot override either rule. No local exception authorizing an amendment after observed/scored data is supplied.

## What holds, and the sense in which the amendment helps the claim

The read-only counter diff d8bf1804..75b78bb4 adds `conversions(sent)` and an additional `e:generic-conversion` refusal. It does not add a favorable acceptance branch, lower target 18, or relax the existing checks. **For the same rows and observations, A1 only refuses more rows.**

Existing fixed-tip receipts agree:

| rule | registered | counted | target | numerical met |
|---|---:|---:|---:|---|
| A0 | 34 | 34 | 18 | true |
| A1 | 34 | 26 | 18 | true |

Evidence: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/final/c1-A0-e49b4cf7-receipt.json` and `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/final/c1-e49b4cf7-receipt.json`. All eight changed final-row verdicts are losses, not gains. **Selecting A1 rather than A0 does not flip the landed data's numerical `met` result.**

However, that does **not** make the choice immaterial to validity: the type-only shortcut in `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/controls-A1/CtlA1Conversion/REPORT.md:12-25,50-57` meets **A0 at 20/52**, but fails **A1 at 0/52**. Thus A1 repairs the very distinction on which the measured depth claim depends. The old scored fixtures also lose successes (source-blind 14→9, label-keyed 12→7); BlindPlus is one observed policy at 11/38, not a universal ceiling. Passing later controls cannot retroactively establish a valid original freeze.

There is also disclosed post-rule data adaptation: at **08:37:50.850Z**, the L1 tells DataG03 that `min_p -0.25 → 0.0` would be refused and requests a new input `-1.5`; the seat replaces the row following a new live probe. See `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/w1/advice/DataG03.md:4,28-39`. The rule remains refusal-only on a fixed dataset, but the actual collection was not held fixed. This is not evidence of invented outcomes or enough to make the numerical target depend on A1; it is another reason not to describe the process as pre-data.

## Smallest safe correction and exact report wording

Correct the timing/provenance sentences and distinguish the original claim measurement from the post-data counter repair. Preserve both existing receipts, target 18, and the technical table; do not amend again, re-label A1 retroactively as pre-data, or present `met true` as resolution of the freeze breach. The canonical judge retains the final ruling.

Recommended report wording, verbatim:

> C1 reaches the numerical target at e49b4cf77046024551ba83d490ef83d9dee061ed under both rules: A0 counts 34/34 and A1 counts 26/34 against 18. A1 is a post-data-informed counter repair, not the rule frozen before data: DataG01 had already evaluated four live row drafts using the A0 counter's own primitives at 08:35:54Z, before A1 was written at about 08:37:23Z and committed at 08:38:16Z. It preceded the first committed data table/registry, not all data observation or scoring; min_p was subsequently re-probed to satisfy the new restriction. A1 only removes successes for fixed rows and does not change the landed data's numerical met result. But a declaration/type-only control meets A0 at 20/52 and falls to 0/52 under A1, so the repair changes shortcut discrimination. The round prompt forbids replacing the claim's rule after any seat has scored. We therefore report the original C1 measurement with its shortcut-validity defect and freeze-rule breach, and the A1 result as post-data repair evidence, not as a verified preregistered depth gain; final disposition belongs to the canonical non-author judge.

This fixes false provenance and overstatement in reporting; it does not erase the historical breach or supply a new independent pre-data experiment. The stricter predicate is useful counter-quality work, but exchanging freeze validity for better shortcut rejection is a tradeoff, not proof of the original measured claim.

## Scope and exercised checks

Read the required preregistration, lesson, dispatch records, canonical prompt and all three A1 control reports; inspected the requested read-only Git log, path-limited data-landing log, amendment metadata and counter diff; read existing receipts and timestamped seat/L1 transcripts. No counter, llama-server, tests, judge, other agent runtime or Git/jj write was invoked. No tracked lane files were edited. Tool installs/updates: none.
