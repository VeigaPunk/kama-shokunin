# RevLookup: `lookup()` repo-state review (round 23, CloseKama22)

Target: `tools/report-landing-audit.py` `lookup()`, lines 131-166 in the latest lane file (sha256 `68476410…`). I reviewed snapshot `79d9e124…`; `lookup()` is byte-identical between the two (`cmp` IDENTICAL), and the drift is limited to the trust docstring, the `GIT_ISOLATION` tuple, and `apply_errata()`. Base: `4fe9339f` blob (sha256 `09ecd63…`).

No production edits, commits, or installs. Every fixture ran in fresh `/tmp` repos. Nothing in the lane or fleet repositories was read or written.

## Bottom line

- **Closed in the current tree (verified):** replace-ref substitution, promisor lazy-fetch execution, ref-shadowed short citations (now a typed refusal), and symbolic errata (non-hex corrections are rejected).
- **Open (verified at audit exit level):**
  - **F1:** peel and cross-repo results overwrite ambiguity, so `landed-ambiguous` is suppressed. This also reaches errata corrections.
  - **F3:** a planted loose object satisfies `unresolved-full-hash`.
- **Latent:** **F2**, repo-local `core.disambiguate` changes bare-name ambiguity. It is masked today by F1 and becomes live as soon as F1 is fixed without pinning it.
- **Scratch prototype (not production)** closes F1-F3. Selftest 50/50 in scratch. See section 4.

## 1. Findings

Severity: Medium = a false clean or wrong verdict reachable from a citation or from repo-local state. Low = semantics or hygiene.

### F1. Medium. Ambiguity erased by peel and by the other repo (false clean, pre-existing, outside the grid)

- **Code:** the bare pre-pass is merged across repos into `status` (lines 140-143). The peel result then sets `status[token] = "found"` unconditionally (line 165). The docstring (lines 132-135) says the bare name keeps ambiguity visible. `apply_errata()` calls the same `lookup()` (lines 396-397).
- **Lookup evidence** (`out/RevLookup/fixtures_lane_latest.txt`):
  - Commit + blob share 7-hex `68c726c`, same repo: bare `ambiguous`; `^{commit}` → `found`.
  - Cross-repo `8877aee`, lane holds both commits, fleet holds the first: `found` for bare and peel. The lane alone is `ambiguous`.
- **Audit exit-level evidence** (`out/RevLookup/e2e_lane_latest.txt`, `main()` return codes, base vs latest lane):
  - R1, commit + blob 7-hex in `## Landed changes`: rc 0, no defects, both versions.
  - R4, commit + commit with the fleet holding the first: rc 0, both versions. The control R4 (fleet lacks the first) gives rc 1 `landed-ambiguous:8877aee`, so the detector works and the cross-repo lookup is what hides it.
  - Errata correcting an unresolved 40-hex with `68c726c`: rc 0, both versions. An ambiguous abbreviation validates as a correction.
- **Selftest blind spot:** `ambiguous-prefix-is-ambiguous` (line 795) uses blob + blob (`hash-object`, line 787). There peel yields `missing`, so the blob-vs-commit path is never exercised.
- **Sibling reconciliation:** this explains `CritFalsifyClaim` b1 "no flip". That is true for the final verdict only because F1 masks the bare-pass flip (F2). `ConnPlanningWalk.md:428` calls the end-to-end 7-hex landed-ambiguous path "infeasible". A 90k-object `fast-import` produced both collision kinds in about 1 s here.
- **Likelihood [INFERENCE]:** natural 7-hex collisions are rare in real object sets. A chosen one needs roughly 2^28 hashes.
- **Fix verified in scratch (section 4):** a per-repo bare probe, with ambiguity sticky so that neither the peel nor another repo can erase it.

### F2. Medium if F1 is fixed without it; Low as the code stands. Repo-local `core.disambiguate` is not pinned

- `GIT_ISOLATION` (lines 94-97) does not pin `core.disambiguate`.
- Observed on git 2.56.0, commit + blob collision in one repo (bare / peel):

