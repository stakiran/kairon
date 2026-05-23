---
name: sample-sleepprint
condition: ログが 1 行以内のとき
tools: Bash
console: true
---

`sleepprint.py` を実行し、その標準出力をログに追記してください。

- 実行コマンド: `python agents/sleepprint.py`（カレントディレクトリは agent の cwd = kairon ディレクトリ）
- スクリプトは「開始 print → 5 秒 sleep → 終了 print」の 2 行を出力する
- 完了したら `logs/sample-sleepprint.log` に以下のフォーマットで 1 行追記する:
  - `YYYY-MM-DD HH:MM:SS | <スクリプトの stdout を 1 行にまとめたもの>`
  - 現在時刻はシステムプロンプトに記載された「現在日時」を使うこと

追記方法（既存内容を壊さないこと）:
1. `logs/sample-sleepprint.log` を Read（存在しなければ「空」とみなす）
2. 既存内容の末尾に上記 1 行を追加した全文を組み立てる
3. Write で `logs/sample-sleepprint.log` に上書き保存

エラー時も `logs/sample-sleepprint.log` に `YYYY-MM-DD HH:MM:SS | ERROR: <内容>` を 1 行追記してください。
