# X1Observe2 - observer vs frozen counter (C1 bind)

tip `97c864bead3ee4a2f629574e77263d33834ec98a`

- observer met=True; extended (parent-environ + marker) met=True
- counter: `bind=1 teardown=1 newrow=1 bound=3/3 met=True`

| leg | replay 1 (mine/counter) | replay 2 (mine/counter) | replay 3 (mine/counter) |
|---|---|---|---|
| exe | True/True | True/True | True/True |
| listen | True/True | True/True | True/True |
| tree | True/True | True/True | True/True |
| mapped | True/True | True/True | True/True |
| env | True/True | True/True | True/True |
| nonce | True/True | True/True | True/True |

- disagreements: 0
- base: counter `bind=0 teardown=0 newrow=0 bound=0/3 met=False`; observer six legs True, extended False; parent env {"canary_keys": ["KAMA_R50_CANARY"], "env_keys": ["HOME", "KAMA_R50_CANARY", "LANG", "PATH", "PYTHONPATH", "TMPDIR"], "pythonpath_keys": ["PYTHONPATH"]}

## counter detail lines

- `{'pid': 3523073, 'port': 39011, 'exe': True, 'listen': True, 'tree': True, 'env': True, 'mapped': True, 'child_pid_join': True, 'mapping_dev': '103:05', 'mapping_inode': '2092475926', 'nonce': 'kama witness 01ae50f9964edc30', 'nonce_roundtrip': True, 'aggregate': 'ok'}`
- `{'pid': 3545877, 'port': 36411, 'exe': True, 'listen': True, 'tree': True, 'env': True, 'mapped': True, 'child_pid_join': True, 'mapping_dev': '103:05', 'mapping_inode': '1022670727', 'nonce': 'kama witness e4556916eaf1b194', 'nonce_roundtrip': True, 'aggregate': 'ok'}`
- `{'pid': 3571221, 'port': 34151, 'exe': True, 'listen': True, 'tree': True, 'env': True, 'mapped': True, 'child_pid_join': True, 'mapping_dev': '103:05', 'mapping_inode': '552660834', 'nonce': 'kama witness 9ff9caf0d350b23b', 'nonce_roundtrip': True, 'aggregate': 'ok'}`
