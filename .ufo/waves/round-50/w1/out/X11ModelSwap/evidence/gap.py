#!/usr/bin/env python3
"""Does the frozen counter's bind leg still pass if the model file is rewritten in
place AFTER its single mapped sample? Uses the counter's own start_replay/wait_ready/
observe and the live tool's model_mapping, imported unmodified."""
import importlib.util, json, os, shutil, subprocess, sys, time
S = "/fast/scratch/hyaku/kama-r50/X11ModelSwap"
LANE = os.path.join(S, "lane")


def load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(LANE, rel))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


c = load("r50c1", "tools/round50-replay-bind-audit.py")
out = {"steps": []}


def step(label, **kw):
    out["steps"].append(dict(label=label, **kw)); print(label, json.dumps(kw)[:600], flush=True)


def completion(port, tag):
    req = subprocess.run(["curl", "-s", "-m", "30", "-o", os.path.join(S, f"gap-{tag}.json"),
                          "-w", "%{http_code}", "-H", "content-type: application/json",
                          "-d", '{"prompt":"Once upon a time","n_predict":8,"temperature":0}',
                          f"http://127.0.0.1:{port}/completion"], capture_output=True, text=True)
    try:
        d = json.load(open(os.path.join(S, f"gap-{tag}.json")))
        return {"http": req.stdout.strip(), "content": d.get("content")}
    except Exception as exc:
        return {"http": req.stdout.strip(), "error": repr(exc)}


receipt = os.path.join(LANE, ".ufo/waves/round-48/c2/live/receipt-1.json")
p, wd, outj, log, canary, marker = c.start_replay(LANE, receipt, S, "gap")
tag = "gap"
model = os.path.join(S, "work-gap/download/stories260K.gguf")
try:
    ready = c.wait_ready(p, wd)
    if ready is None:
        step("no-ready", invoker_exit=p.poll()); raise SystemExit(1)
    pid, port = ready["pid"], ready["port"]
    step("ready", pid=pid, port=port, generated_by="counter.start_replay (isolated -I, canaries)")
    vocab = c.gguf_tokens(os.path.join(S, "origbytes.gguf"))
    probs = []
    nonce, mapped = c.observe(pid, port, vocab, canary, probs)
    step("counter_observe", mapped=mapped, nonce=nonce, probs=probs, canary_env_present=False)
    step("completion_before_swap", **completion(port, "before"))
    shutil.copyfile(os.path.join(S, "dl/stories15M.gguf"), model)   # in place after the sample
    step("swapped_in_place", inode=os.stat(model).st_ino, size=os.stat(model).st_size,
         live_model_mapping=c.model_mapping(pid, model) if hasattr(c, "model_mapping") else None,
         counter_mapped_now=c.mapped_model(pid, []))
    step("completion_after_swap", **completion(port, "after"))
    shutil.copyfile(os.path.join(S, "origbytes.gguf"), model)       # restore before release
    step("restored", sha=os.path.basename(model), live_mapping=c.mapped_model(pid, []))
    open(os.path.join(wd, "release"), "w").write("released\n")
    code = p.wait(timeout=180)
    j = c.load(outj)
    rr = c.load(j.get("rerun_receipt"))
    mapped_ok = (isinstance(rr.get("model_mapping"), dict)
                 and rr["model_mapping"].get("sha256") == c.MODEL_SHA and mapped is not None
                 and str(rr["model_mapping"].get("dev")) == mapped[0]
                 and str(rr["model_mapping"].get("inode")) == mapped[1])
    step("after_release", invoker_exit=code, replay_exit=j.get("live_exit"), match=j.get("match"),
         mismatches=j.get("mismatches"),
         rerun_model_mapping=rr.get("model_mapping"),
         rerun_child_pid=rr.get("child_pid"),
         model_unchanged=[ch["observed"] for ch in rr["checks"] if ch["id"] == "model_unchanged"],
         bind_mapped_leg_condition_line474=mapped_ok)
finally:
    c.reap(p)
    log.close()
json.dump(out, open(os.path.join(S, "gap-result.json"), "w"), indent=1)
