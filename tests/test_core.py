import sys
import os

# 【核心修复】将项目根目录加入 sys.path，确保 pytest 能识别 agent 模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from agent.rag import search_manual
from agent.graph import route_decision_node, parse_input_node

# ==========================================
# 测试 1: 路由与规则拦截 (最核心的安全底线)
# ==========================================
def test_route_high_risk():
    """测试：命中高危错误码 ERR-503 必须强制派单"""
    state = {"error_code": "ERR-503", "user_query": ""}
    result = route_decision_node(state)
    assert result["final_action"] == "create_ticket"

def test_route_normal_risk():
    """测试：普通错误码必须放行，走常规回复"""
    state = {"error_code": "ERR-101", "user_query": ""}
    result = route_decision_node(state)
    assert result["final_action"] == "reply"

# ==========================================
# 测试 2: 特征提取 (正则解析)
# ==========================================
def test_parse_input_extraction():
    """测试：从自然语言中精准提取错误码"""
    state = {"user_query": "我的机器报了 ERR-503 错误，怎么办？"}
    result = parse_input_node(state)
    assert result["error_code"] == "ERR-503"

def test_parse_input_unknown():
    """测试：无错误码时的容错"""
    state = {"user_query": "机器坏了"}
    result = parse_input_node(state)
    assert result["error_code"] == "UNKNOWN"

# ==========================================
# 测试 3: 本地 RAG 检索 (BM25)
# ==========================================
def test_rag_exact_match():
    """测试：BM25 能否精确匹配到错误码对应的手册内容"""
    result = search_manual("ERR-101")
    assert "ERR-101" in result

def test_rag_fuzzy_match():
    """测试：BM25 能否进行模糊语义召回"""
    result = search_manual("流体压力")
    assert "ERR-503" in result or "压力" in result