# M4Ctr mutation matrix — C2 round50-append-audit-v5-check.py

Pristine: tip `fixture=1 lane=1 scenarios=12/12 met=True` exit 0; base `fixture=0 lane=1 scenarios=9/12 met=False` exit 1.
Killed = verdict line or exit code differs from pristine on the same input.

| mutant | site (pristine.py) | tip | base | verdict |
|---|---|---|---|---|
| `M01_fence_open_indent4` | L103 FENCE_OPEN {0,3}->{0,4} | e0 `fixture=1 lane=1 scenarios=12/12 met=True` | e1 `fixture=0 lane=1 scenarios=9/12 met=False` | survived |
| `M02_fence_open_info_guard_off` | L311 backtick-in-info guard | e0 `fixture=1 lane=1 scenarios=12/12 met=True` | e1 `fixture=0 lane=1 scenarios=9/12 met=False` | survived |
| `M03_fence_close_strict_gt` | L322 k >= n -> k > n | e0 `fixture=1 lane=1 scenarios=12/12 met=True` | e1 `fixture=0 lane=1 scenarios=9/12 met=False` | survived |
| `M04_fence_close_no_trailing_ws` | L322 tail strip(b' \t') -> == b'' | e0 `fixture=1 lane=1 scenarios=12/12 met=True` | e1 `fixture=0 lane=1 scenarios=9/12 met=False` | survived |
| `M05_sections_h1_as_title` | L337 '## ' -> '#' | e1 `fixture=1 lane=0 scenarios=12/12 met=False` | e1 `fixture=0 lane=0 scenarios=9/12 met=False` | KILLED |
| `M06_sections_fence_blind` | L330 fence branch off | e0 `fixture=1 lane=1 scenarios=12/12 met=True` | e1 `fixture=0 lane=1 scenarios=9/12 met=False` | survived |
| `M07_key_cr_blind` | L344 CR strip dropped | e0 `fixture=1 lane=1 scenarios=12/12 met=True` | e1 `fixture=0 lane=1 scenarios=9/12 met=False` | survived |
| `M08_split_lines_keep_trailing_empty` | L349-351 trailing pop dropped | e0 `fixture=1 lane=1 scenarios=12/12 met=True` | e1 `fixture=0 lane=1 scenarios=9/12 met=False` | survived |
| `M09_origins_births_only_off` | L455 birth skip off | e0 `fixture=1 lane=1 scenarios=12/12 met=True` | e1 `fixture=0 lane=1 scenarios=9/12 met=False` | survived |
| `M10_origins_parent_last_wins` | L454 |= -> = | e0 `fixture=1 lane=1 scenarios=12/12 met=True` | e1 `fixture=0 lane=1 scenarios=9/12 met=False` | survived |
| `M11_origins_shortcut_removed` | L450-452 identical-parent shortcut removed | e0 `fixture=1 lane=1 scenarios=12/12 met=True` | e1 `fixture=0 lane=1 scenarios=9/12 met=False` | survived (equivalent) |
| `M12_native_origin_conjunct_dropped` | L489 origin conjunct dropped | e0 `fixture=1 lane=1 scenarios=12/12 met=True` | e1 `fixture=0 lane=1 scenarios=9/12 met=False` | survived |
| `M13_native_section_test_inverted` | L489 in ex -> not in ex | e1 `fixture=1 lane=0 scenarios=12/12 met=False` | e1 `fixture=0 lane=0 scenarios=9/12 met=False` | KILLED |
| `M14_native_threshold_ge` | L491 > -> >= | e1 `fixture=1 lane=0 scenarios=12/12 met=False` | e1 `fixture=0 lane=1 scenarios=9/12 met=False` | KILLED (tip only) |
| `M15_numstat_added_column` | L473 ns[1] -> ns[0] | e1 `fixture=1 lane=0 scenarios=12/12 met=False` | e1 `fixture=0 lane=0 scenarios=9/12 met=False` | KILLED |
| `M16_numstat_underreport_ok` | L473 != -> < | e0 `fixture=1 lane=1 scenarios=12/12 met=True` | e1 `fixture=0 lane=1 scenarios=9/12 met=False` | survived |
| `M17_fixture_arithmetic_dropped` | L213-217 fixture sum check off | e0 `fixture=1 lane=1 scenarios=12/12 met=True` | e1 `fixture=0 lane=1 scenarios=9/12 met=False` | survived |
| `M18_lane_arithmetic_dropped` | L467-470 lane sum check off | e0 `fixture=1 lane=1 scenarios=12/12 met=True` | e1 `fixture=0 lane=1 scenarios=9/12 met=False` | survived |
| `M19_order_expectation_loosened` | L279 graded pin dropped | e0 `fixture=1 lane=1 scenarios=12/12 met=True` | e1 `fixture=0 lane=1 scenarios=9/12 met=False` | survived |
| `M20_fence_want_exit_0` | L288 want_exit 1 -> 0 | e1 `fixture=0 lane=1 scenarios=11/12 met=False` | e1 `fixture=0 lane=1 scenarios=9/12 met=False` | KILLED (tip only) |
| `M21_crlf_fixture_lf_move` | L296 CRLF -> LF move | e0 `fixture=1 lane=1 scenarios=12/12 met=True` | e1 `fixture=0 lane=1 scenarios=10/12 met=False` | KILLED (base only) |
| `M22_order_parents_never_swapped` | L275 parents always [ca, cb] | e0 `fixture=1 lane=1 scenarios=12/12 met=True` | e1 `fixture=0 lane=1 scenarios=10/12 met=False` | KILLED (base only) |
| `M23_lane_bad_decls_neutralized` | L397 == 0 -> is not None | e0 `fixture=1 lane=1 scenarios=12/12 met=True` | e1 `fixture=0 lane=1 scenarios=9/12 met=False` | survived |
| `M24_lane_events_gt5` | L397 >= 5 -> > 5 | e1 `fixture=1 lane=0 scenarios=12/12 met=False` | e1 `fixture=0 lane=0 scenarios=9/12 met=False` | KILLED |
| `M25_met_or` | L531 and -> or | e0 `fixture=1 lane=1 scenarios=12/12 met=True` | e0 `fixture=0 lane=1 scenarios=9/12 met=True` | KILLED (base only) |
| `M26_deleted_with_pos_args_swapped` | L366 parent/commit swapped | e1 `CRASH: (empty stdout, empty stderr)` | e1 `CRASH: (empty stdout, empty stderr)` | KILLED (crash) |
| `M27_native_pos_off_by_one` | L489 pos-1 -> pos | e1 `CRASH: (empty stdout, empty stderr)` | e1 `CRASH: (empty stdout, empty stderr)` | KILLED (crash) |
| `M28_binder_neg3_emptied` | L105 NEG3 = () | e0 `fixture=1 lane=1 scenarios=12/12 met=True` | e1 `fixture=0 lane=1 scenarios=9/12 met=False` | survived |
