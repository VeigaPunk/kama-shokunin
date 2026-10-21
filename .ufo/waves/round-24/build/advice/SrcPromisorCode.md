# SrcPromisorCode — git v2.56.0 `promisor-remote.c`: filter-only promisor registration

Seat: KamaR23-2.SrcPromisorCode-2 · base `0df800e896f6bce285a81e794ad4ae1d1e6c3a71` · accessed 2026-10-21
Scope: source evidence only. No production files, registry rows, fixtures, or tests were edited or run.

## Verdict

**Claim SUPPORTED, with a scope limit that matters for r24.** In git v2.56.0 a
`remote.<name>.partialclonefilter` entry registers that remote in the in-process promisor-remote
list even when no `remote.<name>.promisor` boolean is set. The source establishes **promisor
metadata/registration only**; it does not establish that any object is missing, that the
repository is an incomplete partial clone, or that a fail/clean verdict is unavailable.

## Source identity and anchor

- URL (official HTTPS): `https://raw.githubusercontent.com/git/git/v2.56.0/promisor-remote.c`
- HTTP 200, 36203 bytes; sha256 `175e67e1b2cc62db1ead26007ba1e5502f9b585fd33dbc45b59f9876b34f9bca`;
  git blob `43505d1e1ac8fd48cf185169ea76d92dc277ef01` (matches GitHub contents API at `ref=v2.56.0`).
- Version: tag `v2.56.0` (annotated tag object `2478544319491bbd2a42cc57a83e3d2f4730a280` →
  commit `a018953688f1b10bddf91bff8747068f5f4746a4`). Host `git --version` = `2.56.0`.
- Anchor: function `promisor_remote_config`, **lines 148–163**; quote at lines 152–154.
  Rendered: `https://github.com/git/git/blob/v2.56.0/promisor-remote.c#L148-L163`
- Access date: **2026-10-21**.

Exact quote (11 words; only indentation/newlines normalized):

> `r = promisor_remote_lookup(config, remote_name, NULL); if (!r) r = promisor_remote_new(config, remote_name);`

Observed branch, exact lines (`promisor-remote.c.v2.56.0`, line-numbered):

```
148  if (!strcmp(subkey, "partialclonefilter")) {
149      struct promisor_remote *r;
150      char *remote_name = xmemdupz(name, namelen);
152      r = promisor_remote_lookup(config, remote_name, NULL);
153      if (!r)
154          r = promisor_remote_new(config, remote_name);
158      if (!r)
159          return 0;
161      FREE_AND_NULL(r->partial_clone_filter);
162      return git_config_string(&r->partial_clone_filter, var, value);
163  }
```

The sibling `promisor` branch (lines 134–147) is the only place the boolean is consulted:
`if (!git_config_bool(var, value)) return 0;` (line 137). The `partialclonefilter` branch never
reads `remote.<name>.promisor`, so registration does not depend on it.

Related same-file observations: `promisor_remote_init()` applies `repo_config` at line 178, so
registration is lazy per-process, not a load-time repository property; `repo_has_promisor_remote()`
(lines 224–227) is true for any registered entry; `promisor_remote_get_direct()` calls
`promisor_remote_init()` at line 310.

## Claim-vs-source limits

1. **Metadata ≠ incompleteness.** The callback only appends/looks up a `struct promisor_remote` and
   stores the filter string. Nothing here proves objects are absent or that a clone was partial; a
   repository that later fetched all objects keeps the config. Do not turn this into a refusal.
2. **Lazy, per-process registration.** `promisor_remote_init()` (line 168) is only reached through
   consumers such as `repo_promisor_remote_find` (216), `repo_has_promisor_remote` (224–227),
   `repo_has_accepted_promisor_remote` (233), and `promisor_remote_get_direct` (310). Presence of
   the config alone does not alter `log`/`cat-file` results for objects that exist.
3. **`promisor=false` does not cancel a filter-only registration.** The false boolean returns early
   only in its own branch; a later or earlier `partialclonefilter` line still creates the entry.
   Config *order* is not a guard. The C09 control in `tests/report-audit/repo-state-grid.py:539-541`
   sets only `promisor=false`, so it does not exercise the combined case.
4. **One code-level exception.** `promisor_remote_new()` (lines 75–82) warns and returns NULL for a
   remote name beginning with `/`; line 158 then returns without registering. Non-`remote.*` keys
   also return at line 131. The claim is therefore "any well-formed `remote.<name>.partialclonefilter`",
   not literally every string.
