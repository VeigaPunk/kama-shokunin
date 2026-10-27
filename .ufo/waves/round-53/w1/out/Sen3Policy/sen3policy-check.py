#!/usr/bin/env python3
"""Sen3Policy round-53 wave policy and route check (kama-r53-w1).

Read-only. Re-derives every number in policy.md from four frozen lane/fleet
artifacts plus the live OMP config. Emits route-facts.json and the markdown
tables on stdout. Exit 0 when every hard check passes; exit 1 lists failures
under `FAIL` lines and in the JSON.

Inputs (env-overridable, defaults are the round-53 pins):
  POLICY    fleet policy v2
  SPEC      wave spec            (kama-shokunin/.ufo/waves/round-53/w1/spec.json)
  DISPATCH  validated payload    (same dir, dispatch.json)
  REGISTRY  swarm registry       (out/swarm-registry.json)
  CONFIG    live OMP config      (~/.omp/agent/config.yml, read-only)

Run:  python3 sen3policy-check.py [--json PATH] [--tables PATH]
"""
import argparse
import collections
import hashlib
import json
import os
import stat
import sys

import yaml

POLICY = os.environ.get(
    "POLICY", "/home/vgpnk/Projects/shokunin/scripts/hyaku/ufo-wave-policy-v2.json"
)
SPEC = os.environ.get(
    "SPEC",
    "/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/spec.json",
)
DISPATCH = os.environ.get(
    "DISPATCH",
    "/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/dispatch.json",
)
REGISTRY = os.environ.get(
    "REGISTRY",
    "/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/swarm-registry.json",
)
CONFIG = os.environ.get("CONFIG", os.path.expanduser("~/.omp/agent/config.yml"))

# Attack roles: the seat item's definition (reviewer, critic, mutation-tester);
# the binding addendum (scripts/hyaku/lane-addendum.md:159, run-9 §2) adds labrat.
ATTACK_PRIMARY = ("reviewer", "critic", "mutation-tester")
ATTACK_EXTENDED = ATTACK_PRIMARY + ("labrat",)
ATTACK_SHARE_FLOOR = 0.25

# Binding run-9 routing map, transcribed from scripts/hyaku/lane-addendum.md:15-18
# ("Current map: task/main/planner @m_opus; executor @m_mim; reviewer/mutation-tester/
# security-reviewer @m_zfl; scribe/sonic/simplifier/revenger/labrat/sentinel @m_flash;
# critic and scout @m_kfc; connector @m_antigravity; distiller/seance @m_haiku").
RUN9_MAP = {
    "task": "m_opus",
    "main": "m_opus",
    "planner": "m_opus",
    "executor": "m_mim",
    "reviewer": "m_zfl",
    "mutation-tester": "m_zfl",
    "security-reviewer": "m_zfl",
    "scribe": "m_flash",
    "sonic": "m_flash",
    "simplifier": "m_flash",
    "revenger": "m_flash",
    "labrat": "m_flash",
    "sentinel": "m_flash",
    "critic": "m_kfc",
    "scout": "m_kfc",
    "connector": "m_antigravity",
    "distiller": "m_haiku",
    "seance": "m_haiku",
}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path):
    with open(path, "rb") as fh:
        return json.load(fh)


