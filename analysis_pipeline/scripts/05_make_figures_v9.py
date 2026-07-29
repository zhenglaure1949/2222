from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'figures_v9'; OUT.mkdir(parents=True,exist_ok=True)
SUB=ROOT/'submission_figures_v9'; SUB.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({'font.size':9,'axes.titlesize':11,'axes.labelsize':9,'figure.titlesize':14,'pdf.fonttype':42,'ps.fonttype':42})

def save(fig,stem,num):
    fig.tight_layout()
    fig.savefig(OUT/f'{stem}.pdf',bbox_inches='tight')
    fig.savefig(OUT/f'{stem}.png',dpi=300,bbox_inches='tight')
    fig.savefig(SUB/f'Figure_{num}.pdf',bbox_inches='tight')
    plt.close(fig)

fig,ax=plt.subplots(figsize=(12,5.2)); ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis('off')
def box(x,y,w,h,text,fs=9):
    p=FancyBboxPatch((x-w/2,y-h/2),w,h,boxstyle='round,pad=0.018',facecolor='white',edgecolor='black',linewidth=1)
    ax.add_patch(p); ax.text(x,y,text,ha='center',va='center',fontsize=fs)
cols=[0.17,0.50,0.83]
box(cols[0],0.78,0.25,0.18,'GSE127136\n3,620 deposited cells\n13 IgAN + 6 controls')
box(cols[1],0.78,0.25,0.18,'GSE286911\n6 pooled sequencing libraries\n3 low-eGFR + 3 normal-eGFR')
box(cols[2],0.78,0.25,0.18,'GSE220100\n7 IgAVN + 5 IgAN\nkidney biopsies')
box(cols[0],0.45,0.25,0.19,'Formal pyUCell\nwithin-cell-type patient summaries\npatient × cell-type pseudobulk')
box(cols[1],0.45,0.25,0.19,'Formal pyUCell on 525,552 QC nuclei\nall QC / top-UMI\n5 random seeds')
box(cols[2],0.45,0.25,0.19,'Four NanoString normalizations\nPCA + housekeeping diagnostics\nCook distance')
for x in cols: ax.annotate('',xy=(x,0.56),xytext=(x,0.68),arrowprops=dict(arrowstyle='-|>',lw=1))
box(0.50,0.16,0.48,0.14,'Interpretation gate: retain only signals stable to feasible analytical choices;\ndo not infer a validated disease signature or clinical biomarker',fs=10)
for x in cols: ax.annotate('',xy=(0.50,0.23),xytext=(x,0.34),arrowprops=dict(arrowstyle='-|>',lw=1))
ax.set_title('Public-data reanalysis and prespecified robustness gates')
save(fig,'Figure1_analysis_design_final',1)

u=pd.read_csv(ROOT/'results/gse127136/GSE127136_patient_celltype_UCell_summary.csv')
pb=pd.read_csv(ROOT/'results/gse127136/GSE127136_pseudobulk_module_statistics.csv')
sel=['Proximal_tubular','Macrophage_monocyte']
fig,axes=plt.subplots(1,2,figsize=(12.5,5.4),gridspec_kw={'width_ratios':[1,1.35]})
ax=axes[0]
positions=[]; labs=[]
for i,ct in enumerate(sel,1):
    g=u[(u.celltype==ct)&(u.n_cells>=10)]
    for group,offset,marker in [('control',-0.12,'o'),('IgAN',0.12,'s')]:
        vals=g.loc[g.disease_group==group,'median_RIPS_UCell'].dropna().values
        ax.scatter(np.full(len(vals),i+offset),vals,marker=marker,s=45,label=group if i==1 else None)
    positions.append(i); labs.append(ct.replace('_',' '))
ax.set_xticks(positions,labs); ax.set_ylabel('Patient-level median formal UCell RIPS'); ax.set_title('A. Within-cell-type patient summaries\n(minimum 10 cells per stratum)'); ax.legend(frameon=False)
ax.text(0.02,0.02,'No comparison survived within-cell-type FDR correction.',transform=ax.transAxes,fontsize=8,va='bottom')
ax=axes[1]
pp=pb[pb.celltype.isin(sel)].dropna(subset=['cliffs_delta_IgAN_vs_control']).copy()
pp['label']=pp.celltype.str.replace('_',' ')+' | '+pp.module.str.replace('_',' ')
pp=pp.sort_values(['celltype','cliffs_delta_IgAN_vs_control'])
y=np.arange(len(pp)); ax.scatter(pp.cliffs_delta_IgAN_vs_control,y,s=45)
for yi,(d,fdr) in enumerate(zip(pp.cliffs_delta_IgAN_vs_control,pp.FDR_within_celltype)):
    ax.plot([0,d],[yi,yi],linewidth=1); ax.text(1.03 if d>=0 else -1.03,yi,f'FDR {fdr:.2f}',va='center',ha='left' if d>=0 else 'right',fontsize=7)
