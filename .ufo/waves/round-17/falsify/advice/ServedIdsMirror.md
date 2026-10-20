VERDICT: partial — the python-path parse mirrors faithfully and all 72 rows pass, but the join/post-processing diverges on 4 reachable id shapes and the grep fallback is not mirrored at all; no matrix row exercises any divergence.

## What I attacked

C1's `served_model` invariant only. I compared `tests/probe-verdicts/check.py` `served_ids_of()` (293-326) and `expected_served_model()` (339-361) line by line against `tools/kama-probe.sh` `served_ids()` (335-377) and the `C_SERVED` post-processing (524-529) at `54a29268e2083caa2b1e0d54ee1e7d90961302f3`, then replayed every matrix body and ran both paths end to end.

## Comparison — what is identical

| Element | check.py | kama-probe.sh | Result |
|---|---|---|---|
| top-level must be a JSON object | 301-309 | 344-345 | identical (empty for both) |
| unparseable body / wrong type | 306-309 → `[]` | 342-343 → `exit 0`, no ids | identical effective result |
| per-item filter `isinstance(str) and truthy`, dict items only | 311-316 | 347-355 | identical |
| precedence `data[].id → models[].id → models[].name → models[].model → top-level id` | 318-323 | 357-363 | identical order |
| first non-empty group wins | 324 | 364-365 | identical |
| dedupe preserving order | 325 `list(dict.fromkeys(ids))` | 366 `print("\n".join(dict.fromkeys(g)))` | identical |
| empty result | 326 `[]` | no stdout → `-` | identical |

`check.py:296` scopes its own claim: "Mirrors tools/kama-probe.sh served_ids() (lines 335-368, python3 path):" — accurate as to the fallback exclusion, though the python block is 337-368 (335 is the function header).

## Divergences, each with the row that would exercise it

The probe does not emit `served_ids()`' list; it emits `C_SERVED`, built at `kama-probe.sh:526-529`. `check.py:361` rebuilds it with `return ",".join(ids) if ids else "-"`, which skips that post-processing. Four reachable divergences follow.

**D1 — a newline inside an id becomes a comma.** `kama-probe.sh:527` `C_SERVED=$(printf '%s' "$ids" | tr '\n' ',')` cannot distinguish the separator from a newline in an id; `check.py:361` preserves the newline. Reachable via `body_json`: the stub re-dumps the escape, the probe decodes it. End-to-end row `{"data":[{"id":"a\nb"}]}`: probe `served_model='a,b'`, check.py expected `'a\nb'`. **No matrix row exercises this** (all 11 id-bearing ids are plain ASCII).

**D2 — a trailing newline on the last id is eaten by `$( )`.** `kama-probe.sh:526` command substitution strips every trailing newline, including one belonging to the final id. Row `{"data":[{"id":"a\n"}]}`: probe `'a'`, expected `'a\n'`. **Unexercised.**

**D3 — `${C_SERVED%,}` strips a data comma.** `kama-probe.sh:528` removes one trailing comma unconditionally, then 529 turns an empty result into `-`. Row `{"data":[{"id":"a,"}]}`: probe `'a'`, expected `'a,'`. Row `{"data":[{"id":","}]}`: probe `'-'`, expected `','`. The strip is only wrong on the *final* id: `{"data":[{"id":"a,"},{"id":"b"}]}` matched exactly (`'a,,b'` both). **Unexercised.**

**D4 — the body source differs (locale-dependent file read).** `kama-probe.sh:341` `doc = json.load(open(sys.argv[1]))` reads the bytes curl wrote with the process locale encoding; `check.py:301-305` parses the in-memory matrix body (`body_json` dict or `body_text` string). Equivalent for every body this harness can produce, because `check.py make_handler` always `.encode("utf-8")`s the body, and BOM/malformed bodies are rejected identically by both. Divergence would require a non-UTF-8-decodable body under an ASCII locale — **unreachable through the gate**, and unexercised.

**D5 — the grep fallback (HAVE_PY=0) is not mirrored at all.** `kama-probe.sh:371` says "grep fallback: approximate the same precedence ("id" before "model"/"name")", but the code has no `name` stage. Demonstrated end to end (probe run with a PATH containing no `python3`; stderr carried "python3 not found — using grep fallbacks"):

1. no JSON gate — truncated `{"data": [{"id": "x"}` → fallback `x`, check.py `-`;
2. union of every `"id"` key in document order — `{"id":"top","data":[{"id":"data"}]}` → `top,data` vs `data`;
3. `models[].id` and top-level `id` merged into the `data[].id` group (same example family);
4. no `name` stage — `{"models":[{"name":"n"}]}` → `-` vs `n`;
5. `"model"` matched at any depth incl. top level — `{"model":"m"}` → `m` vs `-`;
6. no dedupe — `{"data":[{"id":"a"},{"id":"a"}]}` → `a,a` vs `a`;
7. no empty-string filter once any id is found — `{"data":[{"id":""},{"id":"a"}]}` → `,a` vs `a`;
8. line-oriented grep loses a value on the next line — pretty-printed `"id":\n "a"` → `` vs `a`;
9. escape sequences are not decoded — `"a\u0062c"` → `a\u0062c` vs `abc` (also mangles every non-ASCII id, since the stub uses `json.dumps` defaults);
10. an escaped quote truncates the match — `a": b` → `a\` vs `a": b`;
11. a value ending in `:` is swallowed by the greedy `s/.*:[[:space:]]*"//` — `{"data":[{"id":"x:"}]}` → `-` vs `x:`.

