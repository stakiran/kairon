"""kairon: LLM-based context-aware scheduler.

Windows タスクスケジューラから定期的に起動される想定。
dispatcher.md を claude -p に投げて動かすべき agent 名を得て、
各 agent を fire-and-forget で起動する。

各 claude 起動時に現在日時を --append-system-prompt で注入する。
これにより、claude 側は「現在日時」を確実に参照できる
（Bash で date を叩く権限が不要になる）。
"""
import subprocess
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).parent
DISPATCHER_MD = HERE / "dispatcher.md"
AGENTS_DIR = HERE / "agents"

CLAUDE_BASE = ["claude", "-p", "--permission-mode", "dontAsk"]
DISPATCHER_TOOLS = ["--allowedTools", "Read", "Glob"]
AGENT_TOOLS_DEFAULT = [
    "Read", "Write", "Edit", "Glob", "Grep",
    "WebSearch", "WebFetch",
]


def time_args() -> list[str]:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return ["--append-system-prompt", f"現在日時: {now}"]


def parse_frontmatter(md_text: str) -> dict[str, str]:
    if not md_text.startswith("---"):
        return {}
    parts = md_text.split("---", 2)
    if len(parts) < 3:
        return {}
    fm: dict[str, str] = {}
    for line in parts[1].strip().splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    return fm


def agent_tool_args(fm: dict[str, str]) -> list[str]:
    extra = [t.strip() for t in fm.get("tools", "").split(",") if t.strip()]
    return ["--allowedTools", *AGENT_TOOLS_DEFAULT, *extra]


def is_truthy(v: str) -> bool:
    return v.strip().lower() in ("true", "yes", "on", "1")


def dispatch() -> list[str]:
    prompt = DISPATCHER_MD.read_text(encoding="utf-8")
    result = subprocess.run(
        CLAUDE_BASE + DISPATCHER_TOOLS + time_args(),
        input=prompt,
        capture_output=True,
        text=True,
        cwd=HERE,
        encoding="utf-8",
    )
    return [ln.strip() for ln in result.stdout.splitlines() if ln.strip()]


def fire(name: str) -> None:
    agent_md = AGENTS_DIR / f"{name}.md"
    if not agent_md.exists():
        return
    md_text = agent_md.read_text(encoding="utf-8")
    fm = parse_frontmatter(md_text)

    if is_truthy(fm.get("console", "")):
        flags = subprocess.CREATE_NEW_CONSOLE
        stdio = None
        extra_args = ["--verbose"]
    else:
        flags = (subprocess.DETACHED_PROCESS
                 | subprocess.CREATE_NEW_PROCESS_GROUP)
        stdio = subprocess.DEVNULL
        extra_args = []

    proc = subprocess.Popen(
        CLAUDE_BASE + extra_args + agent_tool_args(fm) + time_args(),
        stdin=subprocess.PIPE,
        stdout=stdio,
        stderr=stdio,
        cwd=HERE,
        creationflags=flags,
    )
    proc.stdin.write(md_text.encode("utf-8"))
    proc.stdin.close()


def main() -> None:
    for name in dispatch():
        fire(name)


if __name__ == "__main__":
    main()
