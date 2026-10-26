| no-deletion | pass | pass |  |  |
| below-threshold | pass | pass |  |  |
| exact-threshold-unrestored | pass | pass |  |  |
| restored-later | pass | pass |  |  |
| partial | pass | pass |  |  |
| undeclared-file | pass | pass |  |  |
| declared-file-removed | pass | pass |  |  |
| merge-first-parent | pass | pass |  |  |
| dashdash-lines | pass | pass |  |  |
| crlf-and-eof | pass | pass |  |  |
| multiset | pass | pass |  |  |
| window-max | FAIL | FAIL | exit_code == 1 | exit_code == 1 |
| relocation | pass | pass |  |  |
| contract | FAIL | FAIL | AuditError: contract line 2: 5 cells, want 4 | declarations[0].ok is True [EXC KeyError: 'declarations'], bad contract 2 rejected, bad contract 3 rejected, bad contract 4 rejected |
| threshold-flag | pass | pass |  |  |
| crlf-restore-exact | pass | pass |  |  |
| dup-kept-not-restored | pass | pass |  |  |
| final-segment | pass | pass |  |  |
| vanished-and-paths | FAIL | FAIL | AuditError: contract line 2: 5 cells, want 4 | summary.bad_declarations == 0 [EXC KeyError: 'bad_declarations'] |
| exempt-rewritten | FAIL | FAIL | AuditError: contract line 2: 5 cells, want 4 | graded == 0 [EXC KeyError: "event has no 'graded' (v3-only field; v2 event keys ['commit', 'deleted', 'file', 'held_at_to', 'restored_best', 'restored_by', 'restored_max', 'status'])"], ungraded == 24 [EXC KeyError: "event has no 'ungraded' (v3-only field; v2 event keys ['commit', 'deleted', 'file', 'held_at_to', 'restored_best', 'restored_by', 'restored_max', 'status'])"], status == ungraded, summary.ungraded_lines == 24 [EXC KeyError: 'ungraded_lines'], exit_code == 0 |
| exempt-gutted | FAIL | FAIL | AuditError: contract line 2: 5 cells, want 4 | graded == 24 [EXC KeyError: "event has no 'graded' (v3-only field; v2 event keys ['commit', 'deleted', 'file', 'held_at_to', 'restored_best', 'restored_by', 'restored_max', 'status'])"] |
| exempt-gutted-then-regrown | FAIL | FAIL | AuditError: contract line 2: 5 cells, want 4 | ungraded == 24 [EXC KeyError: "event has no 'ungraded' (v3-only field; v2 event keys ['commit', 'deleted', 'file', 'held_at_to', 'restored_best', 'restored_by', 'restored_max', 'status'])"], status == ungraded, exit_code == 0 |
| dated-rewritten | FAIL | FAIL | AuditError: contract line 2: 5 cells, want 4 | graded == 25 [EXC KeyError: "event has no 'graded' (v3-only field; v2 event keys ['commit', 'deleted', 'file', 'held_at_to', 'restored_best', 'restored_by', 'restored_max', 'status'])"], ungraded == 0 [EXC KeyError: "event has no 'ungraded' (v3-only field; v2 event keys ['commit', 'deleted', 'file', 'held_at_to', 'restored_best', 'restored_by', 'restored_max', 'status'])"] |
| only-errata | FAIL | FAIL | AuditError: contract line 2: 5 cells, want 4 | c1 status == ungraded, c1 ungraded == 25 [EXC KeyError: "event has no 'ungraded' (v3-only field; v2 event keys ['commit', 'deleted', 'file', 'held_at_to', 'restored_best', 'restored_by', 'restored_max', 'status'])"], c2 graded == 20 [EXC KeyError: "event has no 'graded' (v3-only field; v2 event keys ['commit', 'deleted', 'file', 'held_at_to', 'restored_best', 'restored_by', 'restored_max', 'status'])"] |
| clamp | pass | pass |  |  |
| bad-declarations | FAIL | FAIL | AuditError: contract line 2: 5 cells, want 4 | oks == [F,F,F,F,T] [EXC KeyError: 'declarations'], exit_code == 1 |
| clean | FAIL | FAIL | AuditError: contract line 2: 5 cells, want 4 | ungraded == 1 [EXC KeyError: 'ungraded'], bad_declarations == 0 [EXC KeyError: 'bad_declarations'], exit_code == 0 |