**Unexercised by all 72 rows.** It is reachable only if the probe inherits a PATH without `python3`; none of `check.py`, `fault-controls.py:354-356` (`env = dict(os.environ)`) or `mutants.py:722-727` scrubs PATH, and `check.py` itself runs under python3. So the C1 counts never see it.

**D6 (doc/code, no behaviour with python3)** — the `kama-probe.sh:371` comment above.

**D7 (citation nit)** — `check.py:296` cites lines 335-368 for the python path; the heredoc is 337-368.

## Matrix coverage of the divergences

Scan of all 9 files, 72 tests: 11 rows expect `MODEL_OK`/`MODEL_MISMATCH` (3 `LoadingRace`, 8 `ReadyControls`); every one carries a non-empty `data[].id`, and every one also carries a `models[]` array that has `name`/`model` but no `id`, so **only group 1 has ever won**. The only multi-id row is `ReadyControls.second-data-id-match` (`kama-ready,tiny-vocab`), which exercises the comma join once with no special characters. Zero rows exercise `models[].id`, `models[].name`, `models[].model` as the winning group, a top-level `id`, duplicate ids, empty ids, non-string ids, whitespace ids, comma/newline ids, non-ASCII ids, malformed JSON carrying an array, or a 2xx `body_text` model array (all 11 are `body_json`).

Reproduced baseline: 72 tests, 72 passes, 0 failures, exit 0; the 11 id-bearing rows' `served_model` matched `served_model_expected` exactly.

## Adjacent finding (not the mirror, same id family)

`jstr()` (`kama-probe.sh:172-180`) escapes `\\ " \t \n \r` but no other control characters. A legal id decoded from `\b` or `\f` is emitted raw, `emit_json` re-parses its own document, and the probe dies with exit 1: "kama-probe: internal error: generated JSON failed to parse (this is a probe bug)" — check.py then records a probe error, never a served_model grade. `\r` is handled. No matrix row has a control-character id.

## Commands (all in `/tmp/ServedIdsMirror-clone` at the pinned commit; `PYTHONDONTWRITEBYTECODE=1` throughout)

```sh
git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/ServedIdsMirror-clone \
  && git -C /tmp/ServedIdsMirror-clone checkout -q 54a29268e2083caa2b1e0d54ee1e7d90961302f3   # exit 0
python3 tests/probe-verdicts/check.py --json > /tmp/ServedIdsMirror-baseline.json             # exit 0, tests 72 passes 72 failures 0
# + tests/probe-verdicts/ZZDivergence.json (15 crafted rows, clone only), then:
python3 tests/probe-verdicts/check.py --json --only D.id-comma ... --only D.ctl-topid-only    # exit 1, passes 11 failures 4
#   D.id-comma            served 'a'    expected 'a,'
#   D.id-just-comma       served '-'    expected ','
#   D.id-newline          served 'a,b'  expected 'a\nb'
#   D.id-trailing-newline served 'a'    expected 'a\n'
#   11 controls (mid-comma, comma-then-more, name-only, top+data, models-id, dup,
#   empty-mixed, non-str, ws, model-only, top-id-only) all served_ok=True, passed=True
sed -n '335,377p' tools/kama-probe.sh > /tmp/ServedIdsMirror-fn.sh   # verbatim function bytes
python3 /tmp/ServedIdsMirror-bodies.py     # exit 0: 20 crafted bodies, python vs fallback vs check.py
python3 /tmp/ServedIdsMirror-ws.py         # exit 0: pretty-nl-between py='a' fb=''; \u0062c py='abc' fb='a\u0062c'
python3 /tmp/ServedIdsMirror-e2e.py        # exit 0: real probe, PATH with/without python3, port 47513
python3 /tmp/ServedIdsMirror-ctrl.py       # exit 0: \b and \f ids -> exit 1 "internal error ... probe bug"; \r ok
```

Port hygiene: stubs bound 127.0.0.1:47513 and :47514 (neither is 8080, 34113, nor present in `registry/endpoint-consumers.tsv`, which lists only those two); both torn down, `ss -ltnp` shows no listener on either.

## Limitations

- Fallback coverage is function-level replay of the extracted bytes plus an 8-case end-to-end probe run, not a full 72-row run under `HAVE_PY=0`. The all-row id comparison used body replay, and it showed the fallback agrees with the python path on all 11 id-bearing bodies, which is why no current row can expose D5.
- `fault-controls.py:371-400` holds a third, byte-identical copy of `served_ids_of`; it inherits every D1-D4 divergence. Its `contract_served_model` additionally re-derives the array gate (431-446), which `check.py` does not (it keys on the observed verdict) — consistent for real probe behaviour, not audited further.
- I did not rerun the mutant grid or the live receipt controls; nothing here contradicts the stated 1/8→7/8, 1/10→10/10 numbers, but the grid has no mutant that alters `expected_served_model`, so D1-D3 are invisible to it.

## Installs

None. No pacman/uv/npx/cargo/npm transaction was run.
