CONTROL KamaR26CtlCounterMutants: counted 1 of 14 (frozen counter) -- holds

# Result

The one admitted row is the permitted genuine metrics positive P01. The frozen counter refused all 13 adversarial rows; no frozen false admission was observed. The separate one-row novelty control counted 0. This is a clause-sensitivity probe, not claim data.

Axes: row admission, claim acceptance (`met`), reproducibility, live-run cost, exact restoration.

Fifteen single-point scratch mutants were exercised. All 12 row-check mutants have a distinguishing row. Both runtime/model pins were observably decisive, but their deliberate pristine exit-2 refusals are **inconclusive as conventional mutation kills**, not baseline-success kills. TARGET affects `met`, not `counted`. There are no dead row-admission clauses; TARGET is count-dead but acceptance-live.

## Detector and interpretation

The same bounded counter command was run on pristine, mutant and restored counter bytes. For the 12 admission checks the detector is the receipt's selected registry position (`rows[i].counted`), with successful exit 0 required in all three arms: false → true → false kills the mutant. The shared 14-row input intentionally retains one genuine positive, so an invalid admitted row can suppress P01 via distinctness; **an unchanged aggregate count is not evidence that the mutant survived**. Both the tested-row result and aggregate count are reported below. A scalar-count-only detector would miss those substitutions.

For the two pin probes the exact sequence is expected refusal (exit 2) → admitted P01 (exit 0) → expected refusal (exit 2). The refusal receipts omit `counted`; they are not fabricated zeros. For TARGET, compare `met` as well as count. Shared pristine/restored runs bracket every ordinary mutant; each invocation also restores and hashes the working counter in `finally`.

## Clause → mutant → distinguishing row → result

Numbers in the two count columns are pristine → mutant → restored. Registry positions are one-based. Full receipts and verdicts: /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/clause-results.json.

| Clause | Small mutation | Distinguishing rows / violated premise | Tested-row counted | Total counted | Verdict / receipts |
|---|---|---|---|---|---|
| `a_skill_row` | `c["a_skill_row"] = True` | A01 (1): omit its SKILL row | 0 → 1 → 0 | 1 → 1 → 1 | killed; `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/suite-frozen-before.json`, `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/mutant-a_skill_row.json`, `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/suite-frozen-restored.json` |
| `b_long` | `c["b_long"] = True` | B01 (2): 15-byte `support metrics` | 0 → 1 → 0 | 1 → 1 → 1 | killed; `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/suite-frozen-before.json`, `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/mutant-b_long.json`, `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/suite-frozen-restored.json` |
| `b_new_at_base` | `c["b_new_at_base"] = True` | B02 in the separate singleton: 62-byte help prefix already in base corpus/lessons/round-25.md | 0 → 1 → 0 | 0 → 1 → 0 | killed; `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/novelty-frozen-before.json`, `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/novelty-mutant.json`, `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/novelty-frozen-restored.json` |
| `c_source_row` | `c["c_source_row"] = True` | C01 (4): omit S963 from SOURCES | 0 → 1 → 0 | 1 → 1 → 1 | killed; `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/suite-frozen-before.json`, `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/mutant-c_source_row.json`, `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/suite-frozen-restored.json` |
| `d_source_pinned` | `c["d_source_pinned"] = True` | D01 (5): metrics literal appended as a comment to server-models.cpp; source digest differs | 0 → 1 → 0 | 1 → 1 → 1 | killed; `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/suite-frozen-before.json`, `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/mutant-d_source_pinned.json`, `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/suite-frozen-restored.json` |
| `d_in_source` | `c["d_in_source"] = True` | D02 (6): live JSON-wrapper substring absent from pinned source | 0 → 1 → 0 | 1 → 1 → 1 | killed; `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/suite-frozen-before.json`, `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/mutant-d_in_source.json`, `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/suite-frozen-restored.json` |
| `e_error_shown` | `c["e_error_shown"] = True` | E01 (7): --help prints signature but exits 0 | 0 → 1 → 0 | 1 → 2 → 1 | killed; `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/suite-frozen-before.json`, `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/mutant-e_error_shown.json`, `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/suite-frozen-restored.json` |
| `e_signature_seen` | `c["e_signature_seen"] = True` | E02 (8): claims slots message; /metrics returns a different message | 0 → 1 → 0 | 1 → 1 → 1 | killed; `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/suite-frozen-before.json`, `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/mutant-e_signature_seen.json`, `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/suite-frozen-restored.json` |
| `e_not_echoed` | `c["e_not_echoed"] = True` | E03 (9): signature also in X-Kama-Control request header | 0 → 1 → 0 | 1 → 1 → 1 | killed; `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/suite-frozen-before.json`, `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/mutant-e_not_echoed.json`, `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/suite-frozen-restored.json` |
| `f_absent_from_baseline` | `c["f_absent_from_baseline"] = True` | F01 (10): common_params_print_info appears in both healthy and failing startup | 0 → 1 → 0 | 1 → 2 → 1 | killed; `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/suite-frozen-before.json`, `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/mutant-f_absent_from_baseline.json`, `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/suite-frozen-restored.json` |
| `g_distinct` | `c["g_distinct"] = True` | P01 (13), G01 (14): identical signature and trigger counted twice only by mutant | 0 → 1 → 0 | 1 → 2 → 1 | killed; `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/suite-frozen-before.json`, `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/mutant-g_distinct.json`, `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/suite-frozen-restored.json` |
| `id_unique` | `c["id_unique"] = True` | I01 (11) is an invalid precursor; I01 (12) reuses its ID and otherwise passes | 0 → 1 → 0 | 1 → 1 → 1 | killed; `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/suite-frozen-before.json`, `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/mutant-id_unique.json`, `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/suite-frozen-restored.json` |
| `server_sha_pin` | `if False:` at server hash guard | P01 under HOME containing a copied executable with trailing bytes | N/A (pristine refuses) | refused/exit2 → 1 → refused/exit2 | distinguished expected refusal; kill inconclusive because pristine counter exits 2; `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/server-pin-frozen-before.json`, `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/server-pin-mutant.json`, `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/server-pin-frozen-restored.json` |
| `model_sha_pin` | `if False:` at model hash guard | P01 under HOME containing a copied fixture model with trailing bytes | N/A (pristine refuses) | refused/exit2 → 1 → refused/exit2 | distinguished expected refusal; kill inconclusive because pristine counter exits 2; `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/model-pin-frozen-before.json`, `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/model-pin-mutant.json`, `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/model-pin-frozen-restored.json` |
| `TARGET_comparison` | `receipt["met"] = True` | P01 alone admitted: count 1 remains below TARGET 12; mutant falsely sets met=True | unchanged P01; met False → True → False | 1 → 1 → 1 | killed for met; count-dead; `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/suite-frozen-before.json`, `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/mutant-TARGET_comparison.json`, `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/suite-frozen-restored.json` |

