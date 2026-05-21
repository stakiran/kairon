"""kairon: LLM-based context-aware scheduler.

Windows タスクスケジューラから定期的に起動される想定。
dispatcher.md を claude -p に投げて動かすべき agent 名を得て、
各 agent を fire-and-forget で起動する。
"""
import subprocess
from pathlib import Path

HERE = Path(__file__).parent
DISPATCHER_MD = HERE / "dispatcher.md"
AGENTS_DIR = HERE / "agents"

CLAUDE_COMMON = ["claude", "-p", "--permission-mode", "dontAsk"]
DISPATCHER_TOOLS = ["--allowedTools", "Read", "Glob"]
AGENT_TOOLS = [
    "--allowedTools",
    "Read", "Write", "Edit", "Glob", "Grep",
    "WebSearch", "WebFetch", "Bash(echo:*)",
]


def dispatch() -> list[str]:
    """dispatcher.md を claude -p に渡し、動かすべき agent 名のリストを返す。"""
    prompt = DISPATCHER_MD.read_text(encoding="utf-8")
    result = subprocess.run(
        CLAUDE_COMMON + DISPATCHER_TOOLS,
        input=prompt,
        capture_output=True,
        text=True,
        cwd=HERE,
        encoding="utf-8",
    )
    return [ln.strip() for ln in result.stdout.splitlines() if ln.strip()]


def fire(name: str) -> None:
    """agent を fire-and-forget で起動。stdin に agent.md を流し込んで切り離す。"""
    agent_md = AGENTS_DIR / f"{name}.md"
    if not agent_md.exists():
        return
    proc = subprocess.Popen(
        CLAUDE_COMMON + AGENT_TOOLS,
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd=HERE,
        creationflags=subprocess.DETACHED_PROCESS
                      | subprocess.CREATE_NEW_PROCESS_GROUP,
    )
    proc.stdin.write(agent_md.read_bytes())
    proc.stdin.close()


def main() -> None:
    for name in dispatch():
        fire(name)


if __name__ == "__main__":
    main()
