# CR02ThresholdCounter — attack on the frozen C2 counter (round 91, w1)

## Scope
- C2 at F=`9a41912a598cad00f7ff08391586a0ef3732bbed`, M2=`3f317ecd211e80929c673e306e3230be287fdf20`.
- Counter bytes at F, M2 and the worktree are one file: `fc304abd51135d464c402672c4c894bcff9b1bbe6b7c1565e7d6cf833f109661`
  (`git show F:tools/round91-threshold-rows.py | sha256sum`; same for M2; `sha256sum` of the worktree file).
- Fixture: one scratch git repo per run, `corpus/SOURCES.md` copied from M2 (`71e9db2f93d83cf3c2919852a32522c4526e77d783bb95a8954f6f26b91f3e47`),
  forged `SKILL.md`; the counter is run read-only against each fixture commit. No lane file was touched.
- Upstream bodies re-fetched live; digests equal S593/S594/S595: `c3010a3c…6073` (llama 58830 B), `0b0ea669…1895` (ollama 16343 B),
  `e963af06…0694` (vllm 118996 B). Host curl 8.23.0, python 3.14.8, git 2.56.0.

## Commands and outputs (true exit codes)
- `python3 forge-driver.py --scratch <S> --sources <S>/SOURCES.md --counter <S>/counter.py` → exit 0; 23 variants; `forgeries.out`.
  Load at run: `uptime` 20:26:26 load 23.7; all cells are network fetches, no timing claim is made.
- `python3 .ufo/waves/round-91/controls/c2-forgeries.py --lane <lane> --scratch <S>/harness` → exit 0; `c2-forgeries-rerun.out`.
  Normalised (rev= stripped) comparison with committed `controls/c2-forgeries.out`: 44/44 lines identical, every variant exit 1.
- `python3 tools/round91-threshold-rows.py --repo . --rev 3f317ec…` → exit 0:
  `THRESHOLD_ROWS rows=14 bound=14 unbound=0 duplicates=0 engines=3 fetch_failures=0` (`c2-live-M2.out`; load 27.5).
- CRLF unit probe (imports the F bytes, monkeypatched `fetch`; no counter edit) → exit 0 (`crlf.out`):
  CRLF body with CRLF digest → `bound=True`; CRLF body with LF digest → `sha-mismatch`; LF body/LF digest → `bound=True`.
- HTML-block probe → exit 0 (`htmlblock.out`); 4/4 rows counted and bound.

## Findings
**F1 BLOCKER — the full predicate (exit 0) is reachable from one pinned file with zero real engine diversity.**
G22: 10 rows all citing S593 (one URL), 10 bound, seven honest lines plus three non-default lines (126 commented-out enum, 884 loop
condition, 435 PR-link comment), engine cells `llama.cpp`, `raw.githubusercontent.com`, `githubusercontent.com` — all substrings of the
same URL — each pin `b12177`. Output: `rows=10 bound=10 unbound=0 duplicates=0 engines=3 exit=0` (`forgeries.out` G22). B4 checks
`engine.split()[0].lower() in url.lower()` and `pin in url`, so a URL's own host/substring is a valid "engine"; `engines` is only the
first word of the cell and there is no distinct-source-URL requirement. K2 cannot catch this: K2 covers a row's threshold name, value
or probe decision, not its engine cell, and V4 never varies the label (it proves only that honest labels yield engines=1). Smallest
safe correction: derive the engine from the pinned URL (owner/repo path segment after the host) and require each engine's rows to cite
distinct SOURCES rows; require the pin to match a whole URL path segment (`/b12177/`, `/v0.40.11/`), not a substring.

**F2 DEFECT — six numeric lines that are not defaults bind (the disclosed K2 range, but the battery never tested it).**
All `bound=1 why=bound` (rows<10 so every variant exits 1): llama.cpp line 126 commented-out enum (`5`), line 884 loop condition
(`0`), line 435 PR-link comment (`15408`); Ollama line 21 host-string comment (`11434`, "Default" is the host), line 128 doc comment
for keepAlive (`5`); vLLM line 382 torch-version test (`2.10`). `forgeries.out` G1–G6. These are the claim's disclosed limit ("a row
that names a real parameter on a real numeric line binds whatever its prose says"; semantic fit is K2), but G1/G2/G4/G5 do not name a
parameter of the line at all — the backticked token is any text present there — so K2 is the only guard and no fixture in the committed
battery exercises it. Correction: require the name to be assigned/declared on the line (`\bNAME\s*(:?=)`), which rejects all six.

**F3 DEFECT — pin identity is substring-only.** G10 `llama.cpp b1217` (prefix of b12177) binds; G11 `llama.cpp 1` binds (the digit
`1` occurs in the URL). The row's declared pin can be truncated to a prefix or a single digit and still bind (`forgeries.out`
G10/G11). Correction: whole-segment pin match against the URL path.

