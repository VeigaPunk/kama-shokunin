# X12Zip probe summary

Frozen tool: tools/kama-llamacpp-live.py at lane commit 97c864bead3ee4a2f629574e77263d33834ec98a. Patched = the proposed
fix in proposed/. RSS is the whole-child peak (interpreter baseline ~27 MB).

| case | archive | decompressed / declared | token | s | peak RSS | member hashed | extractfile | decompressed consumed | patched token | patched s |
|---|---|---|---|---|---|---|---|---|---|---|
| a_20000_tiny | 9.78 MiB | - | provenance-archive-too-many-members | 0.049 | 31 MB | False | 0 | 2.00 MiB | provenance-archive-too-many-members | 0.042 |
| b_truncated_declared_size | 5.51 KiB | - | provenance-archive-unreadable | 0.001 | 27 MB | False | 0 | 9.50 KiB | provenance-archive-unreadable | 0.001 |
| b2_padded_wrong_data | 10.00 KiB | - | provenance-member-digest-mismatch | 0.001 | 26 MB | True | 1 | 9.00 KiB | provenance-member-digest-mismatch | 0.001 |
| c_gzip_zeros_huge | 17.87 MiB | 4.00 GiB | provenance-member-absent | 0.01 | 29 MB | False | 0 | 512 B | provenance-member-absent | 0.009 |
| c2_gzip_seek_512m | 2.23 MiB | 512.00 MiB | provenance-member-absent | 0.247 | 28 MB | False | 0 | 512.00 MiB | provenance-member-absent | 0.223 |
| c2_gzip_seek_2g | 8.94 MiB | 2.00 GiB | provenance-member-absent | 0.952 | 28 MB | False | 0 | 2.00 GiB | provenance-archive-walk-too-large | 0.005 |
| c3_gzip_seek_past_eof | 1.12 MiB | 256.00 MiB | provenance-archive-unreadable | 0.127 | 28 MB | False | 0 | 256.00 MiB | provenance-archive-walk-too-large | 0.001 |
| e_xz_seek_4g | 610.25 KiB | 4.00 GiB | provenance-member-absent | 5.939 | 28 MB | False | 0 | 4.00 GiB | provenance-archive-walk-too-large | 0.001 |
| f_bz2_seek_256m | 274 B | 256.00 MiB | provenance-member-absent | 0.407 | 30 MB | False | 0 | 256.00 MiB | provenance-member-absent | 0.411 |
| f_bz2_seek_8g | 5.96 KiB | 8.00 GiB | provenance-member-absent | 12.895 | 29 MB | False | 0 | 8.00 GiB | provenance-archive-walk-too-large | 0.002 |
| f_bz2_seek_32g | 23.49 KiB | 32.00 GiB | provenance-member-absent | 52.118 | 30 MB | False | 0 | 32.00 GiB | provenance-archive-walk-too-large | 0.002 |
| f_bz2_seek_past_eof | 5.96 KiB | 8.00 GiB | provenance-archive-unreadable | 12.678 | 30 MB | False | 0 | 8.00 GiB | provenance-archive-walk-too-large | 0.002 |
| boundary_4096_ok | 2.01 MiB | - | accepted | 0.04 | 28 MB | True | 1 | 2.01 MiB | accepted | 0.038 |
| boundary_4097_cap | 2.01 MiB | - | provenance-archive-too-many-members | 0.04 | 28 MB | False | 0 | 2.00 MiB | provenance-archive-too-many-members | 0.039 |
| d_valid_many | 24.82 KiB | - | accepted | 0.048 | 28 MB | True | 1 | 1.96 MiB | accepted | 0.044 |

## Cost of a declared skip through verify_archive_member (frozen)

- f_bz2_seek_256m: 274 B on disk, 256.00 MiB decoded in 0.407 s (660 MB/s), ratio 979691x
- f_bz2_seek_8g: 6101 B on disk, 8.00 GiB decoded in 12.895 s (666 MB/s), ratio 1407955x
- f_bz2_seek_32g: 24054 B on disk, 32.00 GiB decoded in 52.118 s (659 MB/s), ratio 1428442x
- e_xz_seek_4g: 624896 B on disk, 4.00 GiB decoded in 5.939 s (723 MB/s), ratio 6873x
- c2_gzip_seek_2g: 9370979 B on disk, 2.00 GiB decoded in 0.952 s (2256 MB/s), ratio 229x
