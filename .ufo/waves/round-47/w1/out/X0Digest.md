# X0Digest — round 47, lane kama: the new digests and object ids

**Verdict:** the ledger delta the round needs is small and now measured: **2 digest rows + 1 hexrun row + 2 evidence files** (`proposed-ledgers.patch`, applies cleanly to the build tip) take `digest-ledger.py` on the rows that are actually in the lane worktree (S488–S491) from `unknown=5 exit 1` to `unknown=0 exit 0` once the artifacts those rows cite are committed (`unknown=3` if they are not), and close the round's one new 40-hex run `caa8191d…` as `upstream_ok`; everything else the round cites is the SHA-256 of a tracked file (class `blob`), already ledgered, or a lane object. The 22 unknown hex runs that already sit at the build tip are untouched and still hold the census at exit 1.

## 1. What the round introduces, and how each run classifies

Two sets: the values the item names, and the values the *in-flight* S488–S491 rows cite (a sibling seat added those rows to `corpus/SOURCES.md` in the lane worktree while this seat ran — worktree sha256 `61ab68d5…`, snapshot 2026-10-26T21:36:28Z). Classes below are measured, not asserted; "before" = the rows in the tree with the build-tip ledgers, "after" = plus the patch.

| run | length | cited by | before | after | why |
|---|---|---|---|---|---|
| `bf94332a3001f3ee0b032cda37259f68460e28732ef9a579bfb1b918197e695b` b11909 asset tar.gz | 64 | S488, S489 | unknown | **unverifiable** (new row) | the 22475032-byte archive is not retained on this host, so nothing committed can re-hash it |
| `35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0` b11909 `llama-server` | 64 | S488, S489 | unknown | **external** (new row, `/home/vgpnk/.local/opt/llama-b11909/llama-server`) | sha256sum of the installed file matches; the transient archive's member hashes to the same value |
| `caa8191df159f764fb0160e3d2fc6be008948aee` b11909 tag commit | 40 | S488, S489 `build_info` | unknown | **upstream_ok** (new hexrun row + evidence file) | `ls-remote` one line (lightweight tag), `cat-file -t` → commit, release JSON `target_commitish` |
| `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d` stories260K.gguf | 64 | S488–S490 | external_ok | external_ok | **already known** — `external` row since round 42 (`/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf`); re-hashed here, matches; no new row |
| `6ad897dd84e64dcf6aff9997dc19d2e835b7a90adc37da12bb0e00b310db46d2` `c2/release-b11909.json` | 64 | S488 | blob | blob | tracked file at REV; its content digest is in the blob set |
| `e41c4b75188b7b710843fc450c5ad84463a035670d481e982cebf78729c3b63c` `S1Rows/release-b11909.gh.json` | 64 | S488 | unknown | blob **if that artifact is committed** | `sha256sum .ufo/waves/round-47/w1/out/S1Rows/release-b11909.gh.json` = `e41c4b75…`; unknown while it is only on disk |
| `5ae80d1deee5dc2c1acafff5491c5ba019629b9a785e6781a3e8a411cf9e22ed`, `a486a5f8aa7c75fa7f114547af55a976baf026e5e387f287127e6c6656e2b078` git-diff pages | 64 | S491 | unknown | blob **if `S1Numstat/*.html` are committed** | `sha256sum .ufo/waves/round-47/w1/out/S1Numstat/git-diff.html` / `diff-format.html` match |
| `65301a3c…` tool, `36b64978…` probe, `a4caf311…`/`d36d2941…`/`f3f96151…` receipts, `80eb0e58…` install.txt | 64 | S488, S489 | blob | blob | tracked files at REV — no rows |
| `b8f0f203f3c593225710bc2075b404944037b172c021e0136791dbff6f9043c2` b11909 `libllama-server-impl.so` | 64 | **only this seat's alternative S488** | — | external (optional row) | the in-flight rows do not cite the library digest, so this row is unused unless the wording that cites it wins (`proposed-digest-ledger-row-libimpl-optional.tsv`) |
| `bbcc6dc2fbd7fc04b1d91a97ffa239a6601cd5ba` freeze, `3a09a1d93dcc16799cf6c4b48786e6440af134c4` build | 40 | round-47 prose | lane_oid | lane_oid | ancestors of lane HEAD, `git cat-file -t` = commit; no row needed |

## 2. Measurements (exact commands, outputs, exit codes)

