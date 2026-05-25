# sample-hello
condition: 現在の時が 6～19 のとき、かつログが 3 行以内のとき

現在時刻と挨拶文を `logs/sample-hello.log` に 1 行追記してください。

- 形式: `YYYY-MM-DD HH:MM:SS | hello from kairon`
- 現在時刻は、システムプロンプトに記載された「現在日時」を使うこと
- 追記方法（Bash は使わない）:
  1. `logs/sample-hello.log` を Read（存在しなければ「空」とみなす）
  2. 既存内容の末尾に上記 1 行を追加した全文を組み立てる
  3. Write で `logs/sample-hello.log` に上書き保存
- 既存内容は絶対に壊さないこと

エラーが出た場合も同様に `logs/sample-hello.log` に `YYYY-MM-DD HH:MM:SS | ERROR: <内容>` の 1 行を追記してください。

# sample-news
condition: ログが3行未満のとき

まずは以下を行え:

- 現在日時を把握する（すでに渡されているはず）
- `[a-z]`からランダムに1文字選ぶ
- その1文字から連想する名詞を 10 個挙げる

その上で、10 個の名詞と現在日時を踏まえて話題を一つ決定し、それに関する最新のニュースを調べてから、そのうち 1 件を一言で要約せよ。最後にログにタイムスタンプと要約を append せよ
