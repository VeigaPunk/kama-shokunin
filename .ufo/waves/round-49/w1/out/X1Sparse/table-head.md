| case | HEAD 7fab24e7 (post-integration) | s |
|---|---|---|
| regular member, right digests (control) | **ok** | 0.001 |
| member entry is a symlink | `provenance-member-not-a-file` | 0.001 |
| member absent | `provenance-member-absent` | 0.001 |
| old-GNU sparse, realsize 1 GiB | `provenance-member-sparse` | 0.001 |
| old-GNU sparse, realsize 8589934591 | `provenance-member-sparse` | 0.001 |
| PAX 0.1 sparse, `GNU.sparse.size` 10^15 | `provenance-member-sparse` | 0.002 |
| PAX 1.0 sparse, `GNU.sparse.realsize` 10^15 | `provenance-member-sparse` | 0.001 |
| tar index of 20 000 entries | `provenance-archive-too-many-members` | 0.043 |
| gzip that inflates to 8 GiB of zero blocks | `provenance-member-absent` | 0.032 |
| PAX `size` 10^15 over a 4 GiB zero payload | `provenance-archive-unreadable` | 1.786 |
| archive is a 2 GiB sparse file | `provenance-archive-too-large` | 0.001 |
| archive path is a FIFO | `provenance-archive-not-regular` | 0.001 |
| archive path is /dev/zero | `provenance-archive-not-regular` | 0.001 |
| PAX `size` 10^15 over a 16 GiB zero payload | `provenance-archive-unreadable` | 7.198 |
| PAX 0.0 sparse, `GNU.sparse.size` 10^15 | `provenance-member-sparse` | 0.002 |
| member entry is a directory | `provenance-member-not-a-file` | 0.001 |
| member entry is a FIFO | `provenance-member-not-a-file` | 0.001 |
| malformed `GNU.sparse.map` ("zz") | uncaught `ValueError` | 0.001 |
| PAX 1.0 header with no map block | uncaught `ValueError` | 0.002 |
| real b11909-shaped asset, 62 entries | **ok** | 0.154 |
