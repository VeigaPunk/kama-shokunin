VERDICT: refute — the receipt gate can echo an untrusted environment-value string into captured diagnostics; no actual host credential was observed

## Axes
Privacy/data minimization; provenance and output-root placement; oversized-artifact exposure.

## Scope and method
Audited the delivered round-18 range `e75cf680b53484a61709ee1b2787d8dbc6419f74..1c325b2e58fcfdc6761f645b44cedfb1d65243e6`, the round-18 evidence tree, relevant environment/receipt validation code, and the required lesson/scorecard/quality criteria. The full diff lists 275 paths; the changed production surfaces include `tools/kama-llamacpp-live.py`, `tools/sources-append-only.py`, `tests/llamacpp-live/{check-receipt,controls}.py`, and `tests/probe-verdicts/{check,fault-controls}.py`.

Only local reads, path listing, `find`, and SHA-256 inspection were used. No environment dump, tests, runtime/gate run, listener, installation, or scratch clone. No forbidden session/history/transcript store or `~/.config` was opened. Official `runs/commands.json` says measured commit `c6dc46fabc51eb1dd0e91647f2e5e6b2b8ae4d6d`; no runtime claim is made for target `1c325...`.

## Findings

### Low — malformed `child_env_keys` values are echoed into gate output

- **Exploit path:** A receipt supplied to the gate has `child_env_keys` containing a string like `NAME=<sensitive-value>`. The validator detects `=` but formats the entire element with `!r`; the gate prints every problem, and the controls collector stores stdout problem lines (plus an unredacted stderr tail). If a faulty or untrusted receipt contains a real environment value, validation amplifies it into logs/measurement output.
- **Evidence:** `tests/llamacpp-live/check-receipt.py:446-457` rejects `=` but interpolates `k!r`; `:2101-2103` prints the problem text. `tests/llamacpp-live/controls.py:908-920` retains normalized stdout problem lines and raw stderr tail. Current producer source instead allowlists environment keys and records names only: `tools/kama-llamacpp-live.py:82-84,1256-1258`; the measured receipt has only `HOME`, `LANG`, `PATH` at `.ufo/waves/round-18/live/receipt-1.json:231-234`.
- **Impact / limit:** Conditional leak through diagnostics; the current producer and receipt do not show an environment value, and the existing off-allowlist control uses a name only. This is a code-derived path, not an executed reproduction.
- **Smallest remediation:** For invalid entries, emit a constant message (e.g. “child_env_keys entries must be bare allowlisted names”) without interpolating the element. Add a regression assertion that a synthetic value after `=` is absent from gate output and collected results.
- **Hashes:** `check-receipt.py` SHA-256 `c5715641f34fb9bffaf33ca3e0391dd5485a0a914462bf6540e519b566c78335`; `controls.py` SHA-256 `106dd98b60e066a190ee8fea609e5be99c6b2065b9c5a404e14394ce59b6ffc8`; producer SHA-256 `dc036d7dcfe2933827c07f8bc0dedba68a24f7b099309871f6cb25ccb811a04b`.

### Low — retained evidence exposes the local home-directory layout

- **Exploit path:** Anyone receiving the committed/live receipt or raw command manifest can infer the local account name and locations of the llama-server installation and model cache from absolute paths.
- **Evidence:** `.ufo/waves/round-18/live/receipt-1.json:3-6` records server argv and model path; `.ufo/waves/round-18/runs/commands.json:7-12` records absolute argv and working directory. The receipt SHA-256 is `e616f67e2e2bec196402f56ed3a45fb68f78c9f4e927f0ea7d8acd170caf6d75`; command-manifest SHA-256 is `ce7dc79c9523b92c33e0cbb141299db6196b2aa64b3c307779eee1842b51b84a`.
- **Impact / limit:** Host-path/user-name disclosure, not a credential disclosure. These paths are intentionally useful for reproducibility; no other host account or private file contents were read.
- **Smallest remediation:** Before distributing artifacts outside the trusted lane, redact the `$HOME` prefix or publish normalized paths while retaining hashes. Keep the unredacted originals access-controlled if exact path provenance is required.

### Informational — analysis notes retain synthetic credential-shaped test values

- **Exploit path:** Search-indexing or copying the experiment notes can propagate values used in local authentication tests as though they were credentials.
- **Evidence:** `.ufo/waves/round-18/build/advice/ProbeArgvEffects.md:36-45` records a dummy API-key/Bearer test; `ScoutLlamaArgParse.md:17,64-73` records dummy environment/config/CLI values. SHA-256: `ProbeArgvEffects.md` `4caff953f775b970996071ed2d9e33621e514a7a7c133bdf1f3a6f15b971e089`; `ScoutLlamaArgParse.md` `7def82af6da6a1e6a0eaeed1afa17e27fbb7fdb07b788d6723fa2d037b622803`.
- **Impact / limit:** The inspected text identifies these as temporary/local test inputs; I found no evidence they are live credentials. They are not evidence of an environment dump.
- **Smallest remediation:** Use an explicit non-secret fixture marker in retained prose/output, or redact the values while preserving the test conclusion.

## Clean checks / boundaries

- **Environment values:** The producer records only allowlisted variable names (`tools/kama-llamacpp-live.py:82-84,1256-1258`); `receipt-1.json:231-234` confirms names only. The command manifest stores argv, cwd, exit and stream digests, not an environment map. The noted test strings above are the only credential-shaped values I found in the reviewed experiment notes; none was identified as a real secret.
- **Session excerpts:** `.ufo/waves/round-18/falsify/record.stdout:1-13` is a swarm-registry JSON record (`path` and `reportDir` point to this round’s `falsify/advice` directory, followed by member IDs/roles), not a session transcript. Its SHA-256 is `44184bab90257816c07c14b413082567003484023c9543bb02b6c853978753f9`. I did not open any session/history/transcript store.
- **Output-root placement:** The FALSIFY registry points to `.ufo/waves/round-18/falsify/advice` (`record.stdout:2,7`). `runs/commands.json` unique `cwd` values were the kama checkout and one `/tmp` lane clone. `falsify/validation.json:5-7` names a parent-level `scripts/hyaku` policy as an input, not an output/report destination. No fleet-root report misroot was observed. Validation JSON SHA-256: `5644346ed0d9b543e1934b4ee32cf7c287bd12d0aed67594bf1201f9e4cbcf5c`.
- **Oversized/new artifacts:** `find /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18 -type f -size +10M -print | wc -l` → `0`; symlink count via `find ... -type l -print | wc -l` → `0`. Thus no regular file over 10 MiB and no symlink target was omitted from the size check.
- **Installs / execution:** None. No tests, builds, runtime/gate checks, or ports were used. The conditional diagnostic issue remains unverified by execution.

Report: .ufo/waves/round-18/falsify/advice/PrivacyScope.md