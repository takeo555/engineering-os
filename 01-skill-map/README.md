# Skill Map

優先するCore Skillsは8つです。単独で学ぶのではなく、日次の設計問題の中で組み合わせます。

| Skill | Purpose | Observable behavior | Mastery evidence |
|---|---|---|---|
| Requirement Reading | 要件から設計に必要な情報を取り出す | 曖昧な点を質問として言語化できる | 前提の抜けを設計前に指摘できる |
| Data Modeling | 実体と関係を正しく表現する | ER図と主キー・外部キーを根拠付きで書く | 正規化と意図的な非正規化を説明できる |
| Consistency Design | 不正な状態を作れない構造にする | 制約・一意性・トランザクション境界を設計する | 競合状態を制約で防いだ設計を書ける |
| Interface Design | 境界を決め、契約を明確にする | API/関数の入出力・エラー・冪等性を定義する | 破壊的変更なしに拡張できる設計を出せる |
| Layering | 依存方向を制御する | レイヤーごとの責務と依存方向を図示できる | 依存性逆転が必要な箇所を特定できる |
| Performance Reasoning | 遅さの原因を構造から説明する | 計算量・I/O回数・インデックス利用を見積もる | 実測前に候補を2〜3個に絞れる |
| Failure Analysis | 障害を上位から切り分ける | レイヤー順に仮説と確認手段を並べる | 最短手数で原因レイヤーを特定できる |
| Trade-off Articulation | 判断の根拠を説明する | 選択肢・条件・採用理由・捨てたものを述べる | レビューで設計案を通せる |

## Priority sequence

### Layer 1: Get the data right

`Requirement Reading → Data Modeling → Consistency Design`

データ構造の誤りは後段のすべてに波及します。ここを反射で書けるまで反復します。

### Layer 2: Get the boundaries right

`Interface Design → Layering`

境界の設計は変更容易性を決めます。図と依存方向をセットで書きます。

### Layer 3: Keep it running

`Performance Reasoning → Failure Analysis → Trade-off Articulation`

作った後に説明・運用できるかを問います。

## Level definitions

出題難易度はL1〜L4で管理します。現在の基準レベルは`CURRENT_FOCUS.md`にあります。
当面の出題は L1（基礎期間）。各レベルの到達点の定義は変えない。

| Level | Target | Example expectation |
|---|---|---|
| L1 | 基礎の確認 | 正規形の定義を使って設計を直せる |
| L2 | 若手実務 | 要件から妥当なスキーマとAPIを設計できる |
| L3 | 中堅実務 | 非機能要件を入れて設計判断を比較できる |
| L4 | シニア | 制約下でアーキテクチャを選定しADRを書ける |

## Practice rules

- 各セッションでFocus Skillを1〜2個だけ選ぶ
- 「読んだ」ではなく「30分で書けた」で評価する
- 同じ弱点が2回出たら、Bankへ追記して翌週に再テストする
- 週末にScorecardを更新し、翌週の重点を決める
