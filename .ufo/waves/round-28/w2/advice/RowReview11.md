# Round 28 W2 — F28-21 / F28-22

**Verdict: partly.** The live outcomes and source records hold; both prose cells over-generalize an upper-overflow fixture as “beyond the float range” without distinguishing the lower edge. Both rows are correctly excluded from the A1 count as generic conversions, so neither contributes evidence toward C1's target.

## Live re-measurement

Used the counter's body serialization and request shape (`count-c1.py:333-340, 584-595`), on assigned port 48311: POST `/completion` with `{"prompt":"Once upon a time","n_predict":1}` plus the row's `1e+39` value; separately sent the field-omitted base. Runtime identity was checked: pinned executable SHA-256 `b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804`, pinned mapped library SHA-256 `e404b91a81c9ab65756b6a57b97b42115a5f429c5060c4b7f0d717ca595b59ed`, pinned model SHA-256 `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`; clean counter environment and `/props` model path matched. After stopping the process group, `ss -ltnp '( sport = :48311 )'` showed no listener.

| Row | Field-set request: status, effective, response SHA-256 | Field-omitted base: status, effective, response SHA-256 |
|---|---|---|
| F28-21 | 200; `mirostat_tau = 3.4028234663852886e+38`; `7e4c80584716fd8d553770eec9fd049ed0934cb8176f0133aa2e38c61faffc2e` | 200; `5.0`; `e89d63c5291851a28736daa7e025177a70cf6a4c45a250691fabd5c58afbd02a` |
| F28-22 | 200; `mirostat_eta = 3.4028234663852886e+38`; `ec2d0863a6ca5d69526e9cabc0ca76ea0df6b28a92d101a1c71b7d1550990d0f` | 200; `0.10000000149011612`; `ee21897c3a95445958b5f316464b78f8d81b5b70d358c37c2f1f77b744120a2c` |

To test the prose's unqualified “beyond” claim, also sent `-1e+39`: both fields returned 200 but stored `-3.4028234663852886e+38` (tau response SHA-256 `9f73b588e73a185ceb2e87a739a34546c55b92623605cb9adc2a35e76d557e66`; eta `f9e617776f6ae78d09b669246058bfa5fc19679347ec749c7dba39d4a26ed049`). Thus the lower out-of-range side does not clamp to the positive largest finite float.

## Source and meaning

- **Source verdict (both rows):** `server-schema.cpp:161-162` and `:164-165` declare `field_num` fields with descriptions, but no field-specific limits or handler. Its numeric evaluator at `:532-545` applies `get<T>()` then the non-hard `min/max` clamp; the same-commit `server-schema.h` defines default bounds as `numeric_limits<T>::lowest()/max()`. This explains the measured positive saturation as generic numeric conversion/clamping, not a Mirostat-specific bound.
- **Prose verdict (both rows):** F28-21 at `SKILL.md:1181` and F28-22 at `:1182` accurately describe the tested positive `1e+39` request, but “beyond the float range … the largest finite float” is over-general: the equally out-of-range negative sample stores the negative finite limit. Corrected meanings:
  - F28-21: “For positive mirostat_tau values above float32 max (1e+39 here), /completion accepts HTTP 200 and stores 3.4028234663852886e+38; values below float32's lowest finite value instead store -3.4028234663852886e+38, so check generation_settings when the exact value matters.”
  - F28-22: “For positive mirostat_eta values above float32 max (1e+39 here), /completion accepts HTTP 200 and stores 3.4028234663852886e+38; values below float32's lowest finite value instead store -3.4028234663852886e+38, so check generation_settings when the exact value matters.”
- **SOURCES/Gate verdict:** S160/S161 in `corpus/SOURCES.md:172-173` point to the correct 704366d file/lines; Gate entries are `corpus/lessons/round-28.md:98-99`. Fetched raw upstream file and lane snapshot both hash to `1f9d7b73b4363b90b08de0360b0a5ce0b3d152750bfb8d587a367e90c7904050`; both located quotes match the declaring and description lines after whitespace joining.

## Receipt and verification gap

`c1-e49b4cf7-receipt.json` records 34 registered / 26 counted / target 18 met; F28-21 and F28-22 are both in `not_counted`, with `why: ["e:generic-conversion"]`. That verdict is correct under A1 (`count-c1.py:33-39`): float32 saturation is explicitly a generic conversion. The receipt's original set-request hashes are respectively `16ab26d69e20ad26251d70075b2185793ce7778d887e9b02f4c72f905de3d570` and `d18168deb6e3ae40dd5b35dc7190e661ea0c7f536adb8302d7520d361fcd40d6`; both original observations agree with this re-measurement. LSP was unavailable: `read xd://lsp` returned “No such tool” (only ast_edit/debug devices mounted), so no LSP status/diagnostics were possible; direct source reads and fetched-hash verification were used. No tools installed.