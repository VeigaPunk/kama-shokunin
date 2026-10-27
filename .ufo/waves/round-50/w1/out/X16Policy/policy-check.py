#!/usr/bin/env python3
"""X16Policy wave-policy check: band, maxLanes, roles, wave label, model shares.

Read-only. Inputs are absolute read-only paths; output is JSON+markdown to the seat out dir.
"""
import json
import re
import sys

FLEET = "/home/vgpnk/Projects/shokunin"
LANE = FLEET + "/kama-shokunin"
POLICY_V2 = FLEET + "/scripts/hyaku/ufo-wave-policy-v2.json"
POLICY_V1 = FLEET + "/scripts/hyaku/ufo-wave-policy.json"
ADDENDUM = FLEET + "/scripts/hyaku/lane-addendum.md"
ENVFILE = FLEET + "/scripts/hyaku/hyaku.env"
CONFIG = "/home/vgpnk/.omp/agent/config.yml"
WAVE = LANE + "/.ufo/waves/round-50/w1"

out = {}

pol = json.load(open(POLICY_V2))
swarm = pol["sighting"]["dispatch"]["swarm"]
out["policy_file"] = POLICY_V2
out["policy_swarm"] = {k: swarm.get(k) for k in
                       ("maxLanes", "minLanes", "waveMinLanes", "waveMaxLanes",
                        "rampBatchSize", "rampIntervalMs")}
out["policy_round_budget_maxLanes"] = swarm.get("maxLanes")
out["policy_proposalRoles"] = pol["nativeProfiles"]["omp-native-v1"]["proposalRoles"]
out["policy_lanes_roles"] = [l["role"] for l in pol["lanes"]]
out["policy_native_ceilings"] = {n: p.get("concurrencyCeiling")
                                 for n, p in pol["nativeProfiles"].items()}
out["policy_substrates"] = [s["id"] for s in pol["substrates"]]

v1 = json.load(open(POLICY_V1))
out["policy_v1_swarm"] = {k: v1["sighting"]["dispatch"]["swarm"].get(k) for k in
                          ("maxLanes", "minLanes", "waveMinLanes", "waveMaxLanes")}

# --- validator authority (read-only sibling checkout) ---
val = "/home/vgpnk/Projects/ufo-fsd-alpha/scripts/ufo-mission-result.mjs"
vsrc = open(val, encoding="utf-8").read()
out["validator_file"] = val
m = re.search(r"export const MAX_SWARM_LANES = (\d+);", vsrc)
out["validator_MAX_SWARM_LANES"] = int(m.group(1)) if m else None
m = re.search(r"export const MIN_SWARM_LANES = (\d+);", vsrc)
out["validator_MIN_SWARM_LANES"] = int(m.group(1)) if m else None

wsrc = open("/home/vgpnk/Projects/ufo-fsd-alpha/scripts/ufo-swarm-wave.mjs", encoding="utf-8").read()
m = re.search(r"export const SWARM_ROLES = new Set\(\[(.*?)\]\);", wsrc, re.S)
out["validator_SWARM_ROLES"] = re.findall(r'"([^"]+)"', m.group(1)) if m else None
out["validator_role_fail_line"] = next(
    (i + 1 for i, line in enumerate(wsrc.splitlines()) if 'fail("unknown_role"' in line), None)

# --- wave spec + dispatch + ready ---
spec = json.load(open(WAVE + "/spec.json"))
disp = json.load(open(WAVE + "/dispatch.json"))
ready = json.load(open(LANE + "/.ufo/waves/round-50/w1.ready"))
out["wave_labels"] = {
    "spec.wave": spec.get("wave"),
    "dispatch.wave": disp.get("wave"),
    "ready": {k: ready.get(k) for k in ("lane", "round", "wave", "l1")},
    "reportDir": spec.get("reportDir"),
    "dispatch_registry_path": disp.get("registry", {}).get("path"),
}
out["spec_maxLanes"] = spec.get("maxLanes")
out["dispatch_policy"] = disp.get("policy")
out["dispatch_counts"] = disp.get("counts")
out["spec_items"] = len(spec["items"])
out["dispatch_members"] = len(disp["registry"]["members"])

roles = [i["role"] for i in spec["items"]]
from collections import Counter

rc = Counter(roles)
out["role_counts"] = dict(sorted(rc.items(), key=lambda kv: (-kv[1], kv[0])))
out["role_names_distinct"] = sorted(rc)
out["names_unique"] = len({i["name"] for i in spec["items"]}) == len(spec["items"])

# --- config.yml role -> alias map (the routing authority) ---
import yaml

cfg_text = open(CONFIG, encoding="utf-8").read()
cfg_doc = yaml.safe_load(cfg_text)
cfg = cfg_text.splitlines()


def find_line(needle):
    for n, line in enumerate(cfg, 1):
        if needle in line:
            return n
    return None


overrides = cfg_doc["task"]["agentModelOverrides"]
aliases_doc = cfg_doc["model"]["aliases"] if "model" in cfg_doc else None
if aliases_doc is None:
    # locate the alias parent by probing a known alias key anywhere in the doc
    for k, v in cfg_doc.items():
        if isinstance(v, dict) and "m_flash" in v:
            aliases_doc = v
            break
