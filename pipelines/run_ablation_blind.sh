#!/bin/bash
# ==============================================================================
# Phoenix: Blind Ablation Pipeline (Table 1, Blind tier)
# Agent 1 slicing + Agent 3 blind judge (NO Gherkin specification)
# ==============================================================================

set -e

AGENT3_MODEL="${1:-./models/Qwen3.5-9B}"
SLICED_DATA="./data/output/sliced.jsonl"
OUTPUT="./data/output/blind_judged_${2:-default}.jsonl"

echo "🔪 [Phoenix Ablation] Blind tier: Sliced code → Direct classification"
echo "   Agent 3 Model: $AGENT3_MODEL"

python scripts/agent3_blind_judge.py \
    --model_path "$AGENT3_MODEL" \
    --input_file "$SLICED_DATA" \
    --output_file "$OUTPUT" \
    --prompt_file prompts/agent3_blind.txt

echo ""
echo "📈 Evaluating..."
python scripts/evaluate.py --input_file "$OUTPUT"
