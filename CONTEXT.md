# CONTEXT — 2026-09-11（Fri）

> **自動生成。手で編集しないこと。** 毎朝06:00 JSTと、
> 記録が保存されるたびに再生成されます。
> ChatGPTはこのファイルだけを読めば出題できます。他のファイルを読みに行く必要はありません。

## 今日の割り当て（この通りに出題すること）

| 項目 | 値 |
|---|---|
| 日付 | 2026-09-11（Fri） |
| Track | **Layered Architecture** |
| Format | **Review** |
| Level | **L1** |
| 回答環境 | キーボード想定 |
| 想定所要時間 | 30分 |
| 今日はセッション日か | はい |
| 今日の記録 | 保存済み。2問目は出さない |

選定理由（本人向け。問題文には書かない）

- Track: 重み・弱点・連続回避から選択
- Level: base_level L1 のまま
- Format: キーボード想定のためReviewを選択

## 今日狙う弱点（問題文に弱点名を書かず、必ず表面化させること）

- `W005` [High] HandlerとDomainの責務境界を正しく分離できない（期限 2026-09-12）

## 未クローズの弱点（上位8件）

| ID | Priority | Weakness | Track | Retest on |
|---|---|---|---|---|
| W010 | High | 論理削除時に一意制約がどう衝突するかを説明できない | DB / Table Design | 2026-09-14 |
| W008 | High | DomainとUsecaseの責務境界を具体的に説明できない | Layered Architecture | 2026-09-13 |
| W001 | High | 論理削除と一意制約の衝突に気づけない | DB / Table Design | 2026-09-12 |
| W005 | High | HandlerとDomainの責務境界を正しく分離できない | Layered Architecture | 2026-09-12 |
| W006 | High | 具象Repositoryへの依存を依存性逆転として説明できない | Layered Architecture | 2026-09-12 |
| W002 | High | 複合インデックスの列順を決める基準を説明できない | DB / Table Design | 2026-09-10 |
| W012 | Med | ページングにおけるOFFSET方式の課題とカーソル方式との使い分けを説明できない | Coding / Go / Next.js | 2026-09-20 |
| W013 | Med | レイヤー分離の目的を「関数を軽くする」ではなく変更理由と責務の分離として説明できない | Layered Architecture | 2026-09-20 |

## 直近の出題履歴（題材の重複を避ける。同じ題材は10回空ける）

| Date | Track | Format | Level | Title |
|---|---|---|---|---|
| 2026-09-11 | Coding / Go / Next.js | Review | L1 | 2026-09-11 — 備品一覧APIのページングと責務分離 |
| 2026-09-09 | DB / Table Design | Review | L1 | 2026-09-09 — 論理削除と一意制約が衝突する貸出管理設計 |
| 2026-09-08 | Layered Architecture | Design | L2 | 2026-09-08 — 価格計算APIの責務分離と依存方向 |
| 2026-09-07 | Layered Architecture | Design | L2 | 2026-09-07 — 価格計算APIの責務分離と依存方向 |
| 2026-09-03 | DB / Table Design | Design | L2 | 2026-09-03 — 会議室予約のダブルブッキングを構造で防ぐ |

## 今の数字

| Metric | Value |
|---|---|
| 直近5回の平均スコア | 49.6 |
| 30分内完了率（直近10回） | 75% |
| 記録済みセッション数 | 5 |
| Open弱点 | 13件（High 6件） |
| 再テスト期限切れ | 1件 |

### Track別平均（直近20回）

| Track | Avg |
|---|---|
| DB / Table Design | 44.0 |
| Layered Architecture | 42.5 |
| Web / API / HTTP | — |
| Network / Infra | — |
| Coding / Go / Next.js | 75.0 |
| AI / LLM | — |

## 今週の重点（CURRENT_FOCUS.md 抜粋）

## Current cycle

- Period: 2026-09-08 – 2026-09-30（今月の Horizon）
- Primary track: Layered Architecture
- Secondary track: Coding / Go / Next.js
- Level: L1（基礎の確認）
- North Star connection: 依存方向を指摘でき、小さな Go または Next が動く。AI は10月の生成AIパスポート。今月は出題しない

## Focus skills

1. **Layering:** レイヤーごとの責務と依存方向を図示し、違反を指摘する
2. **Interface Design:** handler / usecase、またはページ / データ取得の境界を決める

## Concepts to activate

- Presentation / Application / Domain / Infrastructure の責務
- 依存性逆転が守られている状態の見分け方
- handler に業務ルールを置かない
- ページとデータ取得の置き場所
- エラーを呼び出し側に返す

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

<!-- eos:context date=2026-09-11 track=Layered Architecture format=Review level=L1
     targets=W005 -->
