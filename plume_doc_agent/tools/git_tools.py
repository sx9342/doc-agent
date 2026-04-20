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