## Dead clauses and observed limits

- **No dead admission check among the 12 named row checks.** Each has a false → true → false row-level witness. `d_in_source` depends on the stored `d_source_pinned` value, so setting the pin check True also releases its dependent membership check; D01 distinguishes this actual assignment mutant.
- **TARGET comparison is dead with respect to row count only.** It executes after the row loop and count sum; disabling it cannot admit a row for any row set. It is not dead with respect to the claim: observed `counted=1, met=False` becomes `counted=1, met=True`. No honest row-count witness exists for that requested comparison; its real acceptance effect is recorded instead.
- Pins are not dead: frozen rejects the changed scratch bytes and the matching single-guard mutant executes them and counts P01. They are conservatively inconclusive for a kill metric requiring a pristine exit-0 run.
- These experiments do not achieve or approach the target of 12. Maximum aggregate mutant count was 2; the unmodified frozen count never admitted an invalid row.

## Exact control rows

The complete 14-entry input, in registry order, is reproduced below. Each SKILL row except A01 contains that entry's exact ID, signature and S token; A01 is intentionally absent. SOURCES adds each source row except S963, naming its source filename and commit `704366d`. The SKILL payload says `Mutation control only; not claim data.` and never lands in the lane. Exact patch files: /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/registry.control.patch, /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/SKILL.md.control.patch, /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/SOURCES.md.control.patch, /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/server-models.cpp.control.patch, /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/LOG.md.control.patch.

```json
{
  "signatures": [
    {
      "id": "A01",
      "signature": "This server does not support metrics endpoint",
      "source": {
        "row": "S960",
        "file": "server-context.cpp"
      },
      "channel": "http",
      "args": [],
      "model": "fixture",
      "request": {
        "method": "GET",
        "path": "/metrics"
      }
    },
    {
      "id": "B01",
      "signature": "support metrics",
      "source": {
        "row": "S961",
        "file": "server-context.cpp"
      },
      "channel": "http",
      "args": [],
      "model": "fixture",
      "request": {
        "method": "GET",
        "path": "/metrics"
      }
    },
    {
      "id": "B02",
      "signature": "when set without -c/--ctx-size, the shared KV pool is sized to n_parallel*N",
      "source": {
        "row": "S962",
        "file": "arg.cpp"
      },
      "channel": "startup",
      "args": [
        "--kv-unified-per-slot",
        "invalid"
      ],
      "model": "fixture"
    },
    {
      "id": "C01",
      "signature": "This server does not support metrics endpoint",
      "source": {
        "row": "S963",
        "file": "server-context.cpp"
      },
      "channel": "http",
      "args": [],
      "model": "fixture",
      "request": {
        "method": "GET",
        "path": "/metrics"
      }
    },
    {
      "id": "D01",
      "signature": "This server does not support metrics endpoint",
      "source": {
        "row": "S964",
        "file": "server-models.cpp"
      },
      "channel": "http",
      "args": [],
      "model": "fixture",
      "request": {
        "method": "GET",
        "path": "/metrics"
      }
    },
    {
      "id": "D02",
      "signature": "\"code\":501,\"message\":\"This server does not support metrics endpoint",
      "source": {
        "row": "S965",
        "file": "server-context.cpp"
      },
      "channel": "http",
      "args": [],
      "model": "fixture",
      "request": {
        "method": "GET",
        "path": "/metrics"
      }
    },
    {
      "id": "E01",
      "signature": "show version and build info",
      "source": {
        "row": "S966",
        "file": "arg.cpp"
      },
      "channel": "startup",
      "args": [
        "--help"
      ],
      "model": "fixture"
    },
    {
      "id": "E02",
      "signature": "This server does not support slots endpoint",
      "source": {
        "row": "S967",
        "file": "server-context.cpp"
      },
      "channel": "http",
      "args": [],
      "model": "fixture",
      "request": {
        "method": "GET",
        "path": "/metrics"
      }
    },
    {
      "id": "E03",
      "signature": "This server does not support metrics endpoint",
      "source": {
        "row": "S968",
        "file": "server-context.cpp"
      },
      "channel": "http",
      "args": [],
      "model": "fixture",
      "request": {
        "method": "GET",
        "path": "/metrics",
        "headers": {
          "X-Kama-Control": "This server does not support metrics endpoint"
        }
      }
    },
    {
      "id": "F01",
      "signature": "common_params_print_info",
      "source": {
        "row": "S969",
        "file": "common.cpp"
      },
      "channel": "startup",
      "args": [],
      "model": "missing"
    },
    {
      "id": "I01",
      "signature": "Fabricated duplicate-id precursor, not a runtime signature",
      "source": {
        "row": "S970",
        "file": "server-context.cpp"
      },
      "channel": "http",
      "args": [],
      "model": "fixture",
      "request": {
        "method": "GET",
        "path": "/metrics"
      }
    },
    {
      "id": "I01",
      "signature": "This server does not support metrics endpoint",
      "source": {
        "row": "S971",
        "file": "server-context.cpp"
      },
      "channel": "http",
      "args": [],
      "model": "fixture",
      "request": {
        "method": "GET",
        "path": "/metrics"
      }
    },
    {
      "id": "P01",
      "signature": "This server does not support metrics endpoint",
      "source": {
        "row": "S972",
        "file": "server-context.cpp"
      },
      "channel": "http",
      "args": [],
      "model": "fixture",
      "request": {
        "method": "GET",
        "path": "/metrics"
      }
    },
    {
      "id": "G01",
      "signature": "This server does not support metrics endpoint",
      "source": {
        "row": "S973",
        "file": "server-context.cpp"
      },
      "channel": "http",
      "args": [],
      "model": "fixture",
      "request": {
        "method": "GET",
        "path": "/metrics"
      }
    }
  ]
}
```

