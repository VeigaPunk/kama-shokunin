VERDICT: holds — each committed *.error-lines.jsonl is byte-identical (sha256-equal) to an independent re-extraction of the errorMessage lines from the transcript README.json names, the three seats are exactly the ones the round-26 spot-check names, and the error text supports the '429 quota' claim.

Reviewer: ReviewRepairD4Bytes (KamaR27A3 w1a3), 2026-10-23. Repo tip read: master @ 324d5d62e61276af312c8eb42f678004aec245d1. Target: `.ufo/waves/round-27/repairs/d4-r26-dead-seat-errors/` (README.json + exactly 3 `*.error-lines.jsonl`, no extra files).

## Method (independent of the author's extraction)

- Transcript re-hash: `sha256sum` + byte count of each transcript path in README.json (host: `/home/vgpnk/.omp/agent/sessions/-Projects-shokunin/2026-10-23T00-54-50-959Z_01a16640-e34f-76e4-8a3b-4d245a8bb241/KamaR26/`), compared to README `transcript_sha256`/`transcript_bytes`.
- Independent line extraction (eval py kernel): read each transcript as bytes, `json.loads` every JSONL line, select lines whose parsed object contains an `errorMessage` key **anywhere in the structure** (recursive key check, not substring match), rejoin with `\n` + trailing newline, sha256. Compared to the committed file bytewise and by hash.
- Committed-file hashes cross-checked with `sha256sum` in bash (independent of the Python path): `d8e038b0…, 07ba70ca…, 48930331…` — identical.
- Quota-text probes: substring checks on the parsed `errorMessage` of each committed file.

## Per-seat results

| seat | transcript sha256 (== README) | transcript bytes (== README) | error lines (== README) | extracted sha256 == committed == README `error_lines_sha256` | byte-identical |
|---|---|---|---|---|---|
| KamaR26CtlDoNothing | `72849087aa605080d78d09b9ecffb11255b36bfcde5e558fd46ece86fadd2c4b` ✔ | 40446 ✔ | 1 ✔ | `d8e038b0852a91774af38772479ef97491ce95ae2effab9d9007a0d043601b09` ✔ | True |
| KamaR26CtlJunk | `1dd04f2fff28b7276078928d6c786ec7047028ea4113c5e88e7a17fbd82f3e76` ✔ | 40667 ✔ | 1 ✔ | `07ba70cab3c2a9dd1503ca4e7c5fb94388eed9073e61bd68cb6c908e83697932` ✔ | True |
| KamaR26CtlNoReader | `5fd458de712058edc80c2e4d6b7aea97687b941c125bb00276302192f37b75` ✔ | 41501 ✔ | 1 ✔ | `4893033180694c4ac5b8b1b8ab95cfa970021c3940a6b79963e07c830c4fde6e` ✔ | True |

Exit codes: `sha256sum`/`wc` pipeline exit 0; extraction script ran clean (no unparsable lines).

## Seat set matches the spot-check

`corpus/lessons/round-26-verifier-spotcheck.md:236` (routed defect 4): "Commit the raw provider error bytes for dead seats. The 429 deaths of KamaR26CtlDoNothing, KamaR26CtlJunk and KamaR26CtlNoReader are self-asserted only." — exactly the three seats repaired; README.json:2 cites the same defect pointer. No fourth seat or extra artifact in the directory.

## '429 quota' text support

Each committed line parses to a message with `stopReason:"error"`, `provider:"google-antigravity"`, `model:"gemini-4-argon"`, and an `errorMessage` (748–749 chars, complete — ends in a `RetryInfo` block and closing braces) containing all of:

- `Cloud Code Assist API error (429)` and `"code": 429`
- `"message": "Individual quota reached. Please upgrade your subscription to increase your limits. Resets in 59h6m2…s."`
- `"status": "RESOURCE_EXHAUSTED"`, `"reason": "QUOTA_EXHAUSTED"`, domain `cloudcode-pa.googleapis.com`
- quota metadata `"model": "gemini-4-argon-high"`, `"quotaResetTimeStamp": "2026-10-25T14:27:28Z"` (plus RetryInfo `retryDelay` ≈ 212782–212784 s)

This supports round-27 lesson §Repairs item 4 ("429 `RESOURCE_EXHAUSTED`, gemini-4-argon-high, reset 2026-10-25T14:27:28Z") in every field.

## Residual risk / verification gaps

- The transcripts live only on this host under `~/.omp/agent/sessions/` and are not committed (README: they hold seat prompts); re-verification is host-scoped and assumes the session files were not edited after extraction. I verified today's bytes match README's recorded hashes, which is the strongest check available without committing the transcripts.
- README.json's `errors[].errorMessage` display strings are truncated at "RetryI…" — display-only; the committed jsonl files are complete and are the repair artifact.
- Byte-identity proves the committed lines are faithful copies of the transcript, and the transcript records the provider's 429 payload; it cannot prove the 429 itself was genuine provider output rather than a crafted transcript. That is inherent to defect 4's repair shape (the spot-check asked for raw bytes + hashes, which is what was delivered).

No tool installs performed. No servers started, no jj/git writes.
