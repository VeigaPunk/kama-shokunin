VERDICT: partial — H1–H7 target mappings are confirmed and independent of the check.py crash fix; two FC results remain unmeasured after the counter repair.

# Reverse-intent review: frozen → current fault controls

## Scope and reconstructed contract

This is a scoped falsification trace, not an admission decision. The C2 universe is the named round-17 set, not a claim about unseen mutants (`corpus/lessons/round-18.md:117-146`; `SCORECARD.md:753-760`). The frozen snapshot is pinned by `.ufo/waves/round-18/frozen/SHA256SUMS` and declares its source revision/capture in `frozen/manifest.json`. The paired family-a design applies each named H mutation to one current `check.py` subject and compares frozen versus current fault-control detectors; the current detector's fault classifier requires a failed row and the fault's designated target conjunct (`tests/probe-verdicts/fault-controls.py:685-752`).

The original round-17 detector-self survivors routed here are the targeted-conjunct guard, shared F6 replay cache, and F0 gate (`round-17/falsify/advice/MutFaultControlsSelf.md`, mutants a/c/d; `corpus/lessons/round-17.md:287-290`). Round 18 also maps the append-only, refused-count, malformed-decoder and escaped-child survivors in its ledger (`round-18.md:130-138`).

## H survivor → fault mapping and crash-fix confound test

The current fault table explicitly maps F9–F14 to H1/H2/H3/H5/H6/H7 (`tests/probe-verdicts/fault-controls.py:50-62,252-303`). The official retained measurement confirms the mapping per mutant: all six Hs survive the frozen detector and are killed by the current detector; in each current mutant run the decision is `exit=1, detected=16, accepted=1`, and the only false fault flag is its mapped fault. Thus no F15–F17 crash fault or off-target failure supplies the kill.

| Named survivor | Round-17 weakening | Current targeted fault | Official current mutant's sole accepted fault |
|---|---|---|---|
| H1 | `reason.casefold()` comparison | F9: reason case-swapped, target `reason` | F9 |
| H2 | `.strip()` verdict comparison | F10: leading/trailing whitespace/newline on `ROWS_PAD`, target `verdict` | F10 |
| H3 | route ignores HTTP method | F11: `/v1/models` only via POST/HEAD/lower-case `get`, target `route` | F11 |
| H5 | normalized served id | F12: case/`.gguf`/space/fullwidth variants, target `served_model` | F12 |
| H6 | no-request branch marks row passed | F13: cached replay with no stub request, target `route` | F13 |
| H7 | grades last row | F14: forged first row, honest second/last, target `reason` | F14 |

Official evidence: `.ufo/waves/round-18/runs/c2-survivors.json` JSON pointers `/results/a/items/{H1,H2,H3,H5,H6,H7}` and `/results/a/baselines/current`. The pristine current baseline is exit 0, F0 healthy, 17 detected and 0 accepted; each mutated arm is exit 1, F0 healthy, 16 detected and 1 accepted. Example H1's complete fault vector has only `F9:false`; the corresponding vectors for H2/H3/H5/H6/H7 have only F10/F11/F12/F13/F14 false, respectively. `fault-controls.py`'s selftest checks that every `SURVIVING_MUTANTS` entry is named by a fault (`:119-121`) and validates the wrapper corruption against the intended normalization (`:1253-1423`).

I independently paired each target fault against the **frozen pre-round-18 check.py**, both pristine and with the matching H mutation. This removes the new crash fix from the subject entirely: every pristine run had F0 true, target fault detected, accepted 0 and suite exit 0; every H-mutant run had F0 true, target fault not detected, accepted 1 and suite exit 1. Each mutant's fault explanation was `check exited 0 (wanted 1)`, meaning the named weakening accepted the exact injected corruption. The frozen check source hash was identical before and after the experiment (`ddc3f3cceaee9687de4d6aa29cd4adb72833e08ef0657371dff97cf582fe2099`). The six temporary mutant-copy hashes were H1 `036f2103aef304fb545ca65b2a0f206335b3c7c4e84fdd0626ead74eb04c3bd5`; H2 `e78796341f17d274de93ed0df556c47265f8f615d81365afc9c698a7042ec6e6`; H3 `7f67387a3958e138fe77bab39b77fe6280d54a1e4b8abb880dd0a41f6fd4692d`; H5 `fab14d2da26568cce976747d10e2a8a5a1264621941b67e237330e85f9dba1e6`; H6 `30623b53c544b6e2f6011375ab22aea81a07ef0a650c8ff942dcd0b68519004f`; H7 `eb7b2ad5008fb6e6593055f444ec0cd46c183b57dd85337570250e18f9632d05`. All six old edit sites occurred exactly once. Temporary copies were automatically removed; no frozen/current source was edited.

