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

def run_scan():
    
    # Setup Paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    # Load Config
    config_path = os.path.join(project_root, "configs", "main_config.yaml")
    config = load_config(config_path)
    
    probes = ",".join(config["garak_settings"]["probes"])
    generations = str(config["garak_settings"].get("generations", 2))
    
    #Week 3: Run Garak scans for both targets A and B

    #For Target A: create unique run_id and directory structure for results Target A
    run_id = f"{str(probes)}_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    run_dir = os.path.join(project_root, "results", "Ablations", run_id, "A","raw")  
    os.makedirs(run_dir, exist_ok=True) 
    report_path_prefix_A = os.path.join(run_dir, "garak")   
    garak_config_path_A = os.path.join(project_root, "configs", "target_A_rest_config.json")    

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
    log_file = Path(run_dir) / "garak_stdout.log"
    with open(log_file, "w", encoding="utf-8") as log:
        subprocess.run(command_A, check=True, stdout=log, stderr=subprocess.STDOUT)

    #For Target B
    run_dir_B = os.path.join(project_root, "results","Ablations", run_id, "B","raw")  
    os.makedirs(run_dir_B, exist_ok=True) 
    report_path_prefix_patched = os.path.join(run_dir_B, "garak_patched")
    garak_config_path_B = os.path.join(project_root, "configs", "target_B_rest_config.json") 


    command_B= [
        sys.executable, "-m", "garak",
        "--target_type", "rest.RestGenerator",
        "-G", garak_config_path_B,
        "--probes", probes,
        "--generations", str(generations),
        "--report_prefix", str(report_path_prefix_patched),
    ] 
    # Capture stdout/stderr for debugging & audit
    log_file =  Path(run_dir_B) / "garak_stdout.log"
    with open(log_file, "w", encoding="utf-8") as log:
        subprocess.run(command_B, check=True, stdout=log, stderr=subprocess.STDOUT)
        
    print(f"Garak scan completed: {run_id}")

if __name__ == "__main__":
    run_scan()
