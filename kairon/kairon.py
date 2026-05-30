"""kairon-sta: 条件指定ベースのスケジューラー（参考実装）。

cron が「時刻」を指定するのに対し、kairon は「条件」を指定する。
本体（このファイル）は、呼ばれたら agents.md を走査し、現在の文脈
（現在日時・各エージェントのログ）を踏まえて、当てはまるエージェント
だけを起動する。

設計の要点:

- 起動するのは **単一の `claude -p` のみ**。
  起動対象のエージェントごとにサブプロセスとして claude を起動しない。
  パフォーマンスとトラブルシューティングの観点から、これは厳守する。
- そのため単一の claude に **JSE フロー**（judgement → strategy →
  execution）を委ねる。すなわち、
    1. judgement : 各エージェントの condition を評価し、起動対象を判断
    2. strategy  : 起動対象をどう処理するかの戦略を練る
    3. execution : 戦略どおりに、各エージェントの本文を実行する
  各エージェントの処理も、この単一の claude 自身が担う。
  （サブエージェントなど Claude Code 内部の並列ロジックの利用は可）
- セキュリティ上、スクリプトやコマンドは実行しない。
  許可ツールは Read / Write / Edit / Glob / Grep / WebSearch / WebFetch のみ。

本体がしないこと:

- 自身の呼び出し方の設定（Windows スケジューラーへの登録など）。
  どう呼ぶかは利用者の運用であり、kairon-sta は関知しない。
"""
import subprocess
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).parent
AGENTS_MD = HERE / "agents.md"

CLAUDE_BASE = ["claude", "-p", "--permission-mode", "dontAsk"]
ALLOWED_TOOLS = ["Read", "Write", "Edit", "Glob", "Grep", "WebSearch", "WebFetch"]


def time_args() -> list[str]:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return ["--append-system-prompt", f"現在日時: {now}"]


def tool_args() -> list[str]:
    return ["--allowedTools", *ALLOWED_TOOLS]


def build_prompt(agents_md: str) -> str:
    """JSE フローを単一の claude に指示するプロンプトを組み立てる。"""
    return f"""\
あなたは kairon-sta の実行エンジンです。以下の JSE フローを 1 回実行してください。

# 前提
- カレントディレクトリは kairon-sta の作業ディレクトリです。
- 現在日時はシステムプロンプトの「現在日時」を使ってください（推測しない）。
- 各エージェントのログは `logs/<エージェント名>.log` にあります。
  存在しない場合は「空」とみなしてください。
- 使えるツールは Read / Write / Edit / Glob / Grep / WebSearch / WebFetch のみです。
  スクリプトやコマンドの実行（Bash など）は禁止です。

# agents.md
1 大見出し（`# 名前`）が 1 エージェントです。各エージェントは
名前・condition（発火条件）・本文を持ちます。

```markdown
{agents_md}
```

# JSE フロー

## 1. judgement（判断）
- 各エージェントの condition を読み取る。
- condition の評価に必要なログ（`logs/<名前>.log`）を Read して文脈を把握する。
  ログが存在しなければ空とみなす。
- 現在日時とログを踏まえ、condition を満たすエージェント（= 起動対象）を確定する。
- 起動対象が 0 件なら、その旨を一言述べて終了する。

## 2. strategy（戦略）
- 起動対象をどの順序・方法で処理するか戦略を立てる。
- 互いに独立した処理は、サブエージェント等で並列化してよい
  （ただし claude プロセスを新たに起動してはならない）。

## 3. execution（実行）
- 戦略どおりに、各起動対象の本文の指示を実行する。
- すべての起動対象は、少なくとも「自分が呼ばれた」事実を
  `logs/<名前>.log` に追記すること（既存内容は壊さない）。
- ログへの追記は **Read →（末尾に1行足した全文を）組み立て → Write** の
  一連を不可分な操作として扱うこと。この一連が完了するまで、同じログ
  ファイルへの別の書き込みを並行・先行させてはならない。
- スクリプト・コマンドは実行しない。Write/Edit によるファイル操作のみで完結させる。

最後に、判断結果（起動対象とその理由）と実行結果を簡潔に報告してください。
"""


def main() -> None:
    agents_md = AGENTS_MD.read_text(encoding="utf-8")
    prompt = build_prompt(agents_md)
    subprocess.run(
        CLAUDE_BASE + tool_args() + time_args(),
        input=prompt,
        text=True,
        encoding="utf-8",
        cwd=HERE,
    )


if __name__ == "__main__":
    main()
