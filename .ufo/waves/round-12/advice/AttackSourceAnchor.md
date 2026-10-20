author: KamaR12.AttackSourceAnchor (critic; author advisor, not closure)

# Round 12 C1 — source-anchor attack review

Scope: I attacked the shared-interface design of `fidelity.py` and `reproduce.py` (spec.json
§Shared interfaces). When I reviewed it, `.ufo/waves/round-12/` held no `fidelity.py`,
`reproduce.py` or `frozen/`, so every finding below is design-level and static. I executed no
attack and ran no test. I installed no tools.

## Read-only facts gathered (git 2.55.0, lane repo)

| Fact | Observed |
|---|---|
| object format | `sha1` |
| `2f7303c…:corpus/SOURCES.md` blob OID | `7de1360655eadada356fe110813c6e1338142551` |
| blob size | `18898` bytes |
| commit tree | `00ef375c64f2741d98d2ddc86ef2e425c7f85739` |
| `git cat-file blob` bytes, SHA-256 | `9dc40d25a595b3d42b39649e17094cfa4e7190cfbf340331252dd29dea22093a` (equals D1 "actual") |
| old frozen `round-11/frozen/before/corpus/SOURCES.md` | `52665cf2…142fa1` (equals D1 "frozen", also pinned in round-11 `expected.json:15`) |
| `refs/replace/*` / `objects/info/alternates` | 0 refs / no alternates file |
| source commit ancestor of HEAD | yes |
| `GIT_*` env inherited by this session | `GIT_EDITOR`, `GIT_PAGER`, `GIT_TERMINAL_PROMPT` (all harmless here; this shows that env is inherited) |

## Counterexamples

**A1. Coherent snapshot and manifest edit (high).** The spec says that "Manifest pins snapshot
SHA-256, source commit/path". Suppose the attacker mutates the snapshot, recomputes the manifest
`sha256`, and points the manifest's `source_commit` at any commit that contains the mutated bytes.
That can be a new commit in the lane, or a commit in a temp repo reached with `--repo`. Integrity
then passes (the self-consistent digest) and correspondence also passes (the attacker-chosen
source). Result: `clean`, exit 0. This repeats the D1 failure class: "a green digest check proves
integrity against the shipped expected file, not correspondence with git history" (spot-check
L109-110). Round-11 avoided half of this by pinning `BASELINE_SHA256` in code (`measure.py:101`).
A manifest-only pin repeats the hole.
*Axes:* calibration (false 0), quality.

**A2. Mutable source revision (high if any is accepted).** A source revision could be a ref name
(`HEAD`, a branch or a tag), an abbreviated hash, or a `rev^{…}`/`@{…}` expression. Any of these
lets the "fixed" source move. A revision that begins with `-` becomes an option injection unless
`--end-of-options` is used.
*Axes:* calibration.

**A3. Redirected git root (high).** `--repo PATH` combined with any of the following redirects
the source:
- (a) An inherited `GIT_DIR`, `GIT_OBJECT_DIRECTORY`, `GIT_ALTERNATE_OBJECT_DIRECTORIES`,
  `GIT_REPLACE_REF_BASE`, `GIT_CONFIG_PARAMETERS`, `GIT_CONFIG_COUNT`/`KEY_*`/`VALUE_*`, or
  `GIT_NAMESPACE`. `GIT_DIR` overrides `-C` discovery.
- (b) A repo where `git replace 2f7303c <evil>` is set. `git show` and `git cat-file` both honour
  replace refs by default, so the pinned-looking hash yields arbitrary bytes.
- (c) [INFERENCE] A hand-written loose object stored under the pinned commit's name. Plain blob
  and commit reads do not rehash content, so this is only caught by `fsck` or by local rehashing.
- (d) A partial clone. A missing blob triggers a promisor lazy fetch, which is a network/endpoint
  call that the contract forbids.
- (e) A `--repo` path inside a different repo's subdirectory. Upward discovery finds the outer
  repo.

Case (b) or (c) inside the runner's "isolated coherent-mutation attack" repo would make the attack
falsely pass rather than prove the defence.
*Axes:* calibration, safety (case d).

**A4. Output and finding false positives (medium).**
- (i) The runner or verifier might grep stdout for `clean` or a finding name. Attacker-controlled
  strings echoed into output could contain those words: snapshot path, manifest fields, git
  stderr.
- (ii) If the tool emits or compares against the manifest's `expected_verdict`, a manifest that
  says `"source_mismatch"` turns a mismatch into "as expected", exit 0.
- (iii) Text-mode comparison (`text=True`, `read_text`) applies universal newlines and decoding.
  CRLF/LF or encoding-normalized copies would then compare equal.
- (iv) `--snapshot` without a manifest yields `clean` for any byte-correct copy. That is correct
  for correspondence. But if the output reports integrity as passed (or omits it), an unpinned run
  reads like a pinned one.
- (v) Ambiguity: `--snapshot` is required and the manifest has a default. If the default manifest
  is applied to the old round-11 file, the result is `snapshot_tampered` (exit 2), not the intended
  `source_mismatch` (exit 1), and the 1→0 delta disappears. If the rule is "apply the manifest only
  when the path equals X", then a symlink or `..` alias silently changes the mode.

**A5. Selftest pressure toward an override (medium).** An isolated `clean` case cannot fabricate
commit `2f7303c` in a temp repo. That makes it tempting to add a `--source-commit` (or similar)
CLI override for the selftest. That override would recreate A1/A2 in production.

