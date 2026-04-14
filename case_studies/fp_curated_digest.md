# Phoenix Case Study: Curated FP Digest

## Overview

From 97 False Positive cases (Agent 3 judged "bad" on ground-truth "good" code), we identified three distinct categories of high academic value. These cases provide empirical evidence for the **semantic ambiguity problem** and demonstrate that Phoenix's Gherkin-based verification reveals genuine security subtleties that binary labeling cannot capture.

**Source**: Best experiment (A2=Qwen2.5-Coder-14B, A3=Qwen3.5-9B, F1=0.825)

---

## Category A: Genuine Residual Bugs in "Fixed" Code ⭐⭐⭐

These are cases where Agent 3's FP verdict is **arguably correct** — the "fixed" code still contains real security issues that the patch did not fully address. These directly prove the **Double Standard Problem**: the same code can be "fixed" relative to one CVE but still vulnerable to a related attack vector.

### A1. IDX 229165 — Developer Acknowledges the Bug

**CVE**: Buffer overflow in QEMU `send_control_msg`
**Commit**: "virtio-serial: fix ANY_LAYOUT"

**Agent 3's Finding**: The code calls `iov_from_buf` without validating `len` against the scatter-gather list capacity.

**Smoking Gun**: The code itself contains a TODO comment that literally says: `/* TODO: detect a buffer that's too short, set NEEDS_RESET */`. **The developer explicitly documented that the security issue Agent 3 identified was known but left unfixed.**

```c
/* TODO: detect a buffer that's too short, set NEEDS_RESET */
iov_from_buf(elem.in_sg, elem.in_num, 0, buf, len);
```

**Academic Value**: Perfect evidence that "fixed" ≠ "fully secure". The patch addressed one layout assumption but left a documented buffer overflow risk.

---

### A2. IDX 224472 — Unchecked `strcpy` in Fix

**CVE**: Double-free in Gpac `gf_text_get_utf8_line`
**Commit**: "fixed #1897"

**Agent 3's Finding**: The fix enlarged a local buffer to 2048 bytes (correct), but then copies data back via `strcpy(szLine, szLineConv)` without checking if `szLine` can hold it.

```c
char szLineConv[2048]; // FIXED: Increased buffer size
// ... processing fills szLineConv ...
strcpy(szLine, szLineConv); // ← Agent 3: unchecked copy!
```

**Academic Value**: The patch fixed the double-free but introduced a classic buffer overflow via `strcpy`. Agent 3 detected a **new vulnerability in the fix itself**.

---

### A3. IDX 225547 / 225552 — Integer Overflow Persists

**CVE**: Integer overflow in TFLite `TfLiteIntArrayCreate`
**Commit**: "Update TfLiteIntArrayCreate to return size_t"

**Agent 3's Finding (IDX 225547)**: The function `TfLiteIntArrayGetSizeInBytes` computes `sizeof(dummy) + sizeof(dummy.data[0]) * size` — if `size` is enormous, the multiplication wraps around `size_t`, producing a tiny allocation and subsequent heap overflow.

**Agent 3's Finding (IDX 225552)**: The caller checks `alloc_size <= 0`, but `size_t` is unsigned — it can never be ≤ 0 after a wrap-around. The check is futile.

```c
size_t alloc_size = TfLiteIntArrayGetSizeInBytes(size);
if (alloc_size <= 0) return NULL;  // ← Agent 3: useless for unsigned!
```

**Academic Value**: The patch changed `int` to `size_t` but didn't add overflow detection. A textbook incomplete fix. Agent 3's Gherkin-based reasoning caught exactly this gap.

---

### A4. IDX 220804 — Off-by-One in Batch Index

**CVE**: Heap overflow in TensorFlow `SparseCountSparseOutput`
**Commit**: "Cleanup and remove duplicate validation in SparseCount"

**Agent 3's Finding**: The code accesses `per_batch_counts[batch_idx - 1]` inside a loop where `batch_idx` starts at 0. If the first element's index maps to `batch_idx = 0`, the subtraction produces -1 (underflow for unsigned), causing out-of-bounds access.