For the isolated novelty rerun only the registry is replaced with this singleton; the original SKILL row still contains the signature verbatim as a prefix. Exact replacement registry patch: /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/novelty-registry.control.patch.

```json
{
  "signatures": [
    {
      "id": "B02",
      "signature": "when set without -c/--ctx-size, the shared KV pool is sized to",
      "source": {
        "row": "S962",
        "file": "arg.cpp"
      },
      "channel": "startup",
      "args": [
        "--kv-unified-per-slot",
        "invalid"
      ],
      "model": "fixture"
    }
  ]
}
```

### Candidate failures retained, not hidden

- `suite-pristine` was a preliminary input: F01 used `system_info: n_threads = `, absent from the default-verbosity trigger and baseline, so it failed `e_signature_seen`, not the intended baseline clause. The final F01 uses `common_params_print_info`, seen in both channels and rejected solely by `f_absent_from_baseline`.
- The first b_new_at_base mutant **survived that first witness**: the 75-byte help literal wrapped before `n_parallel*N`, leaving `e_signature_seen=False`. It is not a dead-clause result. The observed contiguous 62-byte prefix remains at base and distinguishes the same untouched mutant in `novelty-*`. Both attempts and outputs are retained.

## Pins and provenance

Extracted commit: `f071209a0f956680b5722e09242e784a1644e216`. Counter digest checked before inspection: `f800865d8a99187b84bce9e5ff27c1f4bc40e748ad3bffec5c0ca4e9d543ba96`. Default `--repo` was retained and read-only; no git index, jj state, installed runtime, fixture model or operator config was modified.

For each pin probe, HOME points to an isolated scratch home; one actual copied asset has the 31-byte suffix `\nKAMA_R26_TRAILING_PIN_CONTROL\n`, the other asset is an absolute symlink to its unchanged original. Shared libraries are symlinked into the copied executable's scratch directory. No fake server and no manually started server were used; only the counter launched children. Both modified-byte assets actually passed the mutant's healthy baseline and reproduced HTTP 501. Exact paths/digests: /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/fixtures.json.

| Asset | Original / restored sha256 | Probe sha256 |
|---|---|---|
| server | `b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804` | `af5d4cea4219c65d4986e1fbadb33602a32247d1b4aa86273a89757c767586e6` |
| model | `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d` | `a75dec4431b4f2662b7fdd67343395523fd5ad972638835168ea554cf5423850` |

### Mutant hashes

Each patch changes only its named behavior-bearing assignment or guard. Exact patches live at the absolute paths below. Scratch mutant copies were restored to the frozen bytes after the probes.

