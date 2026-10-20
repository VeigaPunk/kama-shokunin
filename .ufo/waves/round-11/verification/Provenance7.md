# Provenance7 — `corpus/knowledge/listener-census.md` provenance supplement review

**Scope:** kama round 11, seat Provenance7. Read-only semantic review of the appended
`## Provenance supplement — round 11 (2026-10-19)` block (`:384-387`) against the original
historical context (`:1-382`) and QUALITY KQ11 (`corpus/QUALITY.md:38`). No implementation,
corpus, or fleet file was modified; `measure.py` was not executed and no build/lint/test/
formatter ran. Paths are relative to `/home/vgpnk/Projects/shokunin/kama-shokunin/`.

**Target:** `corpus/knowledge/listener-census.md` — frozen baseline 34,489 B / 382 lines (last
line unterminated), current 36,460 B / 387 lines; delta +1,971 B, +5 content lines. Baseline
entry in `.ufo/waves/round-11/legacy-baseline.json`: `sha256
9366a759cbaecb9d8227cb50ce4082e507d824aa6f9b6c3b73b31e5836504996`, `bytes 34489`, `missing
["source","verified-at","recheck"]`.

## Verdict

The supplement is **honest on all four KQ11 admit conditions** — exact byte-prefix preservation,
historical dates identified, metadata review explicitly separated from live revalidation, and a
bounded recheck named — and it adds no observation, no runtime claim and no secret. Two
low-severity issues were found: one *inherited* stability-class inconsistency in the historical
context the recheck points at, and one *incomplete* description of what the named recheck tool
does on the wire. Neither is a KQ11 reject condition and neither is introduced by the append.

## Axes (as named, not scored)

1. **Calibration** (current `../shokunin.conf:52` kama row: operability + calibration) — does the
   supplement make the retained historical evidence explicitly sourced, dated and recheckable
   without fabricating freshness? This is the only axis the block touches.
2. **Operability** — not claimed and not advanced: the supplement asserts no listener, endpoint,
   readiness or serving state. No operability delta; no score change is proposed (a metadata-field
   count does not re-derive a 0–10 score, per `corpus/lessons/round-11.md` §Claims).

## What is already correct

1. **Byte prefix is exact, not merely "logically equal".** `head -c 34489
   corpus/knowledge/listener-census.md | sha256sum` → `9366a759…6504996`, identical to the frozen
   baseline and to the `HEAD` blob. The diff against
   `.ufo/waves/round-11/frozen/before/corpus/knowledge/listener-census.md` is a single EOF hunk
   (`382c382,387`); no mid-file insertion, no line-anchor shift. The original file ended without a
   newline and the append begins `\n\n## Provenance supplement…` (od confirms `\n \n # # …` at
   offset 34489), so the heading is genuinely column-zero rather than glued to line 382.
