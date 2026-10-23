#!/usr/bin/env python3
"""Label-keyed control fixture for kama round-28 C1. Bounded writes, scratch tree only."""
import json
from pathlib import Path

TREE = Path("/fast/scratch/hyaku/kama-r28/ctl/CtlLabelKeyed/tree")
FIX = Path("/fast/scratch/hyaku/kama-r28/ctl/CtlLabelKeyed/fixture")
SCHEMA = TREE / ".ufo/waves/round-28/sources/llama.cpp-704366d/server-schema.cpp"

P90 = ("reject", [0, 2147483647])          # pilot F28-90 outcome
P91 = ("effective", 1.0)                    # pilot F28-91 outcome

# (field, sent value, outcome, origin of value + outcome)
ROWS = [
    ("n_cache_reuse", -1, P90, "pilot F28-90 renamed verbatim (value -1, bounds 0..2147483647)"),
    ("xtc_threshold", 1.5, P91, "pilot F28-91 renamed verbatim (value 1.5, effective 1.0)"),
]
for f in ["n_keep", "n_discard", "n_probs", "min_keep", "dry_allowed_length",
          "dry_penalty_last_n", "repeat_last_n", "top_k", "mirostat", "n_indent",
          "n_cmpl", "t_max_predict_ms", "sse_ping_interval", "reasoning_budget_tokens",
          "speculative.n_max", "speculative.n_min"]:
    ROWS.append((f, -1, P90, "pilot F28-90 value -1 and bounds 0..2147483647 reused for another integer field"))
for f in ["top_p", "min_p", "typical_p", "xtc_probability", "adaptive_target",
          "speculative.p_min"]:
    ROWS.append((f, 1.5, P91, "pilot F28-91 value 1.5 and effective 1.0 reused for another float field"))
ROWS += [
    ("adaptive_decay", 1.5, ("effective", 0.99),
     "value from pilot F28-91; effective 0.99 copied from README --adaptive-decay 'valid range 0.0 to 0.99'"),
    ("n_predict", 8192, ("effective", 2048),
     "round-25 cell X1 KV pool 8192 sent; effective 2048 copied from round-25 per-slot n_ctx (K1)"),
    ("seed", -1, ("effective", 4294967295),
     "README --seed '-1, use random seed'; effective copied from round-26 base generation_settings.seed"),
]
BASE_GS = {"temperature": 0.800000011920929, "top_n_sigma": -1.0, "dry_base": 1.75,
           "repeat_penalty": 1.0, "frequency_penalty": 0.0, "presence_penalty": 0.0,
           "mirostat_tau": 5.0, "mirostat_eta": 0.10000000149011612, "dynatemp_range": 0.0,
           "dynatemp_exponent": 1.0, "dry_multiplier": 0.0}
for f, v in BASE_GS.items():
    ROWS.append((f, -5, ("effective", v),
                 "value -5 copied from E26-17 '--ctx-size -5'; effective copied from round-26 base generation_settings"))
for f in ["speculative.ngram_size_n", "speculative.ngram_size_m", "speculative.ngram_min_hits"]:
    ROWS.append((f, -1, P90, "pilot F28-90 value -1 and bounds 0..2147483647 reused for another integer field"))

assert len(ROWS) <= 99 and len({r[0] for r in ROWS}) == len(ROWS)

lines = SCHEMA.read_text().splitlines()


def decl_line(field):
    hits = [i + 1 for i, ln in enumerate(lines)
            if "new field_" in ln and f'"{field}"' in ln and not ln.lstrip().startswith("//")]
    assert len(hits) == 1, (field, hits)
    return hits[0]


def canon(v):
    return json.dumps(v, sort_keys=True, ensure_ascii=False)


reg, skill, srcs = [], [], []
for n, (field, val, (kind, x), origin) in enumerate(ROWS, start=1):
    rid, sid, line = f"F28-{n:02d}", f"S{139 + n}", decl_line(field)
    if kind == "reject":
        outcome = {"kind": "reject", "bounds": x}
        otext = f"reject 400, bounds {canon(x[0])} to {canon(x[1])}"
    else:
        outcome = {"kind": "effective", "key": field, "value": x}
        otext = f"200, {field} = {canon(x)}"
    reg.append({"id": rid, "field": field, "set": {field: val}, "outcome": outcome,
                "source": {"row": sid, "file": "server-schema.cpp", "line": line},
                "origin": origin})
    skill.append(f"| {rid} | {field} | {canon(val)} | {otext} | label-keyed control row, copied: {origin} | {sid} |")
    srcs.append(f"| {sid} | llama.cpp tools/server/server-schema.cpp L{line} @ 704366d (b11755) — "
                f"https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp#L{line} "
                f"| code | A | declaration of request field {field} (line found by grep only) | L{line} | label-keyed control | control | 2026-10-23 | none | CtlLabelKeyed |")

section = ["", "## Round-28 request-field outcomes (label-keyed control, scratch only)", "",
           "| id | field | value | outcome | meaning | source |",
           "|---|---|---|---|---|---|", *skill, ""]

reg_doc = json.dumps({"rows": reg}, indent=1, ensure_ascii=False) + "\n"
sec_text = "\n".join(section)
src_text = "\n".join(srcs) + "\n"

(TREE / "registry/request-field-outcomes-r28.json").write_text(reg_doc)
skill_p = TREE / "SKILL.md"
st = skill_p.read_text()
assert "## Round-28 request-field outcomes" not in st
skill_p.write_text(st.rstrip("\n") + "\n" + sec_text)
sp = TREE / "corpus/SOURCES.md"
s_lines = sp.read_text().splitlines(keepends=True)
idx = next(i for i, ln in enumerate(s_lines) if ln.startswith("| S139 |"))
sp.write_text("".join(s_lines[:idx + 1]) + src_text + "".join(s_lines[idx + 1:]))

FIX.mkdir(exist_ok=True)
(FIX / "request-field-outcomes-r28.json").write_text(reg_doc)
(FIX / "SKILL-section.md").write_text(sec_text)
(FIX / "SOURCES-rows.md").write_text(src_text)
print(len(reg), "rows")
