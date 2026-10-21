# MGI 测序仪智能排障 Agent — 工程踩坑与解决文档

本项目基于 LangGraph 构建多节点状态流转，以下是开发与部署过程中的核心避坑指南。

## 一、 环境与依赖层

**Q1：为什么在 WSL 下运行 Streamlit 频繁卡死，尤其是执行数据库操作时？**
- **原因**：项目最初存放在 Windows 挂载盘（`/mnt/d/...`）。WSL 跨文件系统读写 SQLite 数据库（ChromaDB 的底层）时，文件锁机制极容易导致 IO 死锁。
- **解决**：将整个项目源码复制到 WSL 原生目录（`~/MGI-Device-Agent`），原生 ext4 文件系统下的读写速度提升 10 倍以上，彻底解决卡死。

**Q2：ChromaDB 初始化时报错 `ModuleNotFoundError: No module named 'torchvision'`？**
- **原因**：`transformers` 库在探测某些图像处理模块时会隐性依赖 `torchvision`，即使当前业务只做纯文本 RAG。
- **解决**：执行 `pip install torchvision --index-url https://download.pytorch.org/whl/cpu` 补齐依赖。

**Q3：使用 ChromaDB 时提示 `Embedding function conflict`？**
- **原因**：本地已经存在旧的 `chroma_db` 目录，且其配置中的向量化模型（如 default）与当前代码新引入的模型（如 sentence_transformer）冲突。
- **解决**：直接执行 `rm -rf chroma_db` 删除旧库，让代码重新生成即可；生产环境则需采用新建 Collection 并灰度双写的策略。

**Q4：HuggingFace 模型下载龟速，卡在 17KB/s？**
- **原因**：ChromaDB 默认的 ONNX 模型下载不经过 `HF_ENDPOINT` 镜像，直连海外服务器极慢。
- **解决**：放弃 `DefaultEmbeddingFunction`，改用 `SentenceTransformerEmbeddingFunction`，并在代码最顶端强制设置 `os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"`。

## 二、 框架与逻辑层

**Q5：为什么要从传统的 LangChain 切换为 LangGraph？**
- **原因**：测序仪排障涉及复杂的业务逻辑（如：软件报错需查手册，硬件报错需派工单）。传统的 Chain 是单向直线执行，难以处理条件分支、循环和中断。
- **解决**：使用 LangGraph 构建 `StateGraph`，通过定义 State（状态）和 `Conditional Edges`（条件边），实现精确的路由分发。

**Q6：如何实现工作流的“人工审批”暂停与恢复？**
- **解决**：在编译图时引入 `MemorySaver` 并配置 `interrupt_before=["create_ticket"]`。当状态机流转到派单节点前会强制挂起；前端捕获挂起状态后渲染审批按钮，用户点击批准后，通过传入 `Command(resume=True)` 恢复执行。


---

## 三、 LangGraph 状态流转与 Streamlit 交互踩坑

**Q7：LangGraph 的 `interrupt_before` 或 `interrupt()` 失效，高危节点被直接穿透执行？**
- **原因**：LangGraph 的不同版本对中断 API 的底层实现有差异，在某些版本中，由于 checkpoint（持久化状态）的污染，或者与 Streamlit 的异步刷新机制冲突，会导致中断信号被忽略。
- **解决**：放弃直接依赖框架的底层中断 API。改为**“纯代码级路由拦截”**。让图在到达高危节点时直接返回一个特殊标识（如 `action=create_ticket`），由前端接管挂起逻辑，彻底规避底层 Bug。

**Q8：使用 DeepSeek API 时报错 `This response_format type is unavailable now (json_schema)`？**
- **原因**：LangChain 的 `with_structured_output` 默认使用 OpenAI 的严格 `json_schema` 模式，但部分国产大模型目前只支持基础的 JSON 模式。
- **解决**：引入 `langchain-deepseek` 官方库，使用 `ChatDeepSeek` 类代替 `ChatOpenAI`；或者采用文本解析（如正则提取）的方式获取模型输出。

**Q9：系统卡死在 `Running get_chroma_collection()`，且没有任何报错？**
- **原因**：WSL 跨系统（`/mnt/d/`）文件读写极慢，导致 SQLite（ChromaDB底层）死锁；或者首次下载 HuggingFace 的 ONNX 向量模型时，因为网络问题无限挂起。
- **解决**：彻底抛弃 ChromaDB。对于小型 PoC 项目，直接将完整手册文本作为上下文注入 Prompt（全量上下文注入），利用现代大模型强大的长上下文能力，实现 0 秒级响应，彻底消除了向量库带来的性能瓶颈和网络依赖。

**Q10：Streamlit 页面出现“幽灵刷新”，一键发送就直接自动完成了审批？**
- **原因**：Streamlit 的 `st.chat_input` 或 `st.form` 在触发时，会导致页面重新加载。如果状态管理逻辑存在漏洞，按钮会被意外触发。
- **解决**：使用 `st.session_state` 严格隔离“等待输入”和“等待审批”两个状态。当处于审批状态时，**直接从 DOM 中隐藏输入框**，防止并发提交。

