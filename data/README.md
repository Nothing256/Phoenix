# Data Directory

This directory should contain the PrimeVul dataset and Phoenix pipeline outputs.

## 1. PrimeVul Dataset (Required)

The PrimeVul v0.1 Paired Test Set is hosted on Google Drive by the original
authors:

📥 **[Download PrimeVul v0.1 from Google Drive](https://drive.google.com/drive/folders/19iLaNDS0z99N8kB_jBRTmDLehwZBolMY)**

After downloading, place the file as:
```
data/primevul_test_paired.jsonl
```

**Source**: Ding et al., *Vulnerability Detection with Code Language Models: How Far Are We?*
ICSE 2025. DOI: [10.1109/ICSE55347.2025.00038](https://doi.org/10.1109/ICSE55347.2025.00038)

## 2. Pre-computed Pipeline Outputs (Optional)

To skip re-running the pipeline, download our pre-computed intermediate outputs
from Zenodo:

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)

The archive contains **29 JSONL files** covering all 25+ experimental
configurations reported in the paper:

- 1 × Agent 1 (Slicing) output
- 3 × Agent 2 (Gherkin Feature) outputs (one per A2 model)
- 5 × RAW ablation results (Table 1)
- 5 × Blind ablation results (Table 1)
- 15 × Cross-model judged results (Table 1 Feature tier + Table 2)

See **[MANIFEST.md](MANIFEST.md)** for a detailed mapping of each file to its
experiment configuration, agent models, and expected F1 scores.

### Directory layout after download

```
data/
├── primevul_test_paired.jsonl                          # PrimeVul raw (from Google Drive)
├── primevul_sliced_paired_test_ZShot.jsonl              # Agent 1 output
├── primevul_features_paired_test_*.jsonl                # Agent 2 outputs (×3)
├── primevul_paired_test_ZShot_GroupRaw_Blind_*.jsonl    # RAW ablation (×5)
├── primevul_paired_test_ZShot_GroupA_Blind_*.jsonl      # Blind ablation (×5)
├── primevul_paired_test_ZShot_GroupB_Feature_*.jsonl    # Feature ablation (×3)
├── primevul_judged_paired_test_A2_*_A3_*.jsonl          # Cross-model (×10)
├── primevul_judged_paired_test_ZShot.jsonl              # A2=Gemma, A3=Gemma
├── primevul_paired_test_ZShot_QwenJudge.jsonl           # A2=Gemma, A3=Qwen3.5
├── MANIFEST.md                                          # File-to-experiment mapping
└── README.md                                            # This file
```

## 3. Evaluation

After obtaining the data, evaluate any result file:

```bash
# Instance-wise metrics (F1, Precision, Recall)
python scripts/evaluate.py --input_file data/primevul_judged_paired_test_A2_Qwen2.5-Coder-14B-Instruct_A3_Qwen3.5-9B.jsonl

# Include Pair-Correct metric (requires original PrimeVul data for idx pairing)
python scripts/evaluate.py \
    --input_file data/primevul_judged_paired_test_A2_Qwen2.5-Coder-14B-Instruct_A3_Qwen3.5-9B.jsonl \
    --raw_file data/primevul_test_paired.jsonl
```

## 4. Notes

- **Total data size**: ~260 MB (all 29 pre-computed JSONL files)
- The PrimeVul Paired Test Set contains 870 samples (435 vulnerable + 435 fixed)
- Phoenix processes 859 of 870 samples (11 skipped due to Agent 1 XML parsing)
- Effective evaluation pairs: 427 out of 435
