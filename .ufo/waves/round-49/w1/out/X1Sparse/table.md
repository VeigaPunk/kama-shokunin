| case | before (438127bc) | before s | after (74558c71, `server_size` set) | after s |
|---|---|---|---|---|
| regular member, right digests (control) | **ok** | 0.001 | **ok** | 0.002 |
| regular member, wrong member digest | `provenance-member-digest-mismatch` | 0.001 | `provenance-member-digest-mismatch` | 0.001 |
| member is a symlink | `provenance-member-not-a-file` | 0.001 | `provenance-member-not-a-file` | 0.001 |
| member is a directory | `provenance-member-absent` | 0.002 | `provenance-member-absent` | 0.001 |
| member absent | `provenance-member-absent` | 0.001 | `provenance-member-absent` | 0.001 |
| old-GNU sparse, realsize 1 GiB | `provenance-member-digest-mismatch` | 0.545 | `provenance-member-sparse` | 0.001 |
| old-GNU sparse, realsize 8589934591 | `provenance-member-digest-mismatch` | 4.243 | `provenance-member-sparse` | 0.001 |
| PAX 0.1 sparse, `GNU.sparse.size` 10^15 | **no return in 20 s** | 20 | `provenance-member-sparse` | 0.002 |
| PAX 1.0 sparse, `GNU.sparse.realsize` 10^15 | **no return in 20 s** | 20 | `provenance-member-sparse` | 0.002 |
| tar index of 20 000 entries | `provenance-member-absent` | 0.215 | `provenance-archive-too-many-members` | 0.043 |
| gzip that inflates to 8 GiB of zero blocks | `provenance-member-absent` | 0.054 | `provenance-member-absent` | 0.021 |
| PAX `size` 10^15 over a 4 GiB zero payload | `provenance-archive-unreadable` | 1.821 | `provenance-archive-unreadable` | 1.803 |
| archive is a 2 GiB sparse file | **no return in 60 s** | 60 | `provenance-archive-too-large` | 0.001 |
| archive path is a FIFO | **no return in 6 s** | 6 | `provenance-archive-not-regular` | 0.001 |
| archive path is /dev/zero | **no return in 6 s** | 6 | `provenance-archive-not-regular` | 0.001 |
| duplicate names: first good, last decoy | `provenance-member-digest-mismatch` | 0.001 | `provenance-member-size-mismatch` | 0.001 |
| duplicate names: first decoy, last good | **ok** | 0.002 | **ok** | 0.001 |

### Round-49 code, `server_size=None` (4-arg form; attribute which bound fires)

| case | outcome | s |
|---|---|---|
| regular member, right digests (control) | **ok** | 0.001 |
| regular member, wrong member digest | `provenance-member-digest-mismatch` | 0.001 |
| member is a symlink | `provenance-member-not-a-file` | 0.001 |
| member is a directory | `provenance-member-absent` | 0.001 |
| member absent | `provenance-member-absent` | 0.001 |
| old-GNU sparse, realsize 1 GiB | `provenance-member-sparse` | 0.001 |
| old-GNU sparse, realsize 8589934591 | `provenance-member-sparse` | 0.001 |
| PAX 0.1 sparse, `GNU.sparse.size` 10^15 | `provenance-member-sparse` | 0.001 |
| PAX 1.0 sparse, `GNU.sparse.realsize` 10^15 | `provenance-member-sparse` | 0.001 |
| tar index of 20 000 entries | `provenance-archive-too-many-members` | 0.043 |
| gzip that inflates to 8 GiB of zero blocks | `provenance-member-absent` | 0.018 |
| PAX `size` 10^15 over a 4 GiB zero payload | `provenance-archive-unreadable` | 1.845 |
| archive is a 2 GiB sparse file | `provenance-archive-too-large` | 0.001 |
| archive path is a FIFO | `provenance-archive-not-regular` | 0.001 |
| archive path is /dev/zero | `provenance-archive-not-regular` | 0.001 |
| duplicate names: first good, last decoy | `provenance-member-digest-mismatch` | 0.002 |
| duplicate names: first decoy, last good | **ok** | 0.002 |
