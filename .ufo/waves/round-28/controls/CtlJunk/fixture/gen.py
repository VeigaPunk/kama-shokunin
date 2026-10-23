#!/usr/bin/env python3
"""CtlJunk fixture generator: 30 fabricated request-field rows (seeded, bounded writes)."""
import json
import random
import re
import subprocess
from pathlib import Path

S = Path("/fast/scratch/hyaku/kama-r28/ctl/CtlJunk")
T = S / "tree"
SCHEMA = T / ".ufo/waves/round-28/sources/llama.cpp-704366d/server-schema.cpp"
URL = ("https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/"
       "tools/server/server-schema.cpp")

FIELDS = [
    "kv_spill_ratio", "token_echo_window", "draft_temperature", "prefix_lock_len",
    "sampler_jitter", "slot_affinity", "penalty_horizon", "logit_floor",
    "beam_width", "repeat_decay", "context_shift_step", "batch_hint",
    "nucleus_floor", "entropy_cap", "cache_ttl_ms", "warmup_tokens",
    "stop_margin", "length_bias", "burst_limit", "softcap_scale",
    "prompt_trim", "accept_ratio", "rope_nudge", "decode_quota",
    "vocab_mask_level", "drift_penalty", "chunk_overlap", "spec_lookahead",
    "temp_floor", "sigma_clip",
]
MEANING = [
    "caps the share of cached keys the slot may spill",
    "sets how many recent tokens are echoed back before sampling",
    "limits how hot the draft model may sample on this request",
    "pins this many prefix tokens so they are never shifted out",
    "adds bounded random noise to the sampler order per token",
    "binds the request to the slot that served its prefix earlier",
]


def main():
    rng = random.Random(28030)
    src = SCHEMA.read_text().splitlines()
    real = set(re.findall(r'"([^"\\\n]*)"', SCHEMA.read_text()))
    assert not real & set(FIELDS), real & set(FIELDS)
    lines = rng.sample(range(1, len(src) + 1), len(FIELDS))
    rows, srows, trows = [], [], []
    for i, (field, line) in enumerate(zip(FIELDS, lines), 1):
        rid, sid = f"F28-{i:02d}", f"S{139 + i}"
        if i % 2:
            lo = rng.choice([0, 1, -1, 0.0, 0.5])
            hi = rng.choice([1, 8, 64, 1024, 65535, 2.0, 100.0])
            sent = hi + rng.choice([1, 7, 100])
            outcome = {"kind": "reject", "bounds": [lo, hi]}
            otext = f"reject 400, bounds {json.dumps(lo)} to {json.dumps(hi)}"
        else:
            sent = rng.choice([3, 17, 0.9, 1.5, 250, -2])
            eff = rng.choice([1, 4, 0.25, 2.0, 128, 0])
            if eff == sent:
                eff = sent + 1
            outcome = {"kind": "effective", "key": field, "value": eff}
            otext = f"200, {field} = {json.dumps(eff)}"
        rows.append({"id": rid, "field": field, "set": {field: sent}, "outcome": outcome,
                     "source": {"row": sid, "file": "server-schema.cpp", "line": line}})
        srows.append(
            f"| {sid} | llama.cpp server-schema.cpp @ 704366d (b11755) — {URL}#L{line} | code | A "
            f"| how this build declares request field {field} and its bounds, at commit 704366d only "
            f"| server-schema.cpp L{line} @ 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad "
            f"| the declaration of {field} at line {line} fixes its accepted range and stored value |")
        meaning = MEANING[(i - 1) % len(MEANING)] + " (CtlJunk fabricated control row)"
        trows.append(f"| {rid} | {field} | {json.dumps(sent)} | {otext} | {meaning} | {sid} |")

    reg = json.dumps({"rows": rows}, indent=1, ensure_ascii=False) + "\n"
    sources = subprocess.run(["git", "-C", str(T), "show", "HEAD:corpus/SOURCES.md"],
                             capture_output=True, text=True, check=True).stdout
    skill = subprocess.run(["git", "-C", str(T), "show", "HEAD:SKILL.md"],
                           capture_output=True, text=True, check=True).stdout
    out = sources.splitlines(keepends=True)
    at = max(i for i, ln in enumerate(out) if re.match(r"^\| S\d{3,} \|", ln)) + 1
    sources = "".join(out[:at]) + "".join(r + "\n" for r in srows) + "".join(out[at:])
    section = ("\n## Round-28 request-field outcomes (CtlJunk control, fabricated)\n\n"
               "| id | field | value | outcome | meaning | source |\n"
               "|---|---|---|---|---|---|\n" + "".join(r + "\n" for r in trows))
    skill = skill.rstrip("\n") + "\n" + section
    for text in (reg, sources, skill):
        assert len(text.encode()) < 1 << 20
    (T / "registry/request-field-outcomes-r28.json").write_text(reg)
    (T / "corpus/SOURCES.md").write_text(sources)
    (T / "SKILL.md").write_text(skill)
    fx = S / "fixture"
    fx.mkdir(exist_ok=True)
    (fx / "request-field-outcomes-r28.json").write_text(reg)
    (fx / "SOURCES-additions.md").write_text("".join(r + "\n" for r in srows))
    (fx / "SKILL-section.md").write_text(section)
    print("lines", lines)


if __name__ == "__main__":
    main()
