# Foundation

日次セッションとは別枠で、**週1回20分**だけ確保する枠です。2つの役割があります。

## 役割1: 実機で確認する（毎週）

設計の答え合わせをLLMだけで済ませていると、インデックスや分離レベルは身につきません。`EXPLAIN` を一度も見ずに複合インデックスの列順を学ぶのは、かなり効率が悪いです。

週1回、実際に動かして数字を見ます。テンプレート: [templates/hands-on-session.md](templates/hands-on-session.md)

```bash
docker run --rm -d --name eos-pg \
  -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:16
```

記録は `09-foundation/YYYY-MM-DD-<topic>.md` に残します。**予想と実測の差**が学びの本体なので、必ず「事前の予想」を書いてから実行してください。

## 役割2: 繰り返す弱点をやり直す

同じ弱点が優先度Highに達してなお不合格が続く項目を、基礎からやり直します。

### Entry criteria

- 再テストで2回以上不合格
- 出題形式を変えても同じ誤りが出る
- 「用語を知らない」ではなく「概念が繋がっていない」状態

### Exit criteria

- 自分の言葉で30秒説明できる
- その概念を使う出題を2回連続で正答する
- [Term Bank](../03-banks/term-bank.md)でActiveになる

## Current queue

| Item | Origin weakness | Method | Status | Next |
|---|---|---|---|---|
| トランザクション分離レベルと異常現象の対応 | W001系 | 4つの異常を実機で再現するSQLを書く | Queued | 2026-09-13 |
| 複合インデックスの列順と実行計画 | W002 | 列順を変えて `EXPLAIN ANALYZE` を比較 | Queued | 2026-09-20 |

## Method rules

- 読むだけで終わらせない。必ず手を動かす成果物を1つ作る
- 20分で区切る。終わらなければ翌週へ
- 同時に扱うのは1項目だけ
