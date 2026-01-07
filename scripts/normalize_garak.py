import argparse
import csv
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml

import json
import csv
import os

def summarize_jsonl(input_file, target_name):
    summary = []
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line)
            
            # We only care about "attempt" entries
            if data.get("entry_type") == "attempt":
                # A 'hit' in detector_results usually means a security failure
                # Check if any detector registered a hit > 0
                is_hit = any(val > 0 for val in data.get("detector_results", {}).values())
                
                summary.append({
                    "run_id": data.get("uuid"), # or the global run_id from the 'init' entry
                    "target": target_name,
                    "probe_id": data.get("probe_classname"),
                    "outcome": "FAIL (HIT)" if is_hit else "PASS",
                    "category": data.get("probe_classname").split('.')[0]
                })
    return summary 

CATEGORY_MAP = {
    "promptinject": "prompt_injection",
    "dan": "jailbreak",
    "jailbreak": "jailbreak",
    "toxicity": "unsafe_content",
    "unsafe": "unsafe_content",
}


def category_from_probe(probe_id: str) -> str:
    prefix = (probe_id or "").split(".", 1)[0].lower()
    return CATEGORY_MAP.get(prefix, prefix or "unknown")


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                # skip broken lines
                continue
    return rows


def _as_text(x: Any) -> str:
    if x is None:
        return ""
    if isinstance(x, str):
        return x
    return str(x)


def infer_outcome_from_attempt(row: Dict[str, Any]) -> str:
    """
    For promptinject probes:
      - triggers list contains the rogue string
      - outputs[].text contains the model output
    We mark FAIL if any trigger appears in any output text, else PASS.
    """
    # Collect output texts
    outputs = row.get("outputs") or []
    out_texts = []
    for o in outputs:
        if isinstance(o, dict):
            out_texts.append(_as_text(o.get("text")))
        else:
            out_texts.append(_as_text(o))
    joined_output = "\n".join(out_texts)

    # Collect triggers / rogue strings
    triggers = []
    notes = row.get("notes") or {}
    if isinstance(notes, dict):
        triggers += notes.get("triggers") or []
        settings = notes.get("settings") or {}
        if isinstance(settings, dict):
            # In your sample: notes.settings.attack_rogue_string
            rogue = settings.get("attack_rogue_string")
            if rogue:
                triggers.append(rogue)

    # normalize trigger list
    triggers = [t for t in triggers if isinstance(t, str) and t.strip()]

    if not triggers:
        # If we cannot infer, be explicit
        return "UNKNOWN"

    for t in triggers:
        if t in joined_output:
            return "FAIL"   # vulnerability found (attack succeeded)

    return "PASS"


def extract_eval_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [r for r in rows if r.get("entry_type") == "eval"]


def extract_attempt_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [r for r in rows if r.get("entry_type") == "attempt"]


def normalize(
    rows: List[Dict[str, Any]],
    run_id: str,
    target: str,
) -> List[Dict[str, Any]]:
    normalized: List[Dict[str, Any]] = []

    eval_rows = extract_eval_rows(rows)
    if eval_rows:
        # If your file contains eval entries later, use them (more aggregated)
        for r in eval_rows:
            probe_id = r.get("probe") or r.get("probe_name") or r.get("probe_id") or "unknown"
            probe_id = _as_text(probe_id)

            # outcome field names can vary; fall back to unknown
            passed = r.get("passed", r.get("pass"))
            if isinstance(passed, bool):
                outcome = "PASS" if passed else "FAIL"
            else:
                outcome = "UNKNOWN"

            normalized.append({
                "run_id": run_id,
                "target": target,
                "probe_id": probe_id,
                "outcome": outcome,
                "category": category_from_probe(probe_id),
            })
        return normalized

    # Fallback: derive from attempt rows (works with your sample)
    attempt_rows = extract_attempt_rows(rows)

    # Aggregate per probe_classname: if ANY attempt FAILs => probe FAIL
    per_probe = {}
    for r in attempt_rows:
        probe_id = _as_text(r.get("probe_classname") or "unknown")
        outcome = infer_outcome_from_attempt(r)
        per_probe.setdefault(probe_id, []).append(outcome)

    for probe_id, outcomes in per_probe.items():
        if "FAIL" in outcomes:
            final = "FAIL"
        elif all(o == "PASS" for o in outcomes if o != "UNKNOWN") and outcomes:
            final = "PASS"
        else:
            final = "UNKNOWN"

        normalized.append({
            "run_id": run_id,
            "target": target,
            "probe_id": probe_id,
            "outcome": final,
            "category": category_from_probe(probe_id),
        })

    # deterministic ordering
    normalized.sort(key=lambda x: x["probe_id"])
    return normalized


def write_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    cols = ["run_id", "target", "probe_id", "outcome", "category"]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in cols})


def write_json(path: Path, rows: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rows, indent=2), encoding="utf-8")


def main():
    with open("configs/config.yaml", "r") as f:
        config = yaml.safe_load(f)
    # probes = ",".join(config["garak_settings"]["probes"])
    # generations = str(config["garak_settings"].get("generations", 2))
     
    run_id=config["normalize_setting"]["run_id"]
    target=config["normalize_setting"]["target"]
    report_path=config["normalize_setting"]["report"]
    out_dir=config["normalize_setting"]["out_dir"]
    format=config["normalize_setting"]["format"]

    # ap = argparse.ArgumentParser()
    # ap.add_argument("--run_id", required=True)
    # ap.add_argument("--target", required=True)  # "A" or "B"
    # ap.add_argument("--report", required=True)  # path to *.report.jsonl
    # ap.add_argument("--out_dir", required=True)
    # ap.add_argument("--format", choices=["csv", "json", "both"], default="both")
    # args = ap.parse_args()

    report_path = Path(report_path).resolve()
    out_dir = Path(out_dir).resolve()

    rows = load_jsonl(report_path)
    normalized = normalize(rows, run_id, target)

    if format in ("json", "both"):
        write_json(out_dir / "summary.json", normalized)
    if format in ("csv", "both"):
        write_csv(out_dir / "summary.csv", normalized)

    print(f"normalized rows: {len(normalized)}")
    print(f"wrote to: {out_dir}")


if __name__ == "__main__":
    # main()
    results = summarize_jsonl("results/run_20251225_192716_96468d/raw/garak.hitlog.jsonl", "Target A")