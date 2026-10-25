import sys
path, newrows_file = sys.argv[1], sys.argv[2]
rows = open(newrows_file).read().splitlines()
lines = open(path).read().split('\n')
start = lines.index('## Axes')
i = start + 1
while not lines[i].startswith('|'):
    i += 1
data_start = i + 2
j = data_start
while j < len(lines) and lines[j].startswith('|'):
    j += 1
newlines = lines[:data_start] + rows + lines[j:]
open(path, 'w').write('\n'.join(newlines))
