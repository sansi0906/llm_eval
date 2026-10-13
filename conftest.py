"""pytest session 级共享 fixture、结果收集与报告生成"""
import pytest
import pandas as pd

from config import get_run_dir

# 全局结果列表，由各测试用例填充
eval_results = []

# 本次运行的报告目录，在 pytest_configure 中初始化
RUN_DIR = None


def pytest_configure(config):
    """pytest 启动时创建本次运行的递增报告目录，并启用 HTML 报告"""
    global RUN_DIR
    RUN_DIR = get_run_dir()
    if config.pluginmanager.has_plugin("html"):
        config.option.htmlpath = str(RUN_DIR / "eval_report.html")
        config.option.self_contained_html = True


@pytest.fixture(scope="session", autouse=True)
def save_after_all_cases():
    """所有用例执行完成后，自动汇总并保存报告"""
    yield
    _save_reports()


def _save_reports():
    """写出明细 CSV、汇总 CSV 到本次运行目录"""
    if not eval_results:
        print(f"\n⚠️ 没有收集到任何用例结果，报告目录：{RUN_DIR}")
        return

    result_df = pd.DataFrame(eval_results)
    result_path = RUN_DIR / "eval_result.csv"
    result_df.to_csv(result_path, index=False, encoding="utf-8-sig")

    total = len(eval_results)
    pass_cnt = sum(1 for item in eval_results if item["test_status"] == "PASS")
    fail_cnt = total - pass_cnt
    pass_rate = round(pass_cnt / total * 100, 2)
    latencies = [item["latency_s"] for item in eval_results]
    avg_latency = round(sum(latencies) / len(latencies), 3)
    max_latency = round(max(latencies), 3)
    min_latency = round(min(latencies), 3)

    print("\n==================== 评测汇总统计 ====================")
    print(f"总用例数：{total}")
    print(f"PASS数量：{pass_cnt}")
    print(f"FAIL数量：{fail_cnt}")
    print(f"通过率：{pass_rate} %")
    print(f"平均推理耗时：{avg_latency} s")
    print(f"最大推理耗时：{max_latency} s")
    print(f"最小推理耗时：{min_latency} s")
    print("=======================================================")
    print(f"📁 本次报告目录：{RUN_DIR}")
    print(f"✅ 明细结果已保存至 {result_path}")

    summary_data = [{
        "total_cases": total,
        "pass_count": pass_cnt,
        "fail_count": fail_cnt,
        "pass_rate_percent": pass_rate,
        "avg_latency_s": avg_latency,
        "max_latency_s": max_latency,
        "min_latency_s": min_latency,
    }]
    summary_df = pd.DataFrame(summary_data)
    summary_path = RUN_DIR / "eval_summary.csv"
    summary_df.to_csv(summary_path, index=False, encoding="utf-8-sig")
    print(f"✅ 汇总指标保存到 {summary_path}")
    print(f"✅ HTML 报告保存到 {RUN_DIR / 'eval_report.html'}")