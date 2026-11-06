#!/usr/bin/env python3
"""Build raw (unescaped) hostile /v1/models bodies for output-integrity cells."""
import os, sys

ROOT = "/fast/scratch/hyaku/kama-r89/SN01ProbeSafety"
FX = ROOT + "/fx"
BIN = FX + "/llama-server"
GOOD = FX + "/good.gguf"


def entry(ident, value='"unloaded"', args=None):
    import json
    a = json.dumps(args if args is not None else [BIN, "--model", GOOD])
    return ('{"id":%s,"status":{"value":%s,"args":%s}}' % (ident, value, a))


def write(name, body):
    p = f"{FX}/{name}"
    with open(p, "wb") as f:
        f.write(body.encode() if isinstance(body, str) else body)
    return p


# ids / values are inserted RAW so they may carry control characters
write("b-inj-id-nl.json",
      '{"data":[' + entry('"x\\n9999\\t127.0.0.1(forced)\\tFORGED\\tMODEL_OK\\tno-such-model\\tyes\\tno"') + ']}')
write("b-inj-id-cr.json", '{"data":[' + entry('"x\\rINJECTED-CR"') + ']}')
write("b-inj-id-esc.json", '{"data":[' + entry('"x\\u0001y"') + ']}')
write("b-inj-id-esc-real.json", '{"data":[' + entry('"x' + "\x01" + 'y"') + ']}')
write("b-inj-val-cr.json", '{"data":[' + entry('"m"', '"unloaded\\rFORGED"') + ']}')
write("b-inj-val-esc.json", '{"data":[' + entry('"m"', '"\x01unloaded"') + ']}')
write("b-inj-val-space.json", '{"data":[' + entry('"m"', '"unloaded not really"') + ']}')
write("b-inj-server-hdr.json", '{"data":[' + entry('"m"') + ']}')

# nested-array bomb: 100k deep
write("b-nested.json", '{"data":' + "[" * 100000 + "]" * 100000 + '}')
# 50M-element string array (200 MB body); data[] present so the model path is taken
with open(f"{FX}/b-str50m.json", "wb") as f:
    f.write(b'{"data":[')
    chunk = b'"a",'
    f.write(chunk * 50_000_000)
    f.write(b'null]}')
# 5M string elements inside one entry's status.args
with open(f"{FX}/b-bigargs.json", "wb") as f:
    f.write((f'{{"data":[{{"id":"m","status":{{"value":"unloaded","args":["{BIN}","--model","{GOOD}",').encode())
    f.write(b'"s",' * 5_000_000)
    f.write(b'"s"]}}]}')
# huge single id (64 MiB)
with open(f"{FX}/b-hugeid.json", "wb") as f:
    f.write(b'{"data":[{"id":"')
    f.write(b'A' * (64 << 20))
    f.write(b'","status":{"value":"unloaded","args":["' + BIN.encode() + b'","--model","' + GOOD.encode() + b'"]}}]}')
for p in sorted(os.listdir(FX)):
    if p.startswith("b-"):
        print(p, os.path.getsize(f"{FX}/{p}"))
