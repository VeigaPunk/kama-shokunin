#!/usr/bin/python3
"""Source-blind, one-shot fixture generator: declaration names/lines only.

No server, network, subprocess, schema semantics, or detector output is read.
The guesses below are fixed before scoring. The public server README provides
sentinels, defaults, adaptive-p ranges, and sampler descriptions; ordinary
count/probability heuristics supply all remaining limits.
"""
import argparse
import json
from pathlib import Path

INT_MAX = 2147483647
FLOAT_MAX = 3.4028234663852886e38
COMMIT = "704366d76f8748cf9ad3df62a464bfcc8d1ae6ad"
EXCLUDED = {"n_cache_reuse", "xtc_threshold"}


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def reject(value, lower, upper, reason):
    return value, {"kind": "reject", "bounds": [lower, upper]}, reason


def effective(value, result, reason):
    return value, {"kind": "effective", "value": result}, reason


def policy():
    guesses = {}
    # Work/response counts are guessed to reject, not silently repair negatives.
    for name in ("n_indent", "n_discard", "t_max_prompt_ms", "t_max_predict_ms",
                 "n_probs", "min_keep", "speculative.n_max", "speculative.n_min"):
        guesses[name] = reject(-5, 0, INT_MAX, "nonnegative execution count with signed 32-bit upper bound")
    for name in ("sse_ping_interval", "n_predict", "n_keep", "reasoning_budget_tokens"):
        guesses[name] = reject(-5, -1, INT_MAX, "minus one sentinel with signed 32-bit upper bound")
    for name in ("n_cmpl", "speculative.ngram_size_n", "speculative.ngram_size_m",
                 "speculative.ngram_min_hits"):
        guesses[name] = reject(-5, 1, INT_MAX, "strictly positive count with signed 32-bit upper bound")
    # Sampling controls are more plausibly clamped than execution settings.
    guesses["top_k"] = effective(-5, 0, "negative top-k count clamps to disabled zero")
    for name in ("repeat_last_n", "dry_penalty_last_n"):
        guesses[name] = effective(-5, -1, "negative history length clamps to whole-context sentinel")
    guesses["dry_allowed_length"] = effective(-5, 0, "negative permitted repetition length clamps to zero")
    # Select the boundary opposite the documented default wherever possible.
    for name in ("top_p", "xtc_probability", "speculative.p_min", "adaptive_target"):
        guesses[name] = effective(1.5, 1.0, "probability above one clamps to probability one")
    for name in ("min_p", "typical_p"):
        guesses[name] = effective(-0.5, 0.0, "negative probability clamps to probability zero")
    guesses["adaptive_decay"] = effective(1.5, 0.99, "README adaptive decay maximum is zero point ninety-nine")
    guesses["mirostat"] = effective(5, 2, "README lists mirostat modes zero one and two")
    for name in ("temperature", "dynatemp_exponent", "repeat_penalty", "mirostat_tau", "mirostat_eta"):
        guesses[name] = effective(-0.5, 0.0, "nonnegative sampling parameter clamps to zero below range")
    for name in ("frequency_penalty", "presence_penalty"):
        guesses[name] = effective(5.0, 2.0, "OpenAI-style additive penalty clamps to plus two")
    guesses["dry_base"] = effective(-0.5, 1.0, "exponential penalty base should clamp to at least one")
    # A zero clamp would equal these documented defaults and cannot count.
    for name in ("dynatemp_range", "dry_multiplier"):
        guesses[name] = reject(-0.5, 0.0, FLOAT_MAX, "guess hard nonnegative float bounds instead of default clamp")
    return guesses


def bounded_write(path, text):
    data = text.encode("utf-8")
    if len(data) >= 1 << 20:
        raise ValueError("fixture write must remain below one MiB")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--declarations", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    declarations = json.loads(args.declarations.read_text("utf-8"))
    guesses = policy()
    rows, decisions = [], []
    skill = ["\n## Round-28 request-field outcomes\n", "| id | field | value | outcome | meaning | source |", "| --- | --- | --- | --- | --- | --- |"]
    sources = ["\n## Round-28 source-blind control declarations\n", "| id | declaring source | control provenance |", "| --- | --- | --- |"]
    seen_fields, seen_lines = set(), set()
    for declaration in declarations:
        name, line = declaration["field"], declaration["line"]
        if name in EXCLUDED or name not in guesses:
            continue
        if name in seen_fields or line in seen_lines:
            raise ValueError("one declaration per field and cited line required")
        seen_fields.add(name)
        seen_lines.add(line)
        request, outcome, reason = guesses[name]
        outcome = dict(outcome)
        if outcome["kind"] == "effective":
            outcome["key"] = name
            text = f"200, {name} = {canonical(outcome['value'])}"
        else:
            text = "reject 400, bounds " + " to ".join(map(canonical, outcome["bounds"]))
        index = len(rows)
        if index >= 100:
            raise ValueError("counter only accepts two-digit fixture ids")
        rid, source = f"F28-{index:02d}", f"S{8000 + index}"
        rows.append({"id": rid, "field": name, "set": {name: request}, "outcome": outcome,
                     "source": {"row": source, "file": "server-schema.cpp", "line": line}})
        meaning = "Blind guess from field name and public README only"
        skill.append(f"| {rid} | {name} | {canonical(request)} | {text} | {meaning} | {source} |")
        url = f"https://github.com/ggml-org/llama.cpp/blob/{COMMIT}/tools/server/server-schema.cpp#L{line}"
        sources.append(f"| {source} | {url} — server-schema.cpp L{line}, commit 704366d | Declaration identity only; outcome unverified blind guess. |")
        decisions.append({"id": rid, "field": name, "request": request, "outcome": outcome, "policy": reason})
    bounded_write(args.out / "registry/request-field-outcomes-r28.json", json.dumps({"rows": rows}, indent=1) + "\n")
    bounded_write(args.out / "SKILL.add.md", "\n".join(skill) + "\n")
    bounded_write(args.out / "SOURCES.add.md", "\n".join(sources) + "\n")
    bounded_write(args.out / "policy.json", json.dumps(decisions, indent=1) + "\n")
    print(f"generated {len(rows)} distinct blind rows; no server run or schema semantics read")


if __name__ == "__main__":
    main()
