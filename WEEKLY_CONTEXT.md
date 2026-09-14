# WEEKLY_CONTEXT — 2026-W38

> **自動生成。手で編集しないこと。** レビューの講評は試験官が書きます。
> ここにあるのは数字だけです。ここに無い事実を推測で補わないでください。

- 期間: 2026-09-14 – 2026-09-20
- 生成: 2026-09-14

## 集計

| Metric | Value |
|---|---|
| 実施セッション | 0回（予定 7） |
| 平均スコア | — |
| 15分内完了率 | — |
| Open弱点 | 13件（High 6件） |
| 通算セッション | 5回 |

## この期間のセッション

| Date | Track | Format | Level | Score | Time |
|---|---|---|---|---|---|
| — | — | — | — | — | 記録なし |

## Design Track別

| Track | Avg（期間内） | 回数 |
|---|---|---|
| Layered Architecture | — | 0 |
| DB / Table Design | — | 0 |
| Web / API / HTTP | — | 0 |
| Code Review | — | 0 |

## Drill 正答率（期間内・5軸採点の対象外）

| Category | Rate |
|---|---|
| AI | — |
| 言語 | — |
| ネットワーク | — |

記録ブロックにはこの値を書く: `記録なし`

正答率の低いカテゴリを Design Track に格上げしないこと。目的が違う（Drill=知識、Design=判断）。

## Drill の間違い（期間内）

- なし

## Open弱点（全件）

| ID | Priority | Weakness | Track | Detected | Retest on | 直近結果 |
|---|---|---|---|---|---|---|
| W001 | High | 論理削除と一意制約の衝突に気づけない | DB / Table Design | 2026-09-03 | 2026-09-12 | 不合格 2026-09-09 論理削除とUNIQUE制約の衝突を指摘できず |
| W002 | High | 複合インデックスの列順を決める基準を説明できない | DB / Table Design | 2026-09-03 | 2026-09-10 | — |
| W005 | High | HandlerとDomainの責務境界を正しく分離できない | Layered Architecture | 2026-09-07 | 2026-09-12 | — |
| W006 | High | 具象Repositoryへの依存を依存性逆転として説明できない | Layered Architecture | 2026-09-07 | 2026-09-12 | — |
| W008 | High | DomainとUsecaseの責務境界を具体的に説明できない | Layered Architecture | 2026-09-08 | 2026-09-13 | — |
| W010 | High | 論理削除時に一意制約がどう衝突するかを説明できない | DB / Table Design | 2026-09-09 | 2026-09-14 | — |
| W003 | Med | 時間帯の重なり判定を構造で表現できない | DB / Table Design | 2026-09-03 | 2026-09-12 | — |
| W007 | Med | Domainに置くべき業務ルールを具体的に切り出せない | Layered Architecture | 2026-09-07 | 2026-09-16 | — |
| W009 | Med | interfaceによる依存性逆転がテスト容易性につながる理由を具体的に説明できない | Layered Architecture | 2026-09-08 | 2026-09-17 | — |
| W011 | Med | 保持要件とデータ量を踏まえて履歴データの管理方法を説明できない | DB / Table Design | 2026-09-09 | 2026-09-18 | — |
| W012 | Med | ページングにおけるOFFSET方式の課題とカーソル方式との使い分けを説明できない | Coding / Go / Next.js | 2026-09-11 | 2026-09-20 | — |
| W013 | Med | レイヤー分離の目的を「関数を軽くする」ではなく変更理由と責務の分離として説明できない | Layered Architecture | 2026-09-11 | 2026-09-20 | — |
| W004 | Low | 状態をBOOLEANで持ち、拡張性を検討しない | DB / Table Design | 2026-09-03 | 2026-09-17 | — |

## Closed済みの弱点（直近10件）

- なし

## WIP上限の警告

- Open High弱点が6件（上限5）。Weekly Reviewで統合か降格を行うこと

## 直近の出題タイトル

- 2026-09-11 [Coding / Go / Next.js/Review] 2026-09-11 — 備品一覧APIのページングと責務分離
- 2026-09-09 [DB / Table Design/Review] 2026-09-09 — 論理削除と一意制約が衝突する貸出管理設計
- 2026-09-08 [Layered Architecture/Design] 2026-09-08 — 価格計算APIの責務分離と依存方向
- 2026-09-07 [Layered Architecture/Design] 2026-09-07 — 価格計算APIの責務分離と依存方向
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
| 2026-09-07 | HTTP固有の処理はHandlerで値に変換してUsecaseへ渡す | pattern | Pending |
| 2026-09-07 | Usecaseは具象Repositoryではなくinterfaceに依存させる | pattern | Pending |
| 2026-09-08 | interfaceを依存する側に定義し、具体的なRepository実装を差し替え可能にする | pattern | Pending |
| 2026-09-09 | 論理削除を採用したらUNIQUE制約の対象範囲を確認する | pattern | Pending |

## 難易度の判定（決定済み。試験官は変更してはならない）

- **base_level: L1**
- 理由: 今週のセッションが0回（3回未満）のため難易度は変えない。まず回数を戻すこと

---

<!-- eos:review period=week label=2026-W38 base_level=L1 -->
