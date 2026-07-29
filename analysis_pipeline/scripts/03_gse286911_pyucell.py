from __future__ import annotations
from pathlib import Path
import argparse, json, yaml
import numpy as np
import pandas as pd
import scanpy as sc
from pyucell import compute_ucell_scores
from common import exact_mwu, cliffs_delta, bh_fdr


def coverage_table(var_names, modules):
    rows = []
    geneset = set(map(str, var_names))
    for module, genes in modules.items():
        detected = [g for g in genes if g in geneset]
        rows.append({"module": module, "requested_n": len(genes), "detected_n": len(detected), "coverage_fraction": len(detected) / len(genes) if genes else np.nan, "detected_genes": ";".join(detected), "missing_genes": ";".join([g for g in genes if g not in geneset])})
    return pd.DataFrame(rows)


def selection_indices(ad, mode, n, seed):
    n_use = min(n, ad.n_obs)
    if mode == "all_qc": return np.arange(ad.n_obs)
    if mode == "top_umi": return np.argsort(-ad.obs.total_counts.to_numpy())[:n_use]
    if mode == "random_downsample": return np.random.default_rng(seed).choice(ad.n_obs, n_use, replace=False)
    raise ValueError(mode)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--root", required=True)
    p.add_argument("--signatures", default="config/rips_signatures.yml")
    p.add_argument("--outdir", default="results/gse286911")
    p.add_argument("--min-genes", type=int, default=200)
    p.add_argument("--max-genes", type=int, default=8000)
    p.add_argument("--max-mito", type=float, default=20)
    p.add_argument("--downsample-n", type=int, default=5000)
    p.add_argument("--seeds", default="11,23,37,51,73")
    a = p.parse_args()
    root = Path(a.root); out = Path(a.outdir); out.mkdir(parents=True, exist_ok=True)
    modules = yaml.safe_load(Path(a.signatures).read_text(encoding="utf-8"))["modules"]
    seeds = [int(x) for x in a.seeds.split(",")]
    sample_rows, qc_rows, module_rows, coverage_frames = [], [], [], []
    for sid in ["Le1", "Le2", "Le3", "Ne1", "Ne2", "Ne3"]:
        ad = sc.read_10x_mtx(root / sid, var_names="gene_symbols", make_unique=True, cache=False)
        input_n = ad.n_obs
        ad.var["mt"] = ad.var_names.str.upper().str.startswith("MT-")
        sc.pp.calculate_qc_metrics(ad, qc_vars=["mt"], inplace=True, percent_top=None)
        ad = ad[(ad.obs.n_genes_by_counts >= a.min_genes) & (ad.obs.n_genes_by_counts <= a.max_genes) & (ad.obs.pct_counts_mt <= a.max_mito)].copy()
        group = "low-eGFR" if sid.startswith("Le") else "normal-eGFR"
        qc_rows.append({"sample_id": sid, "clinical_group": group, "input_nuclei": input_n, "qc_nuclei": ad.n_obs, "median_genes": float(ad.obs.n_genes_by_counts.median()), "median_UMI": float(ad.obs.total_counts.median()), "median_pct_mito": float(ad.obs.pct_counts_mt.median())})
        cov = coverage_table(ad.var_names, modules); cov.insert(0, "sample_id", sid); coverage_frames.append(cov)
        compute_ucell_scores(ad, modules, max_rank=min(1500, ad.n_vars), missing_genes="skip", n_jobs=1, device="cpu")
        module_cols = [f"{m}_UCell" for m in modules]
        ad.obs["RIPS_UCell"] = ad.obs[module_cols].mean(axis=1)
        selections = [("all_qc", None), ("top_umi", None)] + [("random_downsample", s) for s in seeds]
        for mode, seed in selections:
            idx = selection_indices(ad, mode, a.downsample_n, seed)
            vals = ad.obs.iloc[idx]
            base = {"sample_id": sid, "clinical_group": group, "selection_mode": mode, "seed": seed, "selected_nuclei": len(idx), "median_RIPS_UCell": float(vals.RIPS_UCell.median()), "mean_RIPS_UCell": float(vals.RIPS_UCell.mean())}
            sample_rows.append(base)
            for module, col in zip(modules, module_cols):
                module_rows.append({**{k: base[k] for k in ["sample_id", "clinical_group", "selection_mode", "seed", "selected_nuclei"]}, "module": module, "median_module_UCell": float(vals[col].median()), "mean_module_UCell": float(vals[col].mean())})
        del ad
    scores = pd.DataFrame(sample_rows); modules_df = pd.DataFrame(module_rows); qc = pd.DataFrame(qc_rows); coverage = pd.concat(coverage_frames, ignore_index=True)
    scores.to_csv(out / "GSE286911_sample_UCell_scores.csv", index=False)
    modules_df.to_csv(out / "GSE286911_sample_module_UCell_scores.csv", index=False)
    qc.to_csv(out / "GSE286911_sample_QC.csv", index=False)
    coverage.to_csv(out / "GSE286911_module_gene_coverage_by_sample.csv", index=False)
    summary_rows = []
    for (mode, seed), g in scores.groupby(["selection_mode", "seed"], dropna=False):
        lo = g.loc[g.clinical_group == "low-eGFR", "median_RIPS_UCell"].to_numpy(); no = g.loc[g.clinical_group == "normal-eGFR", "median_RIPS_UCell"].to_numpy()
        summary_rows.append({"selection_mode": mode, "seed": seed, "metric": "RIPS_UCell", "normal_values": ";".join(map(str, no)), "low_values": ";".join(map(str, lo)), "normal_median": np.median(no), "low_median": np.median(lo), "delta_low_minus_normal": np.median(lo) - np.median(no), "mann_whitney_exact_p": exact_mwu(lo, no), "cliffs_delta_low_vs_normal": cliffs_delta(lo, no), "complete_rank_separation": bool(np.min(lo) > np.max(no) or np.max(lo) < np.min(no)), "design_minimum_two_sided_exact_p": 0.10})
        mg = modules_df[(modules_df.selection_mode == mode) & (modules_df.seed.fillna(-1) == (-1 if pd.isna(seed) else seed))]
        for module, gg in mg.groupby("module"):
            lo_m = gg.loc[gg.clinical_group == "low-eGFR", "median_module_UCell"].to_numpy(); no_m = gg.loc[gg.clinical_group == "normal-eGFR", "median_module_UCell"].to_numpy()
            summary_rows.append({"selection_mode": mode, "seed": seed, "metric": module, "normal_values": ";".join(map(str, no_m)), "low_values": ";".join(map(str, lo_m)), "normal_median": np.median(no_m), "low_median": np.median(lo_m), "delta_low_minus_normal": np.median(lo_m) - np.median(no_m), "mann_whitney_exact_p": exact_mwu(lo_m, no_m), "cliffs_delta_low_vs_normal": cliffs_delta(lo_m, no_m), "complete_rank_separation": bool(np.min(lo_m) > np.max(no_m) or np.max(lo_m) < np.min(no_m)), "design_minimum_two_sided_exact_p": 0.10})
    summary = pd.DataFrame(summary_rows)
    summary["FDR_within_selection"] = summary.groupby(["selection_mode", "seed"], dropna=False)["mann_whitney_exact_p"].transform(lambda x: bh_fdr(x.to_numpy()))
    summary.to_csv(out / "GSE286911_UCell_sensitivity.csv", index=False)
    report = {"independent_units": 6, "units_per_group": 3, "unit_type": "pooled sequencing libraries", "formal_UCell": True, "selection_modes": ["all_qc", "top_umi", "random_downsample"], "random_seeds": seeds, "downsample_n": a.downsample_n, "minimum_attainable_two_sided_exact_Mann_Whitney_p": 0.10, "qc_total_nuclei": int(qc.qc_nuclei.sum())}
    (out / "GSE286911_run_summary.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
