# S04Policy — source snapshots and corpus rows (round 56, w1)

Seat: S04Policy (sentinel, advisory). Item: verify source snapshots and corpus rows cite
public sources only and do not claim the host install is globally trusted.
Lane tip examined: `efc6b3ec6fb6ea308c15855e9b8b62856f4255b7` (freeze; `git rev-parse HEAD`).
Base control: `e10b6d39af450e8d652be9ac2986768b531fe13f`. Lane tree read-only; no lane or
jj/git mutation performed. Read-only validators run from scratch
`/fast/scratch/hyaku/kama-r56/S04Policy` (removed after evidence was copied here).

## Verdict

| check | result |
|---|---|
| round-56 snapshots are public pages, byte-faithful | PASS |
| round-56 rows cite public sources only, no private/local URLs | PASS |
| no claim that the host install is globally trusted | PASS (scoped trust only) |
| committed row S512 valid at the frozen tip | **FAIL — one E11** (finding 1) |
| lesson quote cardinalities exact | **FAIL — S513 says 16 words, quote is 18** (finding 2) |
| lesson "After" census receipt present | **FAIL — `census/end.out` absent** (finding 3) |

No falsification of claim predicates C1/C2 follows from these findings: C1 and C2 do not
read the lesson, the census output, or the snapshot bytes. The defects are in the
source-registry/lesson layer that the round cites as its gate.

## Finding 1 — S512's `used-by` does not resolve at the frozen tip (severity: MEDIUM)

Frozen tip `efc6b3ec` commits `corpus/SOURCES.md`, both snapshots and the preregistration,
but **not** `corpus/lessons/round-56.md`:

```
$ git cat-file -e efc6b3ec6fb6ea308c15855e9b8b62856f4255b7:corpus/lessons/round-56.md
fatal: path 'corpus/lessons/round-56.md' exists on disk, but not in 'efc6b3ec6fb6ea308c15855e9b8b62856f4255b7'
$ echo rc=$?
rc=128
$ git status --porcelain=v1 -- corpus
?? corpus/lessons/round-56.md
```

Timeline from `stat`/`git log`: snapshots 13:00:35 and 13:02:09, `corpus/SOURCES.md`
13:02:31, freeze commit **13:03:18**, lesson **13:06:24**. The lesson was written after the
freeze commit, so S512's committed `used-by` cell (`corpus/lessons/round-56.md`) points at a
path absent from that commit. A full `git archive` extraction of `efc6b3ec` validates as:

```
$ sources-census.sh validate --root $PWD/frozen-full $PWD/frozen-full
frozen-full	E11	S512 missing used-by corpus/lessons/round-56.md
frozen-full	W01	S481 tierC mined used-by=...
frozen-full	W04	S513 duplicate url man7.org/linux/man-pages/man8/ld.so.8.html across scopes
exit=1
```

Exactly one E-code, and it is S512 (receipt `census-frozen-validate.out`). The same command
against the live worktree, where the untracked lesson exists, is green for S512:

```
$ sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama
kama	W01	S481 tierC mined used-by=...
kama	W04	S513 duplicate url man7.org/linux/man-pages/man8/ld.so.8.html across scopes
... (98 W04 rows, no E rows)
kama	ok	/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md
exit=0
```
(receipt `census-worktree-validate.out`)

Failure path: the round reports "registry row S512 admitted, gate cited in the round
lesson", while the frozen tip cannot reproduce that citation — the registry's own validator
exits 1 on the frozen tree. If integration commits the tools/snapshots but not the lesson,
the row stays dangling. Impact is provenance-only: no measured value depends on it, and the
worktree is currently green.

Smallest remediation: include `corpus/lessons/round-56.md` in the integration commit and
record `census/end.out` from that committed tip; alternatively keep the frozen tip intact and
add an append-only correction noting the row becomes E11-clean only once the lesson is
committed. Do not rewrite the frozen lesson or the preregistration.

## Finding 2 — S513 quote word count is wrong (severity: LOW)

`corpus/lessons/round-56.md` §Gate: the ld.so(8) quote is labelled "(16 words)":

```
$ python3 -c 'q1="the environment variable LD_AUDIT must be defined to contain a colon-separated list of shared libraries"; q2="A list of user-specified, ELF shared objects to be loaded before all others in a separate linker namespace"; print("q1",len(q1.split()),"q2",len(q2.split()))'
q1 15 q2 18
```

The quote itself is verbatim in the snapshot (`q2 in html: True`), so only the cardinality is
wrong. S512's "(15 words)" is correct (`len(q1.split())=15`). Fix: change 16 to 18 in the
lesson before it is committed.

## Finding 3 — "After" census receipt named but absent (severity: LOW)

