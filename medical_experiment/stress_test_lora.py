import requests
import json
import time
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from config import ExperimentConfig
from data_generator import DataGenerator
from client_info import ClientInfo

SYSTEM_PROMPT = '你是院前急救协同系统的调度大脑。请根据候选协助者画像（包括位置信息），在 PRIME、RUNNER、GUIDE 三类任务中各选择一个最合适的人。只返回紧凑 JSON，格式必须是 {"PRIME":"userId或null","RUNNER":"userId或null","GUIDE":"userId或null"}。'

def call_api(patient, candidates):
    patient_info = {
        "patient_id": patient["userId"],
        "patient_profession": patient.get("professionIdentity", ""),
        "candidates_summary": [
            {
                "userId": c["userId"],
                "professionIdentity": c.get("professionIdentity", ""),
                "healthCondition": c.get("healthCondition", ""),
                "distance": c.get("distance", 0),
            } for c in candidates
        ]
    }
    input_text = json.dumps(patient_info, ensure_ascii=False)
    
    url = "http://localhost:8008/v1/chat/completions"
    payload = {
        "model": "Qwen/Qwen2.5-7B-Instruct",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": input_text}
        ],
        "temperature": 0.0,
        "max_tokens": 100
    }
    
    try:
        start_time = time.time()
        resp = requests.post(url, json=payload, timeout=20)
        execution_time = (time.time() - start_time) * 1000
        if resp.status_code == 200:
            result_str = resp.json()["choices"][0]["message"]["content"]
            try:
                # 兼容可能的 Markdown json 代码块
                if result_str.startswith("```json"):
                    result_str = result_str[7:-3].strip()
                assignments = json.loads(result_str)
                return assignments, execution_time, None
            except json.JSONDecodeError as e:
                return None, execution_time, f"JSON parse error: {result_str}"
        else:
            return None, execution_time, f"API HTTP Error {resp.status_code}: {resp.text}"
    except Exception as e:
        return None, 0, str(e)

def main():
    config = ExperimentConfig()
    generator = DataGenerator(config)
    success = 0
    failed = 0
    scenarios = ["campus_emergency", "community_emergency", "workplace_emergency"]
    
    print(f"============================================================")
    print(f"开启单机模型强压测：目标1000次，并发8线程")
    print(f"============================================================")
    
    start_all = time.time()
    
    def worker(i):
        scenario = scenarios[i % len(scenarios)]
        generator.set_seed(i + 1234)
        cands = generator.generate_candidates(scenario, count=6)
        patient = {
            "userId": f"test_pt_{i}",
            "professionIdentity": "学生"
        }
        res, t, err = call_api(patient, cands)
        return res, t, err
        
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(worker, i): i for i in range(1000)}
        for future in as_completed(futures):
            res, t, err = future.result()
            if err or not res:
                failed += 1
                print(f"[*] 失败: {err}")
            else:
                success += 1
                if success % 50 == 0:
                    print(f"[!] 进度: 成功 {success}/1000, 耗时 {int(t)}ms")

    end_all = time.time()
    print("============================================================")
    print(f"测试完毕! 成功解析的 JSON 分配数: {success}")
    print(f"失败/格式错误数: {failed}")
    print(f"总耗时: {end_all - start_all:.2f} 秒")
    print(f"平均QPS: {1000 / (end_all - start_all):.2f}")

if __name__ == "__main__":
    main()
