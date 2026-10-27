#!/usr/bin/env python3
"""Sen3Policy, round 52 wave policy + route check (read-only).

Checks, in order:
  1. spec / dispatch / registry agreement (names, role multiset, wave label).
  2. policy v2 band (waveMinLanes..waveMaxLanes), declared maxLanes, validator receipt.
  3. live route map: task.agentModelOverrides -> modelRoles -> enabledModels, plus a
     retry fallback chain per alias used by this wave.
  4. attack share (reviewer, critic, mutation-tester; labrat variant) and per-model seats.
  5. dispatch-time route-map fingerprint (config.yml mtime/sha256 vs registry createdAt).
  6. drift flags (policy lanes[] table, profile concurrencyCeiling, policy surfaceDigest,
     hyaku.env run-9 labels, item axes outside the wave declaration).

Exit 0 = the structural agreement checks pass. Drift flags are printed as findings and
never fail the run: they are reports, not gates.
"""
import hashlib
import json
import os
import re
import stat
import sys
from collections import Counter
from datetime import datetime, timezone

import yaml

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
W = f"{LANE}/.ufo/waves/round-52/w1"
POLICY = "/home/vgpnk/Projects/shokunin/scripts/hyaku/ufo-wave-policy-v2.json"
CONFIG = "/home/vgpnk/.omp/agent/config.yml"
HYAKU_ENV = "/home/vgpnk/Projects/shokunin/scripts/hyaku/hyaku.env"
ORIGIN_CFG = "/home/vgpnk/Projects/ufo-fsd-alpha/config/ufo.json"

ATTACK_ROLES = ("reviewer", "critic", "mutation-tester")
ATTACK_ROLES_WITH_LABRAT = ATTACK_ROLES + ("labrat",)
FAIL = []


def chk(cond, label, detail=""):
    print(f"{'PASS' if cond else 'FAIL'}  {label}{(' :: ' + detail) if detail else ''}")
    if not cond:
        FAIL.append(label)
    return cond


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def iso_ns(st):
    return datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%S.%fZ"
    )


