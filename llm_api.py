"""LLM 接口封装：调用本地 Ollama 服务"""
import requests

from config import OLLAMA_BASE_URL, MODEL_NAME, REQUEST_TIMEOUT


def call_llm(system_prompt: str, user_prompt: str) -> str:
    """
    调用本地 Ollama 大模型

    :param system_prompt: 系统提示词
    :param user_prompt: 用户问题
    :return: 模型完整回答文本；异常时返回错误描述文本
    """
    payload = {
        "model": MODEL_NAME,
        "system": system_prompt,
        "prompt": user_prompt,
        "stream": False,
    }
    try:
        resp = requests.post(OLLAMA_BASE_URL, json=payload, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        return data.get("response", "")
    except requests.exceptions.RequestException as e:
        err_msg = f"调用LLM接口异常：{str(e)}"
        print(err_msg)
        return err_msg


if __name__ == "__main__":
    from config import SYS_PROMPT
    res = call_llm(SYS_PROMPT, "1+1等于几")
    print("模型输出：", res)