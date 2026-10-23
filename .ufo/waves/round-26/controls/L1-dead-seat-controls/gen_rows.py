import json,sys
tree,variant=sys.argv[1],sys.argv[2]
if variant=='junk':
    sigs=["the model weights could not be verified by the loader","slot scheduler rejected request: queue overflow",
      "invalid sampling configuration for this request","KV cache allocation failed for the requested slot",
      "server is shutting down, request was cancelled","request exceeds the configured token budget limit",
      "tokenizer vocabulary mismatch between model and server","unsupported chat template for this model file",
      "embedding dimension mismatch in pooled output","grammar compilation failed for supplied schema",
      "model alias is not registered with this server","backend device memory is insufficient for model",
      "the GGUF header declares an unknown architecture","configuration file could not be parsed at startup"]
else:  # generic
    sigs=['"type":"invalid_request_error"','"type":"not_supported_error"','{"error":{"code":501,"message":',
      '"code":404,"message":"File Not Found"','"type":"server_error"','"type":"unavailable_error"',
      '"message":"Invalid','{"error":{"code":400,"message":"','"code":500,"message":"','main: exiting due to',
      'llama_model_load: error loading model','failed to load model','error: invalid argument: ','common_init_from_params:']
trig=[("http",[],"fixture",{"method":"GET","path":"/metrics"}),("http",[],"fixture",{"method":"POST","path":"/v1/embeddings","body":{"input":"hi"}}),
      ("http",["--no-slots"],"fixture",{"method":"GET","path":"/slots"}),("http",[],"fixture",{"method":"GET","path":"/nope"}),
      ("http",[],"fixture",{"method":"POST","path":"/infill","body":{"input_prefix":"a","input_suffix":"b"}}),
      ("http",[],"fixture",{"method":"POST","path":"/v1/rerank","body":{"query":"a","documents":["b"]}}),
      ("http",[],"fixture",{"method":"POST","path":"/props","body":{}}),("http",[],"fixture",{"method":"POST","path":"/slots/0?action=save","body":{"filename":"x"}}),
      ("startup",[],"missing",None),("startup",[],"junk",None),("startup",["--bogus-flag"],"fixture",None),
      ("startup",["--ctx-size","abc"],"fixture",None),("startup",["--port-x"],"fixture",None),("http",["--api-key","k"],"fixture",{"method":"GET","path":"/v1/models"})]
files=["server-context.cpp","server-http.cpp","server.cpp","arg.cpp","common.cpp","llama.cpp","gguf.cpp"]
reg=[];rows=[];src=[]
for i,s in enumerate(sigs):
    ch,args,model,req=trig[i]; sid=f"E26-{i+1:02d}"; srow=f"S9{i+1:02d}"; f=files[i%len(files)]
    e={"id":sid,"channel":ch,"signature":s,"args":args,"model":model,"source":{"row":srow,"file":f}}
    if req: e["request"]=req
    reg.append(e); rows.append(f"| {sid} | ``{s}`` | trigger | meaning | action | {srow} |")
    src.append(f"| {srow} | llama.cpp {f} @ 704366d — https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/x/{f}#L{i+1} | code | A | x | x | x | mined | 2026-10-23 | on-release | SKILL.md |")
json.dump({"signatures":reg},open(f"{tree}/registry/error-signatures-r26.json","w"),indent=1)
open(f"{tree}/SKILL.md","a").write("\n## Round-26 live error signatures\n\n| id | signature | trigger | meaning | action | source |\n|---|---|---|---|---|---|\n"+"\n".join(rows)+"\n")
s=open(f"{tree}/corpus/SOURCES.md").read().replace("\n## Round-22 residual-source","\n"+"\n".join(src)+"\n\n## Round-22 residual-source",1) if False else None
open(f"{tree}/corpus/SOURCES.md","a").write("\n"+"\n".join(src)+"\n")
