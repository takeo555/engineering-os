# Drill Misses

Drill で間違えた問題の分野を記録する軽量ログ。

## 目的

- 翌日のドリル生成時、試験官が直近3日分（`eos.config.json` の `drill.miss_reinject_lookback_days`）を読んで、同じ分野の類題を1問だけ混ぜる
- 週次レビューで「どのカテゴリが弱いか」の傾向を見る

## Weakness Log との違い

| 観点 | Weakness Log（`weakness-log.md`） | Drill Misses（このファイル） |
|---|---|---|
| 対象 | Design 15分問題の弱点 | Drill 30秒問題の間違い |
| ID | 振る（W001, W002...） | 振らない |
| 再テスト期限 | あり（High:5日, Med:9日, Low:14日） | なし（翌日類題を混ぜるだけ） |
| 優先度 | High / Med / Low | なし |
| クローズ | 再テスト合格でClosed | なし（追記式で残す） |

## 形式

日付ごとにセクションを作り、間違えた項目を箇条書きで追記する：

```text
## 2026-09-14

- AI × 著作権: 生成物の著作権帰属（正解: 原則としてプロンプト提供者・使用者。契約とサービス規約による）
- 言語(Go) × goroutine: leaked goroutine の検出方法（正解: `context.WithCancel` などでキャンセル可能にする）
- ネットワーク × DNS: DNSキャッシュのTTL挙動（正解: TTLの残り時間まで再解決しない）

## 2026-09-15

- 言語(Next.js) × Server Component: 使えないブラウザAPI（正解: `window`, `document` 等）
```

カテゴリ名は `AI` / `言語(Go|Next.js|Python|Terraform)` / `ネットワーク` のいずれか。`×` の後ろが分野、`:` の後ろが問題テーマ。

## パース仕様

`scripts/parse_record.py` は記録ブロックの `## 0. Drill` セクションから間違い項目を抽出し、このファイルに追記する。既存の日付セクションがあれば末尾に追記、なければ新規セクションを作る。

`scripts/eoslib.py` の `load_recent_drill_misses(days)` が直近N日分を読み、`build_context.py` が CONTEXT.md の「今日の Drill 題材枠」に「直近のmiss類題」として書き出す。

## 保守

- 手で編集しない（自動追記のみ）
- 3ヶ月以上前の項目は月次レビューで削除してよい（履歴が長くなりすぎるため）
- ファイルサイズが100KBを超えたら年別に分割（`drill-misses-2026.md`, `drill-misses-2027.md`）

---

<!-- 以下、日次記録の追記が続く。この行より下を自動追記の領域とする -->
