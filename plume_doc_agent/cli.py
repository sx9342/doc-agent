import argparse
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
