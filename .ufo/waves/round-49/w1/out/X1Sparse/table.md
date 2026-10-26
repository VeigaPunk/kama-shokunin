| case | before 438127bc | s | after 74558c71 | s | after + proposed fix | s |
|---|---|---|---|---|---|---|
| regular member, right digests (control) | **ok** | 0.001 | **ok** | 0.002 | **ok** | 0.001 |
| regular member, wrong member digest | `provenance-member-digest-mismatch` | 0.001 | `provenance-member-digest-mismatch` | 0.001 | `provenance-member-digest-mismatch` | 0.002 |
| member entry is a symlink | `provenance-member-not-a-file` | 0.001 | `provenance-member-not-a-file` | 0.001 | `provenance-member-not-a-file` | 0.002 |
| member entry is a directory | `provenance-member-not-a-file` | 0.003 | `provenance-member-not-a-file` | 0.002 | `provenance-member-not-a-file` | 0.002 |
| member entry is a FIFO | `provenance-member-not-a-file` | 0.002 | `provenance-member-not-a-file` | 0.001 | `provenance-member-not-a-file` | 0.002 |
| member absent | `provenance-member-absent` | 0.001 | `provenance-member-absent` | 0.001 | `provenance-member-absent` | 0.001 |
| duplicate names: first good, last decoy | `provenance-member-digest-mismatch` | 0.001 | `provenance-member-size-mismatch` | 0.001 | `provenance-member-size-mismatch` | 0.002 |
| duplicate names: first decoy, last good | **ok** | 0.002 | **ok** | 0.001 | **ok** | 0.002 |
| old-GNU `S` sparse, realsize 1 GiB | `provenance-member-digest-mismatch` | 0.545 | `provenance-member-sparse` | 0.001 | `provenance-member-sparse` | 0.003 |
| old-GNU `S` sparse, realsize 8589934591 | `provenance-member-digest-mismatch` | 4.243 | `provenance-member-sparse` | 0.001 | `provenance-member-sparse` | 0.002 |
| PAX 0.0 sparse, `GNU.sparse.size` 10^15 | **no return**, killed at 30 s | 30 | `provenance-member-sparse` | 0.001 | `provenance-member-sparse` | 0.002 |
| PAX 0.1 sparse, `GNU.sparse.size` 10^15 | **no return**, killed at 20 s | 20 | `provenance-member-sparse` | 0.002 | `provenance-member-sparse` | 0.001 |
| PAX 1.0 sparse, `GNU.sparse.realsize` 10^15 | **no return**, killed at 20 s | 20 | `provenance-member-sparse` | 0.002 | `provenance-member-sparse` | 0.002 |
| tar index of 20 000 entries | `provenance-member-absent` | 0.215 | `provenance-archive-too-many-members` | 0.043 | `provenance-archive-too-many-members` | 0.05 |
| gzip that inflates to 8 GiB of zero blocks | `provenance-member-absent` | 0.054 | `provenance-member-absent` | 0.021 | `provenance-member-absent` | 0.021 |
| PAX `size` 10^15 over a 4 GiB zero payload | `provenance-archive-unreadable` | 1.821 | `provenance-archive-unreadable` | 1.803 | `provenance-member-too-large` | 0.012 |
| PAX `size` 10^15 over a 16 GiB zero payload | `provenance-archive-unreadable` | 7.008 | `provenance-archive-unreadable` | 7.021 | `provenance-member-too-large` | 0.032 |
| plain zeros archive, 512 MiB | `provenance-member-absent` | 38.4 | `provenance-member-absent` | 48.098 | - | - |
| archive is a 2 GiB sparse file | **no return**, killed at 60 s | 60 | `provenance-archive-too-large` | 0.001 | `provenance-archive-too-large` | 0.001 |
| archive path is a FIFO | **no return**, killed at 6 s | 6 | `provenance-archive-not-regular` | 0.001 | `provenance-archive-not-regular` | 0.001 |
| archive path is /dev/zero | **no return**, killed at 6 s | 6 | `provenance-archive-not-regular` | 0.001 | `provenance-archive-not-regular` | 0.001 |
| malformed `GNU.sparse.map` ("zz") | uncaught `ValueError` | 0.001 | uncaught `ValueError` | 0.002 | `provenance-archive-unreadable` | 0.001 |
| PAX 1.0 header with no map block | uncaught `ValueError` | 0.002 | uncaught `ValueError` | 0.001 | `provenance-archive-unreadable` | 0.001 |
| real b11909-shaped asset, 62 entries | **ok** | 0.149 | **ok** | 0.149 | **ok** | 0.149 |
