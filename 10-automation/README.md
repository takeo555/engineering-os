# Automation

「通知 → 出題 → レビュー → GitHub保存」を、**Claude.ai Pro と GitHub Actions** で回す構成です。
Claude Code は使いません。Anthropic API も使いません。

## 前提とする環境

| 項目 | 本構成での前提 |
|---|---|
| 試験官 | **Claude.ai Pro**（Project ＋ **Project内の**定期タスク） |
| 読み書き | 読みは raw URL（+ タスク側で先読み）。書きは**手貼り**。コネクタは未導入（[connector.md](connector.md)） |
| Repository | **Public**（コネクタが落ちた日の予備として raw URL を使う） |
| スマホ | Claude アプリ。Projects → 試験官 → チャット一覧から入る |
| 追加の課金 | Anthropic API は使わない。GitHub MCP も Copilot 契約は不要 |

**モバイルの Project チャットは、指示欄に書かれただけの URL を取りに行きません。**
指示文をいくら強く書いても直りません。そのため **07:00 の定期タスク側で先に読んで出題しておき、
iPhone 側は何も取りに行かなくてよい**構成にしています。取れなかった日は「おまかせ出題」に落ちます。

## なぜこの構成になるのか

| 役割 | 担当 | 理由 |
|---|---|---|
| 今日何を出すか | Actions（`build-context`） | 弱点の再テストを日によって寄せない |
| Drill 8問を出す | **Project内の**定期タスク 07:00 | 開いた瞬間に手が動く状態を作る |
| Design 問題・採点 | 同じ会話の続き | Knowledge（anchors.md）が要るので Project 内 |
| 記録の入口 | Issue #1「記録の投函口」 | Importer を通す。直接コミットしない |
| 記録の正本 | Actions（`save-record`） | 点数固定と弱点の重複防止 |

定期タスクは **Project の中から作ります。** サイドバーの「Scheduled」から単独で作ると
Knowledge が読めず採点できないうえ、結果の会話が Project の外に出てモバイルから辿れません。

## 構成

```text
03:10 JST  Actions: build-context（context.yml）
             ├─ 弱点・スコア履歴・出題履歴を読む
             ├─ Track / Format / Level / 狙う弱点を決定論的に決める
             └─ TODAY.md / CONTEXT.md / STATUS.md を再生成してコミット
             （05:40 に予備実行。GitHub の遅延は数時間出るので 07:00 まで余裕を取る）
                                    │
07:00      Project内の定期タスク「今日のDrill」
             ├─ raw で TODAY.md を読む（だめなら jsDelivr → おまかせ）
             └─ Drill 8問を1メッセージで出して待つ
                                    │
           自分: iPhone で Projects → 試験官 → 最新チャット を開いて回答
                                    │
           同じ会話の続き（Knowledge が効く）
             ├─ Drill 採点 → 間違いの正解を1行ずつ
             ├─ Design 15分問題を出す → 解く
             ├─ anchors.md を参照して5軸採点
             ├─ 30秒サマリ → 詳細レビュー → 記録ブロック
             └─ 記録ブロックをチャットに出す（投稿は試みない）
                                    │
約30秒     自分: 記録ブロックをコピーして Issue #1 へ貼る
                                    │
自動       Actions: save-record（record.yml）
             ├─ 記録ブロックをパース
             ├─ セッション記録を 04-sessions/daily/ へ書く
             ├─ 弱点の開閉、scores.csv、TODAY.md / CONTEXT.md を更新
             └─ 結果を投函口にコメントで返す
                                    │
日曜17:35  Actions: review-facts.yml → WEEKLY_CONTEXT.md（数字だけ）
日曜21:00  Project内の定期タスク: 講評を書いて Issue #1 へ投稿
毎月1日18:35                        → MONTHLY_CONTEXT.md
```

手で残るのは **解いて回答を書く / 記録ブロックを貼る / 週1回 Bank の adopt を書き写す** の3つです。
投函の手順は [inbox.md](inbox.md)。

## なぜ出題内容は試験官、割り当てはActionsなのか

**問題文は試験官が書きます。**
しかし **何を出すか（Track / Format / Level / 狙う弱点）はActionsが決めます。**

試験官に選ばせると、日によって好きなTrackに寄り、期限の来た弱点が放置されます。
`TODAY.md` に「今日はこれを出せ」と書いてあり、試験官はその通りに書くだけ、という分担です。
同じ日に何度実行しても割り当ては変わりません（日付をシードにしています）。

### TODAY.md と CONTEXT.md の使い分け

| ファイル | 大きさ | 誰が読むか |
|---|---|---|
| `TODAY.md` | 約30行 | **試験官。毎朝これだけ読めば出題できる** |
| `CONTEXT.md` | 約7KB | 人間が経緯を追うとき。弱点一覧・履歴14件・Level/Formatの定義まで入った全量版 |

`CONTEXT.md` は静的な定義が大半を占めていて、モバイルで貼るには大きすぎました。
毎日変わる約30行だけを切り出したのが `TODAY.md` です。

---

## セットアップ手順

### 1. Repositoryを作る（Public）

既にある場合は飛ばす。ブランチ名は `main`。

Publicにするのは、コネクタが使えない環境でも raw URL で `TODAY.md` を読めるようにするためです。
会社の情報は書かないでください。

### 2. Actionsの書き込み権限を有効にする

**Settings → Actions → General → Workflow permissions** で `Read and write permissions` を選びます。
APIキーの登録は不要です。

### 3. TODAY.md を1回作る

```bash
gh workflow run context.yml
gh run watch
```

`https://raw.githubusercontent.com/takeo555/engineering-os/main/TODAY.md` が読めること。

