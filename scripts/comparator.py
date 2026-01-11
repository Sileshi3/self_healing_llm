import os
import pandas as pd
import yaml
from pathlib import Path

# Setup Paths
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
config_path = os.path.join(project_root, "configs", "config.yaml")

def _aggregate(df: pd.DataFrame, prefix: str) -> pd.DataFrame:
    """Aggregate counts by probe_id, category, outcome and prefix columns."""
    agg = (
        df
        .groupby(["probe_id", "category", "outcome"])
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )
    agg = agg.rename(
        columns={c: f"{prefix}_{c}" for c in agg.columns
                 if c not in ["probe_id", "category"]}
    )
    return agg

def compare_targets(a_path: str, b_path: str) -> pd.DataFrame:
    """Compare Target A vs Target B numerically, with % improvement for B."""
    df_a = pd.read_csv(a_path)  # run_id,target,probe_id,outcome,category [file:199]
    df_b = pd.read_csv(b_path)  # run_id,target,probe_id,outcome,category [file:200]

    agg_a = _aggregate(df_a, "A")
    agg_b = _aggregate(df_b, "B")

    merged = (
        pd.merge(agg_a, agg_b, on=["probe_id", "category"], how="outer")
        .fillna(0)
    )

    # Cast numeric outcome columns
    num_cols = [c for c in merged.columns if c.startswith(("A_", "B_"))]
    merged[num_cols] = merged[num_cols].astype(int)

    # Total attempts per probe/category
    merged["A_total"] = merged[[c for c in merged.columns if c.startswith("A_")]].sum(axis=1)
    merged["B_total"] = merged[[c for c in merged.columns if c.startswith("B_")]].sum(axis=1)

    # PASS rates and % improvement where PASS exists
    if "A_PASS" in merged.columns and "B_PASS" in merged.columns:
        merged["A_pass_rate (%)"] = round((merged["A_PASS"] / merged["A_total"].where(merged["A_total"] > 0, 1) *100), 2)
        merged["B_pass_rate (%)"] = round((merged["B_PASS"] / merged["B_total"].where(merged["B_total"] > 0, 1) *100), 2) 
        merged["Improvment (%)"] = merged["B_pass_rate (%)"] - merged["A_pass_rate (%)"] 
    return merged

if __name__ == "__main__":
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    run_report_path = config["comparison_settings"]["run_report_path"]
    run_id = Path(run_report_path).name

    result_A = os.path.join(project_root, "results", run_id, "A", "normalized", "normalized_summary.csv")
    result_B = os.path.join(project_root, "results", run_id, "B", "normalized", "normalized_summary.csv")

    comp = compare_targets(result_A, result_B)
    print(comp.head())

    out_path = os.path.join(project_root, "results", run_id, "Patch_success_comparison.csv")
    comp.to_csv(out_path, index=False)
