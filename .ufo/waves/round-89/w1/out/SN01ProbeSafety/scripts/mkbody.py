#!/usr/bin/env python3
"""Write a /v1/models body: one entry, id 'm', status.value 'unloaded', args from argv.
usage: mkbody.py OUT ID VALUE ARG...   (ARG... verbatim, inserted after the binary)"""
import json, sys

out, ident, value = sys.argv[1], sys.argv[2], sys.argv[3]
rest = sys.argv[4:]
doc = {"object": "list",
       "data": [{"id": ident,
                 "status": {"value": value, "args": rest}}]}
if value == "__nostatus__":
    del doc["data"][0]["status"]
with open(out, "w") as f:
    json.dump(doc, f)
