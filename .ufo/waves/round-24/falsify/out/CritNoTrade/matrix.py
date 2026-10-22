import subprocess, sys, time, json, hashlib, os, re
S = "/fast/scratch/hyaku/kama-r24/falsify/CritNoTrade"
T = f"{S}/src/tools/report-landing-audit.py"
env = {**os.environ, "TMPDIR": f"{S}/tmp"}
def norm(s): return re.sub(rf"{S}/fx/(lane|fleet)-[a-z]+", r"<\1>", s)
rows = {}
for l in ("full", "pc", "bl"):
    for f in ("full", "pc", "bl"):
        for e in ("errata", "noerrata"):
            cmd = ["python3", T, "--lane-repo", f"fx/lane-{l}", "--fleet-repo", f"fx/fleet-{f}", "--rounds", "10-22", "--json"] + (["--no-errata"] if e == "noerrata" else [])
            t0 = time.monotonic(); p = subprocess.run(cmd, capture_output=True, text=True, cwd=S, env=env); dt = time.monotonic() - t0
            name = f"{l}-{f}-{e}"
            open(f"{S}/run/{name}.json", "w").write(p.stdout); open(f"{S}/run/{name}.err", "w").write(p.stderr)
            n = norm(p.stdout)
            rows[name] = dict(rc=p.returncode, secs=round(dt, 2), stderr=p.stderr.strip()[:300], norm_sha=hashlib.sha256(n.encode()).hexdigest()[:16])
            if p.returncode in (0, 1):
                d = json.loads(p.stdout); s = d["summary"]
                rows[name].update(status=s["status"], reports=s["reports"], required=s["required_commits"], defects=s["defects"], corrected=s["corrected"], uncorrected=s["uncorrected"], unmatched=s["errata_unmatched"], invalid=s["errata_invalid"],
                    finding_ids=sorted(f"r{r['round']}:{x['kind']}:{x['token']}" for r in d["results"] for x in r["defects"]))
json.dump(rows, open(f"{S}/run/matrix.json", "w"), indent=1)
for k, v in rows.items():
    print(k, {a: b for a, b in v.items() if a != "finding_ids"})
for e in ("errata", "noerrata"):
    ref = rows[f"full-full-{e}"]
    print(e, "all norm_sha equal to full-full:", all(rows[f"{l}-{f}-{e}"]["norm_sha"] == ref["norm_sha"] for l in ("full","pc","bl") for f in ("full","pc","bl")))
    print(e, "finding_ids:", ref.get("finding_ids"))
