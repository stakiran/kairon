# .
質問1: run_kairon.bat で良い
質問2: ログはエージェント側に任せる。ディスパッチャは何も負うべきではない。
質問3: ディスパッチャは子プロセスの終了を待たなくていい。Fire-and-forget（投げっぱなし） で良い

--allowedTools は固定したい。frontmatter での個別指定は嫌だ。また --dangerously-skip-permissions は論外。bash:* や python:* なども論外。この前提で、何を指定すればいいだろう。読み書きとウェブサーチあたりは事前許可でいい。他に何を許可しておけばいいかな。

--permission-mode dontAsk で allowed tool のみに絞れる？abort になるのか？

# run_kairon.bat お試し中
sample-hello でも claude.exe が終了するまでに 20 秒近く、メモリも 0.5 GB くらいは使ってる

重たいな🐰

> condition: 現在の時が 6～19 のとき、かつログが 3 行以内のとき

これはちゃんとマッチしてくれて、5 行以上にはならない感じ。

process explorer で確認しながら見ていた

# sample-sleepprint.md を試す
スクリプト実行できるようにしたい。

frontmatter に tools と console を追加してる。が、console: true にしても print が出てこない。デバッグできねえだろ。トラシューしてるけど的を得ない。

