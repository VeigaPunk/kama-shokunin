# RevBoolean — round-24 bounded static review: promisor classification, booleans, quoted config values, filter-only remotes

Lane: `KamaR23-2.RevBoolean-2` (reviewer, leaf member, no dispatch).
Base reviewed: `0df800e896f6bce285a81e794ad4ae1d1e6c3a71` (`tools/report-landing-audit.py`, `tests/report-audit/repo-state-grid.py`).
Preregistration: `.ufo/waves/round-24/preregistration.json`.
Host git: `git version 2.56.0` (x86_64, Arch). Upstream sources fetched from `https://raw.githubusercontent.com/git/git/v2.56.0/` (official git mirror; digests in `out/RevBoolean/upstream/`).

## Verdict

**The base classification cannot satisfy round-24 as written, and the repair must replace it rather than extend it.** Two independent reasons:

1. `tools/report-landing-audit.py:462-465` refuses *every* promisor-marked repository outright. That is the r23 harm the round-24 preregistration names (`preregistration.json` `expected_before`). A complete, locally-present promisor-marked clone must produce the same substantive verdict as an identical full clone, not exit 2.
2. The boolean/config reading itself (`tools/report-landing-audit.py:482-486`, `git_bool`) diverges from git's own parser on 10 of 35 spellings, cannot distinguish git's NULL value from an empty value, coerces an unreadable boolean to "false", and misses two whole promisor-marking mechanisms (`remote.<name>.partialclonefilter` alone; the `core.repositoryformatversion` gate on `extensions.partialclone`).

