import yaml
import subprocess
import uuid
from pathlib import Path
from datetime import datetime
import sys

CONFIG_PATH = "configs/garak_baseline.yaml"

def main():
    with open(CONFIG_PATH, "r") as f:
        cfg = yaml.safe_load(f)

    run_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    run_dir = Path(cfg["run"]["output_dir"]) / run_id
    raw_dir = run_dir / "raw"

    raw_dir.mkdir(parents=True, exist_ok=True)

    report_prefix = raw_dir / "garak"
    cmd = [
        sys.executable, "-m", "garak",
        "--config", CONFIG_PATH,
        "--report_prefix", str(report_prefix)
    ]

    subprocess.run(cmd, check=True)

    print(f"Garak run completed: {run_id}")

if __name__ == "__main__":
    main()
