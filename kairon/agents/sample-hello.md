---
name: sample-hello
condition: 現在の時が 6～19 のとき、かつログが 3 行以内のとき
---

現在時刻と挨拶文を `logs/sample-hello.log` に 1 行追記してください。

- 形式: `YYYY-MM-DD HH:MM:SS | hello from kairon`
- 追記方法: `Bash(echo:*)` で `echo "..." >> logs/sample-hello.log` を実行
- 既存内容は絶対に壊さないこと（必ず追記）

エラーが出た場合も同様に `logs/sample-hello.log` に `YYYY-MM-DD HH:MM:SS | ERROR: <内容>` の 1 行を追記してください。
