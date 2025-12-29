# AI Research Agent

> **A controllable, multi-mode AI research system that engineers research methodology — not just text generation.**

---

## ✨ 项目简介

**AI Research Agent** 是一个将**研究方法论工程化**的自动化研究系统，而不是一个"万能写报告的 AI"。

在实践中我发现，不同研究问题本质上需要**完全不同的研究范式**：

* 竞品对比
* 市场分析
* 早期概念判断

试图用一个统一的 Prompt 或 Agent 处理所有问题，必然导致**不稳定、胡编或结构失控**。

因此，本项目引入 **Research Modes（A / B / C）**，并为每种模式设计了：

* 不同的执行流程
* 不同的结构约束
* 不同的失败兜底策略

目标是让 LLM 在真实系统中做到：
**可控、稳定、可解释、可交付**。

---

## 🎯 核心特性

### 🔹 Research Mode 分类

系统会先判断用户问题的研究类型，再选择合适的执行策略：

| Mode       | 研究类型       | 特点            |
| ---------- | ---------- | ------------- |
| **Mode A** | 已知竞品对比     | 强结构、零容错、必须可对比 |
| **Mode B** | 成熟/半成熟市场分析 | 表格可选，强调趋势与格局  |
| **Mode C** | 概念/早期市场判断  | 禁止表格，输出判断型结论  |

---

### 🔹 Mode A：结构可控的竞品对比（项目最大亮点）

**挑战**

* 用户预期极高（竞品对比不能错）
* 强结构约束（多产品 × 多维度）
* LLM 天生不服从复杂结构

**解决方案**
引入 **三阶段生成（Three-Phase Generation）**：

```text
Phase 1：生成"对比表骨架"（仅结构，5竞品 × 5维度）
Phase 2：在已存在结构中逐格填充内容（每格 ≤20字）
Phase 3：生成总结（适合谁/不适合谁）
```

* 结构由程序校验
* 内容由模型填充
* Schema 向 LLM 妥协（使用嵌套字典，而非对象列表）

这从工程层面解决了：

> "LLM 语义正确但结构失控"的问题

---

### 🔹 Mode B：理性市场分析，而非参数堆砌

* 不强制生成对比表
* 重点在于：
  * 市场格局
  * 阵营/路线
  * 关键趋势
* 接受信息不完整与不确定性

---

### 🔹 Mode C：早期概念的"判断型研究"

* 禁止生成竞品表
* 输出重点是：
  * 市场是否真实存在
  * 为什么尚未成熟
  * 关键变量与行动建议

在该模式下，**"无法对比"本身就是重要结论**。

---

## 🧠 设计理念

### 1️⃣ 研究 ≠ 写作

本项目不追求"写得像报告"，而追求：

* 研究方法正确
* 结构稳定
* 结果可用

---

### 2️⃣ 失败是系统的一部分

不同模式对失败的态度不同：

* Mode A：不允许失败
* Mode B：允许降级
* Mode C：失败即结论

---

### 3️⃣ 结构优先于内容

只要允许 LLM 同时"决定结构 + 写内容"，结构一定会被破坏。
因此本项目始终坚持：

> **Structure first, content second.**

---

## 🧱 系统架构

```text
User Query
   ↓
Research Mode Classifier
   ↓
┌───────────────┬───────────────┬───────────────┐
│    Mode A     │    Mode B     │    Mode C     │
│ Three-phase   │ Single-pass   │ Judgment-only │
│ generation    │ analysis      │ reasoning     │
└───────────────┴───────────────┴───────────────┘
   ↓
UI-friendly normalized output
```

---

## 🧩 技术栈

### 后端
- **Python 3.11+** + **FastAPI**
- **LangGraph** - Agent 工作流编排
- **Pydantic** - Schema 校验
- **SQLite** - 任务持久化

### 前端
- **Next.js 16** + **React 19**
- **React Query** - 数据获取
- **Framer Motion** - 动画
- **react-markdown + remark-gfm** - Markdown 渲染

### LLM
- 支持 **OpenAI 兼容 API**（GPT-4, Claude, Gemini 等）

---

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/qd-maker/ai-research-agent.git
cd ai-research-agent
```

### 2. 安装依赖

```bash
# 后端
pip install -r requirements.txt

# 前端
cd web && npm install
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 填入你的 LLM API 配置
```

### 4. 启动服务

```bash
# 后端
uvicorn app.main:app --reload

# 前端（新终端）
cd web && npm run dev
```

访问 http://localhost:3000

---

## 📊 示例

### Mode A（竞品对比）

* **Notion 主要竞品对比**
* 多产品 × 多维度表格
* 明确"适合谁 / 不适合谁"

### Mode B（市场分析）

* **2024 AI 大模型市场格局**
* 阵营 / 路线 / 趋势分析
* 不强制参数表

### Mode C（概念判断）

* **Web3 + AI 市场前景**
* 是否成立 + 原因 + 变量
* 无竞品表

---

## 🚀 使用场景

* 产品经理进行竞品研究
* 投资/战略分析中的市场判断
* 开发者验证 AI 在研究任务中的可控性
* 面试/展示一个"非玩具级"的 LLM 项目

---

## 📌 项目亮点总结

> **这是一个把"研究方法论"而不是"Prompt 技巧"工程化的 AI 系统。**

---

## 🔮 后续方向

* Agent + 工具（搜索 / 数据源）增强
* UI 层可视化增强（卡片 / 维度切片）
* 更精细的 Mode B / C 演进
* 多语言支持

---

## 🤝 致谢

本项目的设计思路来源于对真实 AI Research 产品失败案例的反思：

**不是模型不够强，而是系统没有告诉模型"该怎么思考"。**

---

## 📄 License

MIT License
