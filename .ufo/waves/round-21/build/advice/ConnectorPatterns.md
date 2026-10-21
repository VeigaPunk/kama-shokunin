VERDICT: confirm - C1 and C2 share an 'identity summaries silently dropping members' pattern; 8 concrete lane instances cataloged with path:line.

# ConnectorPatterns — cross-claim pattern: silent member drops in identity summaries

## 1. Concrete Instances with path:line
- **Install tree regular files (`tools/kama-llamacpp-live.py:192,198`)**: In `install_tree()`, `except OSError: continue` silently drops unreadable/unstatable files; `combined` SHA-256 hashes only survivors. [Executed: `chmod 0` on `f2.so` -> `tree` holds only `['f1.so']`, returns clean digest `57387bbe…`].
- **Install links symlinks (`tools/kama-llamacpp-live.py:222`)**: In new `install_links()`, `except OSError: continue` silently drops unreadable symlinks on `os.readlink()`. [Executed: mocked `OSError` on `l2.so` -> `links` holds only `['l1.so']`, returns clean `install_links_sha256`]. Non-regular/non-link entries (sockets, FIFOs, directories) are omitted from both digests.
- **Census selftest denominator omission (`tools/error-verdict-census.py:422,430`)**: `selftest()` prints `ok (15 pinned cells…)` but loop filters `r["instrument"] == SURVIVORS`, executing only 2 cells. 13 cells (8 grid, 5 citation) are silently omitted from selftest execution.
- **Audit commit population filter (`tools/report-landing-audit.py:88,92`)**: `round_commits()` drops commits if author is not `f"{lane}-shokunin"` (dropping integrator commits e.g. `8bf99ca`, `37bd4c5`) or subject deviates from `^(?:round-{rnd}:|checkpoint\(r{rnd}\))` (e.g. `round-21 (hyaku phase 2):`, `round-21 :`).
- **Audit hex case sensitivity (`tools/report-landing-audit.py:50,51`)**: `FULL` and `ABBREV` match only lowercase `[0-9a-f]`; uppercase hashes `[0-9A-F]` in reports are silently dropped.
- **Probe served model IDs (`tools/kama-probe.sh:343,366`)**: `except Exception: sys.exit(0)` converts malformed JSON to empty output; `for g in groups: ... break` takes only first non-empty group, silently dropping lower-precedence models.
- **Refused ports (`tools/kama-llamacpp-live.py:287-295`)**: Regex tuple drops non-matching formats; `except ValueError: continue` drops malformed ports from refusal set.
- **Fake child cleanup (`tests/llamacpp-live/controls.py:788,799`)**: `except (OSError, ValueError): return` silently aborts orphan cleanup if pidfile is unreadable.

## 2. Motivating Quality Anchors (`corpus/QUALITY.md`)
- **KQ9 (line 31)**: negative/scope claim requires full-set read (count first, then read).
- **KQ17 (line 72)**: finding and aggregate count reported separately; fail-closed precedence.
- **KQ25 (line 142)**: counter requires completed relevant run; errors must not vanish from denominator.
- **KQ27 (line 144)**: quoted count tied to measured revision; no hardcoded selftest tally as coverage.

## 3. Affected Axes
- **Calibration (7 -> 7/8)**: Prevents undercounting and false-clean verdicts in audits and selftest tallies.
- **Operability (8 -> 8)**: Guarantees install receipts (`install_tree_sha256` and `install_links_sha256`) fail closed on unreadable/partial trees instead of emitting truncated identity digests that pass `check-receipt.py`.

## 4. Proposed Move: Fail-Closed Member Accounting
1. In `tools/kama-llamacpp-live.py` (`install_tree` and `install_links`): replace `except OSError: continue` with fail-closed behavior: return `(tree, None)` if any entry in `directory` raises `OSError` or is unhashable, ensuring receipts never pin partial trees.
2. In `tools/error-verdict-census.py` (`selftest`): align output tally to `len(survivors)` (2 cells) or run stub checks for all 15 pinned cells to satisfy KQ25 and KQ27.
3. In `tools/report-landing-audit.py`: flag non-matching round commits (integrator authors or variant subjects) as uninspected candidates rather than silently dropping them from `required`.

## 5. Risks and Contradictions
- Transient filesystem noise: fail-closed directory reads fail on ephemeral files; mitigated by running against clean install prefix [INFERENCE].
- Errata volume: stricter commit inspection may flag foreign commits; handled by existing `registry/report-landing-errata.tsv`.

## 6. Executed Verification
- `python3 tools/report-landing-audit.py --selftest` -> exit 0 (15 cases).
- `python3 tools/report-landing-audit.py --no-errata` -> exit 1 (9 uncorrected defects).
- `python3 tools/report-landing-audit.py` -> exit 0 (9 corrected, 0 uncorrected, status clean).
- `python3 tests/llamacpp-live/install-links-grid.py --selftest` -> exit 0 (12 cases).
- `python3 tests/llamacpp-live/check-receipt.py --selftest` -> exit 0 (9 valid, 1 not-eval, 90 mutations).
- `python3 tools/error-verdict-census.py --selftest` -> exit 0 (exercises only 2 of 15 cells).
- Detail: `.ufo/waves/round-21/build/out/ConnectorPatterns/omission-patterns.json`.
