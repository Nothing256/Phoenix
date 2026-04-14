"""
Phoenix Agent 1: Semantic Slicer
================================
Extracts minimal vulnerability-relevant code context from paired
code samples (vulnerable + fixed). Supports both vLLM and HuggingFace
inference backends.

Usage:
  python scripts/agent1_slicer.py \
      --model_path models/Qwen3.5-9B \
      --input_file data/primevul_test_paired.jsonl \
      --output_file data/output/sliced.jsonl \
      --engine vllm --max_samples 435
"""

import json
import argparse
import os
from tqdm import tqdm

def load_prompt_template(template_path):
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()

def main():
    parser = argparse.ArgumentParser(description="Agent 1: Semantic Slicer using vLLM (Zero-Shot)")
    parser.add_argument("--model_path", type=str, required=True, help="Path to the LLM (e.g., Qwen3.5-9B)")
    parser.add_argument("--input_file", type=str, default="./data/primevul_test_paired.jsonl")
    parser.add_argument("--output_file", type=str, default="./data/output/sliced.jsonl")
    parser.add_argument("--prompt_file", type=str, default="./prompts/agent1_slicer.txt")
    parser.add_argument("--engine", type=str, choices=["vllm", "hf"], default="vllm", help="Inference engine: vllm (fast) or hf (compatible)")
    parser.add_argument('--gpu_memory_utilization', type=float, default=0.8)
    parser.add_argument("--max_samples", type=int, default=10, help="Number of pairs to process for testing")
    parser.add_argument("--tensor_parallel_size", type=int, default=1)
    args = parser.parse_args()

    print("Loading prompt template...")
    prompt_template_str = load_prompt_template(args.prompt_file)

    if args.engine == "vllm":
        from vllm import LLM, SamplingParams
        print(f"Loading vLLM model from: {args.model_path}")
        llm = LLM(
            model=args.model_path, 
            tensor_parallel_size=args.tensor_parallel_size,
            trust_remote_code=True
        )
        tokenizer = llm.get_tokenizer()
        sampling_params = SamplingParams(temperature=0.1, top_p=0.9, max_tokens=3072)
    else:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        import torch
        print(f"Loading HuggingFace model from: {args.model_path}")
        tokenizer = AutoTokenizer.from_pretrained(args.model_path, trust_remote_code=True)
        model = AutoModelForCausalLM.from_pretrained(
            args.model_path, 
            device_map="auto", 
            torch_dtype=torch.bfloat16,
            trust_remote_code=True
        )

    prompts = []
    metadata = []
    
    print(f"Reading up to {args.max_samples} pairs from {args.input_file}...")
    with open(args.input_file, 'r', encoding='utf-8') as fin:
        for _ in range(args.max_samples):
            pos_line = fin.readline()  # target=1 (Vulnerable)
            neg_line = fin.readline()  # target=0 (Benign/Fixed)
            
            if not pos_line or not neg_line:
                break
                
            pos_data = json.loads(pos_line)
            neg_data = json.loads(neg_line)
            
            cve_desc = pos_data.get('cve_desc', 'No Description')
            commit_message = pos_data.get('commit_message', 'No Message')
            bad_func = pos_data.get('func', '')
            good_func = neg_data.get('func', '')
            
            # Format the system/user prompt
            # For base models, we might just pass the raw concatenated string.
            # If using an Instruct model, we should wrap it in its chat template.
            # Assuming Qwen3.5 uses standard chat template handled by tokenizer:
            raw_prompt = prompt_template_str.format(
                cve_desc=cve_desc,
                commit_message=commit_message,
                bad_func_full=bad_func,
                good_func_full=good_func
            )
            
            messages = [
                {"role": "system", "content": "You are a world-class security architect and forensic code analyst."},
                {"role": "user", "content": raw_prompt.replace("[SYSTEM]", "").replace("You are a world-class security architect and forensic code analyst.", "").strip()}
            ]
            
            # We apply the chat template strictly.
            formatted_prompt = tokenizer.apply_chat_template(
                messages, 
                tokenize=False, 
                add_generation_prompt=True
            )
            
            if "qwen3.5" in args.model_path.lower():
                formatted_prompt += "<think>\n\n</think>\n\n"
            
            prompts.append(formatted_prompt)
            metadata.append({"pos_data": pos_data, "neg_data": neg_data})

    print(f"Executing Agent 1 (Semantic Slicing) via {args.engine.upper()} on {len(prompts)} pairs...")
    if args.engine == "vllm":
        outputs = llm.generate(prompts, sampling_params)
        generated_texts = [output.outputs[0].text for output in outputs]
    else:
        generated_texts = []
        for p in tqdm(prompts, desc="HF Inference"):
            inputs = tokenizer(p, return_tensors="pt").to(model.device)
            output_ids = model.generate(
                **inputs, 
                max_new_tokens=3072, 
                temperature=0.2, 
                top_p=0.9,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
            # Slice off the prompt logic
            gen_ids = output_ids[0][inputs.input_ids.shape[1]:]
            res = tokenizer.decode(gen_ids, skip_special_tokens=True)
            generated_texts.append(res)
    
    os.makedirs(os.path.dirname(args.output_file), exist_ok=True)
    
    print(f"Saving sliced outputs to {args.output_file}...")
    with open(args.output_file, 'w', encoding='utf-8') as fout:
        for i, response_text in enumerate(generated_texts):
            
            pos = metadata[i]["pos_data"]
            neg = metadata[i]["neg_data"]
            
            # Stash the LLM's full XML response into both items for downstream parsing
            pos["agent1_slice_response"] = response_text
            neg["agent1_slice_response"] = response_text
            
            fout.write(json.dumps(pos) + '\n')
            fout.write(json.dumps(neg) + '\n')
            
    print("Agent 1 test run complete! Check the output file for <THINKING> and <SLICED_CODE> tags.")

if __name__ == "__main__":
    main()
