from typing import TypedDict

class AgentState(TypedDict):
    user_query: str
    error_code: str    # 解析节点提取出的错误码
    sop_context: str   # 检索节点找到的手册内容
    ai_analysis: str   # 诊断节点生成的报告
    final_action: str  # 决策结果