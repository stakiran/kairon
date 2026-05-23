# kairon design v1

タスクスケジューラ → `kairon.py` → dispatcher claude → 各 agent claude（fire-and-forget）の構成。
このメモは現状の設計と既知の制約を整理したもの。次のアーキテクチャ検討の土台として残す。

## コンセプト
- `cron` = 時刻一致でジョブを実行する従来型スケジューラ
- `kairon` = LLM が「現在の状況」を読んで実行可否を判断する文脈ベーススケジューラ
  - 発火条件は自然言語で書ける（例: 「ログが 3 行以内のとき」「平日の朝に 1 回くらい」）
- エージェントは markdown ファイル 1 個で定義する

### 名前の由来

`cron` はギリシャ語の `chronos`（時計的・定量的な時間）に由来する。Unix の cron も分・時・日・曜日が現在時刻に一致するかでジョブを動かす、まさに chronos 的な仕組み。
これに対して `kairon` は `kairos`（機を見る、文脈上ふさわしい時）に由来する造語。
末尾を `-on` にしてあるのは cron と韻を踏みつつソフトウェア名らしくするため。

対比：

| 概念   | 判断対象                                |
| ------ | --------------------------------------- |
| cron   | 時刻・曜日・日付が一致するか            |
| kairon | 文脈上、今がその機会か                  |

- cron asks: "Is it 9:00?"
- kairon asks: "Is now the right moment?"

`kairon` はプロダクト名ではなく **概念名／パラダイム名** として位置づける（cron が特定実装名から「定時実行の型」を指す一般語になったのと同じ扱い）。
そのため Kairon という固有名詞が AI / 占星術 / 暗号資産などの分野で既に使われていても、概念名としての衝突は気にしない。

## 全体フロー

```
Windows タスクスケジューラ（3時間おき想定）
  ↓
run_kairon.bat
  ↓
python kairon.py
  ├─ dispatch()
  │   claude -p に dispatcher.md を流し、動かすべき agent 名を取得（同期）
  │     - tools: Read, Glob のみ
  │     - stdout に name を改行区切りで返す
  │
  └─ fire(name)（dispatch の結果を 1 件ずつ）
      claude -p に agents/<name>.md を流して起動（fire-and-forget）
        - tools: AGENT_TOOLS_DEFAULT + frontmatter の追加分
        - DETACHED_PROCESS で裏で動く（または console:true なら CREATE_NEW_CONSOLE）
        - kairon.py 本体はすぐに終了
```

各 claude 起動時に `--append-system-prompt "現在日時: YYYY-MM-DD HH:MM:SS"` で現在時刻を注入する。
これで claude 側は `date` を叩く Bash 権限なしに時刻を参照できる。

## ディレクトリ構成

```
kairon/
├── CLAUDE.md
├── .claude/rules/
│   ├── kairon_concept.md
│   └── kairon_name.md
├── kairon/
│   ├── kairon.py           # エントリポイント
│   ├── dispatcher.md       # ディスパッチャプロンプト
│   ├── run_kairon.bat      # タスクスケジューラから叩く .bat
│   ├── agents/
│   │   ├── sample-hello.md
│   │   ├── sample-sleepprint.md
│   │   └── sleepprint.py   # agent から呼び出す補助スクリプト
│   └── logs/
│       ├── sample-hello.log
│       └── sample-sleepprint.log
└── memo/
    ├── work.md
    └── design-v1.md        # このファイル
```

## kairon.py の役割

- `CLAUDE_BASE = ["claude", "-p", "--permission-mode", "dontAsk"]`
- `DISPATCHER_TOOLS = ["--allowedTools", "Read", "Glob"]`
- `AGENT_TOOLS_DEFAULT = ["Read", "Write", "Edit", "Glob", "Grep", "WebSearch", "WebFetch"]`
- `parse_frontmatter(md_text)` — `---` で囲まれたブロックから `key: value` を素朴に拾う簡易パーサ。複数行値や YAML 構造は非対応
- `agent_tool_args(fm)` — frontmatter の `tools` を `AGENT_TOOLS_DEFAULT` に追加して `--allowedTools` を組み立てる
- `dispatch()` — dispatcher を同期実行し stdout を行で割って返す
- `fire(name)` — agent を `subprocess.Popen` で fire-and-forget 起動
  - 通常: `DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP`、stdin=PIPE で md_text 流し込み、stdout/stderr=DEVNULL
  - `console: true`: `CREATE_NEW_CONSOLE` + `--verbose` 追加（※後述の既知問題あり）

## dispatcher.md の役割

