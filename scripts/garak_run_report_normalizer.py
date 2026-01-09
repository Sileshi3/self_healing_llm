import json
import csv
from pathlib import Path
import yaml
import os


# Setup Paths
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
config_path = os.path.join(project_root, "configs", "config.yaml") 

def summarize_jsonl(input_file, output_csv, target_label):
    summary_data = []
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            entry = json.loads(line)
            
            # Only process 'attempt' entries (skip 'start_run', 'init', etc.)
            if entry.get("entry_type") == "attempt":
                # Check for a HIT: Is there any detector result > 0?
                detectors = entry.get("detector_results", {}) 
                is_hit = False
                for score in detectors.values():
                    if isinstance(score, list):
                        if any(s > 0 for s in score):
                            is_hit = True
                            break
                    elif score > 0:
                        is_hit = True
                        break
                summary_data.append({
                    "run_id": entry.get("uuid"),
                    "target": target_label,
                    "probe_id": entry.get("probe_classname"),
                    "outcome": "FAIL (HIT)" if is_hit else "PASS",
                    "category": entry.get("probe_classname").split('.')[0]
                })

    # Write to CSV
    keys = summary_data[0].keys()
    with open(output_csv, 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(summary_data)
    
    print(f"Normalized summary saved on: {output_csv}")
    
if __name__=="__main__":
    print(project_root)
    with open(config_path, "r") as f:
        config = yaml.safe_load(f) 
    run_report_path=config["normalize_setting"]["run_report_path"]
    target=config["normalize_setting"]["target"]

    run_id = Path(run_report_path).name  
    out_dir=os.path.join(project_root,f"results/{run_id}/{target}/normalized")
    

    # Check if the directory does NOT exist
    if not os.path.exists(out_dir): 
        os.makedirs(out_dir)   
    if target=="A": 
        summarize_jsonl(os.path.join(project_root, f"results/{run_id}/{target}/raw/garak.report.jsonl"), 
                    os.path.join(out_dir, "normalized_summary.csv"), 
                    f"Target {target}")
    if target=="B": 
        summarize_jsonl(os.path.join(project_root, f"results/{run_id}/{target}/raw/garak_patched.report.jsonl"), 
                    os.path.join(out_dir, "normalized_summary.csv"), 
                    f"Target {target}")
    if target not in ["A","B"]:
        raise ValueError("Target must be either A or B")
    
   