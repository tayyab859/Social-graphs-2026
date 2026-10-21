"""Rebuild Week 6 data. Run with PYTHONHASHSEED=0; see requirements.txt."""
from pathlib import Path
import csv,io,json,re,zipfile,hashlib,platform
import importlib.metadata
from urllib.parse import unquote
from urllib.request import urlopen
import numpy as np
import networkx as nx
from gensim.models import Word2Vec
from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS
from sklearn.metrics.pairwise import cosine_similarity
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'data'; DATA.mkdir(exist_ok=True)
for filename in ['week1_nodes.tsv','week1_edges.tsv','marvel_pages.zip']:
 p=DATA/filename
 if not p.exists(): p.write_bytes(urlopen('https://sunelehmann.com/socialgraphs2026-web/data/'+filename).read())
rows=list(csv.DictReader(io.StringIO('\n'.join(x for x in (DATA/'week1_nodes.tsv').read_text().splitlines() if not x.startswith('#'))),delimiter='\t'))
ids=[r['node_id'] for r in rows]; n=len(ids)
z=zipfile.ZipFile(DATA/'marvel_pages.zip')
pages={unquote(Path(f).stem):z.read(f).decode() for f in z.namelist() if f.endswith('.txt') and not f.endswith('README.txt')}
assert set(pages)==set(ids) and n==303
edges=[tuple(l.split('\t')) for l in (DATA/'week1_edges.tsv').read_text().splitlines() if l and not l.startswith('#')]
G=nx.Graph();G.add_nodes_from(ids);G.add_edges_from(edges); assert len(edges)==1784
# Same vocabulary/preprocessing in the two document representations; names retained.
tokenize=lambda t:re.findall(r'[a-z]{2,}',t.lower())
sentences=[tokenize(s) for i in ids for s in re.split(r'(?<=[.!?])\s+',pages[i])];sentences=[s for s in sentences if s]
vec=TfidfVectorizer(tokenizer=tokenize,token_pattern=None,lowercase=False,stop_words=sorted(ENGLISH_STOP_WORDS),min_df=2,max_df=.8)
X=vec.fit_transform([pages[i] for i in ids]); vocab=vec.get_feature_names_out();T=cosine_similarity(X)
def embed(seed,window):
 model=Word2Vec(sentences,vector_size=100,window=window,min_count=5,sg=1,negative=5,epochs=20,seed=seed,workers=1)
 W=np.array([model.wv[t] if t in model.wv else np.zeros(100) for t in vocab]); D=np.asarray(X@W)
 return cosine_similarity(D),float(X[:,[t in model.wv for t in vocab]].sum()/X.sum()),model
E,coverage,model=embed(0,5);Eseed,_,_=embed(1,5);Ewide,_,_=embed(0,10)
def top(M,i,k=5):return [int(j) for j in np.argsort(-M[i],kind='stable') if j!=i][:k]
def agreement(M):return float(np.mean([sum(G.has_edge(ids[i],ids[j]) for j in top(M,i)) for i in range(n)]))
def overlap(A,B):return [len(set(top(A,i))&set(top(B,i))) for i in range(n)]
metrics={'nodes':n,'directed_edges':len(edges),'undirected_edges':G.number_of_edges(),'tfidf_linked_top5':agreement(T),'embedding_linked_top5':agreement(E),'random_expected_top5':5*nx.density(G),'mean_shared_top5':float(np.mean(overlap(T,E))),'seed_shared_top5':float(np.mean(overlap(E,Eseed))),'window_shared_top5':float(np.mean(overlap(E,Ewide))),'embedding_weight_coverage':coverage,'vocabulary':len(vocab),'tokens':sum(map(len,sentences))}
result=[]
for i,r in enumerate(rows):
 def matches(M):
  return [{'index':j,'score':round(float(M[i,j]),5),'linked':G.has_edge(ids[i],ids[j])} for j in top(M,i)]
 result.append({'id':ids[i],'name':ids[i].replace('_',' '),'url':r['url'],'tfidf':matches(T),'embedding':matches(E),'network':[ids.index(j) for j in sorted(G[ids[i]])],'overlap':overlap(T,E)[i]})
cases=[]
for target in ['Storm_(Marvel_Comics)','Doctor_Strange','Wolverine_(character)','Black_Widow_(Natasha_Romanova)','Spider-Man']:
 if target not in ids:continue
 i=ids.index(target)
 for method,M in [('tfidf',T),('embedding',E)]:
  j=top(M,i)[0]; contributions=X[i].multiply(X[j]).toarray()[0]; terms=[str(vocab[k]) for k in np.argsort(-contributions)[:6] if contributions[k]>0]
  def excerpts(idx):
   ss=re.split(r'(?<=[.!?])\s+',pages[ids[idx]])
   return sorted(ss,key=lambda s:sum(t in tokenize(s) for t in terms),reverse=True)[:2]
  cases.append({'target':ids[i],'match':ids[j],'method':method,'score':float(M[i,j]),'shared_terms':terms,'excerpts_target':excerpts(i),'excerpts_match':excerpts(j)})
output={'metrics':metrics,'characters':result,'cases':cases,'provenance':{f:hashlib.sha256((DATA/f).read_bytes()).hexdigest() for f in ['week1_nodes.tsv','week1_edges.tsv','marvel_pages.zip']},'versions':{'python':platform.python_version(),'numpy':np.__version__,'networkx':nx.__version__, **{n:importlib.metadata.version(n) for n in ['gensim','scikit-learn','scipy']}}}
(ROOT/'weeks/week6/results.json').write_text(json.dumps(output,indent=2))
(DATA/'week6_audit.json').write_text(json.dumps(cases,indent=2))
print(json.dumps(metrics,indent=2)); print(json.dumps(cases,indent=2))
# Independent tiny mathematical checks and output invariants.
a=np.array([1.,1.]);b=np.array([2.,2.]);assert abs(a@b/(np.linalg.norm(a)*np.linalg.norm(b))-1)<1e-12
for M in [T,E]:
 assert np.isfinite(M).all() and np.allclose(M,M.T) and np.allclose(np.diag(M),1)
 assert all(i not in top(M,i) and len(set(top(M,i)))==5 for i in range(n))
print('Validation passed: corpus identity, edge count, cosine symmetry, diagonal, finite values, unique non-self matches.')
