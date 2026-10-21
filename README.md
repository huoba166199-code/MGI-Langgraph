# 🧬 MGI 测序仪智能排障 Agent (MGI Device Diagnostics Agent)

![CI Status](https://github.com/huoba166199-code/MGI-Langgraph/actions/workflows/ci.yml/badge.svg)

这是一个面向华大智造（MGI）DNBSEQ 系列测序仪的**企业级智能排障系统**。系统采用 **LangGraph 状态机**编排，结合大模型语义分析与底层硬规则拦截，实现了从“报错输入”到“AI 诊断”再到“人工在环审批（HITL）”的完整业务闭环。

## ✨ 核心特性
- **多节点状态机编排**：基于 LangGraph 构建 `Parse -> Retrieve -> Diagnose -> Route` 拓扑，完美支持条件分支与状态挂起。
- **规则与 AI 双重路由**：大模型负责生成排障建议，底层代码（硬拦截）负责判定高危红线，彻底杜绝 AI 幻觉导致的安全事故。
- **Human-in-the-loop (人工在环)**：高危故障自动挂起，强制要求科室主管进行审批（RBAC 权限隔离）。
- **持久化与断点续传**：基于 SQLite 实现会话状态落盘，刷新页面甚至重启服务都不会丢失现场。
- **Docker 一键交付**：彻底解决本地环境依赖，随时可在离线内网部署。

## 🚀 快速开始
```bash
git clone https://github.com/huoba166199-code/MGI-Langgraph.git
cd MGI-Langgraph
cp .env.example .env # 请填入真实的 LLM_API_KEY
docker compose up -d --build