`corpus/lessons/round-56.md` §Census says in the present tense that the after-run "is
recorded in `.ufo/waves/round-56/census/end.out`". At observation time the directory held
only `start.out` (13:00, 13082 bytes; it predates S512/S513 and therefore contains neither
row). The missing after-receipt is supplied out-of-band by
`census-worktree-validate.out` here: exit 0, S512 clean, S513 W04 only. Fix: land
`census/end.out` at integration, or reword the lesson to future tense until it exists.

## Positive evidence — public-only citations

Both snapshots are exact copies of the live public pages, not host-local or edited text:

```
$ curl -sS -o rtld-live.html -w '%{http_code} %{size_download}\n' https://man7.org/linux/man-pages/man7/rtld-audit.7.html
200 26769
$ curl -sS -o ldso-live.html -w '%{http_code} %{size_download}\n' https://man7.org/linux/man-pages/man8/ld.so.8.html
200 41398
```
(`snapshot-sha256.txt`; snapshot == live fetch byte for byte)

- `rtld-audit.7.html` sha256 `a95aa3fb6407ac8d1890190ca92837445dab774e53996d3d4cf079412c813153`.
- `ld.so.8.html` sha256 `d9b7737e6c9a38f6c7ce11a4feec834704d6ad5139dc790afa9798faf0379f83`.

Page identity matches the rows' anchors: both pages carry `man-pages 6.19 2025-05-17` and
`HTML rendering created 2026-09-09`; both are `docs`/tier A by public manuals, opened
2026-10-27. Quote placement is correct: S512's quote sits between the `DESCRIPTION` anchor
and the next section anchor; S513's sits inside the `LD_AUDIT` environment entry (before
`LD_DEBUG`). No `file:`/`javascript:`/`data:` links; every external href is a public host
(`man7.org`, `www.kernel.org`, `git.kernel.org`, `mirrors.edge.kernel.org`, plus the page's
own `statcounter.com`/`www.jambit.com` analytics and ad hosts). `cookie` occurrences in
rtld-audit(7) are the audit API's
`uintptr_t *cookie` parameter, not tracking data. Wave spec/dispatch cite only man7.org.

Registry-wide: 241 of 254 rows carry an `https://` source URL. The 13 rows without one are
own-lane instrument receipts (S030, S034, S041, S046, S055, S178, S179, S193, S194, S324,
S485, S487, S489), all from rounds 10–46; none is a round-56 row, and the census contract has
no URL requirement for instrument rows.

## Positive evidence — no global host-trust claim

The trust language is scoped everywhere it appears:

- `corpus/SOURCES.md:4-6`: "This file records where claims come from, how far to trust each
  source for which scope, and when to look again. Tiers are scoped to `scope`, never global."
- `preregistration.json:49` (limits): "It does not claim a foreign audit DSO successfully
  injects code on this glibc. C1 is a targeted operability move, not a complete replay-code
  audit refresh."
- `corpus/lessons/round-56.md:3`: "it does not claim to close the broader host-library
  byte-provenance, archive-attribute, or git-config-hermetic routes".
- `tools/round56-replay-code-audit.py:38-42`: "the 13 root-owned host libraries of the honest
  build (basenames, frozen) ... any other root-owned host executable mapping fails".

`grep -ri trust` over the round-56 non-HTML artifacts finds only copies of this seat's own
prompt text (`build_spec.py`, `w1/spec.json`, `w1/dispatch.json`, `w1/validate.out`,
`w1/out/swarm-registry.json`) and the SOURCES header copy under
`out/X06Census/SOURCES-base.md`; `grep -ri globally` over the row/lesson/prereg/counters
finds nothing. The measured receipts are consistent with the
non-claim: `base-c1.out`, `measured/base-c1.out` and `measured/m-drop-ldaudit.out` all show
`ld_audit=missed` while the loader itself prints
`object '/usr/lib/libexpat.so.1' cannot be loaded as audit interface: undefined symbol:
la_version; ignored.` — i.e. the probe depends on the variable name, not on trusting the
host's library set.

## Notes

- S513's `W04 duplicate url ... across scopes` is expected: S067/S079 already register
  ld.so(8), scopes differ, and the row is `rejected` with a flip. Warning only, no action.
- `census/start.out` (13:00) predates the S512/S513 rows, so the "Before: exit 0" line is a
  base-tree run; it does not exercise the new rows. That is why the frozen-tip E11 above was
  only observable from a full-tree validation of `efc6b3ec`.

## Evidence copied here

- `census-worktree-validate.out` — `validate --root /home/vgpnk/Projects/shokunin kama`, exit 0.
- `census-frozen-validate.out` — `validate` against a full `git archive` of `efc6b3ec`, exit 1, E11 S512.
- `snapshot-sha256.txt` — committed snapshots vs live man7.org fetches.
