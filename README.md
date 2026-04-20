# Plume Doc Agent

为 VuePress Plume 主题自动生成标准 Markdown 文档的 CLI 工具。

## 功能

- 单次任务：输入描述，自动生成符合 Plume 规范的 `.md` 文件
- 交互模式：多轮对话，逐步完善文档内容
- 自动写文件：生成结果直接落地到 `output/` 目录

## 安装

```bash
pip install -e .
```

## 配置

复制 `.env.example` 为 `.env` 并填写：

```env
LLM_API_KEY=sk-xxx
LLM_BASE_URL=xxxx
LLM_MODEL=xxxx
OUTPUT_DIR=./output
```

## 使用

```bash

# 交互模式
plume-doc --chat
```

生成的文件保存在 `output/` 目录下。

## 项目结构

```
doc-agent/
├── prompts/
│   └── doc_style.md        # 文档规范 & system prompt
├── plume_doc_agent/
│   ├── cli.py
│   ├── agent.py
│   └── tools/
│       ├── file_tools.py
│       ├── git_tools.py
│       └── memory_tools.py
└── output/                 # 生成的 md 文件
```

## 依赖

- [phidata](https://github.com/phidatahq/phidata) — Agent 框架
- [rich](https://github.com/Textualize/rich) — CLI 美化输出