This directly rules out the new `check.py` crash fix as a necessary cause of the H kills. The check fix changes timeout process-group cleanup and catches `ValueError`/`RecursionError` while decoding probe output (`tests/probe-verdicts/check.py:279-305,397-415`). F9–F14 are valid-JSON grading corruptions, and the paired pre-fix check experiment reproduces each mapped acceptance. Separately, the official family-e results correctly attribute nested JSON, 5,000-digit integer and escaped-sleep transitions to F15/F16/F17: frozen `accepted` → current `handled`, with per-row malformed-output/time-out errors (`runs/c2-survivors.json` `/results/e/items/*`). Those are direct tests of the crash/cleanup repair, not confounds for H1–H7.

## Other named H/F survivor mappings

| Survivor | Frozen → current mapping | Retained measured result and limits |
|---|---|---|
| FC-target | Round-17 mutant (a), removing `if target:`; current selftest's `target-conjunct attribution` classifier assertion | Frozen survived. Old measured current result is **inconclusive**, not a kill: selftest assertion failed as intended, but the independent main arm exited 2 with `F1: fault declares no target conjunct`. This own-fault is in fault-controls, not check.py. |
| FC-f6cache | Round-17 mutant (c), one shared four-row F6 cache; current `selftest_table` per-row cache assertion | Frozen survived. Old measured current result is **inconclusive**, not a kill: named selftest assertion failed, but main arm exited 2 with `F6: a cached replay must target exactly one row (per-row cache), got 4`. Again this is fault-controls' own guard, not the check crash fix. |
| FC-f0gate | Round-17 mutant (d), bypass F0 gate; current reject-everything stub selftest | Frozen survived → current killed by named `F0 gate: a reject-everything` selftest; the ordinary main arm's decision is unchanged. |
| AO-opened / AO-blank | Drop `opened` comparison / stop after blank line; targeted append-only selftest assertions | Frozen survived → current killed by `only opened changes` / `edit after a blank line`. Both mutation source anchors occur once in frozen and current tools. |
| refused-count | Round-17 refused result and attempts evidence, expected 82 | Frozen miscount `0` → current correct `82`; evidence hashes are pinned in the counter JSON and attempts record `[82]`. |
| nested-json / bigint / escaped-sleep | F15 / F16 / F17 | Frozen accepted → current handled; 100,000 nesting, 5,000-digit integer and same-group child timeout are separate crash/cleanup controls. |

The family-b qualification matters: the retained official run was generated with the pre-repair counter (`tool.sha256=2af03fed6ccb0b09e30061828843372cb503d5d5e3afae846bc3f5473ced411d`) and exits 2 with two inconclusives. That output must stay visible (`runs/c2-survivors.exit`; `runs/c2-survivors.json`; the defect and routing are recorded in `round-18.md:162-177`). The pushed-tip counter now changes `combine_arms` so a conclusive named selftest kill wins over an inconclusive opposite arm, and adds cases for targeted-kill+main-exit-2 versus no-targeted-kill+main-exit-2 (`.ufo/waves/round-18/c2/survivors.py:976-982,1735-1749`). Its `--selftest` passed 60/60 in my clone (exit 0), but I did **not** run a corrected full family-b count; therefore I do not upgrade FC-target or FC-f6cache to measured kills here. The tip counter hash is `87cad1cad4565be01ce06e7f92c578c2f449c951894a880166040c3f118dc3ac` and differs from the old measurement's tool hash. This is why the report is partial rather than claiming the full C2 denominator is clean.

## Evidence, commands, setup and limits

