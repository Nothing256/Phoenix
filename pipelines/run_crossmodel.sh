#!/bin/bash
# ==============================================================================
# Phoenix: Cross-Model Matrix Pipeline (Table 2 + Table 4)
#
# Generates Gherkin specs with 3 Agent 2 models, then evaluates each with
# 5 Agent 3 models, producing a 3×5 matrix of 15 configurations.
#
# Agent 2 candidates: Qwen2.5-Coder-14B, Gemma-3-12B-IT, Llama-3.1-8B
# Agent 3 candidates: Qwen3.5-9B, Qwen2.5-Coder-14B, Qwen2.5-Coder-7B,
#                     Gemma-3-12B-IT, Llama-3.1-8B
#
# NOTE: Llama-3.1-8B as Agent 3 produces >80% unparseable outputs (Finding 10),
#       but we include it for completeness.
#
# This also covers Table 1's Feature tier (A2=Gemma row) and the best config
# (A2=QwenCoder14B, A3=Qwen3.5-9B = Table 3).
#
# Hardware: 2× NVIDIA RTX 4090 (48GB total)
# ==============================================================================

set -e

# ─── CONFIGURATION ───────────────────────────────────────────────────────────
# Agent 2 models (Gherkin specification generators)
A2_MODELS=(
    "./models/Qwen2.5-Coder-14B-Instruct"
    "./models/gemma-3-12b-it"
    "./models/Meta-Llama-3.1-8B-Instruct"
)
A2_NAMES=("Qwen2.5-Coder-14B-Instruct" "gemma-3-12b-it" "Meta-Llama-3.1-8B-Instruct")

# Agent 3 models (Contract judges)
A3_MODELS=(
    "./models/Qwen3.5-9B"
    "./models/Qwen2.5-Coder-14B-Instruct"
    "./models/Qwen2.5-Coder-7B-Instruct"
    "./models/gemma-3-12b-it"
    "./models/Meta-Llama-3.1-8B-Instruct"
)
A3_NAMES=("Qwen3.5-9B" "Qwen2.5-Coder-14B-Instruct" "Qwen2.5-Coder-7B-Instruct" "gemma-3-12b-it" "Meta-Llama-3.1-8B-Instruct")

SLICED_DATA="./data/output/sliced.jsonl"
# ─────────────────────────────────────────────────────────────────────────────

echo "🔬 [Phoenix] Cross-Model Matrix Experiment"
echo "   Agent 2 models: ${#A2_MODELS[@]}"
echo "   Agent 3 models: ${#A3_MODELS[@]}"
echo "   Total configs:  $((${#A2_MODELS[@]} * ${#A3_MODELS[@]}))"
echo ""

for i in "${!A2_MODELS[@]}"; do
    A2="${A2_MODELS[$i]}"
    A2N="${A2_NAMES[$i]}"

    FEATURE_DATA="./data/output/features_A2_${A2N}.jsonl"

    # ── Agent 2: Generate Gherkin specs ──
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📝 [Agent 2] Generating Gherkin specs with: $A2N"
    if [ ! -f "$FEATURE_DATA" ]; then
        python scripts/agent2_reverser.py \
            --model_path "$A2" \
            --input_file "$SLICED_DATA" \
            --output_file "$FEATURE_DATA" \
            --prompt_file prompts/agent2_reverser.txt
        echo "✅ Agent 2 complete → $FEATURE_DATA"
    else
        echo "⏩ Already exists, skipping."
    fi

    for j in "${!A3_MODELS[@]}"; do
        A3="${A3_MODELS[$j]}"
        A3N="${A3_NAMES[$j]}"

        JUDGED="./data/output/judged_A2_${A2N}_A3_${A3N}.jsonl"

        # ── Agent 3: Judge ──
        echo ""
        echo "⚖️  [Agent 3] A2=$A2N × A3=$A3N"
        if [ ! -f "$JUDGED" ]; then
            python scripts/agent3_judge.py \
                --model_path "$A3" \
                --input_file "$FEATURE_DATA" \
                --output_file "$JUDGED" \
                --prompt_file prompts/agent3_judge.txt
            echo "✅ Complete → $JUDGED"
        else
            echo "⏩ Already exists, skipping."
        fi

        # ── Evaluate ──
        python scripts/evaluate.py --input_file "$JUDGED"
        echo ""
    done
done

echo "🎉 [Phoenix] Cross-model experiment complete! (${#A2_MODELS[@]}×${#A3_MODELS[@]} = $((${#A2_MODELS[@]} * ${#A3_MODELS[@]})) configs)"
