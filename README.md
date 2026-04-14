# 🔥 Phoenix

**Security Is Relative: Training-Free Vulnerability Detection via Multi-Agent Behavioral Contract Synthesis**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)

---

## Overview

Phoenix is a **training-free multi-agent framework** that transforms vulnerability detection from pattern matching into **behavioral contract verification**.

Instead of asking "Is this code vulnerable?", Phoenix asks: "Does this code satisfy the precise security contract that distinguishes it from its patched version?"

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Phoenix Pipeline                          │
│                                                              │
│  ┌──────────┐    ┌──────────────┐    ┌──────────────────┐   │
│  │  Agent 1  │    │   Agent 2    │    │     Agent 3      │   │
│  │ Semantic  │───▶│ Requirement  │───▶│    Contract      │   │
│  │  Slicer   │    │  Reverse     │    │     Judge        │   │
│  │           │    │  Engineer    │    │                  │   │
│  └──────────┘    └──────────────┘    └──────────────────┘   │
│       │                 │                     │              │
│   Minimal           Gherkin              Binary             │
│   code slice        .feature             verdict            │
│                     spec                 (bad/good)         │
└─────────────────────────────────────────────────────────────┘
```

### Key Results (PrimeVul Paired Test Set)

| Method | F1 | Pair-Correct | Model Size |
|--------|-----|-------------|------------|
| **Phoenix (Ours)** | **0.825** | **64.4%** | 7–14B |
| RASM-Vul | 0.668 | 21.4%* | 685B (DeepSeek-V3) |
| VulTrial (ICSE 2026) | 0.561 | 18.6%* | GPT-4 |
| CodeBERT (fine-tuned) | 0.472 | — | 125M |

*Estimated from reported Precision and Recall.

---

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/[Anonymous]/Phoenix.git
cd phoenix
```

### 2. Set up the environment

**Option A: Conda (recommended)**

```bash
conda env create -f environment.yml
conda activate phoenix
```

**Option B: Docker**
```bash
cd docker && docker build -t phoenix . && cd ..
docker run --gpus all -it -v $(pwd):/workspace phoenix
```

### 3. Download data

```bash
cd data
bash download_primevul.sh
cd ..
```

### 4. Download models

Download the following models from Hugging Face to a `models/` directory:

| Agent | Model | HF Link |
|-------|-------|---------|
| Agent 1 (Slicer) | Qwen3.5-9B | [Qwen/Qwen3.5-9B](https://huggingface.co/Qwen/Qwen3.5-9B) |
| Agent 2 (Reverser) | Qwen2.5-Coder-14B-Instruct | [Qwen/Qwen2.5-Coder-14B-Instruct](https://huggingface.co/Qwen/Qwen2.5-Coder-14B-Instruct) |
| Agent 3 (Judge) | Qwen3.5-9B | [Qwen/Qwen3.5-9B](https://huggingface.co/Qwen/Qwen3.5-9B) |

```bash
# Example using huggingface-cli
pip install huggingface_hub
huggingface-cli download Qwen/Qwen3.5-9B --local-dir models/Qwen3.5-9B
huggingface-cli download Qwen/Qwen2.5-Coder-14B-Instruct --local-dir models/Qwen2.5-Coder-14B-Instruct
```

### 5. Run the full pipeline

```bash
# Edit model paths in the script first
bash pipelines/run_full_pipeline.sh
```

---

## Reproducing Paper Results

### Experiment Coverage Map

| Paper Table | Script | Configurations |
|-------------|--------|---------------|
| Table 1 (RAW tier) | `run_ablation_raw.sh` | 5 models × 1 |
| Table 1 (Blind tier) | `run_ablation_blind.sh` | 5 models × 1 |
| Table 1 (Feature tier) | `run_crossmodel.sh` ★ | 3 A2 × 5 A3 (subsumes Feature) |
| Table 2 (Cross-Model) | `run_crossmodel.sh` | 3 A2 × 5 A3 = 15 configs |
| Table 3 (Best config) | `run_full_pipeline.sh` | A2=QwenCoder14B, A3=Qwen3.5-9B |

★ Table 1's Feature tier uses A2=Gemma results, which are produced as part of the cross-model matrix.

### Table 1: Ablation Study (RAW → Blind → Feature)

```bash
# Run for each of the 5 Agent 3 models:
MODELS=(
    ./models/Qwen3.5-9B
    ./models/Qwen2.5-Coder-14B-Instruct
    ./models/Qwen2.5-Coder-7B-Instruct
    ./models/gemma-3-12b-it
    ./models/Meta-Llama-3.1-8B-Instruct
)

for M in "${MODELS[@]}"; do
    # RAW tier (no slicing, no Gherkin)
    bash pipelines/run_ablation_raw.sh "$M"

    # Blind tier (Agent 1 slicing, no Gherkin)
    bash pipelines/run_ablation_blind.sh "$M"
done

# Feature tier is produced by run_crossmodel.sh (see below)
```

### Table 2: Agent 2 × Agent 3 Cross-Model Matrix

```bash
# Full 3×5 matrix (also produces Table 1 Feature tier)
bash pipelines/run_crossmodel.sh
```

### Table 3: Best Configuration (Quick Reproduction)

```bash
# A2=Qwen2.5-Coder-14B, A3=Qwen3.5-9B → F1=0.825, P-C=64.4%
bash pipelines/run_full_pipeline.sh
```

### Standalone Agent Runs (Advanced)

```bash
# Run Agent 2 only (generate Gherkin specs with a custom model)
bash pipelines/run_agent2.sh ./models/Qwen2.5-Coder-14B-Instruct

# Run Agent 3 only (judge with existing Gherkin specs)
bash pipelines/run_agent3.sh Qwen2.5-Coder-14B-Instruct ./models/Qwen3.5-9B
```

### Evaluate any output

```bash
python scripts/evaluate.py --input_file data/output/judged.jsonl
```

This computes **F1**, **Pair-Correct (P-C)**, and the full confusion matrix.

---

## Project Structure

```
phoenix/
├── README.md                      # This file
├── LICENSE                        # MIT License
├── environment.yml                # Conda environment
│
├── prompts/                       # Agent prompt templates
│   ├── agent1_slicer.txt          # Semantic Slicer system prompt
│   ├── agent2_reverser.txt        # Requirement Reverse Engineer prompt
│   ├── agent3_judge.txt           # Contract Judge prompt (with Gherkin)
│   └── agent3_blind.txt           # Blind Judge prompt (ablation, no Gherkin)
│
├── scripts/                       # Core pipeline scripts
│   ├── agent1_slicer.py           # Agent 1: Semantic Slicer
│   ├── agent2_reverser.py         # Agent 2: Requirement Reverse Engineer
│   ├── agent3_judge.py            # Agent 3: Contract Judge
│   ├── agent3_blind_judge.py      # Agent 3: Blind Judge (ablation)
│   ├── agent3_raw_blind_judge.py  # Agent 3: RAW Blind Judge (ablation)
│   └── evaluate.py                # Unified evaluation (F1, P-C, confusion matrix)
│
├── pipelines/                     # Reproduction scripts
│   ├── run_full_pipeline.sh       # Best config (Table 3)
│   ├── run_ablation_raw.sh        # RAW ablation (Table 1)
│   ├── run_ablation_blind.sh      # Blind ablation (Table 1)
│   ├── run_crossmodel.sh          # 3×5 cross-model matrix (Table 1 Feature + Table 2)
│   ├── run_agent2.sh              # Standalone Agent 2 runner
│   └── run_agent3.sh              # Standalone Agent 3 runner
│
├── case_studies/                  # Qualitative analysis & full results
│   ├── full_ablation_results.md   # Complete 25-config results (Appendix A)
│   ├── fp_curated_digest.md       # False Positive error analysis
│   ├── fn_curated_digest.md       # False Negative error analysis
│   └── double_standard_evidence.md  # Double Standard examples
│
├── results/                       # Pre-computed experiment outputs
│   ├── phoenix_experiment_data.zip  # All 29 JSONL files (36 MB)
│   ├── MANIFEST.md                # File-to-experiment mapping
│   └── README.md                  # Extraction & usage instructions
│
├── docker/                        # Docker containerization
│   ├── Dockerfile
│   ├── environment.yml
│   └── README.md
│
└── data/                          # Working data directory (gitignored)
    ├── README.md                  # Download instructions for PrimeVul
    ├── MANIFEST.md                # File-to-experiment mapping
    └── download_primevul.sh       # PrimeVul download script
```

---

## Supported Models

Phoenix has been tested with the following model families:

| Model | Parameters | Role(s) Tested |
|-------|-----------|----------------|
| Qwen3.5-9B | 9B | Agent 1, Agent 3 |
| Qwen2.5-Coder-14B-Instruct | 14B | Agent 2, Agent 3 |
| Qwen2.5-Coder-7B-Instruct | 7B | Agent 3 |
| Gemma-3-12B-IT | 12B | Agent 2, Agent 3 |
| Meta-Llama-3.1-8B-Instruct | 8B | Agent 2, Agent 3 |

**Hardware**: All experiments were conducted on **2× NVIDIA RTX 4090** (48GB total VRAM).

---

## Pre-computed Results

To reproduce our results without re-running the full pipeline, download our
pre-computed intermediate outputs from Zenodo:

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)

The Zenodo archive contains all JSONL files from each pipeline stage across all
25 configurations reported in the paper.

---

## Citation

If you find Phoenix useful in your research, please cite:

```bibtex
@article{phoenix2026,
  title   = {Security Is Relative: Training-Free Vulnerability Detection
             via Multi-Agent Behavioral Contract Synthesis},
  author  = {Anonymous Authors},
  journal = {Under Review},
  year    = {2026}
}
```

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