2. **Trio is structurally clean.** `source:`, `verified-at:`, `recheck:` occur once each, at
   column zero, at `:385`, `:386`, `:387`; no indented or duplicate occurrences. The file has 8
   ``` fences and the last closes at `:332`, before the supplement, so all three fields are
   outside fences as `measure.py` requires (`measure.py:144-175`).
3. **Source citations resolve exactly as written.**
   - `c6199a2542440db77d69918599e5a378ee116337` exists and is authored
     `2026-09-28T23:15:05-03:00` ("round-1: operability axis"), the same evening as the
     `:3` measurement (~22:47–22:52 -0300).
   - `ea72c3eae4ecc68dab2b0a08153c9c1d2e16df21` exists and is authored
     `2026-10-14T09:46:23-03:00` ("round-3: re-census"); its blob for this file is exactly
     34,489 B / `9366a759…`, equal to `HEAD` (`2f7303c`) and to the frozen baseline.
   - `§5` really is `C1–C19` (`:182-288`), `§7.1` really is a same-session re-check (`:323`), and
     `LOG.md:72` really records `KamaScoutListeners` "23-listener census … died after landing its
     artifact". `LOG.md:164-167` really contains "the round-1 23-listener census refreshed to 20
     due ephemeral socket churn" (`:165`), so the "observed 20 listeners" corroboration is in-range.
4. **Temporal separation is explicit and internally consistent.** Body dates are only
   `2026-09-28` (header/measurement) and `2026-10-14` (the re-measure notes); the supplement adds
   only the steered label `2026-10-19` and the actual review date `2026-10-20` (host UTC at review:
   `2026-10-20T03:46:01Z`). The line discloses that the 10-19 heading is a steered round label, and
   states "no live revalidation, no listener/endpoint probe, and no host config or environment read
   in this review". Nothing in the block offers the review date as refreshed runtime evidence, and
   `source: none` is not used. The live-claim guard wording ("no live revalidation") is a negation
   and would not trip `measure.py`'s bounded regex (`measure.py:126-140`).
5. **The recheck is correctly refused now and bounded later.** The block invokes KQ10
   (`corpus/QUALITY.md:32`) and round-10 Mistake 25 (`corpus/lessons/round-10.md:152`: "`listeners`
   outside checklist step 7's scope … stands") accurately, and SKILL checklist step 7
   (`SKILL.md:232-236`) is exactly that boundary. The named tool exists (`tools/kama-probe.sh`,
   `listeners` at `:88-90`, dispatch at `:1085`, enumeration at `:237`), uses `ss -ltnpH` with an
   unprivileged `-ltnH` fallback, contains no `sudo`, and documents `listeners` as non-gating
   (`:699`). The privileged `§7` one-liner (`:320-321`) quoted in the recheck is the same
   read-only command as the body, and the comparison rule ("stable by bind addr:port; churn by
   owner … never by port number") matches `§7` (`:314-319`).
6. **No credential or secret was added.** The body's own redaction note at `C9` is untouched; the
   supplement adds no config value, token or key.

## Findings by severity

### Low A (inherited — affects the recheck's basis, not the supplement's honesty)

The recheck line (`:387`) tells a future rechecker to "compare `stable` rows by bind addr:port", and
`§7` (`:314`) defines that set as `(34113, 8080, 8888, 8790, 8791, 4226, 43999, 631, 9222, 53×2)`.
But `§1` classifies `127.0.0.1:4226` (sccache) and `127.0.0.1:9222` (Chrome DevTools) as
**`session`** (`:54`, `:56`), not `stable`. Under the file's own SC definitions, `session` "dies
with the owning process", so those two rows do not belong in the `stable` reconciliation set.

Evidence: `corpus/knowledge/listener-census.md:314` vs `:54` and `:56`; the same inconsistency is
present verbatim in the frozen baseline (`frozen/before/...:314`), so it is **not** introduced by
this append and the byte prefix is unaffected.

Impact: a future recheck following `:314` would compare two session-owned listeners as stable by
addr:port. Practical harm is small (both ports are fixed by the owning process — 9222 by Chrome's
`--remote-debugging-port=9222` flag at `:56`, and 4226 as the observed sccache listener at `:54` —
and are still safe to compare by port), but the class label is wrong and the recheck's stated basis
inherits it.

**Smallest repair** (future corpus round, not this wave): align `:314` with `§1`
(`session` for 4226/9222, leaving both in the owner-comparison path), or, if the operator intends
fixed-port session listeners to count as `stable`, correct `:54`/`:56` instead. Do not edit the
supplement for this.

**KQ11 effect:** none — this is a defect in the retained historical context, not in the appended
provenance metadata.

### Low B (the named recheck under-describes the tool's wire behavior)

`:387` describes `bash tools/kama-probe.sh listeners` as "(repo tool, loopback `ss -ltnpH`,
unprivileged, no drift gate)". Those three attributes are true, but the subcommand does more than
enumerate sockets: `cmd_listeners` calls `classify` (`tools/kama-probe.sh:415-417`), which issues
`GET /v1/models` to `http://127.0.0.1:<port>` through `fetch` (`:285`) with `CONNECT_TIMEOUT=2`,
`TIMEOUT=5` (`:61-62`), and `loopback_ports` (`:259-278`) includes wildcard binds
(`0.0.0.0`, `::`, `*`) as `scope=wildcard`, not loopback only. So the recheck contacts each
loopback/wildcard port, bounded per port.

This is **not** a safety breach and **not** a false claim about the enumeration: the clause is
preceded by "revalidation requires a future L1-declared census scope", and SKILL step 7
(`SKILL.md:232-236`) explicitly authorizes `listeners` only as a census. It is an incomplete bound
description that could mislead a reader into treating `listeners` as a pure `ss` read.

**Smallest repair:** extend the parenthetical to, e.g., "(repo tool; unprivileged `ss -ltnpH`
enumeration plus one bounded `GET /v1/models` per loopback/wildcard port, 2 s connect / 5 s max;
census, not a readiness gate)". No change to the authorization gate is needed.

**KQ11 effect:** none — the recheck is still named, bounded and authorization-gated; this is a
precision fix.

### I1 (Informational — two-commit citation needs a precision note, not a repair)

`:385` cites `c6199a2 … and ea72c3e …` as the committed bytes. Both are real and dated as stated,
but only the `ea72c3e` (round-3) blob is 34,489 B / `9366a759…`; the `c6199a2` (round-1) blob is
34,326 B / `325ef7328cdea121b290a6a6495d811df9cc84835fe7943c20623848945fdb33`. The sentence does
not conflate them, and the hash is explicitly tied to the "round-11 baseline", so the citation is
honest; a checker should simply compare the prefix to the round-3 blob, not to every cited commit.
Optional precision edit only: name `ea72c3e` as the blob matching the 34,489-byte prefix.

