Verdict: Drafted five KQ31 supersession rows and Gate quotes; fetched bytes and cited lines agree with the existing source anchors, but three lane snapshot files are absent, so their required byte comparisons could not be made.
Task axes: source fidelity, correction accuracy, provenance/auditability, lane-scope compliance.

## Behavior
No product behavior changed. This seat produced proposed SOURCES rows only, for S106, S107, S109, S112 and S113. Each teaches cell begins `supersedes S1NN —`; the prior rows and lesson explanations remain untouched.

## Findings

- `corpus/QUALITY.md:164` requires a newly opened row whose teaches cell starts `supersedes S0NN —`; the old row and filed explanation stay intact. `corpus/lessons/round-25-verifier-spotcheck.md:213-217` routes S106, S109 and S113; it says S107/S112 fixes were reported by the lane but not verified by that spot-check.
- S106: fresh `fit.cpp` has the initial memory measurement at line 264, before automatic-context resolution at 270-276. Reduction is guarded by `global_surplus < 0` at 384, automatic context and `n_ctx_max > n_ctx_min_total` at 393-394; line 414 sets the floor, and the `sum_used_target`-not-greater branch at 441-444 leaves that floor in place. The draft also preserves interpolation/alignment at 425-430 and the user-set no-change branch at 455.
- S109: `try_clear_idle_slots` returns false unless KV is unified (1813-1815), and clears at most one slot that is not processing and has a nonempty prompt (1817-1830). On the `ret == 1`, `n_batch > 1` retry path, a successful clear avoids halving; otherwise the batch is halved (4334-4337). The `n_batch == 1 && ret == 1` terminal error branch is at 4298-4330. The draft keeps HTTP rendering outside this source's scope.
- S113: `llama-kv-cache.cpp:301-304` passes `kv_size` as the cells field, `layers.size()` as layers and `n_seq_max/n_stream` as sequence counts. It logs total K+V MiB; the format does not print `kv_size * n_stream` as a total per-layer cell count. Constructor allocation and tensor dimensions are at 142-145 and 233-234.
- S107 check: current `corpus/SOURCES.md:119` still says “An unset n_ctx resolves to n_ctx_train” and that per-slot values “never clamp.” Fresh `llama-context.cpp:219` specifically tests `params.n_ctx == 0`; lines 409-417 only log comparisons. The prior review recommends limiting this to the constructor (`.ufo/waves/round-25/a2-falsify/advice/ReopenS107.md:48-79`). The prior review's line-219/default-launch and YaRN-range findings are distinct: this source row already locates YaRN at 4114-4118, while the cited knowledge-entry range at the time was wrong (`ReopenS107.md:63-73`). The new row therefore corrects source scope/teaches, not that entry citation. Current `SKILL.md:679` cites S106-S113 as a range, so the draft used-by includes `SKILL.md` despite the older review's then-current search finding.
- S112 check: current `corpus/SOURCES.md:124` retains its old broad teach and only lists `corpus/knowledge/context-capacity.md` as used-by. Fresh README line 165 gives the KV-pool sizing promise; line 168 describes the cache-RAM MiB limit; lines 1131-1155 include `/metrics`, with `n_tokens_max` described at 1149 as a context-size high watermark; line 1304 shows `meta.n_ctx_train` but does not define it. The prior report's requested corrections and its bounded README review are at `ReopenS112.md:37-48`; the current skill cites S112 at `SKILL.md:690`. Draft S153 narrows the claim to KV-pool sizing, covers `/metrics`, separates the example from its interpretation, and adds `SKILL.md` to used-by.
- Current entry cross-check for the reported S107 fixes: `corpus/knowledge/context-capacity.md:95-96` still cites line 219 for both fallback and split, although the split is at 381-393; `:222-223` still cites YaRN as 4113-4117 rather than 4114-4118. `SKILL.md:688` still attributes the full-training-context-per-slot statement to S106 alone; `ReopenS106.md:53,72` identifies the per-slot division as S107. These knowledge/skill edits are not part of this seat's row drafts.
- S112's current entry text `context-capacity.md:176-180` covers `/props`, `/slots` and `/v1/models` and states `/metrics` was not read at runtime; that statement is distinct from the README documentation search. The new row documents the README `/metrics` section without claiming a runtime metrics probe.
- Current `corpus/SOURCES.md` has no `supersedes S107` or `supersedes S112` match (the targeted search returned “No matches found”). The old rows remain unchanged; the two checks are represented by proposed S151 and S153.

