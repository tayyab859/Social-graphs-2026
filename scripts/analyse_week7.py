"""Reproduce Week 7. Python 3 + matplotlib; no trained NER or live Wikipedia crawl."""
from pathlib import Path
from collections import defaultdict,Counter
from itertools import combinations
from urllib.request import urlopen
from urllib.parse import unquote
import csv,io,re,json,zipfile,hashlib,argparse,platform
ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--output-dir',type=Path,default=ROOT/'weeks/week7');out=ap.parse_args().output_dir;out.mkdir(parents=True,exist_ok=True)
p=ROOT/'data/marvel_pages.zip'
if not p.exists():p.write_bytes(urlopen('https://sunelehmann.com/socialgraphs2026-web/data/marvel_pages.zip').read())
assert hashlib.sha256(p.read_bytes()).hexdigest()=='36023ca077053b3df5bd55630754cb514c3f9dbecbd70afcb2283e5bcc0017ee'
rows=list(csv.DictReader(io.StringIO('\n'.join(l for l in (ROOT/'data/week1_nodes.tsv').read_text().splitlines() if not l.startswith('#'))),delimiter='\t'))
ids=sorted(r['node_id'] for r in rows); urls={r['node_id']:r['url'] for r in rows}
z=zipfile.ZipFile(p);pages={unquote(Path(f).stem):z.read(f).decode() for f in z.namelist() if f.endswith('.txt') and not f.endswith('README.txt')}
assert set(ids)==set(pages) and len(ids)==303
assert hashlib.sha256((ROOT/'data/week1_nodes.tsv').read_bytes()).hexdigest()=='a10ec309ac60ea8b72bcc1a18aba801414896676dac172619def0435e585391e'
stems=defaultdict(list)
for r in rows:stems[re.sub(r'\s*\([^)]*\)$','',r['name']).casefold()].append(r['node_id'])
base={k:v[0] for k,v in stems.items() if len(v)==1}
# Deliberately small, explicit alias dictionary, checked in each character's own frozen article.
aliases={'ororo munroe':'Storm_(Marvel_Comics)','wanda django maximoff':'Scarlet_Witch','natasha romanoff':'Black_Widow_(Natasha_Romanova)'}
for a,i in aliases.items():assert a in pages[i].casefold()

def matcher(mapping):
 pat=re.compile(r'(?<!\w)(?:'+'|'.join(re.escape(k) for k in sorted(mapping,key=lambda k:(-len(k),k)))+r')(?!\w)',re.I)
 return lambda t:[(mapping[m[0].casefold()],m.start(),m.end(),m[0]) for m in pat.finditer(t)]

def run(mapping,evidence=False):
 match=matcher(mapping);S=set();A=set();sw=Counter();aw=Counter();occ={};seen=set()
 for pid,t in sorted(pages.items()):
  matches=match(t); seen.update(m[0] for m in matches)
  # Sentence heuristic: split at newline or whitespace after . ! ?; keep offsets.
  starts=[0]+[m.end() for m in re.finditer(r'(?<!Ms\.)(?<!Mr\.)(?<!Dr\.)(?<!St\.)(?<=[.!?])\s+|\n+',t)]
  ends=starts[1:]+[len(t)];units=[];j=0
  for start,end in zip(starts,ends):
   found=[]
   while j<len(matches) and matches[j][1]<end:
    
    if matches[j][2]<=end:found.append(matches[j])
    j+=1
   ns={m[0] for m in found}
   for pair in combinations(sorted(ns),2):S.add(pair);sw[pair]+=1
   if found:units.append({'start':start,'end':end,'names':sorted(ns),'matches':found})
  names=sorted({m[0] for m in matches})
  for pair in combinations(names,2):A.add(pair);aw[pair]+=1
  if evidence:occ[pid]=units
 assert S<=A and all(a!=b and a in ids and b in ids for a,b in A)
 return S,A,sw,aw,occ,seen
mapping={**base,**aliases};S,A,sw,aw,occ,seen=run(mapping,True)
noalias=run(base);nostorm=run({k:v for k,v in mapping.items() if k!='storm'})
def stats(edges):
 adj={i:set() for i in ids}
 for a,b in edges:adj[a].add(b);adj[b].add(a)
 rest=set(ids);sizes=[]
 while rest:
  stack=[rest.pop()];n=0
  while stack:
   x=stack.pop();n+=1
   for y in adj[x]&rest:rest.remove(y);stack.append(y)
  sizes.append(n)
 return {'edges':len(edges),'density':len(edges)/(303*302/2),'isolates':sum(not v for v in adj.values()),'components':len(sizes),'largest_component':max(sizes),'mean_degree':2*len(edges)/303}