### I2 (Informational — an unverifiable negative, consistent on its face)

"no host path, config, or endpoint was re-opened for this supplement" cannot be proven from the
repo. It is consistent with the artifact: the block adds only provenance metadata and recheck
instructions, with no new observation, counter, timestamped sample or endpoint output. Recorded as
unverifiable-by-construction; no repair.

## KQ11 clause check

| KQ11 clause | Result | Basis |
|---|---|---|
| Preserve the original byte prefix | **Pass** | `head -c 34489` SHA-256 equals the baseline; single EOF hunk; no rewrite |
| Identify historical observation dates (or unknown dates) | **Pass** | `:3` 2026-09-28 ~22:47–22:52 -0300, host `plazir27`; last in-file re-measure 2026-10-14; review 2026-10-20 disclosed as such |
| Distinguish metadata review from live revalidation | **Pass** | `:386` "metadata-only review … no live revalidation, no listener/endpoint probe, and no host config or environment read" |
| Name a bounded current recheck or explicit unavailable surface | **Pass** (with Low B precision) | `:387` on-authorization; future L1 census scope; real unprivileged tool + read-only privileged one-liner; stable-by-addr / churn-by-owner rule |
| Reject: field presence / correction date / `source: none` as refreshed runtime evidence | **Not triggered** | Review date is explicitly metadata-only; no freshness claim |
| Reject: obsolete config-body read revived as current recheck | **Not triggered** | Recheck uses a repo tool + `ss`, not a config body; authorization-gated |
| New knowledge entries open with the trio | **N/A** | Legacy file; append-only supplement is the prescribed path (`corpus/lessons/round-11.md` Mistake "reference-drift") |

Static prediction only (not executed): the file meets `measure.py provenance`'s predicates —
prefix hash, one column-zero occurrence of each required field outside fences, a column-zero
`## Provenance supplement` heading, and no today-dated "live revalidation" wording. The parent owns
the actual measurement.

## Retained evidence (commands run; read-only)

All executed in `kama-shokunin/`; no `measure.py`, build, lint, test or formatter was run.

```sh
sha256sum .ufo/waves/round-11/frozen/before/corpus/knowledge/listener-census.md \
          corpus/knowledge/listener-census.md
# 9366a759…6504996  frozen (34489 B)
# 9e4a36c9…e09491  current (36460 B)
head -c 34489 corpus/knowledge/listener-census.md | sha256sum
# 9366a759…6504996  ← exact baseline prefix
tail -c +34490 corpus/knowledge/listener-census.md | od -c | head -4
# \n \n # #   P r o v e n a n c e   s u p p l e m e n t …
diff <(frozen) <(current)   # single hunk: 382c382,387 (+5 content lines)
grep -n '^source:\|^verified-at:\|^recheck:' corpus/knowledge/listener-census.md
# 385 source: / 386 verified-at: / 387 recheck:  (one each, column zero)
grep -c '^```' corpus/knowledge/listener-census.md   # 8 (even; last closes :332)
git log -1 --format='%H %aI %s' c6199a2   # 2026-09-28T23:15:05-03:00 round-1
git log -1 --format='%H %aI %s' ea72c3e   # 2026-10-14T09:46:23-03:00 round-3
git show ea72c3e:corpus/knowledge/listener-census.md | sha256sum   # 9366a759… (34489 B)
grep -n 'KamaScoutListeners' LOG.md ; sed -n '164,167p' LOG.md
# :72 census landed; :165 "refreshed to 20 due ephemeral socket churn"
sed -n '1,383p' … | grep -o '2026-[0-9][0-9]-[0-9][0-9]' | sort | uniq -c
# 1 2026-09-28 / 3 2026-10-14   (no later body date)
date -u '+%Y-%m-%dT%H:%M:%SZ'     # 2026-10-20T03:46:01Z
grep -n 'sudo' tools/kama-probe.sh        # no matches
sed -n '237p;285p;415,417p;699p' tools/kama-probe.sh
# ss -ltnpH fallback / curl --connect-timeout 2 --max-time 5 / classify→fetch /v1/models / non-gating exit doc
```

## Risks and blockers

- No blocker. Both findings are advisory precision/consistency items; neither reverses admission
  of this supplement and neither changes KQ11 status.
- Integration note for the parent: if a later corpus round repairs Low A, the change belongs in
  `§7`/`§1` of the historical body, not in the supplement, and would then break the frozen-prefix
  invariant by design — it must be handled as a new revision with its own baseline, not as part of
  the round-11 append.
- This review is author-side advisory only; outside non-author review remains a separate step.

## Installs / updates

None. No tool was installed, upgraded or invoked through any package channel; no external URL was
needed or opened for this seat. The only writes were this report file.
