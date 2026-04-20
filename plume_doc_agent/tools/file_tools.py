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
