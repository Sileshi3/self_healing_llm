# This script compares the normalized summary CSVs of Target A and Target B from a Garak run,
import os
import argparse
import pandas as pd
from pathlib import Path
import yaml 

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

def compare_targets(a_path: Path, b_path: Path) -> pd.DataFrame:
    """Compare Target A vs Target B numerically, with % improvement for B."""
    df_a = pd.read_csv(a_path)
    df_b = pd.read_csv(b_path)

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
        merged["A_pass_rate (%)"] = round(
            (merged["A_PASS"] / merged["A_total"].where(merged["A_total"] > 0, 1) * 100), 2
        )
        merged["B_pass_rate (%)"] = round(
            (merged["B_PASS"] / merged["B_total"].where(merged["B_total"] > 0, 1) * 100), 2
        )
        merged["Improvement (%)"] = merged["B_pass_rate (%)"] - merged["A_pass_rate (%)"]
    
    return merged


def main():
    parser = argparse.ArgumentParser(
        description="Compare Target A vs Target B from normalized Garak summaries",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    
    parser.add_argument('-r', '--path', required=True,
                        help='Path to the run directory containing A/ and B/ subdirs')
    
    parser.add_argument('-o', '--output',
                        help='Output CSV filename')
    
    parser.add_argument('--head', type=int,
                        default=10, help='Number of rows to preview')
    
    args = parser.parse_args()
    
    # Resolve paths
    run_dir = Path(args.path).resolve()
    if not run_dir.exists():
        print(f"Error: Run directory not found: {run_dir}")
        return 1
    
    result_A = run_dir / "A" / "normalized" / "normalized_summary.csv"
    result_B = run_dir / "B" / "normalized" / "normalized_summary.csv"
    
    if not result_A.exists():
        print(f"Error: Target A summary not found: {result_A}")
        print("Run garak_run_report_normalizer.py first")
        return 1
    
    if not result_B.exists():
        print(f"Error: Target B summary not found: {result_B}")
        print("Run garak_run_report_normalizer.py first")
        return 1
    
    # Compare
    print(f"\nComparing:")
    print(f"  Target A: {result_A}")
    print(f"  Target B: {result_B}")
    
    comp = compare_targets(result_A, result_B)
    
    # Preview
    if args.head > 0: 
        print(comp.head(args.head).to_string(index=False))
    
    # Save
    output_path = Path(args.output) if args.output else (run_dir / "patch_success_comparison.csv")
    comp.to_csv(output_path, index=False)
    
    print(f"\n Comparison saved: {output_path}")
    print(f"  Total probes compared: {len(comp)}")
    
    # Summary stats
    if "Improvement (%)" in comp.columns:
        avg_improvement = comp["Improvement (%)"].mean()
        print(f"  Average improvement: {avg_improvement:.2f}%")
    
    return 0


if __name__ == "__main__": 
    exit(main())