def main():
    spec = json.load(open(f"{W}/spec.json"))
    dispatch = json.load(open(f"{W}/dispatch.json"))
    registry = json.load(open(f"{W}/out/swarm-registry.json"))
    policy = json.load(open(POLICY))
    cfg = yaml.safe_load(open(CONFIG))

    # ---------------- 1. source agreement ----------------
    items = spec["items"]
    tasks = dispatch["taskCall"]["tasks"]
    members = registry["members"]
    spec_roles = Counter(i["role"] for i in items)
    chk(len(items) == spec["maxLanes"], "spec item count == maxLanes",
        f"{len(items)} == {spec['maxLanes']}")
    chk(len({i['name'] for i in items}) == len(items), "spec seat names unique")
    chk([t["name"] for t in tasks] == [i["name"] for i in items],
        "dispatch taskCall order/names == spec")
    chk(list(members.keys()) == [i["name"] for i in items],
        "registry member order/names == spec")
    chk(Counter(t["agent"] for t in tasks) == spec_roles,
        "dispatch agent selectors == spec role multiset")
    chk(Counter(m["role"] for m in members.values()) == spec_roles,
        "registry roles == spec role multiset")
    labels = {spec["wave"], dispatch["wave"], registry["wave"]}
    chk(len(labels) == 1, "wave label consistent across spec/dispatch/registry",
        ",".join(sorted(labels)))
    chk(not any("model" in t for t in tasks),
        "no per-task model override in the dispatch (role map is authority)")
    chk(dispatch["counts"]["spawn"] == len(items) == dispatch["counts"]["total"],
        "dispatch counts match seats", json.dumps(dispatch["counts"]))
    chk(registry["schema"] == "ufo-swarm-registry-v1"
        and dispatch["schema"] == "ufo-swarm-wave-dispatch-v1",
        "dispatch/registry schemas are the swarm v1 pair")
    val = open(f"{W}/validate.out").read().strip()
    verr = os.path.getsize(f"{W}/validate.stderr")
    chk(val == "exit=0" and verr == 0, "validator receipt clean",
        f"validate.out={val!r} validate.stderr={verr}B")

    # ---------------- 2. policy band ----------------
    band = policy["sighting"]["dispatch"]["swarm"]
    p = dispatch["policy"]
    chk(band["waveMinLanes"] <= len(items) <= band["waveMaxLanes"],
        "wave size inside v2 band",
        f"{band['waveMinLanes']} <= {len(items)} <= {band['waveMaxLanes']}")
    chk(len(items) <= band["maxLanes"], "wave size <= policy maxLanes",
        f"{len(items)} <= {band['maxLanes']}")
    chk(p["waveMinLanes"] == band["waveMinLanes"]
        and p["waveMaxLanes"] == band["waveMaxLanes"]
        and p["hardCeiling"] == band["maxLanes"],
        "dispatch policy block == policy v2 band", json.dumps(p))
    chk(p["declaredMaxLanes"] == spec["maxLanes"] == len(items),
        "declared maxLanes == spec maxLanes == seats")
    chk(p["globalRunnerCeiling"] == policy["sighting"]["dispatch"]["globalRunnerCeiling"],
        "dispatch globalRunnerCeiling == policy")
    prof = policy["nativeProfiles"]["omp-native-v1"]
    chk(set(spec_roles) <= set(prof["proposalRoles"]),
        "every dispatched role is a omp-native-v1 proposal role",
        ",".join(sorted(set(spec_roles) - set(prof["proposalRoles"]))) or "none extra")

    # ---------------- 3. live route resolution ----------------
    overrides = cfg["task"]["agentModelOverrides"]
    roles = cfg["modelRoles"]
    enabled = set(cfg["enabledModels"])
    chains = cfg["retry"]["fallbackChains"]
    missing = sorted(set(spec_roles) - set(overrides))
    chk(not missing, "every dispatched role has an agentModelOverrides route",
        ",".join(missing) or "0 missing")
    resolved, unresolved = {}, []
    for role in sorted(spec_roles):
        alias = overrides.get(role)
        if alias is None:
            unresolved.append(f"{role}:no-route")
            continue
        key = alias.lstrip("@")
        target = roles.get(key)
        if target is None:
            unresolved.append(f"{role}:{alias}->no modelRoles entry")
            continue
        base = target.split(":")[0]
        if base not in enabled:
            unresolved.append(f"{role}:{alias}->{base} not enabled")
        if key not in chains:
            unresolved.append(f"{role}:{alias}->no fallbackChain")
        resolved[role] = (alias, target)
    chk(not unresolved, "all role routes resolve: alias -> enabled model + fallback chain",
        "; ".join(unresolved) or f"{len(resolved)} roles")

    # ---------------- 4. shares ----------------
    n = len(items)
    atk = sum(spec_roles[r] for r in ATTACK_ROLES)
    atk4 = sum(spec_roles[r] for r in ATTACK_ROLES_WITH_LABRAT)
    floor25 = -(-n * 25 // 100)  # ceil
    print(f"\nATTACK reviewer+critic+mutation-tester = {atk}/{n} = {100*atk/n:.2f}%"
          f" (floor {floor25} seats = 25.00%) -> "
          f"{'MET' if atk >= floor25 else 'NOT MET'}")
    print(f"ATTACK with labrat (addendum 4-role)      = {atk4}/{n} = {100*atk4/n:.2f}%"
          f" -> {'MET' if atk4 >= floor25 else 'NOT MET'}")
    by_model, by_alias = Counter(), Counter()
    for role, cnt in spec_roles.items():
        alias, target = resolved.get(role, ("<unresolved>", "<unresolved>"))
        by_alias[alias] += cnt
        by_model[target] += cnt
    print("\nPER-MODEL SEATS (live map)")
    for target, cnt in by_model.most_common():
        who = ", ".join(
            f"{r} {c}" for r, c in sorted(spec_roles.items())
            if resolved.get(r, (None, None))[1] == target
        )
        print(f"  {cnt:3d}  {100*cnt/n:6.2f}%  {target}  [{who}]")
    print("\nPER-ALIAS SEATS")
    for alias, cnt in by_alias.most_common():
        print(f"  {cnt:3d}  {100*cnt/n:6.2f}%  {alias}")
    mflash = by_alias.get("@m_flash", 0)
    print(f"\nm_flash share = {mflash}/{n} = {100*mflash/n:.2f}% "
          f"(run-9 addendum: the >=50% condition no longer binds)")
    print(f"connector seats = {spec_roles.get('connector', 0)}/{n} "
          f"({100*spec_roles.get('connector',0)/n:.2f}%) — few-seat rule")

    # ---------------- 5. route-map fingerprint ----------------
    st = os.stat(CONFIG)
    mtime = iso_ns(st)
    digest = sha256_file(CONFIG)
    created = registry["createdAt"]
    ct = datetime.strptime(created, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
    delta = (ct - datetime.fromtimestamp(st.st_mtime, tz=timezone.utc)).total_seconds()
    print(f"\nCONFIG {CONFIG}")
    print(f"  mtime   {mtime} ({datetime.fromtimestamp(st.st_mtime).astimezone()})")
    print(f"  ctime   {datetime.fromtimestamp(st.st_ctime, tz=timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%fZ')}")
    print(f"  size    {st.st_size} B")
    print(f"  sha256  {digest}")
    print(f"  registry createdAt {created}  (config precedes dispatch by {delta:.0f}s)")
    chk(delta > 0, "config mtime precedes the wave's registry createdAt")

    # ---------------- 6. drift flags ----------------
    print("\nDRIFT FLAGS (reports, not gates)")
    lanes_ids = [l["id"] for l in policy["lanes"]]
    if "labrat" in lanes_ids and "sentinel" not in lanes_ids:
        print(f"  F1 policy lanes[] lists labrat (line 268) and omits sentinel, while "
              f"proposalRoles lists sentinel (line 109); wave dispatches "
              f"sentinel {spec_roles.get('sentinel',0)} / labrat {spec_roles.get('labrat',0)}")
    ceil32 = prof["concurrencyCeiling"]
    if ceil32 < len(items):
        print(f"  F2 omp-native-v1.concurrencyCeiling={ceil32} (policy line 98) < "
              f"{len(items)} dispatched seats, v2 band admits {band['waveMaxLanes']}")
    pol_dig = policy["sighting"]["surfaceDigest"]
    if os.path.exists(ORIGIN_CFG):
        org = json.load(open(ORIGIN_CFG))["sighting"]["surfaceDigest"]
        if org != pol_dig:
            print(f"  F3 policy surfaceDigest {pol_dig[:19]}… != origin "
                  f"{ORIGIN_CFG} {org[:19]}…")
    env = open(HYAKU_ENV).read()
    run9 = "Run 9" in env
    claimed = {}
    for roles_group, alias in re.findall(r"([\w/]+)\s+(@m_\w+)", env):
        for role in roles_group.split("/"):
            claimed[role] = alias
    diffs = {r: (claimed.get(r), overrides.get(r)) for r in spec_roles
             if claimed.get(r) and overrides.get(r) and claimed[r] != overrides[r]}
    if run9 and diffs:
        seats = sum(spec_roles[r] for r in diffs)
        print(f"  F4 hyaku.env run-9 comment block claims the unchanged run-8 map; "
              f"{len(diffs)} wave roles differ over {seats}/{n} seats "
              f"({100*seats/n:.2f}%): "
              + ", ".join(f"{r} label {a} live {b}" for r, (a, b) in sorted(diffs.items())))
    off_axes = [(i["name"], i["role"], i["axes"]) for i in items
                if set(i["axes"]) - set(spec["axes"])]
    if off_axes:
        print(f"  F5 {len(off_axes)} item(s) bind axes outside the wave declaration "
              f"{spec['axes']}: {off_axes}")

    print("\nRESULT " + ("pass" if not FAIL else "FAIL " + "; ".join(FAIL)))
    return 0 if not FAIL else 1


if __name__ == "__main__":
    sys.exit(main())