5. **This file does not decide which objects are promisor objects.** `is_promisor_object` is defined
   in `packfile.c:2061` and walks `ODB_FOR_EACH_OBJECT_PROMISOR_ONLY` (`packfile.c:2073-2074`);
   `.promisor` pack-marker semantics and `extensions.partialclone` are outside this anchor
   (`extensions.partialclone` parsed at `setup.c:622-626`, stored into
   `repository_format_partial_clone` at `setup.c:1813-1814`, only read here at lines 180–190).
6. **`--no-lazy-fetch` interaction.** `fetch_objects()` checks `NO_LAZY_FETCH_ENVIRONMENT` and
   returns -1 with `warning(_("lazy fetching disabled; some objects may not be available"))` at
   lines 34–41, before forking any transport. So the config still makes the repo promisor-backed
   while the existing isolation prevents network fetch; the source does not say what verdict an
   auditor should draw from a missing object.
7. **Version pin.** Behaviour is asserted for v2.56.0 only (the host version). No claim about
   earlier/later versions; no docs page was used to shore this up.

For r24 this licenses exactly: classify a filter-only remote as promisor-backed *metadata*, apply
the missing-evidence rule (required object unavailable → exit2; missing citation → exit2 unless
resolved locally elsewhere), and keep clean/omission verdicts for complete repositories. It does not
license a blanket exit2 on promisor metadata, which is the r23 harm the round is repairing.

## Existing SOURCES rows: new scope, not a reopened source

Observed in `corpus/SOURCES.md` (101 rows, max id S101):

- `rg -n "promisor-remote\.c" corpus/SOURCES.md` → **0 hits**. No row cites this file or this claim.
- S089 `git(1)` and S092/S099 `partial-clone` are git-scm.com **prose**, different URL and different
  evidence class. They teach lazy-fetch-on-missing-object, not config registration.
- S101 is the only prior **git source-code** row (`commit.c` `read_graft_line`); this row follows the
  same pattern but is a separate file and claim.

Classification: **new source row, no supersession.** Candidate row (S102) is written to
`out/SrcPromisorCode/SOURCES-candidate-row.md`; the registry was not edited. If L1 admits it, the
`used-by` should point at this report (and at `tools/report-landing-audit.py` only once the tool
actually consumes the key).

## Consequence observed in the current tree (observation, not a prescribed edit)

`tools/report-landing-audit.py:458-465` scans local config and refuses on
`extensions.partialclone` or on `remote\..+\.promisor` with a true boolean, plus the
`.promisor`+`.pack` pair check at lines 454–457. It has **no `partialclonefilter` match**
(`rg partialclonefilter tools/report-landing-audit.py` → no hits). A filter-only promisor lane is
therefore not classified as promisor-backed today, even though git does register the remote.

`tests/report-audit/repo-state-grid.py:482-498` (F27) already constructs that channel: it sets
`remote.origin.partialclonefilter=blob:none` with no promisor boolean and requires the lazy-fetch
marker at line 496; its expectation at lines 674–675 is exit 1 with `landed-unresolved` /
`unresolved-full-hash`. Under the preregistration's missing-citation rule, a promisor-backed lane
with an unresolvable citation is expected to become exit2 — that is a documented policy-row change,
not something this source alone decides.

Caveat: the binding of `remote.*.partialclonefilter` to the audit's classification is an inference
from the source, not measured here. F27's runtime marker is pre-existing r23 fixture evidence, not
this seat's measurement.

## Files left

- `out/SrcPromisorCode/promisor-remote.c.v2.56.0` — exact fetched bytes.
- `out/SrcPromisorCode/excerpt-config-callback.txt` — lines 122–180, numbered.
- `out/SrcPromisorCode/packfile.c.v2.56.0`, `setup.c.v2.56.0` — adjacent context for limit 5.
- `out/SrcPromisorCode/evidence.md` — provenance, hashes, excerpt.
- `out/SrcPromisorCode/SOURCES-candidate-row.md` — proposed S102 row (not applied).

## Unverified / not run

- No fixture was executed and no audit invocation was made; runtime lazy-fetch behaviour was not
  re-measured. The source reading is static.
- `git hash-object` integrity and GitHub API blob equality were checked; no build, lint, or suite.
- No installs or tool changes were made.

Report: .ufo/waves/round-24/build/advice/SrcPromisorCode.md