| `core.disambiguate` | bare | peel |
|---|---|---|
| unset, `none`, `tree` | `ambiguous` | `found` |
| `blob`, `commit`, `committish` | `found` | `found` |
| `tag` | EvalError, rc 128 `unknown hint type` | same (fail-closed) |

- Today the final verdict is `found` in every row because of F1's override, so the flip is visible only at the bare-pass level. If F1 were fixed without pinning, a repo's config would decide whether a citation is flagged. The prototype pins `-c core.disambiguate=none`, which gives `ambiguous` in both passes.
- Not in the installed `git-config(1)`, `git-rev-parse(1)`, or `gitrevisions(7)` man pages (grepped). Behaviour is observed; upstream docs were not checked.

### F3. Medium (threat-model dependent). Existence is not integrity: a planted loose object is "found"

- `cat-file --batch-check` reads the loose-object header and never re-hashes the content. A loose object at the fabricated name `e4f1c2a9…` containing `blob 3\0abc` is `found` by bare lookup and `missing` by peel (`fixtures_lane_latest.txt`).
- Audit R2 (a 40-hex cited in the body): rc 0, both versions.
- The module docstring's "Repository trust" paragraph says other repository-local channels are not claimed. This gap is therefore a declared non-claim. The lead must decide whether `.git/objects` tampering is in the threat model.
- Fix verified in scratch: re-hash every found object (`sha1("<type> <size>\0" + body) == name`). R2 then gives rc 2 (could-not-evaluate).
- Not tested: packs, and `git fsck`.

### F4. Low. An annotated tag object's abbreviation is accepted as a commit citation

- Fixture `annotated_tag`: the 7-hex prefix of the tag object is `found` by bare lookup and `found` via peel (the target commit), in both versions.
- Peel should count only when the bare name is itself a commit (its type is available in the bare pass). Not verified as fixed.

### F5. Low (hygiene). `excluded` and `dangling` branches are unreachable

- Lines 157-158. The installed `git-cat-file(1)` prints `<object> SP excluded` only for names filtered by `--filter=`, and `dangling SP <size>` only under `--follow-symlinks`. `lookup()` passes neither flag.
- Harmless: if ever reached, they read as `missing`. Delete or assert.

## 2. Verified closed (no action)

- **Replace refs** (`--no-replace-objects`, line 94):
  - Fabricated 40-hex with `refs/replace` → base `found`, latest `missing`.
  - Real commit replaced by a blob, peeled → base `missing` (a false defect), latest `found`.
  - Control unchanged.
- **Promisor exec** (`--no-lazy-fetch`, line 94): object absent locally, `core.sshCommand` planted → base `sshCommand ran=True`, latest `False`; both `missing`.
  - Run level: `check_history_repo` (line 429, called at 479) refuses any `extensions.partialclone` or `remote.*.promisor` repo. Observed EvalError; `main()` maps EvalError to rc 2 (code).
  - Behaviour change: a benign `file://` partial clone was `found` in base and is now refused. The docstring says this is intended. `CritNoHarm.md:17` says the ledger repos have no promisor config; I did not re-verify that.
- **Ref-shadowed short citations** (lines 162-164):
  - `refs/heads/a1b2c3d` and `refs/tags/b2c3d4e` → base `found`; latest refuses with `citation a1b2c3d names a ref`, for both bare and peel.
  - Control: the real prefix is `found`. A 40-hex branch name does not shadow (`missing` in both).
  - The refusal is per repo, so a fleet ref can also trigger it. That is fail-closed.
- **Symbolic errata:** a `HEAD` correction gives base rc 0 (false clean) and latest rc 1. The lookup list is regex-filtered (line 394); `invalid` requires `status.get(...) == "found"` (lines 396-397).
- **Callers:** every `lookup()` input is hex-only (full hashes, checkable abbreviations, errata regex). Informational: `lookup()` is still a revision parser for any other input. An internal hex assertion would be defence in depth.

## 3. Accepted or informational

- **Alternates:** an object present only via `objects/info/alternates` → `found` in both versions, per contract. The re-hash passes it because its bytes are genuine.
- **`unresolved-full-hash` accepts blob and tree names** (control blob → `found`). This matches the docstring's "no git object".

