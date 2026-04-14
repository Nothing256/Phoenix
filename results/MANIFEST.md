# Phoenix Experiment Data — Manifest

All files are in JSONL format. Each line is a JSON object representing one code
sample from the PrimeVul Paired Test Set.

**Dataset**: PrimeVul v0.1 Paired Test Set (870 samples = 435 pairs)
**Effective samples**: 859 (11 samples skipped due to Agent 1 XML parsing edge cases)

---

## Pipeline Stage Outputs

### Agent 1: Semantic Slicer (1 file)

| File | Description |
|------|-------------|
| `primevul_sliced_paired_test_ZShot.jsonl` | Agent 1 output (A1=Qwen3.5-9B). Contains `agent1_slice_response` with `<SLICED_BAD_CODE>` and `<SLICED_GOOD_CODE>` XML tags. |

### Agent 2: Gherkin Feature Generation (3 files)

| File | Agent 2 Model |
|------|--------------|
| `primevul_features_paired_test_ZShot.jsonl` | Gemma-3-12B-IT |
| `primevul_features_paired_test_A2_Qwen2.5-Coder-14B-Instruct.jsonl` | Qwen2.5-Coder-14B-Instruct |
| `primevul_features_paired_test_A2_Meta-Llama-3.1-8B-Instruct.jsonl` | Meta-Llama-3.1-8B-Instruct |

All contain `agent2_feature_response` with `<GHERKIN_FEATURE>` XML tags.

---

## Ablation Results (Table 1 in Paper)

### RAW Tier — No Agents (5 files)

Raw `func` code → Agent 3 direct classification (no slicing, no Gherkin).

| File | Agent 3 Model | F1 |
|------|--------------|-----|
| `primevul_paired_test_ZShot_GroupRaw_Blind_Qwen3.5-9B.jsonl` | Qwen3.5-9B | 0.448 |
| `primevul_paired_test_ZShot_GroupRaw_Blind_Qwen2.5-Coder-14B-Instruct.jsonl` | Qwen2.5-Coder-14B | 0.534 |
| `primevul_paired_test_ZShot_GroupRaw_Blind_Qwen2.5-Coder-7B-Instruct.jsonl` | Qwen2.5-Coder-7B | 0.558 |
| `primevul_paired_test_ZShot_GroupRaw_Blind_gemma-3-12b-it.jsonl` | Gemma-3-12B-IT | 0.643 |
| `primevul_paired_test_ZShot_GroupRaw_Blind_Meta-Llama-3.1-8B-Instruct.jsonl` | Llama-3.1-8B ⚠️ | 0.589* |

### Blind Tier — Agent 1 Only (5 files)

Sliced code → Agent 3 classification (no Gherkin).

| File | Agent 3 Model | F1 |
|------|--------------|-----|
| `primevul_paired_test_ZShot_GroupA_Blind_Qwen3.5-9B.jsonl` | Qwen3.5-9B | 0.510 |
| `primevul_paired_test_ZShot_GroupA_Blind_Qwen2.5-Coder-14B-Instruct.jsonl` | Qwen2.5-Coder-14B | 0.531 |
| `primevul_paired_test_ZShot_GroupA_Blind_Qwen2.5-Coder-7B-Instruct.jsonl` | Qwen2.5-Coder-7B | 0.555 |
| `primevul_paired_test_ZShot_GroupA_Blind_gemma-3-12b-it.jsonl` | Gemma-3-12B-IT | 0.647 |
| `primevul_paired_test_ZShot_GroupA_Blind_Meta-Llama-3.1-8B-Instruct.jsonl` | Llama-3.1-8B ⚠️ | 0.635* |

### Feature Tier — Full Pipeline, A2=Gemma (3 files)

These are part of the cross-model matrix (A2=Gemma row) but listed separately
because they use an older naming convention.

