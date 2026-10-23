# CriticA1Legitimacy — observed evidence excerpts

These are excerpts read during the assigned read-only review, not newly executed server or counter runs. All times below are 2026-10-23 UTC unless an explicit offset is shown.

## 1. Commit chronology

Executed read-only, under `timeout 15s` with GIT_DIR/GIT_WORK_TREE/GIT_INDEX_FILE unset:

```text
git -C /home/vgpnk/Projects/shokunin/kama-shokunin log --format='%H %cI %s' d8bf1804^..e49b4cf77046024551ba83d490ef83d9dee061ed

e49b4cf77046024551ba83d490ef83d9dee061ed 2026-10-23T05:55:40-03:00 round-28: C1 data (34 request-field rows, S140-S173, SKILL section), wave-1 evidence, routed repairs 1-6, instrument registry, lesson draft
fb10d9dab3565470a4a8c52f9e1e118950b7ccac 2026-10-23T05:53:48-03:00 round-28: A1 control call receipts (conversion 0 under A1 vs 20 under A0; rescore max 9; blind-plus 11) before data
75b78bb4900aae1edcdb6b229bb8c572c20fcbce 2026-10-23T05:38:16-03:00 round-28: C1 amendment A1 (generic-conversion refusal in clause e) before any data row lands; A1 pilot receipts
5ebe7b1b2defa4d8109de8fcc9b28f13dd6fb5f6 2026-10-23T05:26:53-03:00 round-28: pre-freeze control call receipts (5 evidential, 5 holds), no counter change
d8bf1804ce52c30343f3e41cbae41c9640db9a64 2026-10-23T05:14:03-03:00 round-28: C1 freeze (counter, preregistration, base and pilot receipts, server-schema snapshot)
```

A path-limited reverse log for `/home/vgpnk/Projects/shokunin/kama-shokunin/registry/request-field-outcomes-r28.json` and `/home/vgpnk/Projects/shokunin/kama-shokunin/SKILL.md` in that range returns only e49b4cf7. AuthorDate and CommitDate of 75b78bb4 are both 2026-10-23T05:38:16-03:00.

Dispatch records: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/w1/dispatched-at.txt:1` is `2026-10-23T08:30:37.161106Z`; `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/w1/spawn-result.txt:1-4` records an initial refusal, then successful data chunks at 08:31:50.597241Z and 08:32:50.875527Z, followed by the remaining chunk at 08:33:50.943650Z. A refused dispatch is not treated as data execution.

## 2. Direct data-seat use of the frozen counter before A1 was written

Source: `/home/vgpnk/.omp/agent/sessions/-Projects-shokunin/2026-10-23T06-27-20-968Z_01a16771-4d08-7011-958e-0f9940db87a7/KamaR28/KamaR28.DataG01-2.jsonl:98-100` (also `history://KamaR28.DataG01-2`).

Assistant tool-call timestamp: **08:35:53.929Z**. Tool id: `call_a49eb97deb664aa3acc7264c`; intent: `Cross-checking rows with counter primitives`.

Exact relevant Python excerpt from the recorded command:

```python
import importlib.util, json, pathlib
spec = importlib.util.spec_from_file_location("c1", "/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/count-c1.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
rows = json.loads(pathlib.Path("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/w1/out/DataG01/rows.json").read_text())
snap = pathlib.Path("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/sources/llama.cpp-704366d/server-schema.cpp").read_text().splitlines()
allok = True
for r in rows["rows"]:
    msg = r["live"]["message"]; mm = m.REJECT_RE.search(msg)
    line_ok = "new field_" in snap[r["line"]-1] and r["field"] in m.literals(snap[r["line"]-1])
    ok = bool(mm and mm.group(1) == r["field"]
              and m.same(float(mm.group(2)), r["outcome"]["bounds"][0])
              and m.same(float(mm.group(3)), r["outcome"]["bounds"][1])
              and m.outcome_text(r["outcome"]) is not None
              and r["live"]["status"] == 400 and line_ok and list(r["set"]) == [r["field"]])
    allok &= ok
    print(r["field"], ok, m.outcome_text(r["outcome"]))
print("all rows pass counter primitives:", allok)
```

Tool-result timestamp: **08:35:54.037Z**, `isError: false`. Relevant stdout verbatim:

```text
sse_ping_interval True reject 400, bounds -1 to 2147483647
n_predict True reject 400, bounds -1 to 2147483647
n_indent True reject 400, bounds 0 to 2147483647
n_keep True reject 400, bounds -1 to 2147483647
all rows pass counter primitives: True
```

This is an actual import and evaluation of counter primitives against live data-row drafts; it is not a complete run of `count-c1.main()` over the integrated registry.

Additional evidence, not conflated with imports: DataG11 evaluated local copies of `same`/`canon` at 08:35:14.665Z and received `same_as_row_value True`, `identity? False default? False` at 08:35:14.670Z. DataG15's offline row-predicate replay returned `ALL FOUR ROW CHECKS PASS` at 08:36:53.398Z. Sources are the corresponding `KamaR28.DataG11-2.jsonl` and `KamaR28.DataG15-2.jsonl` in the same absolute session directory above; the DataG11 report's phrase "counter's own same/canon" is broader than its implementation (local copies).

## 3. A1 authoring and adaptation timestamps

Source: `/home/vgpnk/.omp/agent/sessions/-Projects-shokunin/2026-10-23T06-27-20-968Z_01a16771-4d08-7011-958e-0f9940db87a7/KamaR28.jsonl`.

At **08:37:23.720Z**, call `toolu_01QDrt3wf1yuUpvzNTmDZUxu`, intent `Implementing amendment A1`, replaces the A0 clause-(e) text, adds `conversions`, and adds `e:generic-conversion` in `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/count-c1.py`. Successful result at **08:37:23.732Z**:

```text
283:def conversions(sent) -> list:
625:                                r["why"].append("e:generic-conversion")
```

At **08:37:36.767Z**, call `toolu_01MkiF6aPw7Vin9KH1NmLAQJ` simplifies the new check to `elif any(same(val, c) for c in conversions(sent)):`. At **08:38:16.571Z**, call `toolu_0152qDNt2RCJrSQytjPhYRxY` writes `pre_data_amendment_A1` and commits the amendment; its prose says "Written ... ~08:45Z". The actual authoring record is therefore earlier, about 08:37Z, and follows DataG01's completed evaluation by about 90 seconds.

Source: `/home/vgpnk/.omp/agent/sessions/-Projects-shokunin/2026-10-23T06-27-20-968Z_01a16771-4d08-7011-958e-0f9940db87a7/KamaR28/KamaR28.DataG03-2.jsonl`, incoming IRC at **08:37:50.850Z**. Exact relevant message excerpt:

> min_p -0.25 -> 0.0 equals trunc(-0.25)=0, so it would be refused. Re-probe min_p with a value whose clamp result differs from every such conversion (e.g. -1.5 -> expect 0.0; trunc is -1), and if it shows, replace the min_p row in rows.json (keep the old probe as a no_row note) with the new live evidence and raw body.

The resulting update is disclosed at `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/w1/advice/DataG03.md:4,28-39`.

## 4. Fixed-tip counts and shortcut counts

Existing receipts read, not rerun:

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/final/c1-A0-e49b4cf7-receipt.json`: registered 34, counted 34, target 18, met true, counter sha256 `e6a706bb2e15aec288924b9aec863ff0b1ffdd7e588e78250c0f642565c0540c`.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/final/c1-e49b4cf7-receipt.json`: registered 34, counted 26, target 18, met true, counter sha256 `a38faefeeb48be9fd3590b5077030ed6b7cef08dcaf1ca0540b464bd222749a5`. Only lost ids: F28-11, F28-14, F28-16, F28-17, F28-21, F28-22, F28-25, F28-26.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/controls-A1/CtlA1Conversion/receipt-A0.json`: registered 52, counted 20, target 18, met true; same fixture under `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/controls-A1/CtlA1Conversion/receipt.json`: registered 52, counted 0, met false. Report describes a declaration/type-only shortcut, without field-specific bounds or observed outcomes.

The read-only diff `d8bf1804..75b78bb4` of the counter adds one refusal branch; it adds no admission branch or removed refusal. Constants and existing checks are unchanged apart from receipt schema/version and explanatory text. For fixed rows and identical live observations, A1 acceptance is a subset of A0 acceptance.
