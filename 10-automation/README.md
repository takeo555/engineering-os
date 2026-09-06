# Automation

「通知 → 出題 → レビュー → GitHub保存」を、**ChatGPTの個人無料プランと追加課金ゼロ**で回すための構成と設定手順です。

## 前提とする環境

| 項目 | 本構成での前提 |
|---|---|
| ChatGPT | **個人アカウントの無料プラン**（¥0） |
| Repository | **Public**（rawファイルを誰でも読めるようにする） |
| GitHubコネクタ | あってもよいが**依存しない**。読めなければraw URLで読む |
| 追加の課金 | **なし。** OpenAI APIも使わない |
| スマホ | ChatGPTアプリ ＋ GitHubアプリ |

## なぜこの構成になるのか

無料プランで確定している制約は次の通りです。ここが設計の出発点です。

| 制約 | 影響 |
|---|---|
| ChatGPTのGitHubコネクタは**読み取り専用** | 連携してもコミットできない |
| **カスタムGPTは無料プランでは作れない**（Actionsも使えない） | ChatGPTからの書き込み経路が存在しない |
| **Projectsは無料プランでも使える**（指示欄＋ファイル5個） | 試験官の常設化はここで実現する |
| **定期タスクは無料でも使える**が、3個まで・1日1回・時刻は枠指定 | 通知には使える。時刻は正確でない |
| **定期タスクはProjectの指示もファイルも読めない** | 定期タスクは通知だけに使い、出題と採点はProject側に寄せる |
| 定期タスクのGitHubイベントトリガーは**有料のみ** | Pushをきっかけにした自動化はできない |

したがって、**ChatGPTに書き込ませることは諦めます。** 代わりに、
ChatGPTが出した「記録ブロック」を**GitHubのIssueに貼る一手**を、書き込みのスイッチにします。
コピペ1回だけ増える代わりに、PAT・カスタムGPT・有料プランへの依存がすべて消えます。

## 構成

```text
06:00 JST  Actions: context.yml
             ├─ 弱点・スコア履歴・出題履歴を読む
             ├─ Track / Format / Level / 狙う弱点を決定論的に決める
             └─ CONTEXT.md と STATUS.md を再生成してコミット
                                    │
朝         ChatGPT 定期タスク（無料枠3個のうち1個）
             └─ 「Projectを開いて『今日の1問』と送って」と通知するだけ
                                    │
           ChatGPT Project「Engineering OS 試験官」← ここで全部やる
             ├─ raw の CONTEXT.md を読み、その割り当て通りに出題
             │        ↓（自分: 30分で解いて、同じ会話に回答を貼る）
             ├─ Knowledge の anchors.md を参照して5軸採点
             ├─ 60秒サマリ → 詳細レビュー
             ├─ 狙う弱点の合否を判定（passed / failed）
             └─ 記録ブロックを1つのコードブロックで出力
                                    │
           自分: 記録ブロックをコピー → GitHubの「記録の投函口」にコメントで貼る（15秒）
                                    │
自動       Actions: record.yml（issue_comment / issues）
             ├─ 記録ブロックをパース
             ├─ セッション記録を 04-sessions/daily/ へ書く
             ├─ 合格した弱点を Closed へ、不合格は優先度+1で3日後に再テスト
             ├─ 新規弱点を登録（既存と類似なら重複させず優先度を上げる）
             ├─ scores.csv / promotion-queue.md / STATUS.md / CONTEXT.md を更新
             └─ 結果を投函口にコメントで返す（投函口は開いたまま）
                                    │
日曜21:00  Actions: review-facts.yml → WEEKLY_CONTEXT.md（数字だけ）
毎月1日21:00                        → MONTHLY_CONTEXT.md
           講評はChatGPTが書き、同じくIssueに貼って保存する
```

