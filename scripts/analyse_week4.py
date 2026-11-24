#!/usr/bin/env python3
"""Week 4: repeat weighted/unweighted Louvain on one frozen philosopher graph.
Run from any directory; --output-dir permits an isolated reproducibility check.
"""
from pathlib import Path
import argparse, collections, csv, hashlib, itertools, json, platform
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.optimize import linear_sum_assignment
from sklearn.metrics import normalized_mutual_info_score
import sklearn
ROOT=Path(__file__).resolve().parents[1]
EXPECTED={'week4_philosophers_edges.tsv':'ddc0cac2c763e6ade9acb336ffb391af43952a0c0fc75c4c370bd593b16e438b','week4_philosophers_nodes.tsv':'c5bd92ba8319fed505cc1fa67f02fb3c62691595175c55abed2144140cfaac45'}
def stats(x):
 x=np.array(x);return dict(n=len(x),mean=float(x.mean()),median=float(np.median(x)),min=float(x.min()),max=float(x.max()),sample_sd=float(x.std(ddof=1)))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output-dir',type=Path,default=ROOT/'weeks/week4');args=ap.parse_args();out=args.output_dir;out.mkdir(parents=True,exist_ok=True)
 for file,h in EXPECTED.items():assert hashlib.sha256((ROOT/'data/week4'/file).read_bytes()).hexdigest()==h, 'Changed official data: '+file
 nd=pd.read_csv(ROOT/'data/week4/week4_philosophers_nodes.tsv',sep='\t',comment='#',quoting=3).fillna('')
 ed=pd.read_csv(ROOT/'data/week4/week4_philosophers_edges.tsv',sep='\t',comment='#')
 G=nx.Graph();G.add_nodes_from(nd.node_id)
 directed={}
 for s,t,w in ed.itertuples(index=False):
  assert s in G and t in G and s!=t and int(w)==w and w>0
  assert (s,t) not in directed
  directed[s,t]=int(w)
  if G.has_edge(s,t):G[s][t]['weight']+=int(w)
  else:G.add_edge(s,t,weight=int(w))
 assert len(G)==1444 and G.number_of_edges()==9140
 components=sorted(nx.connected_components(G),key=len,reverse=True)
 G=G.subgraph(components[0]).copy();order=list(G);index={u:i for i,u in enumerate(order)}
 assert len(G)==1374 and G.number_of_edges()==9139
 for u,v,d in G.edges(data=True):assert d['weight']==directed.get((u,v),0)+directed.get((v,u),0)
 assert sum(dict(G.degree(weight='weight')).values())==2*G.size(weight='weight')
 meta=nd.set_index('node_id');names=meta.name.to_dict();seeds=list(range(20));runs={};partitions={}
 for model,weight in [('unweighted',None),('weighted','weight')]:
  runs[model]=[];partitions[model]=[]
  for seed in seeds:
   part=nx.community.louvain_communities(G,weight=weight,resolution=1,seed=seed)
   part=sorted(part,key=lambda c:(-len(c),min(c))) # deterministic ids; not historical labels
   lookup={u:i for i,c in enumerate(part) for u in c}
   assert len(lookup)==len(G) and sum(map(len,part))==len(G)
   label=[lookup[u] for u in order]
   runs[model].append(dict(seed=seed,communities=len(part),Q=nx.community.modularity(G,part,weight=weight,resolution=1),labels=label));partitions[model].append(part)
 rows=[];matrix=[]
 for a in range(20):
  matrix.append([])
  for b in range(20):
   val=normalized_mutual_info_score(runs['unweighted'][a]['labels'],runs['weighted'][b]['labels'],average_method='arithmetic');matrix[-1].append(val)
   rows.append(dict(comparison='between_models',seed_a=a,seed_b=b,NMI=val))
 within={}
 for model in runs:
  vals=[]
  for a,b in itertools.combinations(range(20),2):
   v=normalized_mutual_info_score(runs[model][a]['labels'],runs[model][b]['labels'],average_method='arithmetic');vals.append(v);rows.append(dict(comparison='within_'+model,seed_a=a,seed_b=b,NMI=v))
  within[model]=stats(vals)
 summary={'within':within,'between_all_400':stats(np.array(matrix).ravel()),'paired_20':stats(np.diag(matrix)),'reference_seed0':matrix[0][0]}
 U,W=partitions['unweighted'][0],partitions['weighted'][0]
 ulabels=np.array(runs['unweighted'][0]['labels']);wlabels=np.array(runs['weighted'][0]['labels'])
 overlap=np.array([[len(c&d) for d in W] for c in U]);assert overlap.sum()==len(G)
 rr,cc=linear_sum_assignment(-overlap);alignment=dict(zip(cc.tolist(),rr.tolist()))
 def desc(part):
  return [dict(id=i,size=len(c),label=names[sorted(c,key=lambda u:(-G.degree(u),u))[0]],top5=[names[u] for u in sorted(c,key=lambda u:(-G.degree(u),u))[:5]]) for i,c in enumerate(part)]
 # Expose the most highly connected label-aligned mismatches for transparent case selection.
 moved=[u for u in G if alignment.get(int(wlabels[index[u]]),-1)!=int(ulabels[index[u]])]
 moved.sort(key=lambda u:(-G.degree(u),u));candidates=[]
 for u in moved[:30]:
  i=index[u];peers=[]
  for seed in seeds:
   a=partitions['unweighted'][seed][runs['unweighted'][seed]['labels'][i]]-{u};b=partitions['weighted'][seed][runs['weighted'][seed]['labels'][i]]-{u};peers.append(len(a&b)/len(a|b))
  candidates.append(dict(id=u,name=names[u],degree=G.degree(u),strength=G.degree(u,weight='weight'),unweighted=int(ulabels[i]),weighted=int(wlabels[i]),peer_jaccard_mean=float(np.mean(peers)),strongest=[dict(id=v,name=names[v],weight=G[u][v]['weight'],outgoing=directed.get((u,v),0),incoming=directed.get((v,u),0),unweighted=int(ulabels[index[v]]),weighted=int(wlabels[index[v]])) for v in sorted(G[u],key=lambda v:(-G[u][v]['weight'],v))[:10]]))
 # Select a descriptive case deterministically: strongest repeated edge among the
 # 30 highest-degree seed-0 mismatches. This is exploratory, not a representative sample.
 chosen=max(candidates,key=lambda c:c['strongest'][0]['weight']);case_id=chosen['id'];ci=index[case_id]
 incident=[]
 for v in sorted(G[case_id],key=lambda v:(-G[case_id][v]['weight'],v)):
  vi=index[v]
  incident.append(dict(neighbor_id=v,neighbor=names[v],outgoing=directed.get((case_id,v),0),incoming=directed.get((v,case_id),0),weight=G[case_id][v]['weight'],unweighted_seed0=int(ulabels[vi]),weighted_seed0=int(wlabels[vi]),same_unweighted_runs=sum(x['labels'][ci]==x['labels'][vi] for x in runs['unweighted']),same_weighted_runs=sum(x['labels'][ci]==x['labels'][vi] for x in runs['weighted'])))
 assert len(incident)==G.degree(case_id) and sum(x['weight'] for x in incident)==G.degree(case_id,weight='weight')
 case={**chosen,'selection':'Largest repeated edge among the 30 highest-degree reference mismatches','url':meta.loc[case_id,'url'],'incident_links':incident}
 pd.DataFrame(incident).to_csv(out/'case_links.csv',index=False)
 # Independent information-theoretic NMI calculation from the contingency counts.
 probability=overlap/overlap.sum();px=probability.sum(axis=1);py=probability.sum(axis=0)
 mi=sum(probability[i,j]*np.log(probability[i,j]/(px[i]*py[j])) for i in range(len(U)) for j in range(len(W)) if probability[i,j]>0)
 independent_nmi=2*mi/(-sum(px*np.log(px))-sum(py*np.log(py)))
 assert np.isclose(independent_nmi,matrix[0][0],atol=1e-12)
 result={'question':'Do repeated Wikipedia links change which communities philosophers belong to?','data_source':'https://sunelehmann.com/socialgraphs2026-web/data/','snapshot':'2026-09-15','sha256':EXPECTED,'graph':dict(original_nodes=len(nd),directed_edges=len(ed),full_undirected_edges=9140,nodes=len(G),edges=G.number_of_edges(),total_weight=int(G.size(weight='weight')),excluded_nodes=1444-len(G),excluded_edges=1,components_sizes=[len(c) for c in components],weight_one_edges=sum(d['weight']==1 for _,_,d in G.edges(data=True))),'parameters':dict(seeds=seeds,resolution=1,nmi_average_method='arithmetic',graph_order='official file insertion order',case_selection='Highest-degree seed-0 mismatches after maximum-overlap label matching; article states final inspected case'),'software':dict(python=platform.python_version(),networkx=nx.__version__,numpy=np.__version__,pandas=pd.__version__,sklearn=sklearn.__version__,matplotlib=matplotlib.__version__),'node_ids':order,'runs':runs,'nmi':summary,'cross_nmi_matrix':matrix,'reference':dict(seed=0,unweighted=desc(U),weighted=desc(W),overlap=overlap.tolist(),aligned_overlap=int(overlap[rr,cc].sum()),alignment_weighted_to_unweighted=alignment),'case_candidates':candidates,'case':case,'checks':{'independent_reference_nmi':float(independent_nmi),'weight_sums_validated':True,'partition_coverage_validated':True}}
 (out/'results.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
 pd.DataFrame(rows).to_csv(out/'seed_agreement.csv',index=False)
 pd.DataFrame(overlap,index=[f'U{i}' for i in range(len(U))],columns=[f'W{i}' for i in range(len(W))]).to_csv(out/'community_overlap.csv')
 pd.DataFrame([dict(node_id=u,name=names[u],unweighted_seed0=int(ulabels[i]),weighted_seed0=int(wlabels[i])) for i,u in enumerate(order)]).to_csv(out/'memberships.csv',index=False)
 # One overlap figure. Show counts, not percentages; ids and named anchors avoid implying truth.
 plt.rcParams.update({'svg.fonttype':'none','svg.hashsalt':'week4-fixed','font.family':'DejaVu Sans','font.size':11})
 f,ax=plt.subplots(figsize=(12,9),facecolor='#0d1a25');ax.set_facecolor('#0d1a25')
 from matplotlib.colors import LinearSegmentedColormap
 cmap=LinearSegmentedColormap.from_list('mirror',['#122432','#207782','#41d9d0'])
 im=ax.imshow(overlap,cmap=cmap,vmin=0,vmax=overlap.max(),aspect='auto')
 ax.set_yticks(range(len(U)),[f"U{i} · {d['label']} ({d['size']})" for i,d in enumerate(desc(U))],color='#eef6fb')
 ax.set_xticks(range(len(W)),[f"W{i} · {d['label']} ({d['size']})" for i,d in enumerate(desc(W))],rotation=45,ha='right',color='#eef6fb')
 for i in range(len(U)):
  for j in range(len(W)):
   if overlap[i,j]:ax.text(j,i,str(overlap[i,j]),ha='center',va='center',color='#071018' if overlap[i,j]>overlap.max()*.6 else '#eef6fb',fontsize=11)
 ax.set_xlabel('Weighted Louvain communities · number in brackets = group size',color='#eef6fb',labelpad=18);ax.set_ylabel('Unweighted Louvain communities',color='#eef6fb',labelpad=14)
 ax.tick_params(length=0);[sp.set_visible(False) for sp in ax.spines.values()]
 cb=f.colorbar(im,ax=ax,pad=.025,shrink=.65);cb.set_label('Philosophers shared by the two groups',color='#eef6fb');cb.ax.tick_params(colors='#eef6fb');cb.outline.set_visible(False)
 f.suptitle('Repeated links redraw some community boundaries',x=.06,ha='left',color='#eef6fb',fontsize=20,y=.98)
 f.text(.06,.93,f'Same 1,374 nodes and 9,139 edges · seed 0 for both · NMI {matrix[0][0]:.3f}',color='#9db0be',fontsize=12)
 f.subplots_adjust(left=.30,bottom=.32,right=.9,top=.87)
 f.text(.06,.025,'Each cell counts shared members. Blank = zero. Names identify high-degree anchors, not verified schools.\nWeights sum repeated links in both directions. Other seeds are reported in the article.',color='#9db0be',fontsize=10)
 f.savefig(out/'community-overlap.svg',metadata={'Date':None});f.savefig(out/'community-overlap.png',dpi=150,metadata={'Software':'Week 4 analysis'});plt.close(f)
 print(json.dumps({'graph':result['graph'],'nmi':summary,'communities':{m:[x['communities'] for x in runs[m]] for m in runs},'candidates':candidates[:8]},indent=2,ensure_ascii=False))
if __name__=='__main__':main()
