# 项目上下文信息

- AI Research Agent 项目骨架已完成构建。技术栈：FastAPI + LangGraph + Crawl4AI + OpenAI。包含完整的生产级特性：异步架构、结构化日志、错误处理、重试逻辑、数据库持久化、Guardrails（step limit、URL limit、并发控制、超时）。项目结构：40+ 文件，~3000+ 行代码，7 个 API 端点，7 个 LangGraph 节点。Search tool 当前为 stub，需集成真实搜索 API。首次运行需：pip install -r requirements.txt && playwright install，配置 .env 中的 OPENAI_API_KEY。
