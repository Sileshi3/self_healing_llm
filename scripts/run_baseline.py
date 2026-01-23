import subprocess
import sys
from pathlib import Path
from datetime import datetime
import uuid
import os
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
    
    # Create unique run_id and directory structure 
    run_id = f"{str(probes)}_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    run_dir = os.path.join(project_root, "results", run_id, "raw")  
    os.makedirs(run_dir, exist_ok=True)
    run_dir = Path(run_dir)
    
    # Define the Garak report prefix Garak will add extensions like .report.jsonl and .report.html to this
    report_path_prefix = os.path.join(run_dir, "garak")  
    garak_config_path = os.path.join(project_root, "configs", "garak_rest_config.json")
    
    
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

    print(f"Garak scan completed: {run_id}")

if __name__ == "__main__":
    run_scan()