手で触るのは**同じ会話の中で「今日の1問」と送る／解いて回答を貼る**、そして**記録ブロックを投函口に貼る**、この3つだけです。
ChatGPT側は1本の会話で完結するので、実質「1回のやりとり ＋ 15秒のコピペ」です。

貼る手間をさらに減らす方法（ホーム画面アイコン、iOSショートカットでの1タップ化）は
[inbox.md](inbox.md) にまとめてあります。

## なぜ出題内容はChatGPT、割り当てはActionsなのか

**問題文はChatGPTが書きます**（無料で、質も出るため）。
しかし **何を出すか（Track / Format / Level / 狙う弱点）はActionsが決めます。**

ChatGPTに選ばせると、日によって好きなTrackに寄り、期限の来た弱点が放置されます。
`CONTEXT.md` に「今日はこれを出せ」と書いてあり、ChatGPTはその通りに書くだけ、という分担にすることで、
弱点の再テストが必ず回るようにしています。同じ日に何度実行しても割り当ては変わりません（日付をシードにしています）。

---

## セットアップ手順

### 1. Repositoryを作る（Public）

Macのターミナルで、展開したフォルダの中に入って実行します。
`gh` が無ければ `brew install gh` → `gh auth login` を先に済ませてください。

```bash
cd ~/Downloads/engineering-os     # zipを展開した場所
git init -b main                  # ← ブランチ名は必ず main
git add -A
git commit -m "chore: init Engineering OS"
gh repo create engineering-os --public --source=. --push
```

**`-b main` を忘れないでください。** ブランチが `master` になると、Workflowのpushトリガも
raw URL（`/main/CONTEXT.md`）も全部空振りします。既に `master` で作ってしまった場合は
`git branch -M main && git push -u origin main` で直せます。

ターミナルを使わない場合は **GitHub Desktop** でも構いません。
File → Add Local Repository でフォルダを選び、Publish repository で
「Keep this code private」の**チェックを外して**公開します。ブランチ名が `main` かだけ確認してください。

Publicにするのは、**ChatGPTのコネクタが使えなくてもraw URLで読めるようにするため**です。
無料プランではコネクタの可否がプラン・画面によって変動するので、そこに依存しない形にしてあります。
中身は自分の学習記録なので、公開しても実害はありません。会社の情報は書かないでください。

### 2. Actionsの書き込み権限を有効にする

**Settings → Actions → General → Workflow permissions** で `Read and write permissions` を選びます。
これがないと自動コミットが失敗します。**APIキーの登録は不要です。**

### 3. CONTEXT.md を1回作る

```bash
gh workflow run context.yml
gh run watch
```

Web画面からでも実行できます。Actions タブ → build-context → Run workflow。

`CONTEXT.md` と `STATUS.md` が生成され、今日のTrack / Format / Levelが入っていることを確認します。

そのあと、rawで読めることを確認します（ここが読めないと全部動きません）。

```text
https://raw.githubusercontent.com/<OWNER>/<REPO>/main/CONTEXT.md
```

### 4. ChatGPTでProjectを作る

サイドバーの **Projects → 新規プロジェクト**、名前は `Engineering OS 試験官`。

1. **指示欄**: [prompts/project-instructions.md](../prompts/project-instructions.md) の `---` 以下を貼り、`<OWNER>/<REPO>` を置換する
2. **ファイル**（無料プランは5個まで）
   - `07-scorecard/anchors.md` — **必須**。採点の見本
   - `prompts/examiner-manual.md` — 出題と採点の詳細ルール
   - `prompts/record-block.md` — 記録ブロックの雛形
   - `01-skill-map/README.md` — 鍛える能力の定義
3. **入れないもの**: `weakness-log.md`、`scores.csv`。Knowledgeは静的なので、日々変わるファイルを入れると実態とズレます

指示欄に入り切らない場合は、`project-instructions.md` 自体もファイルとしてアップロードし、
指示欄には「詳細は `project-instructions.md` に従う」とだけ書けば動きます。

