# K01C2DoNothingCritic — round 60 C2 falsification (do-nothing registry)

## Result
Counterexample found: round60-c2-counter.py prints **met=True** for a registry that says nothing true about Ollama's behavior as it relates to the 14 lines. The counter checks line coverage, quote substring, predicate evaluates equal to the verdict, and mutation sensitivity. It never checks that a predicate is about the statement on its line.

Claim attacked: C2-r60 (freeze.txt lines 28-43; counter docstring) — "every line covered ... at least 5 rows over at least 4 distinct lines carry a live predicate ... falsifiable ... controls rejected".

## Method (scratch only)
importlib on tools/round60-c2-counter.py; population(repo, BASE) → 14 lines (9 in ollama-evidence-replay.md: 35,44,46,60,141,170,294,301,302; 5 in served-identity-crosswalk.md: 29,45,51,103,132). Registry built by build.py (in out dir). Then ran the real CLI against a scratch clone of the lane (git clone --no-hardlinks into /fast/scratch/..., toplevel asserted) with the registry committed in the clone at registry/ollama-live-claims-r60.tsv. No amendment file at tip (0 blobs), none needed: all verdicts confirmed, so contradicted=0.

## Registry (cheapest form: 1 predicate string pasted onto 5 lines, 9 boilerplate rows) — out/min.tsv
Header: id path line quote predicate verdict observed reason. Quotes are any 3–8-word substring of the base line.
- D0..D4 (lines 35,44,46,60,141 of ollama-evidence-replay.md): predicate `c['version']['version'] == '0.40.11'`, verdict `confirmed`
- D5..D13 (lines 170,294,301,302 + all 5 crosswalk lines): predicate empty, verdict `not-observable`, reason `xxxxxxxxxxxxxxxxxxxx` (20 chars; the counter only checks len>=20)
Also the "varied" version (out/registry.tsv): five different one-field-equals-receipt-literal predicates (version=='0.40.11'; ps-before models==[]; tags-empty models==[]; v1-model-single object=='model'; generate done==True) and reason "not observable in this capture set".

## Exact outputs
Varied registry, CLI on clone: `population=14 rows=14 covered=14/14 evaluated=5 eval_lines=5 sensitive=5/5 bound=5 contradicted=0 amended=0/0 receipt_ok=1 controls_rejected=35/35 errors=0 met=True` exit=0
Minimal registry (one repeated predicate, x*20 reasons): identical line, met=True, exit=0.
In-process score(): {'rows':14,'covered':14,'evaluated':5,'eval_lines':5,'sensitive':5,'bound':5,'contradicted':0,'amended':0,'receipt_ok':True,'good_rows':14,'errors':0,'met':True}
controls(): {'tautology':(1,1),'verdict_flip':(5,5),'quote_corrupt':(14,14),'drop_line':(14,14),'tamper':(1,1)} — all rejected.
Caveat: the 35/35 controls rejecting is not evidence of honest registry; each control only perturbs the registry or receipt and asks whether met flips, and a do-nothing registry is as perturbable as an honest one.

## Why the controls miss it
- tautology control swaps predicate to `True` (non-falsifiable); my predicates are field==literal reads that mutation flips → "sensitive". Sensitivity ≠ relevance.
- Quote check is `q in line` with 3..25 words: no relation between quote, line statement and predicate.
- not-observable rows need only an empty predicate and len(reason.strip())>=20; unlimited share (9/14 here; the counter would accept 9/14, and 14-5 in general).
- Verdict flip only flips verdict on predicate rows; no control downgrades/relabels a not-observable row or swaps predicates across lines.
- Note also that predicates may be ones true by construction of the tool (version, empty-before-state), i.e. they test the tool's own run, not statements about Ollama.

## What additional frozen counter clause would reject it
A semantic-binding clause the counter itself enforces (not a seat read), pre-frozen as data, e.g.:
1. Binding map: a frozen table line-key → set of capture keys/fields the line's statement concerns (e.g. line 44 expires_at → c['ps-after']['models'][*]['expires_at']; digest join lines → tags/ps-after digest). Reject a live row whose predicate chains() (counter already extracts them) don't intersect its line's frozen field set; plus the quote's tokens must overlap the predicate's capture name or field tokens for at least 1 token.
2. A cap/requirement on not-observable rows: each must name a specific missing capture or endpoint in its reason and not exceed a fixed fraction (or each population line must be either live-bound or have a reason that matches a frozen list of unobservable causes).
3. A swap control: permute predicates across live rows; honest bound rows must flip met (the binding clause rejects), the do-nothing set is exactly what remains invariant.
4. Distinct predicates minimum (>=5 distinct chains, ≥3 distinct captures).
A single clause (1) with the frozen map is sufficient; (2) hardens the dodge route.

## Does the counter count self-assessment mismatch?
No. freeze.txt C2 (lines 28-43) and the counter docstring do not contain any measure of mismatch between the lane's self-assessment (its INFERENCE labels/confidence) and repo/live state as a count or rate: contradicted=K only counts rows whose predicate evaluates false and whose verdict was recorded as contradicted, and K=0 is accepted. It requires contradicted rows to be named in the amendment doc (amended==contra), but never requires any mismatch to exist, never counts not-observable rows as a mismatch/uncertainty, never compares a stated confidence/labelled level with outcomes, and never checks repo state outside the corpus lines (e.g. cited ids, S-rows). If the round prompt demands a calibration claim to "count any mismatch", the counter does not do it; the do-nothing registry gets met=True with mismatches=0 by construction and a lane that hides mismatches in not-observable rows is undetectable.
Better description: the claim is a *coverage plus live-checkability* axis (operability/documentation-evidence — "claims about a surface graded against captures"), or "evidence/provenance of statements", not calibration, unless it adds (a) a frozen outcome set, (b) a mismatch count/rate tied to the lane's self-stated confidence, (c) a falsifiable denominator that cannot be gamed by not-observable rows. Currently it measures: all INFERENCE lines are acknowledged by rows, ≥5 are machine-checked against one receipt.

## Smallest safe correction
Clause 1 (frozen binding map keyed by population line) plus a not-observable cap (e.g. ≤ 50% of lines or each reason matching a frozen cause list) and a predicate-swap control. Rerun the do-nothing registry in out/ to show met=False.

## Files
out/build.py, out/registry.tsv, out/min.tsv. Scratch clone removed at exit.
