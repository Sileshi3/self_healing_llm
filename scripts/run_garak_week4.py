import subprocess
import yaml
import sys
from pathlib import Path
from datetime import datetime
import uuid
import os
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
from src.core.config import load_config
from garak_run_report_normalizer import summarize_jsonl
from scripts.ablation_comparator import compare_targets

def run_scan(project_root):
      
    probes = ",".join(config["garak_settings"]["probes"])
    generations = str(config["garak_settings"].get("generations", 2))
    
    #Week 3: Run Garak scans for both targets A and B

    #For Target A
    # Create unique run_id and directory structure for results Target A
    run_id = f"{str(probes)}_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    run_dir = os.path.join(project_root, "results", "Ablations", run_id, "A","raw")  
    os.makedirs(run_dir, exist_ok=True) 
    report_path_prefix_A = os.path.join(run_dir, "garak")   
    garak_config_path_A = os.path.join(project_root, "configs", "target_A_rest_config.json")    

    #For Target B
    run_dir_B = os.path.join(project_root, "results\\Ablations", run_id, "B","raw")  
    os.makedirs(run_dir_B, exist_ok=True) 
    report_path_prefix_patched = os.path.join(run_dir_B, "garak_patched")
    garak_config_path_B = os.path.join(project_root, "configs", "target_B_rest_config.json") 
    run_path=os.path.join(project_root, "results\\Ablations", run_id)

    print(f"Scanning Target A with probes: {probes}")
    print(f"Run ID: {run_id}")

    command_A = [
        sys.executable, "-m", "garak", 
        "--target_type", "rest.RestGenerator",
        "-G", garak_config_path_A,
        "--probes", probes,
        "--generations", str(generations),
        "--report_prefix", str(report_path_prefix_A),
    ] 

    # Capture stdout/stderr for debugging & audit
    # log_file = Path(run_dir) / "garak_stdout.log"
    # with open(log_file, "w", encoding="utf-8") as log:
    #     subprocess.run(command_A, check=True, stdout=log, stderr=subprocess.STDOUT)

    command_B= [sys.executable, "-m", "garak",
                "--target_type", "rest.RestGenerator",
                "-G", garak_config_path_B,
                "--probes", probes,
                "--generations", str(generations),
                # "--parallel_requests", "4",
                "--report_prefix", str(report_path_prefix_patched),
        ] 
    # Capture stdout/stderr for debugging & audit
    log_file =  Path(run_dir_B) / "garak_stdout.log"
    with open(log_file, "w", encoding="utf-8") as log:
        subprocess.run(command_B, check=True, stdout=log, stderr=subprocess.STDOUT)
        
    print(f"Garak scan completed: {run_id}")
    return run_path

def normalizer(run_path,project_root): 
    run_report_path=run_path 
    target= 'both'   
    out_dir=os.path.join(project_root,run_report_path) 
    path_A=os.path.join(out_dir,f"A\\normalized")
    path_B=os.path.join(out_dir,f"B\\normalized") 
    os.makedirs(path_A, exist_ok=True)
    os.makedirs(path_B, exist_ok=True)
     
    if target=="A": 
        summarize_jsonl(os.path.join(project_root, f"{out_dir}/{target}/raw/garak.report.jsonl"), 
                    os.path.join(path_A, "normalized_summary.csv"), 
                    f"Target {target}")
    if target=="B": 
        summarize_jsonl(os.path.join(project_root, f"{out_dir}/{target}/raw/garak_patched.report.jsonl"), 
                    os.path.join(path_B, "normalized_summary.csv"), 
                    f"Target {target}")
    if target=='both':
        summarize_jsonl(os.path.join(project_root, f'{out_dir}/A/raw/garak.report.jsonl'), 
                    os.path.join(path_A,'normalized_summary.csv'), 
                    "Target A") 
        summarize_jsonl(os.path.join(project_root, f"{out_dir}/B/raw/garak_patched.report.jsonl"), 
                    os.path.join(path_B, "normalized_summary.csv"), 
                    "Target B")
    if target not in ["A","B","both"]:
        raise ValueError("Target must be either A or B")

def comparator(run_report_path): 

    result_A = os.path.join(project_root, run_report_path, "A", "normalized", "normalized_summary.csv")
    result_B = os.path.join(project_root, run_report_path, "B", "normalized", "normalized_summary.csv")
    # print(project_root)
    print(os.path.join(project_root,run_report_path))
    comp = compare_targets(result_A, result_B)
    print(comp.head())

    out_path = os.path.join(project_root, run_report_path, "Patch_success_comparison.csv")
    comp.to_csv(out_path, index=False)

if __name__ == "__main__":
    # Setup Paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    # Load Config
    config_path = os.path.join(project_root, "configs", "main_config.yaml") 
    config = load_config(config_path)
    
    # For run garak scans
    run_path=run_scan(project_root)

    # For normalizing garak reports
    normalizer(run_path,project_root)

    # For comparing the normalized results between target A and B
    comparator(run_path)
