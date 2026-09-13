# 導入チェックリスト

上から順に進めます。詳細は [README.md](README.md) の対応する手順番号を参照してください。

## 前提確認

- [ ] Claude.ai の Pro アカウントがある
- [ ] Claude のサイドバーに **Projects** がある
- [ ] GitHubアカウントがあり、このリポジトリが Public である
- [ ] `gh auth login` でサインイン済み

## GitHub側

- [ ] 2. Settings → Actions → General → Workflow permissions を **Read and write** に変更
- [ ] 3. `gh workflow run context.yml` を実行
- [ ] 3. `CONTEXT.md` と `STATUS.md` が生成された
- [ ] 3. `https://raw.githubusercontent.com/takeo555/engineering-os/main/CONTEXT.md` をブラウザで開いて中身が見える

**この最後の1行が読めることが全ての前提です。**

## Claude Project

- [ ] 4. Projects → 新規（名前: `Engineering OS 試験官`）
- [ ] 4. 指示欄に `prompts/project-instructions.md` の `---` 以下を貼付
- [ ] 4. ファイルに **`07-scorecard/anchors.md` をアップロード**（必須）
- [ ] 4. ファイルに `prompts/examiner-manual.md` をアップロード
- [ ] 4. ファイルに `prompts/record-block.md` をアップロード
- [ ] 4. ファイルに `01-skill-map/README.md` をアップロード（任意）
- [ ] 4. `weakness-log.md` と `scores.csv` は **入れていない**
- [ ] 4. GitHub コネクタを ON にした

## 定期タスク

- [ ] 5. 毎日 07:00 JST のタスクを作り、`prompts/claude-tasks.md` のタスク1を貼付（**出題させない**）
- [ ] 5. 日曜 21:00 JST のタスクを作り、タスク2を貼付（講評して投函口へ投稿する）

## 記録の投函口

- [ ] 5.5. Issue #1「📥 記録の投函口」がある（無ければ作ってピン留め）

## スマホ

- [ ] Claude アプリにサインインし、Projectが見える
- [ ] （予備）投函口IssueのURLをホーム画面に追加した

## 通し確認

- [ ] 6. Projectで「今日の1問」と送ると、CONTEXT.mdの割り当て通りの問題が出る
- [ ] 6. 出題時にヒントや模範解答が混ざっていない
- [ ] 6. 適当な回答を送ると、**60秒サマリが先に**出る
- [ ] 6. 続けて詳細レビュー（Correctness / Strengths / Gaps / In practice / Model answer / 到達の区別）が出る
- [ ] 6. 5軸の採点が出る（この点が最終スコア）
- [ ] 6. 最後に**記録ブロック**がチャットに出る
- [ ] 6. 記録ブロックの点数が、直前の採点と一致している
- [ ] 6. `time_spent_min` が問題の「30分」ではなく、実測（不明なら0）になっている
- [ ] 6. 試験官が **Issue #1 にコメントした**（失敗したら手貼り）
- [ ] 6. 記録のために新しいIssueを作っていない
- [ ] 6. 1〜2分後、同じIssueに「記録しました」のコメントが返った
- [ ] 6. `04-sessions/daily/` に新しいコミットが入った

## 1週間後の確認

- [ ] 5日分以上、記録が溜まっている
- [ ] `weakness-log.md` に Closed が1件以上ある
- [ ] 日曜20:45に `WEEKLY_CONTEXT.md` が更新された
- [ ] 日曜21:00に Claude が講評を投函口へコメントした
- [ ] 新しいIssueが立っていない

Open弱点が増える一方でClosedが0件の場合は、試験官が `retest:` を書いていません。
Projectの指示欄を確認してください。
