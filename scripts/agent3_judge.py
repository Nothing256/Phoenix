import json
import argparse
import os
import re
from tqdm import tqdm
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

def extract_xml_content(text, tag):
    """Safely extracts content enclosed in XML-like tags."""
    if not text:
        return None
    match = re.search(f"<{tag}>(.*?)</{tag}>", text, re.DOTALL)
    return match.group(1).strip() if match else None

def main():
    parser = argparse.ArgumentParser(description="Agent 3: Formal Judge")
    parser.add_argument("--model_path", type=str, required=True, help="Path to the LLM")
    parser.add_argument("--input_file", type=str, required=True, help="Path to Agent 2 output JSONL")
    parser.add_argument("--output_file", type=str, required=True, help="Path to save Agent 3 evaluation JSONL")
    parser.add_argument("--prompt_file", type=str, required=True, help="Path to Agent 3 prompt txt")
    parser.add_argument("--max_samples", type=int, default=None, help="Max individual samples to process")
    args = parser.parse_args()

    # Load prompt template
    with open(args.prompt_file, "r", encoding="utf-8") as f:
        prompt_template = f.read()

    print(f"Loading model {args.model_path} via HuggingFace Transformers...")
    tokenizer = AutoTokenizer.from_pretrained(args.model_path, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        args.model_path,
        torch_dtype="auto",
        device_map="auto",
        trust_remote_code=True
    )

    # Load data
    data = []
    print(f"Reading from {args.input_file}...")
    with open(args.input_file, "r") as f:
        for line in f:
            data.append(json.loads(line))
            if args.max_samples and len(data) >= args.max_samples:
                break
    
    prompts = []
    metadata = []
    
    for item in data:
        # Agent 3 evaluates each sample individually (either vulnerable or safe)
        target = item.get("target") # 1 = bad (vulnerable), 0 = good (safe)
        
        # We need the feature (the golden standard rule)
        feature_text = item.get("agent2_feature_response")
        gherkin_feature = extract_xml_content(feature_text, "GHERKIN_FEATURE")
        
        # We need the sliced code
        slice_text = item.get("agent1_slice_response")
        
        target_code = None
        if target == 1:
            target_code = extract_xml_content(slice_text, "SLICED_BAD_CODE")
        else:
            target_code = extract_xml_content(slice_text, "SLICED_GOOD_CODE")
            
        if not gherkin_feature or not target_code:
            print(f"Skipping idx {item.get('idx')} (target {target}) due to missing parsed XML tags.")
            continue
            
        system_prompt = prompt_template.split("[USER]")[0].replace("[SYSTEM]", "").strip()
        user_prompt_template = prompt_template.split("[USER]")[1].strip()
        
        user_prompt = user_prompt_template.format(
            gherkin_feature=gherkin_feature,
            target_code=target_code
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        
        # Bypass thinking phase for Qwen3.5 just like prior layers
        if "qwen3.5" in args.model_path.lower():
            text += "<think>\n\n</think>\n\n"
            
        prompts.append(text)
        metadata.append(item)

    print(f"Executing Judge on {len(prompts)} independent samples...")
    
    os.makedirs(os.path.dirname(args.output_file), exist_ok=True)
    with open(args.output_file, "w") as f:
        pass

    # Inference execution and on-the-fly metric tracking
    correct = 0
    true_positives = 0
    false_positives = 0
    false_negatives = 0

    for i, (prompt, item) in tqdm(enumerate(zip(prompts, metadata)), total=len(prompts)):
        inputs = tokenizer([prompt], return_tensors="pt").to(model.device)
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=1024, # Just thinking + verdict
                temperature=0.2,    # Highly deterministic
                top_p=0.9,
                do_sample=True

            )
            
        generated_ids = outputs[0][len(inputs.input_ids[0]):]
        output_text = tokenizer.decode(generated_ids, skip_special_tokens=True)
        
        item["agent3_judge_response"] = output_text
        
        # Try to calculate metric logic
        verdict = extract_xml_content(output_text, "VERDICT")
        if verdict:
            verdict = verdict.strip().lower()
            ground_truth = "bad" if item["target"] == 1 else "good"
            
            if verdict == ground_truth:
                correct += 1
                
            if verdict == "bad" and ground_truth == "bad":
                true_positives += 1
            elif verdict == "bad" and ground_truth == "good":
                false_positives += 1
            elif verdict == "good" and ground_truth == "bad":
                false_negatives += 1
        
        with open(args.output_file, "a") as f:
            f.write(json.dumps(item) + "\n")

    print("\n--- ZERO-SHOT AGENT 3 METRICS ---")
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    print(f"Total Evaluated: {len(prompts)}")
    print(f"Accuracy: {correct / len(prompts):.4f}")
    print(f"Bad Precision: {precision:.4f}")
    print(f"Bad Recall: {recall:.4f}")
    print(f"Bad F1 Score: {f1:.4f}")
    
    print(f"Generation complete. Results saved to {args.output_file}")

if __name__ == "__main__":
    main()