| Clause | Mutated counter sha256 | Patch |
|---|---|---|
| `a_skill_row` | `f36ad8a8958f770c11be0acc52c0ce1468c2ee539adfba80e1569b2642417f42` | /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/a_skill_row.mutant.patch |
| `b_long` | `39f1bd99aaad63fbbb62da8956a956df5740c76ecc076c97377c480080f92240` | /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/b_long.mutant.patch |
| `b_new_at_base` | `69bb6b73d2e37ce83cc5b3c73ec4effa45a4432790c29d26a2ec715fff599939` | /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/b_new_at_base.mutant.patch |
| `c_source_row` | `39703c38c07620b55515578868e01c3ce100e8784838009a4c9b1372557f5ecb` | /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/c_source_row.mutant.patch |
| `d_source_pinned` | `9afd00ef173c4f10dc257e8d2393d71a0bc8ded013bda84154f117993049d3ca` | /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/d_source_pinned.mutant.patch |
| `d_in_source` | `718d51a016043c2a1c703ec08a234983215f23ea7c33330a0b601b0eea40b5aa` | /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/d_in_source.mutant.patch |
| `e_error_shown` | `e97712a5b549526cec98d2ade930c21258104136e2fc18ac56bc57603e1127e9` | /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/e_error_shown.mutant.patch |
| `e_signature_seen` | `bc8ffa0076169da7361fc8db3eba92f39ce01bec97eaf661cfbf40d29fb5ccdb` | /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/e_signature_seen.mutant.patch |
| `e_not_echoed` | `49cbd5f282cf0b71a46b5e007e59ea32f18237e9862b458abfcb9472ce02a76e` | /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/e_not_echoed.mutant.patch |
| `f_absent_from_baseline` | `0798b2137e2a7bb646152423d4dc92600dea41a679a4df8cc354950dce399b37` | /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/f_absent_from_baseline.mutant.patch |
| `g_distinct` | `7bc7f56073f745f422f4ce9f95ac04efc9727d1e770f8f30cf68ed61fdb8ddbb` | /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/g_distinct.mutant.patch |
| `id_unique` | `760feccd7f69c1d4d1e5ad480bfc27ae8785dad9ceef201b48a2158c0a12dbaf` | /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/id_unique.mutant.patch |
| `server_sha_pin` | `19006fc20b48abc39b84ce436efd7d310505d875d9d0ce4f9618ec709915fe0a` | /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/server_sha_pin.mutant.patch |
| `model_sha_pin` | `3bd6b5d03c99f932a6e3674d433414b3380d13aaceb2639aba4c4ad33c6eb67d` | /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/model_sha_pin.mutant.patch |
| `TARGET_comparison` | `9c0eab13a00551d29a839b00fe13770da56df76542b2b40e06fee8b18ab1a635` | /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/TARGET_comparison.mutant.patch |

## Exact commands, outputs and exits

All 25 executed counter calls held the same host-wide flock. Four deliberate pin refusals launched no server. There were 21 live evaluations, serialized, with no manual llama-server launch. Runner wall limit is 650 s; counter wall limit is 600 s, address space 8 GiB, per-process CPU 180 s, per-UID process ceiling 8192, core dumps disabled. TMPDIR is inside the assigned scratch directory; GIT_DIR/GIT_WORK_TREE/GIT_INDEX_FILE are unset. Counter environment and actual full commands are individually in `*.run.json`. The helper's outer argv is `timeout 650 python3 /fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlCounterMutants/run_probe.py <name> [--mutant <scratch mutant>] [--home <scratch HOME>]`; the invoked counter commands are reproduced below.

Initial setup commands and actual statuses, including the one tool-level async refusal before any command executed: /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/setup-commands.json. No tools were installed or updated.

### suite-pristine

`cwd=/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlCounterMutants/tree`; `HOME=/home/vgpnk`; TMPDIR=/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlCounterMutants/tmp.

```sh
flock /fast/scratch/hyaku/kama-r26/counter.lock timeout 600 python3 .ufo/waves/round-26/count-c1.py --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/suite-pristine.json
```

stdout:
```text
registered 14 counted 1 target 12 met False not-counted ['A01:a_skill_row', 'B01:b_long', 'B02:b_new_at_base', 'C01:c_source_row', 'D01:d_source_pinned,d_in_source', 'D02:d_in_source', 'E01:e_error_shown', 'E02:e_signature_seen', 'E03:e_not_echoed', 'F01:e_signature_seen', 'I01:d_in_source', 'I01:id_unique', 'G01:g_distinct']
```

stderr:
```text
```

Exit code: 0. Full metadata: /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/suite-pristine.run.json.

### suite-frozen-before

`cwd=/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlCounterMutants/tree`; `HOME=/home/vgpnk`; TMPDIR=/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlCounterMutants/tmp.

```sh
flock /fast/scratch/hyaku/kama-r26/counter.lock timeout 600 python3 .ufo/waves/round-26/count-c1.py --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/suite-frozen-before.json
```

stdout:
```text
registered 14 counted 1 target 12 met False not-counted ['A01:a_skill_row', 'B01:b_long', 'B02:b_new_at_base', 'C01:c_source_row', 'D01:d_source_pinned,d_in_source', 'D02:d_in_source', 'E01:e_error_shown', 'E02:e_signature_seen', 'E03:e_not_echoed', 'F01:f_absent_from_baseline', 'I01:d_in_source', 'I01:id_unique', 'G01:g_distinct']
```

stderr:
```text
```

Exit code: 0. Full metadata: /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/suite-frozen-before.run.json.

### mutant-a_skill_row

`cwd=/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlCounterMutants/tree`; `HOME=/home/vgpnk`; TMPDIR=/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlCounterMutants/tmp.

```sh
flock /fast/scratch/hyaku/kama-r26/counter.lock timeout 600 python3 .ufo/waves/round-26/count-c1.py --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/mutant-a_skill_row.json
```

stdout:
```text
registered 14 counted 1 target 12 met False not-counted ['B01:b_long,g_distinct', 'B02:b_new_at_base', 'C01:c_source_row,g_distinct', 'D01:d_source_pinned,d_in_source,g_distinct', 'D02:d_in_source,g_distinct', 'E01:e_error_shown', 'E02:e_signature_seen,g_distinct', 'E03:e_not_echoed,g_distinct', 'F01:f_absent_from_baseline', 'I01:d_in_source,g_distinct', 'I01:id_unique,g_distinct', 'P01:g_distinct', 'G01:g_distinct']
```