## Gates and provenance

KQ31 form: passed for the five drafts. Gate rows include the pinned GitHub blob URL with `#L` anchor, access date 2026-10-23, and an exact quote of at most 25 words. Fetched-file line checks were read from the downloaded bytes: `fit.cpp:264,270-276,384,393-455`; `llama-context.cpp:219,377-393,409-417,4114-4118`; `server-context.cpp:1810-1834,4298-4341`; `README.md:165,168-169,1131-1155,1304`; `llama-kv-cache.cpp:142-145,233-234,301-304`.

Fresh fetch command (all five downloads completed):

```sh
mkdir -p /fast/scratch/hyaku/kama-r26/ScribeSupersedes && curl --fail --location --silent --show-error --max-time 45 'https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/fit.cpp' -o /fast/scratch/hyaku/kama-r26/ScribeSupersedes/fit.cpp && curl --fail --location --silent --show-error --max-time 45 'https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp' -o /fast/scratch/hyaku/kama-r26/ScribeSupersedes/server-context.cpp && curl --fail --location --silent --show-error --max-time 45 'https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/llama-kv-cache.cpp' -o /fast/scratch/hyaku/kama-r26/ScribeSupersedes/llama-kv-cache.cpp && curl --fail --location --silent --show-error --max-time 45 'https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/llama-context.cpp' -o /fast/scratch/hyaku/kama-r26/ScribeSupersedes/llama-context.cpp && curl --fail --location --silent --show-error --max-time 45 'https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/README.md' -o /fast/scratch/hyaku/kama-r26/ScribeSupersedes/README.md && sha256sum /fast/scratch/hyaku/kama-r26/ScribeSupersedes/fit.cpp /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/sources/llama.cpp-704366d/common/fit.cpp /fast/scratch/hyaku/kama-r26/ScribeSupersedes/server-context.cpp /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/sources/llama.cpp-704366d/tools/server/server-context.cpp /fast/scratch/hyaku/kama-r26/ScribeSupersedes/llama-kv-cache.cpp /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/sources/llama.cpp-704366d/src/llama-kv-cache.cpp /fast/scratch/hyaku/kama-r26/ScribeSupersedes/llama-context.cpp /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/sources/llama.cpp-704366d/src/llama-context.cpp /fast/scratch/hyaku/kama-r26/ScribeSupersedes/README.md /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/sources/llama.cpp-704366d/tools/server/README.md && cmp -s /fast/scratch/hyaku/kama-r26/ScribeSupersedes/fit.cpp /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/sources/llama.cpp-704366d/common/fit.cpp && printf 'fit.cpp identical\n' && cmp -s /fast/scratch/hyaku/kama-r26/ScribeSupersedes/server-context.cpp /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/sources/llama.cpp-704366d/tools/server/server-context.cpp && printf 'server-context.cpp identical\n' && cmp -s /fast/scratch/hyaku/kama-r26/ScribeSupersedes/llama-kv-cache.cpp /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/sources/llama.cpp-704366d/src/llama-kv-cache.cpp && printf 'llama-kv-cache.cpp identical\n' && cmp -s /fast/scratch/hyaku/kama-r26/ScribeSupersedes/llama-context.cpp /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/sources/llama.cpp-704366d/src/llama-context.cpp && printf 'llama-context.cpp identical\n' && cmp -s /fast/scratch/hyaku/kama-r26/ScribeSupersedes/README.md /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/sources/llama.cpp-704366d/tools/server/README.md && printf 'README.md identical\n'
```

That command exited 1 during `sha256sum` because the snapshot paths I first supplied were nested (`common/fit.cpp`, `tools/server/server-context.cpp`, `src/llama-kv-cache.cpp`, `src/llama-context.cpp`, `tools/server/README.md`). The tool reported `No such file or directory (os error 2)` for each nested snapshot path; it did not reach the `cmp` chain. Fresh fetched hashes printed before those errors were:

