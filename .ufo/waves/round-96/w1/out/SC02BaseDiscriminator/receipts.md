# SC02BaseDiscriminator — receipts (frozen C1 counter, base revision 5d43528b)

## R1 — base control, exactly as committed (--burners 0 --skip-load)
command: python3 tools/round96-router-budget.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --rev 5d43528badc31ad6c0ca1848c00561f531924e4d --work <scratch>/work-a --burners 0 --skip-load
exit: 2  (could-not-evaluate: margin guard, see R2)
```
ROUTER_BUDGET96_CELL nat W01-slow-x1 ok=1 want=MODEL_UNLOADED/router-model-invalid run1=MODEL_UNLOADED/router-model-invalid/1.35s run2=MODEL_UNLOADED/router-model-invalid/1.45s
ROUTER_BUDGET96_CELL nat W02-slow-x8 ok=1 want=MODEL_UNLOADED/router-model-invalid run1=MODEL_UNLOADED/router-model-invalid/10.02s run2=MODEL_UNLOADED/router-model-invalid/10.07s
ROUTER_BUDGET96_CELL nat W03-slow-x40 ok=1 want=MODEL_UNLOADED/router-model-invalid run1=MODEL_UNLOADED/router-model-invalid/49.54s run2=MODEL_UNLOADED/router-model-invalid/54.94s
ROUTER_BUDGET96_CELL nat W04-ok-x8 ok=1 want=MODEL_OK/router-unloaded-autoload run1=MODEL_OK/router-unloaded-autoload/0.16s run2=MODEL_OK/router-unloaded-autoload/0.15s
ROUTER_BUDGET96_CELL nat W05-slow-then-ok ok=1 want=MODEL_OK/router-unloaded-autoload run1=MODEL_OK/router-unloaded-autoload/9.55s run2=MODEL_OK/router-unloaded-autoload/9.48s
ROUTER_BUDGET96_CELL nat W06-missing-x8 ok=1 want=MODEL_UNLOADED/router-model-missing run1=MODEL_UNLOADED/router-model-missing/0.15s run2=MODEL_UNLOADED/router-model-missing/0.15s
ROUTER_BUDGET96_CELL nat W07-fast-k40 ok=1 want=MODEL_UNLOADED/router-model-invalid run1=MODEL_UNLOADED/router-model-invalid/0.16s run2=MODEL_UNLOADED/router-model-invalid/0.14s
ROUTER_BUDGET96_CELL nat W08-hardlink-x8 ok=1 want=MODEL_UNLOADED/router-model-invalid run1=MODEL_UNLOADED/router-model-invalid/1.52s run2=MODEL_UNLOADED/router-model-invalid/1.61s
ROUTER_BUDGET96_CELL nat W09-undecided-big ok=1 want=MODEL_OK/router-unloaded-autoload run1=MODEL_OK/router-unloaded-autoload/0.13s run2=MODEL_OK/router-unloaded-autoload/0.14s
ROUTER_BUDGET96_CELL nat W11-700k ok=0 want=MODEL_UNLOADED/router-model-invalid run1=MODEL_OK/router-unloaded-autoload/1.54s run2=MODEL_OK/router-unloaded-autoload/1.53s
ROUTER_BUDGET96_CELL nat W12-strings ok=0 want=MODEL_OK/router-unloaded-autoload run1=MODEL_UNLOADED/router-model-invalid/0.13s run2=MODEL_UNLOADED/router-model-invalid/0.12s
ROUTER_BUDGET96_CELL nat W10-rewrite ok=1 v1=MODEL_UNLOADED/router-model-invalid v2=MODEL_OK/router-unloaded-autoload v3=MODEL_UNLOADED/router-model-invalid
ROUTER_BUDGET96 could-not-evaluate: W03 natural pass 54.9s < 1.2 x 60s — the round-94 constant wrapper would not truncate this listing on this host, so no discriminator is claimed
EXIT=2
```

## R2 — base control, guard bypassed, both passes (--burners 0 --allow-clock)
command: python3 tools/round96-router-budget.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --rev 5d43528badc31ad6c0ca1848c00561f531924e4d --work <scratch>/work-base-full --burners 0 --allow-clock
exit: 1
```
ROUTER_BUDGET96_CELL nat W01..W09 ok=1 (all nine); W10-rewrite ok=1 v1=invalid v2=MODEL_OK v3=invalid
ROUTER_BUDGET96_CELL nat W11-700k ok=0 want=MODEL_UNLOADED/router-model-invalid run1=MODEL_OK/router-unloaded-autoload/2.04s run2=MODEL_OK/router-unloaded-autoload/2.06s
ROUTER_BUDGET96_CELL nat W12-strings ok=0 want=MODEL_OK/router-unloaded-autoload run1=MODEL_UNLOADED/router-model-invalid/0.17s run2=MODEL_UNLOADED/router-model-invalid/0.17s
ROUTER_BUDGET96_CELL load W11-700k ok=0 run1=MODEL_OK/router-unloaded-autoload/1.66s run2=MODEL_OK/router-unloaded-autoload/1.67s
ROUTER_BUDGET96_CELL load W12-strings ok=0 run1=MODEL_UNLOADED/router-model-invalid/0.14s run2=MODEL_UNLOADED/router-model-invalid/0.13s
ROUTER_BUDGET96_CELL load W01..W09 ok=1 (all nine); load W10-rewrite ok=1
ROUTER_BUDGET96 cells=12 mismatches=2 positive_mismatches=0 load_cells=12 load_stable=1 budget=work probe=rev probe_sha256=b49d961a0548f3c30a264d036b080c0b99a2bb8dfce523f575fbdb00d76a85df base_sha256=27065a5c487ec819a975cc96d3c990ab5161d0e55d82be02a87dde86974ed3b4 rev=5d43528badc31ad6c0ca1848c00561f531924e4d w03_seconds=66.9 load1_nat=25.34 burners=0
EXIT=1
```

## R3 — tip (M1 candidate = freeze commit 58001b71), guard bypassed, both passes
command: python3 tools/round96-router-budget.py --repo . --rev 58001b71 --work <scratch>/work-tip-full --burners 0 --allow-clock
```
ROUTER_BUDGET96_CELL nat W01..W09 ok=1 (all nine); nat W11-700k ok=1 run1=MODEL_UNLOADED/router-model-invalid; nat W10-rewrite ok=1
ROUTER_BUDGET96_CELL nat W12-strings ok=0 want=MODEL_OK/router-unloaded-autoload run1=MODEL_UNLOADED/router-model-invalid/0.13s run2=MODEL_UNLOADED/router-model-invalid/0.13s
(see R4 for the full tip summary line)
```
