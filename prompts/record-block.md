# 記録ブロックの雛形

ChatGPTはレビューの最後にこの形で1つのコードブロックを出す。
ユーザーはそれをコピーし、GitHubで新しいIssueを作って本文に貼るだけでよい（タイトルは何でもよい）。

## 崩してはいけない点

- ヘッダは `---` で挟む。`key: value` の1行1項目のみ。入れ子・配列・引用符・コメントを書かない
- `type:` の行は必須。これが無いとGitHub側のWorkflowが起動しない
- 点数は5軸すべてを整数で書く（`18` でも `18/30` でも読める）
- コードブロックの中に別のコードブロック（```）を入れない。DDLやコードは4スペースのインデントで書く
- 弱点は `weakness_1:` `weakness_2:` と番号を振る。最大5件
- 「なし」の項目は行ごと省いてよい

## 日次セッション

````text
```markdown
---
type: session
date: 2026-09-07
track: DB / Table Design
format: Design
level: L2
title: 予約システムの重複予約を防ぐテーブル設計
time_spent_min: 32
correctness: 18
completeness: 15
reasoning: 19
practicality: 8
clarity: 8
retest: W001=passed, W002=failed(同じ誤りを繰り返した)
weakness_1: High | DB / Table Design | 論理削除と一意制約の衝突に気づけない
weakness_2: Med | DB / Table Design | 時間帯の重なり判定を構造で表現できない
bank_1: pattern | 排他制約で時間帯の重複を防ぐ
next_hint: 次はロックの粒度を問う
---

## 1. Problem

### 前提
（出題した前提をそのまま）

### 要件
1. …

### 提出物
- …

### 制約
- …

## 2. My answer

（ユーザーの回答を原文のまま。整形も要約もしない）

## 3. Review

### 3.1 Correctness
…

### 3.2 Strengths
…

### 3.3 Gaps
…

### 3.4 In practice
…

### 3.5 Model answer
…

## 6. What I learned

1. …
2. …
3. …
```
````

### 各項目の意味

| Key | 必須 | 内容 |
|---|---|---|
| `type` | ✓ | `session` 固定 |
| `date` | ✓ | CONTEXT.mdの日付（Asia/Tokyo） |
| `track` | ✓ | 4Trackのいずれか。`DB` のような略称でも読める |
| `format` / `level` | | CONTEXT.mdの割り当てをそのまま |
| `title` | | 20〜40字。体言止め |
| `time_spent_min` | | 申告された所要時間 |
| 5軸の点数 | | `correctness` `completeness` `reasoning` `practicality` `clarity` |
| `retest` | 狙う弱点がある日は✓ | `W001=passed, W002=failed(理由)` |
| `weakness_N` | | `優先度 \| Track \| 〜できない`。「知識不足」のような抽象語は禁止 |
| `bank_N` | | `pattern\|pitfall\|tradeoff\|term \| 一言` |
| `next_hint` | | 翌日の出題に反映してほしい点 |

## 週次レビュー

````text
```markdown
---
type: weekly
week: 2026-W37
base_level: L2
---

## 1. 今週の事実

…

## 2. 詰まった原因（1つだけ）

…

## 3. 来週やること

…

## NEXT CURRENT_FOCUS

（ここから下がそのまま CURRENT_FOCUS.md を置き換える。
　既存の構成・見出し順を維持し、Periodは翌週の月曜〜日曜にする）

# Current Focus

## Current cycle
…
```
````

`## NEXT CURRENT_FOCUS` の見出しが無ければ CURRENT_FOCUS.md は変更されない。
`base_level` は WEEKLY_CONTEXT.md に書かれている決定値をそのまま写すこと。自分で決めない。
