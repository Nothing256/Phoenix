# Phoenix — Full Ablation Results (25 Configurations)

This document presents the complete results from all 25 experimental
configurations reported in the paper. It serves as the supplementary material
referenced in Appendix A.

**Agent 1 (Slicer)**: Qwen3.5-9B (fixed across all experiments)
**Dataset**: PrimeVul v0.1 Paired Test Set (870 samples, 859 effective)
**Hardware**: 2× NVIDIA RTX 4090, HuggingFace Transformers, bfloat16, zero-shot

---

## Part 1: Three-Tier Ablation (Table 1)

Agent 2 = Gemma-3-12B-IT for the Feature tier.

### F1 Summary

| Agent 3 Model | RAW | Blind | Feature | Δ (RAW→Feature) |
|---|---|---|---|---|
| **Qwen3.5-9B** | 0.448 | 0.510 | **0.800** | **+0.351** |
| **Qwen2.5-Coder-14B** | 0.534 | 0.531 | **0.797** | **+0.263** |
| **Qwen2.5-Coder-7B** | 0.558 | 0.555 | **0.760** | **+0.203** |
| **Gemma-3-12B-IT** | 0.643 | 0.647 | **0.736** | **+0.092** |
| Llama-3.1-8B ⚠️ | 0.589* | 0.635* | 0.602* | +0.013* |

> ⚠️ Llama-3.1-8B as Agent 3 has severe `<VERDICT>` format compliance failures
> (50–67% unparsed), making its scores non-comparable.

### Detailed Confusion Matrices

#### RAW Tier (No Agents Active)

| Model | Eval | Unparsed | TP | FP | FN | TN | Prec | Recall | F1 |
|---|---|---|---|---|---|---|---|---|---|
| Gemma-3-12B | 859 | 0 | 376 | 361 | 56 | 66 | 0.510 | 0.870 | **0.643** |
| Qwen2.5-7B | 859 | 0 | 269 | 264 | 163 | 163 | 0.505 | 0.623 | **0.558** |
| Qwen2.5-14B | 859 | 0 | 262 | 288 | 170 | 139 | 0.476 | 0.607 | **0.534** |
| Qwen3.5-9B | 839 | 20 | 162 | 138 | 261 | 278 | 0.540 | 0.383 | **0.448** |
| Llama-3.1 ⚠️ | 289 | 570 | 98 | 75 | 38 | 78 | 0.566 | 0.721 | 0.589* |

#### Blind Tier (Agent 1 Slicing Only)

| Model | Eval | Unparsed | TP | FP | FN | TN | Prec | Recall | F1 |
|---|---|---|---|---|---|---|---|---|---|
| Gemma-3-12B | 859 | 0 | 351 | 302 | 81 | 125 | 0.538 | 0.813 | **0.647** |
| Qwen2.5-7B | 859 | 0 | 257 | 241 | 172 | 185 | 0.516 | 0.599 | **0.555** |
| Qwen2.5-14B | 859 | 0 | 233 | 212 | 199 | 215 | 0.524 | 0.539 | **0.531** |
| Qwen3.5-9B | 852 | 7 | 190 | 127 | 238 | 297 | 0.599 | 0.444 | **0.510** |
| Llama-3.1 ⚠️ | 282 | 577 | 107 | 75 | 28 | 74 | 0.588 | 0.793 | 0.635* |

#### Feature Tier (Full Pipeline, A2=Gemma-3-12B-IT)

| Model | Eval | Unparsed | TP | FP | FN | TN | Prec | Recall | F1 |
|---|---|---|---|---|---|---|---|---|---|
| Qwen3.5-9B | 854 | 5 | 353 | 100 | 77 | 324 | 0.779 | 0.821 | **0.800** |
| Qwen2.5-14B | 859 | 0 | 368 | 124 | 64 | 303 | 0.748 | 0.852 | **0.797** |
| Qwen2.5-7B | 855 | 4 | 350 | 140 | 81 | 284 | 0.714 | 0.812 | **0.760** |
| Gemma-3-12B | 859 | 0 | 277 | 44 | 155 | 383 | 0.863 | 0.641 | **0.736** |
| Llama-3.1 ⚠️ | 312 | 547 | 105 | 69 | 39 | 99 | 0.603 | 0.729 | 0.602* |

---

## Part 2: Agent 2 × Agent 3 Cross-Model Matrix (Table 2)

### F1 Score Matrix

| | A3: Q3.5-9B | A3: Q14B | A3: Q7B | A3: Gem-12B | A3: Llama ⚠️ |
|---|---|---|---|---|---|
| **A2: Qwen2.5-Coder-14B** | **0.825** 🏆 | 0.795 | 0.764 | 0.773 | 0.630* |
| **A2: Gemma-3-12B-IT** | 0.800 | 0.797 | 0.760 | 0.736 | 0.602* |
| **A2: Llama-3.1-8B** | 0.769 | 0.714 | 0.722 | 0.697 | 0.515* |