stderr:
```text
```

Exit code: 0. Full metadata: /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/mutant-a_skill_row.run.json.

### mutant-b_long

`cwd=/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlCounterMutants/tree`; `HOME=/home/vgpnk`; TMPDIR=/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlCounterMutants/tmp.

```sh
flock /fast/scratch/hyaku/kama-r26/counter.lock timeout 600 python3 .ufo/waves/round-26/count-c1.py --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/mutant-b_long.json
```

stdout:
```text
registered 14 counted 1 target 12 met False not-counted ['A01:a_skill_row', 'B02:b_new_at_base', 'C01:c_source_row,g_distinct', 'D01:d_source_pinned,d_in_source,g_distinct', 'D02:d_in_source,g_distinct', 'E01:e_error_shown', 'E02:e_signature_seen,g_distinct', 'E03:e_not_echoed,g_distinct', 'F01:f_absent_from_baseline', 'I01:d_in_source,g_distinct', 'I01:id_unique,g_distinct', 'P01:g_distinct', 'G01:g_distinct']
```

stderr:
```text
```

Exit code: 0. Full metadata: /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/mutant-b_long.run.json.

### mutant-b_new_at_base

`cwd=/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlCounterMutants/tree`; `HOME=/home/vgpnk`; TMPDIR=/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlCounterMutants/tmp.

```sh
flock /fast/scratch/hyaku/kama-r26/counter.lock timeout 600 python3 .ufo/waves/round-26/count-c1.py --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/mutant-b_new_at_base.json
```

stdout:
```text
registered 14 counted 1 target 12 met False not-counted ['A01:a_skill_row', 'B01:b_long', 'B02:e_signature_seen', 'C01:c_source_row', 'D01:d_source_pinned,d_in_source', 'D02:d_in_source', 'E01:e_error_shown', 'E02:e_signature_seen', 'E03:e_not_echoed', 'F01:f_absent_from_baseline', 'I01:d_in_source', 'I01:id_unique', 'G01:g_distinct']
```

stderr:
```text
```

Exit code: 0. Full metadata: /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/mutant-b_new_at_base.run.json.

### mutant-c_source_row

`cwd=/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlCounterMutants/tree`; `HOME=/home/vgpnk`; TMPDIR=/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlCounterMutants/tmp.

```sh
flock /fast/scratch/hyaku/kama-r26/counter.lock timeout 600 python3 .ufo/waves/round-26/count-c1.py --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/mutant-c_source_row.json
```

stdout:
```text
registered 14 counted 1 target 12 met False not-counted ['A01:a_skill_row', 'B01:b_long', 'B02:b_new_at_base', 'D01:d_source_pinned,d_in_source,g_distinct', 'D02:d_in_source,g_distinct', 'E01:e_error_shown', 'E02:e_signature_seen,g_distinct', 'E03:e_not_echoed,g_distinct', 'F01:f_absent_from_baseline', 'I01:d_in_source,g_distinct', 'I01:id_unique,g_distinct', 'P01:g_distinct', 'G01:g_distinct']
```

stderr:
```text
```

Exit code: 0. Full metadata: /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/mutant-c_source_row.run.json.

### mutant-d_source_pinned

`cwd=/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlCounterMutants/tree`; `HOME=/home/vgpnk`; TMPDIR=/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlCounterMutants/tmp.

```sh
flock /fast/scratch/hyaku/kama-r26/counter.lock timeout 600 python3 .ufo/waves/round-26/count-c1.py --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/mutant-d_source_pinned.json
```

stdout:
```text
registered 14 counted 1 target 12 met False not-counted ['A01:a_skill_row', 'B01:b_long', 'B02:b_new_at_base', 'C01:c_source_row', 'D02:d_in_source,g_distinct', 'E01:e_error_shown', 'E02:e_signature_seen,g_distinct', 'E03:e_not_echoed,g_distinct', 'F01:f_absent_from_baseline', 'I01:d_in_source,g_distinct', 'I01:id_unique,g_distinct', 'P01:g_distinct', 'G01:g_distinct']
```

stderr:
```text
```

Exit code: 0. Full metadata: /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/mutant-d_source_pinned.run.json.

### mutant-d_in_source

`cwd=/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlCounterMutants/tree`; `HOME=/home/vgpnk`; TMPDIR=/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlCounterMutants/tmp.

```sh
flock /fast/scratch/hyaku/kama-r26/counter.lock timeout 600 python3 .ufo/waves/round-26/count-c1.py --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/mutant-d_in_source.json
```

stdout:
```text
registered 14 counted 1 target 12 met False not-counted ['A01:a_skill_row', 'B01:b_long', 'B02:b_new_at_base', 'C01:c_source_row', 'D01:d_source_pinned', 'E01:e_error_shown', 'E02:e_signature_seen,g_distinct', 'E03:e_not_echoed,g_distinct', 'F01:f_absent_from_baseline', 'I01:e_signature_seen,g_distinct', 'I01:id_unique,g_distinct', 'P01:g_distinct', 'G01:g_distinct']
```

stderr:
```text
```

Exit code: 0. Full metadata: /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/mutant-d_in_source.run.json.

### mutant-e_error_shown

