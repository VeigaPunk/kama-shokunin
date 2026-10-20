VERDICT: confirm — both requested counts reproduce exactly, and an independent first-nonempty-line recount agrees.

## Findings

No actionable defect found in the routed-defect-2 correction or the checked lesson statements.

- **Round-16 falsify correction confirmed.** At `corpus/lessons/round-17.md:87`, the lesson states “strict first-line count is 34/40/0 + 5 nonconformant”; at `:101-105`, it gives 34 confirm / 40 partial / 0 refute, names the five nonconformant seats, and says the count tool reports them. The pinned-commit run returned exactly confirm 34, partial 40, refute 0, n/a 0, nonconformant 5; 79 files and 79 expected names, with no missing or unexpected names. The five listed names exactly matched the lesson: `ConnectSiblingCollision`, `ExecNoPythonFallback`, `ReviewLesson`, `ScribeNumbersLedger`, and `ScribeReportWaves`.
- **Round-17 build count confirmed.** The requested run returned confirm 34, partial 32, refute 1, n/a 15, nonconformant 0; 82 files and 82 expected names, with no missing or unexpected names. The categories sum to 82.
- **Independent cross-check agrees.** A separate script read each top-level Markdown file's first non-empty line and compared filename stems with the spec names. It reproduced both category counts and the same five round-16 nonconformant files. The count tool's relevant contract is visible at `.ufo/waves/round-17/count-verdicts.py:58-60` (anchored verdict expression), `:126-145` (top-level `.md` scan and nonconformant reporting), and `:169` (exit 2 only for unreadable files).

## Commands and results

All lane tools ran only in `/tmp/CountVerdictsRerun-clone`, cloned and checked out at `54a29268e2083caa2b1e0d54ee1e7d90961302f3`; each Python invocation used `PYTHONDONTWRITEBYTECODE=1`.

```sh
git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/CountVerdictsRerun-clone && git -C /tmp/CountVerdictsRerun-clone checkout -q 54a29268e2083caa2b1e0d54ee1e7d90961302f3
# exit 0

cd /tmp/CountVerdictsRerun-clone && PYTHONDONTWRITEBYTECODE=1 python3 .ufo/waves/round-17/count-verdicts.py .ufo/waves/round-16/falsify/advice --expect-names .ufo/waves/round-16/falsify/spec.json --json
# exit 0

cd /tmp/CountVerdictsRerun-clone && PYTHONDONTWRITEBYTECODE=1 python3 .ufo/waves/round-17/count-verdicts.py .ufo/waves/round-17/build/advice --expect-names .ufo/waves/round-17/build/spec.json --json
# exit 0
```

The independent recount command was run in the same clone with `PYTHONDONTWRITEBYTECODE=1 python3 - <<'EOF'` and a standard-library script that loaded both `spec.json` files, enumerated `pathlib.Path(advice_dir).glob("*.md")`, parsed each file's first non-empty line, counted verdicts, and compared spec-name sets to file stems; exit 0. Both primary JSON results reported `missing: []`, `unexpected: []`, `unreadable: []`.

## Residual risk and verification gaps

This attack covered only the two specified advice directories and the corresponding lesson claims; it did not rerun mutant/control suites or validate other round measurements. The utility scans top-level regular `.md` files (and ignores non-Markdown files); that scope matched the two requested directories and their complete spec-name sets. No installs or updates were made. The temporary clone was removed; the port check reported no listeners on 8080 or 34113.