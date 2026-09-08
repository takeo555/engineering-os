# Foundation

日次セッションとは別枠で、既定は**週1回20分**だけ確保する枠です。2つの役割があります。

**今月（Current horizon）:** コーディングを厚くするため、当面は **週2回** まで増やしてよい。同時に扱う項目は1つのまま。Go または Next を実際に動かす。

## 役割1: 実機で確認する（毎週）

設計の答え合わせをLLMだけで済ませていると、層の境界も実行結果も身につきません。

既定は週1回、今月は週2回まで、実際に動かして数字または起動結果を見ます。テンプレート: [templates/hands-on-session.md](templates/hands-on-session.md)

```bash
# 例: 小さな Go モジュール
go run .

# 例: Postgres が必要なとき
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
| GoでHTTPハンドラ1本を動かし、handler/usecaseに分ける | 今月Horizon | `go run` で起動し、置き場所を記録する | Queued | 2026-09-10 |
| Nextでページ1枚を出し、データ取得の置き場所を説明 | 今月Horizon | ページを表示し、取得処理の場所を記録する | Queued | 2026-09-17 |

DB の分離レベル / インデックス（W001 / W002）は弱点ログに残す。今月の Foundation 本体にはしない。

## Method rules

- 読むだけで終わらせない。必ず手を動かす成果物を1つ作る
- 20分で区切る。終わらなければ翌週へ
- 同時に扱うのは1項目だけ
