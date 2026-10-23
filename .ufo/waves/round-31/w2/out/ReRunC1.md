# ReRunC1 — scoped findings (round 31, wave 2, attempt 2)

Claim served: C1 (depth) — fresh-clone re-run of the frozen counter at the dispatch tip.

## FINDING
Reproduced exactly. Fresh `git clone --no-hardlinks` of the lane checked out at `382d11b2107d335705875da1a4d889b074bd6fa6`; counter bytes verified `sha256 = d86c4a94b9a464a9aa6212b2958c72229b7134eb440f64edab70de090d924216` (frozen pin). Counter run from the clone root, exit 0, verbatim stdout:

`registered 18 counted 17 target 12 met True not-counted ['K31-10']`

Per-row `counted` from the receipt: True for K31-01..09 and K31-11..18 (17 rows), False for K31-10. Independent one-line derivation over the receipt (`[r['id'] for r in rows if r['counted']]` / `if not r['counted']`) yields counted 17 and not-counted `['K31-10']`, equal to the receipt's `not_counted` field (complement check: True). K31-05 live block: `{"status": 400, "error_keys": ["code","message","type"], "message": "top_logprobs requires logprobs to be set to true", "type": "invalid_request_error", "code": 400}` — the exact `{code,message,type}` envelope the SKILL table row claims (`reject 400 invalid_request_error: top_logprobs requires logprobs to be set to true`, SKILL.md line 1251): key set exact, `code` equals the HTTP status, `type` and `message` byte-identical.

This is advisory evidence, not a verdict: `met True` reproduces the counter reading at the tip and nothing more; the wave-1 no-op control (`.ufo/waves/round-31/w1/out/CriticClaimSize/c1-noop.json`) and `RevCounterFair` F1/F2 classes remain the open defects against C1's admission as an improvement.

## Evidence
- Receipt (raw, sha256 `6b58b4340886f602fd5e2a2f2795d4e7abf50dad9252d033c41050beba80331e`): `.ufo/waves/round-31/w2/out/ReRunC1/c1.json`
- Verbatim stdout: `.ufo/waves/round-31/w2/out/ReRunC1/c1.stdout.txt`
- Full command log with exit codes: `.ufo/waves/round-31/w2/out/ReRunC1/report.md`

## LIMITS
- One re-run on one host; single-run reproducibility only (counter pins binary/library/model by sha256 itself).
- Does not adjudicate counted-row meaningfulness (no-op registry still meets the target); integrity claim is byte-identity of the counter, not a re-derivation of its logic.
- Live blocks hold the counter's parsed fields, not raw HTTP bodies; only K31-05's envelope was checked against SKILL, not the other 17 rows.
- No tools installed for this seat.
