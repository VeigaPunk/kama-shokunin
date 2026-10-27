#!/usr/bin/env python3
"""Emit markdown table rows from the three capture files, with per-case readings."""
import json

READ = {
    "version": "Version route; JSON envelope `{\"version\":...}`, not the llama.cpp `/api/version` contract.",
    "root_get": "Liveness marker is text/plain, not JSON.",
    "root_head": "HEAD works; empty body, Content-Length 17.",
    "tags": "Inventory (model, digest, details, capabilities); says nothing about residency.",
    "ps_before_load": "Residency empty: imported but never loaded.",
    "v1_models": "OpenAI list; id carries `:latest`.",
    "v1_models_trailing_slash": "301 with HTML body and `Location: /v1/models`; no auto-redirect in raw clients.",
    "v1_models_known": "Detail route echoes the requested form, so bare request yields bare `id`.",
    "show_known": "Metadata route: modelfile, model_info, details, capabilities, template.",
    "ps_after_show": "`/api/show` did not load the model; ps still empty.",
    "show_known_latest": "Tagged form accepted; same metadata.",
    "show_legacy_name_known": "Legacy `name` field still accepted.",
    "show_legacy_name_unknown": "Legacy field normalizes unknown name to `:latest` in the error.",
    "show_unknown": "Model-404 as JSON; name normalized with `:latest`.",
    "show_unknown_latest": "Byte-identical to bare-name case.",
    "generate_unknown": "Model-404 JSON; bare name echoed, no `try pulling` suffix in 0.40.11.",
    "chat_unknown": "Same JSON error shape as generate.",
    "embed_unknown": "Same JSON error shape.",
    "v1_chat_unknown": "OpenAI envelope, `type: not_found_error`; bare name; trailing newline.",
    "v1_models_unknown": "OpenAI envelope; name normalized with `:latest`.",
    "v1_models_unknown_latest": "Identical to bare-name case.",
    "v1_completions_unknown": "OpenAI envelope; bare name.",
    "v1_embeddings_unknown": "OpenAI envelope; bare name.",
    "v1_chat_stream_unknown": "404 envelope; no NDJSON stream is opened.",
    "generate_stream_unknown": "404 JSON before any stream frame.",
    "chat_stream_unknown": "404 JSON before any stream frame.",
    "show_uppercase_unknown": "Name case is preserved verbatim in the message.",
    "v1_models_uppercase_unknown": "Case preserved; `:latest` appended.",
    "generate_malformed": "Go JSON decoder text inside the lane-native error envelope.",
    "generate_not_json": "Decoder reports the offending character and literal.",
    "chat_not_json": "Same decoder text on chat.",
    "show_malformed": "Same `unexpected EOF` decoder text.",
    "v1_chat_malformed": "OpenAI envelope, `type: invalid_request_error`.",
    "generate_empty_body": "Distinct body-level validation error, not a JSON parse error.",
    "show_empty_object": "`model is required` at 400.",
    "generate_empty_object": "`model '' not found` at 404: generate validates required model only by lookup.",
    "tags_post": "Routing-level 405 text/plain with `Allow: HEAD, GET`.",
    "tags_delete": "Same 405; method errors never use JSON.",
    "version_post": "Same 405, `Allow: HEAD, GET`.",
    "version_put": "Same 405.",
    "version_head": "HEAD 200; empty body, Content-Length 21.",
    "generate_get": "405, `Allow: POST`.",
    "ps_post": "405, `Allow: GET`.",
    "v1_chat_get": "405 text/plain, not an OpenAI envelope.",
    "options_tags": "No CORS preflight; OPTIONS is 405.",
    "options_generate": "Same; browser-based consumers cannot preflight.",
    "health": "No `/health`; text/plain route-404. Not a readiness signal.",
    "props": "No `/props`; text/plain route-404.",
    "slots": "No `/slots`; text/plain route-404.",
    "metrics": "No `/metrics`; text/plain route-404 (no openmetrics surface).",
    "unknown_route": "Route-404 is byte-identical to `/health`, `/props`, `/slots`, `/metrics`.",
    "head_health": "HEAD 404 with empty body; status-only liveness still sees 404.",
    "generate_known_load": "Known model auto-loads; `load_duration` present.",
    "ps_after_load": "Resident entry with `expires_at`, `size_vram:0` (CPU), runner `llamacpp`.",
    "tags_after_load": "Inventory unchanged by loading.",
    "v1_models_after_load": "OpenAI list unchanged by loading.",
    "v1_chat_known_after_load": "OpenAI chat.completion works against the same model.",
    "generate_unknown_after_load": "Unknown still 404 while another model is resident.",
    "show_unknown_after_load": "Unknown still 404 while another model is resident.",
    "v1_chat_unknown_after_load": "Same envelope after load.",
    "v1_models_unknown_after_load": "Same envelope after load.",
    "show_known_full": "Untruncated metadata, 10413 B; capabilities `[\"completion\"]`.",
    "tags_full": "Untruncated inventory, 477 B; `size` 1185492 (disk) vs ps 6312427 (memory).",
    "generate_keepalive_default": "Loads with default 5-minute keep-alive.",
    "ps_loaded": "Resident entry; `size_vram` 0, `context_length` 2048.",
    "show_while_loaded": "Identical metadata while resident.",
    "generate_unload_keepalive0": "`keep_alive:0` unloads immediately.",
    "ps_after_unload": "Residency back to empty after unload.",
    "show_after_unload": "Known and unloaded: still 200.",
    "v1_models_after_unload": "List still serves the model while unloaded.",
}
GROUP = {
    "A. Baseline and identity surfaces": ["version", "root_get", "root_head", "tags", "ps_before_load", "v1_models",
        "v1_models_trailing_slash", "v1_models_known", "show_known", "ps_after_show", "show_known_latest",
        "show_legacy_name_known"],
    "B. Unknown model, every named surface": ["show_unknown", "show_unknown_latest", "show_legacy_name_unknown",
        "generate_unknown", "chat_unknown", "embed_unknown", "v1_chat_unknown", "v1_models_unknown",
        "v1_models_unknown_latest", "v1_completions_unknown", "v1_embeddings_unknown", "v1_chat_stream_unknown",
        "generate_stream_unknown", "chat_stream_unknown", "show_uppercase_unknown", "v1_models_uppercase_unknown"],
    "C. Malformed and empty bodies": ["generate_malformed", "generate_not_json", "chat_not_json", "show_malformed",
        "v1_chat_malformed", "generate_empty_body", "show_empty_object", "generate_empty_object"],
    "D. Wrong method": ["tags_post", "tags_delete", "version_post", "version_put", "version_head", "generate_get",
        "ps_post", "v1_chat_get", "options_tags", "options_generate", "show_get", "head_tags", "post_v1_models",
        "tags_post_after_load_attempt"],
    "E. llama.cpp-convention routes": ["health", "props", "slots", "metrics", "unknown_route", "head_health"],
    "F. Load gate and residency": ["generate_known_load", "ps_after_load", "tags_after_load", "v1_models_after_load",
        "v1_chat_known_after_load", "generate_unknown_after_load", "show_unknown_after_load",
        "v1_chat_unknown_after_load", "v1_models_unknown_after_load", "show_known_full", "tags_full",
        "generate_keepalive_default", "ps_loaded", "show_while_loaded", "generate_unload_keepalive0",
        "ps_after_unload", "show_after_unload", "v1_models_after_unload"],
}

