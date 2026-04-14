# Pre-computed Experiment Results

This directory contains all pre-computed outputs from the Phoenix pipeline
experiments reported in the paper.

## `phoenix_experiment_data.zip` (36 MB)

Contains 29 JSONL files + MANIFEST.md covering:
- Agent 1 slicing output (1 file)
- Agent 2 Gherkin specification outputs (3 files, one per A2 model)
- RAW ablation results (5 files)
- Blind ablation results (5 files)
- Feature ablation + Cross-model matrix results (15 files)

## Usage

```bash
# Extract to the data/ directory
unzip results/phoenix_experiment_data.zip -d data/

# Evaluate the best configuration
python scripts/evaluate.py \
    --input_file data/primevul_judged_paired_test_A2_Qwen2.5-Coder-14B-Instruct_A3_Qwen3.5-9B.jsonl \
    --raw_file data/primevul_test_paired.jsonl
```

See **[MANIFEST.md](MANIFEST.md)** for a complete file-to-experiment mapping.