1. Glob で `agents/*.md` を列挙
2. 各ファイルを Read して frontmatter の `name` と `condition` を取得
3. `condition` を自然言語で解釈し、判定に必要な情報（現在時刻、`logs/<name>.log` など）を集める
4. 真と判定した agent の `name` を改行区切りで stdout に出す
5. 説明文・Markdown 装飾・空行は禁止（純粋な name 一覧のみ）

判定ガイドライン:
- 過度な深読みはしない
- 迷ったら動かさない（過剰実行よりマシ）
- ログファイルが無ければ「ログ 0 行」として扱う

## agent.md の仕様

frontmatter（自前パーサで読める範囲）:
- `name` — agent 識別子。`logs/<name>.log` と対応
- `condition` — 発火条件の自然言語記述
- `tools` — `AGENT_TOOLS_DEFAULT` に追加するツールをカンマ区切りで列挙（例: `Bash`）
- `console` — `true` で `CREATE_NEW_CONSOLE` + `--verbose`（claude の挙動を窓で覗き見る用）

本文 = 発火時に claude が実行する自然言語の指示。

## ログ運用

- agent ごとに `logs/<name>.log`
- agent 自身が Read → 末尾追加 → Write で追記する（Bash 不要にするため）
- 形式は agent ごとに自由。現状の慣習は `YYYY-MM-DD HH:MM:SS | <要約 1 行>`
- dispatcher は logs を Read して condition 判定に使う

## 現存サンプル

### sample-hello
- `condition: 現在の時が 6～19 のとき、かつログが 3 行以内のとき`
- 挨拶文をログに 1 行追記する

### sample-sleepprint
- `condition: ログが 1 行以内のとき`
- `tools: Bash`、`console: true`
- `python agents/sleepprint.py`（print → 5 秒 sleep → print）を実行し、stdout をログに追記する

## 既知の制約・課題

1. **`console: true` で窓は出るが中身が空**
   - 原因: `subprocess.Popen(stdin=PIPE, ...)` で `STARTF_USESTDHANDLES` が立つと、未指定の stdout/stderr が **親プロセスのコンソール** から継承される。`CREATE_NEW_CONSOLE` を指定しても新規コンソールの標準ハンドルは使われない
   - 回避案: プロンプトをコマンドライン引数で渡す → Windows の引数長・改行・エスケープで詰むため不採用
   - 残る案: 一時ファイル経由で `cmd /c "claude ... < tmpfile"` のようにシェルでリダイレクトし、Popen 側は stdin/stdout/stderr を一切指定しない

2. **Bash 経由で python を叩いても DOS 窓は出ない**
   - 原因: claude の Bash ツールはサブプロセスの stdout を **キャプチャしてログに渡す** ため、コンソール表示されない
   - 「python の print を窓でリアルタイムに見たい」用途には別アプローチ（`start /wait cmd /c ...` で別窓を開く等）が要る

3. **frontmatter パーサが脆い**
   - 単純な `key: value` 1 行のみ対応。複数行値・リスト・ネストは不可
   - 値にコロンを含めると壊れる（`split(":", 1)` で逃げているが完全ではない）

4. **fire-and-forget なのでエラー検知が agent 任せ**
   - kairon.py 側は agent 起動後に即終了するため、agent が落ちても気付けない
   - agent 自身が catch してログに書き込む規約に依存

5. **LLM 判定のブレ**
   - dispatcher の condition 解釈は日によって揺れる可能性がある
   - 「ログ 3 行以内」のような閾値もブレうる（決定論ではない）

6. **コスト・呼び出し回数の考慮なし**
   - 3 時間おき起動 × dispatcher 1 回 + agent 数の claude 呼び出し
   - 個人利用なら問題ないが、agent が増えると地味に効いてくる

## 設計判断の記録

- **Go/Rust の常駐デーモンを書かない**: Windows サービス化の罠（権限・デバッグ難・停止挙動）を避ける。OS のタスクスケジューラに乗せて claude を叩くだけで足りる
- **cron 式でなく自然言語の condition**: kairon のコンセプトそのもの。文法を覚える必要がない
- **frontmatter の YAML パースを自前**: 依存ライブラリゼロを優先。複雑な構造を要求しない設計
- **agent ごとに別ログファイル**: claude が「このエージェントの過去履歴」を取得しやすい
- **dispatcher と agent を別 claude プロセスに**: コンテキスト混在を避ける。dispatcher の権限は Read/Glob のみに絞れる
- **発火後は fire-and-forget**: 長時間 agent をブロックせず、kairon.py 自体は即終了する。タスクスケジューラの「次の起動」が前回完了を待たない構造にしたい
