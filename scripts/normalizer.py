import json
import csv
import yaml
import os
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
    with open("configs/config.yaml", "r") as f:
        config = yaml.safe_load(f) 
    run_id=config["normalize_setting"]["run_id"]
    target=config["normalize_setting"]["target"]
    # report_path=config["normalize_setting"]["report"]
    # out_dir=config["normalize_setting"]["out_dir"]
    # format=config["normalize_setting"]["format"]
    
    out_dir=f"results/normalized/{run_id}"
    
    # Check if the directory does NOT exist
    if not os.path.exists(out_dir): 
        os.makedirs(out_dir)
        
    summarize_jsonl(f"results/{run_id}/raw/garak.report.jsonl", 
                    f"{out_dir}/normalized_summary.csv", 
                    f"Target {target}")