## 4. Scratch prototype (not production)

File: `/tmp/kama-r23/RevLookup/proto_audit.py`, derived from snapshot `79d9e124…`. Patch: `out/RevLookup/proto.patch`.

- `object_is_genuine` (re-hash), `_probe` (per-repo bare and peel probes with the same ref refusal), and a new `lookup()` with sticky per-repo ambiguity.
- `-c core.disambiguate=none` appended to `GIT_ISOLATION`.

Results:
- **Lookup matrix:** commit + blob → `ambiguous` in both passes; cross-repo → `ambiguous`; planted object → EvalError; every `core.disambiguate` value → `ambiguous` in both passes (`tag` still refuses). Replace, promisor, ref-shadow, and alternates are unchanged.
- **Audit replay** (`out/RevLookup/e2e_proto.txt`):
  - R1 → rc 1 `landed-ambiguous:68c726c`.
  - R2 → rc 2 could-not-evaluate (re-hash).
  - R4 → rc 1 `landed-ambiguous:8877aee`.
  - Errata `68c726c` → rc 1 (invalid).
  - R3 and R3 + `HEAD` unchanged (rc 1 and rc 1).
- **Selftest (scratch copies):** snapshot 50/50 (`selftest_cur.txt`); prototype 50/50 (`selftest_proto.txt`).

Not done:
- The latest lane file's selftest was not run.
- The historical ledger was not re-run. `HistoricalNoHarm` must re-run before adoption: sticky ambiguity and the re-hash could change a historical verdict, which I do not expect.
- The patch targets `79d9e124`. The latest lane file drops `core.quotePath` from `GIT_ISOLATION`, so the last hunk needs re-applying by hand.

## 5. Verification gaps

- Only git 2.56.0 is installed. The docstring's ">= 2.45" floor is unverified. The `core.disambiguate` docs were not checked online.
- F3 was tested with loose objects only. Packs and `git fsck` were not run.
- Real-world prevalence of F1 and F3 was not measured.
- Sibling channels (grafts, shallow, textconv, showSignature, mailmap, notes) were not re-run. I relied on `CritFalsifyClaim`, `CritNoHarm`, and `ScoutShowSignature` and kept scope to `lookup()`.
- The lane file moved during review (`79d9e124…` → `68476410…`). Findings were re-run on the latest sha.

## 6. Tooling

No installs or updates. Used the installed git 2.56.0 and python3 stdlib only.

## 7. Files written

- `.ufo/waves/round-23/build/advice/RevLookup.md` (this report).
- `.ufo/waves/round-23/build/out/RevLookup/`:
  - Harnesses: `fixtures.py`, `e2e.py`. The `CUR_PY` environment variable selects the candidate file.
  - Outputs: `fixtures_cur.txt`, `fixtures_proto.txt`, `fixtures_lane_latest.txt`, `e2e_lane_latest.txt`, `e2e_proto.txt`, `selftest_cur.txt`, `selftest_proto.txt`.
  - Patches: `proto.patch`, `lane_drift.patch`.
- Scratch only, not deliverables: `/tmp/kama-r23/RevLookup/`.

No production file, lane index, or tracked file was touched.

Reproduce: `cd /tmp/kama-r23/RevLookup && CUR_PY=<lane>/tools/report-landing-audit.py python3 fixtures.py && CUR_PY=<lane>/tools/report-landing-audit.py python3 e2e.py`.

## 8. Lane access (disclosure, appended)

The header's statement that nothing in the lane was read or written is too strong. I read the lane's tracked `tools/report-landing-audit.py` and ran read-only git commands in the lane checkout: `status --short`, `diff --stat`, `diff --no-index` against a scratch copy, `log -1`, `rev-parse HEAD`, and `show 4fe9339f:…`. `git status` and `git diff` can refresh the `.git/index` stat cache without changing content. I wrote no commit, ref, `.jj` state, or tracked file. The index refresh is a possible write that the contract forbids, so it is disclosed here. The fleet repository was not touched. The fixtures ran only in `/tmp`.
