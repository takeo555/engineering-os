# Current Focus

このファイルは今だけを見るダッシュボードです。Weekly Reviewで更新します。

## Current cycle

- Period: 2026-09-14 – 2026-09-30（Phase 1初週〜9月末）
- Phase: Phase 1（生成AIパスポート期）
- North Star connection: ドリルで知識の床を作りながら、Design 15分で設計判断の練習を続ける。生成AIパスポートは10月中旬受験

## Study structure

日次は Drill 4分 + Design 15分 の二層構造。

### Drill（毎日8問・30秒・単答）
- AI 3問: 生成AIパスポート範囲（GUGAシラバス）
- コーディング言語 3問: Go 35% / Next.js 35% / Python 20% / Terraform 10%
- ネットワーク 2問: 『ネットワークはなぜつながるのか』の読了章まで

### Design（毎日1問・15分・5軸採点）
- Layered Architecture 25% / DB / Table Design 25% / Web / API / HTTP 25% / Code Review 25%
- Level: L1（基礎の確認）

## Focus skills（Design側）

1. **Layering**: レイヤーごとの責務と依存方向を図示し、違反を指摘する
2. **Interface Design**: handler / usecase、page / data fetch の境界を決める

## This week's plan（Design側の狙い）

| Day | Design Track | Format | Target |
|---|---|---|---|
| Mon | Layered Architecture | Review | 与えられた設計の依存方向違反を指摘（W005 / W006） |
| Tue | DB / Table Design | Explain | 論理削除と一意制約の衝突を後輩に3分で説明（W001） |
| Wed | Web / API / HTTP | Design | 冪等キーの保存期間と衝突時の挙動を定義 |
| Thu | Code Review | Review | 与えられたGoコードの責務混在を指摘して分ける |
| Fri | Layered Architecture | Design | 小さなユースケースをレイヤー分割して図示 |
| Sat | DB / Table Design | Design | 複合インデックスの列順を根拠付きで設計 |
| Sun | Code Review | Explain | コードレビューで見るべき観点を5つ挙げて説明 |

## Weaknesses in retest queue（Designのみ）

- W001 — 論理削除と一意制約の衝突に気づけない（retest: 2026-09-12・期限到来）
- W002 — 複合インデックスの列順を決める基準が言えない（retest: 2026-09-10）
- W005 — HandlerとDomainの責務境界を正しく分離できない（retest: 2026-09-12）
- W006 — 具象Repositoryへの依存を依存性逆転として説明できない（retest: 2026-09-12）

## Drill miss recent（直近3日、翌日類題投入用）

（`05-failures/drill-misses.md` の直近3日分をここに転記する運用にする。build_context.py が自動で埋める）

## Concepts to activate

- Presentation / Application / Domain / Infrastructure の責務
- 依存性逆転が守られている状態の見分け方
- コードレビューで最初に見るべき3点（責務・命名・境界）
- 冪等性を実装する定石
- 論理削除と一意制約の共存パターン

## Exit criteria（今週）

- Drill を7日連続で記録
- Design を4回以上完了（うち1回はコードを書く）
- W005 または W006 を自分の言葉で30秒
- Weekly Review を完了する
