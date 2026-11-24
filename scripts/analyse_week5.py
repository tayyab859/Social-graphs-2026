#!/usr/bin/env python3
"""Controlled ASCII-hyphen tokenization comparison; run from any directory."""
import argparse, collections, csv, hashlib, json, re, sys, zipfile
from pathlib import Path
from urllib.parse import unquote
from urllib.request import urlretrieve
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT = Path(__file__).resolve().parents[1]
URL = 'https://sunelehmann.com/socialgraphs2026-web/data/marvel_pages.zip'
SHA = '36023ca077053b3df5bd55630754cb514c3f9dbecbd70afcb2283e5bcc0017ee'
# Unicode alphabetic runs, with ASCII hyphens internal only in KEEP.
KEEP = re.compile(r'[^\W\d_]+(?:-[^\W\d_]+)*')
SPLIT = re.compile(r'[^\W\d_]+')
def tokens(text, keep):
    return [m.group().lower() for m in (KEEP if keep else SPLIT).finditer(text)]
def stats(c):
    h = sum(n == 1 for n in c.values())
    return dict(tokens=sum(c.values()), types=len(c), hapax=h, hapax_share=h/len(c))
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output-dir',type=Path,default=ROOT/'weeks/week5');ap.add_argument('--archive',type=Path,default=ROOT/'data/marvel_pages.zip');args=ap.parse_args()
    if not args.archive.exists():
        args.archive.parent.mkdir(parents=True,exist_ok=True);urlretrieve(URL,args.archive)
    digest=hashlib.sha256(args.archive.read_bytes()).hexdigest()
    assert digest==SHA, 'Archive changed: inspect and update the analysis deliberately.'
    with zipfile.ZipFile(args.archive) as z:
        pages={unquote(n.split('/')[-1][:-4]):z.read(n).decode('utf-8') for n in z.namelist() if n.endswith('.txt') and 'README' not in n}
    with (ROOT/'data/week1_nodes.tsv').open() as f:
        nodes={r['node_id']:r for r in csv.DictReader((l for l in f if not l.startswith('#')),delimiter='\t',quoting=csv.QUOTE_NONE)}
    assert len(pages)==303 and set(pages)==set(nodes)
    a,b=collections.Counter(),collections.Counter(); perdoc=[]
    for node,text in sorted(pages.items()):
        ka=tokens(text,True);kb=tokens(text,False)
        # Independent transformation invariant on every document's exact sequence.
        assert [part for t in ka for part in t.split('-')]==kb
        ca,cb=collections.Counter(ka),collections.Counter(kb);a.update(ca);b.update(cb)
        perdoc.append({'node_id':node,**{'keep_'+k:v for k,v in stats(ca).items()},**{'split_'+k:v for k,v in stats(cb).items()}})
    compounds={t:n for t,n in a.items() if '-' in t}
    extra=sum(n*t.count('-') for t,n in compounds.items())
    assert sum(b.values())-sum(a.values())==extra
    rebuilt=collections.Counter()
    for t,n in a.items():
        for part in t.split('-'): rebuilt[part]+=n
    assert rebuilt==b
    assert tokens("Spider-Man's X-Men — déjà-vu 2099",True)==['spider-man','s','x-men','déjà-vu']
    assert tokens("Spider-Man's X-Men — déjà-vu 2099",False)==['spider','man','s','x','men','déjà','vu']
    out=args.output_dir;out.mkdir(parents=True,exist_ok=True)
    for name,c in [('keep',a),('split',b)]:
        with (out/f'{name}_frequencies.csv').open('w') as f:
            w=csv.writer(f);w.writerow(['rank','type','frequency'])
            w.writerows((i,t,n) for i,(t,n) in enumerate(sorted(c.items(),key=lambda x:(-x[1],x[0])),1))
    with (out/'document_counts.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(perdoc[0]));w.writeheader();w.writerows(perdoc)
    with (out/'hyphen_audit.csv').open('w') as f:
        w=csv.writer(f);w.writerow(['kept_type','keep_count','split_pieces','split_corpus_counts'])
        for t,n in sorted(compounds.items(),key=lambda x:(-x[1],x[0])):
            w.writerow([t,n,' | '.join(t.split('-')),' | '.join(str(b[p]) for p in t.split('-'))])
    # Cases selected transparently: common names and one hapax whose parts all recur.
    rare=sorted(t for t,n in compounds.items() if n==1 and len(t)<26 and all(b[p]>1 for p in t.split('-')))
    selected=['spider-man','x-men',rare[0]]
    examples=[]
    for target in selected:
        for node,text in sorted(pages.items()):
            match=next((m for m in KEEP.finditer(text) if m.group().lower()==target),None)
            if match:
                start=max(0,match.start()-65);end=min(len(text),match.end()+85)
                examples.append(dict(type=target,node_id=node,url=nodes[node]['url'],excerpt=text[start:end],char_start=start,char_end=end,keep_count=a[target],split_count=b[target],parts={p:{'keep':a[p],'split':b[p]} for p in target.split('-')}));break
    lost_hapax=sorted(t for t,n in a.items() if n==1 and b[t]!=1)
    gained_hapax=sorted(t for t,n in b.items() if n==1 and a[t]!=1)
    result=dict(source=URL,sha256=digest,snapshot='2026-08-26',documents=len(pages),characters=sum(map(len,pages.values())),rules={'keep_regex':KEEP.pattern,'split_regex':SPLIT.pattern,'normalization':'lower() after regex extraction; no stopword removal or lemmatization; digits, underscores, apostrophes and other punctuation are boundaries; only ASCII U+002D internal hyphens are retained by keep'},keep=stats(a),split=stats(b),hyphen_types=len(compounds),hyphen_tokens=sum(compounds.values()),extra_split_tokens=extra,lost_hapax_count=len(lost_hapax),gained_hapax_count=len(gained_hapax),lost_hapax=lost_hapax,gained_hapax=gained_hapax,examples=examples,versions={'python':sys.version.split()[0],'matplotlib':matplotlib.__version__})
    assert result['split']['hapax']==result['keep']['hapax']-len(lost_hapax)+len(gained_hapax)
    (out/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    plt.rcParams.update({'svg.hashsalt':'week5-hyphens','font.family':'DejaVu Sans','font.size':12})
    fig,ax=plt.subplots(figsize=(10,6),facecolor='#0b1020');ax.set_facecolor('#0b1020')
    for c,color,label,style in [(a,'#68e5ce','Keep internal hyphens','-'),(b,'#ffbf69','Split at hyphens','--')]:
        vals=sorted(c.values(),reverse=True);ax.loglog(range(1,len(vals)+1),vals,color=color,lw=2,label=label,ls=style)
    ax.set(xlabel='Frequency rank (1 = most frequent type) · log scale',ylabel='Occurrences in all 303 articles · log scale',title='Same text. Different word boundaries.')
    ax.tick_params(colors='#cbd5e1');ax.xaxis.label.set_color('#e2e8f0');ax.yaxis.label.set_color('#e2e8f0');ax.title.set_color('#ffffff')
    for sp in ax.spines.values():sp.set_color('#475569')
    ax.grid(which='major',alpha=.18,color='white');ax.legend(facecolor='#182238',edgecolor='#475569',labelcolor='white');ax.set_ylim(.8,max(max(a.values()),max(b.values()))*1.6)
    fig.text(.12,.015,'Frequency 1 is the hapax tail. Curves overlap substantially; no Zipf fit or significance claim.',color='#cbd5e1',fontsize=10)
    fig.tight_layout(rect=(0,.04,1,1));fig.savefig(out/'rank-frequency.svg',metadata={'Date':None});fig.savefig(out/'rank-frequency.png',dpi=160);plt.close(fig)
    print(json.dumps({k:v for k,v in result.items() if k not in ['lost_hapax','gained_hapax']},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
