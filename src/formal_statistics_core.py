#!/usr/bin/env python3
"""Compact reproducible core for the formal Hengsha inference.

Inputs are the instrument-aware hourly table created by the main harmonisation
pipeline. The full figure-producing driver is shipped in the downloadable
formal analysis bundle; this compact module keeps the inferential contract
reviewable in GitHub.
"""
from __future__ import annotations
import argparse, csv, itertools, json, math
from pathlib import Path
import numpy as np
import statsmodels.api as sm

PAIRED = ["HSQ1", "HSQ2", "HSQ4", "HSQ5"]

def read_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        rows=list(csv.DictReader(f))
    for r in rows:
        for k,v in list(r.items()):
            if k in {"station","tide","time","campaign","hydro_instrument","wq_instrument"}: continue
            try: r[k]=float(v) if v not in ("",None) else None
            except Exception: pass
    return rows

def exact_signflip_p(d):
    d=np.asarray(d,float); obs=abs(d.mean())
    null=[abs(np.mean(d*np.asarray(s))) for s in itertools.product([-1.,1.],repeat=len(d))]
    return float(np.mean(np.asarray(null)>=obs-1e-14))

def station_boot(sp, statistic, B=20000, seed=20260818):
    rng=np.random.default_rng(seed); sts=list(sp); vals=[]
    for _ in range(B):
        q=[sp[sts[i]] for i in rng.integers(0,len(sts),len(sts))]
        vals.append(statistic(q))
    return np.quantile(vals,[.025,.5,.975])

def paired(rows, metric, kind="difference"):
    sp={}
    for st in PAIRED:
        m={}
        for tide in ("小潮","大潮"):
            x=[r[metric] for r in rows if r["station"]==st and r["tide"]==tide and r.get(metric) is not None]
            if x: m[tide]=float(np.median(x))
        if len(m)==2: sp[st]=(m["小潮"],m["大潮"])
    d=[b-a for a,b in sp.values()]
    if kind=="ratio":
        f=lambda q: math.exp(float(np.median([math.log(b/a) for a,b in q if a>0 and b>0])))
        effect=f(list(sp.values()))
    else:
        f=lambda q: float(np.median([b-a for a,b in q]))
        effect=f(list(sp.values()))
    ci=station_boot(sp,f)
    return {"n_station_pairs":len(sp),"effect":effect,"bootstrap95":[float(ci[0]),float(ci[2])],
            "exact_signflip_p":exact_signflip_p(d),"all_same_direction":bool(all(x>0 for x in d) or all(x<0 for x in d)),
            "station_pairs":sp}

def interaction(rows,outcome):
    d=[r for r in rows if r.get(outcome) is not None and r.get("sal_h_abs_delta") is not None and r.get("ssc_mean") is not None and r["station"] in ["HSQ1","HSQ2","HSQ4"]]
    y=np.array([r[outcome] for r in d],float)
    strat=np.array([r["sal_h_abs_delta"] for r in d],float)
    ssc=np.log1p(1000*np.array([r["ssc_mean"] for r in d],float))
    zs=(strat-strat.mean())/strat.std(ddof=0); zq=(ssc-ssc.mean())/ssc.std(ddof=0)
    st=sorted(set(r["station"] for r in d)); tides=sorted(set(r["tide"] for r in d))
    X=[np.ones(len(d)),zs,zq,zs*zq]
    for s in st[1:]: X.append(np.array([r["station"]==s for r in d],float))
    for t in tides[1:]: X.append(np.array([r["tide"]==t for r in d],float))
    X=np.column_stack(X); groups=np.array([r["campaign"] for r in d])
    fit=sm.OLS(y,X).fit(cov_type="cluster",cov_kwds={"groups":groups})
    j=3
    return {"outcome":outcome,"n":len(d),"n_campaigns":len(set(groups)),"beta":float(fit.params[j]),
            "se_cluster":float(fit.bse[j]),"p_cluster":float(fit.pvalues[j]),
            "ci95":[float(fit.conf_int()[j,0]),float(fit.conf_int()[j,1])],"r2":float(fit.rsquared)}

def segmented(rows, response, transform, grid_n=70, B=400, seed=20260818):
    d=[r for r in rows if r["station"] in PAIRED and r.get("speed") is not None and r.get(response) is not None]
    x=np.array([r["speed"] for r in d],float); y=np.array([transform(r[response]) for r in d],float)
    st=sorted(set(r["station"] for r in d)); td=sorted(set(r["tide"] for r in d))
    base=[np.ones(len(d)),x]
    for s in st[1:]: base.append(np.array([r["station"]==s for r in d],float))
    for t in td[1:]: base.append(np.array([r["tide"]==t for r in d],float))
    base=np.column_stack(base)
    grid=np.linspace(np.quantile(x,.1),np.quantile(x,.9),grid_n)
    def best(idx):
        bx=base[idx]; xx=x[idx]; yy=y[idx]; ans=None
        for c in grid:
            X=np.column_stack([bx,np.maximum(0,xx-c)])
            f=sm.OLS(yy,X).fit(); a=(float(np.sum(f.resid**2)),c,f)
            if ans is None or a[0]<ans[0]: ans=a
        return ans
    _,bp,fit=best(np.arange(len(d)))
    rng=np.random.default_rng(seed); bps=[]; station=np.array([r["station"] for r in d])
    for _ in range(B):
        sample=rng.choice(PAIRED,len(PAIRED),replace=True); idx=np.concatenate([np.where(station==s)[0] for s in sample])
        bps.append(best(idx)[1])
    q=np.quantile(bps,[.025,.5,.975])
    return {"n":len(d),"best_breakpoint_m_s":float(bp),"bootstrap95":[float(q[0]),float(q[2])],
            "bootstrap_median":float(q[1]),"hinge_p_naive":float(fit.pvalues[-1]),"r2":float(fit.rsquared),
            "stable_threshold":bool((q[2]-q[0])<0.15 and fit.pvalues[-1]<0.05)}

def main():
    p=argparse.ArgumentParser(); p.add_argument("--hourly",required=True); p.add_argument("--out",required=True)
    a=p.parse_args(); rows=read_csv(a.hourly)
    out={"paired":{
        "current":paired(rows,"speed","difference"),
        "profile_mean_ssc":paired(rows,"ssc_mean","ratio"),
        "bottom_ssc":paired(rows,"ssc_bottom","ratio"),
        "vertical_ssc_contrast":paired(rows,"ssc_abs_delta","ratio"),
        "salinity_stratification":paired(rows,"sal_h_abs_delta","ratio")},
        "interaction":[interaction(rows,k) for k in ["fdom_delta","chla_delta","aou_delta"]],
        "transition":{
            "ssc":segmented(rows,"ssc_mean",lambda x:math.log10(max(x,0)+.001)),
            "stratification":segmented(rows,"sal_h_abs_delta",lambda x:math.log1p(max(x,0)))}}
    Path(a.out).write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=="__main__": main()
