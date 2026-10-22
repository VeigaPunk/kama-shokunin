# SrcFsckReject — round24 fresh source falsification (S104 / S105)

Advice only; no source-row edits, no candidate/grid runs, no execution-bearing
probes. Production repository was read only; all checkout work is in
`/fast/scratch/hyaku/kama-r24/falsify/SrcFsckReject/repo`.

## Verdict

- **S104 — holds.** The registry anchor, v2.56.0 version pin, 2026-10-21
  access date, 5-word located code quote and rejected-inference teaches cell
  all match a fresh open. The rejection is scoped to *fsck green as local
  availability proof for promised/required objects*; it does not reject
  generic fsck validity, and its knowledge/SKILL consumers use it at that same
  narrow scope.
- **S105 — holds.** The explicit rejection of the S095 subprocess/
  TextIOWrapper cross-API inference is supported by the live page and by the
  hash-pinned retained snapshot (0/0/0 negative counts), with a 9-word located
  bytes.decode quote. S095's immutable teaches/status are unchanged; S096
  remains the mined positive bytes.decode consumer actually used by the
  auditor.
- Two observation-only notes for L1, neither a failure: (a) the same
  `'strict' ... UnicodeError ... raised` sentence also appears in the
  preceding `str.encode` paragraph, so the anchor must stay paragraph-specific;
  (b) S096 and S105 share one URL and therefore fall in the existing W04
  duplicate-url warning class (pre-round validate showed many such warnings
  with exit 0; source-census verification is L1-owned and was not run here).

## Snapshot and bounds

- Integrated revision observed exactly:
  `2e254a1763a9c08aa07fc53081287f506c447d84` (clone from
  `/home/vgpnk/Projects/shokunin/kama-shokunin` with `--no-hardlinks`,
  detached checkout; `git status --porcelain` empty).
- `corpus/SOURCES.md` sha256
  `f42c75522e064b34bcaedd3188c85967718a625b7886786c430bdbebaf17d9bd`,
  105 registry rows. Identical hash in the pinned checkout and the lane file.
- Base for immutability comparison:
  `0df800e896f6bce285a81e794ad4ae1d1e6c3a71` (101 rows).
- `S105.json` sha256
  `9f6b8c6ae16282cf1567d7f4c86e9dfa0b0863348ac9d32f5d6be7eacb584990`;
  retained reader snapshot sha256
  `54d4532cb9073365147c168ad6cdf46dd1ecb922ca3b11f77dd867f1ec08cb80`
  (matches the receipt).

## S104 — Git fsck promisor exception (v2.56.0)

Command / exit / finding or token:

1. `curl -sS -L -o fsck.c https://raw.githubusercontent.com/git/git/v2.56.0/builtin/fsck.c`
   → exit 0, HTTP 200, 26980 bytes; sha256
   `d25f3b1a0b96f736bea3c77b79368501d87b1a2d23a0b1daf170b2c2e5a9ca35`.
2. `sha256sum fsck.c .ufo/waves/round-24/build/out/SrcFsck/fsck-builtin.c`
   → both `d25f3b1a...` (fresh open byte-identical to the independently filed
   code snapshot; no version drift).
3. `sed -n '143p;149p;151p' fsck.c` → exit 0:
   - 143 `if (is_promisor_object(options->repo, &obj->oid))`
   - 149 `return 0;`
   - 151 `if (!(obj->flags & HAS_OBJ)) {`
   The row/Gate anchor "`mark_object`, lines143–149" and the words
   "returns ... before HAS_OBJ checking" are exact.
4. Quote length: `if (is_promisor_object(options->repo, &obj->oid))` +
   `return 0;` = 5 whitespace tokens, ≤25; both substrings are present
   verbatim in `corpus/lessons/round-24.md` §Gate.
5. Registry row S104 (live checkout):
   URL `.../git/git/v2.56.0/builtin/fsck.c` (tag-pinned), `kind=code`,
   `tier=A`, scope "rejection of fsck green as proof every promised object is
   locally present", anchor "`mark_object`, lines143–149, v2.56.0;
   opened2026-10-21", status `rejected`, opened `2026-10-21`,
   recheck `on-release`, used-by lesson + knowledge + `SKILL.md`.
6. Knowledge/SKILL use, exit 0 via `grep -n`:
   - `corpus/knowledge/error-is-not-a-verdict.md:104-105`: "Rejected S104
     shows why fsck green cannot substitute for required-object availability."
   - `SKILL.md:846`: "rejected S104 explains why fsck green is not local
     availability proof."
   Neither text generalizes to "fsck is invalid" or "fsck detects nothing".
7. Corroborating code paths (static, same fresh fetch):
   - `fsck.c:253-255` `check_reachable_object` returns on
     `is_promisor_object(repo, &obj->oid)` before printing `missing`
     (line 258 prints only for non-promisor objects).
   - `fsck.c:469` reflog handling skips the invalid-entry error for a
     promisor OID.
   - `packfile.c` (sha256
     `021b1b9b25551070a3a1f986d1972ef93ef9695c3ff4f60eeb0a9a0798b94032`)
     `add_promisor_object` at 2006-2058 inserts a present promisor tree's
     entries and a promisor commit's tree/parents into the promisor set, so an
     absent referenced blob/tree is classified promisor too;
     `is_promisor_object` at 2061 only builds that set when
     `repo_has_promisor_remote(r)` (2066) is true.

[INFERENCE] The runtime consequence — a green `git fsck` on a promisor-remote
clone does not establish local presence of absent promised blobs/trees — is
read from that control flow. No fsck execution or partial-clone fixture was
run in this seat; the assignment is a source check. The rejection's boundary is
also visible: without a promisor remote, the promisor set is not built, so the
row's wording "promised object" (not "any repository") is the correct limit.

