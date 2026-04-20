

## 第一阶段开发方案

### 目标与范围

跑通这条最小闭环：

```
CLI → Phidata Agent → LiteLLM → 豆包/DeepSeek → write_file → 输出标准 Plume Markdown
```

不接 RAG，不接图片，不接 Word 输出。只验证核心链路。

---

### 项目初始化

**目录结构（第一阶段只需这些）：**

```
doc-agent/
├── pyproject.toml
├── .env
├── .env.example
├── prompts/
│   └── doc_style.md          ← 核心规范文件
├── plume_doc_agent/
│   ├── __init__.py
│   ├── cli.py
│   ├── agent.py
│   └── tools/
│       ├── __init__.py
│       ├── file_tools.py
│       ├── git_tools.py
│       └── memory_tools.py   ← 第一阶段只做轮数计数，不接 RAG
└── output/                   ← 生成的 md 文件落地目录
```

**`pyproject.toml` 关键依赖：**

```toml
[project]
name = "doc-agent"
requires-python = ">=3.11"
dependencies = [
    "phidata>=2.7",
    "litellm>=1.40",
    "python-dotenv",
    "rich",          # CLI 美化输出
]

[project.scripts]
plume-doc = "plume_doc_agent.cli:main"
```

---

### 核心文件实现

**`.env` 配置：**

```env
# 二选一，先用 DeepSeek 验证（更便宜）
DEEPSEEK_API_KEY=sk-xxx
# VOLCENGINE_API_KEY=xxx
# VOLCENGINE_MODEL=ep-xxx   # 豆包需要 endpoint id

LLM_PROVIDER=deepseek       # 切换用
OUTPUT_DIR=./output
```

**`agent.py` 核心结构：**

```python
from phi.agent import Agent
from phi.model.litellm import LiteLLM
from pathlib import Path
from plume_doc_agent.tools.file_tools import read_file, write_file, list_dir
from plume_doc_agent.tools.git_tools import git_commit
import os

def load_doc_style() -> str:
    p = Path(__file__).parent.parent / "prompts" / "doc_style.md"
    return p.read_text(encoding="utf-8")

def create_agent() -> Agent:
    provider = os.getenv("LLM_PROVIDER", "deepseek")

    if provider == "deepseek":
        model = LiteLLM(model="deepseek/deepseek-chat")
    else:
        # 豆包：需要 volcengine endpoint id
        model = LiteLLM(
            model=f"openai/{os.getenv('VOLCENGINE_MODEL')}",
            api_base="https://ark.cn-beijing.volces.com/api/v3",
            api_key=os.getenv("VOLCENGINE_API_KEY"),
        )

    return Agent(
        model=model,
        system_prompt=load_doc_style(),
        tools=[read_file, write_file, list_dir, git_commit],
        show_tool_calls=True,
        markdown=True,
    )
```

> 豆包走 LiteLLM 的 `openai/` 前缀 + 自定义 `api_base`，因为火山引擎的 Ark 接口兼容 OpenAI 格式，这样不需要单独写适配器。

**`file_tools.py`：**

```python
from pathlib import Path
from phi.tools import tool
import os

OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "./output"))

@tool
def write_file(filename: str, content: str) -> str:
    """将内容写入 output 目录下的 Markdown 文件"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / filename
    path.write_text(content, encoding="utf-8")
    return f"已写入：{path.resolve()}"

@tool
def read_file(filepath: str) -> str:
    """读取文件内容"""
    return Path(filepath).read_text(encoding="utf-8")

@tool
def list_dir(dirpath: str = ".") -> str:
    """列出目录内容"""
    entries = list(Path(dirpath).iterdir())
    return "\n".join(str(e) for e in entries)
```

**`git_tools.py`：**

```python
import subprocess
from phi.tools import tool

@tool
def git_commit(message: str, dirpath: str = ".") -> str:
    """在指定目录执行 git add . && git commit"""
    try:
        subprocess.run(["git", "add", "."], cwd=dirpath, check=True)
        result = subprocess.run(
            ["git", "commit", "-m", message],
            cwd=dirpath, capture_output=True, text=True
        )
        return result.stdout or result.stderr
    except subprocess.CalledProcessError as e:
        return f"Git 错误：{e}"
```

