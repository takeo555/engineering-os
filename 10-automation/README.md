# Automation

「通知 → 出題 → レビュー → GitHub保存」を、**Claude.ai Pro と GitHub Actions** で回す構成です。
Claude Code は使いません。Anthropic API も使いません。

## 前提とする環境

| 項目 | 本構成での前提 |
|---|---|
| 試験官 | **Claude.ai Pro**（Project ＋ 定期タスク） |
| Repository | **Public**（raw URL で CONTEXT.md を読める） |
| スマホ | Claude アプリ |
| 追加の課金 | Anthropic API は使わない |

## なぜこの構成になるのか

| 役割 | 担当 | 理由 |
|---|---|---|
| 今日何を出すか | Actions（`build-context`） | 弱点の再テストを日によって寄せない |
| 「今日の1問」と送る | Claude 定期タスク 07:00 | 着火だけ。問題は作らない |
| 問題文・採点 | Claude Project | 対話向き。モバイルで解ける |
| 記録の入口 | Issue #1「記録の投函口」 | Importer を通す。直接コミットしない |
| 記録の正本 | Actions（`save-record`） | 点数固定と弱点の重複防止 |

定期タスクに出題させると、試験官のルールを持たない会話で問題が分かれます。
出題は Project に寄せます。

## 構成

```text
06:00 JST  Actions: build-context（context.yml）
             ├─ 弱点・スコア履歴・出題履歴を読む
             ├─ Track / Format / Level / 狙う弱点を決定論的に決める
             └─ CONTEXT.md と STATUS.md を再生成してコミット
                                    │
07:00      Claude 定期タスク
             └─ 「Projectを開いて『今日の1問』と送って」と通知するだけ
                                    │
           Claude Project「Engineering OS 試験官」
             ├─ raw の CONTEXT.md を読み、その割り当て通りに出題
             │        ↓（自分: 30分で解いて、同じ会話に回答を貼る）
             ├─ anchors.md を参照して5軸採点
             ├─ 60秒サマリ → 詳細レビュー → 記録ブロック
             └─ 記録ブロックを自分で Issue #1 へコメント（手貼り）
                                    │
自動       Actions: save-record（record.yml）
             ├─ 記録ブロックをパース
             ├─ セッション記録を 04-sessions/daily/ へ書く
             ├─ 弱点の開閉、scores.csv、CONTEXT.md を更新
             └─ 結果を投函口にコメントで返す
                                    │
日曜20:45  Actions: review-facts.yml → WEEKLY_CONTEXT.md（数字だけ）
日曜21:00  Claude定期タスク: 講評を書いて Issue #1 へコメント
毎月1日21:00                        → MONTHLY_CONTEXT.md
```

手で残るのは **「今日の1問」と送る / 解いて回答を貼る / 週1回 Bank の adopt を書き写す** です。
記録ブロックは自分で投函口へ貼ります（**これが標準**）。手順は [inbox.md](inbox.md)。

## なぜ出題内容は試験官、割り当てはActionsなのか

**問題文は試験官が書きます。**
しかし **何を出すか（Track / Format / Level / 狙う弱点）はActionsが決めます。**

試験官に選ばせると、日によって好きなTrackに寄り、期限の来た弱点が放置されます。
`CONTEXT.md` に「今日はこれを出せ」と書いてあり、試験官はその通りに書くだけ、という分担です。
同じ日に何度実行しても割り当ては変わりません（日付をシードにしています）。

---

## セットアップ手順

### 1. Repositoryを作る（Public）

既にある場合は飛ばす。ブランチ名は `main`。

Publicにするのは、試験官が raw URL で `CONTEXT.md` を読めるようにするためです。これが唯一の GitHub → Claude の経路です。
会社の情報は書かないでください。

### 2. Actionsの書き込み権限を有効にする

**Settings → Actions → General → Workflow permissions** で `Read and write permissions` を選びます。
APIキーの登録は不要です。

