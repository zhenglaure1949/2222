from __future__ import annotations
from pathlib import Path
import argparse, json, re, warnings, yaml
import numpy as np
import pandas as pd
import scanpy as sc
from scipy import sparse
from anndata import AnnData
from pyucell import compute_ucell_scores
from common import exact_mwu, cliffs_delta, bh_fdr


def read_counts(path: str) -> AnnData:
    df = pd.read_csv(path, index_col=0, compression="infer")
    first_index = [str(x) for x in df.index[:50]]
    gene_like = np.mean([bool(re.match(r"^[A-Za-z0-9_.-]+$", x)) for x in first_index])
    if df.shape[0] > df.shape[1] and gene_like > 0.8:
        X = sparse.csr_matrix(df.T.to_numpy(dtype=np.float32, copy=False))
        ad = AnnData(X=X)
        ad.obs_names = df.columns.astype(str)
        ad.var_names = df.index.astype(str)
    else:
        X = sparse.csr_matrix(df.to_numpy(dtype=np.float32, copy=False))
        ad = AnnData(X=X)
        ad.obs_names = df.index.astype(str)
        ad.var_names = df.columns.astype(str)
    ad.var_names_make_unique()
    return ad


def parse_patient(cell: str) -> str | None:
    m = re.match(r"^(IgAN_\d+|NM_\d+)", str(cell))
    return m.group(1) if m else None