- Official measurement command retained in `.ufo/waves/round-18/runs/commands.json`: `python3 .ufo/waves/round-18/c2/survivors.py --json --out .ufo/waves/round-18/runs/c2-survivors.json`; elapsed 1577.225s, exit 2. Official JSON SHA-256 `bd217de0030d1b69f07c0ac3cc334ccdac192896441a177bb13eb3c308509829`; exit-file SHA-256 `5f8bd21203fdbe78b3339b6c8102f5a67cea53316e7b8797aa7aea63e498d985`.
- Frozen manifest SHA256SUMS SHA-256 `696211fb8005743e66c61286c028465eec199c5f5815ce868e0edd57ea32ba8c`; frozen fault-controls `d3eaadeb8a061b4e322868d569df77afbd7331089d06b06c86a2063fdc31b312`; frozen check.py `ddc3f3cceaee9687de4d6aa29cd4adb72833e08ef0657371dff97cf582fe2099`.
- Current fault-controls SHA-256 `58dac1f71346734532bddc60a2d20f95f640406e924b1aec00a0b750feed072a`; current check.py `12367de62efafa02641c4acb497e50f1be5019b54879a9ac6da13efd5f8071a5`; probe `36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3`; matrix-set digest `bf9068d89e4cb8a080167cb32cc818943d717a65fcbd21edb2b8256e22771f32` (nine files/72 rows).
- The paired H experiments ran only in `/tmp/kama-r18-falsify-RevFCDelta`, cloned at `1c325b2e58fcfdc6761f645b44cedfb1d65243e6`; one current fault-controls suite at a time, loopback test stubs only, F0 gate passed in all twelve paired runs, stderr empty and no invocation timed out. No registered port, runtime, system service or installed model was used. No tools were installed/updated.
- One preliminary scratch invocation with a malformed/incompletely generated check copy hit the F0 invalid-baseline gate and exited 2; it was discarded as an own setup fault and is not counted as evidence. The paired runs reported above all passed F0 before their targeted arm.
- LSP was not present in the available tool inventory; source discovery used literal range reads and diffs, not semantic-reference proof. Behavioral conclusions are grounded in the executed paired runs and official result JSON. The inspected universe is exactly the named set; no unseen-mutant immunity is inferred.

### Exact paired-experiment source

This was the complete Python source passed to `python3 -` (cwd `/tmp/kama-r18-falsify-RevFCDelta`; each subprocess cap 300 seconds; outer tool cap 1200 seconds):

```python
import pathlib, subprocess, json, hashlib, tempfile
root=pathlib.Path('/tmp/kama-r18-falsify-RevFCDelta')
frozen=root/'.ufo/waves/round-18/frozen/tests_probe-verdicts_check.py'
current_fc=root/'tests/probe-verdicts/fault-controls.py'
probe=root/'tools/kama-probe.sh'
matrix=root/'tests/probe-verdicts'
edits={
'H1':('            and record["reason"] == expected["reason"]\n','            and record["reason"].casefold() == expected["reason"].casefold()\n','F9'),
'H2':('            record["verdict"] == expected["verdict"]\n','            record["verdict"].strip() == expected["verdict"].strip()\n','F10'),
'H3':('    return any(r.get("method") == "GET"\n               and r.get("path", "").split("?", 1)[0] == "/v1/models"\n               for r in requests)\n','    return any(r.get("path", "").split("?", 1)[0] == "/v1/models"\n               for r in requests)\n','F11'),
'H5':('        record["served_model_ok"] = (\n            record["served_model"] == record["served_model_expected"])\n','        record["served_model_ok"] = (\n            [sid.lower().removesuffix(".gguf")\n             for sid in (record["served_model"] or "").split(",")]\n            == [sid.lower().removesuffix(".gguf")\n                for sid in record["served_model_expected"].split(",")])\n','F12'),
'H6':('            record["error"] = ("stub accepted no requests; probe never "\n                               "reached a listening socket")\n','            record["error"] = ("stub accepted no requests; probe never "\n                               "reached a listening socket")\n            record["passed"] = True\n','F13'),
'H7':('    row = rows[0]\n','    row = rows[-1]\n','F14'),
}
original_hash=hashlib.sha256(frozen.read_bytes()).hexdigest()
with tempfile.TemporaryDirectory(prefix='rfc-paired-target-faults-') as td:
    td=pathlib.Path(td)
    for mutant,(old,new,fid) in edits.items():
        src=frozen.read_text()
        assert src.count(old)==1,(mutant,src.count(old))
        mutated=src.replace(old,new)
        cp=td/f'{mutant}.py'; cp.write_text(mutated)
        print(f'{mutant} source_sha256={hashlib.sha256(cp.read_bytes()).hexdigest()} old_count=1')
        for arm,check in (('pristine',frozen),('mutant',cp)):
            r=subprocess.run(['python3',str(current_fc),'--check',str(check),'--probe',str(probe),'--matrix-dir',str(matrix),'--only-fault',fid,'--json'],cwd=root,capture_output=True,text=True,timeout=300)
            d=json.loads(r.stdout); flt=d['faults'][0]
            print(f' {arm} {fid}: exit={r.returncode} f0={d["positive_control"]["detected"]} detected={flt["detected"]} accepted={d["accepted"]} fault_why={flt["why"][:105]} stderr={r.stderr!r}')
print('frozen_source_sha256_after='+hashlib.sha256(frozen.read_bytes()).hexdigest())
print('frozen_source_sha256_before='+original_hash)
```

No package/tool installation or update occurred. No production source, evidence, lesson or frozen file was edited; the only lane write requested by this assignment is this report.