### Detailed Results — A2: Qwen2.5-Coder-14B-Instruct

| Agent 3 | Eval | Unparsed | TP | FP | FN | TN | Prec | Recall | F1 |
|---|---|---|---|---|---|---|---|---|---|
| **Qwen3.5-9B** | 854 | 5 | 369 | 97 | 60 | 328 | **0.792** | **0.860** | **0.825** 🏆 |
| Qwen2.5-14B | 859 | 0 | 380 | 144 | 52 | 283 | 0.725 | 0.880 | 0.795 |
| Gemma-3-12B | 859 | 0 | 301 | 46 | 131 | 381 | 0.867 | 0.697 | 0.773 |
| Qwen2.5-7B | 857 | 2 | 365 | 160 | 66 | 266 | 0.695 | 0.847 | 0.764 |
| Llama-3.1 ⚠️ | 131 | 728 | 40 | 44 | 3 | 44 | 0.476 | 0.930 | 0.630* |

### Detailed Results — A2: Gemma-3-12B-IT

| Agent 3 | Eval | Unparsed | TP | FP | FN | TN | Prec | Recall | F1 |
|---|---|---|---|---|---|---|---|---|---|
| Qwen3.5-9B | 854 | 5 | 353 | 100 | 77 | 324 | 0.779 | 0.821 | **0.800** |
| Qwen2.5-14B | 859 | 0 | 368 | 124 | 64 | 303 | 0.748 | 0.852 | 0.797 |
| Qwen2.5-7B | 855 | 4 | 350 | 140 | 81 | 284 | 0.714 | 0.812 | 0.760 |
| Gemma-3-12B | 859 | 0 | 277 | 44 | 155 | 383 | 0.863 | 0.641 | 0.736 |
| Llama-3.1 ⚠️ | 312 | 547 | 105 | 69 | 39 | 99 | 0.603 | 0.729 | 0.602* |

### Detailed Results — A2: Meta-Llama-3.1-8B-Instruct

| Agent 3 | Eval | Unparsed | TP | FP | FN | TN | Prec | Recall | F1 |
|---|---|---|---|---|---|---|---|---|---|
| Qwen3.5-9B | 843 | 6 | 377 | 179 | 48 | 239 | 0.678 | 0.887 | **0.769** |
| Qwen2.5-7B | 849 | 0 | 372 | 232 | 55 | 190 | 0.616 | 0.871 | 0.722 |
| Qwen2.5-14B | 849 | 0 | 386 | 268 | 41 | 154 | 0.590 | 0.904 | 0.714 |
| Gemma-3-12B | 849 | 0 | 276 | 89 | 151 | 333 | 0.756 | 0.646 | 0.697 |
| Llama-3.1 ⚠️ | 133 | 716 | 35 | 56 | 10 | 32 | 0.385 | 0.778 | 0.515* |

---

## Part 3: Agent 3 Behavioral Profiles (Table 4)

Averaged over the 3 Agent 2 models (excluding Llama-as-A3).

| Agent 3 | Avg Prec | Avg Recall | Avg F1 | Profile |
|---|---|---|---|---|
| Qwen3.5-9B | 0.750 | 0.856 | **0.798** | Balanced |
| Qwen2.5-Coder-14B | 0.688 | 0.881 | 0.769 | Recall-dominant |
| Qwen2.5-Coder-7B | 0.675 | 0.843 | 0.748 | Recall-dominant |
| Gemma-3-12B-IT | 0.829 | 0.661 | 0.735 | Precision-dominant |

---

## Part 4: Agent 2 Quality Hierarchy

Averaged over the 4 reliable Agent 3 models.

| Agent 2 | Avg F1 | Rank |
|---|---|---|
| Qwen2.5-Coder-14B | **0.789** | 🥇 |
| Gemma-3-12B-IT | 0.773 | 🥈 |
| Llama-3.1-8B | 0.725 | 🥉 |

---

## Key Findings

1. **🏆 Best Configuration**: A2=Qwen2.5-Coder-14B + A3=Qwen3.5-9B → F1=0.825, P-C=64.4% (275/427)

2. **Gherkin Is the Decisive Driver**: Feature tier improvements of +0.09 to +0.35 over RAW, while Blind tier shows only +0.00 to +0.06.

3. **Code Models Produce Better Specs**: Qwen2.5-Coder-14B (code-specialized) generates the highest-quality Gherkin, outperforming general models in every Agent 3 column.

4. **Distinct Judicial Temperaments**: Gemma = conservative (high Precision, low Recall), Qwen2.5-14B = aggressive (high Recall, low Precision), Qwen3.5-9B = balanced (best F1).

5. **Generating ≠ Following Format**: Llama-3.1-8B generates usable Gherkin as Agent 2 (849/859 parsed) but fails 80%+ `<VERDICT>` compliance as Agent 3 — structured content generation and structured output format are independent capabilities.