### 3. CONTEXT.md を1回作る

```bash
gh workflow run context.yml
gh run watch
```

`https://raw.githubusercontent.com/takeo555/engineering-os/main/CONTEXT.md` が読めること。

### 4. Claude で Project を作る

サイドバーの **Projects → 新規**、名前は `Engineering OS 試験官`。

1. **指示欄**: [prompts/project-instructions.md](../prompts/project-instructions.md) の `---` 以下を貼る
2. **ファイル**
   - `07-scorecard/anchors.md` — **必須**
   - `prompts/examiner-manual.md`
   - `prompts/record-block.md`
   - `01-skill-map/README.md`
3. **入れないもの**: `weakness-log.md`、`scores.csv`
4. GitHub コネクタは不要（読み取り専用でIssueに書けないため使わない）

ルールを変えたあとは、指示欄と Knowledge を差し替える。git に書いただけでは Claude 側は変わりません。

### 5. 定期タスクを登録する

文面は [prompts/claude-tasks.md](../prompts/claude-tasks.md)。

- 毎日 07:00 JST: 「今日の1問」と送るよう促す（**出題はさせない**）
- 日曜 21:00 JST: `WEEKLY_CONTEXT.md` を読み、講評を書いて Issue #1 へコメントする

週次の数字は 20:45 に Actions が書く。今週分でなければ投稿せず止まる。

### 5.5. 記録の投函口を作る

```bash
gh issue create --title "📥 記録の投函口" --body "ここに記録ブロックをコメントで貼る"
gh issue pin <番号>
```

日次も週次もここにコメントします。新しいIssueは作りません。

### 6. 通しで確認する

1. Projectで「今日の1問」と送る → CONTEXT.mdの割り当て通りの問題が出るか
2. 適当な回答を送る → 60秒サマリ → 詳細レビュー → 記録ブロックが出るか
3. 試験官が Issue #1 へコメントしたか（しなければ手貼り）
4. 1〜2分後、同じIssueに「記録しました」が返るか
5. `04-sessions/daily/` にコミットが入り、`STATUS.md` が動くか

チェックリストは [setup-checklist.md](setup-checklist.md)。

---

## 壊れたときの切り分け

| 症状 | 原因 | 対処 |
|---|---|---|
| 何もコメントが返らない | `type: session` の行がない | 試験官に「記録ブロックを出し直して」と言い、コメントを編集する |
| 「取り込めませんでした」と返る | ヘッダが崩れている | 原文は `04-sessions/inbox/` にある。ヘッダだけ直して編集する |
| 試験官がCONTEXT.mdを読めない | raw URLの誤り / Private | URLを開く。読めなければ中身を会話に貼る |
| 点数が明らかに甘い | `anchors.md` を参照していない | 「anchors.mdの見本と比べて」と送る |
| チャットの点とGitHubの点が違う | 記録時に採点し直している | 確定した5軸をそのまま写す |
| 所要時間がいつも30分 | 制約時間を実測として書いている | 明示された実測だけ。不明なら0 |
| 記録用の新しいIssueができた | 投函口ではなく新規作成している | 本文を Issue #1 へ移す |
| 定期タスクが届かない | タスク未登録 / 通知オフ | Projectを開いて「今日の1問」と送る |
| 試験官が「投稿できません」と言う | 投稿を試みる古い指示が残っている | 指示欄と examiner-manual を最新版に差し替える。投函は手貼りが標準 |
| Workflowが動かなくなった | 60日以上休止すると自動無効化 | `gh workflow enable context.yml` で戻す |

## この構成が失うもの

- 投函は常に手貼り（1日30秒）
- 定期タスクが Project の Knowledge を読めないことがあるので、日次の出題は Project 側に残している

失わないものは、**記録すべて**です。Claude 側が使えなくなっても、GitHub にある学習資産は残ります。
