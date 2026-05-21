質問1: run_kairon.bat で良い
質問2: ログはエージェント側に任せる。ディスパッチャは何も負うべきではない。
質問3: ディスパッチャは子プロセスの終了を待たなくていい。Fire-and-forget（投げっぱなし） で良い

--allowedTools は固定したい。frontmatter での個別指定は嫌だ。また --dangerously-skip-permissions は論外。bash:* や python:* なども論外。この前提で、何を指定すればいいだろう。読み書きとウェブサーチあたりは事前許可でいい。他に何を許可しておけばいいかな。

--permission-mode dontAsk で allowed tool のみに絞れる？abort になるのか？