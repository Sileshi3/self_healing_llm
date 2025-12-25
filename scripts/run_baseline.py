import subprocess
import yaml
import sys
from pathlib import Path
from datetime import datetime
import uuid

def run_scan():
    # Load config
    with open("configs/config.yaml", "r") as f:
        config = yaml.safe_load(f)

    probes = ",".join(config["garak_settings"]["probes"])
    generations = str(config["garak_settings"].get("generations", 2))

    # Create run_id + directories
    run_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    run_dir = Path("results") / run_id / "raw"
    run_dir.mkdir(parents=True, exist_ok=True)

    #report_prefix = run_dir / "garak"

    print(f"Scanning Target A with probes: {probes}")
    print(f"Run ID: {run_id}")

    # command = [
    #     sys.executable, "-m", "garak",
    #     "--target_type", "rest.RestGenerator",
    #     "--target_name", "http://host.docker.internal:8000/generate",
    #     "-G", "configs/garak_rest_config.yaml",
    #     "--probes", probes,
    #     "--generations", generations,
    #     "--report", "json",
    #     "--report_prefix", str(run_dir),
    #     "--detectors", "promptinject.AttackRogueString,judge.Refusal,unsafe_content.LDNOOBW",
    # ]
    command = [
        sys.executable, "-m", "garak",
        "--target_type", "rest",
        "-G", "configs/garak_rest_config.json",
        "--probes", probes,
        "--generations", str(generations),
        "--report_prefix", str(run_dir),
    ]


    # Capture stdout/stderr for debugging & audit
    log_file = run_dir / "garak_stdout.log"
    with open(log_file, "w", encoding="utf-8") as log:
        subprocess.run(command, check=True, stdout=log, stderr=subprocess.STDOUT)

    print(f"Garak scan completed: {run_id}")

if __name__ == "__main__":
    run_scan()
