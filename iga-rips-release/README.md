# IgA renal injury program reanalysis — release candidate v0.9.0-rc1

Reproducible analysis package for the manuscript:

**Exploratory integration of public transcriptomic datasets identifies method-dependent renal injury signals in IgA nephropathy and IgA vasculitis nephritis**

## Scope

RIPS is a broad downstream renal-injury program summary, not an IgA-specific biomarker. The workflow audits sensitivity to formal UCell scoring, cell/nucleus sampling, patient-level pseudobulk aggregation, and NanoString normalization.

## Current gate status

- Official `pyucell==0.7.3` workflow: implemented and smoke-tested.
- GSE127136 patient × cell-type pseudobulk: implemented with minimum-cell thresholds and patient-level inference.
- GSE220100 alternative NanoString normalization: implemented.
- Table S1 gene-level provenance: complete.
- Dataset-level numerical execution remains pending until the public GEO binary inputs are placed under `data/external/`.

## Required public inputs

- GSE127136: `GSE127136_project_IgA_nephropathy_counts.csv.gz`
- GSE286911: `GSE286911_RAW.tar`
- GSE220100: `GSE220100_RAW.tar`

## Reproduce

```bash
conda env create -f environment.yml
conda activate iga-rips-v8
python scripts/00_validate_environment.py
python scripts/01_acquire_public_inputs.py --dataset all
python scripts/02_gse127136_pyucell_pseudobulk.py --counts data/external/GSE127136/GSE127136_project_IgA_nephropathy_counts.csv.gz
python scripts/03_gse286911_pyucell.py --root data/external/GSE286911/10x
python scripts/04_gse220100_nanostring.py --rcc-dir data/external/GSE220100/rcc --metadata metadata/GSE220100_samples.csv
python scripts/05_make_figures.py
python scripts/06_validate_outputs.py
```

## Release policy

Create `v1.0.0` only after all three real-data runs complete and `scripts/06_validate_outputs.py` passes. Zenodo should archive the validated release and mint the DOI.