`cwd=/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlCounterMutants/tree`; `HOME=/home/vgpnk`; TMPDIR=/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlCounterMutants/tmp.

```sh
flock /fast/scratch/hyaku/kama-r26/counter.lock timeout 600 python3 .ufo/waves/round-26/count-c1.py --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/mutant-e_error_shown.json
```

stdout:
```text
registered 14 counted 2 target 12 met False not-counted ['A01:a_skill_row', 'B01:b_long', 'B02:b_new_at_base', 'C01:c_source_row', 'D01:d_source_pinned,d_in_source', 'D02:d_in_source', 'E02:e_signature_seen', 'E03:e_not_echoed', 'F01:f_absent_from_baseline', 'I01:d_in_source', 'I01:id_unique', 'G01:g_distinct']
```

stderr:
```text
```

Exit code: 0. Full metadata: /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/mutant-e_error_shown.run.json.

### mutant-e_signature_seen

`cwd=/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlCounterMutants/tree`; `HOME=/home/vgpnk`; TMPDIR=/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlCounterMutants/tmp.

```sh
flock /fast/scratch/hyaku/kama-r26/counter.lock timeout 600 python3 .ufo/waves/round-26/count-c1.py --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/mutant-e_signature_seen.json
```

stdout:
```text
registered 14 counted 1 target 12 met False not-counted ['A01:a_skill_row', 'B01:b_long', 'B02:b_new_at_base', 'C01:c_source_row', 'D01:d_source_pinned,d_in_source', 'D02:d_in_source', 'E01:e_error_shown', 'E03:e_not_echoed,g_distinct', 'F01:f_absent_from_baseline', 'I01:d_in_source,g_distinct', 'I01:id_unique,g_distinct', 'P01:g_distinct', 'G01:g_distinct']
```

stderr:
```text
```

Exit code: 0. Full metadata: /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/mutant-e_signature_seen.run.json.

### mutant-e_not_echoed

`cwd=/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlCounterMutants/tree`; `HOME=/home/vgpnk`; TMPDIR=/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlCounterMutants/tmp.

```sh
flock /fast/scratch/hyaku/kama-r26/counter.lock timeout 600 python3 .ufo/waves/round-26/count-c1.py --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/mutant-e_not_echoed.json
```

stdout:
```text
registered 14 counted 1 target 12 met False not-counted ['A01:a_skill_row', 'B01:b_long', 'B02:b_new_at_base', 'C01:c_source_row', 'D01:d_source_pinned,d_in_source', 'D02:d_in_source', 'E01:e_error_shown', 'E02:e_signature_seen', 'F01:f_absent_from_baseline', 'I01:d_in_source', 'I01:id_unique,g_distinct', 'P01:g_distinct', 'G01:g_distinct']
```

stderr:
```text
```

Exit code: 0. Full metadata: /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/mutant-e_not_echoed.run.json.

### mutant-f_absent_from_baseline

`cwd=/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlCounterMutants/tree`; `HOME=/home/vgpnk`; TMPDIR=/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlCounterMutants/tmp.

```sh
flock /fast/scratch/hyaku/kama-r26/counter.lock timeout 600 python3 .ufo/waves/round-26/count-c1.py --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/mutant-f_absent_from_baseline.json
```

stdout:
```text
registered 14 counted 2 target 12 met False not-counted ['A01:a_skill_row', 'B01:b_long', 'B02:b_new_at_base', 'C01:c_source_row', 'D01:d_source_pinned,d_in_source', 'D02:d_in_source', 'E01:e_error_shown', 'E02:e_signature_seen', 'E03:e_not_echoed', 'I01:d_in_source', 'I01:id_unique', 'G01:g_distinct']
```

stderr:
```text
```

Exit code: 0. Full metadata: /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/mutant-f_absent_from_baseline.run.json.

### mutant-g_distinct

`cwd=/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlCounterMutants/tree`; `HOME=/home/vgpnk`; TMPDIR=/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlCounterMutants/tmp.

```sh
flock /fast/scratch/hyaku/kama-r26/counter.lock timeout 600 python3 .ufo/waves/round-26/count-c1.py --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/mutant-g_distinct.json
```

stdout:
```text
registered 14 counted 2 target 12 met False not-counted ['A01:a_skill_row', 'B01:b_long', 'B02:b_new_at_base', 'C01:c_source_row', 'D01:d_source_pinned,d_in_source', 'D02:d_in_source', 'E01:e_error_shown', 'E02:e_signature_seen', 'E03:e_not_echoed', 'F01:f_absent_from_baseline', 'I01:d_in_source', 'I01:id_unique']
```

stderr:
```text
```

Exit code: 0. Full metadata: /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/mutant-g_distinct.run.json.

### mutant-id_unique

`cwd=/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlCounterMutants/tree`; `HOME=/home/vgpnk`; TMPDIR=/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlCounterMutants/tmp.

```sh
flock /fast/scratch/hyaku/kama-r26/counter.lock timeout 600 python3 .ufo/waves/round-26/count-c1.py --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/mutant-id_unique.json
```

stdout:
```text
registered 14 counted 1 target 12 met False not-counted ['A01:a_skill_row', 'B01:b_long', 'B02:b_new_at_base', 'C01:c_source_row', 'D01:d_source_pinned,d_in_source', 'D02:d_in_source', 'E01:e_error_shown', 'E02:e_signature_seen', 'E03:e_not_echoed', 'F01:f_absent_from_baseline', 'I01:d_in_source', 'P01:g_distinct', 'G01:g_distinct']
```