- `fit.cpp` `1f83da2a5dc460b893373365e07341695be80d6c662e53679032a138cce4dd58`
- `server-context.cpp` `dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329`
- `llama-kv-cache.cpp` `d0739eaf00d8457f4109a616e0beb1cf07ea074c9b460d92a7b6d48c4519d294`
- `llama-context.cpp` `2a25e556cb0d16725e01ce853fb1b76da91dcb41b803ce1a6bacec89bfb94aa5`
- `README.md` `714c067bdbc49bde2735810fbff83eb2933b12c57d50f0012b61fcecb75a6a37`

Corrected flattened-snapshot comparison command:

```sh
sha256sum /fast/scratch/hyaku/kama-r26/ScribeSupersedes/server-context.cpp /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/sources/llama.cpp-704366d/server-context.cpp /fast/scratch/hyaku/kama-r26/ScribeSupersedes/llama-context.cpp /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/sources/llama.cpp-704366d/llama-context.cpp && cmp -s /fast/scratch/hyaku/kama-r26/ScribeSupersedes/server-context.cpp /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/sources/llama.cpp-704366d/server-context.cpp && printf 'server-context.cpp identical\n' && cmp -s /fast/scratch/hyaku/kama-r26/ScribeSupersedes/llama-context.cpp /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/sources/llama.cpp-704366d/llama-context.cpp && printf 'llama-context.cpp identical\n' && test ! -e /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/sources/llama.cpp-704366d/fit.cpp && printf 'fit.cpp snapshot missing\n' && test ! -e /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/sources/llama.cpp-704366d/llama-kv-cache.cpp && printf 'llama-kv-cache.cpp snapshot missing\n' && test ! -e /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/sources/llama.cpp-704366d/README.md && printf 'README.md snapshot missing\n'
```

Output: the local snapshot hashes matched for `server-context.cpp` and `llama-context.cpp`; both `cmp` calls printed `identical`. The final checks printed `fit.cpp snapshot missing`, `llama-kv-cache.cpp snapshot missing`, `README.md snapshot missing`. The command completed successfully (exit 0). The five downloaded hashes match the SHA-256 anchors in the old S106, S109, S113, S107 and S112 rows respectively, but the three absent lane snapshot files could not be compared. No snapshot file was written because this seat is limited to its output directory.

The output-directory preparation command was `mkdir -p /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/w1-build/out/ScribeSupersedes && printf 'output directory ready\n'`; output `output directory ready`, exit 0.

Line-number proof from the required grep search: `rows.md` S150-S154 are on lines 3-7; `gate.md` S150-S154 are on lines 5-9. Both searches returned all five IDs.

## Gates not run / limits

- No llama-server was started; this seat has no authorized port block. No frozen counter, build, test, or runtime behavior was run.
- No tools were installed.
- The three missing source snapshots leave the required byte-identity gate unresolved for fit.cpp, llama-kv-cache.cpp and README.md. This report does not claim those comparisons passed.
- No edits were made to `corpus/SOURCES.md`, `SKILL.md`, `corpus/knowledge/context-capacity.md`, the counter, judge or source snapshot. Integration remains the lane owner's task.

## Files written

Lane outputs:
- `.ufo/waves/round-26/w1-build/out/ScribeSupersedes/rows.md`
- `.ufo/waves/round-26/w1-build/out/ScribeSupersedes/gate.md`
- `.ufo/waves/round-26/w1-build/advice/ScribeSupersedes.md`

Scratch fetches:
- `/fast/scratch/hyaku/kama-r26/ScribeSupersedes/fit.cpp`
- `/fast/scratch/hyaku/kama-r26/ScribeSupersedes/server-context.cpp`
- `/fast/scratch/hyaku/kama-r26/ScribeSupersedes/llama-kv-cache.cpp`
- `/fast/scratch/hyaku/kama-r26/ScribeSupersedes/llama-context.cpp`
- `/fast/scratch/hyaku/kama-r26/ScribeSupersedes/README.md`
