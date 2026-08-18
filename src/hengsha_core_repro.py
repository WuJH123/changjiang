#!/usr/bin/env python3
"""Reproduce the core Hengsha Shoal data audit and spring-neap contrasts.

Uses only Python's standard library plus numpy/scipy. It reads .xlsx files as
OpenXML ZIPs, avoiding Excel/openpyxl/pandas dependencies.
"""
from __future__ import annotations
import argparse, csv, datetime as dt, math, re, tempfile, zipfile
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path
import numpy as np
from scipy import stats

NS={'a':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
PROFILE={'03_':'ssc_g_l','07_':'salinity_psu'}
DATE_IDS={14,15,16,17,18,19,20,21,22,27,30,36,45,46,47,50,57}
CACHE={}

def colnum(s):
    n=0
    for c in s:
        if c.isalpha(): n=n*26+ord(c.upper())-64
    return n

def xldt(x,date1904=False):
    return (dt.datetime(1904,1,1) if date1904 else dt.datetime(1899,12,30))+dt.timedelta(days=float(x))

def info(path:Path):
    k=str(path.resolve())
    if k in CACHE:return CACHE[k]
    z=zipfile.ZipFile(path); shared=[]
    if 'xl/sharedStrings.xml' in z.namelist():
        r=ET.fromstring(z.read('xl/sharedStrings.xml'))
        for si in r.findall('a:si',NS):
            shared.append(''.join(t.text or '' for t in si.iter('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t')))
    wb=ET.fromstring(z.read('xl/workbook.xml')); d1904=False
    p=wb.find('a:workbookPr',NS)
    if p is not None and p.attrib.get('date1904') in ('1','true','True'): d1904=True
    rr=ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
    rel={x.attrib['Id']:x.attrib['Target'] for x in rr}
    sheets=[]
    for sh in wb.find('a:sheets',NS):
        rid=sh.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']
        t=rel[rid]; t=('xl/'+t.lstrip('/')) if not t.startswith('/') else t.lstrip('/')
        sheets.append((sh.attrib['name'],t))
    date_styles=set()
    if 'xl/styles.xml' in z.namelist():
        sr=ET.fromstring(z.read('xl/styles.xml')); nf={}
        nfs=sr.find('a:numFmts',NS)
        if nfs is not None:
            for x in nfs: nf[int(x.attrib['numFmtId'])]=x.attrib.get('formatCode','')
        xfs=sr.find('a:cellXfs',NS)
        if xfs is not None:
            for i,x in enumerate(xfs):
                nid=int(x.attrib.get('numFmtId','0')); code=nf.get(nid,'').lower()
                if nid in DATE_IDS or any(q in code for q in ('yy','dd','hh','ss')): date_styles.add(i)
    CACHE[k]=(z,shared,sheets,date_styles,d1904); return CACHE[k]

def names(path): return [x[0] for x in info(path)[2]]

def sheet(path,name):
    z,shared,sheets,date_styles,d1904=info(path); target=dict(sheets)[name]
    root=ET.fromstring(z.read(target)); cells={}; mr=mc=0
    for row in root.findall('.//a:sheetData/a:row',NS):
        r=int(row.attrib.get('r','0'))
        for c in row.findall('a:c',NS):
            m=re.match(r'([A-Z]+)(\d+)',c.attrib.get('r',''))
            if not m: continue
            j=colnum(m.group(1)); typ=c.attrib.get('t'); sty=int(c.attrib.get('s','0')); v=c.find('a:v',NS); val=None
            if typ=='inlineStr':
                x=c.find('a:is',NS); val=''.join(t.text or '' for t in x.iter('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t')) if x is not None else None
            elif v is not None:
                raw=v.text
                if typ=='s': val=shared[int(raw)]
                elif typ=='b': val=raw=='1'
                elif typ=='str': val=raw
                else:
                    try:
                        q=float(raw); val=xldt(q,d1904) if sty in date_styles and q>1 else q
                    except: val=raw
            cells[(r,j)]=val; mr=max(mr,r); mc=max(mc,j)
    return [[cells.get((r,j)) for j in range(1,mc+1)] for r in range(1,mr+1)]

def parse_station(name):
    m=re.search(r'(HSQ\d+)(小潮|大潮)',name)
    return (m.group(1),m.group(2)) if m else None

def depth(h):
    if not isinstance(h,str): return None
    if h.strip() in ('表层','表层流速'): return 0.0
    if h.strip() in ('底层','底层流速'): return 1.0
    m=re.search(r'(0(?:\.\d+)?)层',h); return float(m.group(1)) if m else None

def fnum(x):
    return float(x) if isinstance(x,(int,float)) and math.isfinite(float(x)) else None

def writecsv(path,rows,fields):
    with open(path,'w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

def hour(t): return t.replace(minute=0,second=0,microsecond=0)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--zip',required=True);ap.add_argument('--out',default='results_core');a=ap.parse_args()
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    td=tempfile.TemporaryDirectory(); root=Path(td.name)
    with zipfile.ZipFile(a.zip) as z:z.extractall(root)
    files=sorted(root.rglob('*.xlsx')); fmap={p.name:p for p in files}

    inventory=[]
    for p in files: inventory.append({'file':p.name,'n_sheets':len(names(p)),'sheets':' | '.join(names(p))})
    writecsv(out/'data_inventory.csv',inventory,['file','n_sheets','sheets'])

    prof=[]; coverage=defaultdict(lambda:{'times':set(),'n':0,'tides':set()})
    for prefix,var in PROFILE.items():
        p=next((x for x in files if x.name.startswith(prefix)),None)
        if not p: continue
        for sn in names(p):
            st=parse_station(sn)
            if not st:continue
            station,tide=st; r=sheet(p,sn)
            if not r:continue
            dcols=[(j,depth(h)) for j,h in enumerate(r[0]) if depth(h) is not None]
            for row in r[1:]:
                if not row or not isinstance(row[0],dt.datetime):continue
                for j,zf in dcols:
                    if j>=len(row):continue
                    v=fnum(row[j])
                    if v is None:continue
                    prof.append({'station':station,'tide':tide,'time':row[0],'z':zf,'variable':var,'value':v})
                    k=(station,var); coverage[k]['n']+=1;coverage[k]['times'].add(row[0]);coverage[k]['tides'].add(tide)

    vp=next(x for x in files if x.name.startswith('04_')); vh=defaultdict(list)
    stations=set()
    for sn in names(vp):
        st=parse_station(sn)
        if not st:continue
        station,tide=st;stations.add(station);r=sheet(vp,sn)
        if not r:continue
        hdr=r[0]; idx=hdr.index('平均流速') if '平均流速' in hdr else None
        if idx is None:continue
        for row in r[1:]:
            if row and isinstance(row[0],dt.datetime) and idx<len(row):
                v=fnum(row[idx])
                if v is not None:vh[(station,tide,hour(row[0]))].append(v)
    vel={k:float(np.median(v)) for k,v in vh.items()}

    by=defaultdict(dict)
    for r in prof: by[(r['station'],r['tide'],hour(r['time']),r['variable'])][r['z']]=r['value']
    metrics=defaultdict(dict)
    for (s,t,h,v),d in by.items():
        zs=sorted(d); vals=[d[z] for z in zs]
        metrics[(s,t,h)][v+'_mean']=float(np.mean(vals));metrics[(s,t,h)][v+'_surface']=d[zs[0]];metrics[(s,t,h)][v+'_bottom']=d[zs[-1]]
        metrics[(s,t,h)][v+'_bottom_minus_surface']=d[zs[-1]]-d[zs[0]]
    rows=[]
    for (s,t,h),m in metrics.items():
        q={'station':s,'tide':t,'time':h,'current_speed_m_s':vel.get((s,t,h))};q.update(m);rows.append(q)

    paired=[]
    definitions=[('current_speed_m_s','current_speed_m_s'),('salinity_psu_bottom_minus_surface','salinity_psu_bottom_minus_surface'),('ssc_g_l_mean','ssc_g_l_mean'),('ssc_g_l_bottom_minus_surface','ssc_g_l_bottom_minus_surface')]
    for label,key in definitions:
        per={}
        for s in sorted(stations,key=lambda x:int(re.findall(r'\d+',x)[0])):
            sm=[r.get(key) for r in rows if r['station']==s and r['tide']=='小潮' and r.get(key) is not None]
            lg=[r.get(key) for r in rows if r['station']==s and r['tide']=='大潮' and r.get(key) is not None]
            if sm and lg:
                S=float(np.median(sm));L=float(np.median(lg));per[s]=(L,S)
                paired.append({'variable':label,'station':s,'large_tide_median':L,'small_tide_median':S,'difference_large_minus_small':L-S,'ratio_large_over_small':L/S if S else ''})
        if per:
            L=float(np.median([v[0] for v in per.values()]));S=float(np.median([v[1] for v in per.values()]))
            paired.append({'variable':label,'station':'ACROSS_STATION_MEDIANS','large_tide_median':L,'small_tide_median':S,'difference_large_minus_small':L-S,'ratio_large_over_small':L/S if S else ''})
    writecsv(out/'regime_contrast_summary.csv',paired,['variable','station','large_tide_median','small_tide_median','difference_large_minus_small','ratio_large_over_small'])

    matched=[r for r in rows if r.get('current_speed_m_s') is not None and r.get('ssc_g_l_mean') is not None]
    x=np.array([r['current_speed_m_s'] for r in matched]);y=np.array([r['ssc_g_l_mean'] for r in matched]);rho,p=stats.spearmanr(x,y)
    groups=defaultdict(list)
    for i,r in enumerate(matched):groups[(r['station'],r['tide'])].append(i)
    xd=x.copy();yd=y.copy()
    for inds in groups.values():xd[inds]-=np.mean(x[inds]);yd[inds]-=np.mean(y[inds])
    rw,pw=stats.spearmanr(xd,yd)
    statsrows=[{'test':'current_vs_profile_mean_ssc','n':len(matched),'rho_global':rho,'p_global':p,'rho_within_station_tide':rw,'p_within_station_tide':pw}]
    writecsv(out/'preliminary_statistics.csv',statsrows,list(statsrows[0]))

    cov=[]
    for (s,v),q in sorted(coverage.items()):
        ts=sorted(q['times']);cov.append({'station':s,'variable':v,'n_values':q['n'],'n_times':len(ts),'tides':'+'.join(sorted(q['tides'])),'start':ts[0] if ts else '', 'end':ts[-1] if ts else ''})
    writecsv(out/'station_variable_coverage_core.csv',cov,['station','variable','n_values','n_times','tides','start','end'])
    present=sorted(stations|{r['station'] for r in prof},key=lambda x:int(re.findall(r'\d+',x)[0]))
    summary=f"""# Core Hengsha audit and reproducible physical contrast\n\n- Parsed {len(files)} Excel workbooks.\n- Station IDs present: {', '.join(present)}. HSQ6 is absent.\n- Paired small-/large-tide contrast is restricted to stations with both regimes and matched variables.\n- Current speed vs profile-mean SSC: Spearman rho={rho:.3f} (n={len(matched)}); within station+tide rho={rw:.3f}.\n- See `regime_contrast_summary.csv` for the primary large-/small-tide ratios.\n\nGuardrail: this is observational process evidence, not definitive causal attribution. DO/AOU is not handled here because the supplied DO unit is not documented.\n"""
    (out/'core_findings.md').write_text(summary,encoding='utf-8')
    print(summary)

if __name__=='__main__':main()