## Smallest non-bypassable anchoring (recommend to KamaR12.Fidelity)

1. **Code constants, not manifest authority:**
   - `SOURCE_COMMIT = "2f7303c242319c1dc96c6bcf7702ac18b3ca1aad"`
   - `SOURCE_PATH = "corpus/SOURCES.md"`
   - `SOURCE_BLOB_OID = "7de1360655eadada356fe110813c6e1338142551"`
   - `SOURCE_SHA256 = "9dc40d25…093a"`
   - `SOURCE_BYTES = 18898`

   The manifest may restate these, but any difference is `snapshot_tampered` (exit 2). Also pin
   the manifest's own SHA-256 in code, as round 11 did, so that a coherent manifest edit fails
   closed. Provide no CLI flag for commit or path.
2. **Correspondence from a self-verifying hash chain, not from repo trust:**
   - Run git as `git --no-pager --no-replace-objects -C <repo> cat-file …`, with
     `env = {PATH, HOME, LC_ALL=C, GIT_NO_LAZY_FETCH=1, GIT_NO_REPLACE_OBJECTS=1,
     GIT_CONFIG_NOSYSTEM=1, GIT_CONFIG_GLOBAL=/dev/null}` and every other `GIT_*` dropped.
   - Read `commit SOURCE_COMMIT`, then the root tree, then the `corpus` tree, then
     `blob SOURCE_BLOB_OID`, as raw bytes (`capture_output`, no `text=`).
   - At each step, recompute `sha1(b"<type> <len>\0" + body)` in Python and require it to equal
     the expected OID. Parse the tree entries to the next OID.

   This is about 25 stdlib lines. It defeats A3(a)-(e): a redirected or forged repository cannot
   satisfy the code-pinned commit OID chain. A missing object becomes `source_unavailable`
   (exit 2) with no fetch. Plumbing `cat-file` avoids porcelain `show` config and pager behaviour.
3. **Two independent fields, one exit rule:**
   - `integrity`: `verified`, `tampered` or `not_checked` (no manifest).
   - `correspondence`: `match`, `mismatch` or `unavailable`.
   - Report the snapshot's SHA-256, the source's SHA-256 and the first differing byte offset.

   The exit rule is: 2 if `tampered` or `unavailable`, otherwise 1 if `mismatch`, otherwise 0.
   Always compute correspondence even when integrity fails, so tamper cannot mask mismatch. The
   verdict is derived only in code; never read or echo the manifest's `expected_verdict` as the
   result. Instead, assert in code that it equals `"clean"`. Emit exactly one `json.dumps` object.
4. **Unambiguous no-manifest mode:** add an explicit `--no-manifest` flag (or treat the manifest as
   default-on only when `--manifest` is omitted *and* `--no-manifest` is absent). Report
   `integrity: not_checked`. Do not switch modes by comparing paths.
5. **Selftest without overrides:**
   - clean: real `--repo` (read-only cat-file) plus a temp copy of the snapshot.
   - mismatch: temp copy with one byte flipped and `--no-manifest`.
   - tamper: temp copy plus the default manifest.
   - unavailable: `git init` in a tmpdir (isolated write) as `--repo`.
   - redirect: a tmp repo committing the mutated SOURCES, plus a coherent manifest. Expect exit 2
     (`tampered`, or `unavailable` if the manifest restates the commit honestly). Never exit 0.
6. **Runner checks (KamaR12.Runner):** assert the exit code *and* `json.loads(stdout)` field
   equality. For the old file, expect `correspondence == "mismatch"`, `snapshot_sha256 == 52665cf2…`
   and `source_sha256 == 9dc40d25…`. For the new file, expect `integrity == "verified"`,
   `correspondence == "match"` and exit 0. Never use substring matching. The isolated attack must
   use a temp repo and temp manifest and must expect non-zero.

## Distinguishing fixes from tradeoffs

- A1, A2, A3 and A4(ii)/(v) are fixable defects. They block a truthful 1→0 if they are left open.
- Residual tradeoff for the judge to weigh: the anchor is SHA-1 (the repo object format) together
  with SHA-256 of the blob bytes. A forged chain would need SHA-1 preimages. A collision alone does
  not suffice, because the commit OID was fixed before round 12. This is acceptable, and it should
  be stated as a limitation rather than claimed as cryptographic proof of history.
- Correspondence proves that the snapshot equals the committed bytes. It does not prove the truth
  of any registry row. There is no scalar or calibration increase.

## Checks for L1 (not run by me)

1. Grep `fidelity.py` for the constants above. Confirm that there is no commit/path CLI flag and
   no `text=True` or `read_text` on compared bytes.
2. Confirm the `GIT_*` env scrub and that `--no-replace-objects` and `GIT_NO_LAZY_FETCH=1` are
   present.
3. Run `python3 .ufo/waves/round-12/reproduce.py` once. Expect:
   - old file: exit 1, `mismatch`, hashes as above.
   - new file: exit 0, `verified`/`match`, snapshot SHA-256 `9dc40d25…`, size 18898.
   - selftest: all pass.
   - coherent attack: non-zero exit.
4. Independently run `git -C <lane> cat-file blob 2f7303c…:corpus/SOURCES.md | sha256sum` and
   compare it with `sha256sum .ufo/waves/round-12/frozen/corpus/SOURCES.md`.
5. Run `GIT_DIR=/nonexistent python3 …/fidelity.py --snapshot <new>`: expect the same verdict,
   with the env ignored.