**F4 DEFECT — B7's gloss ("names the parameter, flag or constant the line sets") is not enforced.** G7 backticks `int32_t` (the type)
and G8 backticks `9931` (the value itself); both bind because the code accepts any backticked token of ≥3 chars occurring in the
literal. The code matches B7's operative sentence, but only K2's human read covers the misstatement.

**F5 DEFECT — duplicate `S###` rows are silently first-wins.** `sources()` uses `setdefault`; a duplicate S593 decoy prepended with
tier `C` shadows the real tier-A row, and every legitimate row citing S593 then reads `source-status=mined/tier=C` → unbound
(`forgeries.out` G21: `bound=0`, false RED). No duplicate-source counter exists, unlike row ids. A false green needs an
attacker-hosted URL whose self-declared digest and literal satisfy B4–B6; not demonstrated, but the authority duplication is real.
Correction: reject/flag duplicate S-ids.

**F6 NOTE — two URLs in a source cell: only the first is examined.** G14 (pinned URL then `master` URL) binds and the master URL is never
checked; G15 (master first) is rejected `moving-ref`. `forgeries.out` G14/G15.

**F7 NOTE — fragment and query string bind.** `…#L632` and `…?x=1` both fetch the same bytes, digest matches, `bound=1`
(`forgeries.out` G12/G13). Byte identity makes this harmless; B5 checks content, not URL spelling.

**F8 NOTE — a literal containing `|` cannot be expressed.** G16 splits to `cells=9` and is unbound. Safe direction (never a false green),
but a real upstream line containing `|` (llama-common.h has many `||`) cannot be cited as a literal. Correction: split on unescaped
pipes outside backticks.

**F9 NOTE — population overreach for raw HTML blocks.** Rows at column 0 inside `<div>`, inside `<details>` with no blank line, and after
`<details><summary>x</summary>` are counted and bound (`htmlblock.out` H1–H4). GFM does not parse Markdown inside a raw HTML block, so
these are not "rendered rows"; the counter only excludes HTML comments and fences. G17's blank-line-separated `<details>` is correctly
rendered.

**F10 NOTE — a fenced `## ` does not end the section** (correct per rendering): T90 inside the fence is invisible, T91 after the closing
fence is counted and bound, T92 after the real `## Next` is not (`forgeries.out` G18). A forger can therefore keep appending rows after a
fenced fake heading, but those rows must still bind.

**F11 NOTE — leading spaces 1–3 and blockquote rows are not counted** (`forgeries.out` G19, rows=1). This matches the frozen "column 0"
wording, though the docstring says "rendered".

**F12 NOTE — CRLF is byte-exact, not a false green.** With a CRLF body the counter binds iff the SOURCES digest is the CRLF digest;
an LF digest yields `sha-mismatch` (`crlf.out`). Line addressing still works (line 632 holds the literal in the CRLF body).

**F13 NOTE — network dependency is availability-only.** Three live GETs, no retry. A 404 gives `fetch_failures=1`, exit 1
(`forgeries.out` G20): a false RED, never a false green; the live M2 run now gives `fetch_failures=0`. A transient failure during
grading therefore reads as a claim failure and must be re-run (the frozen `fetch_failures=0` is load/availability-sensitive).

**F14 NOTE — the n>=10 / e>=3 thresholds are not breadth conditions.** V4 already passes n with 10 bound rows from one engine (two curl
files) and fails only on e; e is label-only and defeatable (F1). Against the committed V4 receipt the thresholds are meaningful only as
"10 rows + 3 honest labels", not as "three engines of depth". F1 is the counterexample.

## Deliverables (in `.ufo/waves/round-91/w1/out/CR02ThresholdCounter/`)
`forgeries.out` (23 variants, counter stdout+exit), `forge-driver.py` (candidate, exact fixture bytes/lines),
`crlf.out`, `htmlblock.out`, `c2-forgeries-rerun.out`+`.err`, `c2-live-M2.out`.
Counter-under-test hash only; no tracked lane file was modified.
Scratch (`/fast/scratch/hyaku/kama-r91/CR02ThresholdCounter/`) was removed at 20:28; a foreign process then recreated that path with
`common.h`, `config.go`, `envs.py`, `load.txt` (not this seat's files), which I left untouched rather than delete a live peer's data.

VERDICT: partial — measured C2 reproduces live (14/14, engines=3, bytes identical at F/M2, fetch_failures=0), but the counter's engine and pin identity are substring-satisfiable and G22 reaches the full frozen predicate (exit 0) from a single pinned file with zero real engine diversity.
