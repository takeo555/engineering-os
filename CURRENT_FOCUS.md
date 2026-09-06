# Current Focus

このファイルは今だけを見るダッシュボードです。Weekly Reviewで更新します。

## Current cycle

- Period: 2026-09-07 – 2026-09-13
- Primary track: DB / Table Design
- Secondary track: Web / API / HTTP
- Cross-cutting track: Layered Architecture
- Level: L2（若手・1〜3年相当）
- North Star connection: 要件から30分でテーブル設計を書き、正規化と整合性の根拠を説明できる状態にする

## Focus skills

1. **Data Modeling:** 要件文から実体と関係を抽出し、第3正規形まで根拠付きで説明する
2. **Consistency Design:** 一意制約・外部キー・トランザクション境界で不正状態を作れなくする

## This week's plan

| Day | Track | Format | Target |
|---|---|---|---|
| Mon | DB / Table Design | Design | 予約系の重複防止をDB制約で表現する |
| Tue | Web / API / HTTP | Design | 冪等キーの設計とリトライ時の挙動を定義する |
| Wed | Architecture | Review | 与えられたコードの依存方向違反を指摘する |
| Thu | DB / Table Design | Debug | 遅いクエリの原因をインデックス観点で切り分ける |
| Fri | Network / Infra | Explain | DNSからTLSまでの接続過程を順に説明する |

## Weaknesses in retest queue

- W001 — トランザクション分離レベルの選択根拠を説明できない（retest: 2026-09-09）
- W002 — 複合インデックスの列順を決める基準が言えない（retest: 2026-09-10）

## Concepts to activate

- 第3正規形とその意図的な崩し方
- 一意制約 vs アプリケーション側チェック
- 冪等性キーの保存期間
- READ COMMITTED と REPEATABLE READ の違い
- 依存性逆転の原則が守られている状態の見分け方

## Exit criteria

- 5 sessions completed
- 平均スコア 70点以上
- W001とW002を再テストし、結果をWeakness Logへ記録
- Weekly Reviewを完了し、翌週のFocusを1〜2個に絞る
