# IgA RIPS formal reanalysis v1.0.0

This validated release completes the four presubmission methodological gates for the public transcriptomic reanalysis of IgA nephropathy and IgA vasculitis nephritis.

## Completed analyses

- Formal `pyucell==0.7.3` scoring in GSE127136 and GSE286911.
- Patient-by-cell-state pseudobulk analysis in GSE127136.
- All-QC, top-UMI, and five-seed random downsampling in GSE286911.
- Four-strategy NanoString normalization audit from GSE220100 RCC files.
- Runtime-verified gene-level Table S1 with source traceability and platform coverage.
- Regenerated Figures 1–5 and automated output validation.

## Evidence boundary

- GSE127136: no FDR-stable patient-level disease contrast.
- GSE286911: sampling-stable separation of six pooled libraries, with zero-inflated scores and no patient-level inference.
- GSE220100: IgAN-IgAVN direction reversal after housekeeping normalization.
- No validated biomarker, prognostic, treatment-selection, or causal claim.

## Validation

The automated validator returned PASS with no missing required outputs and 66 checksummed files. Raw GEO inputs are not redistributed; acquisition identifiers and executable workflows are provided.
