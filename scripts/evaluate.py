"""
Phoenix Evaluation Script
=========================
Computes classification metrics and Pair-Correct (P-C) accuracy from
Agent 3 output JSONL files.

Metrics:
  - Per-class Precision, Recall, F1 (bad/good) — instance-wise over all evaluated samples
  - Overall Accuracy
  - Pair-Correct (P-C): percentage of pairs where both
    the vulnerable and fixed sample are correctly classified.
    Requires --raw_file to reconstruct original pairing by idx.

Usage:
  # Instance-wise metrics only
  python scripts/evaluate.py --input_file data/output/judged.jsonl

  # Instance-wise + Pair-Correct
  python scripts/evaluate.py --input_file data/output/judged.jsonl \\
      --raw_file data/primevul_test_paired.jsonl
"""

import json
import argparse
import re


def extract_xml_content(text, tag):
    """Safely extracts content enclosed in XML-like tags."""
    if not text:
        return None
    match = re.search(f"<{tag}>(.*?)</{tag}>", text, re.DOTALL)
    return match.group(1).strip() if match else None


def load_results(filepath):
    """Load JSONL results and extract verdicts."""
    results = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            item = json.loads(line)
            response = item.get("agent3_judge_response", "")
            verdict = extract_xml_content(response, "VERDICT")
            if verdict:
                verdict = verdict.strip().lower()
            results.append({
                "idx": item.get("idx"),
                "target": item.get("target"),
                "verdict": verdict,
            })
    return results


def compute_metrics(results):
    """Compute instance-wise classification metrics for the 'bad' (vulnerable) class."""
    tp = fp = fn = tn = 0
    unparsed = 0

    for r in results:
        gt = "bad" if r["target"] == 1 else "good"
        pred = r["verdict"]

        if pred is None:
            unparsed += 1
            continue

        if pred == "bad" and gt == "bad":
            tp += 1
        elif pred == "bad" and gt == "good":
            fp += 1
        elif pred == "good" and gt == "bad":
            fn += 1
        elif pred == "good" and gt == "good":
            tn += 1

    total = tp + fp + fn + tn
    accuracy = (tp + tn) / total if total > 0 else 0

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

    return {
        "total_evaluated": total,
        "unparsed": unparsed,
        "tp": tp, "fp": fp, "fn": fn, "tn": tn,
        "accuracy": accuracy,
        "bad_precision": precision,
        "bad_recall": recall,
        "bad_f1": f1,
    }


def compute_pair_correct(results, raw_file):
    """
    Compute Pair-Correct (P-C) by reconstructing pairs from the original
    PrimeVul data using idx matching.

    The raw PrimeVul Paired Test Set uses sequential pairing:
      line 1 (target=1) + line 2 (target=0) = pair 1
      line 3 (target=1) + line 4 (target=0) = pair 2, etc.

    Since some samples may be skipped during pipeline execution (e.g., XML
    parsing failures in Agent 1), we cannot rely on the output file's line
    order. Instead, we:
      1. Build an idx→verdict map from the output
      2. Walk the original raw file in sequential pairs
      3. Count pairs where both members exist in the output AND are correct

    A pair is "correct" if:
      - The vulnerable sample (target=1) is predicted "bad"
      - The fixed sample (target=0) is predicted "good"
    """
    # Build idx → verdict lookup from results (include unparsed as None)
    verdict_map = {}
    idx_set = set()
    for r in results:
        idx_set.add(r["idx"])
        verdict_map[r["idx"]] = r["verdict"]  # may be None (unparsed)

    # Walk original raw file in sequential pairs
    total_pairs = 0
    correct_pairs = 0
    skipped_pairs = 0

    with open(raw_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    i = 0
    while i + 1 < len(lines):
        pos_item = json.loads(lines[i])      # target=1 (vulnerable)
        neg_item = json.loads(lines[i + 1])   # target=0 (fixed)

        pos_idx = pos_item["idx"]
        neg_idx = neg_item["idx"]

        # Count pair if both members exist in output (even if verdict unparsed)
        if pos_idx in idx_set and neg_idx in idx_set:
            total_pairs += 1
            pos_v = verdict_map.get(pos_idx)
            neg_v = verdict_map.get(neg_idx)
            if pos_v == "bad" and neg_v == "good":
                correct_pairs += 1
        else:
            skipped_pairs += 1

        i += 2

    pc = correct_pairs / total_pairs if total_pairs > 0 else 0
    return {
        "total_pairs": total_pairs,
        "correct_pairs": correct_pairs,
        "skipped_pairs": skipped_pairs,
        "pair_correct": pc,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Phoenix Evaluation: Compute F1 and Pair-Correct metrics"
    )
    parser.add_argument("--input_file", type=str, required=True,
                        help="Path to Agent 3 output JSONL file")
    parser.add_argument("--raw_file", type=str, default=None,
                        help="Path to original PrimeVul paired JSONL "
                             "(required for Pair-Correct computation)")
    args = parser.parse_args()

    print(f"Loading results from {args.input_file}...")
    results = load_results(args.input_file)

    # Classification metrics (instance-wise)
    metrics = compute_metrics(results)
    print("\n" + "=" * 60)
    print("  PHOENIX EVALUATION RESULTS (Instance-wise)")
    print("=" * 60)
    print(f"  Total Evaluated:  {metrics['total_evaluated']}")
    print(f"  Unparsed:         {metrics['unparsed']}")
    print()
    print(f"  Confusion Matrix:")
    print(f"                    Predicted Bad   Predicted Good")
    print(f"    Actual Bad       {metrics['tp']:>8}        {metrics['fn']:>8}")
    print(f"    Actual Good      {metrics['fp']:>8}        {metrics['tn']:>8}")
    print()
    print(f"  Accuracy:          {metrics['accuracy']:.4f}")
    print(f"  Bad Precision:     {metrics['bad_precision']:.4f}")
    print(f"  Bad Recall:        {metrics['bad_recall']:.4f}")
    print(f"  Bad F1 Score:      {metrics['bad_f1']:.4f}")

    # Pair-Correct metrics (only if raw_file provided)
    if args.raw_file:
        pc_metrics = compute_pair_correct(results, args.raw_file)
        print()
        print("-" * 60)
        print(f"  PAIR-CORRECT (P-C) METRIC")
        print("-" * 60)
        print(f"  Total Pairs:       {pc_metrics['total_pairs']}")
        print(f"  Correct Pairs:     {pc_metrics['correct_pairs']}")
        print(f"  Skipped Pairs:     {pc_metrics['skipped_pairs']}")
        print(f"  Pair-Correct:      {pc_metrics['pair_correct']:.4f} "
              f"({pc_metrics['correct_pairs']}/{pc_metrics['total_pairs']} "
              f"= {pc_metrics['pair_correct']*100:.1f}%)")
    else:
        print()
        print("  ℹ️  To compute Pair-Correct, add: --raw_file data/primevul_test_paired.jsonl")

    print("=" * 60)


if __name__ == "__main__":
    main()