Scratch clone `git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane`. Fixtures: `D=$(mktemp -d -p $S/fix) && git -C "$D" init -q`, then `git -C "$D" fetch $S/lane refs/heads/master:refs/fixture/lane`, `git -C "$D" checkout -b <b> 3a09a1d93dcc…`; `git -C "$D" rev-parse --show-toplevel` = `$D` asserted before the first commit; every commit carries `user.name=X0Digest fixture`. Fetching lane history into the fixture is what makes `lane_oid` resolve as it will in the lane.

**Baseline — identical in the lane clone and the fixture** (`scan-baseline.txt`, `hexrun-baseline.txt`):

```
$ python3 tools/digest-ledger.py scan --repo <clone|fixture> --rev 3a09a1d93dcc… --details
tokens=111 blob=97 external_ok=7 external_absent=1 unverifiable=5 wrong_flagged=1 ledger_bad=0 wrong_unflagged=0 unknown=0   exit=0
  detail: wrong_flagged 5585f602… class=wrong      detail: external_absent bcc55c92… class=external
$ python3 tools/hexrun-census.py scan --repo <clone|fixture> --rev 3a09a1d93dcc…
tokens=1772 distinct=280 lane_oid=178 md5_blob=1 upstream_ok=68 unverifiable=9 wrong_flagged=2 ledger_bad=0 unknown=22   exit=1
```

The same two lines hold at the wave-spec tip `46a924e027f05614558c45ff02bf7a94ca57d3e1`. Selftests: `digest-ledger.py selftest` → `pass=10 fail=0 exit=0`; `hexrun-census.py selftest` → `pass=18 fail=0 exit=0`.

**The in-flight rows on the build-tip ledgers — the true "before"** (fixture `2cef0e66d16d157f45deac5981479c3051db35f3`: snapshot docs, build-tip ledgers, no evidence, no artifacts; `scan-inflight-before-rows.txt`):

```
$ python3 tools/digest-ledger.py scan --repo <fixture> --rev <that> --details
tokens=121 blob=102 external_ok=7 external_absent=1 unverifiable=5 wrong_flagged=1 ledger_bad=0 wrong_unflagged=0 unknown=5   exit=1
  detail: unknown 35ac50fb…   detail: unknown bf94332a…   detail: unknown e41c4b75…   detail: unknown 5ae80d1d…   detail: unknown a486a5f8…
$ python3 tools/hexrun-census.py scan --repo <fixture> --rev <that>
tokens=1776 distinct=282 lane_oid=179 md5_blob=1 upstream_ok=68 unverifiable=9 wrong_flagged=2 ledger_bad=0 unknown=23   exit=1
  (the 23rd is caa8191d…)
```

Five digest runs and one hex run are unprecedented by the tree as it stands; the patch supplies two of the five digest runs (`35ac50fb…`, `bf94332a…`) and the hex run, and the other three (`e41c4b75…`, `5ae80d1d…`, `a486a5f8…`) are the hashes of artifacts the rows name, so they resolve the moment those artifacts are committed rather than by a ledger row.

**With the minimal patch, cited artifacts not committed** (fixture `202abcc8a38148e5aa068c61154dcb2347903411`, `scan-inflight-no-artifacts.txt`):

```
tokens=121 blob=102 external_ok=8 external_absent=1 unverifiable=6 wrong_flagged=1 unknown=3   exit=1
  detail: unknown 5ae80d1d… / a486a5f8… / e41c4b75…
```

**With the minimal patch and the cited artifacts committed** (fixture `0335e9d5f6c605b503b763693192ae0e513e99e5`, `scan-inflight-with-artifacts.txt`, `hexrun-inflight.txt`):

```
$ python3 tools/digest-ledger.py scan --repo <fixture> --rev <that> --details
tokens=121 blob=105 external_ok=8 external_absent=1 unverifiable=6 wrong_flagged=1 ledger_bad=0 wrong_unflagged=0 unknown=0   exit=0
$ python3 tools/hexrun-census.py scan --repo <fixture> --rev <that>
tokens=1776 distinct=282 lane_oid=179 md5_blob=1 upstream_ok=69 unverifiable=9 wrong_flagged=2 ledger_bad=0 unknown=22   exit=1
```

`blob` 102→105 is `e41c4b75…` + the two page digests; `upstream_ok` 68→69 is `caa8191d…`; `lane_oid` 178→179 is the build commit cited by the in-flight prose. The residual 22 unknowns are the build tip's own list, unchanged.

