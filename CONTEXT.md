# CONTEXT — 2026-09-08（Tue）

> **自動生成。手で編集しないこと。** 毎朝06:00 JSTと、
> 記録が保存されるたびに再生成されます。
> ChatGPTはこのファイルだけを読めば出題できます。他のファイルを読みに行く必要はありません。

## 今日の割り当て（この通りに出題すること）

| 項目 | 値 |
|---|---|
| 日付 | 2026-09-08（Tue） |
| Track | **DB / Table Design** |
| Format | **Review** |
| Level | **L1** |
| 回答環境 | モバイル想定 |
| 想定所要時間 | 30分 |
| 今日はセッション日か | はい |
| 今日の記録 | 未保存 |

選定理由（本人向け。問題文には書かない）

- Track: 重み・弱点・連続回避から選択
- Level: base_level L1 のまま
- Format: モバイル想定のためReviewを選択

## 今日狙う弱点（問題文に弱点名を書かず、必ず表面化させること）

- `W001` [High] 論理削除と一意制約の衝突に気づけない（期限 2026-09-08）

## 未クローズの弱点（上位8件）

| ID | Priority | Weakness | Track | Retest on |
|---|---|---|---|---|
| W005 | High | HandlerとDomainの責務境界を正しく分離できない | Layered Architecture | 2026-09-12 |
| W006 | High | 具象Repositoryへの依存を依存性逆転として説明できない | Layered Architecture | 2026-09-12 |
| W002 | High | 複合インデックスの列順を決める基準を説明できない | DB / Table Design | 2026-09-10 |
| W001 | High | 論理削除と一意制約の衝突に気づけない | DB / Table Design | 2026-09-08 |
| W007 | Med | Domainに置くべき業務ルールを具体的に切り出せない | Layered Architecture | 2026-09-16 |
| W003 | Med | 時間帯の重なり判定を構造で表現できない | DB / Table Design | 2026-09-12 |
| W004 | Low | 状態をBOOLEANで持ち、拡張性を検討しない | DB / Table Design | 2026-09-17 |

## 直近の出題履歴（題材の重複を避ける。同じ題材は10回空ける）

| Date | Track | Format | Level | Title |
|---|---|---|---|---|
| 2026-09-07 | Layered Architecture | Design | L2 | 2026-09-07 — 価格計算APIの責務分離と依存方向 |
| 2026-09-03 | DB / Table Design | Design | L2 | 2026-09-03 — 会議室予約のダブルブッキングを構造で防ぐ |

## 今の数字

| Metric | Value |
|---|---|
| 直近5回の平均スコア | 34.0 |
| 30分内完了率（直近10回） | 0% |
| 記録済みセッション数 | 2 |
| Open弱点 | 7件（High 4件） |
| 再テスト期限切れ | 1件 |

### Track別平均（直近20回）

| Track | Avg |
|---|---|
| DB / Table Design | 68.0 |
| Layered Architecture | 0.0 |
| Web / API / HTTP | — |
| Network / Infra | — |

## 今週の重点（CURRENT_FOCUS.md 抜粋）

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

## Concepts to activate

- 第3正規形とその意図的な崩し方
- 一意制約 vs アプリケーション側チェック
- READ COMMITTED と REPEATABLE READ の違い
- 複合インデックスの列順
- 依存性逆転の原則が守られている状態の見分け方

## Levelの意味

| Level | 出題の重心 |
|---|---|
| L1 | 定義を使って設計を直せるか。選択肢を示してよい |
| L2 | 要件から妥当な設計を自力で書けるか。定石を知っているか |
| L3 | 非機能要件を入れて複数案を比較できるか。代償を語れるか |
| L4 | 制約下でアーキテクチャを選定し、ADRを書けるか |

## Formatの意味

- **Design:** 要件を渡し、スキーマ・構成・インターフェースを設計させる
- **Review:** ありそうな「悪い設計」を提示し、問題点の指摘と修正を求める。悪い設計は自然に見えるものにする
- **Debug:** 症状と観測できる事実だけを渡し、切り分け手順を書かせる。原因は明かさない
- **Explain:** 「〜とは」ではなく「この状況で相手に説明せよ」の形にする

---

<!-- eos:context date=2026-09-08 track=DB / Table Design format=Review level=L1
     targets=W001 -->
