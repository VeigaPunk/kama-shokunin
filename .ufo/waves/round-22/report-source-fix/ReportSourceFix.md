# ReportSourceFix — round 22

Seat: `ReportSourceFix`; implementation only in the assigned sandbox clone and its `out/` witness artifacts. This is a distinct follow-up, not a replacement for another seat. The canonical lane source and fleet report were not edited.

## Changed files

1. `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-22/report-source-fix/ReportSourceFix/clone/tools/report-landing-audit.py`
2. `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-22/report-source-fix/ReportSourceFix/out/red-green-witness.py`
3. `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-22/report-source-fix/ReportSourceFix/out/red-green-fixture.json`
4. `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-22/report-source-fix/ReportSourceFix/out/fixtures/census-report.md`
5. This handoff: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-22/report-source-fix/ReportSourceFix.md`

## Patch

The auditor now loads `corpus/SOURCES.md` from the selected committed `--branch` tree: `ls-tree` distinguishes an absent legacy file (no exemptions) from a Git failure, then an explicit `cat-file blob` reads a regular committed blob. Non-regular entries and decoding/Git failures become `EvalError`; the worktree copy is never consulted.

The source census is deliberately narrow and mirrors its row walk: only `## Registry`, a structurally 11-column S-row (`S[0-9]{3,}`), and the **first** HTTPS URL in its source cell can contribute a URL form. It records the exact full URL and census-normalized form (fragment removed, one trailing slash removed, scheme stripped, host lowercased). Matching uses explicit left/right URL boundaries; arbitrary URLs, malformed-width rows, non-S rows, and URLs under `## Leads` do not qualify. There is no hash/repository whitelist or network lookup.

`FULL` matches are classified by occurrence span, not by token value. A match is exempt only inside one of those exact URL occurrences and outside the `## Landed changes` body. A bare copy of the same hash remains unresolved; full scanning in Landed remains unchanged. Existing `ABBREV`, Landed resolution/omission, and errata logic are untouched. Each JSON report result gains `source_url_hashes` to make URL classification visible without presenting it as source-validity proof.

The auditor selftest retains its original splice/full-hash and omission assertions and adds isolated cases for absent registry, full URL, census-normalized URL, same bare hash, unregistered URL, malformed row, Leads, left/right/scheme boundaries, worktree-only row, and a source URL in Landed (which still produces full-hash and Landed findings).

The prepared witness's central expected comparison is:

```text
old cc9f8d3: exit 1; unresolved-full-hash 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad
candidate:  exit 0; no defects; source_url_hashes=[704366d76f8748cf9ad3df62a464bfcc8d1ae6ad]
```

`red-green-witness.py` retrieves and verifies the old script, registry, and census-output blobs from the local clone, then builds one temporary synthetic lane and fleet with the same committed report for both CLI runs. It asserts the report embeds the pinned census stdout bytes. All Git writes and the temporary old-script file are under its temporary directory; it does not write to the actual lane or fleet. This witness was prepared, **not run**.

## Retained evidence and pins

- Base lane revision observed: `cc9f8d316358e13aa094cdb07714771a009805e9`.
- Old auditor at that revision: blob `d8af6b38036905670cd7eb64ffcb7669ff1b5c50`, SHA-256 `80a588257fce8e436f39bcf0b59a473f4537eaeb4f06442a14b027dd7bed9808`.
- Committed `corpus/SOURCES.md`: blob `14ea0501b9fae159681d2ca0a55765a7a02f357a`, SHA-256 `44ff346bf16d5c382b94775ee918b9e65f77e6ad4315542641e8697188d058a9`.
- Retained `fr-sources-validate.stdout`: blob `ec8a1c80d1d081c216f9991b955359cb0114532e`, SHA-256 `cf5f3cb576ab68a45f415e62c6a45b784bbf81ae2071edd380b545de900347b3`. The recorded output has the 40-hex hash inside the S043, S056, and S060 census-form URLs.
- Static report fixture SHA-256: `b10a77b2fda921c75244ce97a75df2f6d52e7482d848fd685f9e17b058a87948`. Manifest SHA-256: `499442f137f69e0af93aa8d76e706e15e61d2cb6e632df98992d281cd0794d6b`. Witness runner SHA-256: `ac3bb57eac7666a4ba4bfb16b1ad3a69b9c5eee5afd35eb80bbbaccd577b9a3c`.
- Candidate auditor SHA-256 in the sandbox clone: `543e2d00eeaca810dfbebb1cc4384f48fd2c81e4571ad6bc6cffa47e0b560c61`.
- The task handoff reports that `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad` is missing from both actual repositories. I did **not** rerun either prohibited `cat-file` lookup.
- Existing C1 evidence remains the committed `6433390a` record in `corpus/lessons/round-22.md` (`29/29`); no helper claim, receipt, or historical command evidence was changed.

## Proposed L1 commands — not run here

From any working directory, run the isolated selftest and pinned comparison:

```sh
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-22/report-source-fix/ReportSourceFix/clone/tools/report-landing-audit.py --selftest
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-22/report-source-fix/ReportSourceFix/out/red-green-witness.py
```

After integration, run the historical audit with the existing errata ledger, then the round-22 draft audit when that absolute report path exists:

```sh
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/report-landing-audit.py --lane-repo /home/vgpnk/Projects/shokunin/kama-shokunin --fleet-repo /home/vgpnk/Projects/shokunin --rounds 10- --json
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/report-landing-audit.py --lane-repo /home/vgpnk/Projects/shokunin/kama-shokunin --fleet-repo /home/vgpnk/Projects/shokunin --branch master --rounds 22 --report 22=/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/reports/round-22/kama.md --no-errata --json
```

## Risks and execution boundary

This is type classification from a committed curated source URL, not proof that upstream bytes exist, are trustworthy, or match a claim. It stays within the assigned trusted lane/fleet scope and adds no D4/untrusted-repository guarantee. No network or external state was touched. No build, lint, formatter, selftest, audit, or witness was run; L1 owns those checks. No tool was installed. The supplied tool inventory had no LSP client, so symbol/call-site review used repository reads and search instead.

Boundaries are intentionally conservative: a trailing sentence period or URL
continuation outside the explicit delimiters remains unresolved rather than
being exempted. The additive JSON `source_url_hashes` field may affect any
consumer that assumes an exact result-key set.

One read observation was issued early against the actual lane: `git status --porcelain -- tools/report-landing-audit.py` returned empty. No explicit stage/commit/reset/index-write command was issued there. Git status may refresh index stat metadata; I did not inspect or restore the lane index under the no-index-edit restriction.

## L1 integration addendum (before verification)

The canonical auditor now contains the candidate plus a stricter common URL
left boundary and a full-URL-inside-another-URL negative case. The now-unused
`landed_section` wrapper was removed; maintained heading tests call
`landed_match` directly. This is a clean private-helper cutover, not a shim.

The witness now reads pinned objects and the current candidate from the real
lane read-only, rather than depending on the disposable executor clone.
It pins the manifest digest in code, exposes a CLI selftest with
positive/tamper/missing/genuine-mismatch/child-error controls, and refuses to
interpret an auditor's exit2 as a completed verdict. The earlier candidate
and witness hashes above identify the handed-off proposals, not the final
shipping source; measured hashes will be in the actual run.

The report draft path in the proposed command above was misrooted to the
lane's `.ufo/reports/`: the required actual path is
`/home/vgpnk/Projects/shokunin/.ufo/reports/round-22/kama.md` on the fleet repo.
No report was written at the wrong path. The duplicate clone is removed after
retaining the patch; the out/fixture and canonical code remain runnable.