Recommendation: adopt a **git-faithful classification** (`promisor_backed(repo)`) and let *content* decide the verdict. A candidate fragment implementing exactly that is attached (`out/RevBoolean/candidate-classification-fragment.patch`, applies cleanly with `git apply --check`, and agrees with git's own behaviour on 13/13 decidable classification cases — the 2 remaining rows are the deliberately conservative "unreadable boolean ⇒ treat as promisor-backed" choice, see AP-4).

**This verdict is a recommendation. I did not edit, judge, integrate or ship anything; no production file was modified.**

## Method (all local, offline, synthetic)

* Read base files: `tools/report-landing-audit.py` (esp. 438-486 `check_history_repo`/`git_bool`, 139-181 `lookup`), `tests/report-audit/repo-state-grid.py` (195-212 `f_promisor_pack`, 272-290 `f_lazy_fetch`, 482-499 `f_filter_promisor`, 539-552 `c_promisor_false`/`c_orphan_marker`, 596-604 `t_blobless`, 640-712 row table + `REASONS`).
* Ground truth for *git's* promisor semantics: upstream v2.56.0 sources (digests under `out/RevBoolean/upstream/`), plus a **behavioural** probe on a real synthetic partial clone.
* Behavioural probe (offline, `file://` local transport only, `GIT_NO_LAZY_FETCH=1`, no transport ever invoked): in a promisor-backed repository git tries to lazy-fetch a missing object; with lazy fetch suppressed git prints `warning: lazy fetching disabled; some objects may not be available` + `fatal: could not fetch <oid> from promisor remote` (`promisor-remote.c` `fetch_objects`, `promisor_remote_get_direct`). That warning is a clean discriminator of "git considers this repository promisor-backed".
* Probes, fixtures and result tables: `out/RevBoolean/probes/*.py`, `out/RevBoolean/*.tsv`.

## Git's own rules (ground truth, with citations)

| # | Rule | Upstream evidence | Empirical evidence |
|---|---|---|---|
| R1 | `remote.<name>.promisor` is read with `git_config_bool`; a false value registers nothing | `promisor-remote.c:134-146` (`promisor_remote_config`) | matrix rows `promisor = false/no/off/0/00` → not promisor-backed |
| R2 | a *bare* key (`promisor`, no `=`) is git's NULL value → **true** | `config.h` "If the variable had no value specified, the value will be NULL (typically this means it should be interpreted as boolean true)"; `parse.c:git_parse_maybe_bool_text` (`if (!value) return 1`) | matrix row `promisor (valueless key)` → promisor-backed |
| R3 | an **empty value** (`promisor =`) is **false** | `parse.c:git_parse_maybe_bool_text` (`if (!*value) return 0`) | matrix row `promisor = (empty value)` → not promisor-backed |
| R4 | `true/yes/on` and `false/no/off` are case-insensitive; anything else that is not an integer is **invalid** and git *dies* (`bad boolean config value`) | `parse.c:git_parse_maybe_bool_text`; `config.c:1304-1310` (`git_config_bool` → `die`) | `boolean-spellings.tsv`: `' true '`, `'true '`, `' true'`, `'1abc'`, `'abc'`, `'maybe'`, `'08'`, `'9999999999999999999999'` → rc=128 fatal |
| R5 | integers use `strtoimax(..., base 0)`: `0x1`/`0X1` → true, `+1` → true, `010` → 8 → true, `00` → 0 → false, out-of-range → invalid | `parse.c:git_parse_signed` (line 18-48), `git_parse_maybe_bool` | `boolean-spellings.tsv` |
| R6 | `remote.<name>.partialclonefilter` **alone** (no `promisor` key) registers a promisor remote → the repository is promisor-backed | `promisor-remote.c:148-163` (filter branch calls `promisor_remote_new`) | matrix rows `filter only` and `filter + promisor=false` → promisor-backed; the r23 grid already asserts this (`repo-state-grid.py:482-499`, F27: "filter-only promisor did not lazy fetch") |
| R7 | `extensions.partialclone` registers a promisor remote **only when `core.repositoryformatversion` is present**; git discards the whole format block when that key is absent | `setup.c:read_repository_format` (`if (format->version == -1) clear_repository_format(format)`), `setup.c:612-632` (`handle_extension_v0`), `promisor-remote.c:180-190` (`promisor_remote_init`) | matrix rows `extension only, no formatversion` → not promisor-backed; `extension + formatversion 1` → promisor-backed |
| R8 | a **multi-valued** key: *any* true value wins (git processes every value) | `promisor-remote.c:128-146` (callback runs per value) | matrix row `promisor = true` then `promisor = false` → promisor-backed, while `git config --bool --get` returns `false` |
| R9 | `git config --null --list` prints `key\nvalue\0` for a valued key and `key\0` for a bare key — the NULL/empty distinction **is** available at byte level | verified byte-wise | `od -c` output in `out/RevBoolean/config-classification.tsv` probe; see AP-2 |
| R10 | the config scopes git uses are exactly what `--null --list` reports: repo-local, worktree config (`config.worktree` under `extensions.worktreeConfig`), and `include.path` files | verified | scope probe: `--null --list` reported `remote.wt.promisor` (worktree) and `remote.frominclude.promisor` (include) |
| R11 | git 2.56 writes a partial clone as `remote.origin.promisor = true` + `remote.origin.partialclonefilter = blob:none`; it does **not** write `extensions.partialclone` | observed in the git-generated clone config | `out/RevBoolean/promisor-classification-matrix.tsv`, case `git-generated partial clone` |
| R12 | `git cat-file --batch-check` (the audit's lookup path) never triggers the promisor machinery and never dies on an unreadable boolean | probe: invalid `promisor = maybe` → `cat-file --batch-check` prints `missing`, rc=0 | ⇒ the audit must classify from config itself; it cannot ask git |

## Findings (severity ordered; path:line + command evidence)

**F1 — critical — filter-only remotes are not classified as promisor-backed.**
`tools/report-landing-audit.py:462-464` matches only `extensions.partialclone` and `remote\..+\.promisor`. `remote.<name>.partialclonefilter` is never read. Under git's rules (R6) such a repository *is* promisor-backed, so a missing citation there is **unknown**, not proved absent. If the repair keeps this gap, a filter-only repository yields `unresolved-full-hash` / `landed-unresolved` (exit 1, "proved absent") for an object git could still fetch — precisely the verdict class the preregistration forbids (`expected_after[4]`). It also re-opens the transport channel the r23 grid closed: F27 (`repo-state-grid.py:482-499`) proves that a filter-only remote makes git run `core.sshCommand` on a missing-object lookup.
Evidence: `promisor-classification-matrix.tsv` (rows `partialclonefilter only (no promisor key)` and `partialclonefilter + promisor = false` → `git_promisor_backed=True`).

**F2 — critical — the blanket refusal at `:462-465` is the r23 harm itself.**
`check_history_repo` raises `EvalError(f"{repo}: partial clone ({key})")` for any promisor-marked repository, so a *complete* local promisor-marked clone exits 2 (`preregistration.json` `expected_before`, `expected_after[0]`, `expected_after[1]`). Metadata must decide only whether *absence* is evidence; content completeness decides the outcome (`expected_after[6]`).
Evidence: `tests/report-audit/repo-state-grid.py:596-604` `t_blobless` (a real blobless clone whose required commits/trees are all present) is currently a *non-graded* `tradeoff` row expecting exit 0 — i.e. r23 recorded the refusal as an accepted downside. Under round-24 this row must become graded and expect the clean verdict.

**F3 — major — `git_bool` cannot distinguish git's NULL value from an empty value, and gets the empty value wrong.**
`tools/report-landing-audit.py:482-486`: `v = value.strip().lower(); return v in ("", "true", ...)`. The parser at `:461` (`key, _, value = entry.partition("\n")`) collapses "bare key" and "empty value" to the same `""`, and `""` is then classified **true**. Git says: bare key → true (R2), empty value → **false** (R3). Consequence: `remote.origin.promisor =` (explicitly empty) is treated as promisor-marked → a repository git considers complete is refused → the same false-refusal class as F2.
Evidence: `boolean-spellings.tsv` row `''` → `git_config_bool=False`, `base_git_bool=True`; matrix row `promisor = (empty value)` → git: not promisor-backed.

**F4 — major — an unreadable boolean is coerced to "false", i.e. unknown becomes proved-absent.**
`git_bool` returns `False` for `'maybe'`, `'abc'`, `'1abc'`, `'08'`, `'true#comment'`, `"'true'"` (single quotes are *not* dequoted by git), and returns `True` for `' true '`, `'true '`, `'1 '` (git rejects all of these and dies). Git's own verdict for those values is "this repository is not usable as configured", never "the remote is not a promisor".
Evidence: `boolean-spellings.tsv` (git column = `rc=128 fatal: bad boolean config value …` for each). Consequence under round-24: a citation missing from such a repository would be reported as *proved absent* (exit 1) instead of *unknown* (exit 2), violating `expected_after[4]`.
Note: `git cat-file --batch-check` does **not** die on these values (R12), so the audit will not trip over them by accident — the classification must handle them deliberately.

**F5 — major — valid true spellings are coerced to "false".**
`0x1`, `0X1` and `+1` are true to git (R5) but `git_bool` returns `False` for them (its integer regex is `-?[0-9]+`). Consequence: a genuinely promisor-backed repository is classified as complete → absence treated as proved → false `unresolved-full-hash` verdicts.
Evidence: `boolean-spellings.tsv` rows `0x1`, `0X1`, `+1`.

**F6 — moderate — `extensions.partialclone` is honoured even when git discards it.**
`:462` treats the mere presence of the key as promisor-marked, but git discards the whole extension block when `core.repositoryformatversion` is absent (R7). A repository whose config lacks that key is **not** promisor-backed to git, so refusing it is a false refusal.
Evidence: matrix rows `extensions.partialclone = origin (remote has no promisor key)` → not promisor-backed (no `core.repositoryformatversion` in the fixture) vs. `core fmtv1 + extension` → promisor-backed.

**F7 — moderate — `git config --bool --get` is not a usable shortcut.**
It returns only the **last** value of a multi-valued key (R8), so `promisor = true` + `promisor = false` would classify as *not* promisor-backed while git classifies it as promisor-backed (matrix row `promisor = true, then promisor = false`). It also cannot express "absent" vs "invalid" (rc 1 vs rc 128) in one call, and it hides git's NULL value. Any implementation that uses it must combine it with a full enumeration of the key's values.
Evidence: `promisor-backed.tsv` (`--bool-get` column) vs. `promisor-classification-matrix.tsv` (git truth) for the multi-value rows.

**F8 — minor — `git_bool`'s `.strip()` accepts values git rejects** (`' true '`, `'true '`), overlapping F4; and the base integer path is unbounded (`int('9999999999999999999999')` → True while git reports ERANGE → invalid). Evidence: `boolean-spellings.tsv`.

**F9 — minor (documentation) — the base docstring is right about intent but not about the data.** `:483` says "a bare key (no '=') is true" — correct, but the value reaching `git_bool` cannot express "no '='", so the docstring promises a distinction the code has thrown away (see AP-2).

## Acceptance points (concrete; each is checkable without a network)

* **AP-1 — classification is git-faithful, not a re-implementation.** Either delegate the boolean to git (`git config --bool --get <key>` per value, or `git -c <key>=<value> config --bool --get <key>` for a single value) or implement `git_parse_maybe_bool_text` + `git_parse_int` exactly, including `NULL → true`, `"" → false`, case-insensitive words, `strtoimax` base 0, and an explicit *invalid* outcome. **An invalid value must have its own outcome; it must never be read as "false".**
* **AP-2 — the NULL/empty distinction is preserved.** The reader must distinguish a `key\0` entry (bare key → true) from a `key\n\0` entry (empty value → false). `entry.partition("\n")` (`:461`) does not; the fix is to test whether the separator is present (R9).
* **AP-3 — all three promisor-marking mechanisms are honoured**: (a) `remote.<name>.promisor` true, (b) `remote.<name>.partialclonefilter` set (with or without (a)), (c) `extensions.partialclone` **and** `core.repositoryformatversion` present. (R1, R6, R7)
* **AP-4 — unknown is never absence.** For a promisor-backed repository, a required object that is not present locally ⇒ exit 2 (could-not-evaluate), never a `missing`/`unresolved` verdict; and a citation missing from *any* promisor-backed repository is unknown unless it resolves in the other audited repository (`preregistration.json` `expected_after[3..4]`). An unreadable boolean must not downgrade the repository to "complete": treat it as promisor-backed (conservative) or refuse the repository — but never as "not promisor".
* **AP-5 — metadata alone never decides the outcome.** A promisor-marked repository whose required commits/trees/blobs/reports are all present locally must return the same substantive clean/failed findings as an identical non-promisor clone (`expected_after[0..1]`, `expected_after[6]`). The refusal reason for the exit-2 cases must be the *content* reason ("required evidence unavailable"), not "partial clone".
* **AP-6 — no transport, no repository program, no hang.** Classification must be read from config only; the audit must keep `GIT_ISOLATION` (`:93-96`: `--no-replace-objects --no-lazy-fetch`, `log.showSignature=false`, `log.follow=false`, `log.mailmap=false`), the `GIT_CONFIG_GLOBAL=/dev/null` + `GIT_CONFIG_NOSYSTEM=1` neutralization (`:99-105`) and `GIT_TIMEOUT = 20` (`:108`). `git config --null --list` respects `include.path`, so an include pointing at a FIFO must still time out rather than hang (r23 row F30).
* **AP-7 — the equivalence test is part of the deliverable.** The new harness (`tests/report-audit/promisor-grid.py`, named in `preregistration.json` `measurement`; it does **not** exist at base) must contain the classification matrix as expectations, i.e. rows for: `promisor=true/TRUE/True/yes/on/1/0x1/+1/-1/010/00`, `false/FALSE/no/off/0/-0`, empty value, bare key, `"true"`, `'true'`, `" true "`, `maybe`, `1abc`, `08`, filter-only, filter+`promisor=false`, `extensions.partialclone` with and without `core.repositoryformatversion`, and multi-valued `true`+`false`. My measured expectations are in `out/RevBoolean/promisor-classification-matrix.tsv` and `out/RevBoolean/boolean-spellings.tsv`.
* **AP-8 — the no-harm rows must keep their verdicts.** `C09-promisor-false-config` (exit 0), `C10-orphan-promisor-marker` (exit 0), `C11`, `C12`, `C13` and every non-promisor row of `repo-state-grid.py` must not change. `C09` in particular is the `promisor = false` control and must stay exit 0 under the new classification.

## Impact on the r23 grid (`tests/report-audit/repo-state-grid.py`)

| Row | r23 expectation | round-24 requirement |
|---|---|---|
| `T01-blobless-partial-clone` (`t_blobless`, :596) | `tradeoff`, exit 0, **not graded** | must become graded; the clone's required objects are present ⇒ same clean verdict as a full clone (`expected_after[0]`). The refusal must be gone. |
| `F06-lazy-fetch-command` (`f_lazy_fetch`, :272) | fault, exit 2, reason pinned to `"partial clone"` | exit stays 2, but the pinned reason must change to the content reason (missing required evidence in a promisor-backed repository); the `core.sshCommand` marker must still not be created. |
| `F23-promisor-pack-without-config` (`f_promisor_pack`, :195) | contract, exit 2, reason `"promisor pack"` | exit stays 2; reason must become the content reason (the cited blob is absent while the repository is promisor-backed). The `.promisor` pack alone remains a promisor marker. |
| `F27-filter-only-promisor-remote` (`f_filter_promisor`, :482) | fault, exit 1, kinds `[landed-unresolved, unresolved-full-hash]` | the filter-only repository must be classified promisor-backed ⇒ the fabricated citation becomes *unknown* ⇒ exit 2, no verdict kinds, and the marker must not be created (no lazy fetch). This is AP-1/AP-3 made observable. |
| `C09-promisor-false-config` (`c_promisor_false`, :539) | control, exit 0 | unchanged (AP-8). |
| `C10-orphan-promisor-marker` (`c_orphan_marker`, :545) | control, exit 0 | unchanged: an orphan `.promisor` file without its `.pack` is not a promisor marker (`:454-455` requires the sibling `.pack`). |

## Candidate fragment (not applied)

`out/RevBoolean/candidate-classification-fragment.patch` — adds `config_entries()`, `git_bool_value()` (True/False/None) and `promisor_backed()` to `tools/report-landing-audit.py`, and removes the wholesale refusal at `:460-465`.

* `git apply --check -p1` against the base tree: **rc 0**.
* Self-check against git's own behaviour on the synthetic partial clone: **13/13 decidable cases agree**; the two invalid-boolean rows are the deliberate conservative choice "unreadable ⇒ promisor-backed" (`out/RevBoolean/candidate-selfcheck.tsv`).
* It deliberately does **not** decide the policy for a missing required object in a promisor-backed repository — that is the integrator's call under `expected_after[2..4]`. It does not touch `GIT_ISOLATION`, the timeouts, or anything else.

## Residual risk and verification gaps

* **Unrun = unverified.** I did not run `tools/report-landing-audit.py` on any fixture, did not run `tests/report-audit/repo-state-grid.py`, and did not run any full-suite check (lane contract: L1 runs once after integration). Every claim above about *the audit's* behaviour is derived from reading the base source plus git's own behaviour; no end-to-end audit exit code was observed.
* The r24 implementation does not exist at base; the findings are therefore against the base classification, not against a candidate diff. When L1's candidate lands, AP-1…AP-8 must be re-checked against the actual diff (the classification rules above are the check list).
* `tests/report-audit/promisor-grid.py` (named in `preregistration.json` `measurement`) does not exist at base; AP-7 states what it must contain.
* Scope gaps I did not cover (other lanes' scope): the completeness/availability policy for missing commits/trees/blobs/reports, the "resolved locally by another audited repository" rule, the exit-2 reason vocabulary, and the r23 evidence corrections in `expected_after[7]`.
* Environment caveat for the ground truth: git 2.56.0 is the host's git. The `extensions.partialclone` writer was removed from modern git (R11), so a repository marked only by that extension is legacy-shaped; the classification still honours it when `core.repositoryformatversion` is present (R7). Behaviour of older git (2.45, the documented minimum) was not measured here — `unverified`.
* I did not measure `git config --bool` behaviour on a repository with `extensions.worktreeConfig` and a worktree-config boolean beyond the scope probe (the worktree value was visible in `--null --list`); the byte-level NULL/empty distinction inside `config.worktree` is `unverified`.

## Named files

Production (read only, unmodified):
* `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/report-landing-audit.py` (base 0df800e)
* `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/report-audit/repo-state-grid.py` (base 0df800e)
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/preregistration.json`

Artifacts written by this lane:
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/build/advice/RevBoolean.md` (this file)
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/build/out/RevBoolean/candidate-classification-fragment.patch`
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/build/out/RevBoolean/candidate-selfcheck.tsv`
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/build/out/RevBoolean/promisor-classification-matrix.tsv`
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/build/out/RevBoolean/boolean-spellings.tsv`
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/build/out/RevBoolean/config-classification.tsv`
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/build/out/RevBoolean/promisor-backed.tsv`
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/build/out/RevBoolean/config-scope-probe.txt` (config scopes seen by `git config --null --list`)
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/build/out/RevBoolean/candidate/tools/report-landing-audit.py` (the candidate file the patch produces, for review without applying)
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/build/out/RevBoolean/probes/*.py` (eight offline probes; each is re-runnable in a scratch tree)
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/build/out/RevBoolean/upstream/` (git v2.56.0 sources used as ground truth; sha256 in the file list below)

Upstream digests (git v2.56.0, `raw.githubusercontent.com/git/git/v2.56.0/`):
`parse.c` 4eb73ad2301f5fadb4b1f40ccb7cfa2bcd443dc44f9494204080c74f8c0f6f7f ·
`odb.c` 72c674c043c5e6abab0ea03c7848f8adabc4ba297136d46d67a8fad4b5e1dc97 ·
`setup.c` 8316b1ad961ac6b1fa29dfdf1094a344aec8673f6637e6c00ba913a6668fc589 ·
`config.c` eb3fa62bc57b07d9cbc5622d5d7c8fe04cc4efa96bd9d5abdcce1dcd7db3cb26 ·
`promisor-remote.h` a3fc663da2150da0b903af4a6f9c0b58bbda64275d94b8e294f3713d99b07a82 ·
`promisor-remote.c` 175e67e1b2cc62db1ead26007ba1e5502f9b585fd33dbc45b59f9876b34f9bca (fetched by `KamaR23-2.SrcPromisorCode-2`, reused here).

Tools installed/updated by this lane: none (no `pacman`, `uv`, `cargo` or `npm` transaction was needed; `git 2.56.0` and `python3` were already present).
