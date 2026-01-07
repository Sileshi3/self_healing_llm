import subprocess
import yaml
import sys
from pathlib import Path
from datetime import datetime
import uuid
import os

def run_scan():
    
    # Setup Paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    # Load Config from configs/config.yaml
    config_path = os.path.join(project_root, "configs", "config.yaml")
    with open(config_path, "r") as f:
        config = yaml.safe_load(f) 
    
    probes = ",".join(config["garak_settings"]["probes"])
    generations = str(config["garak_settings"].get("generations", 2))
    
    #Week 3: Run Garak scans for both targets A and B
    # Create unique run_id and directory structure for results Target A
    run_id = f"{str(probes)}_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    run_dir = os.path.join(project_root, "results", run_id, "A","raw")  
    os.makedirs(run_dir, exist_ok=True)
    run_dir = Path(run_dir) 
    report_path_prefix = os.path.join(run_dir, "garak")  
    garak_config_path = os.path.join(project_root, "configs", "garak_rest_A.json")
    
    #For Target B
    run_dir_B = os.path.join(project_root, "results", run_id, "B","raw")  
    report_path_prefix_patched = os.path.join(run_dir_B, "garak_patched")
    os.makedirs(run_dir_B, exist_ok=True)
    run_dir_B = Path(run_dir_B)  
    garak_config_path_B = os.path.join(project_root, "configs", "garak_rest_B.json")
    
        #report_prefix = run_dir / "garak"
    # report_prefix = (run_dir / "garak").resolve()

    print(f"Scanning Target A with probes: {probes}")
    print(f"Run ID: {run_id}")

    command = [
        sys.executable, "-m", "garak",
        "--target_type", "rest.RestGenerator",
        "-G", garak_config_path,
        "--probes", probes,
        "--generations", str(generations),
        "--report_prefix", str(report_path_prefix),
    ] 
    # Capture stdout/stderr for debugging & audit
    log_file = run_dir / "garak_stdout.log"
    with open(log_file, "w", encoding="utf-8") as log:
        subprocess.run(command, check=True, stdout=log, stderr=subprocess.STDOUT)


    command_B= [
        sys.executable, "-m", "garak",
        "--target_type", "rest.RestGenerator",
        "-G", garak_config_path_B,
        "--probes", probes,
        "--generations", str(generations),
        "--report_prefix", str(report_path_prefix_patched),
    ] 
    # Capture stdout/stderr for debugging & audit
    log_file = run_dir_B / "garak_stdout.log"
    with open(log_file, "w", encoding="utf-8") as log:
        subprocess.run(command_B, check=True, stdout=log, stderr=subprocess.STDOUT)
        
    print(f"Garak scan completed: {run_id}")

if __name__ == "__main__":
    run_scan()
