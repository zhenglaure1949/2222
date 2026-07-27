# IgA RIPS formal reanalysis

This directory contains the executable submission-gate workflow for three public datasets: GSE127136, GSE286911, and GSE220100.

The workflow implements official pyUCell scoring, patient-by-cell-type pseudobulk analysis, NanoString multi-normalization sensitivity analysis, runtime-verified gene-source Table S1 generation, figure regeneration, and checksum validation.

RIPS is a broad downstream renal-injury framework. It is not an IgA-specific biomarker and is not validated for diagnosis, prognosis, or treatment selection.

The biological unit of inference is the patient for GSE127136, the pooled sequencing library for GSE286911, and the biopsy specimen for GSE220100. Cells and nuclei are not treated as independent biological replicates.
