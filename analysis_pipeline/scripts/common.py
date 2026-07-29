from __future__ import annotations
from pathlib import Path
import hashlib, json, math
import numpy as np
from scipy.stats import mannwhitneyu


def cliffs_delta(case, control):
    case=np.asarray(case,float); control=np.asarray(control,float)
    if len(case)==0 or len(control)==0: return np.nan
    gt=sum(x>y for x in case for y in control)
    lt=sum(x<y for x in case for y in control)
    return (gt-lt)/(len(case)*len(control))


def exact_mwu(case, control):
    case=np.asarray(case,float); control=np.asarray(control,float)
    if len(case)==0 or len(control)==0: return np.nan
    return float(mannwhitneyu(case, control, alternative='two-sided', method='exact').pvalue)


def bh_fdr(pvalues):
    p=np.asarray(pvalues,float)
    out=np.full(len(p),np.nan)
    ok=np.isfinite(p)
    vals=p[ok]
    if len(vals)==0: return out
    order=np.argsort(vals); ranked=vals[order]
    adj=np.minimum.accumulate((ranked*len(ranked)/(np.arange(len(ranked))+1))[::-1])[::-1]
    adj=np.minimum(adj,1.0)
    restored=np.empty_like(adj); restored[order]=adj
    out[np.where(ok)[0]]=restored
    return out


def sha256(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''): h.update(block)
    return h.hexdigest()


def save_json(obj,path):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(obj,indent=2,ensure_ascii=False),encoding='utf-8')
