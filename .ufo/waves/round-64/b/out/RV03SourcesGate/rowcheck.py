import re,sys
rows=[l for l in open(sys.argv[1]) if re.match(r'^\| S5(29|3[0-2]) \|',l)]
for r in rows:
    cells=[c.strip() for c in r.strip().strip('|').split('|')]
    print(cells[0], len(cells), 'anchor-has-section:', bool(re.search(r'§\w+',cells[5])), 'rev:', bool(re.search(r'20\d\d-\d\d-\d\d|\d+\.\d+',cells[5])), 'pipe-in-cell:', any('|' in c for c in cells) )
