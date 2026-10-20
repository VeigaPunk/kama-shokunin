VERDICT: partial — v2 re-derives its 11 runtime checks, but source-span metadata is not gate-validated and four current bindings lack registry ids.

# Round-17 source-span binding: scope and handoff

## Axes

Round 17 declares **calibration** (lowest assigned, 7) and **operability** (8) as its axes (`/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-17.md:6-8`). This scoped proposal targets calibration while preserving the v2 live-check set and runtime behavior (`/home/vgpnk/Projects/shokunin/kama-shokunin/SCORECARD.md:645-681`).

## Evidence and contested scope

- The producer emits one source-binding record per cited span, with `check`, `row`, pinned commit, path/URL, line range, whole-file digest, literal span text, and SHA-256 of that text (`/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py:834-938`). The digest is computed from UTF-8 `span_text`; this binds the recorded text to its own digest, not by itself to upstream source bytes.
- At the landing commit, the five bindings are one S036 binding plus four with `row: null`: the health span and three teardown spans pass `None` to `_binding`; only the loading span names S036 (`/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py:866-938`). The receipt carries the same null row values (`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/live/receipt-1.json:437-513`). The lesson explains the historical cause: “the rows did not exist when the tool was written” (`/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-17.md:74-79`), while S042 and S043 now exist (`/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md:54-55`). Thus old receipts should remain historical, but a fresh receipt from this producer would still omit those now-available row links.
- The receipt gate documents and enumerates exactly 11 v2 check ids (`/home/vgpnk/Projects/shokunin/kama-shokunin/tests/llamacpp-live/check-receipt.py:28-36,80-92`). A targeted source/span search of that gate returned no matches: it does not validate `source_binding`. The build-wave gate advice explicitly records that the proposed source-binding obligation was “NOT implemented here: out of this item's scope” and that the v2 check-id set was fixed (`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/build/advice/C2ReceiptGate.md:37`). This is a separate provenance gap, not evidence against the measured lifecycle checks.
- Kaidoku's citation conventions are compatible only within their stated limits. Its quality bar requires “one contiguous passage” with the actual section locator (`/home/vgpnk/Projects/shokunin/kaidoku-shokunin/corpus/QUALITY.md:26-27`); it also says to “check the appropriate source manually under #1” for code members and commit objects (same lines). A `span_sha256` and byte-contiguous locator are useful integrity metadata, but they do not establish that the quote is authentic, complete, or semantically sufficient.

## What to retain vs hand off

- **Kama retains** upstream source research, `SOURCES.md` row stewardship, and the receipt's `source_binding` contract. Kaidoku explicitly says “Anti-trigger: ordinary source repositories — use normal repo tools, never run REA on available source” (`/home/vgpnk/Projects/shokunin/kaidoku-shokunin/SKILL.md:3`); its province calls source-available reconstruction of ordinary repositories unowned (`/home/vgpnk/Projects/shokunin/kaidoku-shokunin/PROVINCE.md:106-107`). Do not hand kaidoku raw-source citation validation or import its prose quote-fidelity instrument as a code-span validator.
- **Hand off only a shipped-binary question**—for example, whether a specifically pinned `llama-server` ELF corresponds to or implements the cited source—to kaidoku's native-ELF analysis surface (`/home/vgpnk/Projects/shokunin/kaidoku-shokunin/PROVINCE.md:48`). That handoff must include the absolute executable path and stable SHA-256 required by kaidoku's artifact identity criterion (`/home/vgpnk/Projects/shokunin/kaidoku-shokunin/corpus/QUALITY.md:13-18`). The present source bindings do not establish source-to-binary correspondence. [INFERENCE]

## One bounded move

Add an **offline source-binding audit alongside the receipt gate, not as a twelfth `checks[]` id**. Keep the v2 lifecycle contract and v1 compatibility unchanged. For subsequent receipts, change the producer's existing `None` values to S042/S043 where those rows cover the predicate; never rewrite the already-issued receipts. The audit should verify metadata shape, `sha256(span_text)`, pinned commit/path/URL/line-range consistency, and—when a row is present—the row-to-file-digest association. Report `row: null` as unresolved provenance, not as a failed lifecycle observation. Add red controls for a changed span with stale hash and a mismatched row/path/digest.

This is the compatible synthesis of the producer's in-receipt spans and the gate proposal deferred for the fixed 11-id contract. It improves **calibration** by making citation-field corruption detectable without adding a runtime operation, changing the measured check set, or claiming that a hash proves source semantics. Exact correspondence to upstream code and semantic support remain manual source-review obligations; an all-fields-recomputed forged record could still pass a metadata-only audit. Do not label that audit a source-authenticity or binary-correspondence verdict.

## Verification to request

1. Run the new audit on all three existing v2 receipts: lifecycle gate results remain unchanged; null-row bindings are reported as unresolved, not silently promoted to verified.
2. Run audit self-tests: correct S036/S042/S043 bindings pass; stale span hash and row/path/file-digest mismatch controls fail with the named clause. Check that no new `checks[]` id is introduced.
3. In the required scratch clone, re-run `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/llamacpp-live/check-receipt.py --selftest`, validate the two round-16 v1 receipts and all three absolute receipt paths under `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/live/`, and run `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/llamacpp-live/controls.py` against frozen/current tool+gate. No live server is required for this metadata-only change.
4. Manually compare each claimed code span against the raw file at its pinned commit before describing the citation as source-supported. If binary/source correspondence is requested, route the pinned ELF and digest to kaidoku; otherwise leave that relationship unknown.

## Commands, limitations, installs

- `rm -rf /tmp/ConnectKaidoku-3-clone && git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/ConnectKaidoku-3-clone && git -C /tmp/ConnectKaidoku-3-clone checkout -q 54a29268e2083caa2b1e0d54ee1e7d90961302f3 && echo CLONE_OK` — exit 0 (`CLONE_OK`).
- `git -C /tmp/ConnectKaidoku-3-clone rev-parse HEAD && rm -rf /tmp/ConnectKaidoku-3-clone && echo SCRATCH_REMOVED` — exit 0; printed the assigned landing commit and `SCRATCH_REMOVED`.
- Inspected the specified kaidoku `SKILL.md`, `PROVINCE.md`, and `corpus/QUALITY.md`, and the kama landing using read/grep tools. The receipt-gate source/span search returned no matches. No tests, gates, live server, network fetch, or binary analysis were run. No installs.
