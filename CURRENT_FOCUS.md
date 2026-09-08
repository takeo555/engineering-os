# Current Focus

このファイルは今だけを見るダッシュボードです。Weekly Reviewで更新します。

## Current cycle

- Period: 2026-09-08 – 2026-09-30（今月の Horizon）
- Primary track: Layered Architecture
- Secondary track: Coding / Go / Next.js
- Level: L1（基礎の確認）
- North Star connection: 依存方向を指摘でき、小さな Go または Next が動く。AI は10月の生成AIパスポート。今月は出題しない

## Focus skills

1. **Layering:** レイヤーごとの責務と依存方向を図示し、違反を指摘する
2. **Interface Design:** handler / usecase、またはページ / データ取得の境界を決める

## This week's plan

| Day | Track | Format | Target |
|---|---|---|---|
| Tue | Layered Architecture | Review | 与えられた設計の依存方向違反を指摘する（W005 / W006） |
| Wed | Coding / Go / Next.js | Explain | 小さな機能の置き場所を後輩に3分で説明させる |
| Thu | Layered Architecture | Review | Domain に置くべきルールを切り出せるか（W007） |
| Fri | Coding / Go / Next.js | Design | Go または Next で最小の動く骨格を書く |
| Sat | Layered Architecture | Explain | 依存性逆転が必要な箇所を状況付きで説明する |
| Sun | Coding / Go / Next.js | Review | 与えられたコードの責務混在を指摘して分ける |

用語の穴埋めは出さない。期限の来た弱点は Horizon 外でも出題される。

## Weaknesses in retest queue

- W005 — HandlerとDomainの責務境界を正しく分離できない（retest: 2026-09-12）
- W006 — 具象Repositoryへの依存を依存性逆転として説明できない（retest: 2026-09-12）
- W001 — 論理削除と一意制約の衝突に気づけない（retest: 2026-09-08）※期限到来。出たら片付ける
- W002 — 複合インデックスの列順を決める基準が言えない（retest: 2026-09-10）

## Concepts to activate

- Presentation / Application / Domain / Infrastructure の責務
- 依存性逆転が守られている状態の見分け方
- handler に業務ルールを置かない
- ページとデータ取得の置き場所
- エラーを呼び出し側に返す

## Exit criteria

- Layered Architecture のセッションを2回以上
- Coding のセッションを2回以上（うち1回はコードを書く）
- W005 または W006 を自分の言葉で30秒
- Foundation を1回以上（Go または Next を動かす）
- Weekly Review を完了する
