# K2Negation — round 49 attack: v4 negation window and word token

Verdict: **the v4 negation window (`NEG_WINDOW`, tools/append-only-audit.py:212-213) is under- and over-inclusive — it misses six genuine negation forms (including all four named in the assignment) and rejects three rule-declaring lines — while the lane's 384 flagged lines are all correctly treated; the frozen C2 counter still passes 8/8 because none of its eight scenarios exercises any escape. Defect is in the instrument, not in the lane's current contract.**

## Method
All runs used my shared clone `git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin /fast/scratch/hyaku/kama-r49/K2Negation/lane` at tip `74558c71c38ceaeace15fd4cf8aa9d84977584b1` (READ-ONLY; no lane file touched). The v4 binder was executed by importing the tip's own `tools/append-only-audit.py` (source of truth; `NEG_WINDOW` and `binds()` at 212-213 / 216-233). The C2 counter was run once against the clone.

## F1 — false negatives (genuine negation binds; audit exits 0 when it should exit 1)
The window `(?:\b(?:not|never|no|nor|neither|non|isn't|aren't)\b|\bno longer\b)(?:[\s\-]+[\w'’]+){0,3}?[\s\-]+append[- ]only` misses:

| probe (declared_at line) | window | binds | tool exit / bad_declarations | should be |
|---|---|---|---|---|
| `score.md cannot be called append-only` | no | **yes** | 0 / 0 | unbound, exit 1 |
| `score.md can't be append-only` | no | **yes** | 0 / 0 | unbound, exit 1 |
| `append-only? No.` (negation after target) | no | **yes** | 0 / 0 | unbound, exit 1 |
| `not, as of round 40, append-only` (commas; 4 tokens) | no | **yes** | 0 / 0 | unbound, exit 1 |
| `isn’t append-only` (curly U+2019 apostrophe) | no | **yes** | 0 / 0 | unbound, exit 1 |
| `not—append-only` (em dash U+2014) | no | **yes** | 0 / 0 | unbound, exit 1 |
| `not append--only` (double hyphen) | no | **yes** | — | unbound |

