from phi.tools import tool

_turn_count = 0

@tool
def get_turn_count() -> str:
    """返回当前对话轮数"""
    return str(_turn_count)