### 5. 定期タスクを登録する

[prompts/chatgpt-tasks.md](../prompts/chatgpt-tasks.md) の本文をコピーして、ChatGPTの定期タスクを2つ作ります。

- 毎日（朝）: 「Projectを開いて『今日の1問』と送って」と促す（**出題はさせない**）
- 日曜（夜）: 週次レビューを促す

定期タスクはProjectの指示もファイルも読めないので、ここで出題させると
「タスクの会話で出題 → Projectへ貼り直して採点」の往復が毎日発生します。
出題はProject側に寄せて、その日の会話を1本にまとめてください。

無料プランの上限は3個なので、1つは予備として空けておきます。

### 5.5. 記録の投函口を作る

記録ブロックを毎日貼るための、**開きっぱなしのIssue**を1つ作ります。

```bash
gh issue create --title "📥 記録の投函口" --body "ここに記録ブロックをコメントで貼る"
gh issue pin <番号>
```

そのURLをスマホのホーム画面に追加しておきます。手順とショートカット化は [inbox.md](inbox.md) を参照。

### 6. 通しで確認する

1. Projectを開いて「今日の1問」と送る → CONTEXT.mdの割り当て通りの問題が出るか
2. 適当な回答を送る → 60秒サマリ → 詳細レビュー → **記録ブロック**が出るか
3. 記録ブロックをコピーし、「記録の投函口」にコメントとして貼る
4. 1〜2分後、同じIssueに「記録しました」のコメントが返るか
5. `04-sessions/daily/` にコミットが入り、`STATUS.md` の数字が動き、`CONTEXT.md` が翌日の割り当てに変わるか
6. サンプルデータを消す場合は `04-sessions/daily/2026/2026-09-03.md`、`scores.csv` の該当行、
   `weakness-log.md` の W001–W004、`promotion-queue.md` の3行を削除する

チェックリスト形式のものが [setup-checklist.md](setup-checklist.md) にあります。

---

## 壊れたときの切り分け

| 症状 | 原因 | 対処 |
|---|---|---|
| 何もコメントが返らない | 貼った文に `type: session` の行がない | ChatGPTに「記録ブロックを出し直して」と言い、コメントを**編集**して貼り直す（編集でも再実行される） |
| 「取り込めませんでした」と返る | ヘッダが崩れている | 原文は `04-sessions/inbox/` に残っている。ヘッダだけ直してIssueを編集する |
| ChatGPTがCONTEXT.mdを読めない | raw URLの誤り / Privateのまま | URLを開いて確認する。読めなければCONTEXT.mdの中身を会話に貼れば動く |
| 点数が明らかに甘い | `anchors.md` を参照していない | 「anchors.mdの見本と比べて」と一言送る。頻発するならProjectのファイルを確認する |
| 定期タスクが届かない | 無料プランは配信時刻が枠指定 | Projectを開いて「今日の1問」と送る。通知は着火装置にすぎない |
| Workflowが動かなくなった | 60日以上休止すると自動無効化される | `gh workflow enable context.yml` で戻す |

## この構成が失うもの

正直に書いておきます。

- **採点の一貫性は有料プランより弱い。** 無料枠の上限に当たると軽いモデルに落ちるため、点数がぶれます。`anchors.md` の参照はその対策ですが、完全ではありません
- **添削の往復は1回で終える設計にしてある。** 無料のメッセージ上限を食い潰さないためです。深掘りしたい日は上限に注意してください
- **コピペが1日1回増える。** これが有料プラン（カスタムGPT + Actions）との唯一の実質的な差です

失わないものは、**記録すべて**です。ChatGPT側が使えなくなっても、GitHubにある学習資産（弱点ログ、スコア、Bank、レビュー）は残ります。
将来Plusに上げたくなったら、カスタムGPTのActionsで書き込みを自動化すればコピペが消えます。Repository側は変更不要です。