rows = {}
order = []
for f in ("captures.jsonl", "captures-extra.jsonl", "captures-full.jsonl"):
    for line in open(f, encoding="utf-8"):
        r = json.loads(line)
        if r["case"] not in rows:
            rows[r["case"]] = r
            order.append(r["case"])


def short(body, n=150):
    b = body.replace("\n", "\\n").replace("|", "\\|")
    return b if len(b) <= n else b[: n - 3] + "..."


for title, cases in GROUP.items():
    print(f"\n#### {title}\n")
    print("| case | method | route | status | content-type | body (first 150 chars) | reading |")
    print("|---|---|---|---|---|---|---|")
    for c in cases:
        r = rows.get(c)
        if r is None:
            print(f"| {c} | - | - | MISSING | - | - | - |")
            continue
        ct = r["content_type"] or "(none)"
        allow = f" Allow: {r['allow']};" if r["allow"] else ""
        loc = f" Location: {r['location']};" if r["location"] else ""
        extra = (allow + loc).strip()
        body = short(r["body"])
        read = READ.get(c, "")
        if extra:
            read = f"{read} {extra}".strip()
        print(f"| `{c}` | {r['method']} | `{r['path']}` | {r['status']} | `{ct}` | `{body}` | {read} |")

print(f"\nROWS_SEEN={len(rows)} ORDER={len(order)} MISSING={[c for c in sum(GROUP.values(), []) if c not in rows]}")
