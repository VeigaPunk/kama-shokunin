import sys, html, re
from html.parser import HTMLParser
class P(HTMLParser):
    def __init__(s):
        super().__init__(); s.out=[]; s.skip=0
    def handle_starttag(s,t,a):
        if t in('script','style'): s.skip+=1
        if t in('br','p','div','pre','li','tr'): s.out.append('\n')
    def handle_endtag(s,t):
        if t in('script','style'): s.skip-=1
    def handle_data(s,d):
        if not s.skip: s.out.append(d)
p=P(); p.feed(open(sys.argv[1],encoding='utf-8',errors='replace').read())
txt=html.unescape(''.join(p.out))
lines=[re.sub(r'[ \t\xa0]+',' ',l).strip() for l in txt.split('\n')]
lines=[l for l in lines if l]
for i,l in enumerate(lines,1): print(f"{i}: {l}")
