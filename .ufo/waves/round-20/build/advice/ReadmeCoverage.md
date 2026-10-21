VERDICT: partial - GGUF header identity is new mapped ground; error-vs-verdict adds a cross-instrument census over partly held rules.

Scope: frozen lane commit `37bd4c5bd456a2f8a54d3312c28495c321715856` (branch master). I read the requested README/PROVINCE and relevant overlaps in a scratch clone; I did not edit the lane checkout, index or git state. Unless noted, lane citations refer to this revision.

## Findings

- **GGUF declared identity — confirm, with historical overlap.** README coverage lines 84–94 describe `gguf-runtime-compatibility-boundary.md` as “GGUF naming is not an identity parser or support certificate” (`corpus/README.md:92`). The entry's subject is filenames/compatibility; the spec phrase it cites is “is not intended to be perfectly parsable in the field” (`corpus/knowledge/gguf-runtime-compatibility-boundary.md:8-13`). It also says “no endpoint, process or file was contacted” (`:24-27`). No committed knowledge/tool reader was located by a frozen marker search in `corpus/knowledge tools tests` (Git exit 1; command below). Round-16 advice had already read this fixture's header (“GGUF v3, 48 tensors”; `build/advice/CriticC2ToyModel.md:7-9`) and proposed comparing served metadata to it (`:37-41`), but that was advice, not a committed knowledge entry or reusable reader. Thus new ground is the offline bounded reader/reconciliation capability, not first observation of this fixture's metadata.
- **Independent spot evidence.** Official PyPI `gguf` 0.19.0 decoding reports `general.architecture=llama`, `general.name=llama`, `llama.context_length=2048`, `llama.block_count=5`, `llama.embedding_length=64`, `tokenizer.ggml.model=llama`, 19 KVs / 48 tensors; `general.file_type` and `general.alignment` are absent. The fixture SHA-256 is `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d` (1,185,376 bytes). Retained round-18 `live-recovery/receipt-1.json` has that `model_sha256_post`, `/props default_generation_settings.n_ctx=256`, and launch `-c 256`. This is old receipt evidence, not a live round-20 check.
- **K05 remains open.** The README's carried frontier says “Reconcile declared-vs-served context size only as a separate feature move when an authorized serving runtime permits a real comparison” (`corpus/README.md:71-72`). Round 1 defines the original declaration as consumer `limit.context=32768` versus server `--ctx-size=16384` (`corpus/lessons/round-1.md:83-85`). The 2048 GGUF training context vs 256 retained fixture slot is a different pair. `PROVINCE.md:82-90` says this fixture is “pending L0 ratification” (`:82-90`); it does not establish registered-consumer state.
- **Error-vs-verdict — partial, not wholly uncovered.** KQ20 already rejects when “a kill comes from a traceback, a crashed wrapper or a changed denominator” (`corpus/QUALITY.md:121`); KQ24 says an unobserved trigger “is explicitly not-evaluated” (`:133`). Round-18 knowledge says “tool exit 2 / gate exit 3 says NOT-EVALUATED” and “A genuine false check dominates” (`corpus/knowledge/llamacpp-loading-lifecycle.md:239-243`), and records signal semantics / setup-error receipts (`:254-257`; SOURCES S044/S051/S052). Round-19 reports that the grid's “kill test is `code == 1`” and a crash without INVALID “still counts as rejected” (`corpus/lessons/round-19-verifier-spotcheck.md:107-110`); round 18 records the early-abort selftest-kill gap (`corpus/lessons/round-18.md:343-348`). The new delta is the unified rule, explicit exit-1/crash distinction and fixed cross-instrument error-injection census—not the underlying idea that missing observations are not failures.
- **Province boundary.** `PROVINCE.md:6-15` lists producer discovery, consumer pins, served IDs, probes and drift, not an offline model-header surface. It explicitly says “Refuses: model quality/eval (kengaku)” (`:40-43`). `tameshi-shokunin/PROVINCE.md` @ `6acaf4dd2f2a8c9de4312e89a05c0f5155c9f055`, lines 3-11, calls its domain “verification-fixture craft” and owns reusable “verdict-line discipline”; kama should apply it to kama's own instruments without claiming the general method. This scout does not recommend a PROVINCE edit; route any ownership change through the province reviewer/L1.
- Proposed append-only rows and Frontier text: `.ufo/waves/round-20/build/out/ReadmeCoverage/README-append.md`. Existing README lines were not changed.

## Executed commands and observed exits

- `git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse HEAD` → `37bd4c5bd456a2f8a54d3312c28495c321715856`, exit 0.
- `git -C /home/vgpnk/Projects/shokunin/kama-shokunin ls-tree -r --name-only 37bd4c5bd456a2f8a54d3312c28495c321715856 -- corpus PROVINCE.md SKILL.md README.md` → tracked corpus/README/PROVINCE inventory, exit 0.
- `git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r20-ReadmeCoverage/lane && git -C /tmp/kama-r20-ReadmeCoverage/lane checkout -q 37bd4c5bd456a2f8a54d3312c28495c321715856 && git -C /tmp/kama-r20-ReadmeCoverage/lane rev-parse HEAD && git -C /tmp/kama-r20-ReadmeCoverage/lane status --short | wc -l` → same base, `0` status lines, exit 0.
- `git -C /tmp/kama-r20-ReadmeCoverage/lane grep -n -E 'GGUF magic|general\.architecture|tokenizer\.ggml\.model|kv_count|tensor_count|GGUFReader|gguf\.GGUFReader' 37bd4c5bd456a2f8a54d3312c28495c321715856 -- corpus/knowledge tools tests` → no matches, Git exit 1.
- `sha256sum /home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf && stat -c '%s %n' /home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf && command -v uv && uv --version` → SHA/size above; `/home/vgpnk/.local/bin/uv`, `uv 0.13.0`, exit 0.
- Exact oracle command below ran; output included `gguf 0.19.0`, header fields/counts above, exit 0. Tooling record: ephemeral official PyPI `gguf` package 0.19.0 via uv, reason: independent GGUF-header oracle; no persistent tool/service installed or started.

```sh
cd /tmp/kama-r20-ReadmeCoverage && uv run --no-project --with gguf==0.19.0 python3 -c '
import gguf, importlib.metadata as m
r = gguf.GGUFReader("/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf", "r")
print("gguf", m.version("gguf"))
want = ["general.architecture","general.name","llama.context_length","llama.block_count","llama.embedding_length","general.file_type","general.alignment","tokenizer.ggml.model"]
for k in want:
    f = r.get_field(k)
    print(k, "=", None if f is None else f.contents())
print("kv_count", len(r.fields) - 3, "tensor_count", len(r.tensors))
'
```

## Remaining unknowns

The census's final current-arm results, official measured denominators, and L1 admission of either knowledge entry are outside this scout's evidence; proposed README text must not be promoted to a measured/pass claim until those records land. Header declarations are self-claims [INFERENCE]; SHA-256 identifies bytes, not metadata truth. No live server was started.
