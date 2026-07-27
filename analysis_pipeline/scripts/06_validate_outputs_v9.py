from pathlib import Path
import hashlib, json, sys
root=Path(__file__).resolve().parents[1]
required=[
 'results/gse127136/GSE127136_run_summary.json',
 'results/gse127136/GSE127136_patient_celltype_UCell_summary.csv',
 'results/gse127136/GSE127136_pseudobulk_module_statistics.csv',
 'results/gse286911/GSE286911_run_summary.json',
 'results/gse286911/GSE286911_UCell_sensitivity.csv',
 'results/gse220100/GSE220100_run_summary.json',
 'results/gse220100/GSE220100_normalization_sensitivity.csv',
 'results/gse220100/GSE220100_gene_statistics.csv',
 'supplement/TableS1_v9_RIPS_gene_sources_runtime_verified.xlsx',
 'submission_figures_v9/Figure_1.pdf','submission_figures_v9/Figure_2.pdf','submission_figures_v9/Figure_3.pdf','submission_figures_v9/Figure_4.pdf','submission_figures_v9/Figure_5.pdf'
]
missing=[x for x in required if not (root/x).exists() or (root/x).stat().st_size==0]
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
 return h.hexdigest()
manifest=[]
for d in ['results','figures_v9','submission_figures_v9','supplement','config','metadata','scripts']:
 for p in sorted((root/d).rglob('*')) if (root/d).exists() else []:
  if p.is_file() and p.stat().st_size<100_000_000: manifest.append({'path':str(p.relative_to(root)),'bytes':p.stat().st_size,'sha256':sha(p)})
(root/'metadata').mkdir(exist_ok=True)
(root/'metadata'/'sha256_manifest_v9.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
report={'status':'PASS' if not missing else 'FAIL','missing':missing,'n_manifest_files':len(manifest)}
(root/'results'/'validation_report_v9.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
if missing: sys.exit(1)
