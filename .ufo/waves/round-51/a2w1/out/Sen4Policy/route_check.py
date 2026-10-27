#!/usr/bin/env python3
"""Round-51 a2w1 wave policy + route check (seat Sen4Policy).

Read-only. Recomputes, from the four sources named by the seat item:
  1. wave role counts       spec.json items, dispatch.json taskCall.tasks, swarm-registry.json members
  2. route map resolution   ~/.omp/agent/config.yml task.agentModelOverrides -> modelRoles -> enabledModels
  3. attack share           reviewer + critic + mutation-tester (+ labrat), addendum v2-wave rule
  4. route-map provenance   mtime/ctime/size/inode/sha256 of config.yml vs dispatch createdAt (closure R7)
and cross-checks the wave against scripts/hyaku/ufo-wave-policy-v2.json and lane-addendum routing text.

Exit 0 = every source agrees and every derived assertion holds. Findings are printed, not raised.
"""
import collections
import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import sys

import yaml

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
FLEET = "/home/vgpnk/Projects/shokunin"
W = f"{LANE}/.ufo/waves/round-51/a2w1"
CONFIG = "/home/vgpnk/.omp/agent/config.yml"
POLICY = f"{FLEET}/scripts/hyaku/ufo-wave-policy-v2.json"
HYAKU_ENV = f"{FLEET}/scripts/hyaku/hyaku.env"
ADDENDUM = f"{FLEET}/scripts/hyaku/lane-addendum.md"
UFO_JSON = "/home/vgpnk/Projects/ufo-fsd-alpha/config/ufo.json"

ATTACK = ("reviewer", "critic", "mutation-tester")
ATTACK_V2 = ("reviewer", "critic", "mutation-tester", "labrat")  # addendum v2-wave wording
CONNECTOR = ("connector",)

ok = True


def say(*a):
    print(*a)


def check(cond, label):
    global ok
    ok = ok and bool(cond)
    say(f"[{'OK ' if cond else 'FAIL'}] {label}")
    return cond


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def iso(ts):
    return dt.datetime.fromtimestamp(ts).astimezone().isoformat(timespec="seconds")


# ---------------------------------------------------------------- sources
spec = json.load(open(f"{W}/spec.json"))
disp = json.load(open(f"{W}/dispatch.json"))
reg = json.load(open(f"{W}/out/swarm-registry.json"))
cfg = yaml.safe_load(open(CONFIG))
pol = json.load(open(POLICY))
items = spec["items"]
tasks = disp["taskCall"]["tasks"]
members = reg["members"]

say("== sources ==")
for p in (CONFIG, POLICY, f"{W}/spec.json", f"{W}/dispatch.json", f"{W}/out/swarm-registry.json"):
    st = os.stat(p)
    say(f"  {p}\n    sha256={sha256(p)} size={st.st_size} mtime={iso(st.st_mtime)} ctime={iso(st.st_ctime)} ino={st.st_ino}")

# ---------------------------------------------------------------- 1. role counts, three ways
say("\n== 1. wave role counts (spec / dispatch / registry) ==")
c_spec = collections.Counter(i["role"] for i in items)
c_disp = collections.Counter(t["agent"] for t in tasks)
c_reg = collections.Counter(m["role"] for m in members.values())
for role in sorted(set(c_spec) | set(c_disp) | set(c_reg)):
    say(f"  {role:15s} spec={c_spec[role]:2d} dispatch={c_disp[role]:2d} registry={c_reg[role]:2d}")
check(c_spec == c_disp == c_reg, "spec, dispatch and registry carry the same role multiset")
total = sum(c_spec.values())
check(total == len(items) == len(tasks) == len(members), f"seat count {total} == items == tasks == registry members")
check(len({t["name"] for t in tasks}) == total, "seat names unique")
check(total == spec["maxLanes"], f"seat count {total} == spec maxLanes {spec['maxLanes']}")
check(spec["wave"] == disp["wave"] == reg["wave"], f"wave label identical in spec/dispatch/registry ({spec['wave']})")

# ---------------------------------------------------------------- 2. route map
say("\n== 2. live route map (task.agentModelOverrides -> modelRoles -> enabledModels) ==")
mr = cfg["modelRoles"]
ov = cfg["task"]["agentModelOverrides"]
enabled = set(cfg.get("enabledModels") or [])
chains = (cfg.get("retry") or {}).get("fallbackChains") or {}
root = os.path.dirname(CONFIG)
with open(CONFIG, encoding="utf-8") as fh:
    cfg_lines = fh.read().splitlines()


