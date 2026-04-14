#!/bin/bash
# ==============================================================================
# Phoenix: Standalone Agent 2 Runner
# Generates Gherkin specifications from Agent 1's sliced output.
# Useful for re-running Agent 2 with a different model without re-slicing.
#
# Usage: bash pipelines/run_agent2.sh <path_to_model>
# Example: bash pipelines/run_agent2.sh ./models/Qwen2.5-Coder-14B-Instruct
# ==============================================================================

set -e

MODEL_PATH=$1

if [ -z "$MODEL_PATH" ]; then
    echo "❌ ERROR: Model path not provided."
    echo "📝 Usage: bash pipelines/run_agent2.sh <path_to_model>"
    exit 1
fi

MODEL_NAME=$(basename "$MODEL_PATH")

SLICED_DATA="./data/output/sliced.jsonl"
FEATURE_DATA="./data/output/features_A2_${MODEL_NAME}.jsonl"
PROMPT_FILE="./prompts/agent2_reverser.txt"

if [ ! -f "$SLICED_DATA" ]; then
    echo "❌ ERROR: Sliced data not found at $SLICED_DATA."
    echo "💡 Run the full pipeline first: bash pipelines/run_full_pipeline.sh"
    exit 1
fi

echo "📝 [Phoenix Agent 2] Generating Gherkin specifications"
echo "   Model:  $MODEL_NAME"
echo "   Input:  $SLICED_DATA"
echo "   Output: $FEATURE_DATA"

if [ ! -f "$FEATURE_DATA" ]; then
    python scripts/agent2_reverser.py \
        --model_path "$MODEL_PATH" \
        --input_file "$SLICED_DATA" \
        --output_file "$FEATURE_DATA" \
        --prompt_file "$PROMPT_FILE"
    echo "✅ Agent 2 complete → $FEATURE_DATA"
else
    echo "⏩ Output already exists. Delete it to re-run."
fi
