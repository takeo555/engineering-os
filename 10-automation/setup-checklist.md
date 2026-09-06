# 導入チェックリスト

上から順に進めます。所要 30〜40分。詳細は [README.md](README.md) の対応する手順番号を参照してください。
**課金は一切発生しません。** APIキーもPATも使いません。

## 前提確認

- [ ] ChatGPTの個人アカウントがある（無料プランでよい）
- [ ] ChatGPTのサイドバーに **Projects** がある
- [ ] GitHubアカウントがあり、Publicリポジトリを作れる
- [ ] Macのターミナルで `gh --version` が出る（出なければ `brew install gh`）
- [ ] `gh auth login` でサインイン済み

## GitHub側（10分）

- [ ] 1. zipを展開したフォルダへ `cd` した
- [ ] 1. `git init -b main`（**ブランチ名が main であること。master だと全部動かない**）
- [ ] 1. `git add -A && git commit -m "chore: init Engineering OS"`
- [ ] 1. `gh repo create engineering-os --public --source=. --push`
- [ ] 1. GitHubのWeb画面でリポジトリが **Public** になっている
- [ ] 2. Settings → Actions → General → Workflow permissions を **Read and write** に変更
- [ ] 3. `gh workflow run context.yml` を実行
- [ ] 3. `CONTEXT.md` と `STATUS.md` が生成された
- [ ] 3. `CONTEXT.md` に今日のTrack / Format / Levelが入っている
- [ ] 3. `https://raw.githubusercontent.com/<OWNER>/<REPO>/main/CONTEXT.md` をブラウザで開いて中身が見える

**この最後の1行が読めることが全ての前提です。** 読めないならPublicになっていません。

## ChatGPT Project（15分）

- [ ] 4. Projects → 新規プロジェクト（名前: `Engineering OS 試験官`）
- [ ] 4. 指示欄に `prompts/project-instructions.md` の `---` 以下を貼付
- [ ] 4. `<OWNER>/<REPO>` を置換した（**3か所**）
- [ ] 4. ファイルに **`07-scorecard/anchors.md` をアップロード**（必須）
- [ ] 4. ファイルに `prompts/examiner-manual.md` をアップロード
- [ ] 4. ファイルに `prompts/record-block.md` をアップロード
- [ ] 4. ファイルに `01-skill-map/README.md` をアップロード（任意）
- [ ] 4. `weakness-log.md` と `scores.csv` は **入れていない**

## 定期タスク（5分）

- [ ] 5. 毎日（朝）のタスクを作成し、`prompts/chatgpt-tasks.md` のタスク1を貼付（**リマインドのみ。出題させない**）
- [ ] 5. 日曜（夜）のタスクを作成し、タスク2を貼付
- [ ] 5. `<OWNER>/<REPO>` を置換した
- [ ] 5. 定期タスクの枠を1つ空けてある（無料は3個まで）

## 記録の投函口（5分）

- [ ] 5.5. `gh issue create --title "📥 記録の投函口"` でIssueを1つ作った
- [ ] 5.5. `gh issue pin <番号>` でピン留めした
- [ ] 5.5. そのIssueのURLを控えた

## スマホ（5分）

- [ ] ChatGPTアプリにサインインし、Projectが見える
- [ ] 投函口IssueのURLを **ホーム画面に追加した**（Safari → 共有 → ホーム画面に追加）
- [ ] ホーム画面のアイコンから開いて、コメント欄が出る
- [ ] （任意）[inbox.md](inbox.md) の方式Cでショートカット化した

## 通し確認（10分）

- [ ] 6. Projectで「今日の1問」と送ると、CONTEXT.mdの割り当て通りの問題が出る
- [ ] 6. 出題時にヒントや模範解答が混ざっていない
- [ ] 6. 適当な回答を送ると、**60秒サマリが先に**出る
- [ ] 6. 続けて詳細レビュー（Correctness / Strengths / Gaps / In practice / Model answer）が出る
- [ ] 6. 5軸の採点が出る
- [ ] 6. 最後に**記録ブロック**が1つのコードブロックで出る
- [ ] 6. 記録ブロックをコピーし、投函口にコメントとして貼った
- [ ] 6. 1〜2分後、同じIssueに「記録しました」のコメントが返った
- [ ] 6. 投函口は開いたままになっている（毎日ここに貼り続ける）
- [ ] 6. `04-sessions/daily/` に新しいコミットが入った
- [ ] 6. `STATUS.md` の数字が動いた
- [ ] 6. `CONTEXT.md` の割り当てが変わった

## 運用開始前の掃除（5分）

- [ ] `04-sessions/daily/2026/2026-09-03.md` を削除（サンプル）
- [ ] `07-scorecard/scores.csv` の 2026-09-03 の行を削除
- [ ] `05-failures/weakness-log.md` の W001〜W004 を削除
- [ ] `03-banks/promotion-queue.md` の3行を削除
- [ ] `03-banks/*.md` のサンプル項目を削除するか、自分の言葉に書き換え
- [ ] `CURRENT_FOCUS.md` の Period を今週に更新
- [ ] `eos.config.json` の `session_days` と `keyboard_days` を自分の生活に合わせる

`07-scorecard/anchors.md` は**削除しないでください**。採点の物差しです。

## 1週間後の確認

- [ ] 5日分以上、記録が溜まっている
- [ ] `weakness-log.md` に Closed が1件以上ある（＝再テストが機能している）
- [ ] Open弱点が15件を超えていない
- [ ] 日曜21:00に `WEEKLY_CONTEXT.md` が更新された
- [ ] 週次レビューをChatGPTに書かせ、Issueに貼って保存した
- [ ] `CURRENT_FOCUS.md` が翌週向けに書き換わった

Open弱点が増える一方でClosedが0件の場合は、ChatGPTが `retest:` を書いていません。
Projectの指示欄にある「再テストの判定」の節が正しく貼られているか確認してください。

## 続かなくなったときに最初に疑うこと

- [ ] 朝の30分が取れていない → `eos.config.json` の `session_days` を減らす。毎日をやめる
- [ ] 記録ブロックを貼るのが面倒 → ホーム画面アイコンにしたか確認。まだ重いなら [inbox.md](inbox.md) の方式C（1タップ化）
- [ ] 問題が難しすぎる → `base_level` は週次で自動調整されるが、手で下げてもよい
- [ ] English OSなど他の習慣と衝突している → **両方を毎日やらない。** 曜日で分ける
