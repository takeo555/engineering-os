# ROADMAP

Engineering OS の学習フェーズを宣言的に持つ。試験官はドリル問題を生成する前にこのファイルを読み、**今日がどのフェーズか** を判定して AI ドリルの題材を選ぶ。

このファイルは月次レビューで見直す。日次では変更しない。

## Phase 1: 生成AIパスポート期

- **期間**: 2026-09-14 〜 生成AIパスポート受験日（2026-10-18・仮。確定したら末尾のフェーズ定義を直す）
- **主目的**: 生成AIパスポート合格
- **AI drill 題材**:
  - 生成AIの仕組み概要（Transformer, LLM, RAG, ファインチューニング）
  - リスク（幻覚、著作権、秘密漏洩、バイアス）
  - 法制度と倫理（EU AI Act, 日本の指針、ガバナンス）
  - 業務利用の注意点
- **言語 drill 題材**: Go / Next.js / Python / Terraform の各基礎文法（後述の `coding-language.md` 参照）
- **ネットワーク drill 題材**: 『ネットワークはなぜつながるのか』の読了章まで
- **Design 15分**: Layered Architecture / DB / API / Code Review を25%ずつ
- **出口**: 生成AIパスポート合格 + engineering OS 二層構造の定着（連続実施14日以上）

## Phase 2: CCAO-F期

- **期間**: 生成AIパスポート受験翌々日（2026-10-20・仮） 〜 2027-01-末
- **主目的**: Claude Certified Associate – Foundations（CCAO-F）合格（スコア720/1000以上）
- **AI drill 題材**: CCAO-F の7ドメイン
  - Domain 1: Prompting and Task Execution（14%）
  - Domain 2: Output Evaluation and Validation（21%・最重要）
  - Domain 3: Product and Model Selection（12%）
  - Domain 4: Workflow Integration and Solution Design（16%）
  - Domain 5: Configuration and Knowledge Management（12%）
  - Domain 6: Governance, Risk, and Responsible Use（15%）
  - Domain 7: Troubleshooting and Optimization（10%）
- **言語 drill 題材**: 継続（Phase 1と同じ配分）
- **ネットワーク drill 題材**: 本読了後、公式ドキュメント（MDN HTTP、AWS/GCP ネットワーク docs等）を追加検討
- **Design 15分**: 同上
- **出口**: CCAO-F 合格（1回で）

## Phase 3: CCAR-F期

- **期間**: 2027-02-01 〜 2027-03-末
- **主目的**: Claude Certified Architect – Foundations（CCAR-F）受験準備
- **AI drill 題材**: CCAR-F の出題範囲（試験ガイドを入手後に確定）
- **言語 drill 題材**: Terraform 比重を上げる可能性あり（IaCがアーキテクトに直結）
- **ネットワーク drill 題材**: LB、可用性、分散システムの基礎に重心
- **Design 15分**: 同上
- **出口**: CCAR-F 受験計画確定、模試70%以上

## 見直しタイミング

- **月次レビュー**: 各フェーズの進捗を評価。次月の AI drill 題材と Design 重みを微調整
- **フェーズ切替時**: このファイルを更新して次フェーズ開始日を確定
- **月次レビュー以外での変更禁止**: 日次でこのファイルを触らない

## フェーズ定義（機械可読・`scripts/eoslib.py` の `current_phase()` が読む）

日付が確定したらこの行だけを直す。上の散文と食い違わせないこと。
`end` はそのフェーズの最終日（その日を含む）。

<!-- eos:phase id=1 name=生成AIパスポート期 start=2026-09-14 end=2026-10-19 -->
<!-- eos:phase id=2 name=CCAO-F期 start=2026-10-20 end=2027-01-31 -->
<!-- eos:phase id=3 name=CCAR-F期 start=2027-02-01 end=2027-03-31 -->

- Phase 1 の `end` は「受験日の翌日」。受験翌々日から Phase 2 が始まるため
- 受験日が動いたら Phase 1 の `end` と Phase 2 の `start` を同時に直す
