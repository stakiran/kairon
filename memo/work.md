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

frontmatter に tools と console を追加してる。動いてはいる。

が、console: true にしても print が出てこない。デバッグできねえだろ。トラシューしてるけど的を得ない。

# やっぱりアーキ変えよう
claude -p のネストはダメだ。

claude -p は kairon だけにして、kairon が起動対象特定 → 起動対象を全部自分で起動、にする。処理はなるべく決定的にすればいい。必要なら使い捨てスクリもつくれ。非同期も使え。その辺の判断は丸々任せればいい。権限だけ絞って暴れないようにだけはしておく。

v1 は切っておく。memo/ に置いといた。

# ====

# kairon v2
kairon は概念、参考実装として kairon-sta を提示するモデルにした。

次: これでつくれそうか尋ねるところから

つくらせて実行してみた:

- 1分以内に実行されてるっぽい。いいんじゃないか？🐰

ログの排他制御は直させた

実行を繰り返して、condition が効くことを確かめたい:


