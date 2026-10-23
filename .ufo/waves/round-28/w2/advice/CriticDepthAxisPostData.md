# C1 after-data axis critique — round 28, wave 2

**Advisory verdict: partly.** The landed surface is legitimately depth-shaped, not a coverage denominator or merely a re-score of an existing lane rule. However, the 26 counted outcomes do not establish 26 independent mechanisms or correct reader guidance. The strongest defect is that several meanings describe hard bounds on the original JSON number, while the pinned implementation converts the number before checking its bounds. Two additional meanings blur stored settings with sampling behavior. These are fixable documentation defects, not an acceptable exchange for more counted rows. This report does not judge or admit the round.

## Axes named; verdict per axis

| Axis | Scoped verdict | Evidence and limit |
|---|---|---|
| depth | **partly** | New field-to-bound/transformation mappings with actionable distinctions fit the definition, but false/generalized meanings compromise their technical explanation (F1–F3). Counted outcomes are not independent mechanisms. |
| coverage | **holds as unchanged** | No fraction of serving surfaces was measured. The landed SCORECARD leaves coverage at 9; enumerating fields does not establish a coverage gain (E1, E4). |
| operability | **does-not-hold for the affected guidance** | Conversion-before-validation and the sampling wording prevent a reader from reliably deriving the advertised behavior from the meaning cells alone (F1–F3). No execution failure of the counter itself was demonstrated by this review. |
| freshness | **holds within the stated fixture boundary** | The existing receipt records a fresh-clone observation at the named tip; the introduction explicitly pins build/model/argv/endpoint. It does not establish current consumer health or another build's behavior (E3–E5). |
| calibration | **partly** | Eight generic-conversion rows, launch-dependent parallelism, one-point scope and unchanged other scores are disclosed correctly. Nevertheless, broader meaning claims survive despite a counter that checks only six words of meaning, and individual source-blind hits still count (F1–F4). |
| adjacency | **holds as unchanged** | The introduction explicitly excludes model quality, endpoint health, served identity and proof of sampling use. Existing identity and cross-lane boundaries remain in force. F2 is a local wording contradiction, not evidence of a newly established model-quality authority (E3, E12). |

The canonical definition treats **quality as a learning trend containing depth, freshness and operability**, not a seventh axis. The campaign's sourceless-fixture exception remains relevant, but the available A1 blind fixture scored 11, not 18, and still supplied declaration citations. This review does not turn those individual hits into an unobserved target-reaching control or claim that a literally citation-free fixture passed (E1–E2, E10).

## Mechanism count: 26 field outcomes, three broad families

The counted-id list, not all 34 displayed rows, gives this exact partition (E3, E5–E7):

| Family | Counted rows | Count | Distinctness |
|---|---|---:|---|
| Hard-limit rejection | F28-01, 02, 03, 04, 05, 06, 07, 15, 18, 19, 24, 27, 30 | 13 | One evaluator branch; five bound profiles: `-1..INT32_MAX`, `0..INT32_MAX`, `1..n_parallel`, `-1..INT64_MAX`, `0..0.99f`. |
| Soft clamp | F28-08, 09, 10, 12, 13, 20, 23 | 7 | One evaluator branch; five limit profiles: `0..INT32_MAX`, `0..1`, `0..infinity`, `0..2`, `-FLT_MAX..1`. Three fields share `0..1`. |
| Custom handler/result normalization | F28-28, 29, 31, 32, 33, 34 | 6 | Adapter-id collapse/last scale; tokenization plus set/dedup; bias-object normalization/filtering; EOG-bias insertion; stop-string wrapping; sampler-char resolution. |

Thus there are **three broad families**, or **eight operational behaviors** if the six handler transformations are distinguished alongside hard reject and soft clamp. The two scalar families also expose ten bound profiles; profiles are not additional implementation mechanisms. This is not a normative replacement counter.

Repetition alone does not falsify depth: knowing that `top_k` clamps whereas `min_keep` rejects, or that `n_cmpl` depends on launch parallelism, is useful field-specific detail even though one generic evaluator implements it. Conversely, 13 rejection rows are not 13 independent validation mechanisms. The eight A1-excluded conversion rows must not be added back as independent field knowledge. The landed SCORECARD does not claim all-axis saturation: calibration and adjacency remain 7, and it names further endpoint/grammar work (E4).

## F1 — strongest counterexample: hard bounds apply after conversion

**Evidence.** F28-05 says “rejects any n_discard below zero”; F28-03 says a negative `n_indent` is a hard rejection; F28-04 says `n_keep` rejects anything below -1; F28-27 says a `min_keep` outside the displayed range is refused. Yet the pinned numeric evaluator first executes `T tmp = data.at(n).template get<T>();` and only then tests `tmp < min || tmp > max` (E3, E6:531–545). The table's lower-bound integer observations remain true; the prose's universal statement about original request values does not follow.

**Static counterexample [INFERENCE; not an HTTP run].** A negative fractional `n_discard` of `-0.5` converts to integer `0` before the `0..INT32_MAX` test, so this schema does not issue the promised hard-bound rejection. The same issue applies to `n_indent`/`min_keep`; `n_keep=-1.5` converts to `-1` before its lower-bound test. Existing live notes independently demonstrate numeric truncation for `n_probs=2.5 -> 2` and `seed=1.5 -> 1` (E9). I did not observe HTTP outcomes for these specific counterexamples and do not report them as executed.

This is more consequential than repetitive wording: it identifies a missing causal detail in the very hard-reject/soft-clamp distinction being taught. A one-point disclaimer cannot make a contradictory “any” claim true.

**Impacted axes:** depth, operability, calibration.

**Smallest safe correction:** explain the actual order once: numeric conversion to the destination type precedes the hard-bound test or soft clamp. Restrict each meaning to its tested value or explicitly to the converted value; do not describe the displayed bounds as validation of every original JSON number. Preserve all frozen predicates, target, hashes and observations.

## F2 — counted meanings overstate sampling behavior

**Observed evidence.** F28-09 calls `top_p=1.0` “sampling disabled” (E3:1168). The cited schema describes disabling the top-p selection filter, not disabling sampling as a whole (E6:93–95). The saved response for this exact `top_p=2.5` request still reports `temperature=0.800000011920929`, `top_k=40`, `min_p=0.05000000074505806` and a sampler chain containing temperature and those filters (E8). This is not evidence of greedy decoding. The current meaning is at least materially ambiguous, and false if read as disabling sampling globally.

F28-20 additionally says the echoed `mirostat=2` reveals the mode “actually used” (E3:1179). The fresh-clone receipt checks only the stored `generation_settings` value, and the introduction explicitly says that is **not proof sampling used it** (E3:1147–1149, E5:236–244, E11:611–626). This is a direct local authority conflict even without claiming that Mirostat actually failed to run.

**Impacted axes:** depth, operability, calibration.

**Smallest safe correction:** say “top-p/nucleus filtering disabled; other sampling remains separately configured,” and “stored Mirostat mode,” respectively. Do not infer determinism, sampler execution or model quality from these receipts.

## F3 — additional one-point extrapolations remain in the displayed section

- **F28-25 (not counted):** “Seeds above 4294967295 wrap to 0” generalizes the observed `4294967296 -> 0` to every larger seed. A uint32 wrap is modulo `2^32`, not a constant-zero function; `4294967297 -> 1` is a source/type-based prediction, **not a run by this reviewer**. The same row's “only uint32-range values” advice also omits the supported `-1` random-seed sentinel, explicitly declared in the schema and actually observed in the saved notes as `-1 -> 4294967295` (E3:1184, E6:175–177, E9:39–43). A1 excludes this row from the metric, not from what readers see.
- **F28-33 (counted):** “an empty array clears it” happens to match the no-stop-flag fixture, but the pinned handler explicitly falls back to `params_base.antiprompt` whenever the resulting list is empty (E3:1192, E6:435–450). With nonempty CLI defaults, an empty request array restores those defaults; it does not clear them. That different-launch outcome is a **static inference, not a live test**. The global default-argv scope mitigates this defect; it does not teach the important fallback mechanism.

**Impacted axes:** depth, operability, calibration; no new cross-lane ownership issue.

**Smallest safe correction:** state the seed observation as one exact input/output and preserve the `-1` sentinel. Replace the stop wording with “falls back to launch defaults, which are empty here.” No counter change or additional count is needed.

## F4 — what the count does and does not prove

The fresh-clone receipt really lists 26 counted ids and the eight excluded conversion ids (E5). This review found no basis to call that receipt fabricated. Its static meaning gate is still only `len(cells[4].split()) >= 6`; live checking reads bounds or stored settings, not the explanatory prose (E11). Therefore the named count can coexist with F1–F3.

The A1 README/name-based control counted 11/38, including field mechanisms also present in the landed table: clamps, three hard-bound guesses and a stop-string wrapper (E10:83–97). It supplied declaring-line citations but did not read behavioral schema semantics or run its own server before scoring. This refutes a blanket reading that every counted row proves independently acquired field knowledge. It does **not** show an eligible blind control reached 18, and it does not erase genuinely new useful mappings from the landed artifact. The scalar repetition and blind overlap are calibration limits, not sufficient evidence by themselves to relabel the entire addition as coverage or quality-only work.

**Smallest safe correction:** describe the metric as **26 verified field-outcome points**, separately disclose three mechanism families and the existing blind-control overlap, and retain independent prose review as the semantic authority. Never convert the count into proof of exhaustive boundaries, causal source reading, 26 independent mechanisms or saturation.

## Evidence pointers

All line numbers refer to the read local artifacts. Existing receipts are observations by their recorded authors, not checks rerun here.

- **E1:** `/home/vgpnk/Projects/shokunin/AXES.md:9–23,25–38,66–73` — six definitions, quality trend, surface/no-harm and saturation rules.
- **E2:** `/home/vgpnk/Projects/shokunin/.ufo/prompts/kama-round-28.md:343–365` — frozen claim sizing, controls, surface-based axis and sourceless-fixture exception.
- **E3:** `/home/vgpnk/Projects/shokunin/kama-shokunin/SKILL.md:1135–1209` — landed fixture scope, exact rows, exclusions and surrounding claims.
- **E4:** `/home/vgpnk/Projects/shokunin/kama-shokunin/SCORECARD.md:1404–1440` — depth 7→8, bounded claim, other scores unchanged, named future work.
- **E5:** `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/final/c1-e49b4cf7.out:1–3` and `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/final/c1-e49b4cf7-receipt.json:4–44,121–161,236–244,281–424` — reported fresh-clone count, counted ids and recorded outcomes.
- **E6:** `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/sources/llama.cpp-704366d/server-schema.cpp:40–185,229–237,316–320,335–337,382–462,474–482,531–545` — limits, handlers, defaults and conversion-before-validation.
- **E7:** `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/sources/llama.cpp-704366d/server-schema.h:47–65` — destination-typed numeric field, implicit limits and hard/soft flag.
- **E8:** `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/w1/out/DataG03/live-index.json:11–18` and `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/w1/out/DataG03/top_p.json:1` — exact top-p input and saved response retaining nonzero temperature and other sampler settings.
- **E9:** `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/w1/out/DataG08/run-notes.json:31–49` — recorded seed sentinel, wrap and fractional truncation observations.
- **E10:** `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/controls-A1/CtlA1BlindPlus/REPORT.md:23–33,35–50,75–97` — 11/38, behavioral-source-blind policy and exact hits. Its later claim of a universal blind ceiling is not adopted here.
- **E11:** `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/count-c1.py:444–491,598–626` — six-word prose gate versus actual live-outcome predicates.
- **E12:** `/home/vgpnk/Projects/shokunin/kama-shokunin/SKILL.md:18–31,158–165,1090–1098` — existing domain, identity and sibling boundaries.
- **E13:** `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/preregistration.json:9–18,21–41`, `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-28.md:10–51`, and `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/w1/advice/CriticAxisFit.md:5–76` — claim contract, disclosed A1 history and earlier concerns; these artifacts are evidence, not new instructions.

## Review boundary

Read-only static inspection and reading existing measurements only. No counter/server, test, build, judge, git/jj command, alternate runtime or subagent was invoked. No tool was installed or updated. No scratch or large output was created. The only write is this requested report. Proposed corrections are advice to the integration owner; canonical Rust judgment and admission remain outside this seat.