**`cli.py`：**

```python
import argparse
import sys
from dotenv import load_dotenv
from rich.console import Console
from plume_doc_agent.agent import create_agent

load_dotenv()
console = Console()

def chat_loop(agent):
    console.print("[bold purple]Plume Doc Agent[/] 已启动，输入 exit 退出\n")
    turn = 0
    while True:
        try:
            user_input = input("你: ").strip()
        except (KeyboardInterrupt, EOFError):
            break
        if user_input.lower() in ("exit", "quit", "q"):
            break
        if not user_input:
            continue
        turn += 1
        agent.print_response(user_input, stream=True)
        # 第一阶段：8轮提醒（不自动存 RAG，留到第二阶段）
        if turn % 8 == 0:
            console.print("\n[dim]提示：对话已达8轮，建议总结当前进度。[/]\n")

def main():
    parser = argparse.ArgumentParser(prog="plume-doc")
    parser.add_argument("task", nargs="?", help="单次任务描述")
    parser.add_argument("--chat", action="store_true", help="进入交互模式")
    args = parser.parse_args()

    agent = create_agent()

    if args.chat or not args.task:
        chat_loop(agent)
    else:
        agent.print_response(args.task, stream=True)

if __name__ == "__main__":
    main()
```

---

### `doc_style.md` 核心内容框架

这个文件直接决定输出质量，建议参照你上传的示例文件，按以下结构填充：

```markdown
# Plume Doc Agent — 文档写作规范

## 角色定位
你是一个专为 VuePress Plume 主题服务的文档写作 Agent。
每次生成文档时，必须严格遵守以下规范。

## Frontmatter 规范
每篇文档必须包含以下字段：
- title（必填）
- tags（数组）
- createTime（格式：YYYY/MM/DD HH:mm:ss）
- permalink（格式：/分类/slug/）

## 文件命名规范
使用 kebab-case，与 permalink 的 slug 一致。

## 标题层级
- H1 不出现在正文（由 frontmatter title 替代）
- 从 H2 开始，最深到 H4

## 自定义容器语法
提示用 ::: tip，警告用 ::: warning，
错误用 ::: caution，折叠内容用 ::: details。
（参考具体语法见附录）

## 代码块规范
- 必须标注语言
- 重点行用 [!code highlight]
- 新增行用 [!code ++]，删除行用 [!code --]

## 写作风格
- 技术文档：准确、简洁，避免废话
- 教程类：步骤清晰，每步有明确产出
- 正文适当使用 Badge 和 Icon 组件增强可读性

## 工具调用规则
生成文档后，必须调用 write_file 将内容保存为 .md 文件。
文件名格式：{slug}.md
```

---

### 第一阶段验证清单

按顺序验证，任何一步失败立刻停下来排查：

1. `pip install -e .` 安装成功，`doc-agent --help` 能输出帮助
2. 配置 `.env`，运行 `doc-agent "写一篇介绍Vue3 Composition API的文档"` → LiteLLM 能调通 DeepSeek
3. Agent 调用 `write_file` 工具，`output/` 目录下出现 `.md` 文件
4. 生成的文件有完整 frontmatter + 正确的 Plume 容器语法
5. `--chat` 模式下多轮对话正常，8轮提示出现
6. 切换 `LLM_PROVIDER=doubao`，重跑步骤 2-4，验证豆包链路

---

### 一个容易踩的坑

Phidata 的 `@tool` 装饰器在不同版本有变化，如果遇到工具注册失败，用这种更保守的写法：

```python
from phi.tools.function import Function

write_file_tool = Function(
    name="write_file",
    description="将内容写入 Markdown 文件",
    entrypoint=write_file,
)
```

然后在 `Agent(tools=[write_file_tool, ...])` 里传入。