Controls: `score.md is not strictly append-only` → window fires, unbound, exit 1 bad=1 (the counter's own `negated` scenario, reproduced); `score.md is append-only` → binds, exit 0 bad=0. Fixture harness mirrors the counter's binding scenarios (single commit; `score.md` row declared at the line; `--contract` + `--json`), see `out/K2Negation/fixtures-self-declared.txt` and `fixtures-cross-file.txt`.

Causes (tools/append-only-audit.py:212-213):
- `cannot`/`can't`/`can’t` are not in the negator alternation; `\bno\b` cannot match inside `cannot` (no word boundary).
- Only straight U+0027 is listed: `isn't|aren't`, so `isn’t`/`aren’t` (U+2019) escape; the generic token class `[\w'’]+` accepts curly but only *after* a negator.
- The tail `(?:[\s\-]+[\w'’]+){0,3}?[\s\-]+append[- ]only` requires whitespace/hyphen separators only: a comma, semicolon, em dash or double hyphen breaks the chain, so `not, as of round 40, append-only` (also >3 intervening words), `not—append-only`, `not append--only` escape.
- The window only looks **before** `append(- )only`: `append-only? No.` escapes.
- The four fixed strings `NEGATIONS` (line 141: `not append-only`, `not append only`, `no longer append`, `never append-only`) are substring scans and cannot catch the punctuation variants either.
- Round-48 seat K1Binding already listed three of these escapes in `.ufo/waves/round-48/w1/out/K1Binding.md:24` (`not an append-only`, `isn't append-only`, `never been append-only`); v4 catches exactly those three — the forms above remain. (For the record, `non-append-only` is correctly caught by `\bnon\b` + hyphen, and `no longer`/`never`/`not strictly` are caught.)

## F2 — false positives (rule-declaring line unbound; audit exits 1 when it should exit 0)
| declared_at line | window | binds | tool exit / bad_declarations | should be |
|---|---|---|---|---|
| `no edits append-only` | yes | **no** | 1 / 1 | bound, exit 0 |
| `not editable append-only` | yes | **no** | 1 / 1 | bound, exit 0 |
| `no one may edit append-only files` | yes | **no** | 1 / 1 | bound, exit 0 |
| `no edits: append-only` (punctuation control) | no | **yes** | 0 / 0 | bound — same sentence as row 1, verdict flips on a colon |

The window cannot tell "not **strictly** append-only" (negation) from "not **editable** append-only" / "no **edits** append-only" (declaration: the file IS append-only; `no edits` is the rule being declared). Verdict is punctuation-sensitive: `no edits: append-only` binds only because the colon breaks the regex's separator chain.

## F3 — word-token edges (`binds()` whole-word class is only `[a-z0-9_]`)
`(?<![a-z0-9_])` + token + `(?![a-z0-9_])` (append-only-audit.py:233): the K1Binding `catalog` fix holds for ASCII alnum, and `logs`/`logging`/`xlog`/`log_x` correctly fail — but hyphen, apostrophe, slash and Unicode letters are *not* excluded, so:

- `the co-log is append-only` binds LOG.md; `log's owner is append-only` binds; `a/b/log is append-only` binds; `log²`/`logĀ`/`日志log` bind.
- These are contract-compliant with the letter of the v4 definition ("not preceded or followed by [a-z0-9_]"), so this is a documented edge, not a contract breach; if whole-word naming is intended, the excluded class should also cover `' ’ - /` and non-ASCII letters (keeping `.` allowed so `LOG.md` self-naming still works).

## Lane sweep — every line the v4 binder treats as negated, judged
`git -C $S/lane grep -n -i -E 'append[- ]only' 74558c71…` ⇒ 7249 matches (1 binary file — `.ufo/waves/round-34/w1/out/ExecTransformAppend/seat.log` — not a text line). The v4 binder (`NEG_WINDOW.search(lower(line))` or a fixed NEGATIONS string) flags **384 lines**; full per-line table with my judgment in `out/K2Negation/flagged-classified.tsv` (raw: `flagged-raw.jsonl`; spans: `flagged-spans.txt`). Judgment:

- 245 genuinely negate the append-only property (`is not an append-only file`, `does not prove append-only`, `non-append-only knowledge entry`, `not append-only evidence`, `not called append-only until …`) — **right** to treat as negated.
- 126 are literal guard output / receipts (`no append-only violations`) or quoted examples of negation forms in docs/code — not declarations; **right** to reject.
- 7-8 are absence statements (`no append-only guard/verification/gate/event on …`) — **right** to reject.
- 5 meta/backticked mentions of the negation strings — **right**.
- Exactly 1 semantic false positive: `.ufo/waves/round-17/build/advice/ReviewSourcesHistoryRule2.md:28` — "… disclosure does not restore the append-only property the contract requires." affirms the property (the contract **requires** append-only); the window flags it because `not` sits ≤3 words before `append-only`. It is prose, never a `declared_at`, so no grading impact today.
- None of the 11 contract declaration lines (registry/append-only-contract.tsv at tip) is flagged; all bind under v4 (verified with the tool's own `binds()` per row).

→ the C2 lane leg stays clean (tool exit 0, bad_declarations 0), and the counter confirms `fixture=1 lane=1 scenarios=8/8 met=True exit 0` on this clone (`out/K2Negation/c2-counter-run.txt`). The defect is latent: the counter's `negated` scenario (round49-append-audit-v4-check.py:219-220) pins exactly `not strictly append-only`, so F1/F2 are invisible to it; the counter's own binder (NEGW, lines 91-92) is byte-identical to the tool's and inherits every case.

## Defect location and smallest safe correction
Defect: `tools/append-only-audit.py:212-213` (`NEG_WINDOW`) and `:141` (`NEGATIONS`); mirrors `tools/round49-append-audit-v4-check.py:91-92,115-117` (frozen — any fix must land in the tool and the counter together in a later round, or the counter must be extended).

Demonstrating commands (run in a fixture repo with the row `score.md\tA\tscore.md:1\t*\tfixture`):
```
python3 tools/append-only-audit.py --repo <fx> --to HEAD --contract <contract> --json
# F1: file score.md line 1 = "score.md cannot be called append-only" → exit 0, bad_declarations 0 (want 1)
# F2: file score.md line 1 = "no edits append-only" → exit 1, bad_declarations 1 (want 0)
```
Proposed v5 fix (smallest that covers F1 without widening F2):
1. Negator set: add `cannot|can't|can’t`, normalize apostrophes (`isn['’]t`, `aren['’]t`), and normalize dashes (`[-\u2013\u2014]`) in separators.
2. Let the separator run consume one optional interpunct: `(?:[\s\-–—]*[,;:!?]?[\s\-–—]+[\w'’]+){0,3}?` → still misses `not, as of round 40, append-only` unless the token cap is removed; if kept, raise the cap to cover the phrase and accept the risk.
3. The false-positive direction cannot be fixed lexically: `no edits append-only` vs `not strictly append-only` differ only in the *part of speech* of the intervening word. Recommend a clause-level parse: walk back from each `append(- )only` over ≤3 word tokens; treat as negation only if every intervening token is an adverb/adjective intensifier (`strictly, really, very, quite, entirely, currently, anymore, longer, an, a, the, …`) and none is a noun/verb (`edits, edit, may, one, …`). That keeps `not strictly append-only` unbound while binding `no edits append-only` and `no one may edit append-only files`.
4. For trailing negation (`append-only? No.`): after the append-only match, scan the remainder of the line for a bare negator at clause end.

## Tooling / housekeeping
No tools installed (none needed). No lane file was modified; no services started; no network calls besides the counter's own fixture-less run. Evidence copies listed below; scratch `/fast/scratch/hyaku/kama-r49/K2Negation` removed after copying.

## Absolute paths written
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/K2Negation.md (this report)
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/K2Negation/negation-window-probes.txt
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/K2Negation/fixtures-self-declared.txt
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/K2Negation/fixtures-cross-file.txt
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/K2Negation/word-token-probes.txt
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/K2Negation/flagged-classified.tsv
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/K2Negation/flagged-raw.jsonl
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/K2Negation/flagged-spans.txt
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/K2Negation/flagged-nontrivial.txt
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/K2Negation/c2-counter-run.txt
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/K2Negation/c2-counter-stdout.txt
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/K2Negation/analyze-import.err