| File | Agent 3 Model | F1 |
|------|--------------|-----|
| `primevul_paired_test_ZShot_GroupB_Feature_Qwen2.5-Coder-14B-Instruct.jsonl` | Qwen2.5-Coder-14B | 0.797 |
| `primevul_paired_test_ZShot_GroupB_Feature_Qwen2.5-Coder-7B-Instruct.jsonl` | Qwen2.5-Coder-7B | 0.760 |
| `primevul_paired_test_ZShot_GroupB_Feature_Meta-Llama-3.1-8B-Instruct.jsonl` | Llama-3.1-8B ⚠️ | 0.602* |

The remaining A2=Gemma combinations use the older naming:

| File | Corresponds to | F1 |
|------|---------------|-----|
| `primevul_paired_test_ZShot_QwenJudge.jsonl` | A2=Gemma, A3=Qwen3.5-9B | 0.800 |
| `primevul_judged_paired_test_ZShot.jsonl` | A2=Gemma, A3=Gemma | 0.736 |

---

## Cross-Model Matrix Results (Table 2 in Paper)

### A2 = Qwen2.5-Coder-14B-Instruct (5 files)

| File | Agent 3 | F1 |
|------|---------|-----|
| `primevul_judged_..._A2_Qwen2.5-Coder-14B-Instruct_A3_Qwen3.5-9B.jsonl` | Qwen3.5-9B | **0.825** 🏆 |
| `primevul_judged_..._A2_Qwen2.5-Coder-14B-Instruct_A3_Qwen2.5-Coder-14B-Instruct.jsonl` | Qwen2.5-14B | 0.795 |
| `primevul_judged_..._A2_Qwen2.5-Coder-14B-Instruct_A3_Qwen2.5-Coder-7B-Instruct.jsonl` | Qwen2.5-7B | 0.764 |
| `primevul_judged_..._A2_Qwen2.5-Coder-14B-Instruct_A3_gemma-3-12b-it.jsonl` | Gemma-3-12B | 0.773 |
| `primevul_judged_..._A2_Qwen2.5-Coder-14B-Instruct_A3_Meta-Llama-3.1-8B-Instruct.jsonl` | Llama-3.1 ⚠️ | 0.630* |

### A2 = Meta-Llama-3.1-8B-Instruct (5 files)

| File | Agent 3 | F1 |
|------|---------|-----|
| `primevul_judged_..._A2_Meta-Llama-3.1-8B-Instruct_A3_Qwen3.5-9B.jsonl` | Qwen3.5-9B | 0.769 |
| `primevul_judged_..._A2_Meta-Llama-3.1-8B-Instruct_A3_Qwen2.5-Coder-14B-Instruct.jsonl` | Qwen2.5-14B | 0.714 |
| `primevul_judged_..._A2_Meta-Llama-3.1-8B-Instruct_A3_Qwen2.5-Coder-7B-Instruct.jsonl` | Qwen2.5-7B | 0.722 |
| `primevul_judged_..._A2_Meta-Llama-3.1-8B-Instruct_A3_gemma-3-12b-it.jsonl` | Gemma-3-12B | 0.697 |
| `primevul_judged_..._A2_Meta-Llama-3.1-8B-Instruct_A3_Meta-Llama-3.1-8B-Instruct.jsonl` | Llama-3.1 ⚠️ | 0.515* |

---

## Notes

- ⚠️ **Llama-3.1-8B as Agent 3**: 80%+ of outputs fail `<VERDICT>` format compliance.
  F1 scores marked with * are computed on the ~130 parseable samples only.
- **File name prefix `primevul_judged_`** is abbreviated as `primevul_judged_...` in the
  cross-model tables above for readability. Full filenames use the pattern:
  `primevul_judged_paired_test_A2_{model}_A3_{model}.jsonl`
- All Agent 1 outputs use **Qwen3.5-9B** (fixed across all experiments).
- All inference was performed on **2× NVIDIA RTX 4090** using HuggingFace Transformers
  with bfloat16 precision, zero-shot (no fine-tuning).
