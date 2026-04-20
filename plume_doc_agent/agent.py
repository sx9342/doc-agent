from phi.agent import Agent
from phi.model.openai.like import OpenAILike
from pathlib import Path
from plume_doc_agent.tools.file_tools import read_file, write_file, list_dir
from plume_doc_agent.tools.git_tools import git_commit
import os

def load_doc_style() -> str:
    p = Path(__file__).parent.parent / "prompts" / "doc_style.md"
    return p.read_text(encoding="utf-8")

def create_agent() -> Agent:
    model = OpenAILike(
        id=os.getenv("LLM_MODEL", "Pro/zai-org/GLM-4.7"),
        api_key=os.getenv("LLM_API_KEY"),
        base_url=os.getenv("LLM_BASE_URL", "https://api.siliconflow.cn/v1"),
    )

    return Agent(
        model=model,
        system_prompt=load_doc_style(),
        tools=[read_file, write_file, list_dir, git_commit],
        show_tool_calls=True,
        markdown=True,
    )
