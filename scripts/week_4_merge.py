import pandas as pd
from pathlib import Path
import argparse

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, help="results/Ablations/<RUN_ID>")
    ap.add_argument("--out", default="week4_summary.csv")
    args = ap.parse_args()

    root = Path(args.root)
    rows = []

    # find all normalized_summary.csv files
    for csv_path in root.rglob("*normalized_summary.csv"):
        # infer condition + target from path (adjust if your folder naming differs)
        parts = csv_path.parts
        # expected: .../Ablations/RUN_ID/CX/(A|B)/.../target_X_normalized_summary.csv
        condition = next((p for p in parts if p.startswith("C")), "unknown")
        target = "A" if "target_A" in csv_path.name else ("B" if "target_B" in csv_path.name else "unknown")

        df = pd.read_csv(csv_path)
        df["condition"] = condition
        df["target"] = target
        df["source_file"] = str(csv_path)
        rows.append(df)

    if not rows:
        raise SystemExit(f"No normalized_summary.csv found under {root}")

    out_df = pd.concat(rows, ignore_index=True)
    out_df.to_csv(args.out, index=False)
    print(f"Wrote {args.out} with {len(out_df)} rows")

if __name__ == "__main__":
    main()
