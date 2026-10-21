# Falsify Row C03-fabricated-full-hash (control)

Target: `tests/report-audit/repo-state-grid.py` row `("C03-fabricated-full-hash",
"control", c_fake_full, 1, ["unresolved-full-hash"])` at lane
`245a37f69628c2c6bb29bbf17897d8fb5946c857`, builder at
`tests/report-audit/repo-state-grid.py:139-143`.

**Verdict: holds.** Premise real, frozen arm produced the same ordinary verdict
as current, the expectation is the *correct* one per the auditor's documented
contract, and no in-channel near variant made current crash, flip, misgrade, or
violate its declared semantics. One variant (`v-replace-fake`) shows current is
strictly *more* correct than frozen — evidence the round-23 hardening works.

## Independent fixture (built by hand, no grid import)

Replica of `c_fake_full` (commit order, authors, `@when +0000` dates, env
scrubbing, argv all mirrored, in `/tmp/c03-probe-4cnqsz_u/replica-C03`):

- `lane`: `git init -b master`; one commit `db796f8b…` by `kama-shokunin`
  `@1000`, subject `round-1: work`.
- `fleet`: committed `.ufo/reports/round-1/kama.md` by `fleet` `@2000`, bytes
  `# kama round 1\n\n## Landed changes\n\n- <lc>\n\n## Notes\n\nsee <FAKE>\n`
  with `FAKE = 1234567890abcdef1234567890abcdef12345678`.
- Premise confirmed at the object layer: `git cat-file --batch-check` →
  `…missing` in **both** lane and fleet; `for-each-ref` shows only
  `refs/heads/master`. Report bytes verified with `cat -A`.

## Runs (both arms, my replica)

`python3 <auditor> --lane-repo lane --fleet-repo fleet --json --rounds 1 --no-errata`
(scrubbed env, `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1`, cwd=fixture):

- frozen (`4fe9339f…:tools/report-landing-audit.py`, sha256 `09ecd63b…`):
  **exit 1, kinds=[unresolved-full-hash], no traceback, empty stderr.**
- current (`tools/report-landing-audit.py`, sha256 `f228f174…`):
  **exit 1, kinds=[unresolved-full-hash], no traceback.**
- Grid on my clone for this row alone: `repo-state-grid.py --case
  C03-fabricated-full-hash` → `exit=0`, both arms `met`.

## Q1 — premise real & observed in frozen? YES.

The fabricated 40-hex is a "40-hex token … no git object in the lane or fleet
repo" (docstring, `tools/report-landing-audit.py:12`). `FULL.finditer(text)`
(`:278`) scans the whole report — `## Notes` is in scope — `lookup` returns
`missing` in both repos → `unresolved-full-hash` → exit 1. Frozen shares this
exact logic (the frozen↔current diff does not touch FULL/ABBREV regexes,
`classify_full_hashes`, `lookup`'s missing→found mapping, or `audit_round`'s
defect assembly), and it emitted the identical verdict. The row is a *control*:
its job is to prove the ordinary `unresolved-full-hash` verdict survives in
both arms — it does.

## Q2 — is the expected outcome correct? YES.

- `unresolved-full-hash` is literally the documented kind for this input; the
  Notes occurrence is outside `## Landed changes`, so `landed-unresolved` must
  NOT join (landed = section `group(1)` only — verified in `v-heading-hash`
  below). Exit 1 follows `summary.status` logic at `:499-501`.
- Cross-checked the URL exemption: with NO `corpus/SOURCES.md`, `source_urls`
  is `None` → every 40-hex scanned (`:273-274`), so FAKE cannot dodge. With a
  13-cell Registry row registering `https://e.invalid/x/<FAKE>`, the same
  report text correctly goes **clean** (`v-url-exempt2` exit 0,
  `source_url_hashes=[FAKE]`) and a non-registered sibling URL still flags
  (`v-near-url` exit 1). Exemption is exact-match, not substring — correct.

## Q3 — near variants, same channel (17 probes, both arms)

Flagged correctly by current (exit 1):

| variant | result |
|---|---|
| FAKE inside `## Landed changes` (`v-landed-fake`) | `landed-unresolved` + `unresolved-full-hash` |
| FAKE as only citation, lc real (`v-fake-only`) | + `landed-omitted` |
| FAKE on the `## Landed changes` heading line (`v-heading-hash`) | `unresolved-full-hash` only — spec-exact boundary |
| FAKE in unregistered https URL, no SOURCES.md (`v-fake-in-url`) | `unresolved-full-hash` |
| FAKE in URL inside Landed despite registration (`v-url-exempt-landed2`) | flagged (landed wins over URL exemption, per `:281-284`) |
| 40-hex-named branch, tag, packed ref (`v-fake-ref/tag/packed-ref`) | `unresolved-full-hash` — `cat-file` treats 40-hex as object name; ref names can't shadow it |
| corrupt loose object at FAKE's path (`v-corrupt-object`) | `missing` → flagged, no crash |
| fenced-block `## Landed changes` shadow (`v-fenced-shadow`) | first-match regex takes fake section → 3 kinds; markdown-render disagreement is spec-consistent |

Correctly clean (exit 0): `v-blob-token`, `v-tree-token` (spec says "no git
*object*", blob/tree qualify); `v-fleet-only-object` ("lane **or** fleet
repo"); `v-url-exempt2`, `v-census-form` (registered URL, exact + census forms).

**`v-replace-fake` — the one divergence, in current's favor.** Fixture plants
`refs/replace/<FAKE> → lc`. Frozen: `cat-file --batch-check` honors replace →
token resolves → **exit 0, fabricated citation laundered.** Current passes
`--no-replace-objects` (`GIT_ISOLATION`, `:93`) → `missing` → **exit 1**,
correct. This is direct positive evidence the round-23 hardening is real on
exactly the C03 channel.

One-character token-boundary dodges — `g<FAKE>` prefix, `FAKE+"f"` (41-hex),
uppercase FAKE — are invisible to both FULL and ABBREV → exit 0 in **both**
arms, consistent with "40-hex token" in the docstring (adjacent `[0-9A-Za-z]`
disqualifies; git refs/hex are lowercase anyway). Gray, spec-faithful,
not a falsification.

## What I did NOT verify

- Grading internals beyond this row (kinds sortedness only checked on my own
  outputs; the grid's `met` logic read, not re-derived per-row).
- O01 alternates, O02 gitfile, second-Landed-section, errata-CR channels
  (declared open / other rows' scope).
- Whether `unresolved-full-hash` *should* demand commit-ness for blob/tree
  tokens — spec's literal "git object" wording makes current behavior correct;
  flagging this semantic tightening is a spec question, not a defect.
- Auditor mutation: post-run `git status --porcelain`/`fsck` on the replica —
  empty/silent; auditor is read-only on fixtures.

## Files written

- `/tmp/kama-r23w2/RowC03FabricatedFull/` — `--no-hardlinks` clone at the
  pinned commit (verified `rev-parse HEAD` = `245a37f6…`).
- `/tmp/kama-r23w2/frozen-audit.py`, `c03_probe.py`, `c03_probe2.py`,
  `c03_probe3.py`; fixture roots `/tmp/c03-probe{,2,3}-*`.
- This report. No lane tracked files touched. No installs needed (python3 +
  git 2.56.0 suffice).
