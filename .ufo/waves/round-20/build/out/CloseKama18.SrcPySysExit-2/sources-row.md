| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| TBD | Python 3.14 `sys` documentation — https://docs.python.org/3.14/library/sys.html#sys.exit | docs | A | CPython `sys.exit` status semantics for non-integer arguments relevant to gate failure classification | §`sys.exit`, optional-argument paragraph; page title: Python 3.14.8 documentation | Any argument other than an integer or `None` is printed to stderr and results in exit code 1; status alone does not encode why exit was requested. | queued | 2026-10-21 | on-release | — |

Quote (15 words): “any other object is printed to stderr and results in an exit code of 1.”
Location: Python 3.14.8 Library Reference, `sys` → `sys.exit(arg)`, optional-argument paragraph; https://docs.python.org/3.14/library/sys.html#sys.exit.