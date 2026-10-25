#!/usr/bin/env python3
"""Bounded behavioral detector for the R36-D2A / R36-D2B legs.

Read-only: reads the staged SOURCES.append.md, imports a counter copy given on
argv, runs fixed probes, prints one line per probe. No repo writes.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

APPEND = Path("/home/vgpnk/Projects/shokuknow/merge/kama/SOURCES.append.md").read_text(encoding="utf-8")

SYNTH_CENSUS_TIP = (
    "kama\tW04\tx\n"
    "kama\tok\t/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md\n"
)
SYNTH_EXITCODES = json.dumps(
    {"seats": [{"name": "ScribeLog", "rc": 1}, {"name": "RevQ206", "rc": 1}]}
)
SYNTH_SEATLOGS = "seat ScribeLog failed: rate_limit 429\n"

GOOD = {
    "R36-D1": "R36-D1: .ufo/waves/round-36/census-end.out",
    "R36-D2A": "R36-D2A: S371 native_api miswritten",
    "R36-D2B": "R36-D2B: http_server.py S364 S365 S377 S396",
    "R36-D3": "R36-D3: ScribeLog RevQ206 429",
}


def load(path: str):
    spec = importlib.util.spec_from_file_location("cnt", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def aggregate(mod, overrides: dict[str, str]) -> dict[str, int]:
    rows = dict(GOOD)
    rows.update(overrides)
    lesson = "\n".join(rows[k] for k in mod.IDS) + "\n"
    return mod.score(
        lesson,
        append=APPEND,
        census_tip=SYNTH_CENSUS_TIP,
        census_base=None,
        exitcodes=SYNTH_EXITCODES,
        seatlogs=SYNTH_SEATLOGS,
        lesson_blob=mod.LESSON_BLOB,
        report_blob=mod.REPORT_BLOB,
    )


PROBES = {
    "P0_good": {},
    "P1_D2B_with_S359": {"R36-D2B": "R36-D2B: http_server.py S364 S365 S377 S396 S359"},
    "P2_D2A_no_miswritten": {"R36-D2A": "R36-D2A: S371 native_api"},
    "P3_D2A_inverted_but_all_tokens": {"R36-D2A": "R36-D2A: S371 native_api; S366 miswritten"},
}


def main() -> int:
    mod = load(sys.argv[1])
    out = {"legs": {}, "aggregate": {}}
    # Leg-level: forbidden_in + holds, no aggregation.
    for name, row in (
        ("P1_D2B_with_S359", PROBES["P1_D2B_with_S359"]["R36-D2B"]),
        ("P2_D2A_no_miswritten", PROBES["P2_D2A_no_miswritten"]["R36-D2A"]),
        ("P3_D2A_inverted_but_all_tokens", PROBES["P3_D2A_inverted_but_all_tokens"]["R36-D2A"]),
        ("P0_good_D2B", GOOD["R36-D2B"]),
        ("P0_good_D2A", GOOD["R36-D2A"]),
    ):
        sid = "R36-D2B" if "D2B" in name else "R36-D2A"
        out["legs"][name] = {
            "sid": sid,
            "forbidden": mod.forbidden_in(sid, row),
            "holds": bool(
                mod.holds(
                    sid,
                    row,
                    append=APPEND,
                    census_tip=SYNTH_CENSUS_TIP,
                    census_base=None,
                    exitcodes=SYNTH_EXITCODES,
                    seatlogs=SYNTH_SEATLOGS,
                )
            ),
        }
    for name, ov in PROBES.items():
        out["aggregate"][name] = aggregate(mod, ov)
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
