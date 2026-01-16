#!/usr/bin/env bash
set -euo pipefail

IMAGE=self-healing-llm
PROBES="lmrc.Bullying,lmrc.Sexualisation"
GEN=1

RUN_ID="week4_$(date +%Y%m%d_%H%M%S)"
ROOT_RESULTS="results/Ablations/${RUN_ID}"
mkdir -p "${ROOT_RESULTS}"

echo "==> Run: ${RUN_ID}"

# Start baseline container (A + B endpoints exist, but B may be full; baseline is /generate)
docker rm -f shllm >/dev/null 2>&1 || true
docker run -d --name shllm -p 8000:8000 "${IMAGE}"
sleep 2

# echo "==> Garak C0 baseline (Target A)"
# mkdir -p "${ROOT_RESULTS}/C0/A/raw"
# python -m garak --target_type rest.RestGenerator -G configs/target_A_rest_config.json \
#   --probes "${PROBES}" --generations "${GEN}" --report_prefix "${ROOT_RESULTS}/C0/A/raw/garak"

docker rm -f shllm

# Conditions C1-C4 (Target B)
declare -a CONDS=("C1" "C2" "C3" "C4")
declare -a CFGS=(
#   "configs/week4/patches_C1_policy_only.yaml"
#   "configs/week4/patches_C2_sanitize_only.yaml"
  "configs/week4/patches_C3_output_only.yaml"
#   "configs/week4/patches_C4_full.yaml"
)

for i in "${!CONDS[@]}"; do
  C="${CONDS[$i]}"
  CFG="${CFGS[$i]}"
  echo "==> ${C} Target B with ${CFG}"

  docker rm -f shllm >/dev/null 2>&1 || true
  docker run -d --name shllm -p 8000:8000 -e PATCHES_CONFIG_PATH="${CFG}" "${IMAGE}"
  sleep 2

  mkdir -p "${ROOT_RESULTS}/${C}/B/raw"
  python -m garak --target_type rest.RestGenerator -G configs/target_B_rest_config.json \
    --probes "${PROBES}" --generations "${GEN}" --report_prefix "${ROOT_RESULTS}/${C}/B/raw/garak_patched"

  docker rm -f shllm
done

echo "==> Done. Results in ${ROOT_RESULTS}"