ax.axvline(0,color='black',linewidth=0.8); ax.set_xlim(-1.25,1.25); ax.set_yticks(y,pp.label,fontsize=8); ax.set_xlabel("Cliff's delta: IgAN vs control"); ax.set_title('B. Patient-level pseudobulk module effects')
fig.suptitle('GSE127136: formal UCell localization and patient-level pseudobulk')
save(fig,'Figure2_GSE127136_final',2)

scores=pd.read_csv(ROOT/'results/gse286911/GSE286911_sample_UCell_scores.csv')
st=pd.read_csv(ROOT/'results/gse286911/GSE286911_UCell_sensitivity.csv')
qc=pd.read_csv(ROOT/'results/gse286911/GSE286911_sample_QC.csv')
fig,axes=plt.subplots(1,3,figsize=(15,4.8))
ax=axes[0]; allq=scores[scores.selection_mode=='all_qc']
for group,marker in [('normal-eGFR','o'),('low-eGFR','s')]:
    g=allq[allq.clinical_group==group]; ax.scatter(g.sample_id,g.median_RIPS_UCell,marker=marker,s=60,label=group)
ax.set_ylabel('Pool-level median formal UCell RIPS'); ax.set_title('A. All 525,552 QC nuclei'); ax.legend(frameon=False); ax.tick_params(axis='x',rotation=30)
ax.text(0.02,0.02,'Normal-eGFR pool medians were zero,\nindicating strong score zero inflation.',transform=ax.transAxes,fontsize=8,va='bottom')
ax=axes[1]; r=st[st.metric=='RIPS_UCell'].copy(); r['analysis']=r.selection_mode.str.replace('_',' ')+np.where(r.seed.notna(),' (seed '+r.seed.fillna(0).astype(int).astype(str)+')','')
y=np.arange(len(r)); ax.scatter(r.cliffs_delta_low_vs_normal,y,s=45); ax.axvline(0,color='black',linewidth=0.8); ax.set_xlim(-1.1,1.1); ax.set_yticks(y,r.analysis,fontsize=8); ax.set_xlabel("Cliff's delta: low vs normal eGFR"); ax.set_title('B. Direction across sampling schemes')
for yi,pv in enumerate(r.mann_whitney_exact_p): ax.text(1.02,yi,f'P={pv:.2f}',va='center',fontsize=7)
ax=axes[2]; ax.bar(qc.sample_id,qc.qc_nuclei); ax.set_ylabel('QC nuclei'); ax.set_title('C. Pool-level QC nuclei'); ax.tick_params(axis='x',rotation=30)
ax.text(0.02,0.98,'Inference remains at the six-pool level;\npatient-level variance is unavailable.',transform=ax.transAxes,fontsize=8,va='top')
fig.suptitle('GSE286911: formal pyUCell direction is sampling-stable but pool-limited and zero-inflated')
save(fig,'Figure3_GSE286911_final',3)