out["alias_parent_key"] = next(
    (k for k, v in cfg_doc.items() if isinstance(v, dict) and "m_flash" in v), None)
out["task_maxConcurrency"] = cfg_doc["task"].get("maxConcurrency")
out["task_maxRecursionDepth"] = cfg_doc["task"].get("maxRecursionDepth")
out["role_alias"] = {r: {"alias": a, "line": find_line(f"    {r}: \"{a}\"")}
                     for r, a in sorted(overrides.items())}
out["aliases"] = {k: {"model": v, "line": find_line(f"  {k}: {v}")}
                  for k, v in sorted(aliases_doc.items()) if isinstance(v, str)}
alias_of = {r: a.lstrip("@") for r, a in overrides.items()}
resolved = {r: aliases_doc.get(alias_of[r]) for r in overrides}
out["resolved_model"] = {r: {"alias": alias_of[r], "model": resolved[r]}
                         for r in sorted(overrides)}

# --- shares ---
# m_flash set per lane-addendum.md:16-18 (run-9 amendment): critic excluded.
MFLASH_ROLES = ["executor", "labrat", "scribe", "sonic", "simplifier", "revenger", "sentinel"]
ATTACK_ROLES = ["reviewer", "critic", "mutation-tester", "labrat"]  # addendum:147
total = len(roles)
mf_by_role = {r: rc.get(r, 0) for r in MFLASH_ROLES}
at_by_role = {r: rc.get(r, 0) for r in ATTACK_ROLES}
mf = sum(mf_by_role.values())
at = sum(at_by_role.values())
out["mflash_roles"] = MFLASH_ROLES
out["mflash_by_role"] = mf_by_role
out["mflash_seats"] = mf
out["mflash_share"] = mf / total
out["mflash_threshold"] = 0.50
out["mflash_meets"] = mf / total >= 0.50
out["mflash_min_seats_required"] = -(-total * 50 // 100)
out["attack_by_role"] = at_by_role
out["attack_seats"] = at
out["attack_share"] = at / total
out["attack_threshold"] = 0.25
out["attack_meets"] = at / total >= 0.25
out["attack_min_seats_required"] = -(-total * 25 // 100)
out["other_seats"] = total - mf - at
out["other_roles"] = {r: c for r, c in rc.items() if r not in MFLASH_ROLES and r not in ATTACK_ROLES}

# alias-derived cross-check: seats whose role maps to @m_flash in config.yml
alias_mflash = sum(c for r, c in rc.items()
                   if alias_of.get(r) == "m_flash")
out["alias_mflash_seats"] = alias_mflash
out["alias_mflash_roles"] = sorted(r for r in rc if alias_of.get(r) == "m_flash")
out["alias_mflash_share"] = alias_mflash / total

# --- conformance assertions ---
band_ok = out["policy_swarm"]["waveMinLanes"] <= spec["maxLanes"] <= out["policy_swarm"]["waveMaxLanes"]
out["band_check"] = {
    "waveMinLanes": out["policy_swarm"]["waveMinLanes"],
    "spec_maxLanes": spec["maxLanes"],
    "waveMaxLanes": out["policy_swarm"]["waveMaxLanes"],
    "seats": total,
    "maxLanes_in_band": band_ok,
    "seats_in_band": out["policy_swarm"]["waveMinLanes"] <= total <= out["policy_swarm"]["waveMaxLanes"],
    "under_hard_ceiling": total <= out["validator_MAX_SWARM_LANES"],
    "under_round_budget": total <= out["policy_swarm"]["maxLanes"],
}
out["role_conformance"] = {
    "wave_roles_subset_of_proposalRoles": set(rc) <= set(out["policy_proposalRoles"]),
    "wave_roles_subset_of_SWARM_ROLES": set(rc) <= set(out["validator_SWARM_ROLES"]),
    "proposalRoles_eq_SWARM_ROLES": set(out["policy_proposalRoles"]) == set(out["validator_SWARM_ROLES"]),
    "roles_in_lanes_but_not_wave": sorted(set(out["policy_lanes_roles"]) - set(rc)),
    "wave_roles_missing_from_policy_lanes": sorted(set(rc) - set(out["policy_lanes_roles"])),
    "roles_in_lanes_but_not_proposalRoles": sorted(set(out["policy_lanes_roles"]) - set(out["policy_proposalRoles"])),
    "frozen_topology_roles_present": sorted(set(rc) & {"planner", "distiller", "labrat", "main", "task"}),
    "every_wave_role_has_config_override": all(r in alias_of for r in rc),
    "roles_missing_config_override": sorted(r for r in rc if r not in alias_of),
}

# hyaku.env run-9 label vs config authority (critic divergence)
env_text = open(ENVFILE, encoding="utf-8").read()
out["hyaku_env_critic_label_mflash"] = bool(
    re.search(r"simplifier/critic/revenger/sentinel @m_flash", env_text))
out["config_critic_alias"] = alias_of.get("critic")

json.dump(out, open(sys.argv[1], "w"), indent=2, sort_keys=False)
print(json.dumps(out, indent=2))
