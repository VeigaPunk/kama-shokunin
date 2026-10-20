# ReviewMethods — round 13: capture/comparison method vs reproduce.py and fidelity.py

Scope: static review of the round-12 source-correspondence method as implemented in `.ufo/waves/round-12/fidelity.py` and `.ufo/waves/round-12/reproduce.py`, against the KQ15 wording (`corpus/QUALITY.md:49`) and the planned KQ16 literals. Question under review: whether "same Git repository" is independent provenance authority.

Executed: nothing. No fidelity.py, reproduce.py, selftest, git command, build, test, linter, or gate was run by this seat. Evidence is file reads and text search (`grep` over the two `.py` files for `show|textconv|GIT_CONFIG|independent`, which matched only `fidelity.py:115 --show-toplevel`, `reproduce.py:34`, `reproduce.py:92`, `fidelity.py:9`). Receipt observations below are read from committed files, not re-observed. Tools installed or updated: none.

## Verdict on the corrected method

- **Comparison verb: accurate.** Both gates compare with `git cat-file blob`. `fidelity.py:261-262` (`rev-parse --verify`), `fidelity.py:271-273` (`cat-file blob REV:PATH`), `reproduce.py:79-80` (`rev-parse --verify`, `cat-file blob`). Nothing in either file invokes `git show`. The KQ15 phrase "blob fetched directly as `git show`" (`corpus/QUALITY.md:49`) is therefore inaccurate for the comparator. The planned KQ16 comparison literal `comparison: git cat-file blob` is correct.
- **Capture verb: narrative only, not machine-checkable.** The snapshot was produced once by `git show` (`.ufo/waves/round-12/advice/Fidelity.md:19-20`, `:37-40`; registry `SKILL.md:396` "captured byte-exactly via `git show`"). No committed file records that command: `frozen/expected.json:1-10` has no capture field, no sidecar exists, and ReviewGateInterface F8 (`advice/ReviewGateInterface.md:58`) asked for one. `reproduce.py` re-checks bytes only. The planned literal `capture: git show` is therefore an accurate description of history but is not reproducible by any committed code.
- **Capture mechanism does not affect the verdict.** The gates compare actual bytes against the code-pinned blob, so a different capture route would surface as `source_mismatch`, not as a false clean. The "byte-identical by construction" reading should be avoided: the `git show` plain-blob quote (S032) does not establish that display bypasses textconv or filters (`advice/ReviewSkill.md:39` and `advice/AttackSourceCuration.md:77-83` already flag this as [INFERENCE]).

## Same repo is not independent provenance (primary finding)

Both gates read one object database through the host `git` binary: `fidelity.py:93-111` (`-C` repo), `reproduce.py:49-50` (`-C ROOT`). The source authority is the lane's own committed history: commit `2f7303c…` was authored by `kama-shokunin` (`.git/logs/HEAD:21`), and the pinned constants (`fidelity.py:44-49`, `reproduce.py:15-19`) were chosen by the same lane.

What the code does establish (strengths, verified statically):
- Content pin: `fidelity.py:283-285` requires `source_oid == SOURCE_BLOB_OID`, `sha256(blob) == SOURCE_SHA256`, and length; a repository returning other bytes for that OID yields `source_unavailable` (exit 2), not a clean. Constants live in code, and `load_manifest` rejects any manifest that redirects them (`fidelity.py:148-175`; `reproduce.py` pins `MAN_EXPECTED` at `:23-26`).
- Replace refs disabled: `--no-replace-objects` (`fidelity.py:95`, `reproduce.py:50`) and `GIT_NO_REPLACE_OBJECTS=1` (`fidelity.py:84`, `reproduce.py:33`).