stderr:
```text
```

Exit code: 0. Full metadata: /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/mutant-id_unique.run.json.

### mutant-TARGET_comparison

`cwd=/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlCounterMutants/tree`; `HOME=/home/vgpnk`; TMPDIR=/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlCounterMutants/tmp.

```sh
flock /fast/scratch/hyaku/kama-r26/counter.lock timeout 600 python3 .ufo/waves/round-26/count-c1.py --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/mutant-TARGET_comparison.json
```

stdout:
```text
registered 14 counted 1 target 12 met True not-counted ['A01:a_skill_row', 'B01:b_long', 'B02:b_new_at_base', 'C01:c_source_row', 'D01:d_source_pinned,d_in_source', 'D02:d_in_source', 'E01:e_error_shown', 'E02:e_signature_seen', 'E03:e_not_echoed', 'F01:f_absent_from_baseline', 'I01:d_in_source', 'I01:id_unique', 'G01:g_distinct']
```

stderr:
```text
```

Exit code: 0. Full metadata: /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/mutant-TARGET_comparison.run.json.

### suite-frozen-restored

`cwd=/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlCounterMutants/tree`; `HOME=/home/vgpnk`; TMPDIR=/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlCounterMutants/tmp.

```sh
flock /fast/scratch/hyaku/kama-r26/counter.lock timeout 600 python3 .ufo/waves/round-26/count-c1.py --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/suite-frozen-restored.json
```

stdout:
```text
registered 14 counted 1 target 12 met False not-counted ['A01:a_skill_row', 'B01:b_long', 'B02:b_new_at_base', 'C01:c_source_row', 'D01:d_source_pinned,d_in_source', 'D02:d_in_source', 'E01:e_error_shown', 'E02:e_signature_seen', 'E03:e_not_echoed', 'F01:f_absent_from_baseline', 'I01:d_in_source', 'I01:id_unique', 'G01:g_distinct']
```

stderr:
```text
```

Exit code: 0. Full metadata: /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/suite-frozen-restored.run.json.

### server-pin-frozen-before

`cwd=/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlCounterMutants/tree`; `HOME=/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlCounterMutants/home-server`; TMPDIR=/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlCounterMutants/tmp.

```sh
flock /fast/scratch/hyaku/kama-r26/counter.lock timeout 600 python3 .ufo/waves/round-26/count-c1.py --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/server-pin-frozen-before.json
```

stdout:
```text
```

stderr:
```text
could-not-evaluate: llama-server sha256 mismatch
```

Exit code: 2. Full metadata: /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/server-pin-frozen-before.run.json.

### server-pin-mutant

`cwd=/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlCounterMutants/tree`; `HOME=/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlCounterMutants/home-server`; TMPDIR=/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlCounterMutants/tmp.

```sh
flock /fast/scratch/hyaku/kama-r26/counter.lock timeout 600 python3 .ufo/waves/round-26/count-c1.py --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/server-pin-mutant.json
```

stdout:
```text
registered 14 counted 1 target 12 met False not-counted ['A01:a_skill_row', 'B01:b_long', 'B02:b_new_at_base', 'C01:c_source_row', 'D01:d_source_pinned,d_in_source', 'D02:d_in_source', 'E01:e_error_shown', 'E02:e_signature_seen', 'E03:e_not_echoed', 'F01:f_absent_from_baseline', 'I01:d_in_source', 'I01:id_unique', 'G01:g_distinct']
```

stderr:
```text
```

Exit code: 0. Full metadata: /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/server-pin-mutant.run.json.

### server-pin-frozen-restored

`cwd=/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlCounterMutants/tree`; `HOME=/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlCounterMutants/home-server`; TMPDIR=/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlCounterMutants/tmp.

```sh
flock /fast/scratch/hyaku/kama-r26/counter.lock timeout 600 python3 .ufo/waves/round-26/count-c1.py --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/server-pin-frozen-restored.json
```

stdout:
```text
```

stderr:
```text
could-not-evaluate: llama-server sha256 mismatch
```

Exit code: 2. Full metadata: /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/server-pin-frozen-restored.run.json.

### model-pin-frozen-before

`cwd=/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlCounterMutants/tree`; `HOME=/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlCounterMutants/home-model`; TMPDIR=/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlCounterMutants/tmp.

```sh
flock /fast/scratch/hyaku/kama-r26/counter.lock timeout 600 python3 .ufo/waves/round-26/count-c1.py --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/model-pin-frozen-before.json
```

stdout:
```text
```

stderr:
```text
could-not-evaluate: fixture model sha256 mismatch
```

Exit code: 2. Full metadata: /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/model-pin-frozen-before.run.json.

### model-pin-mutant

`cwd=/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlCounterMutants/tree`; `HOME=/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlCounterMutants/home-model`; TMPDIR=/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlCounterMutants/tmp.

```sh
flock /fast/scratch/hyaku/kama-r26/counter.lock timeout 600 python3 .ufo/waves/round-26/count-c1.py --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/model-pin-mutant.json
```

stdout:
```text
registered 14 counted 1 target 12 met False not-counted ['A01:a_skill_row', 'B01:b_long', 'B02:b_new_at_base', 'C01:c_source_row', 'D01:d_source_pinned,d_in_source', 'D02:d_in_source', 'E01:e_error_shown', 'E02:e_signature_seen', 'E03:e_not_echoed', 'F01:f_absent_from_baseline', 'I01:d_in_source', 'I01:id_unique', 'G01:g_distinct']
```

