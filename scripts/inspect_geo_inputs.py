from __future__ import annotations
import csv, gzip, json, tarfile
from collections import Counter
from pathlib import Path

ROOT=Path('data/external')
OUT=Path('inspection'); OUT.mkdir(parents=True, exist_ok=True)
report={}

p=ROOT/'GSE127136'/'GSE127136_project_IgA_nephropathy_counts.csv.gz'
with gzip.open(p,'rt',newline='',errors='replace') as f:
    reader=csv.reader(f)
    header=next(reader)
    first=next(reader)
cell_names=header[1:]

def first_tokens(x,n=2):
    parts=str(x).split('_')
    return '_'.join(parts[:n]) if len(parts)>=n else str(x)

prefix1=Counter(str(x).split('_')[0] for x in cell_names)
prefix2=Counter(first_tokens(x,2) for x in cell_names)
report['GSE127136']={
    'file_bytes':p.stat().st_size,
    'header_columns':len(header),
    'putative_cells':len(cell_names),
    'first_header_fields':header[:20],
    'first_data_fields':first[:10],
    'prefix1_counts':prefix1.most_common(),
    'prefix2_counts':prefix2.most_common(),
}
(OUT/'GSE127136_cell_names.txt').write_text('\n'.join(cell_names), encoding='utf-8')

for ds in ['GSE220100','GSE286911']:
    tarpath=ROOT/ds/f'{ds}_RAW.tar'
    with tarfile.open(tarpath,'r') as tf:
        members=[m for m in tf.getmembers() if m.isfile()]
        report[ds]={
            'file_bytes':tarpath.stat().st_size,
            'member_count':len(members),
            'members':[{'name':m.name,'size':m.size} for m in members],
        }
        if ds=='GSE220100':
            previews={}
            for m in members:
                raw=tf.extractfile(m).read()
                if m.name.endswith('.gz'):
                    raw=gzip.decompress(raw)
                txt=raw.decode('utf-8','replace')
                previews[m.name]='\n'.join(txt.splitlines()[:35])
            report[ds]['previews']=previews

gsm_map={
 'GSM8733684':'Le1','GSM8733685':'Le2','GSM8733686':'Le3',
 'GSM8733687':'Ne1','GSM8733688':'Ne2','GSM8733689':'Ne3',
}
map_rows=[]
for m in report['GSE286911']['members']:
    sid=next((v for k,v in gsm_map.items() if k in m['name']),None)
    kind=next((k for k in ['matrix','features','barcodes'] if k in m['name'].lower()),None)
    map_rows.append({'member':m['name'],'bytes':m['size'],'sample_id':sid,'kind':kind})
report['GSE286911']['inferred_mapping']=map_rows

(OUT/'geo_input_inspection.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
with open(OUT/'GSE286911_mapping.csv','w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=['member','bytes','sample_id','kind']); w.writeheader(); w.writerows(map_rows)
print(json.dumps({k:{'bytes':v.get('file_bytes'),'members':v.get('member_count')} for k,v in report.items()},indent=2))