```c
int batch_idx = 0;
for (int idx = 0; idx < num_values; ++idx) {
    while (idx >= splits_values(batch_idx)) { batch_idx++; }
    per_batch_counts[batch_idx - 1][value] = 1; // ← batch_idx could be 0!
}
```

**Academic Value**: A classic off-by-one that the patch didn't address. The Gherkin specification's explicit boundary scenarios caught the precise failure condition.

---

## Category B: Deeper Analysis Than the Patch Scope 🔬

These cases show Agent 3 analyzing security properties **beyond the specific CVE fix**. The code is "fixed" for the targeted CVE, but Agent 3's Gherkin specification is broader and catches additional weaknesses.

### B1. IDX 221123 — Fix Handles A but Not B

**CVE**: Use-after-free in TensorFlow `DecodePng`
**Commit**: "Prevent use after free in DecodePng kernel"

**Agent 3's Finding**: The visible code adds dimension validation (overflow checks), but the Gherkin specification requires memory lifecycle management (cleanup of `decode` object). The sliced code shows the dimension fix but not the UAF fix, leading Agent 3 to correctly note the memory management requirement is unmet in the visible scope.

**Academic Value**: Demonstrates how Agent 1's slicing can sometimes separate the "fix zone" from the "requirement zone", and how Agent 3 rigidly enforces ALL Gherkin scenarios, not just the visible ones.

### B2. IDX 222666 — Race Condition in Permission Fix

**CVE**: World-writable permissions in tmate-ssh-server
**Commit**: "Harden /tmp/tmate directory"

**Agent 3's Finding**: The fix creates directories with `mkdir(..., 0700)` and then calls `chmod(..., 0700)`. But between `mkdir` and `chmod`, there's a TOCTOU (time-of-check-time-of-use) race window. Also, `umask` could modify the permissions set by `mkdir`.

**Academic Value**: Agent 3's Gherkin contract says "directories must have mode 0700" — it doesn't care about the mechanism. It caught a genuine race condition in the fix.

---

## Category C: Gherkin Over-Specification Artifacts ⚙️

These cases reveal where Agent 2's specification was stricter than what the developer intended. Not bugs in the code, but evidence that the Gherkin contract imposes a **higher standard** than the patch.

### C1. IDX 224891 — Error Message Format Mismatch

**CVE**: TensorFlow `FractionalAvgPoolGrad` missing validation
**Agent 3's Finding**: The code throws the correct `InvalidArgument` error but the error message string format doesn't exactly match the Gherkin specification's expected format.

**Academic Value**: Shows the Gherkin contract is a **strict formal spec**, not a fuzzy heuristic. This strictness is a double-edged sword — it catches real bugs (Category A) but also produces format-level false alarms.

### C2. IDX 225566 — External Function Not Verified

**CVE**: Integer overflow in ImageMagick `pcl.c`
**Agent 3's Finding**: The code calls `CastDoubleToLong()` which presumably handles overflow, but since the function body is outside the sliced scope, Agent 3 cannot verify it satisfies the Gherkin contract and conservatively judges "bad".

**Academic Value**: Illustrates the trade-off of source-level analysis — Agent 3 can only verify what it can see. This is a fundamental limitation of any code-based reasoning, not specific to Phoenix.

---

## Statistical Summary

| Category | Count (estimated) | Academic Use |
|---|---|---|
| **A: Genuine Residual Bugs** | ~15-20 | Introduction (Double Standard), Discussion (Why Gherkin Works) |
| **B: Deeper Than Patch Scope** | ~30-40 | Discussion (Cognitive Load Reduction) |
| **C: Over-Specification** | ~40-50 | Limitations, Future Work (Gherkin calibration) |

## Key Insight for the Paper

> Phoenix's "False Positives" are not ordinary classification errors. A significant fraction (15-20%) represent **genuine security concerns** in code labeled as "fixed" by the dataset. This reveals a fundamental limitation of binary vulnerability labels: security is not a binary property of code, but a **relative property** defined against specific behavioral contracts. Phoenix's Gherkin-based approach naturally surfaces this nuance, while binary classifiers are forced to collapse it.