Verdict: **holds**, narrow and mechanically supported.

## S105 — bytes.decode rejection record (3.14 series page)

Command / exit / finding or token:

1. `curl -sS -L -o stdtypes.html 'https://docs.python.org/3.14/builtins/stdtypes.html#bytes.decode'`
   → exit 0, HTTP 200, 773977 bytes; sha256
   `044b91ef0e0e6786de9ebdd078282478c8165650d83a8c6b96a59e3c2b7fa67e`.
   Title: `Built-in Types — Python 3.14.9 documentation`; `id="bytes.decode"`
   present.
2. Live bytes.decode/bytearray.decode shared section extracted
   (`id="bytes.decode"` slice, tags stripped, whitespace normalized):
   quote `If 'strict' (the default), a UnicodeError exception is raised.`
   present; occurrences in that section of `subprocess` = 0,
   `TextIOWrapper` = 0, `text mode` = 0.
3. Retained snapshot
   `.ufo/waves/round-24/sources/python-bytes-decode-reader.txt`
   (sha256 `54d4532c...`, equal to `S105.json.sha256`):
   `bytes.decode` starts line 2933; the exact quote is line 2943 in the
   decode errors paragraph; same 0/0/0 counts in that section.
   The reader snapshot's whole-page counts are also 0/0/0.
4. `S105.json` fields match the row and lesson: URL, `accessed: 2026-10-21`,
   page title 3.14.9, snapshot name/hash, anchor "bytes.decode errors
   paragraph", quote (9 words, ≤25), negative counts, and
   `rejected_inference: bytes.decode default documents subprocess text mode
   or TextIOWrapper default`.
5. Registry row S105: scope "explicit rejection record for the cross-API
   inference in S095; not a new decoder fact"; teaches begins
   `supersedes S095 — REJECTED: bytes.decode strict-default documentation
   does not establish subprocess text-mode or TextIOWrapper defaults; flip:
   cite the separately opened subprocess/io anchors (S097/S098). S096 remains
   the narrowed positive decoder fact.`; status `rejected`; opened
   `2026-10-21`.
6. Flip anchors exist and fit: S097 covers `subprocess.run` text-mode
   streams; S098 covers `io.TextIOWrapper` `errors=None` behaving as strict.
7. S095 immutability (`git show 0df800e:corpus/SOURCES.md` vs pinned file):
   all immutable cells equal, including teaches ("...text-mode subprocess
   output with invalid bytes raises...") and status `rejected`; only the
   mutable `used-by` cell changed. S096 remains `mined`, keeps its narrowed
   teaches ("Says nothing about subprocess text mode (S097, S098)") and lists
   `tools/report-landing-audit.py`; the auditor's `git()` defaults
   `errors="strict"` and decodes stdout with
   `proc.stdout.decode("utf-8", errors)` (tools/report-landing-audit.py:156,177).
8. Whole-registry check base→current (static parse, no edits): new rows are
   exactly S102/S103/S104/S105 appended after the preserved 101-row prefix;
   immutable-cell diffs = none; mutable diffs = `used-by` only on
   S083/S089/S094/S095/S096/S099/S100/S101, exactly the round-24 lesson's
   old→new table.

Observation: the identical `'strict'` sentence also occurs in the preceding
`str.encode` paragraph (snapshot line 1397). It is still located in the
bytes.decode errors paragraph (line 2943); the row and receipt correctly name
that paragraph rather than relying on a page-unique sentence.

Verdict: **holds**, with the rejection scoped to the cross-API inference, not
to `bytes.decode`'s documented strict default.

## Observed vs inferred

- Observed: fetched bytes and hashes; exact source lines; fresh-vs-filed
  snapshot byte identity for fsck.c; live and retained bytes.decode section
  text, quote and 0/0/0 negative counts; row cells; base→current immutable
  diff; consumer references.
- [INFERENCE]: fsck's behavior in a real promisor-remote repository, read
  from `mark_object`/`check_reachable_object`/reflog and
  `add_promisor_object`/`is_promisor_object`; no runtime fixture was executed.
- [INFERENCE]: the S096 used-by entry is a semantic consumer relation (the
  auditor does not cite S096 literally; it relies on bytes.decode's strict
  default), consistent with how S089/S100/S101 also list the tool.

## Files written

- `.ufo/waves/round-24/falsify/advice/SrcFsckReject.md` (this report)
- `.ufo/waves/round-24/falsify/out/SrcFsckReject/evidence.json` (hashes,
  commands, checks)

Scratch (not a deliverable): `/fast/scratch/hyaku/kama-r24/falsify/SrcFsckReject/`
with the detached clone, `fsck.c`, `packfile.c`, `stdtypes.html`.

## Unverified / remaining unknowns

- No source census/validate run (L1-owned by lane bounds); the S096/S105
  duplicate URL is reported as an expected W04 warning-class observation, not
  adjudicated. No source-row edits made.
- No `git fsck` execution or partial-clone fixture; no candidate/grid runs,
  no mutation probes.
- Live HTML and the retained reader snapshot are different serializations;
  byte identity was verified only for the scoped bytes.decode section, title,
  quote and negative terms, not the whole page.
- No blobless/promisor fixture was created or probed; the only git commands
  in this seat were the full lane clone/checkout and `git show` inside that
  clone, so no lazy-fetch-capable fixture probe ran here.
- Inherited Git ≥ 2.45 prerequisite remains open at L0 and was not tested or
  changed.

trailer: .ufo/waves/round-24/falsify/advice/SrcFsckReject.md
