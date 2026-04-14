import json
import argparse
import os
import re
from tqdm import tqdm
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

def parse_agent1_response(response_text):
    """Extracts SLICED_BAD_CODE and SLICED_GOOD_CODE from Agent 1's XML output."""
    bad_match = re.search(r'<SLICED_BAD_CODE>(.*?)</SLICED_BAD_CODE>', response_text, re.DOTALL)
    good_match = re.search(r'<SLICED_GOOD_CODE>(.*?)</SLICED_GOOD_CODE>', response_text, re.DOTALL)
    
    sliced_bad = bad_match.group(1).strip() if bad_match else None
    sliced_good = good_match.group(1).strip() if good_match else None
    return sliced_bad, sliced_good

def main():
    parser = argparse.ArgumentParser(description="Agent 2: Reverse Engineer")
    parser.add_argument("--model_path", type=str, required=True, help="Path to the LLM")
    parser.add_argument("--input_file", type=str, required=True, help="Path to Agent 1 output JSONL")
    parser.add_argument("--output_file", type=str, required=True, help="Path to save Agent 2 output JSONL")
    parser.add_argument("--prompt_file", type=str, required=True, help="Path to agent 2 prompt txt")
    parser.add_argument("--max_samples", type=int, default=None, help="Max samples to process")
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
    with open(args.input_file, "r") as f:
        for line in f:
            data.append(json.loads(line))
            if args.max_samples and len(data) >= args.max_samples:
                break
    
    # Process in pairs
    prompts = []
    valid_pairs = [] # Keeping track of which pairs actually had agent1_slice_response
    
    it = iter(data)
    for pos_item in it:
        neg_item = next(it, None)
        if neg_item is None:
            break
            
        if "agent1_slice_response" not in pos_item:
            print(f"Skipping pair idx {pos_item.get('idx')} - no agent 1 response")
            continue
            
        sliced_bad, sliced_good = parse_agent1_response(pos_item["agent1_slice_response"])
        
        # Fallback if Agent 1 failed to format correctly
        if not sliced_bad or not sliced_good:
            print(f"Warning: Could not parse XML tags for idx {pos_item.get('idx')}. Falling back.")
            
        sliced_bad = sliced_bad or "/* PARSING FAILED - SLICE UNVAILABLE */"
        sliced_good = sliced_good or "/* PARSING FAILED - SLICE UNVAILABLE */"

        cve_desc = pos_item.get("cve_desc", "No description available.")
        commit_message = pos_item.get("commit_message", "No commit message available.")
        
        system_prompt = prompt_template.split("[USER]")[0].replace("[SYSTEM]", "").strip()
        user_prompt_template = prompt_template.split("[USER]")[1].strip()
        
        user_prompt = user_prompt_template.format(
            cve_desc=cve_desc,
            commit_message=commit_message,
            sliced_bad_code=sliced_bad,
            sliced_good_code=sliced_good
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
        
        if "qwen3.5" in args.model_path.lower():
            text += "<think>\n\n</think>\n\n"
            
        prompts.append(text)
        valid_pairs.append((pos_item, neg_item))

    print(f"Generating features for {len(prompts)} samples...")
    
    # Output file
    os.makedirs(os.path.dirname(args.output_file), exist_ok=True)
    with open(args.output_file, "w") as f:
        pass

    # Inference (Batch size 1 for simplicity in HF script)
    for i, (prompt, (pos_item, neg_item)) in tqdm(enumerate(zip(prompts, valid_pairs)), total=len(prompts)):
        inputs = tokenizer([prompt], return_tensors="pt").to(model.device)
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=3072,
                temperature=0.2, # Low temp for formal logic
                top_p=0.9,
                do_sample=True
            )
            
        generated_ids = outputs[0][len(inputs.input_ids[0]):]
        output_text = tokenizer.decode(generated_ids, skip_special_tokens=True)
        
        pos_item["agent2_feature_response"] = output_text
        neg_item["agent2_feature_response"] = output_text
        
        with open(args.output_file, "a") as f:
            f.write(json.dumps(pos_item) + "\n")
            f.write(json.dumps(neg_item) + "\n")

    print(f"Generation complete. Results saved to {args.output_file}")

if __name__ == "__main__":
    main()
