# Current Focus

このファイルは今だけを見るダッシュボードです。Weekly Reviewで更新します。

## Current cycle

- Period: 2026-09-07 – 2026-09-13
- Primary track: DB / Table Design
- Secondary track: Web / API / HTTP
- Cross-cutting track: Layered Architecture
- Level: L1（基礎の確認）
- North Star connection: 基礎を材料として厚くし、説明と指摘で使えるようにする。他人の設計をレビューできるのはその先

## Focus skills

1. **Data Modeling:** 要件文から実体と関係を抽出し、第3正規形まで根拠付きで説明する
2. **Consistency Design:** 一意制約・外部キー・トランザクション境界で不正状態を作れなくする

## This week's plan

| Day | Track | Format | Target |
|---|---|---|---|
| Mon | DB / Table Design | Review | 与えられたスキーマの問題を3つ指摘して直す |
| Tue | DB / Table Design | Explain | 分離レベルを後輩に3分で説明させる（W001） |
| Wed | Architecture | Review | 与えられた設計の依存方向違反を指摘する |
| Thu | DB / Table Design | Explain | 複合インデックスの列順の基準を説明させる（W002） |
| Fri | Network / Infra | Explain | DNSからTLSまでの接続過程を順に説明する |

用語の穴埋めは出さない。状況付きの説明と、渡された設計の指摘にする。

## Weaknesses in retest queue

- W001 — トランザクション分離レベルの選択根拠を説明できない（retest: 2026-09-09）
- W002 — 複合インデックスの列順を決める基準が言えない（retest: 2026-09-10）

## Concepts to activate

- 第3正規形とその意図的な崩し方
- 一意制約 vs アプリケーション側チェック
- READ COMMITTED と REPEATABLE READ の違い
- 複合インデックスの列順
- 依存性逆転の原則が守られている状態の見分け方

## Exit criteria

- 予定したセッションをこなす（平均70点は必須にしない。L1で材料を埋めている週のため）
- W001 と W002 を自分の言葉で30秒言える
- Review 形式で「指摘が3つ、直しが具体」まで書けた回が2回
- Foundation をこの週に2回以上（分離レベルまたはインデックス）
- Weekly Review を完了し、翌週の Focus を1〜2個に絞る
