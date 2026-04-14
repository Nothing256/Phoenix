# Phoenix Case Study: False Negative (Missed Vulnerability) Digest

## Overview

From 60 False Negative cases (Agent 3 judged "good" on ground-truth "bad/vulnerable" code), we identify systematic failure modes that guide future improvements. These represent vulnerabilities that **Phoenix missed** in the best configuration (A2=Qwen2.5-Coder-14B, A3=Qwen3.5-9B, F1=0.825).

**Key Observations**:
- 73% (44/60) of FN reasonings contain "satisfies/meets" — Agent 3 is **confidently wrong**
- 63% (38/60) use "correctly implements" — Agent 3 **actively validates** the vulnerable code
- The longest FN reasoning (3927 chars, IDX 213370) is a thorough but fundamentally flawed analysis

---

## FN Distribution by CWE

| CWE | Count | Description | Top Projects |
|---|---|---|---|
| **CWE-787** | 13 | Out-of-bounds Write | gpac, vim, wolfMQTT |
| **CWE-125** | 7 | Out-of-bounds Read | mruby, LuaJIT, vim |
| **CWE-476** | 5 | NULL Pointer Dereference | gpac, weechat, linux |
| **CWE-416** | 5 | Use After Free | tensorflow, linux, vim |
| **CWE-703** | 4 | Improper Check for Unusual Conditions | mruby, gpac |
| **CWE-401** | 2 | Missing Release of Memory | tensorflow, ovs |
| **CWE-415** | 2 | Double Free | gpac, micro-ecc |
| Others | 22 | Various (19 distinct CWEs) | scattered |

## FN Distribution by Project

| Project | Missed | Notes |
|---|---|---|
| **vim** | 11 | Largest source of missed vulns — complex text processing logic |
| **linux** | 7 | Kernel-level bugs requiring deep system knowledge |
| **tensorflow** | 5 | Complex tensor operations |
| **gpac** | 4 | Multimedia format parsing |
| **php-src** | 3 | Language runtime internals |

---

## Failure Mode Categories

### Mode 1: Gherkin Specification Too Narrow ⭐⭐⭐ (Estimated ~25 cases)

Agent 2 generated a Gherkin specification that captured **some** but not **all** critical security properties. Agent 3 verified the code against the spec and correctly determined compliance — but the spec itself was incomplete.

**Example: IDX 195409 (gpac, CWE-476)**
- The Gherkin spec focused on NULL pointer handling: "if ptr is NULL, return without operations"
- The vulnerable code does check `if (ptr == NULL) return;` — **passing the spec**
- But the vulnerability is a **different** NULL dereference path not covered by the spec

**Implication**: Agent 2 needs to generate **broader** specifications, or a feedback loop where Agent 3's initial pass informs a second specification refinement round.

---

### Mode 2: Subtle Off-by-One / Boundary Conditions (Estimated ~15 cases)

Agent 3 looks at the code, sees boundary checks present, and concludes compliance — but the check itself has a subtle bug (off-by-one, wrong operator, missing edge case).

**Example: IDX 207520 (rizin, CWE-787)**
- The code iterates `i = 0` to `i < abbrev->count - 1`
- Agent 3 sees the bounds check and concludes it's safe
- But when `abbrev->count == 0`, the subtraction underflows (unsigned), causing massive out-of-bounds access
- Agent 3 reasoning is only 426 chars — **superficial analysis** missed this corner case

**Implication**: Agent 3 needs explicit prompting to check **boundary conditions of the boundary checks themselves** (meta-level verification).

---

### Mode 3: False Confidence from Partial Match (Estimated ~15 cases)

When the code correctly handles 3 out of 4 scenarios in the Gherkin spec, Agent 3 rounds up to "good" instead of strictly enforcing 100% compliance.

**Example: IDX 202392 (php-src, CWE-119)**
- 1809-char reasoning where Agent 3 meticulously verifies overflow detection, memory cleanup, etc.
- Concludes "correctly detects overflow using SafeAdd"
- Misses that the loop condition `while (u >= 0)` with an unsigned int is **always true** (infinite loop)
- The commit message literally says: "while (u>=0) with unsigned int will always be true"

**Implication**: This is a **reasoning depth** limitation. Agent 3 performs surface-level compliance checking but misses semantic traps.

---

### Mode 4: Context-Dependent / Architecture-Level Bugs (Estimated ~5 cases)

Some vulnerabilities require understanding the broader system architecture (kernel privilege levels, protocol state machines, inter-process communication) that are invisible in a single function slice.

**Example: IDX 195082 (linux, CWE-862/Missing Authorization)**
- KVM nested virtualization: L1 should always intercept VMLOAD/VMSAVE when nested
- The vulnerability is about **missing privilege escalation checks** in a hypervisor context
- This requires understanding the entire KVM security model, not just the function's syntax

**Example: IDX 200157 (exim, CWE-264/Permissions)**  
- Configuration file permission checking when process is privileged
- Requires understanding Unix privilege escalation semantics

**Implication**: These are **fundamentally hard** for any single-function analysis approach. Addressing them requires cross-function context (which Agent 1's slicing intentionally removes) or domain-specific security knowledge bases.

---

## Statistical Insight: The Confident Failure Problem

| Reasoning Pattern | % of FN Cases | Interpretation |
|---|---|---|
| "satisfies/meets" | 73% (44/60) | Agent 3 explicitly declares compliance |
| "correctly implements" | 63% (38/60) | Agent 3 actively validates the code |
| "prevents/handles" | 53% (32/60) | Agent 3 acknowledges security measures |
| "properly validates" | 13% (8/60) | Agent 3 endorses validation logic |

> **Key Finding**: Agent 3 doesn't miss vulnerabilities due to uncertainty — it misses them due to **confident misanalysis**. The model actively reasons through the Gherkin scenarios and erroneously concludes compliance. This suggests that the failure point is in **reasoning depth**, not reasoning engagement.

---

## Improvement Directions for Future Work

| Direction | Target Mode | Expected Impact |
|---|---|---|
| **Multi-round Gherkin refinement** (Agent 2 ↔ Agent 3 feedback loop) | Mode 1 | High — catches incomplete specs |
| **Boundary-condition meta-prompting** for Agent 3 | Mode 2 | Medium — catches off-by-one in checks |
| **Adversarial self-critique** (Agent 3 argues both sides) | Mode 3 | Medium — reduces false confidence |
| **CWE-specific knowledge injection** into Gherkin templates | Mode 4 | Low-Medium — limited by scope |
| **Cross-function context expansion** for Agent 1 | Mode 4 | High but complex — breaks current architecture |

---

## Key Quote for Paper

> Phoenix's 60 False Negatives reveal a **confident failure mode**: in 73% of cases, Agent 3 explicitly declares the vulnerable code "satisfies" the security specification. This is not a failure of engagement but of **reasoning depth** — the model performs surface-level compliance checking against the Gherkin contract but misses subtle semantic traps (unsigned integer boundary conditions, implicit type coercions, missing edge cases). This motivates future work on adversarial self-critique mechanisms and multi-round specification refinement.