### 3.5.（保留）MCP コネクタ

投函を自動化する場合の構成は [connector.md](connector.md) と [mcp/](mcp/) にコードごと置いてあります。
**2026-09-23 時点では導入していません。** 新しいアカウント（Cloudflare）を増やさない判断です。
朝の出題は定期タスク側が raw URL を読むので、コネクタが無くても回ります。

導入するときは [mcp/README.md](mcp/README.md)（`bash 10-automation/mcp/setup.sh` で1コマンド）。

### 4. Claude で Project を作る

サイドバーの **Projects → 新規**、名前は `Engineering OS 試験官`。

1. **指示欄**: [prompts/project-instructions.md](../prompts/project-instructions.md) の `---` 以下を貼る
2. **ファイル**（7つ）
   - `07-scorecard/anchors.md` — **必須**。これが無いと採点がドリフトする
   - `prompts/examiner-manual.md`
   - `prompts/record-block.md`
   - `ROADMAP.md` — **必須**。AIドリルの題材をフェーズで決める
   - `02-tracks/coding-language.md`
   - `02-tracks/code-review.md`
   - `01-skill-map/README.md`
3. **入れないもの**: `weakness-log.md`、`scores.csv`、`TODAY.md`、`CONTEXT.md`
   （日々変わるものは Knowledge に入れず、毎回コネクタで取る）
4. 手順3.5 のコネクタが **この Project で有効になっていることを確認する**

ルールを変えたあとは、指示欄と Knowledge を差し替える。git に書いただけでは Claude 側は変わりません。

### 5. 定期タスクを登録する（**必ず Project の中から作る**）

文面は [prompts/claude-tasks.md](../prompts/claude-tasks.md)。

- 毎日 07:00 JST: `TODAY.md` を読み、**Drill 8問を出して待つ**
- 日曜 21:00 JST: `WEEKLY_CONTEXT.md` を読み、講評を書いて Issue #1 へ投函する

サイドバーの「Scheduled」から単独で作らないこと。Knowledge が読めず採点できないうえ、
結果の会話が Project の外に出て、iPhone から辿り着けなくなります。

週次の数字は 17:35 に Actions が書く。今週分でなければ投函せず止まる。

### 5.5. 記録の投函口を作る

```bash
gh issue create --title "📥 記録の投函口" --body "ここに記録ブロックをコメントで貼る"
gh issue pin <番号>
```

日次も週次もここにコメントします。新しいIssueは作りません。

### 6. 通しで確認する

**iPhone で通す**（デスクトップで通っても意味がありません。折れているのはモバイルです）。

1. Projects → 試験官 → 「今日の1問」と送る → **Drill 8問**が出るか
   （「CONTEXT.mdがありません」と言われたら手順3.5のコネクタが効いていない）
2. まとめて回答 → 正答率1行＋間違いの正解 → 続けて Design 15分問題が出るか
3. 適当な回答を送る → 30秒サマリ → 詳細レビュー → 記録ブロックが出るか
4. 記録ブロックをコピーして Issue #1 へ貼る
5. 1〜2分後、同じIssueに「記録しました」が返るか
6. `04-sessions/daily/` にコミットが入り、`STATUS.md` が動くか

チェックリストは [setup-checklist.md](setup-checklist.md)。

---

## 壊れたときの切り分け

| 症状 | 原因 | 対処 |
|---|---|---|
| 何もコメントが返らない | `type: session` の行がない | 試験官に「記録ブロックを出し直して」と言い、コメントを編集する |
| 「取り込めませんでした」と返る | ヘッダが崩れている | 原文は `04-sessions/inbox/` にある。ヘッダだけ直して編集する |
| モバイルで「TODAY.md がプロジェクトにありません」と言う | Project チャットが raw URL を取りに行かない | 「おまかせ」と送れば出題される。恒常的なら定期タスク側で出題させる（本構成） |
| `TODAY.md` の日付が前日 | `build-context` の遅延 | `gh workflow run context.yml`。恒常的なら cron をさらに前倒し |
| 点数が明らかに甘い | `anchors.md` を参照していない | 「anchors.mdの見本と比べて」と送る |
| チャットの点とGitHubの点が違う | 記録時に採点し直している | 確定した5軸をそのまま写す |
| 所要時間がいつも30分 | 制約時間を実測として書いている | 明示された実測だけ。不明なら0 |
| 記録用の新しいIssueができた | 投函口ではなく新規作成している | 本文を Issue #1 へ移す |
| 通知は来るが会話が開けない | タスクを Project の外で作っている | Project の中で作り直す。iPhone では Projects → 試験官 → チャット一覧から入る |
| 定期タスクが採点できない | タスクを Project の外で作っていて Knowledge が読めない | 同上 |
| 試験官が「投稿できません」と言う | 投稿を試みる古い指示が残っている | 指示欄と examiner-manual を最新版に差し替える。投函は手貼りが標準 |
| 週次レビューが書かれない | `review-facts` が動いていない | `gh run list --workflow=review-facts.yml` で確認。0件なら `gh workflow run review-facts.yml` |
| Workflowが動かなくなった | 60日以上休止すると自動無効化 | `gh workflow enable context.yml` で戻す |

## この構成が失うもの

- 投函は手貼り（1日30秒）。自動化には新しいアカウントが要るので、いまは採らない
- Design 問題は定期タスクでは出さない。Drill に答えてから会話の続きで出る

失わないものは、**記録すべて**です。Claude 側が使えなくなっても、GitHub にある学習資産は残ります。
どの経路が落ちても、3段の梯子の最後（おまかせ出題）で
**その日が0問で終わることはありません。**