**Alternative wording (this seat's drafted S488/S489), for completeness** (`scan-docs-only.txt`, `scan-with-ledgers.txt`, `hexrun-docs-only.txt`, `hexrun-with-ledgers.txt`): with those rows in place and no ledger row, digest is `unknown=3` — `35ac50fb…`, `b8f0f203…`, `bf94332a…` — and hexrun `unknown=23` (`caa8191d…`); with the three digest rows and the hexrun row, digest is `unknown=0 exit 0` (`external_ok` 7→9, `unverifiable` 5→6) and hexrun `unknown=22` with `bbcc6dc2…`/`3a09a1d9…` classified `lane_oid` and `caa8191d…` `upstream_ok`. `6ad897dd…` (release JSON), `65301a3c…` (tool), `36b64978…` (probe), the three receipt digests and `80eb0e58…` (install record) all classified `blob` with no row — that is why the draft has three rows and not four.

**Upstream check for `caa8191d…`** (no `gh` call — shared API quota untouched):

```
$ git ls-remote --tags https://github.com/ggml-org/llama.cpp.git refs/tags/b11909 'refs/tags/b11909^{}'
caa8191df159f764fb0160e3d2fc6be008948aee	refs/tags/b11909          # one line ⇒ lightweight tag, no annotated object
$ git init -q <filtered clone> && git -C <clone> fetch --depth 1 --filter=blob:none --no-tags https://github.com/ggml-org/llama.cpp.git refs/tags/b11909
$ git -C <clone> cat-file -t caa8191df…   → commit
$ git -C <clone> log -1 --format='%H %ci %s' caa8191df…
caa8191df159f764fb0160e3d2fc6be008948aee 2026-10-26 08:21:14 -0700 hexagon: MUL_MAT_ID row skipping optimizations and improvements (#31169)
```

**Host re-hashes** (`.ufo/waves/round-47/c2/x0-digest-rehash.txt`): `llama-server` → `35ac50fb…`; `libllama-server-impl.so` → `b8f0f203…`; cache `stories260K.gguf` → `270cba…`; `c2/release-b11909.json` → `6ad897dd…` (68603 bytes); receipts → `a4caf311…`/`d36d2941…`/`f3f96151…`; `install.txt` → `80eb0e58…`; `tools/kama-llamacpp-live.py` → `65301a3c…`, `tools/kama-live-replay.py` → `39cd387a…`, `tools/kama-probe.sh` → `36b64978…`. The archive is **not retained** (`ls /home/vgpnk/.local/opt/*.tar.gz` lists only `llama-b11755-bin-ubuntu-x64.tar.gz`); a transient scratch copy hashed to `bf94332a…` and its members `llama-b11909/llama-server` and `llama-b11909/libllama-server-impl.so` to `35ac50fb…` and `b8f0f203…`, i.e. the installed binary and library are the asset's members. That copy is cited as no path and was deleted with the scratch.

## 3. The landable change

`proposed-ledgers.patch` (88 lines, `git apply --check` clean against a build-tip tree, and the lane worktree touches none of these paths):

- `registry/digest-ledger.tsv` +2: `35ac50fb…` `external` → `/home/vgpnk/.local/opt/llama-b11909/llama-server`; `bf94332a…` `unverifiable` with the `gh api …/releases/tags/b11909` re-verify recipe.
- `registry/hexrun-ledger.tsv` +1: `caa8191d…` `upstream`, repo `ggml-org/llama.cpp`, evidence `.ufo/waves/round-47/hexrun-evidence/caa8191df159f764fb0160e3d2fc6be008948aee.txt`.
- new `.ufo/waves/round-47/c2/x0-digest-rehash.txt` and `.ufo/waves/round-47/hexrun-evidence/caa8191df159f764fb0160e3d2fc6be008948aee.txt` (both currently untracked in the lane: `git status --porcelain` → `?? .ufo/waves/round-47/c2/x0-digest-rehash.txt`, `?? .ufo/waves/round-47/hexrun-evidence/`).

Companion files, not part of the patch: `proposed-digest-ledger-row-libimpl-optional.tsv` (only if the library digest gets cited), `proposed-sources-rows.md` (an alternative S488/S489 wording — **do not** apply alongside the in-flight rows; ids already taken), and the measurement logs.

## 4. Findings and risks

1. **The round cites the b11909 release record twice, with different bytes and different digests.** `S488` names `.ufo/waves/round-47/w1/out/S1Rows/release-b11909.gh.json` (68614 bytes, `e41c4b75…`), while `.ufo/waves/round-47/c2/release-b11909.json` is 68603 bytes, `6ad897dd…` — two fetches of the same endpoint 11 bytes apart. Both classify `blob` only while their files are committed; if the worktree keeps just one, the other digest is `unknown` and the census fails. Measured: `scan-inflight-no-artifacts.txt`. Fix: commit both artifacts, or drop the citation of the one that is not kept.
2. **`S491`'s page digests depend on committed page bytes.** `5ae80d1d…` and `a486a5f8…` are the hashes of `.ufo/waves/round-47/w1/out/S1Numstat/git-diff.html` and `diff-format.html` (verified by `sha256sum`); the same failure mode as (1) if those files are not committed. Measured: `unknown=3` without them, `0` with them.
3. **Land the rows, the evidence and the artifacts in one commit.** A hexrun `upstream` row whose `evidence` blob is absent at REV classifies `ledger_bad` (`tools/hexrun-census.py`, `Context.upstream_ok`); the same is true of every `blob` digest whose file is left behind. Committing S488–S491 without the artifacts above is strictly worse than committing neither, because it turns working rows into failures.
4. **The asset digest must stay `unverifiable`.** Nothing on this host retains 22475032 bytes of archive, and an `external` row pointed at seat scratch classifies `external_absent` as soon as the scratch is reaped — the dead-pointer class round-46 D5 closed.
5. **Pre-existing, not introduced here:** `hexrun-census.py` exits 1 at `3a09a1d9…` and at `46a924e0…` with `unknown=22`. The largest cited offenders are `b0fd7b7f5ae6a0ad7717461c5fea8cb8a8724025` (104 occurrences), `0a14a9620961ff627348952112b4a9a6a0513c43` (72), `6105c5870859f15ba5372ccbe3835d65b0d9d38b` (70), `80a9f2d7270d072967c9ad243864147cbd1e175e` (26) and `d854d98bae598388ecea1ed84396587e5edc326d` (19 — b11889's tag commit, cited by S482/S484/S486 and the round-45/46 prose, with no hexrun row: the ledger has rows for `4d71b42f…` (b11906) and `4b851fbe…` (b11907) and none for `d854d98b…`). This item's rows neither add to nor remove from that set; the frontier item in `preregistration.json:63` ("r46-D4") owns it.
6. **`b8f0f203…` is optional.** The in-flight rows do not cite the library digest, so the row in `proposed-digest-ledger-row-libimpl-optional.tsv` is unused unless a row that cites it lands. Nothing else in the draft is conditional.
7. **No `gh` call by this seat** (shared quota): the release metadata is read from the committed `c2/release-b11909.json`, and the tag commit is established with `ls-remote` plus a filtered fetch (§2). The cache model digest is re-hashed on the host, not re-downloaded.

## 5. Files written

Lane evidence (new, untracked at the build tip; the patch adds exactly these):

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/c2/x0-digest-rehash.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/hexrun-evidence/caa8191df159f764fb0160e3d2fc6be008948aee.txt`

Out directory `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/X0Digest/`:

- `proposed-ledgers.patch` (landable), `proposed-digest-ledger-rows.tsv` (2 rows), `proposed-hexrun-ledger-rows.tsv` (1 row), `proposed-digest-ledger-row-libimpl-optional.tsv`, `proposed-sources-rows.md` (alternative wording, do not apply alongside the in-flight rows)
- `scan-baseline.txt`, `scan-docs-only.txt`, `scan-with-ledgers.txt`, `hexrun-baseline.txt`, `hexrun-docs-only.txt`, `hexrun-with-ledgers.txt`, `scan-inflight-before-rows.txt`, `scan-inflight-no-artifacts.txt`, `scan-inflight-with-artifacts.txt`, `hexrun-inflight.txt`

The three receipts, `install.txt` and both release-JSON copies are cited at their lane paths rather than copied here: they are (or must be) committed at integration, and their digests are in `x0-digest-rehash.txt`.

No tool was installed or upgraded this round. No lane file other than the two evidence paths, this report and the out directory was written; the lane's jj state and git index were not touched, and the scratch fixtures (five repos: three measurement fixtures, one rule-out fixture and one filtered upstream clone, all deleted with `$S`) carried the fixture identity so no commit could land elsewhere.
