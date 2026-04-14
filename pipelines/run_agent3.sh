#!/bin/bash
# ==============================================================================
# Phoenix: Standalone Agent 3 Runner (with Gherkin Features)
# Evaluates code samples against Gherkin specs from a specific Agent 2 model.
# Useful for testing different Agent 3 models on existing Gherkin specs.
#
# Usage: bash pipelines/run_agent3.sh <agent2_model_name> <path_to_agent3_model>
# Example: bash pipelines/run_agent3.sh Qwen2.5-Coder-14B-Instruct ./models/Qwen3.5-9B
# ==============================================================================

set -e

A2_MODEL_NAME=$1
A3_MODEL_PATH=$2

if [ -z "$A2_MODEL_NAME" ] || [ -z "$A3_MODEL_PATH" ]; then
    echo "❌ ERROR: Both Agent 2 model name and Agent 3 model path are required."
    echo "📝 Usage: bash pipelines/run_agent3.sh <agent2_model_name> <path_to_agent3_model>"
    echo "💡 Example: bash pipelines/run_agent3.sh Qwen2.5-Coder-14B-Instruct ./models/Qwen3.5-9B"
    exit 1
fi

A3_MODEL_NAME=$(basename "$A3_MODEL_PATH")

FEATURE_DATA="./data/output/features_A2_${A2_MODEL_NAME}.jsonl"
JUDGED_DATA="./data/output/judged_A2_${A2_MODEL_NAME}_A3_${A3_MODEL_NAME}.jsonl"
PROMPT_FILE="./prompts/agent3_judge.txt"

if [ ! -f "$FEATURE_DATA" ]; then
    echo "❌ ERROR: Feature data not found at $FEATURE_DATA."
    echo "💡 Run Agent 2 first: bash pipelines/run_agent2.sh <path_to_${A2_MODEL_NAME}>"
    exit 1
fi

echo "⚖️  [Phoenix Agent 3] Feature-Guided Judgement"
echo "   Agent 2 (specs from): $A2_MODEL_NAME"
echo "   Agent 3 (judge):      $A3_MODEL_NAME"
echo "   Input:  $FEATURE_DATA"
echo "   Output: $JUDGED_DATA"

if [ ! -f "$JUDGED_DATA" ]; then
    python scripts/agent3_judge.py \
        --model_path "$A3_MODEL_PATH" \
        --input_file "$FEATURE_DATA" \
        --output_file "$JUDGED_DATA" \
        --prompt_file "$PROMPT_FILE"
    echo "✅ Agent 3 complete → $JUDGED_DATA"
else
    echo "⏩ Output already exists. Delete it to re-run."
fi

echo ""
echo "📈 Evaluation:"
python scripts/evaluate.py --input_file "$JUDGED_DATA"
