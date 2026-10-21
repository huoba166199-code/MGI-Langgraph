# MGI 测序仪智能排障 Agent

![CI Status](https://github.com/huoba166199-code/MGI-Langgraph/actions/workflows/ci.yml/badge.svg)

这是一个面向华大智造（MGI）DNBSEQ 系列测序仪的企业级智能排障系统。采用 LangGraph 状态机编排，结合大模型与硬规则拦截，实现业务闭环。

## 核心特性
- 多节点状态机编排
- 规则与 AI 双重路由
- Human-in-the-loop 人工在环
- SQLite 状态持久化
- Docker 一键交付

## 快速开始
``bash
git clone https://github.com/huoba166199-code/MGI-Langgraph.git
cd MGI-Langgraph
docker compose up -d --build
``