# Added pairs with several supporting pages; deterministic selection for inspection.
added=A-S
ranked=sorted(added,key=lambda p:(-aw[p],p))
safe={v for k,v in base.items() if ' ' in k and '.' not in k and v!='Iron_Man_(Ultimate_Marvel_character)'}
selected=[p for p in ranked if set(p)<=safe][:2]+ranked[:1]
cases=[]
for pair in selected:
 for pid,units in occ.items():
  u=[next((u for u in units if n in u['names']),None) for n in pair]
  if all(u):
   assert u[0] is not u[1]
   cases.append({'pair':pair,'supporting_articles':aw[pair],'page':pid,'url':urls[pid],'passages':[{'start':v['start'],'end':v['end'],'text':pages[pid][v['start']:v['end']].strip()} for v in u]});break
# Two auditable ambiguity/alias examples, keeping exact source offsets.
audit=[]
for pid,needle,explanation in [('Surge_(Marvel_Comics)','storm of electrical bolts','storm refers to an electrical discharge, not necessarily the character Storm; a case-insensitive dictionary cannot tell.'),('Storm_(Marvel_Comics)','Ororo Munroe','The real-name alias is mapped to the same roster node as Storm; aliases are not additional nodes.')]:
 t=pages[pid];m=re.search(re.escape(needle),t,re.I);assert m
 start=max(t.rfind('.',0,m.start())+1,t.rfind('\n',0,m.start())+1);end=t.find('.',m.end());end=len(t) if end<0 else end+1
 audit.append({'page':pid,'url':urls[pid],'needle':needle,'start':start,'end':end,'text':t[start:end].strip(),'interpretation':explanation})
# Independently recheck each selected pair: article co-presence, and no shared sentence anywhere.
check_match=matcher(mapping)
for c in cases:
 a,b=c['pair'];assert any(a in {m[0] for m in check_match(t)} and b in {m[0] for m in check_match(t)} for t in pages.values())
 for t in pages.values():
  for unit in re.split(r'(?<!Ms\.)(?<!Mr\.)(?<!Dr\.)(?<!St\.)(?<=[.!?])\s+|\n+',t):
   ns={m[0] for m in check_match(unit)}
   assert not {a,b}<=ns
 for v in c['passages']:assert pages[c['page']][v['start']:v['end']].strip()==v['text']
# Small hand-designed test of the actual matcher/window rules.
f=matcher(mapping)
assert {m[0] for m in f('Ororo Munroe met Storm.')}=={'Storm_(Marvel_Comics)'}
assert not f('thunderstorm')
assert {m[0] for m in f('storm')}=={'Storm_(Marvel_Comics)'}
res={'nodes':303,'matched_nodes':len(seen),'sentence':stats(S),'article':stats(A),'added_edges':len(added),'jaccard':len(S)/len(A),'aliases':aliases,'excluded_collisions':{k:v for k,v in stems.items() if len(v)>1},'sensitivity':{'no_aliases':{'sentence':stats(noalias[0]),'article':stats(noalias[1])},'without_storm_surface':{'sentence':stats(nostorm[0]),'article':stats(nostorm[1]),'sentence_removed':len(S-nostorm[0]),'article_removed':len(A-nostorm[1])}},'cases':cases,'audit':audit,'inputs':{f:hashlib.sha256((ROOT/'data'/f).read_bytes()).hexdigest() for f in ['marvel_pages.zip','week1_nodes.tsv']},'python':platform.python_version()}
(out/'results.json').write_text(json.dumps(res,indent=2))
with (out/'edges.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['source','target','sentence_units','article_units','article_only'])
 for a,b in sorted(A):w.writerow([a,b,sw[(a,b)],aw[(a,b)],(a,b) not in S])
with (out/'matching_rules.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['surface','node_id','kind'])
 for k,v in sorted(mapping.items()):w.writerow([k,v,'alias' if k in aliases else 'unique_title_stem'])
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({'svg.hashsalt':'week7','font.family':'DejaVu Sans'})
fig,ax=plt.subplots(figsize=(10,4.6),facecolor='#071018');ax.set_facecolor('#071018')
ax.barh(['Same sentence','Same article'],[len(S),len(S)],color='#41d9d0',label='Present under both rules')
ax.barh(['Same article'],[len(added)],left=[len(S)],color='#ff8a5b',label='Added by article rule')
for y,n in enumerate([len(S),len(A)]):ax.text(n+len(A)*.015,y,f'{n:,}',va='center',color='white',fontweight='bold')
ax.invert_yaxis();ax.set_xlim(0,len(A)*1.15);ax.set_xlabel('Distinct undirected connections • same 303 roster nodes',color='white');ax.tick_params(colors='white');ax.spines[['top','right','left']].set_visible(False);ax.spines['bottom'].set_color('#9db0be');ax.set_title('A larger text window adds connections',loc='left',color='white',pad=20,fontweight='bold');ax.legend(loc='upper center',bbox_to_anchor=(.5,-.2),ncol=2,facecolor='#071018',labelcolor='white',edgecolor='none');fig.tight_layout()
fig.savefig(out/'window-comparison.svg',metadata={'Date':None});plt.close(fig)
print(json.dumps({k:v for k,v in res.items() if k not in ['cases','excluded_collisions','audit','inputs']},indent=2));print(json.dumps(cases,indent=2));print(json.dumps(audit,indent=2));print('Checks passed.')
