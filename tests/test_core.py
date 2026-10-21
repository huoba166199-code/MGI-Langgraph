import sys
import os

# 【最核心修复】：必须在导入 agent 模块之前，注入环境变量！
# 否则 graph.py 里的 ChatDeepSeek() 一初始化就会因为找不到 Key 而崩溃。
os.environ["LLM_API_KEY"] = "fake_key_for_testing"
os.environ["LLM_API_BASE"] = "https://api.deepseek.com"
os.environ["LLM_MODEL"] = "deepseek-chat"

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent.rag import search_manual
from agent.graph import route_decision_node, parse_input_node

def test_route_high_risk():
    state = {"error_code": "ERR-503", "user_query": ""}
    assert route_decision_node(state)["final_action"] == "create_ticket"

def test_route_normal_risk():
    state = {"error_code": "ERR-101", "user_query": ""}
    assert route_decision_node(state)["final_action"] == "reply"

def test_parse_input_extraction():
    state = {"user_query": "我的机器报了 ERR-503 错误"}
    assert parse_input_node(state)["error_code"] == "ERR-503"

def test_parse_input_unknown():
    state = {"user_query": "机器坏了"}
    assert parse_input_node(state)["error_code"] == "UNKNOWN"

def test_rag_exact_match():
    assert "ERR-101" in search_manual("ERR-101")