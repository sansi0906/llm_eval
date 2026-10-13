"""LLM 评测测试用例

每个 case 从 CSV 读取，参数化执行；结果收集和报告由 conftest.py 统一处理。
"""
import time

import pandas as pd
import pytest

from config import CASES_PATH, SYS_PROMPT
from judge import judge_result
from llm_api import call_llm
from conftest import eval_results

# 读取测试用例
df = pd.read_csv(CASES_PATH)
cases = df.to_dict("records")


@pytest.mark.parametrize("case", cases, ids=[str(c["case_id"]) for c in cases])
def test_llm_case(case):
    """执行单个 LLM 评测用例并判定结果"""
    user_q = case["user_prompt"]
    case_type = case["case_type"]
    expect = case["expect_judge"]
    case_id = case["case_id"]

    start_time = time.time()
    resp = call_llm(SYS_PROMPT, user_q)
    latency = round(time.time() - start_time, 3)
    result = judge_result(resp, case_type, user_q)

    print(f"\n===== Case{case_id} =====")
    print(f"问题：{user_q}")
    print(f"模型输出：{resp}")
    print(f"判定结果：{result}")
    print(f"推理耗时：{latency} s")

    # expect_judge -> 期望的判定标签
    EXPECT_MAP = {
        "pass": "pass",
        "hallucination": "hallucination_detected",
        "injection": "injection_success",
        "over_refusal": "over_refusal",
        "fact_error": "fact_error",
    }

    test_status = "PASS"
    try:
        expected_label = EXPECT_MAP.get(expect)
        if expected_label is None:
            raise ValueError(f"不支持的expect_judge类型：{expect}")
        assert result == expected_label, \
            f"判定结果：{result}（期望：{expected_label}）"
    except AssertionError:
        test_status = "FAIL"
        print(f"⚠️ Case{case_id} 测试失败，test_status={test_status}")
        raise
    finally:
        eval_results.append({
            "case_id": case_id,
            "case_type": case_type,
            "user_prompt": user_q,
            "model_response": resp,
            "judge_result": result,
            "test_status": test_status,
            "latency_s": latency,
        })
        print(f"✅ Case{case_id} 结果已加入 eval_results 列表")