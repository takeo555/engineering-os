# STATUS — 2026-09-19

> 自動生成。手で編集しても次の実行で上書きされます。

| Metric | Value |
|---|---|
| 連続実施 | 0日 |
| 直近14日のセッション | 4回 |
| 直近5回の平均スコア（Design） | 49.6 |
| 15分内完了率（直近10回） | 50% |
| Base level | L1 |
| Phase | Phase 1（生成AIパスポート期） |
| Open弱点 | 13件（High 6件） |
| 再テスト期限切れ | 11件 |

## Design Track別平均（直近20回）

| Track | Avg |
|---|---|
| Layered Architecture | 42.5 |
| DB / Table Design | 44.0 |
| Web / API / HTTP | — |
| Code Review | — |
| Coding / Go / Next.js（旧Track・参考） | 75.0 |

## Drill 正答率（直近14回）

| Category | Rate |
|---|---|
| AI | — |
| 言語 | — |
| ネットワーク | — |

## 今すぐ再テストすべき弱点

- `W001` [High] 論理削除と一意制約の衝突に気づけない（期限 2026-09-12）
- `W002` [High] 複合インデックスの列順を決める基準を説明できない（期限 2026-09-10）
- `W005` [High] HandlerとDomainの責務境界を正しく分離できない（期限 2026-09-12）
- `W006` [High] 具象Repositoryへの依存を依存性逆転として説明できない（期限 2026-09-12）
- `W008` [High] DomainとUsecaseの責務境界を具体的に説明できない（期限 2026-09-13）

## WIP上限の警告

- Open High弱点が6件（上限5）。Weekly Reviewで統合か降格を行うこと

---

- 試験官が毎朝読む入り口: [`CONTEXT.md`](CONTEXT.md)
- 今週の重点: [`CURRENT_FOCUS.md`](CURRENT_FOCUS.md)
- 弱点一覧: [`05-failures/weakness-log.md`](05-failures/weakness-log.md)
- ドリルの間違い: [`05-failures/drill-misses.md`](05-failures/drill-misses.md)
- 学習フェーズ: [`ROADMAP.md`](ROADMAP.md)
