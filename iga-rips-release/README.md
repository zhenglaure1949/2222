# IgA renal injury program reanalysis — v1.0.0

Reproducible analysis package for the manuscript:

**Robustness-focused reanalysis of public transcriptomic datasets identifies sampling-stable but normalization-sensitive renal injury signals in IgA-associated kidney disease**

## Scope

RIPS is a broad downstream renal-injury program summary, not an IgA-specific biomarker. The workflow audits formal UCell scoring, cell/nucleus sampling, patient-level pseudobulk aggregation, and NanoString normalization.

## Validated gate status

- Official `pyucell==0.7.3`: completed on GSE127136 and GSE286911.
- GSE127136 patient × cell-state pseudobulk: completed with a prespecified minimum of 10 cells and patient-level inference.
- GSE286911 all-QC, top-UMI, and five-seed random downsampling: completed on 525,552 QC nuclei, with inference restricted to six pooled libraries.
- GSE220100 four-strategy NanoString normalization audit: completed from RCC files.
- Table S1 gene-level provenance and runtime platform coverage: completed.
- Five submission figures: regenerated from validated outputs.
- Automated validation: PASS; no required output missing; 66 checksummed files.

## Reproduce

The executable project is under `analysis_pipeline/`.

```bash
cd analysis_pipeline
conda env create -f environment.yml
conda activate iga-rips-v9

python scripts/02_gse127136_pyucell_pseudobulk.py \
  --counts ../data/external/GSE127136/GSE127136_project_IgA_nephropathy_counts.csv.gz \
  --signatures config/rips_signatures.yml \
  --markers config/celltype_markers.yml \
  --outdir results/gse127136

python scripts/03_gse286911_pyucell.py \
  --root ../data/external/GSE286911/10x \
  --signatures config/rips_signatures.yml \
  --outdir results/gse286911

python scripts/04_gse220100_nanostring.py \
  --rcc-dir ../data/external/GSE220100/rcc \
  --metadata metadata/GSE220100_samples.csv \
  --signatures config/rips_signatures.yml \
  --outdir results/gse220100

python scripts/07_update_table_s1.py
python scripts/05_make_figures_v9.py
python scripts/06_validate_outputs_v9.py
```

## Interpretation boundary

- GSE127136 did not yield an FDR-stable patient-level disease contrast.
- GSE286911 showed sampling-stable formal-UCell separation of six pooled libraries, but the score was zero-inflated and not patient-level.
- GSE220100 changed IgAN-IgAVN direction after housekeeping normalization.
- No clinical biomarker, prognosis, treatment-selection, or causal claim is supported.

## Archival

The validated `v1.0.0` GitHub release is intended for Zenodo archival. The minted DOI should be added to the manuscript and `CITATION.cff` after repository activation in Zenodo.
