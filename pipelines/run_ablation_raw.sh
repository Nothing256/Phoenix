#!/bin/bash
# ==============================================================================
# Phoenix: RAW Ablation Pipeline (Table 1, RAW tier)
# Raw unsliced code → Agent 3 blind judge (NO slicing, NO Gherkin)
# ==============================================================================

set -e

AGENT3_MODEL="${1:-./models/Qwen3.5-9B}"
RAW_DATA="./data/primevul_test_paired.jsonl"
OUTPUT="./data/output/raw_judged_${2:-default}.jsonl"

echo "📄 [Phoenix Ablation] RAW tier: Raw code → Direct classification"
echo "   Agent 3 Model: $AGENT3_MODEL"

python scripts/agent3_raw_blind_judge.py \
    --model_path "$AGENT3_MODEL" \
    --input_file "$RAW_DATA" \
    --output_file "$OUTPUT" \
    --prompt_file prompts/agent3_blind.txt

echo ""
echo "📈 Evaluating..."
python scripts/evaluate.py --input_file "$OUTPUT"
