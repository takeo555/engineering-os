# STATUS — 2026-09-12

> 自動生成。手で編集しても次の実行で上書きされます。

| Metric | Value |
|---|---|
| 連続実施 | 1日 |
| 直近14日のセッション | 5回 |
| 直近5回の平均スコア | 49.6 |
| 30分内完了率（直近10回） | 75% |
| Base level | L1 |
| Open弱点 | 13件（High 6件） |
| 再テスト期限切れ | 5件 |

## Track別平均（直近20回）

| Track | Avg |
|---|---|
| DB / Table Design | 44.0 |
| Layered Architecture | 42.5 |
| Web / API / HTTP | — |
| Network / Infra | — |
| Coding / Go / Next.js | 75.0 |
| AI / LLM | — |

## 今すぐ再テストすべき弱点

- `W001` [High] 論理削除と一意制約の衝突に気づけない（期限 2026-09-12）
- `W002` [High] 複合インデックスの列順を決める基準を説明できない（期限 2026-09-10）
- `W005` [High] HandlerとDomainの責務境界を正しく分離できない（期限 2026-09-12）
- `W006` [High] 具象Repositoryへの依存を依存性逆転として説明できない（期限 2026-09-12）
- `W003` [Med] 時間帯の重なり判定を構造で表現できない（期限 2026-09-12）

## WIP上限の警告

- Open High弱点が6件（上限5）。Weekly Reviewで統合か降格を行うこと

---

- ChatGPTが毎朝読む入り口: [`CONTEXT.md`](CONTEXT.md)
- 今週の重点: [`CURRENT_FOCUS.md`](CURRENT_FOCUS.md)
- 弱点一覧: [`05-failures/weakness-log.md`](05-failures/weakness-log.md)
