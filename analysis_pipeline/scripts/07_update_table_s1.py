from __future__ import annotations
from pathlib import Path
import argparse, json
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Alignment

p=argparse.ArgumentParser(); p.add_argument('--template',default='supplement/TableS1_v8_RIPS_gene_sources.xlsx'); p.add_argument('--out',default='supplement/TableS1_v9_RIPS_gene_sources_runtime_verified.xlsx'); p.add_argument('--results-root',default='results'); a=p.parse_args(); root=Path(a.results_root)
cov127=pd.read_csv(root/'gse127136/GSE127136_module_gene_coverage.csv'); cov286=pd.read_csv(root/'gse286911/GSE286911_module_gene_coverage_by_sample.csv'); cov220=pd.read_csv(root/'gse220100/GSE220100_module_gene_coverage.csv')
def genes_from(df,module,col='detected_genes'):
 vals=df.loc[df.module==module,col].dropna().astype(str); out=set()
 for v in vals: out.update(x for x in v.split(';') if x)
 return out
modules=['Fibrosis','Inflammatory_chemotaxis','Complement','Endothelial_activation','Tubular_injury']; sets={}
for m in modules:
 sets[(m,'GSE127136')]=genes_from(cov127,m); sets[(m,'GSE286911')]=genes_from(cov286,m); sets[(m,'GSE220100')]=genes_from(cov220,m)
wb=load_workbook(a.template); ws=wb['Gene_sources']; header={ws.cell(4,c).value:c for c in range(1,ws.max_column+1)}
for r in range(5,ws.max_row+1):
 module=ws.cell(r,header['Module']).value; gene=ws.cell(r,header['Gene']).value
 if not module or not gene: continue
 ws.cell(r,header['GSE127136 coverage']).value='Yes' if gene in sets.get((module,'GSE127136'),set()) else 'No'
 ws.cell(r,header['GSE286911 coverage']).value='Yes' if gene in sets.get((module,'GSE286911'),set()) else 'No'
 ws.cell(r,header['GSE220100 current-output coverage']).value='Yes' if gene in sets.get((module,'GSE220100'),set()) else 'No'
ws.cell(2,1).value='RIPS is a broad downstream renal-injury framework, not an IgA-specific biomarker. Platform coverage in this version was verified against the real GSE127136, GSE286911, and GSE220100 inputs.'
pc=wb['Platform_coverage']; pc.cell(2,1).value='Coverage counts were recalculated from the runtime-verified Gene_sources sheet after formal UCell and NanoString sensitivity analyses.'
for r in range(5,pc.max_row+1):
 m=pc.cell(r,1).value
 if not m: continue
 total=sum(1 for rr in range(5,ws.max_row+1) if ws.cell(rr,header['Module']).value==m); pc.cell(r,2).value=total; pc.cell(r,3).value=total; pc.cell(r,4).value=len(sets.get((m,'GSE127136'),set())); pc.cell(r,5).value=len(sets.get((m,'GSE286911'),set())); pc.cell(r,6).value=len(sets.get((m,'GSE220100'),set()))
wb['Version_notes'].append(['v9','2026-07-27','Runtime-verified platform coverage; formal pyUCell and patient-level pseudobulk execution; NanoString multi-normalization audit.','Post-analysis submission candidate'])
for sheet in wb.worksheets:
 sheet.freeze_panes='A5' if sheet.title in ['Gene_sources','References','Curation_rules','Platform_coverage','Version_notes'] else None
 for row in sheet.iter_rows():
  for cell in row: cell.alignment=Alignment(vertical='top',wrap_text=True)
out=Path(a.out); out.parent.mkdir(parents=True,exist_ok=True); wb.save(out)
rows=[]
for r in range(5,ws.max_row+1):
 if ws.cell(r,header['Gene']).value: rows.append({k:ws.cell(r,c).value for k,c in header.items()})
pd.DataFrame(rows).to_csv(out.with_suffix('.tsv'),sep='\t',index=False)
summary={'output':str(out),'rows':len(rows),'coverage':{f'{m}_{ds}':len(sets[(m,ds)]) for m in modules for ds in ['GSE127136','GSE286911','GSE220100']}}
(out.parent/'TableS1_v9_runtime_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8'); print(json.dumps(summary,indent=2))