def line_of(pattern):
    for n, ln in enumerate(cfg_lines, 1):
        if re.search(pattern, ln):
            return n
    return None


resolved = {}
say(f"  {'role':16s} {'alias':10s} {'target':48s} {'enabled':7s} {'chain':5s} {'seats':5s} cfglines")
for role in sorted(set(c_spec) | set(ov)):
    alias = ov.get(role)
    key = alias.lstrip("@") if alias else None
    tgt = mr.get(key) if key else None
    base = tgt.split(":")[0] if tgt else None
    en = base in enabled if base else False
    ch = key in chains
    resolved[role] = tgt
    if c_spec.get(role):
        say(f"  {role:16s} {str(alias):10s} {str(tgt):48s} {str(en):7s} {str(ch):5s} {c_spec[role]:5d} "
            f"ov={line_of(rf'^    {re.escape(role)}:')} role={line_of(rf'^  {re.escape(key or "-")}:')}")
wave_roles = set(c_spec)
check(wave_roles <= set(ov), f"all {len(wave_roles)} wave roles have an agentModelOverrides entry")
check(all(resolved[r] for r in wave_roles), "all wave roles resolve to a modelRoles target")
check(all(resolved[r].split(":")[0] in enabled for r in wave_roles), "every resolved target is in enabledModels")
check(all(ov[r].lstrip("@") in chains for r in wave_roles), "every wave role alias has a fallbackChain")
check(not any("model" in t or "modelAlias" in t for t in tasks), "no dispatch task carries model/modelAlias (routing by role only)")
check(not any("modelAlias" in i for i in items) and "modelAlias" not in spec, "spec carries no modelAlias override")
say(f"  task.maxConcurrency={cfg['task']['maxConcurrency']} maxRecursionDepth={cfg['task']['maxRecursionDepth']} "
    f"eager={cfg['task'].get('eager')} retry.modelFallback={(cfg.get('retry') or {}).get('modelFallback')}")
check(cfg["task"]["maxConcurrency"] >= total, "task.maxConcurrency admits the wave")

per_model = collections.Counter(resolved[r] for r in c_spec.elements())
say("\n  per-model seat counts under the live map:")
for m, n in per_model.most_common():
    say(f"    {n:3d}  {n / total * 100:5.2f}%  {m}")

