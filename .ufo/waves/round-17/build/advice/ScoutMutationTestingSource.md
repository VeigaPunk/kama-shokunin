VERDICT: confirm — PIT Mutation Testing's docs are a primary, maintained source that define killed/survived mutants and mutation score as killed-over-all-mutations.

# Primary source

- **PIT Mutation Testing — Basic Concepts**, https://pitest.org/quickstart/basic_concepts/, §Running the tests.
  - Quote (8 words): "**Killed** means a test caught the mutation successfully."
  - Quote (11 words): "**Survived** means the mutation was not detected by the covering test."
  - The same section lists seven explicit outcomes — `Killed`, `Survived`, `No coverage`, `Non viable`, `Timed Out`, `Memory error`, `Run error` — so "survived" is a named outcome, not merely "not killed".
  - Quote (18 words): "**No coverage** is the same as **Survived** except there were no tests that exercised the line of code"
- **PIT Mutation Testing — Command Line Quick Start**, https://pitest.org/quickstart/commandline/, §`--mutationThreshold` — the mutation-score arithmetic.
  - Quote (19 words): "This is a percentage (0-100) that represents the fraction of killed mutations out of all mutations."
- Corroborating definition on the homepage, https://pitest.org/, §"What is mutation testing?" (51 words):
  - Quote (17 words): "If your tests fail then the mutation is killed, if your tests pass then the mutation lived."
  - Quote (13 words): "The quality of your tests can be gauged from the percentage of mutations killed."
  - Formal docs use "Survived"; the homepage's "lived" is prose shorthand. The FAQ also uses the formal pair: "a mutant may be detected as timed out on one run, but killed or surviving on another" — https://pitest.org/faq/, §"Is it random?" (18 words).

# Maintained, and what "current" means

- Source of the docs is version-controlled: `git ls-remote https://github.com/hcoles/pitest-site refs/heads/gh-pages` → `614bec6fd16670852e94c8cc03a002f6bf05db09` (observed 2026-10-20); the raw files read above came from that branch head. [INFERENCE] the fetched raw content corresponds to that commit because both reads bracketed the same ls-remote head.
- The tool is released: Maven Central `search.maven.org/solrsearch/select?q=g:org.pitest%20AND%20a:pitest&rows=1&wt=json` returns `"latestVersion": "1.19.1"`, timestamp `1744029039839` = `2025-04-07T12:30:39Z`, `"versionCount": 126` (observed). The docs themselves document removals "in 1.9.0" (`--dependencyDistance`) and a `--testStrengthThreshold` parameter, so they are not a frozen legacy page.
- GitHub REST (`api.github.com/repos/hcoles/pitest`) returned HTTP 403 unauthenticated; Maven Central plus `ls-remote` were used instead. No claim about commit frequency beyond the above.
- **mutmut note:** https://mutmut.readthedocs.io/ and `/en/latest/` currently serve the GitHub repository page (`boxed/mutmut`), not rendered docs; no citable definition passage was reachable there. PIT is the stronger primary source anyway. [INFERENCE] RTD redirects to repo because the project publishes docs from the README.

# Why this grounds C1's counting method