stderr:
```text
```

Exit code: 0. Full metadata: /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/model-pin-mutant.run.json.

### model-pin-frozen-restored

`cwd=/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlCounterMutants/tree`; `HOME=/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlCounterMutants/home-model`; TMPDIR=/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlCounterMutants/tmp.

```sh
flock /fast/scratch/hyaku/kama-r26/counter.lock timeout 600 python3 .ufo/waves/round-26/count-c1.py --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/model-pin-frozen-restored.json
```

stdout:
```text
```

stderr:
```text
could-not-evaluate: fixture model sha256 mismatch
```

Exit code: 2. Full metadata: /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/model-pin-frozen-restored.run.json.

### novelty-frozen-before

`cwd=/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlCounterMutants/tree`; `HOME=/home/vgpnk`; TMPDIR=/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlCounterMutants/tmp.

```sh
flock /fast/scratch/hyaku/kama-r26/counter.lock timeout 600 python3 .ufo/waves/round-26/count-c1.py --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/novelty-frozen-before.json
```

stdout:
```text
registered 1 counted 0 target 12 met False not-counted ['B02:b_new_at_base']
```

stderr:
```text
```

Exit code: 0. Full metadata: /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/novelty-frozen-before.run.json.

### novelty-mutant

`cwd=/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlCounterMutants/tree`; `HOME=/home/vgpnk`; TMPDIR=/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlCounterMutants/tmp.

```sh
flock /fast/scratch/hyaku/kama-r26/counter.lock timeout 600 python3 .ufo/waves/round-26/count-c1.py --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/novelty-mutant.json
```

stdout:
```text
registered 1 counted 1 target 12 met False not-counted []
```

stderr:
```text
```

Exit code: 0. Full metadata: /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/novelty-mutant.run.json.

### novelty-frozen-restored

`cwd=/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlCounterMutants/tree`; `HOME=/home/vgpnk`; TMPDIR=/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlCounterMutants/tmp.

```sh
flock /fast/scratch/hyaku/kama-r26/counter.lock timeout 600 python3 .ufo/waves/round-26/count-c1.py --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/novelty-frozen-restored.json
```

stdout:
```text
registered 1 counted 0 target 12 met False not-counted ['B02:b_new_at_base']
```

stderr:
```text
```

Exit code: 0. Full metadata: /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/novelty-frozen-restored.run.json.

## Concrete weakness and fix proposal

**Observed coverage weakness: aggregate-count aliasing.** Disabling a_skill_row, b_long, c_source_row, d_source_pinned, d_in_source, e_signature_seen, e_not_echoed or id_unique admits the intended invalid row while P01 becomes non-distinct, leaving the total at 1. A detector asserting only the printed count would falsely report these mutants survived. Fix proposal: preregister the exact per-position admission vector/reasons for each control, and use a singleton input for ordinary gates (two rows only for distinctness/ID checks); assert `met` independently for TARGET. No counter or contract change was integrated.

**[INFERENCE] Runtime pin scope:** count-c1.py hashes only the resolved executable and the GGUF, not the shared-library closure. The installed directory contains server-implementation shared libraries; if execution delegates to them, pinning just the launcher does not pin all runtime behavior. A concrete hardening is to pin the resolved runtime libraries as well, or pin a self-contained executable. This was not tested by modifying libraries; the assignment forbids changing the installed runtime and the probe stops here.

## Restoration and process evidence

Every completed invocation has before SHA `f800865d8a99187b84bce9e5ff27c1f4bc40e748ad3bffec5c0ca4e9d543ba96`, its actual run SHA, and restored SHA `f800865d8a99187b84bce9e5ff27c1f4bc40e748ad3bffec5c0ca4e9d543ba96` in `*.run.json`; every `cleanup_killed_pids` and `owned_servers_remaining` list is empty. The same frozen detector after the mutants reproduced every final static/live rejection and P01 admission.

After those restored-byte runs, SKILL.md, SOURCES.md, server-models.cpp and LOG.md were restored byte-for-byte to the extracted commit; the newly created registry was removed. All 15 scratch mutant files were restored to frozen bytes; both scratch copied pin assets were restored to original bytes. The lane counter and the original server/model digests are unchanged. Per-file before, probe-input and restored digests: /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/restoration.json.

Final required process check:
```sh
pgrep -af llama-server
```
```text
3778099 timeout 120 /home/vgpnk/.local/bin/llama-server -m /home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf --host 127.0.0.1 --port 47654 -t 2
3778102 /home/vgpnk/.local/bin/llama-server -m /home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf --host 127.0.0.1 --port 47654 -t 2
```
Exit code 0. These two PIDs are not ours: both cwd values are `/home/vgpnk/Projects/shokunin` and their port is 47654, outside our counter's 47560–47579 range. They were not touched. Ownership receipt: /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/process-ownership.json. No assigned-counter server remains.

## Files written

All authored output files are under /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/; the exhaustive absolute-path manifest, including every per-run JSON/stdout/stderr receipt, every exact patch and each scratch-only authored/changed file, is /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants/files-written.json. Extraction wrote the commit's archive members only under /fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlCounterMutants/tree/; it never wrote the lane tree. Scratch temp directories were created and removed by the counter. No tool installs/updates.