n=pd.read_csv(ROOT/'results/gse220100/GSE220100_normalization_sensitivity.csv')
qc220=pd.read_csv(ROOT/'results/gse220100/GSE220100_NanoString_QC.csv')
score_full=pd.read_csv(ROOT/'results/gse220100/GSE220100_scores_background_positive_housekeeping.csv',index_col=0)
fig,axes=plt.subplots(1,3,figsize=(15,4.8))
order=['raw_log2','background_only','background_positive','background_positive_housekeeping']; labels=['Raw log2','Background','Background + positive','Background + positive + HK']
ax=axes[0]; rr=n[n.metric=='restricted_RIPS'].set_index('normalization_strategy').loc[order]
ax.bar(np.arange(4),rr.delta_IgAN_minus_IgAVN); ax.axhline(0,color='black',linewidth=0.8); ax.set_xticks(np.arange(4),labels,rotation=25,ha='right'); ax.set_ylabel('Median difference: IgAN - IgAVN'); ax.set_title('A. Restricted RIPS direction')
for i,pv in enumerate(rr.mann_whitney_exact_p): ax.text(i,rr.delta_IgAN_minus_IgAVN.iloc[i],f' P={pv:.3f}',ha='center',va='bottom' if rr.delta_IgAN_minus_IgAVN.iloc[i]>=0 else 'top',fontsize=7)
ax=axes[1]; cc=n[n.metric=='Complement'].set_index('normalization_strategy').loc[order]
ax.bar(np.arange(4),cc.delta_IgAN_minus_IgAVN); ax.axhline(0,color='black',linewidth=0.8); ax.set_xticks(np.arange(4),labels,rotation=25,ha='right'); ax.set_ylabel('Complement difference: IgAN - IgAVN'); ax.set_title('B. Complement module')
for i,fdr in enumerate(cc.FDR_modules_only_within_strategy): ax.text(i,cc.delta_IgAN_minus_IgAVN.iloc[i],f' FDR={fdr:.3f}',ha='center',va='bottom' if cc.delta_IgAN_minus_IgAVN.iloc[i]>=0 else 'top',fontsize=7)
ax=axes[2]; q=qc220.set_index('sample_id').loc[score_full.index]; x=np.log2(q.housekeeping_geo_mean.astype(float)); yv=score_full.restricted_RIPS.astype(float); groups=score_full.disease_group
for group,marker in [('IgAN','s'),('IgAVN','o')]:
    m=groups==group; ax.scatter(x[m],yv[m],marker=marker,s=55,label=group)
coef=np.polyfit(x,yv,1); xx=np.linspace(x.min(),x.max(),100); ax.plot(xx,np.polyval(coef,xx),linewidth=1); ax.set_xlabel('log2 housekeeping geometric mean'); ax.set_ylabel('Fully normalized restricted RIPS'); ax.set_title('C. Housekeeping dependence'); ax.legend(frameon=False); ax.text(0.04,0.04,'Spearman ρ = -0.804\nP = 0.0016',transform=ax.transAxes,fontsize=8)
fig.suptitle('GSE220100: the IgAN-IgAVN contrast reverses across plausible NanoString normalizations')
save(fig,'Figure4_GSE220100_final',4)

rows=['GSE127136\nwithin-cell-type UCell','GSE127136\npseudobulk modules','GSE286911\nformal UCell direction','GSE220100\nrestricted RIPS','GSE220100\ncomplement module']
cols=['Observed signal','Robustness result','Disease-specific inference']
texts=[['Localized','No FDR-stable difference','Not established'],['Effect directions','No FDR-stable difference','Not established'],['Complete pool rank separation','Sampling-stable; zero-inflated','Not established'],['Group contrast','Normalization direction reversal','Not established'],['FDR signal in one path','Normalization-specific only','Not established']]
vals=np.array([[0.25,0.65,0.95],[0.35,0.65,0.95],[0.15,0.45,0.95],[0.25,0.75,0.95],[0.25,0.75,0.95]])
fig,ax=plt.subplots(figsize=(10.5,5.7)); ax.imshow(vals,cmap='Greys',vmin=0,vmax=1,aspect='auto')
ax.set_xticks(np.arange(3),cols,fontsize=10); ax.set_yticks(np.arange(len(rows)),rows,fontsize=9)
for i in range(len(rows)):
    for j in range(3):
        ax.text(j,i,texts[i][j],ha='center',va='center',fontsize=8,color='white' if vals[i,j]>0.72 else 'black',wrap=True)
ax.set_title('Evidence boundary after formal robustness analyses',pad=14)
ax.set_xticks(np.arange(-.5,3,1),minor=True); ax.set_yticks(np.arange(-.5,len(rows),1),minor=True); ax.grid(which='minor',color='black',linewidth=0.6); ax.tick_params(which='minor',bottom=False,left=False)
fig.tight_layout(rect=[0,0.12,1,1])
fig.text(0.5,0.035,'Clinical biomarker, prognosis, treatment selection, and causal claims remain unsupported.',ha='center',fontsize=9)
fig.savefig(OUT/'Figure5_evidence_boundary_final.pdf',bbox_inches='tight')
fig.savefig(OUT/'Figure5_evidence_boundary_final.png',dpi=300,bbox_inches='tight')
fig.savefig(SUB/'Figure_5.pdf',bbox_inches='tight')
plt.close(fig)
