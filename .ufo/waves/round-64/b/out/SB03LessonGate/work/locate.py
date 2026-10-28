import sys, re, json
def norm(s): return re.sub(r'\s+',' ',s).strip()
def locate(txtfile, quote):
    lines=[]; 
    for raw in open(txtfile,encoding='utf-8'):
        n,_,body=raw.rstrip('\n').partition(': ')
        lines.append((int(n),body))
    hay=''; spans=[]
    for n,b in lines:
        start=len(hay); hay+=b+' '; spans.append((start,len(hay),n))
    q=norm(quote)
    i=hay.find(q)
    if i<0: return None
    j=i+len(q)
    def line_of(pos):
        for s,e,n in spans:
            if s<=pos<e: return n
    return line_of(i), line_of(j-1), len(q.split())
quotes=json.load(open(sys.argv[1]))
for row in quotes:
    r=locate(row['file'],row['quote'])
    print(row['id'], row['file'], 'FOUND lines %s-%s words=%d' % r if r else 'NOT FOUND', '|', row['quote'][:60])
