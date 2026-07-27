from __future__ import annotations
from pathlib import Path
import argparse, gzip, json
import numpy as np
import pandas as pd
import yaml
from scipy.stats import mannwhitneyu, spearmanr
from sklearn.decomposition import PCA
import statsmodels.api as sm
from common import cliffs_delta, bh_fdr


def read_text(path: Path) -> str:
    if path.suffix == ".gz":
        with gzip.open(path, "rt", errors="replace") as f: return f.read()
    return path.read_text(errors="replace")


def parse_rcc(path: Path) -> pd.DataFrame:
    lines = read_text(path).splitlines()
    start = next(i for i, x in enumerate(lines) if x.startswith("CodeClass\tName\tAccession"))
    rows = [x.split("\t") for x in lines[start:] if x.strip()]
    df = pd.DataFrame(rows[1:], columns=rows[0])
    df["Count"] = pd.to_numeric(df["Count"], errors="coerce")
    return df


def gmean(x):
    x = np.asarray(x, float); x = x[np.isfinite(x) & (x > 0)]
    return float(np.exp(np.mean(np.log(x)))) if len(x) else np.nan


def exact_stats(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    return float(mannwhitneyu(a, b, alternative="two-sided", method="exact").pvalue)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--rcc-dir", required=True)
    p.add_argument("--metadata", required=True)
    p.add_argument("--signatures", default="config/rips_signatures.yml")
    p.add_argument("--outdir", default="results/gse220100")
    a = p.parse_args()
    out = Path(a.outdir); out.mkdir(parents=True, exist_ok=True)
    md = pd.read_csv(a.metadata)
    modules = yaml.safe_load(Path(a.signatures).read_text(encoding="utf-8"))["modules"]
    mat, qc_rows, codeclass_rows, hk_gene_counts = {}, [], [], {}
    for _, r in md.iterrows():
        d = parse_rcc(Path(a.rcc_dir) / r["file"])
        mat[r.sample_id] = d.set_index("Name")["Count"]
        cc = d.CodeClass.str.lower(); neg = d.loc[cc.eq("negative"), "Count"]; pos = d.loc[cc.eq("positive"), "Count"]; hk = d.loc[cc.eq("housekeeping"), ["Name", "Count"]]
        hk_gene_counts[r.sample_id] = hk.set_index("Name")["Count"]
        qc_rows.append({"sample_id": r.sample_id, "disease_group": r.disease_group, "tissue": r.tissue, "negative_mean": neg.mean(), "negative_sd": neg.std(ddof=0), "background_threshold": neg.mean() + 2 * neg.std(ddof=0), "positive_geo_mean": gmean(pos), "housekeeping_geo_mean": gmean(hk.Count), "n_endogenous": int(cc.eq("endogenous").sum()), "n_housekeeping": int(cc.eq("housekeeping").sum()), "n_positive": int(cc.eq("positive").sum()), "n_negative": int(cc.eq("negative").sum())})
        for c, n in d.CodeClass.value_counts().items(): codeclass_rows.append({"sample_id": r.sample_id, "CodeClass": c, "n_rows": int(n)})
    counts = pd.DataFrame(mat).fillna(0.0)
    qc = pd.DataFrame(qc_rows).set_index("sample_id")
    qc["positive_factor"] = qc.positive_geo_mean.median() / qc.positive_geo_mean
    qc["housekeeping_factor"] = qc.housekeeping_geo_mean.median() / qc.housekeeping_geo_mean
    qc["log2_housekeeping_geo_mean"] = np.log2(qc.housekeeping_geo_mean)
    qc.reset_index().to_csv(out / "GSE220100_NanoString_QC.csv", index=False)
    pd.DataFrame(codeclass_rows).to_csv(out / "GSE220100_RCC_codeclass_counts.csv", index=False)
    strategies = {"raw_log2": np.log2(counts + 1.0)}
    bg = counts.copy()
    for s in bg.columns: bg[s] = np.maximum(bg[s] - qc.loc[s, "background_threshold"], 1.0)
    strategies["background_only"] = np.log2(bg)
    pos = bg.mul(qc.positive_factor, axis=1); strategies["background_positive"] = np.log2(pos)
    ph = pos.mul(qc.housekeeping_factor, axis=1); strategies["background_positive_housekeeping"] = np.log2(ph)
    mdk = md[(md.tissue.str.lower() == "kidney") & md.disease_group.isin(["IgAN", "IgAVN"])].set_index("sample_id")
    igan_samples = mdk.index[mdk.disease_group == "IgAN"].tolist(); igavn_samples = mdk.index[mdk.disease_group == "IgAVN"].tolist()
    panel_genes = set(counts.index.astype(str)); coverage_rows = []
    for module, genes in modules.items():
        detected = [g for g in genes if g in panel_genes]
        coverage_rows.append({"module": module, "requested_n": len(genes), "detected_n": len(detected), "coverage_fraction": len(detected)/len(genes), "detected_genes": ";".join(detected), "missing_genes": ";".join([g for g in genes if g not in panel_genes])})
    pd.DataFrame(coverage_rows).to_csv(out / "GSE220100_module_gene_coverage.csv", index=False)
    stats_rows, gene_rows, pca_rows, model_rows, cook_rows, score_tables = [], [], [], [], [], {}
    restricted_modules = ["Inflammatory_chemotaxis", "Complement", "Endothelial_activation"]
    for strategy, expr in strategies.items():
        x = expr.loc[:, mdk.index]
        z = x.sub(x.mean(axis=1), axis=0).div(x.std(axis=1, ddof=0).replace(0, np.nan), axis=0)
        module_scores = {}
        for module in restricted_modules:
            genes = [g for g in modules[module] if g in z.index]
            module_scores[module] = z.loc[genes].mean(axis=0)
        sdf = pd.DataFrame(module_scores); sdf["restricted_RIPS"] = sdf.mean(axis=1); sdf["disease_group"] = mdk.disease_group; sdf["housekeeping_geo_mean"] = qc.loc[sdf.index, "housekeeping_geo_mean"]
        sdf.to_csv(out / f"GSE220100_scores_{strategy}.csv"); score_tables[strategy] = sdf
        for metric in restricted_modules + ["restricted_RIPS"]:
            igan = sdf.loc[igan_samples, metric].to_numpy(); igavn = sdf.loc[igavn_samples, metric].to_numpy()
            stats_rows.append({"normalization_strategy": strategy, "metric": metric, "IgAN_n": len(igan), "IgAVN_n": len(igavn), "IgAN_median": np.median(igan), "IgAVN_median": np.median(igavn), "delta_IgAN_minus_IgAVN": np.median(igan) - np.median(igavn), "mann_whitney_exact_p": exact_stats(igan, igavn), "cliffs_delta_IgAN_vs_IgAVN": cliffs_delta(igan, igavn)})
        for gene in x.index:
            igan = x.loc[gene, igan_samples].to_numpy(); igavn = x.loc[gene, igavn_samples].to_numpy()
            gene_rows.append({"strategy": strategy, "gene": gene, "median_IgAN": np.median(igan), "median_IgAVN": np.median(igavn), "median_difference_IgAN_minus_IgAVN": np.median(igan) - np.median(igavn), "raw_p": exact_stats(igan, igavn), "cliffs_delta_IgAN_vs_IgAVN": cliffs_delta(igan, igavn)})
        pca_input = x.T.loc[:, x.std(axis=1, ddof=0) > 0]; pca = PCA(n_components=2, random_state=20260727); pcs = pca.fit_transform(pca_input)
        for i, sid in enumerate(pca_input.index): pca_rows.append({"strategy": strategy, "sample_id": sid, "disease_group": mdk.loc[sid, "disease_group"], "PC1": pcs[i,0], "PC2": pcs[i,1], "PC1_variance": pca.explained_variance_ratio_[0], "PC2_variance": pca.explained_variance_ratio_[1], "log2_housekeeping_geo_mean": qc.loc[sid, "log2_housekeeping_geo_mean"]})
        y = sdf["restricted_RIPS"].astype(float)
        X = pd.DataFrame({"IgAN_indicator": (sdf.disease_group == "IgAN").astype(int), "log2_housekeeping_geo_mean": qc.loc[sdf.index, "log2_housekeeping_geo_mean"].astype(float)}, index=sdf.index)
        X = sm.add_constant(X); fit = sm.OLS(y, X).fit()
        for term in fit.params.index: model_rows.append({"strategy": strategy, "term": term, "beta": fit.params[term], "standard_error": fit.bse[term], "p_value": fit.pvalues[term], "n": int(fit.nobs), "r_squared": fit.rsquared})
        influence = fit.get_influence()
        for sid, cook in zip(sdf.index, influence.cooks_distance[0]): cook_rows.append({"strategy": strategy, "sample_id": sid, "cooks_distance": cook, "high_leverage_threshold_4_over_n": 4/len(sdf), "flag_above_4_over_n": bool(cook > 4/len(sdf))})
    stats = pd.DataFrame(stats_rows); stats["FDR_modules_only_within_strategy"] = np.nan
    for strategy, idx in stats.groupby("normalization_strategy").groups.items():
        module_idx = [i for i in idx if stats.loc[i, "metric"] != "restricted_RIPS"]
        stats.loc[module_idx, "FDR_modules_only_within_strategy"] = bh_fdr(stats.loc[module_idx, "mann_whitney_exact_p"].to_numpy())
    stats["FDR_all_metrics_within_strategy"] = stats.groupby("normalization_strategy")["mann_whitney_exact_p"].transform(lambda x: bh_fdr(x.to_numpy()))
    stats.to_csv(out / "GSE220100_normalization_sensitivity.csv", index=False)
    genes = pd.DataFrame(gene_rows); genes["FDR_within_strategy"] = genes.groupby("strategy")["raw_p"].transform(lambda x: bh_fdr(x.to_numpy()))
    focus = ["CCL5","CCR2","CXCR3","ITGAL","CFB","C1QA","BCL2","STAT2","TAPBP","PSMB10"]
    genes["predefined_focus_gene"] = genes.gene.isin(focus); genes.to_csv(out / "GSE220100_gene_statistics.csv", index=False); genes[genes.predefined_focus_gene].to_csv(out / "GSE220100_focus_gene_statistics.csv", index=False)
    pd.DataFrame(pca_rows).to_csv(out / "GSE220100_PCA_diagnostics.csv", index=False); pd.DataFrame(model_rows).to_csv(out / "GSE220100_housekeeping_diagnostic_models.csv", index=False); pd.DataFrame(cook_rows).to_csv(out / "GSE220100_Cooks_distance.csv", index=False)
    hk_mat = pd.DataFrame(hk_gene_counts).loc[:, mdk.index]; hk_rows = []
    for gene in hk_mat.index:
        vals = hk_mat.loc[gene].astype(float); igan = vals[igan_samples].to_numpy(); igavn = vals[igavn_samples].to_numpy()
        hk_rows.append({"gene": gene, "mean_count": vals.mean(), "sd_count": vals.std(ddof=0), "CV": vals.std(ddof=0)/vals.mean() if vals.mean() else np.nan, "median_difference_IgAN_minus_IgAVN": np.median(igan)-np.median(igavn), "raw_p": exact_stats(igan, igavn)})
    hk_stats = pd.DataFrame(hk_rows); hk_stats["FDR"] = bh_fdr(hk_stats.raw_p.to_numpy()); hk_stats.to_csv(out / "GSE220100_housekeeping_gene_stability.csv", index=False)
    rho, rho_p = spearmanr(qc.loc[mdk.index, "log2_housekeeping_geo_mean"], score_tables["background_positive_housekeeping"].restricted_RIPS)
    direction_map = stats[stats.metric == "restricted_RIPS"].set_index("normalization_strategy")["delta_IgAN_minus_IgAVN"].to_dict()
    report = {"kidney_IgAN_n": len(igan_samples), "kidney_IgAVN_n": len(igavn_samples), "normalization_strategies": list(strategies), "restricted_modules": restricted_modules, "restricted_RIPS_directions_IgAN_minus_IgAVN": direction_map, "direction_reversal_present": bool(min(direction_map.values()) < 0 < max(direction_map.values())), "housekeeping_vs_restricted_RIPS_spearman_rho_under_full_normalization": float(rho), "housekeeping_vs_restricted_RIPS_spearman_p": float(rho_p), "formal_interpretation": "Normalization-sensitivity audit; no stable disease-difference claim if direction changes across plausible strategies."}
    (out / "GSE220100_run_summary.json").write_text(json.dumps(report, indent=2), encoding="utf-8"); print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