def marker_assisted_annotation(ad: AnnData, marker_file: str, seed: int):
    markers = yaml.safe_load(Path(marker_file).read_text(encoding="utf-8"))
    work = ad.copy()
    sc.pp.normalize_total(work, target_sum=1e4)
    sc.pp.log1p(work)
    sc.pp.highly_variable_genes(work, n_top_genes=min(2000, work.n_vars), flavor="seurat")
    hv = work[:, work.var.highly_variable].copy()
    sc.pp.scale(hv, max_value=10)
    sc.tl.pca(hv, n_comps=min(30, hv.n_obs - 1, hv.n_vars - 1), random_state=seed)
    sc.pp.neighbors(hv, n_neighbors=min(15, max(2, hv.n_obs // 20)), n_pcs=min(20, hv.obsm["X_pca"].shape[1]), random_state=seed)
    sc.tl.leiden(hv, resolution=0.6, random_state=seed, key_added="leiden")
    work.obs["leiden"] = hv.obs["leiden"].astype(str).values
    marker_cols = []
    coverage_rows = []
    for name, genes in markers.items():
        present = [g for g in genes if g in work.var_names]
        coverage_rows.append({"celltype": name, "requested_genes": len(genes), "detected_genes": len(present), "genes_detected": ";".join(present)})
        col = f"marker_{name}"
        marker_cols.append(col)
        if present:
            vals = work[:, present].X.mean(axis=1)
            work.obs[col] = np.asarray(vals).ravel()
        else:
            work.obs[col] = np.nan
    cluster_means = work.obs.groupby("leiden", observed=True)[marker_cols].mean()
    cmap = {}
    for cl in cluster_means.index:
        row = cluster_means.loc[cl]
        cmap[cl] = row.idxmax().replace("marker_", "") if row.notna().any() else "Unresolved"
    ad.obs["leiden"] = work.obs["leiden"].values
    ad.obs["celltype"] = work.obs["leiden"].map(cmap).astype(str).values
    return ad, cluster_means, pd.DataFrame(coverage_rows)


def module_coverage(ad: AnnData, modules: dict[str, list[str]]) -> pd.DataFrame:
    rows = []
    for module, genes in modules.items():
        detected = [g for g in genes if g in ad.var_names]
        rows.append({"module": module, "requested_n": len(genes), "detected_n": len(detected), "coverage_fraction": len(detected) / len(genes) if genes else np.nan, "detected_genes": ";".join(detected), "missing_genes": ";".join([g for g in genes if g not in ad.var_names])})
    return pd.DataFrame(rows)


def patient_level_ucell(ad: AnnData, module_cols: list[str], outdir: Path):
    summary = ad.obs.groupby(["patient_id", "disease_group", "celltype"], observed=True).agg(n_cells=("RIPS_UCell", "size"), median_RIPS_UCell=("RIPS_UCell", "median"), mean_RIPS_UCell=("RIPS_UCell", "mean"), **{f"median_{c}": (c, "median") for c in module_cols}).reset_index()
    summary.to_csv(outdir / "GSE127136_patient_celltype_UCell_summary.csv", index=False)
    rows = []
    metrics = ["RIPS_UCell"] + [c.replace("_UCell", "") for c in module_cols]
    for threshold in [1, 10, 25, 50]:
        keep = summary[summary.n_cells >= threshold].copy()
        for ctype, g in keep.groupby("celltype", observed=True):
            for metric in metrics:
                col = "median_RIPS_UCell" if metric == "RIPS_UCell" else f"median_{metric}_UCell"
                control = g.loc[g.disease_group == "control", col].dropna().to_numpy()
                case = g.loc[g.disease_group == "IgAN", col].dropna().to_numpy()
                rows.append({"min_cells": threshold, "celltype": ctype, "metric": metric, "control_n": len(control), "IgAN_n": len(case), "control_median": np.median(control) if len(control) else np.nan, "IgAN_median": np.median(case) if len(case) else np.nan, "delta_IgAN_minus_control": np.median(case) - np.median(control) if len(case) and len(control) else np.nan, "mann_whitney_exact_p": exact_mwu(case, control), "cliffs_delta_IgAN_vs_control": cliffs_delta(case, control)})
    stats = pd.DataFrame(rows)
    stats["FDR_within_threshold_celltype"] = stats.groupby(["min_cells", "celltype"], observed=True)["mann_whitney_exact_p"].transform(lambda x: bh_fdr(x.to_numpy()))
    stats.to_csv(outdir / "GSE127136_UCell_threshold_statistics.csv", index=False)
    return summary, stats


def pseudobulk(ad: AnnData, modules: dict[str, list[str]], outdir: Path, min_cells: int):
    rows, matrices = [], []
    grouped = ad.obs.groupby(["patient_id", "celltype"], observed=True).indices
    for (patient, ctype), idx in grouped.items():
        if len(idx) < min_cells:
            continue
        summed = np.asarray(ad.X[idx].sum(axis=0)).ravel().astype(float)
        lib = float(summed.sum())
        logcpm = np.log2((summed / max(lib, 1.0)) * 1e6 + 1.0)
        matrices.append(pd.Series(logcpm, index=ad.var_names, name=f"{patient}|{ctype}"))
        rows.append({"patient_id": patient, "disease_group": ad.obs.iloc[idx[0]]["disease_group"], "celltype": ctype, "n_cells": len(idx), "library_size": lib})
    if not matrices:
        raise RuntimeError("No patient-cell-type strata passed the pseudobulk minimum-cell threshold.")
    expr = pd.DataFrame(matrices)
    expr.index = pd.MultiIndex.from_tuples([tuple(x.split("|", 1)) for x in expr.index], names=["patient_id", "celltype"])
    meta = pd.DataFrame(rows).set_index(["patient_id", "celltype"])
    expr.to_csv(outdir / "GSE127136_patient_celltype_pseudobulk_logCPM.csv.gz", compression="gzip")
    meta.to_csv(outdir / "GSE127136_patient_celltype_pseudobulk_metadata.csv")
    score_rows = []
    for ctype in sorted(meta.index.get_level_values("celltype").unique()):
        x = expr.xs(ctype, level="celltype")
        m = meta.xs(ctype, level="celltype")
        z = (x - x.mean(axis=0)) / x.std(axis=0, ddof=0).replace(0, np.nan)
        for module, genes in modules.items():
            use = [g for g in genes if g in z.columns]
            if not use:
                continue
            s = z[use].mean(axis=1, skipna=True)
            controls = s[m.loc[s.index, "disease_group"] == "control"].dropna().to_numpy()
            cases = s[m.loc[s.index, "disease_group"] == "IgAN"].dropna().to_numpy()
            score_rows.append({"celltype": ctype, "module": module, "n_genes": len(use), "control_n": len(controls), "IgAN_n": len(cases), "control_median": np.median(controls) if len(controls) else np.nan, "IgAN_median": np.median(cases) if len(cases) else np.nan, "delta_IgAN_minus_control": np.median(cases) - np.median(controls) if len(controls) and len(cases) else np.nan, "mann_whitney_exact_p": exact_mwu(cases, controls), "cliffs_delta_IgAN_vs_control": cliffs_delta(cases, controls)})
    stats = pd.DataFrame(score_rows)
    stats["FDR_within_celltype"] = stats.groupby("celltype", observed=True)["mann_whitney_exact_p"].transform(lambda x: bh_fdr(x.to_numpy()))
    stats.to_csv(outdir / "GSE127136_pseudobulk_module_statistics.csv", index=False)
    return meta.reset_index(), stats


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--counts", required=True)
    p.add_argument("--signatures", default="config/rips_signatures.yml")
    p.add_argument("--markers", default="config/celltype_markers.yml")
    p.add_argument("--outdir", default="results/gse127136")
    p.add_argument("--min-genes", type=int, default=100)
    p.add_argument("--max-mito", type=float, default=25.0)
    p.add_argument("--min-cells-pseudobulk", type=int, default=10)
    p.add_argument("--seed", type=int, default=20260727)
    p.add_argument("--write-h5ad", action="store_true")
    a = p.parse_args()
    out = Path(a.outdir); out.mkdir(parents=True, exist_ok=True)
    modules = yaml.safe_load(Path(a.signatures).read_text(encoding="utf-8"))["modules"]
    ad = read_counts(a.counts)
    input_cells = ad.n_obs
    ad.obs["patient_id"] = [parse_patient(x) for x in ad.obs_names]
    excluded_pbm = int(ad.obs["patient_id"].isna().sum())
    ad = ad[ad.obs["patient_id"].notna()].copy()
    ad.obs["disease_group"] = np.where(ad.obs["patient_id"].str.startswith("IgAN_"), "IgAN", "control")
    ad.var["mt"] = ad.var_names.str.upper().str.startswith("MT-")
    sc.pp.calculate_qc_metrics(ad, qc_vars=["mt"], inplace=True, percent_top=None)
    qc_before = ad.n_obs
    ad = ad[(ad.obs.n_genes_by_counts >= a.min_genes) & (ad.obs.pct_counts_mt <= a.max_mito)].copy()
    ad, cluster_means, marker_coverage = marker_assisted_annotation(ad, a.markers, a.seed)
    cluster_means.to_csv(out / "GSE127136_marker_cluster_scores.csv")
    marker_coverage.to_csv(out / "GSE127136_marker_coverage.csv", index=False)
    module_coverage(ad, modules).to_csv(out / "GSE127136_module_gene_coverage.csv", index=False)
    compute_ucell_scores(ad, modules, max_rank=min(1500, ad.n_vars), missing_genes="skip", n_jobs=1, device="cpu")
    module_cols = [f"{m}_UCell" for m in modules]
    ad.obs["RIPS_UCell"] = ad.obs[module_cols].mean(axis=1)
    ad.obs[["patient_id", "disease_group", "celltype", "leiden", "n_genes_by_counts", "total_counts", "pct_counts_mt", "RIPS_UCell"] + module_cols].to_csv(out / "GSE127136_cell_level_UCell_scores.csv.gz", compression="gzip")
    ad.obs.groupby(["patient_id", "disease_group"], observed=True).size().rename("n_cells").reset_index().to_csv(out / "GSE127136_patient_total_counts.csv", index=False)
    ad.obs.groupby(["patient_id", "disease_group", "celltype"], observed=True).size().rename("n_cells").reset_index().to_csv(out / "GSE127136_patient_celltype_counts.csv", index=False)
    summary, _ = patient_level_ucell(ad, module_cols, out)
    pb_meta, _ = pseudobulk(ad, modules, out, a.min_cells_pseudobulk)
    if a.write_h5ad:
        ad.write_h5ad(out / "GSE127136_processed_with_UCell.h5ad", compression="gzip")
    report = {"input_cells": input_cells, "excluded_PBM_cells": excluded_pbm, "kidney_cells_before_qc": qc_before, "kidney_cells_after_qc": ad.n_obs, "genes": ad.n_vars, "patients": int(ad.obs.patient_id.nunique()), "IgAN_patients": int(ad.obs.loc[ad.obs.disease_group == "IgAN", "patient_id"].nunique()), "control_patients": int(ad.obs.loc[ad.obs.disease_group == "control", "patient_id"].nunique()), "celltypes": sorted(ad.obs.celltype.unique().tolist()), "pseudobulk_strata": int(len(pb_meta)), "min_cells_pseudobulk": a.min_cells_pseudobulk, "formal_UCell": True, "seed": a.seed}
    (out / "GSE127136_run_summary.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