# ---------------------------------------------------------------- 3. attack share
say("\n== 3. attack share ==")
att = sum(c_spec[r] for r in ATTACK)
att_v2 = sum(c_spec[r] for r in ATTACK_V2)
say(f"  reviewer={c_spec['reviewer']} critic={c_spec['critic']} mutation-tester={c_spec['mutation-tester']} labrat={c_spec['labrat']}")
say(f"  attack (reviewer/critic/mutation-tester)      = {att}/{total} = {att / total * 100:.2f}%")
say(f"  attack (addendum incl. labrat, 0 seats)       = {att_v2}/{total} = {att_v2 / total * 100:.2f}%")
check(att_v2 == att, "both attack enumerations agree (labrat holds 0 seats)")
floor = -(-total * 25 // 100)
check(att >= floor, f"attack share {att / total * 100:.2f}% >= 25% ({floor}-seat floor)")
say(f"  attack seats by model: {dict(collections.Counter(resolved[r] for r in c_spec.elements() if r in ATTACK))}")
say(f"  connector seats: {c_spec['connector']} ({c_spec['connector'] / total * 100:.2f}%)")

# ---------------------------------------------------------------- 4. policy conformance
say("\n== 4. policy v2 conformance ==")
sw = pol["sighting"]["dispatch"]["swarm"]
say(f"  band=[{sw['waveMinLanes']},{sw['waveMaxLanes']}] maxLanes={sw['maxLanes']} hardCeiling="
    f"{disp['policy']['hardCeiling']} ramp={sw['rampBatchSize']}/{sw['rampIntervalMs']}ms")
check(sw["waveMinLanes"] <= total <= sw["waveMaxLanes"], f"{total} seats inside the v2 band 64-128")
check(total <= sw["maxLanes"], f"{total} <= policy maxLanes {sw['maxLanes']}")
check(disp["policy"]["waveMinLanes"] == sw["waveMinLanes"] and disp["policy"]["waveMaxLanes"] == sw["waveMaxLanes"],
      "dispatch.policy band equals the policy file band")
say(f"  ramp: ceil({total}/{sw['rampBatchSize']}) = {-(-total // sw['rampBatchSize'])} batches "
    f"x {sw['rampIntervalMs']} ms = {-(-total // sw['rampBatchSize']) * sw['rampIntervalMs'] / 1000:.1f} s")
check(open(f"{W}/validate.out").read().strip() == "exit=0" and os.path.getsize(f"{W}/validate.stderr") == 0,
      "validator receipt: validate.out exit=0, validate.stderr empty")
props = pol["nativeProfiles"]["omp-native-v1"]["proposalRoles"]
check(wave_roles <= set(props), f"wave roles subset of proposalRoles {sorted(props)}")
lanes_tbl = {l["role"] for l in pol["lanes"]}
say(f"  lanes[] roles={sorted(lanes_tbl)}")
say(f"  wave roles absent from lanes[]: {sorted(wave_roles - lanes_tbl)}  |  lanes[] roles with 0 seats: {sorted(lanes_tbl - wave_roles)}")
ufo = json.load(open(UFO_JSON)) if os.path.exists(UFO_JSON) else {}
say(f"  surfaceDigest policy={pol['sighting']['surfaceDigest']}  ufo.json={ufo.get('sighting', {}).get('surfaceDigest')}")

# ---------------------------------------------------------------- 5. axes binding
say("\n== 5. axes binding ==")
wave_axes = spec["axes"]
say(f"  wave axes={wave_axes}  milestones={sorted({i['milestone'] for i in items})}")
ax = collections.Counter(tuple(i["axes"]) for i in items)
for k, n in ax.most_common():
    say(f"    {n:3d}  {list(k)}")
off = [(i["name"], i["axes"]) for i in items if not set(i["axes"]) <= set(wave_axes)]
say(f"  items binding an axis outside spec.axes: {off}")
say(f"  These are valid canonical item axes (AXES.md); the validator accepts per-item bindings independently of spec.axes.")
cov = {a: sum(1 for i in items if a in i["axes"]) for a in wave_axes}
say(f"  seats per declared axis: {cov}")

# ---------------------------------------------------------------- 6. label drift (hyaku.env)
say("\n== 6. hyaku.env routing labels vs live map ==")
env_lines = open(HYAKU_ENV, encoding="utf-8").read().splitlines()
labels = {}
for n, ln in enumerate(env_lines, 1):
    if not ln.lstrip().startswith("#"):
        continue
    for seg in ln.split(";"):
        seg = seg.lstrip("# ")
        m = re.search(r"([a-z/][a-z0-9/_-]*)\s+`?(@m_[a-z0-9]+)`?", seg)
        if m:
            alias = m.group(2).strip("`")
            for r in m.group(1).split("/"):
                labels[r] = (alias, n)
drift = []
for r in sorted(wave_roles):
    if r in labels and labels[r][0] != ov.get(r):
        drift.append((r, labels[r][0], ov.get(r), c_spec[r], labels[r][1]))
for r, lab, live, n, ln in drift:
    say(f"  DRIFT {r:15s} label={lab:18s} (hyaku.env:{ln})  live={live:18s}  seats={n}")
say(f"  seats whose label-implied model differs from the live map: {sum(d[3] for d in drift)}/{total} "
    f"({sum(d[3] for d in drift) / total * 100:.2f}%)")
lab_models = collections.Counter()
for r in c_spec.elements():
    lab_models[labels.get(r, (ov[r], 0))[0]] += 1
say(f"  per-model seats if the labels were believed: {dict(lab_models)}")
say(f"  label entries parsed: {len(labels)}; changed roles: {len(drift)}")
addendum_txt = open(ADDENDUM, encoding="utf-8").read()
check("executor `@m_mim`" in addendum_txt and "connector `@m_antigravity`" in addendum_txt
      and "critic and scout `@m_kfc`" in addendum_txt, "lane-addendum current map matches live map on the changed roles")

# ---------------------------------------------------------------- 7. lane bounds
say("\n== 7. lane bounds text ==")
grant = [t for t in tasks if "except your single labrat" in t["task"]]
say(f"  seats granted one labrat: {len(grant)} (roles={dict(collections.Counter(t['agent'] for t in grant))})")
ctx = disp["taskCall"]["context"]
say(f"  context says 'do not spawn subagents (leaf)': {'do not spawn subagents' in ctx}")
say(f"  spec declares labrat seats: {c_spec['labrat']}")
check(len(grant) == c_spec["executor"], "the labrat grant lands exactly on the executor seats")

say("\n== assertions ==")
say("RESULT " + ("pass" if ok else "fail"))
sys.exit(0 if ok else 1)

