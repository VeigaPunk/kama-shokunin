import sys, socket, importlib.util, os, time, json
spec = importlib.util.spec_from_file_location("c1", sys.argv[1])
c1 = importlib.util.module_from_spec(spec); spec.loader.exec_module(c1)
port = int(sys.argv[2])
ls = c1.listeners(port)
print("listeners", ls)
inodes = [i for i, _ in ls]
pids, unreadable = c1.holder_pids(inodes)
print("holder_pids", sorted(pids), "unreadable", sorted(unreadable))
