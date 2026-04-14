#!/bin/bash
# ==============================================================================
# Phoenix: Full 3-Agent Zero-Shot Pipeline
# Reproduces the best configuration from the paper (Table 3):
#   Agent 1: Qwen3.5-9B (Semantic Slicer)
#   Agent 2: Qwen2.5-Coder-14B-Instruct (Requirement Reverse Engineer)
#   Agent 3: Qwen3.5-9B (Contract Judge)
#
# Result: F1 = 0.825, Pair-Correct = 64.4%
# Hardware: 2× NVIDIA RTX 4090 (48GB total)
# ==============================================================================

set -e

# ─── CONFIGURATION ───────────────────────────────────────────────────────────
# Update these paths to your local model locations (Hugging Face format)
AGENT1_MODEL="./models/Qwen3.5-9B"                    # Agent 1: Semantic Slicer
AGENT2_MODEL="./models/Qwen2.5-Coder-14B-Instruct"    # Agent 2: Requirement Reverser
AGENT3_MODEL="./models/Qwen3.5-9B"                    # Agent 3: Contract Judge

# Data paths
RAW_DATA="./data/primevul_test_paired.jsonl"           # PrimeVul Paired Test Set (870 samples)
SLICED_DATA="./data/output/sliced.jsonl"               # Agent 1 output
FEATURE_DATA="./data/output/featured.jsonl"            # Agent 2 output
JUDGED_DATA="./data/output/judged.jsonl"               # Agent 3 output (final)
# ─────────────────────────────────────────────────────────────────────────────

echo "🔥 [Phoenix] Starting Full 3-Agent Pipeline..."
echo "📊 Dataset: $RAW_DATA"
echo ""

# ── Phase 1: Agent 1 (Semantic Slicer) ──────────────────────────────────────
echo "🔪 [Phase 1/3] Agent 1: Semantic Slicer ($AGENT1_MODEL)"
if [ ! -f "$SLICED_DATA" ]; then
    python scripts/agent1_slicer.py \
        --model_path "$AGENT1_MODEL" \
        --input_file "$RAW_DATA" \
        --output_file "$SLICED_DATA" \
        --prompt_file prompts/agent1_slicer.txt \
        --engine hf \
        --max_samples 435
    echo "✅ Phase 1 complete → $SLICED_DATA"
else
    echo "⏩ Sliced data exists, skipping."
fi

# ── Phase 2: Agent 2 (Requirement Reverse Engineer) ─────────────────────────
echo ""
echo "📝 [Phase 2/3] Agent 2: Requirement Reverse Engineer ($AGENT2_MODEL)"
if [ ! -f "$FEATURE_DATA" ]; then
    python scripts/agent2_reverser.py \
        --model_path "$AGENT2_MODEL" \
        --input_file "$SLICED_DATA" \
        --output_file "$FEATURE_DATA" \
        --prompt_file prompts/agent2_reverser.txt
    echo "✅ Phase 2 complete → $FEATURE_DATA"
else
    echo "⏩ Feature data exists, skipping."
fi

# ── Phase 3: Agent 3 (Contract Judge) ───────────────────────────────────────
echo ""
echo "⚖️  [Phase 3/3] Agent 3: Contract Judge ($AGENT3_MODEL)"
if [ ! -f "$JUDGED_DATA" ]; then
    python scripts/agent3_judge.py \
        --model_path "$AGENT3_MODEL" \
        --input_file "$FEATURE_DATA" \
        --output_file "$JUDGED_DATA" \
        --prompt_file prompts/agent3_judge.txt
    echo "✅ Phase 3 complete → $JUDGED_DATA"
else
    echo "⏩ Judged data exists, skipping."
fi

# ── Evaluation ──────────────────────────────────────────────────────────────
echo ""
echo "📈 [Evaluation] Computing metrics..."
python scripts/evaluate.py --input_file "$JUDGED_DATA"

echo ""
echo "🎉 [Phoenix] Pipeline complete!"
