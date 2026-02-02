import json
import csv
import argparse
from pathlib import Path


def summarize_jsonl(input_file, output_csv, target_label):
    summary_data = []
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            entry = json.loads(line)
            
            if entry.get("entry_type") == "attempt":
                detectors = entry.get("detector_results", {}) 
                is_hit = any(
                    (s > 0 if isinstance(s, (int, float)) else any(x > 0 for x in s))
                    for s in detectors.values()
                )
                
                summary_data.append({
                    "run_id": entry.get("uuid"),
                    "target": target_label,
                    "probe_id": entry.get("probe_classname"),
                    "outcome": "FAIL (HIT)" if is_hit else "PASS",
                    "category": entry.get("probe_classname").split('.')[0]
                })

    if not summary_data:
        print(f"Warning: No attempt entries found in {input_file}")
        return

    with open(output_csv, 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=summary_data[0].keys())
        dict_writer.writeheader()
        dict_writer.writerows(summary_data)
    
    print(f" Normalized summary saved: {output_csv}")


def main():
    parser = argparse.ArgumentParser(description="Normalize Garak JSONL reports into CSV summaries",
                                     formatter_class=argparse.RawDescriptionHelpFormatter ) 
    parser.add_argument('-r', '--path',
                        required=True,
                        help='Path to the garak log directory'
                        )
    
    parser.add_argument('-t', '--target',
                        choices=['A', 'B', 'both'],
                        default='both',
                        help='Which target(s) log to normalize (default: both)'
    )
    
    args = parser.parse_args()
    
    # Resolve paths
    run_dir = Path(args.path).resolve()
    if not run_dir.exists():
        print(f"Error: Run directory not found: {run_dir}")
        return 1
    
    # Process targets
    targets_to_process = ['A', 'B'] if args.target == 'both' else [args.target]
    
    for target in targets_to_process:
        raw_file = run_dir / target / "raw" / (
            "garak.report.jsonl" if target == "A" else "garak_patched.report.jsonl")
        
        if not raw_file.exists():
            print(f"Warning: {raw_file} not found, skipping Target {target}")
            continue
        
        # Create output directory
        norm_dir = run_dir / target / "normalized"
        norm_dir.mkdir(parents=True, exist_ok=True)
        
        output_csv = norm_dir / "normalized_summary.csv"
        
        print(f"\nProcessing Target {target}...")
        summarize_jsonl(raw_file, output_csv, f"Target {target}")
    
    print("\n Normalization complete!")
    return 0


if __name__ == "__main__":
    exit(main())