1. **Kill direction is fixed by the source.** A mutant is killed iff the detector (here `tests/probe-verdicts/check.py`) fails on it; surviving means the detector still passes. This is exactly the polarity C1's `mutants.py` must implement — a mutant that weakens grading and still yields PASS is *survived*, i.e. a defect in the detector, not a pass.
2. **Score denominator.** PIT defines the score as killed/all, so a before→after report must print `killed/total` and the ratio, never an unlabelled "55/17" or "72/0" pair. If C1 keeps the round-16 frozen pair, state whether each number is killed or survived; the source's formula disambiguates (killed first, total second).
3. **No-coverage is not a kill.** PIT counts unexercised mutants as survived-equivalent ("No coverage is the same as Survived"). For a fixed nine-file corpus every check.py mutant is exercised, so this mainly matters as a conservative fallback: a mutant no matrix row reaches must not be scored as killed.
4. **Timeouts are a separate outcome.** PIT lists `Timed Out` apart from killed/survived and the FAQ records run-to-run variance ("killed or surviving on another"). C1's `timeout-pass` mutant should therefore be counted as survived-unless-the-detector-fails, and the runner should record timeouts distinctly rather than folding them into kills.
5. **Determinism is claimed by the tool, not assumed.** FAQ §"Is it random?" (11 words): "Given the same input Pitest will always generate the same mutants". [INFERENCE] C1 may borrow this as a design target for its mutant set enumeration; it is PIT's property, not evidence about `mutants.py`.
6. **Equivalent mutants exist and shift the score.** §`--mutationThreshold`: "your build may contain equivalent mutations" (6 words). [INFERENCE] C1 should not silently drop survivors as "equivalent"; if it excludes any, the exclusion rule must be stated and justified per mutant, otherwise 5/5 surviving stays a detector finding.
7. **Test strength is the sharper metric.** §`--testStrengthThreshold`: "the test strength (killed / (killed + survived), excluding mutants where no coverage information is available)" (17 words). [INFERENCE] For C1's pair this is the better headline number than raw kills, because the corpus breadth (72 rows) is constant across the before/after runs.

# Candidate SOURCES row (S042)

Next free id is S042: `corpus/SOURCES.md:11` is the registry header, rows run `S001`–`S041` (`corpus/SOURCES.md:11-53`), and `grep -in 'mutation\|mutant' corpus/SOURCES.md` returns no hits — no existing row covers this. Row is written for the 11-column contract at `corpus/SOURCES.md:11`; per contract rule 2, `anchor`/`teaches` must be final at first commit (only `status`/`recheck`/`used-by` are editable later), so this row places the commit pin and release fact in `anchor`.

| S042 | PIT Mutation Testing — Basic Concepts — https://pitest.org/quickstart/basic_concepts/ | docs | A | mutation-testing outcome vocabulary (killed, survived, no coverage, timed out) and mutation-score arithmetic as PIT defines them; not a claim about non-JVM harnesses | §Running the tests (outcome list and *Killed*/*Survived*/*No coverage* definitions); §`--mutationThreshold` and §`--testStrengthThreshold` of https://pitest.org/quickstart/commandline/; docs source `hcoles/pitest-site` gh-pages `614bec6fd16670852e94c8cc03a002f6bf05db09`; PIT 1.19.1, Maven Central 2025-04-07; read 2026-10-20 | "Killed means a test caught the mutation successfully"; "Survived means the mutation was not detected by the covering test"; mutation score is "the fraction of killed mutations out of all mutations"; no-coverage counts as survived; test strength is killed/(killed+survived); timeouts are a separate outcome with run-to-run variance | mined | 2026-10-20 | on-release | .ufo/waves/round-17/c1/mutants.py |

[INFERENCE] Tier A is defensible only for the narrow `scope` above (PIT's own definitions). If L1 wants the row to assert the field-wide definition, tier should drop to B and the scope widened accordingly; a second tool's docs (or a textbook/standard) would then be needed for cross-tool corroboration.

# Limitations

- PIT is a JVM/bytecode mutation system. Only the **vocabulary and score arithmetic** transfer to kama's Python-source mutants; PIT's mechanics (coverage targeting, in-JVM mutant insertion, mutator catalogue) do not. Marked inference where C1 borrows the determinism claim.
- No page states a "definition of mutation testing" as a formal standard; PIT's homepage 51-word block is the definitional text used. If the Gate demands a standards body or peer-reviewed source, this row does not satisfy that stronger form.
- mutmut docs were not citable (RTD → GitHub repo redirect). Not needed for the claim.
- Read-only seat: `corpus/SOURCES.md` was not edited (scribe seat owns it); no lane gates, `measure.py`, `mutants.py`, or `controls.py` were run. No files written outside this Report.

# Installs

None.
