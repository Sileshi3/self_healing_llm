
import os
import json
import sys  
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from itertools import chain
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
from src.core.config import load_config_json
from src.core.benign_regression_suit import (
    load_benign_suite,
    evaluate_response,
    call_target,
    )

print("=== Running Week 5 Benign Regression Suite ===")

garak_config_path_A = os.path.join(project_root, "configs", "target_A_rest_config.json")    
garak_config_path_B = os.path.join(project_root, "configs", "target_B_rest_config.json")    

# Load target endpoints from config files
target_a_config=load_config_json(garak_config_path_A)
target_b_config=load_config_json(garak_config_path_B)

TARGET_A_URI = target_a_config["rest"]["RestGenerator"]["uri"]
TARGET_B_URI = target_b_config["rest"]["RestGenerator"]["uri"]

BASE_DIR = Path(__file__).resolve().parent.parent
# PROMPT_TIMEOUT = float(os.getenv("PROMPT_TIMEOUT", "30"))

RESULTS_ROOT = BASE_DIR / "results" / "benign_suite"

def run_suite(target_conditions: List[str] = ["A", "B"]) -> pd.DataFrame:
    run_id = f"week5_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    run_dir = RESULTS_ROOT / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    prompts = load_benign_suite(BASE_DIR)

    all_results: List[Dict[str, Any]] = []
    for cond in target_conditions:
        endpoint = TARGET_A_URI if cond == "A" else TARGET_B_URI

        print(f"\nRunning benign suite for Condition {cond}")

        jsonl_path = run_dir / f"benign_{cond.lower()}.jsonl"
        cond_results: List[Dict[str, Any]] = []

        for i, prompt_data in enumerate(prompts):
            prompt_id = prompt_data["id"]
            request_id = f"{cond}-{prompt_id}-{i+1}"

            raw_result = call_target(endpoint, cond, prompt_data["prompt"], request_id=request_id)
            raw_result["prompt_id"] = prompt_id
            raw_result["category"] = prompt_data["category"]

            eval_result = evaluate_response(raw_result.get("response"), prompt_data["criteria"])
            full_result = {**raw_result, **eval_result}

            cond_results.append(full_result)

            with open(jsonl_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(full_result, ensure_ascii=False) + "\n")

        summary_df = pd.DataFrame(cond_results)
        summary_df["response_len"] = summary_df["response"].fillna("").astype(str).str.len()
        (run_dir / f"benign_{cond.lower()}_summary.csv").write_text(
            summary_df.to_csv(index=False), encoding="utf-8"
        )

        all_results.extend(cond_results)

    master_df = pd.DataFrame(all_results)
    if not master_df.empty:
        master_df["response_len"] = master_df["response"].fillna("").astype(str).str.len()

        overall = (
            master_df.groupby(["condition"])
            .agg(
                total=("pass", "count"),
                pass_rate=("pass", "mean"),
                # utility_preserved_rate=("utility_preserved", "mean"),
                refusal_rate=("is_refusal", "mean"),
                avg_len=("response_len", "mean"),
            )
            .round(4)
        )
        overall_path = run_dir / "benign_overall_rates.csv"
        overall.to_csv(overall_path)

        by_cat = (
            master_df.groupby(["condition", "category"])
            .agg(
                total=("pass", "count"),
                pass_rate=("pass", "mean"),
                # utility_preserved_rate=("utility_preserved", "mean"),
                refusal_rate=("is_refusal", "mean"),
                avg_len=("response_len", "mean"),
            )
            .round(4)
        )
        by_cat_path = run_dir / "benign_by_category_rates.csv"
        by_cat.to_csv(by_cat_path)

        print(f"\nSaved run outputs to: {run_dir}")
        print(f"- Overall rates: {overall_path.name}")
        print(f"- Category rates: {by_cat_path.name}\n")
        print(overall)

    return master_df


if __name__ == "__main__":
    # Run suite against both Target A and Target B
    df = run_suite(["A", "B"])
    if df.empty:
        print("\nNo results. Check endpoints/config.")
