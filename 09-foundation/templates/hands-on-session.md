---
date: YYYY-MM-DD
topic: 
origin_weakness: 
minutes: 20
---

# YYYY-MM-DD — 実機で確認: <topic>

設計の答え合わせをLLMだけで済ませていると、インデックスや分離レベルは身につきません。週1回20分、実際に動かして数字を見ます。

## 1. 確認したいこと

<!-- 「複合インデックスの列順で実行計画がどう変わるか」のように、1つだけ -->

## 2. 環境

```bash
# 例: PostgreSQL 16 を立てる
docker run --rm -d --name eos-pg \
  -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:16

docker exec -it eos-pg psql -U postgres
```

## 3. 実行したSQL / コマンド

```sql
-- スキーマ
-- データ投入（generate_series で十分な件数を作る）
-- EXPLAIN (ANALYZE, BUFFERS) で計測
```

## 4. 観測した結果

| 条件 | 実行計画 | 実測 |
|---|---|---|
| | | |

## 5. 予想との差

<!-- 事前に予想していたことと、実際の差。ここが学びの本体 -->

## 6. 判断ルールとして残すこと

<!-- 1〜2行。Bankへ昇格させるならその旨も -->

## 7. 片付け

```bash
docker stop eos-pg
```
