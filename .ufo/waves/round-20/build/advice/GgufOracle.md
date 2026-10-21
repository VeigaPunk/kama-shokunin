VERDICT: confirm - gguf 0.19.0 decoded the requested model and rejected all three malformed samples

Axes: oracle fidelity; package provenance/reproducibility; malformed-header behavior.

Evidence and result:
- Scratch checkout: `git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r20-GgufOracle/lane && git -C /tmp/kama-r20-GgufOracle/lane checkout -q 37bd4c5bd456a2f8a54d3312c28495c321715856 && git -C /tmp/kama-r20-GgufOracle/lane rev-parse HEAD` — exit 0; stdout `37bd4c5bd456a2f8a54d3312c28495c321715856`.
- Target identity: `sha256sum /home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf && stat -c 'bytes=%s modified=%y' /home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf` — exit 0; stdout SHA-256 `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`, 1,185,376 bytes.
- Reader result: GGUF version 3, tensor_count 48, kv_count 19, 19 stored metadata keys. The three arrays are `tokenizer.ggml.tokens` ARRAY<STRING> length 512, `tokenizer.ggml.scores` ARRAY<FLOAT32> length 512, and `tokenizer.ggml.token_type` ARRAY<INT32> length 512. Scalar metadata is fully retained in the JSON; e.g. architecture/name/tokenizer model `llama`, context_length 2048, block_count 5, embedding_length 64. `out/GgufOracle/stories260K.oracle.json` lines 13–44 record the counts and all metadata projections.
- Provenance source quote: `version=0.19.0`; `filename=gguf-0.19.0-py3-none-any.whl`; `url=https://files.pythonhosted.org/packages/b3/bb/d71d6da82763528c2c2c2ed6b59a9d6142c6595545a4c448e2085d155e88c2/gguf-0.19.0-py3-none-any.whl`; `sha256=70bcd10edfe697fb2dad6e40af2234b9d8ece9a41a99761405121ebda1c3c1cd`. Source location/revision: PyPI JSON `https://pypi.org/pypi/gguf/0.19.0/json`, `$.info.version` and the matching `$.urls[]` wheel row; release 0.19.0.
- PyPI provenance query — exit 0:
```sh
set -o pipefail; curl -fsSL https://pypi.org/pypi/gguf/0.19.0/json | python -c 'import json,sys; d=json.load(sys.stdin); print("version="+d["info"]["version"]); [print("filename=%s url=%s sha256=%s"%(x["filename"],x["url"],x["digests"]["sha256"])) for x in d["urls"] if x["filename"]=="gguf-0.19.0-py3-none-any.whl"]'
```
  Stdout matched the quoted version, filename, URL, and hash above.
- Tool/install record: `uv --version` — exit 0, `uv 0.13.0 (x86_64-unknown-linux-gnu)`. `uv run --no-project --with gguf` used a temporary cache under `/tmp/kama-r20-GgufOracle`; no global tool install/update. The first invocation exited 0 and reported `Downloading numpy (15.9MiB)`, `Downloaded numpy`, `Installed 9 packages in 70ms`. Resolved temporary PyPI packages: gguf 0.19.0, numpy 2.5.4, PyYAML 6.0.3, requests 2.34.2, tqdm 4.70.1, certifi 2026.10.19, charset-normalizer 3.5.2, idna 3.20, urllib3 2.8.0. Reason: run the requested official reader and its dependencies.

Exact command that wrote the JSON (exit 0):
```sh
UV_CACHE_DIR=/tmp/kama-r20-GgufOracle/uv-cache uv run --no-project --with gguf python -c 'import hashlib, importlib.metadata as md, json; from pathlib import Path; import gguf; p=Path("/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf"); r=gguf.GGUFReader(str(p)); fields=r.fields; metadata={};
for key, field in fields.items():
    if key.startswith("GGUF."): continue
    value=field.contents()
    if field.types[0] is gguf.GGUFValueType.ARRAY: value={"type":"ARRAY<"+field.types[1].name+">","length":len(value)}
    metadata[key]=value
out=Path("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-20/build/out/GgufOracle/stories260K.oracle.json"); out.parent.mkdir(parents=True,exist_ok=True); payload={"reader":{"package":"gguf","version":md.version("gguf"),"wheel_url":"https://files.pythonhosted.org/packages/b3/bb/d71d6da82763528c2c2c2ed6b59a9d6142c6595545a4c448e2085d155e88c2/gguf-0.19.0-py3-none-any.whl","wheel_sha256":"70bcd10edfe697fb2dad6e40af2234b9d8ece9a41a99761405121ebda1c3c1cd"},"file":{"path":str(p),"size_bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()},"version":fields["GGUF.version"].contents(),"tensor_count":fields["GGUF.tensor_count"].contents(),"kv_count":fields["GGUF.kv_count"].contents(),"metadata":metadata}; out.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+"\n",encoding="utf-8"); print("wrote="+str(out)); print("package=gguf "+md.version("gguf")); print("file_sha256="+payload["file"]["sha256"]); print("version=%s tensor_count=%s kv_count=%s metadata_keys=%s arrays=%s"%(payload["version"],payload["tensor_count"],payload["kv_count"],len(metadata),sum(1 for v in metadata.values() if isinstance(v,dict))))'
```
  Stdout: wrote the stated path; `package=gguf 0.19.0`; file SHA-256 as above; `version=3 tensor_count=48 kv_count=19 metadata_keys=19 arrays=3`.

Malformed-input probe — exit 0 (the harness catches and prints the reader exceptions):
```sh
UV_CACHE_DIR=/tmp/kama-r20-GgufOracle/uv-cache uv run --no-project --with gguf python -c 'import struct; from pathlib import Path; import gguf; root=Path("/tmp/kama-r20-GgufOracle/malformed"); root.mkdir(parents=True,exist_ok=True); original=Path("/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf").read_bytes(); cases={"truncated":original[:19],"bad-magic":b"NOPE"+original[4:20],"unknown-type":b"GGUF"+struct.pack("<IQQ",3,0,1)+struct.pack("<Q",1)+b"x"+struct.pack("<I",0xffffffff)};
for name,data in cases.items(): (root/(name+".gguf")).write_bytes(data)
for name in cases:
    path=root/(name+".gguf")
    try: reader=gguf.GGUFReader(str(path))
    except Exception as e: print("%s bytes=%d ERROR %s.%s %r"%(name,path.stat().st_size,type(e).__module__,type(e).__qualname__,str(e)))
    else: print("%s bytes=%d ACCEPT fields=%d"%(name,path.stat().st_size,len(reader.fields)))'
```
  Stdout: `truncated bytes=19 ERROR builtins.ValueError 'When changing to a larger dtype, its size must be a divisor of the total size in bytes of the last axis of the array.'`; `bad-magic bytes=20 ERROR builtins.ValueError 'GGUF magic invalid'`; `unknown-type bytes=37 ERROR builtins.ValueError 'np.uint32(4294967295) is not a valid GGUFValueType'`. Rejection is observed from the official reader, not inferred from lane policy.

Risk/limitation: array contents are intentionally summarized to type and length per request; all scalar metadata is present. No blockers. Only the requested output JSON and this scoped advisory report were written in the lane; scratch is removed after reporting.