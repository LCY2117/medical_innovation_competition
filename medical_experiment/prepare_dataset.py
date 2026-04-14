import json
import glob
import os

# Find the JSON file
input_files = glob.glob('/home/lcy/medical_competition/medical_experiment/stress_test_results/stress_test_*.json')

if not input_files:
    print("No stress test JSON files found.")
    exit(1)

# Pick the first one
input_file = input_files[0]
print(f"Reading from {input_file}...")

with open(input_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

results = data.get('results', [])
dataset = []

for r in results:
    if "assignments" not in r:
        continue
        
    patient_info = {
        "patient_id": r.get("patient_id"),
        "patient_profession": r.get("patient_profession"),
        "candidates_summary": r.get("candidates_summary", [])
    }
    
    # Format according to Alpaca standard
    input_text = json.dumps(patient_info, ensure_ascii=False)
    output_text = json.dumps(r.get("assignments"), separators=(',', ':'), ensure_ascii=False)
    
    dataset.append({
        "instruction": "你是院前急救协同系统的调度大脑。请根据候选协助者画像（包括位置信息），在 PRIME、RUNNER、GUIDE 三类任务中各选择一个最合适的人。只返回紧凑 JSON，格式必须是 {\"PRIME\":\"userId或null\",\"RUNNER\":\"userId或null\",\"GUIDE\":\"userId或null\"}。",
        "input": input_text,
        "output": output_text
    })

output_path = '/home/lcy/medical_competition/medical_experiment/dispatch_dataset.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(dataset, f, ensure_ascii=False, indent=2)

print(f"Generated {output_path} with {len(dataset)} examples.")