from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

root=Path(__file__).resolve().parents[1]
out=root/'figures_v9'; out.mkdir(exist_ok=True)
sub=root/'submission_figures_v9'; sub.mkdir(exist_ok=True)

def save(fig,stem,num):
    fig.tight_layout(); fig.savefig(out/f'{stem}.pdf',bbox_inches='tight'); fig.savefig(out/f'{stem}.png',dpi=300,bbox_inches='tight'); fig.savefig(sub/f'Figure_{num}.pdf',bbox_inches='tight'); plt.close(fig)

fig,ax=plt.subplots(figsize=(11,6)); ax.axis('off')
boxes=[(0.10,0.75,'GSE127136\n3,620 deposited cells\n13 IgAN + 6 controls'),(0.50,0.75,'GSE286911\n6 pooled libraries\n3 per eGFR group'),(0.90,0.75,'GSE220100\n7 IgAVN + 5 IgAN\nkidney biopsies'),(0.10,0.38,'Formal UCell\npatient × cell type\npseudobulk'),(0.50,0.38,'All QC nuclei\ntop-UMI selection\n5 random seeds'),(0.90,0.38,'Four normalization paths\nPCA/QC diagnostics\nCook distance'),(0.50,0.08,'Interpretation gate\nretain only signals stable to feasible analytical choices')]
for x,y,t in boxes: ax.text(x,y,t,ha='center',va='center',fontsize=10,bbox=dict(boxstyle='round,pad=0.55',facecolor='white',edgecolor='black'))
for x in [0.10,0.50,0.90]: ax.annotate('',xy=(x,0.49),xytext=(x,0.65),arrowprops=dict(arrowstyle='->'))
for x in [0.10,0.50,0.90]: ax.annotate('',xy=(0.50,0.16),xytext=(x,0.28),arrowprops=dict(arrowstyle='->'))
ax.set_title('Figure 1. Public-data reanalysis and prespecified robustness gates',fontsize=14); save(fig,'Figure1_analysis_design',1)

u=pd.read_csv(root/'results/gse127136/GSE127136_patient_celltype_UCell_summary.csv'); pb=pd.read_csv(root/'results/gse127136/GSE127136_pseudobulk_module_statistics.csv')
counts=u.groupby('celltype').n_cells.sum().sort_values(ascending=False); top=counts.head(6).index.tolist(); fig,axes=plt.subplots(1,2,figsize=(13,5.5)); ax=axes[0]
positions=[]; labels=[]; pos=1
for ct in top:
    g=u[(u.celltype==ct)&(u.n_cells>=10)]
    for group,offset,marker in [('control',-0.12,'o'),('IgAN',0.12,'s')]:
        vals=g.loc[g.disease_group==group,'median_RIPS_UCell'].dropna().values; ax.scatter(np.full(len(vals),pos+offset),vals,marker=marker,label=group if pos==1 else None)
    positions.append(pos); labels.append(ct); pos+=1
ax.set_xticks(positions,labels,rotation=35,ha='right'); ax.set_ylabel('Patient-level median RIPS UCell'); ax.set_title('A. Within-cell-type UCell summaries'); ax.legend()
ax=axes[1]; pb2=pb[pb.celltype.isin(top)].copy(); pb2['label']=pb2.celltype+' | '+pb2.module; pb2=pb2.sort_values('cliffs_delta_IgAN_vs_control')
ax.barh(np.arange(len(pb2)),pb2.cliffs_delta_IgAN_vs_control); ax.axvline(0,linewidth=1); ax.set_yticks(np.arange(len(pb2)),pb2.label,fontsize=7); ax.set_xlabel("Cliff's delta: IgAN vs control"); ax.set_title('B. Patient-level pseudobulk module effects'); save(fig,'Figure2_GSE127136_UCell_pseudobulk',2)

s=pd.read_csv(root/'results/gse286911/GSE286911_sample_UCell_scores.csv'); st=pd.read_csv(root/'results/gse286911/GSE286911_UCell_sensitivity.csv'); fig,axes=plt.subplots(1,2,figsize=(12,5)); ax=axes[0]; a=s[s.selection_mode=='all_qc']
for group,marker in [('normal-eGFR','o'),('low-eGFR','s')]:
    g=a[a.clinical_group==group]; ax.scatter(g.sample_id,g.median_RIPS_UCell,marker=marker,s=60,label=group)
ax.set_ylabel('Median formal UCell RIPS'); ax.set_title('A. Six pooled sequencing units (all QC nuclei)'); ax.legend(); ax.tick_params(axis='x',rotation=30)
ax=axes[1]; r=st[st.metric=='RIPS_UCell'].copy(); r['analysis']=r.selection_mode+np.where(r.seed.notna(),' seed '+r.seed.fillna(0).astype(int).astype(str),'')
ax.barh(np.arange(len(r)),r.cliffs_delta_low_vs_normal); ax.axvline(0,linewidth=1); ax.set_yticks(np.arange(len(r)),r.analysis,fontsize=8); ax.set_xlabel("Cliff's delta: low vs normal eGFR"); ax.set_title('B. Sampling sensitivity of the effect direction'); save(fig,'Figure3_GSE286911_formal_UCell',3)

n=pd.read_csv(root/'results/gse220100/GSE220100_normalization_sensitivity.csv'); fig,axes=plt.subplots(1,2,figsize=(12,5)); ax=axes[0]; rr=n[n.metric=='restricted_RIPS']
ax.bar(rr.normalization_strategy,rr.delta_IgAN_minus_IgAVN); ax.axhline(0,linewidth=1); ax.tick_params(axis='x',rotation=30); ax.set_ylabel('Median difference: IgAN - IgAVN'); ax.set_title('A. Restricted RIPS direction by normalization')
ax=axes[1]; comp=n[n.metric=='Complement']; ax.bar(comp.normalization_strategy,comp.delta_IgAN_minus_IgAVN); ax.axhline(0,linewidth=1); ax.tick_params(axis='x',rotation=30); ax.set_ylabel('Complement module difference: IgAN - IgAVN'); ax.set_title('B. Complement signal is normalization-dependent')
for i,(_,r0) in enumerate(comp.iterrows()): ax.text(i,r0.delta_IgAN_minus_IgAVN,f"FDR={r0.FDR_modules_only_within_strategy:.3f}",ha='center',va='bottom' if r0.delta_IgAN_minus_IgAVN>=0 else 'top',fontsize=8)
save(fig,'Figure4_GSE220100_normalization_audit',4)

labels=['GSE127136\ncell-type localization','GSE127136\npseudobulk direction','GSE286911\nformal UCell direction','GSE220100\nrestricted RIPS direction','GSE220100\ncomplement direction']; mat=np.array([[1,1,-1],[1,0,-1],[1,1,-1],[1,0,-1],[1,0,-1]],float)
fig,ax=plt.subplots(figsize=(8,5)); ax.imshow(mat,aspect='auto',vmin=-1,vmax=1,cmap='Greys'); ax.set_yticks(np.arange(len(labels)),labels); ax.set_xticks([0,1,2],['Observed signal','Robustness support','Disease-specific inference'])
for i in range(mat.shape[0]):
    for j in range(mat.shape[1]): ax.text(j,i,{1:'Supported',0:'Sensitive',-1:'Not established'}[int(mat[i,j])],ha='center',va='center',fontsize=8)
ax.set_title('Figure 5. Evidence boundary after formal robustness analyses'); save(fig,'Figure5_evidence_boundary_v9',5)