def model_keys(o, hits=None, path=""):
    """Every `model`-ish key in a nested structure (routing must be role-only)."""
    if hits is None:
        hits = []
    if isinstance(o, dict):
        for k, v in o.items():
            if k in ("model", "modelId", "modelRole", "modelOverride", "modelAlias") and v is not None:
                hits.append(f"{path}/{k}")
            model_keys(v, hits, f"{path}/{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o):
            model_keys(v, hits, f"{path}[{i}]")
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=None, help="write route-facts.json here")
    ap.add_argument("--tables", default=None, help="write markdown tables here")
    args = ap.parse_args()

    pol = load_json(POLICY)
    spec = load_json(SPEC)
    disp = load_json(DISPATCH)
    reg = load_json(REGISTRY)
    st = os.stat(CONFIG)
    with open(CONFIG, "r", encoding="utf-8") as fh:
        cfg_text = fh.read()
    cfg = yaml.safe_load(cfg_text)

    items = spec["items"]
    roles = collections.Counter(i["role"] for i in items)
    axes = collections.Counter()
    axis_roles = collections.defaultdict(collections.Counter)
    for i in items:
        for a in i["axes"]:
            axes[a] += 1
            axis_roles[a][i["role"]] += 1

    n = len(items)
    overrides = {k: (v.lstrip("@") if isinstance(v, str) else v)
                 for k, v in cfg["task"]["agentModelOverrides"].items()}
    model_roles = cfg["modelRoles"]
    chains = cfg.get("retry", {}).get("fallbackChains", {})
    enabled = cfg.get("enabledModels") or []
    enabled_base = {m.split(":")[0] for m in enabled}

    used_roles = sorted(roles)
    per_alias = collections.Counter()
    per_model = collections.Counter()
    per_model_roles = collections.defaultdict(collections.Counter)
    route_rows = []
    for role in used_roles:
        alias = overrides.get(role)
        target = model_roles.get(alias) if alias else None
        per_alias[alias] += roles[role]
        per_model[target] += roles[role]
        per_model_roles[target][role] = roles[role]
        chain = chains.get(alias) if alias else None
        route_rows.append(
            {
                "role": role,
                "seats": roles[role],
                "override": f"@{alias}" if alias else None,
                "alias_target": target,
                "in_enabled_models": bool(target and target.split(":")[0] in enabled_base),
                "fallback_chain": chain,
                "fallback_head": chain[0] if chain else None,
            }
        )

    attack_p = sum(roles[r] for r in ATTACK_PRIMARY if r in roles)
    attack_e = sum(roles[r] for r in ATTACK_EXTENDED if r in roles)
    policy_lane_ids = [l["id"] for l in pol["lanes"]]
    proposal_roles = pol["nativeProfiles"]["omp-native-v1"]["proposalRoles"]
    swarm = pol["sighting"]["dispatch"]["swarm"]
    l1_alias = pol["sighting"]["dispatch"]["missionFormat"]["l1Alias"]
    profile_ceiling = pol["nativeProfiles"]["omp-native-v1"]["concurrencyCeiling"]

    members = reg.get("members", {})
    disp_tasks = disp["taskCall"]["tasks"]
    reg_roles = collections.Counter(m.get("role") for m in members.values())
    spec_by_name = {i["name"]: i["role"] for i in items}
    reg_role_mismatch = sorted(
        name for name, m in members.items() if spec_by_name.get(name) != m.get("role")
    )
    modelish = model_keys(disp)

    checks = []

    def check(name, ok, detail, severity="FAIL"):
        checks.append({"check": name, "ok": bool(ok), "detail": detail, "severity": severity})

    check("roles.resolve", all(r["alias_target"] for r in route_rows),
          f"{len(route_rows)}/{len(used_roles)} wave roles have an agentModelOverrides entry")
    check("models.enabled", all(r["in_enabled_models"] for r in route_rows),
          "every resolved model id is in config enabledModels (base id, effort suffix dropped)")
    check("aliases.fallback", all(r["fallback_head"] for r in route_rows),
          "every used alias has a retry.fallbackChains entry")
    check("roles.in_policy_proposalRoles", set(used_roles) <= set(proposal_roles),
          f"wave roles ⊆ proposalRoles ({len(proposal_roles)} roles)")
    missing_lane = sorted(set(used_roles) - set(policy_lane_ids))
    check("roles.in_policy_lanes", not missing_lane,
          f"policy lanes[] enumerates {len(policy_lane_ids)} role ids; wave roles absent from it: "
          f"{missing_lane or 'none'} ({sum(roles[r] for r in missing_lane)} seats)",
          severity="WARN")
    check("wave.band", swarm["waveMinLanes"] <= n <= swarm["waveMaxLanes"],
          f"{n} seats in policy band [{swarm['waveMinLanes']},{swarm['waveMaxLanes']}]")
    check("wave.hard_ceiling", n <= swarm["maxLanes"], f"{n} seats <= policy maxLanes {swarm['maxLanes']}")
    check("wave.declared_slack", n < spec["maxLanes"],
          f"spec maxLanes={spec['maxLanes']} vs {n} items (slack {spec['maxLanes'] - n})",
          severity="WARN")
    check("attack.share", attack_p / n >= ATTACK_SHARE_FLOOR,
          f"{attack_p}/{n} = {attack_p / n:.2%} >= {ATTACK_SHARE_FLOOR:.0%}")
    check("dispatch.no_model_passthrough", not modelish,
          f"model-ish keys in dispatch.json: {len(modelish)} (routing is role-only)")
    check("seats.agreement", len(disp_tasks) == n == len(members),
          f"spec items {n}, dispatch tasks {len(disp_tasks)}, registry members {len(members)}")
    check("registry.roles_match_spec", not reg_role_mismatch,
          f"registry role != spec role for: {reg_role_mismatch or 'none'}")
    check("concurrency.profile_ceiling", n <= profile_ceiling,
          f"{n} seats in one task call vs omp-native-v1.concurrencyCeiling {profile_ceiling}",
          severity="WARN")
    main_alias = overrides.get("main")
    check("route.l1_alias", model_roles.get(l1_alias) == model_roles.get(main_alias),
          f"policy l1Alias @{l1_alias} -> {model_roles.get(l1_alias)}; live main -> "
          f"@{main_alias} -> {model_roles.get(main_alias)}", severity="WARN")
    map_drift = {r: (f"@{a}", f"@{overrides.get(r)}")
                 for r, a in RUN9_MAP.items() if overrides.get(r) != a}
    extra_roles = sorted(set(overrides) - set(RUN9_MAP))
    check("route.run9_map_equality", not map_drift,
          f"live agentModelOverrides vs binding run-9 map: {len(RUN9_MAP)} roles compared, "
          f"drift {map_drift or 'none'}, roles outside the map {extra_roles or 'none'}")

    facts = {
        "wave": spec["wave"],
        "seats": n,
        "spec_maxLanes": spec["maxLanes"],
        "policy": {
            "path": POLICY,
            "sha256": sha256(POLICY),
            "wave_band": [swarm["waveMinLanes"], swarm["waveMaxLanes"]],
            "maxLanes": swarm["maxLanes"],
            "l1Alias": l1_alias,
            "concurrencyCeiling_omp_native_v1": profile_ceiling,
        },
        "spec": {"path": SPEC, "sha256": sha256(SPEC)},
        "dispatch": {"path": DISPATCH, "sha256": sha256(DISPATCH)},
        "registry": {"path": REGISTRY, "sha256": sha256(REGISTRY)},
        "config": {
            "path": CONFIG,
            "sha256": sha256(CONFIG),
            "size": st.st_size,
            "mtime": st.st_mtime,
            "mtime_iso": __import__("datetime").datetime.fromtimestamp(
                st.st_mtime).astimezone().isoformat(),
            "mode": oct(stat.S_IMODE(st.st_mode)),
            "task_maxConcurrency": cfg["task"].get("maxConcurrency"),
            "async_maxJobs": cfg.get("async", {}).get("maxJobs"),
        },
        "role_counts": dict(roles),
        "axis_counts": dict(axes),
        "axis_roles": {k: dict(v) for k, v in axis_roles.items()},
        "attack": {
            "primary_roles": list(ATTACK_PRIMARY),
            "primary_seats": attack_p,
            "primary_share": round(attack_p / n, 6),
            "extended_roles": list(ATTACK_EXTENDED),
            "extended_seats": attack_e,
            "extended_share": round(attack_e / n, 6),
            "floor": ATTACK_SHARE_FLOOR,
        },
        "per_alias": dict(per_alias),
        "per_model": dict(per_model),
        "per_model_roles": {k: dict(v) for k, v in per_model_roles.items()},
        "routes": route_rows,
        "connector_seats": roles.get("connector", 0),
        "checks": checks,
        "failures": [c["check"] for c in checks if not c["ok"] and c["severity"] == "FAIL"],
        "warnings": [c["check"] for c in checks if not c["ok"] and c["severity"] == "WARN"],
    }

    lines = []
    add = lines.append
    add(f"## Seats by role ({n} total)\n")
    add("| role | seats | share | axes |")
    add("|---|---:|---:|---|")
    for role, cnt in roles.most_common():
        ax = ",".join(sorted(a for a, rr in axis_roles.items() if role in rr))
        add(f"| {role} | {cnt} | {cnt / n:.2%} | {ax} |")
    add(f"| **total** | **{n}** | 100.00% | |")
    add("")
    add("## Attack share\n")
    add("| definition | roles | seats | share | floor | result |")
    add("|---|---|---:|---:|---:|---|")
    for label, rs, seats in (
        ("seat item (primary)", ATTACK_PRIMARY, attack_p),
        ("addendum §2 (extended)", ATTACK_EXTENDED, attack_e),
    ):
        ok = "PASS" if seats / n >= ATTACK_SHARE_FLOOR else "FAIL"
        add(f"| {label} | {'/'.join(rs)} | {seats}/{n} | {seats / n:.2%} | ≥25% | {ok} |")
    add("")
    add("## Route by role (live `task.agentModelOverrides`)\n")
    add("| role | seats | override | alias → model | fallback head | in enabledModels |")
    add("|---|---:|---|---|---|---|")
    for r in route_rows:
        add(f"| {r['role']} | {r['seats']} | `{r['override']}` | `{r['alias_target']}` | "
            f"`{r['fallback_head']}` | {'yes' if r['in_enabled_models'] else 'NO'} |")
    add("")
    add("## Seats per model\n")
    add("| model | seats | share | roles |")
    add("|---|---:|---:|---|")
    for m, cnt in per_model.most_common():
        rr = ", ".join(f"{r} {c}" for r, c in per_model_roles[m].most_common())
        add(f"| `{m}` | {cnt} | {cnt / n:.2%} | {rr} |")
    add(f"| **distinct models: {len(per_model)}** | **{n}** | 100.00% | |")
    add("")
    add("## Checks\n")
    add("| check | result | detail |")
    add("|---|---|---|")
    for c in checks:
        verdict = "PASS" if c["ok"] else c["severity"]
        add(f"| `{c['check']}` | {verdict} | {c['detail']} |")
    tables = "\n".join(lines) + "\n"

    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(facts, fh, indent=1, sort_keys=True)
            fh.write("\n")
    if args.tables:
        with open(args.tables, "w", encoding="utf-8") as fh:
            fh.write(tables)
    sys.stdout.write(tables)
    for f in facts["failures"]:
        print(f"FAIL {f}")
    for w in facts["warnings"]:
        print(f"WARN {w}")
    return 1 if facts["failures"] else 0


if __name__ == "__main__":
    sys.exit(main())
