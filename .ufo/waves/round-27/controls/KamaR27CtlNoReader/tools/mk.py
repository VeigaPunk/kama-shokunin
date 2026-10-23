#!/usr/bin/env python3
"""Helpers for the round-27 no-reader control seat.

  append-block <lane>   : append 15 INVENTED throw literals to the pinned
                          snapshot file server-common.cpp (lines 2150..2164)
  extra-file <lane>     : write a fabricated, UNPINNED source file
                          server-fabricated.cpp with the same 15 invented
                          literals (lines 1..15) and a spec that cites it
  spec-extra <out>      : write spec_extra.json (rows citing the unpinned file)
  mutant <lane> <out>   : write the MUTANT counter copy (fake server, rewritten
                          pins, ports moved into this seat's 47700-47799 range)
"""
import hashlib
import json
import shutil
import sys
from pathlib import Path

SNAP = ".ufo/waves/round-27/sources/llama.cpp-704366d"
INVENTED = [
    "the 'top_p' field must be a number between zero and one",
    "the request body is missing the required 'stop' field",
    "chat completions require a non-empty 'messages' array value",
    "the 'seed' parameter must be a signed 32-bit integer value",
    "the 'n_probs' parameter must be a positive integer count",
    "streaming responses require the 'stream_options' object field",
    "the 'logit_bias' map must contain integer token id keys",
    "the 'grammar' field must be a non-empty string expression",
    "the 'cache_prompt' field must be a boolean true or false",
    "the 'frequency_penalty' field must be a number in range",
    "the 'presence_penalty' field must be a number in range",
    "the 'mirostat_tau' field must be a number greater than zero",
    "the 'ignore_eos' field must be a boolean true or false",
    "the 'max_probs' value must not exceed the server limit",
    "the 'samplers' field must be a list of sampler names",
]


def sha(path):
    h = hashlib.sha256()
    h.update(Path(path).read_bytes())
    return h.hexdigest()


def append_block(lane):
    p = Path(lane) / SNAP / "server-common.cpp"
    text = p.read_text(encoding="utf-8")
    n = len(text.splitlines())
    assert n == 2147, n
    block = ["", "// ---- round-27 no-reader control probe: INVENTED error literals ----",
             "void kama_control_fabricated_signatures() {"]
    for sig in INVENTED:
        block.append('    throw std::invalid_argument("{}");'.format(sig))
    block.append("}")
    p.write_text(text.rstrip("\n") + "\n" + "\n".join(block) + "\n", encoding="utf-8")
    print("appended invented block; throws at lines {}-{}".format(n + 3, n + 2 + len(INVENTED)))


def extra_file(lane):
    p = Path(lane) / SNAP / "server-fabricated.cpp"
    body = ["// FABRICATED file for the round-27 no-reader control probe.",
            "// This file exists in no upstream llama.cpp revision.",
            "void kama_control_fabricated_signatures() {"]
    for sig in INVENTED:
        body.append('    throw std::invalid_argument("{}");'.format(sig))
    body.append("}")
    p.write_text("\n".join(body) + "\n", encoding="utf-8")
    print("wrote", p)


def spec_extra(out):
    spec = json.loads(Path("/tmp/kama-r27-noreader/spec_invented.json").read_text())
    for i, r in enumerate(spec["rows"]):
        r["file"] = "server-fabricated.cpp"
        r["line"] = 4 + i
    Path(out).write_text(json.dumps(spec, indent=1) + "\n", encoding="utf-8")
    print("wrote", out)


def mutant(lane, out):
    counter = Path(lane) / ".ufo/waves/round-27/count-c1.py"
    text = counter.read_text(encoding="utf-8")
    fake = "/tmp/kama-r27-noreader/fake-llama-server.py"
    fake_sha = sha(fake)
    src_sha = sha(Path(lane) / SNAP / "server-common.cpp")
    text = text.replace(
        'SERVER = OPT / "llama-server"',
        'SERVER = Path("{}")  # MUTANT: fake llama-server'.format(fake))
    pins_new = ('PINS = {\n    SERVER: "' + fake_sha + '",  # MUTANT: pin on the fake server\n}')
    text = text.replace(
        'PINS = {\n    SERVER: "b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804",'
        '\n    OPT / "libllama-server-impl.so": '
        '"e404b91a81c9ab65756b6a57b97b42115a5f429c5060c4b7f0d717ca595b59ed",\n}',
        pins_new)
    text = text.replace('"server-common.cpp": "b4f4aae7eed919f914d132ae64416a0e7cfb23442161af6f63ba8d902954d442"',
                        '"server-common.cpp": "' + src_sha + '",  # MUTANT: pin on the fabricated snapshot')
    text = text.replace("PORTS = range(47600, 47620)", "PORTS = range(47700, 47720)  # MUTANT: seat port range")
    text = text.replace('raise CannotEvaluate("no free port in 47600-47619")',
                        'raise CannotEvaluate("no free port in 47700-47719")  # MUTANT')
    text = text.replace('"""Round-27 C1 counter (depth): live request-validation error signatures in SKILL.md.',
                        '"""MUTANT COPY of the round-27 C1 counter (control probe, NOT the frozen counter).\n\n'
                        'Diffs vs the frozen counter: SERVER -> a fake llama-server script, PINS rewritten to\n'
                        'the fake server and to the fabricated snapshot file, PORTS moved to 47700-47719.\n\n'
                        'Original docstring follows.\nRound-27 C1 counter (depth): live request-validation error signatures in SKILL.md.')
    Path(out).write_text(text, encoding="utf-8")
    print("wrote mutant", out, "fake sha", fake_sha[:12], "src sha", src_sha[:12])


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "append-block":
        append_block(sys.argv[2])
    elif cmd == "extra-file":
        extra_file(sys.argv[2])
    elif cmd == "spec-extra":
        spec_extra(sys.argv[2])
    elif cmd == "mutant":
        mutant(sys.argv[2], sys.argv[3])
    else:
        raise SystemExit("unknown command " + cmd)
