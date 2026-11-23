"""Frozen-rank node removal. Run from any directory; --output-dir isolates reruns."""
import argparse, csv, hashlib, json, random, platform
from pathlib import Path
import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(); p.add_argument('--output-dir',type=Path,default=ROOT/'weeks/week3'); args=p.parse_args(); out=args.output_dir; out.mkdir(parents=True,exist_ok=True)
def rows(path):
    return csv.reader((l for l in path.read_text().splitlines() if not l.startswith('#')),delimiter='\t',quoting=csv.QUOTE_NONE)
nodes=list(csv.DictReader((l for l in (ROOT/'data/week1_nodes.tsv').read_text().splitlines() if not l.startswith('#')),delimiter='\t',quoting=csv.QUOTE_NONE))
expected={'week1_nodes.tsv':'a10ec309ac60ea8b72bcc1a18aba801414896676dac172619def0435e585391e','week1_edges.tsv':'87be017a35e8f27a1f1bc0912ebb5723c0084e460cb2dbd0d2abd0e83fc644b2'}
for name,digest in expected.items(): assert hashlib.sha256((ROOT/'data'/name).read_bytes()).hexdigest()==digest
ids=sorted(n['node_id'] for n in nodes); edges=list(rows(ROOT/'data/week1_edges.tsv'))
D=nx.DiGraph(); D.add_nodes_from(ids); D.add_edges_from(edges)
assert len(D)==303 and D.number_of_edges()==1784 and set(D)==set(ids)
G=D.to_undirected(); G.remove_edges_from(nx.selfloop_edges(G))
assert G.number_of_edges()==1434 and len(list(nx.isolates(G)))==17
N=len(G); degree=dict(G.degree()); between=nx.betweenness_centrality(G,normalized=True,weight=None)
orders={'degree':sorted(ids,key=lambda n:(-degree[n],n)), 'betweenness':sorted(ids,key=lambda n:(-between[n],n))}
def curve(order):
    H=G.copy(); result=[len(max(nx.connected_components(H),key=len))]
    for n in order:
        H.remove_node(n); result.append(max(map(len,nx.connected_components(H)),default=0))
    assert result[-1]==0 and all(a>=b for a,b in zip(result,result[1:]))
    assert all(v<=N-k for k,v in enumerate(result))
    return result
curves={k:curve(v) for k,v in orders.items()}
random_curves=[]
for seed in range(20261123,20261323):
    order=ids.copy(); random.Random(seed).shuffle(order); random_curves.append(curve(order))
mean=[sum(c[k] for c in random_curves)/len(random_curves) for k in range(N+1)]
def quantile(v,q):
    v=sorted(v); x=(len(v)-1)*q; i=int(x); return v[i]+(v[min(i+1,len(v)-1)]-v[i])*(x-i)
lo=[quantile([c[k] for c in random_curves],.025) for k in range(N+1)]
hi=[quantile([c[k] for c in random_curves],.975) for k in range(N+1)]
ranks={key:{n:i+1 for i,n in enumerate(order)} for key,order in orders.items()}
case='Rockman_(comics)'
if case not in G: case=next(n for n in ids if n.startswith('Rockman'))
assert set(G[case])=={'Black_Widow_(Natasha_Romanova)','The_Witness_(character)'}
assert set(G['The_Witness_(character)'])=={case}
H=G.copy(); H.remove_node(case)
case_info={'id':case,'degree':degree[case],'betweenness':between[case],'degree_rank':ranks['degree'][case],'betweenness_rank':ranks['betweenness'][case],'neighbors':sorted(G[case]),'directed_links':[list(e) for e in D.edges() if case in e],'components_after_removal':sorted([sorted(c) for c in nx.connected_components(H)],key=lambda x:-len(x))}
# Independent BFS component finder, checked at selected cuts for both orders.
def bfs_lcc(removed):
    unseen=set(ids)-set(removed); largest=0
    while unseen:
        start=unseen.pop(); stack=[start]; count=1
        while stack:
            for v in G[stack.pop()]:
                if v in unseen: unseen.remove(v); stack.append(v); count+=1
        largest=max(largest,count)
    return largest
for key,order in orders.items():
    for k in [0,1,10,30,60,100,150,250,303]: assert bfs_lcc(order[:k])==curves[key][k]
assert len(G)==303 and G.number_of_edges()==1434
with (out/'removal_curves.csv').open('w') as f:
    w=csv.writer(f); w.writerow(['removed','degree_lcc','betweenness_lcc','random_mean','random_p025','random_p975'])
    w.writerows(zip(range(N+1),curves['degree'],curves['betweenness'],mean,lo,hi))
with (out/'rankings.csv').open('w') as f:
    w=csv.writer(f); w.writerow(['node_id','degree','betweenness','degree_rank','betweenness_rank']); w.writerows((n,degree[n],between[n],ranks['degree'][n],ranks['betweenness'][n]) for n in ids)
results={'nodes':N,'edges':G.number_of_edges(),'initial_lcc':curves['degree'][0],'seed_start':20261123,'random_runs':200,'random_curves':random_curves,'orders':orders,'curves':curves,'random_mean':mean,'case':case_info,'sha256':{name:hashlib.sha256((ROOT/'data'/name).read_bytes()).hexdigest() for name in ['week1_nodes.tsv','week1_edges.tsv']},'versions':{'python':platform.python_version(),'networkx':nx.__version__,'matplotlib':matplotlib.__version__}}
(out/'results.json').write_text(json.dumps(results,separators=(',',':'))+'\n')
plt.rcParams.update({'font.size':12,'svg.hashsalt':'week3-removal'})
fig,ax=plt.subplots(figsize=(11,5.5),layout='constrained'); fig.set_facecolor('#101722'); ax.set_facecolor('#101722')
ax.fill_between(range(N+1),lo,hi,color='#aeb9cb',alpha=.18,label='Random: central 95% of 200 runs')
ax.plot(mean,color='#aeb9cb',ls=':',lw=2,label='Random mean (seeded)')
ax.plot(curves['degree'],color='#58dfcf',lw=2,label='Highest degree first')
ax.plot(curves['betweenness'],color='#ffad66',ls='--',lw=2,label='Highest betweenness first')
ax.set(xlabel='Number of characters removed (fixed starting rankings)',ylabel='Characters in largest connected component',xlim=(0,N),ylim=(0,303))
ax.tick_params(colors='#e8edf5'); ax.xaxis.label.set_color('#e8edf5'); ax.yaxis.label.set_color('#e8edf5'); ax.grid(alpha=.15)
for s in ax.spines.values(): s.set_color('#657087')
ax.legend(facecolor='#101722',labelcolor='#e8edf5',fontsize=10)
fig.savefig(out/'removal-comparison.svg',metadata={'Date':None}); fig.savefig(out/'removal-comparison.png',dpi=150); plt.close(fig)
print(json.dumps({ 'initial_lcc':results['initial_lcc'],'checkpoints':{k:[curves['degree'][k],curves['betweenness'][k],mean[k]] for k in [1,10,30,60,100,150]},'case':case_info},indent=2))
