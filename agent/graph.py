import os
import re
import requests  # 用于模拟真实派单
from langgraph.graph import StateGraph, END
from langchain_deepseek import ChatDeepSeek
from langchain_core.messages import HumanMessage
from .state import AgentState
from .rag import search_manual
from dotenv import load_dotenv

load_dotenv()

llm = ChatDeepSeek(
    api_key=os.getenv("LLM_API_KEY"),
    api_base=os.getenv("LLM_API_BASE"),
    model=os.getenv("LLM_MODEL"),
    temperature=0.1
)


# ================= 定义独立节点 =================

def parse_input_node(state: AgentState):
    """节点 1：解析用户输入，提取特征"""
    print("📌 [节点1] 正在解析输入...")
    user_input = state["user_query"]
    # 尝试提取错误码
    match = re.search(r"ERR-\d{3}", user_input)
    error_code = match.group(0) if match else "UNKNOWN"
    return {"error_code": error_code}


def retrieve_sop_node(state: AgentState):
    """节点 2：根据提取的特征去检索手册"""
    print(f"📌 [节点2] 正在检索手册，错误码: {state['error_code']}...")
    sop = search_manual(state["user_query"])
    return {"sop_context": sop}


def diagnose_node(state: AgentState):
    """节点 3：诊断专家（调用大模型）"""
    print("📌 [节点3] 诊断专家正在生成排障建议...")
    prompt = f"""
    你是华大智造的资深售后工程师。
    用户报错：{state['user_query']}
    维修手册：{state['sop_context']}
    请给出详细的排障建议（字数控制在200字以内）。
    """
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"ai_analysis": response.content}


def route_decision_node(state: AgentState):
    """节点 4：规则引擎路由（决定是否高危）"""
    print("📌 [节点4] 规则引擎正在判定红线...")
    HIGH_RISK_CODES = ["ERR-503", "ERR-999"]
    is_high_risk = state["error_code"] in HIGH_RISK_CODES

    if is_high_risk:
        print("🚨 触发企业红线，必须人工审批！")
        return {"final_action": "create_ticket"}
    return {"final_action": "reply"}


def ticket_node(state: AgentState):
    """节点 5：高危工单生成（真实调用 Tool）"""
    print("📌 [节点5] 正在调用发单工具...")
    # 这里模拟调用钉钉/企业微信的 Webhook
    # requests.post("https://oapi.dingtalk.com/robot/send?...", json={"msg": "工单"})
    return {"ai_analysis": state["ai_analysis"]}  # 保持原有的分析文本


# ================= 构建图 =================

workflow = StateGraph(AgentState)

# 注册节点
workflow.add_node("parse", parse_input_node)
workflow.add_node("retrieve", retrieve_sop_node)
workflow.add_node("diagnose", diagnose_node)
workflow.add_node("route", route_decision_node)
workflow.add_node("ticket", ticket_node)

# 编排路由
workflow.set_entry_point("parse")
workflow.add_edge("parse", "retrieve")
workflow.add_edge("retrieve", "diagnose")
workflow.add_edge("diagnose", "route")

# 条件路由：根据 final_action 决定下一步
workflow.add_conditional_edges(
    "route",
    lambda x: x["final_action"],
    {
        "create_ticket": "ticket",
        "reply": END
    }
)
workflow.add_edge("ticket", END)

mgi_agent = workflow.compile()