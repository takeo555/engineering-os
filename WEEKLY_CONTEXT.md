# WEEKLY_CONTEXT — 2026-W37

> **自動生成。手で編集しないこと。** レビューの講評はChatGPTが書きます。
> ここにあるのは数字だけです。ここに無い事実を推測で補わないでください。

- 期間: 2026-09-07 – 2026-09-13
- 生成: 2026-09-07

## 集計

| Metric | Value |
|---|---|
| 実施セッション | 0回（予定 7） |
| 平均スコア | — |
| 30分内完了率 | — |
| Open弱点 | 4件（High 2件） |
| 通算セッション | 1回 |

## この期間のセッション

| Date | Track | Format | Level | Score | Time |
|---|---|---|---|---|---|
| — | — | — | — | — | 記録なし |

## Track別

| Track | Avg（期間内） | 回数 |
|---|---|---|
| DB / Table Design | — | 0 |
| Layered Architecture | — | 0 |
| Web / API / HTTP | — | 0 |
| Network / Infra | — | 0 |

## Open弱点（全件）

| ID | Priority | Weakness | Track | Detected | Retest on | 直近結果 |
|---|---|---|---|---|---|---|
| W001 | High | 論理削除と一意制約の衝突に気づけない | DB / Table Design | 2026-09-03 | 2026-09-08 | — |
| W002 | High | 複合インデックスの列順を決める基準を説明できない | DB / Table Design | 2026-09-03 | 2026-09-10 | — |
| W003 | Med | 時間帯の重なり判定を構造で表現できない | DB / Table Design | 2026-09-03 | 2026-09-12 | — |
| W004 | Low | 状態をBOOLEANで持ち、拡張性を検討しない | DB / Table Design | 2026-09-03 | 2026-09-17 | — |

## Closed済みの弱点（直近10件）

- なし

## WIP上限の警告

- なし

## 直近の出題タイトル

- 2026-09-03 [DB / Table Design/Design] 2026-09-03 — 会議室予約のダブルブッキングを構造で防ぐ

## Bank昇格キュー

# Bank Promotion Queue

日次セッションから出た昇格候補です。Weekly Reviewで採否が判定され、レビューファイルの「Bank昇格の判定」表に結果が出ます。

**adopt になったものだけを `03-banks/` の該当ファイルへ書き写し、この表の行を削除してください。** ここに溜めたままではBankになりません。自動でBankへ書き込まないのは、Bankの質を人が守るためです。

| Date | Candidate | Target bank | Status |
|---|---|---|---|
| 2026-09-03 | 複合一意制約による枠の排他（P001） | pattern | Adopted |
| 2026-09-03 | 論理削除とUNIQUEの衝突（E001） | pitfall | Adopted |
| 2026-09-03 | 物理削除 vs 論理削除（T002） | tradeoff | Adopted |

## 難易度の判定（決定済み。ChatGPTは変更してはならない）

- **base_level: L2**
- 理由: 今週のセッションが0回（3回未満）のため難易度は変えない。まず回数を戻すこと

---

<!-- eos:review period=week label=2026-W37 base_level=L2 -->
