VERDICT: confirm - all 11 committed receipts agree; training context is captured.

## Reconstructed contract
Observed receipt values at `HEAD 37bd4c5bd456a2f8a54d3312c28495c321715856`:

| Committed receipt group | Count | Root `ctx`; argv context; `--parallel` | Served `/props` `n_ctx`; `total_slots` | `model_alias`; `/v1/models` `n_ctx_train` |
|---|---:|---|---|---|
| R16 `live/receipt*.json` (`receipt.json`, `receipt-frozen-probe.json`) | 2 | `256`; `-c 256`; absent | `256`; `4` | `kama-stories260k`; `2048` |
| R17 `live/receipt-1..3.json` | 3 | `256`; `-c 256`; absent | `256`; `4` | `kama-live-probe`; `2048` |
| R18 `live/receipt-1..3.json` | 3 | `256`; `-c 256`; absent | `256`; `4` | `kama-r18-live`; `2048` |
| R18 `live-recovery/receipt-1..3.json` | 3 | `256`; `-c 256`; absent | `256`; `4` | `kama-r18-live`; `2048` |
| R19 matching receipts | 0 | — | — | — |

Across all 11, `.captures.props.fields` has exactly these keys: `build_info`, `default_generation_settings.n_ctx`, `is_sleeping`, `model_alias`, `total_slots`. Their values are respectively `b11755-704366d76`, `256`, `false`, the alias in the table, and `4`. `--ctx-size` is not spelled out in argv; the context option is its short spelling `-c 256`. No receipt argv contains an explicit `--parallel` option.

**Training context:** yes, captured in `.captures.models.body` (the `/v1/models` response), as `.data[0].meta.n_ctx_train = 2048` in every receipt. It is not among the selected `/props` fields. Both model-body truncation flags are `false` in all 11 receipts.

Observed relation: every receipt has root `ctx = 256`, argv `-c 256`, and `/props` `default_generation_settings.n_ctx = 256`; `total_slots` is consistently 4. [INFERENCE] This population demonstrates equality for the observed configuration, not a general scaling rule: it has no context-size or explicit-parallel variation, and `total_slots=4` alone does not prove a `--parallel=4` launch argument.

## Evidence and confidence
The committed-tree inventory at the stated HEAD returned 11 `receipt*.json` paths (R16=2, R17=3, R18=6, R19=0), exit 0. The committed-record extraction used `git show HEAD:<path>` and jq; all records parsed. Representative source: R16 `live/receipt.json` at this revision has `"-c", "256"` in `argv` (lines 13–14), `"default_generation_settings.n_ctx": 256` in `.captures.props.fields` (lines 62–68), and root `"ctx": 256` (line 199). Its captured `/v1/models` body includes `"n_ctx_train":2048` (line 43); all-receipt jq parsing below independently returned 2048 with both truncation flags false. Confidence: high for these receipt observations; no extrapolation to other launch settings.

## Reproducible jq commands
Run from the repo root; the output rows were condensed into the table above. Each command exited 0.

```sh
jq -r '[input_filename, (.ctx|tostring), (.argv as $a | ([range(0;($a|length)) as $i | select($a[$i]=="-c" or $a[$i]=="--ctx-size") | "\($a[$i]) \($a[$i+1])"] | first) // "absent"), (.argv as $a | ([range(0;($a|length)) as $i | select($a[$i]=="--parallel") | "\($a[$i]) \($a[$i+1])"] | first) // "absent"), (.captures.props.fields|keys|join(",")), (.captures.props.fields["default_generation_settings.n_ctx"]|tostring), (.captures.props.fields.total_slots|tostring)] | @tsv' .ufo/waves/round-16/live/receipt*.json .ufo/waves/round-17/live/receipt*.json .ufo/waves/round-18/live/receipt*.json .ufo/waves/round-18/live-recovery/receipt*.json
# exit 0; 11 TSV rows
jq -r '[input_filename, (.captures.models.body_truncated|tostring), (.captures.models.body_read_truncated|tostring), (.captures.models.body|fromjson|.data[0].meta.n_ctx_train|tostring)] | @tsv' .ufo/waves/round-16/live/receipt*.json .ufo/waves/round-17/live/receipt*.json .ufo/waves/round-18/live/receipt*.json .ufo/waves/round-18/live-recovery/receipt*.json
# exit 0; 11 TSV rows, each false / false / 2048
jq -r '[input_filename, (.captures.props.fields|tojson)] | @tsv' .ufo/waves/round-16/live/receipt*.json .ufo/waves/round-17/live/receipt*.json .ufo/waves/round-18/live/receipt*.json .ufo/waves/round-18/live-recovery/receipt*.json
# exit 0; 11 TSV rows
```