What it does not establish:
- Provenance independence. The anchor is a content hash, so it detects corruption of the blob in this repository, but the constants and the blob are both lane-authored, read by the same binary and object store, and the "before" defect was found by an outside reviewer while the "after" 0 is a construction copy (`corpus/lessons/round-12-verifier-spotcheck.md:93`). The correspondence result is "snapshot equals a blob this lane committed earlier." It says nothing about whether that blob is accurate about its external sources (KQ14 already says so).
- Statistical independence: n = 1 blob, one repository, one author, one git binary, one publish path. Repeating the check inside the same repository adds no independent observation.
- Remote: `.git/config:6-8` configures `origin` (GitHub). `.git/refs/remotes/origin/master` (loose) contains `941bb32c3f591bc63cbf7579b2b6c552228307cd`, which overrides the packed `83bee7f…` entry. Whether `2f7303c…` is an ancestor of `origin/master` is **not observed** here (no git or network run). Even if it is, a remote copy is a second storage location, not a second authority: same author, same publish path. Treat as [INFERENCE] until Main checks.

Recommendation for KQ16 wording: describe the check as "byte correspondence to a code-pinned blob in this repository, recomputed by two code paths that share one object store and one git binary." Do not call it independent provenance.

## Other findings (ranked)

1. **Wording overstates independence (low).** `reproduce.py:92` says "independent source anchor/correspondence checks failed"; the checks are recomputations over the same repository. `fidelity.py:9` ("Two independent checks") refers to integrity vs correspondence and is accurate. Recommend "recomputed" in any future correction. Not to be edited in round 13 (outside write set).
2. **Capture step not recorded in committed artifacts (low-medium).** See capture verb above. Recommend KQ16 state "capture: git show (one-time, uncommitted command; see advice/Fidelity.md:19-20)" or equivalent, rather than implying reproduction.
3. **Git environment asymmetry (low).** `reproduce.py:33-34` sets `GIT_CONFIG_NOSYSTEM=1` and `GIT_CONFIG_GLOBAL=/dev/null`. `fidelity.py:80-90` strips every `GIT_*` variable and sets neither, so its git reads honour user and system configuration. Reproduce's suppression is also not inherited by the fidelity child, because fidelity strips `GIT_*` from its own environment. The lane's own design (`advice/AttackSourceAnchor.md:94-96`) recommended these two variables. Byte effect on `cat-file blob`: not observed; [INFERENCE] none for raw blob output. Record as residual; do not change `fidelity.py` in round 13.
4. **Textconv question open (low).** Whether `git show REV:PATH` applies textconv for this path is not established by the quoted manual text (`advice/AttackSourceCuration.md:27,77-83`). Doesn't change the verdict (see above) but KQ16 should not assert byte identity by construction.
5. **Gate-code provenance not in receipt (info).** `reproduce.py` records the `fidelity.py` invocation path and output digests, not `fidelity.py`'s own SHA-256. A byte-equality claim for `fidelity.py` across revisions rests on closure's separate comparison (`corpus/lessons/round-12-verifier-spotcheck.md:79`), not on the receipt.

## Confirmed consistent (no defect found)

- Exit mapping: `fidelity.py:317-319` (`source_mismatch`→1; `snapshot_tampered`, `source_unavailable`→2) matches the KQ16 literal `source_mismatch=1; snapshot_tampered=2; source_unavailable=2`, and the registry `SKILL.md:396`.
- Precedence: `fidelity.py:55-56,64-72` makes every exit-2 finding outrank `source_mismatch`. `mismatches` counts only `anchor_matches is True and source_matches is False` (`fidelity.py:323`), so pin failures are not folded into the C1 count.
- Control matrix: `reproduce.py:123-181` covers before/after/selftest/coherent/tamper/repoint/unavailable, with the C1 derivation at `:104-105`.

## Limits

- Static reading only; no execution, so all behaviour above is [INFERENCE] from code except where a file quote is given.
- KQ16 text was not present in `corpus/QUALITY.md` at review time (last criterion row KQ15 at line 49); findings on KQ16 wording are conditional on the Criterion seat's final bytes. Re-check when notified.
- Remote ancestry of `2f7303c` and textconv behaviour of `git show` are unobserved.

Report: .ufo/waves/round-13/advice/ReviewMethods.md
