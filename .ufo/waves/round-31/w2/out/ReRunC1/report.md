# ReRunC1 — fresh-clone re-run of the frozen C1 counter at the dispatch tip

## RESULTS

```
$ mkdir -p /tmp/kama-r31w2/ReRunC1 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/ReRunC1 && git clone --no-hardlinks --quiet /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r31w2/ReRunC1/lane && git -C /tmp/kama-r31w2/ReRunC1/lane checkout -q 382d11b2107d335705875da1a4d889b074bd6fa6 && echo "CLONE_OK" && sha256sum /tmp/kama-r31w2/ReRunC1/lane/.ufo/waves/round-31/count-c1.py && git -C /tmp/kama-r31w2/ReRunC1/lane rev-parse HEAD && git -C /tmp/kama-r31w2/ReRunC1/lane log --oneline -1; echo "EXIT_CODE=$?"
CLONE_OK
d86c4a94b9a464a9aa6212b2958c72229b7134eb440f64edab70de090d924216  /tmp/kama-r31w2/ReRunC1/lane/.ufo/waves/round-31/count-c1.py
382d11b2107d335705875da1a4d889b074bd6fa6
382d11b round-31: SOURCES repair — S180-S191 relocated into ## Registry (census E12 exit 1 -> exit 0), lesson Mistakes row 4, census start/end receipts, two late seat artifacts
EXIT_CODE=0

$ /usr/bin/python3 .ufo/waves/round-31/count-c1.py --lane /tmp/kama-r31w2/ReRunC1/lane --repo /tmp/kama-r31w2/ReRunC1/lane --tip 382d11b2107d335705875da1a4d889b074bd6fa6 --out /tmp/kama-r31w2/ReRunC1/c1.json; echo "EXIT_CODE=$?"   # cwd = /tmp/kama-r31w2/ReRunC1/lane
registered 18 counted 17 target 12 met True not-counted ['K31-10']
EXIT_CODE=0

$ cp /tmp/kama-r31w2/ReRunC1/c1.json /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/ReRunC1/c1.json && sha256sum /tmp/kama-r31w2/ReRunC1/c1.json /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/ReRunC1/c1.json
6b58b4340886f602fd5e2a2f2795d4e7abf50dad9252d033c41050beba80331e  /tmp/kama-r31w2/ReRunC1/c1.json
6b58b4340886f602fd5e2a2f2795d4e7abf50dad9252d033c41050beba80331e  /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/ReRunC1/c1.json

$ /usr/bin/python3 -c "import json;d=json.load(open('/tmp/kama-r31w2/ReRunC1/c1.json'));c=[r['id'] for r in d['rows'] if r['counted']];n=[r['id'] for r in d['rows'] if not r['counted']];print('summary_repr:',repr(d['summary']));print('per_row:',[(r['id'],r['counted']) for r in d['rows']]);print('counted_ids:',c);print('derived_not_counted:',n);print('field_not_counted:',d['not_counted']);print('complement_equals_field:',sorted(n)==sorted(d['not_counted']));print('counted_len:',len(c));print('k31_05:',json.dumps([r for r in d['rows'] if r['id']=='K31-05'][0],indent=1))"
summary_repr: "registered 18 counted 17 target 12 met True not-counted ['K31-10']"
per_row: [('K31-01', True), ('K31-02', True), ('K31-03', True), ('K31-04', True), ('K31-05', True), ('K31-06', True), ('K31-07', True), ('K31-08', True), ('K31-09', True), ('K31-10', False), ('K31-11', True), ('K31-12', True), ('K31-13', True), ('K31-14', True), ('K31-15', True), ('K31-16', True), ('K31-17', True), ('K31-18', True)]
counted_ids: ['K31-01', 'K31-02', 'K31-03', 'K31-04', 'K31-05', 'K31-06', 'K31-07', 'K31-08', 'K31-09', 'K31-11', 'K31-12', 'K31-13', 'K31-14', 'K31-15', 'K31-16', 'K31-17', 'K31-18']
derived_not_counted: ['K31-10']
field_not_counted: ['K31-10']
complement_equals_field: True
counted_len: 17
k31_05: {
 "id": "K31-05",
 "counted": true,
 "reasons": [],
 "live": {
  "status": 400,
  "error_keys": [
   "code",
   "message",
   "type"
  ],
  "message": "top_logprobs requires logprobs to be set to true",
  "type": "invalid_request_error",
  "code": 400
 }
}
```

## FINDING:
Fresh-clone re-run at 382d11b2107d335705875da1a4d889b074bd6fa6 reproduces attempt 1's frozen C1 reading exactly — stdout `registered 18 counted 17 target 12 met True not-counted ['K31-10']`, exit 0, receipt `summary` identical to stdout; counter bytes sha256-identical to the frozen pin (d86c4a94…). Per-row `counted` is True for K31-01..09 and K31-11..18, False for K31-10; an independent one-line derivation over the receipt gives counted 17 / not-counted `['K31-10']`, which equals the receipt's `not_counted` field (complement check True). The K31-05 live block shows the exact `{code,message,type}` envelope the SKILL table claims (SKILL.md row `K31-05 | top_logprobs | 3 | reject 400 invalid_request_error: top_logprobs requires logprobs to be set to true`): key set exactly `[code, message, type]`, `code` 400 equals the observed HTTP status 400, `type` `invalid_request_error`, `message` byte-identical to the claimed string. The counter reading is reproducible; consistent with the wave-1 no-op control (`.ufo/waves/round-31/w1/out/CriticClaimSize/c1-noop.json`, 12 duplicate `n_predict` rows → `counted 12 met True`), `met True` here remains met-on-counter and is not, by itself, an improvement claim.

## LIMITS:
- One fresh run, one host, one run-time free port; the counter sha256-pins binary/library/model (server b6a31a8e…, model 270cba1b…, per registry `build`) but this seat does not establish reproducibility beyond this single re-run or across hosts.
- This run validates the counter's mechanics and reproducibility only; it cannot distinguish counted rows that prove something from counted rows that prove nothing (the w1 `CriticClaimSize` no-op control and `RevCounterFair` F1/F2 classes still stand against C1's admission).
- Integrity claim is byte-identity of the counter to the frozen sha256; I did not re-derive the counter's logic, and the receipt's `live` block holds the counter's parsed fields (status, error key set, message, type, code), not the raw HTTP body.
- Not independently re-checked by this seat: the other 17 rows' live blocks, the SKILL cell text for rows other than K31-05, and the source-snapshot substring checks (the counter performed them; my run reports only its outputs).
- No tools were installed or upgraded for this seat (nothing needed beyond /usr/bin/python3, git, cp).

## Artifacts
- `c1.json` — raw counter receipt (sha256 6b58b4340886f602fd5e2a2f2795d4e7abf50dad9252d033c41050beba80331e), copy of `/tmp/kama-r31w2/ReRunC1/c1.json`.
- `c1.stdout.txt` — verbatim stdout of the counter run.
- Scratch clone preserved at `/tmp/kama-r31w2/ReRunC1/lane` (read-only use; no lane file, tracked or clone-local, was edited).
