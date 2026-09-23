# 導入チェックリスト

上から順に進めます。詳細は [README.md](README.md) の対応する手順番号を参照してください。

> **2026-09-23 の改修で作業順が変わりました。**
> 日次が 2026-09-11 から止まった原因は「朝、割り当てを取得できず0問で終わること」だったので、
> **指示欄の貼り直し（手順4）と、Project内での定期タスク作成（手順5）が最優先**です。
> 投函の自動化（コネクタ）は保留にしています。

## 前提確認

- [ ] Claude.ai の Pro アカウントがある
- [ ] Claude のサイドバーに **Projects** がある
- [ ] GitHubアカウントがあり、このリポジトリが Public である
- [ ] `gh auth login` でサインイン済み

## GitHub側

- [ ] 2. Settings → Actions → General → Workflow permissions を **Read and write** に変更
- [ ] 3. `gh workflow run context.yml` を実行
- [ ] 3. `TODAY.md` `CONTEXT.md` `STATUS.md` が生成された
- [ ] 3. `https://raw.githubusercontent.com/takeo555/engineering-os/main/TODAY.md` をブラウザで開いて中身が見える
- [ ] 3. `gh run list --workflow=review-facts.yml` が **0件でない**（0件なら週次レビューが死んでいる）

## コネクタ（保留・やらなくてよい）

投函を自動化する構成は [connector.md](connector.md) と [mcp/](mcp/) に用意してありますが、
**2026-09-23 時点では導入しません。** 新しいアカウント（Cloudflare）を増やさない判断です。

投函は手貼り（1日30秒）。朝の出題は定期タスク側が raw URL を読むので、コネクタ無しで回ります。

導入したくなったら `bash 10-automation/mcp/setup.sh` の1コマンドです。

## Claude Project

- [ ] 4. Projects → 新規（名前: `Engineering OS 試験官`）
- [ ] 4. 指示欄に `prompts/project-instructions.md` の `---` 以下を貼付
- [ ] 4. `07-scorecard/anchors.md` をアップロード（**必須**。無いと採点がドリフトする）
- [ ] 4. `prompts/examiner-manual.md` をアップロード
- [ ] 4. `prompts/record-block.md` をアップロード
- [ ] 4. `ROADMAP.md` をアップロード（**必須**。AIドリルの題材をフェーズで決める）
- [ ] 4. `02-tracks/coding-language.md` をアップロード
- [ ] 4. `02-tracks/code-review.md` をアップロード
- [ ] 4. `01-skill-map/README.md` をアップロード（任意）
- [ ] 4. `weakness-log.md` `scores.csv` `drill-misses.md` `TODAY.md` `CONTEXT.md` は **入れていない**

## 定期タスク（**必ず Project の中から作る**）

サイドバーの「Scheduled」から単独で作らないこと。Knowledge が読めず採点できないうえ、
結果の会話が Project の外に出て iPhone から辿り着けません。

- [ ] 5. Project の中で 毎日 07:00 JST のタスクを作り、`prompts/claude-tasks.md` のタスク1を貼付
- [ ] 5. Project の中で 日曜 21:00 JST のタスクを作り、タスク2を貼付
- [ ] 5. 翌朝、**iPhone で Projects → 試験官 → チャット一覧** に新しい会話が並んでいる

## 記録の投函口

- [ ] 5.5. Issue #1「📥 記録の投函口」がある（無ければ作ってピン留め）

## 通し確認（**iPhone で行う**）

デスクトップで通っても意味がありません。折れているのはモバイルです。

- [ ] 6. Projects → 試験官 で「今日の1問」と送ると、**まず Drill 8問がまとめて**出る（AI 3 / 言語 3 / ネットワーク 2）
- [ ] 6. 「TODAY.md がプロジェクトにありません」で止まらない（止まったら「おまかせ」と送る）
- [ ] 6. Drill に選択肢が付いていない。1問ずつ出してこない
- [ ] 6. まとめて回答すると、正答率1行＋**間違えた問題の正解**が返り、Design に進む
- [ ] 6. 続けて `TODAY.md` の割り当て通りの Design 問題が出る（15分・4Trackのいずれか）
- [ ] 6. 出題の1行目に `割り当て: <日付> / <Track> / <Format> / <Level>` がある
- [ ] 6. 出題時にヒントや模範解答が混ざっていない
- [ ] 6. 適当な回答を送ると、**30秒サマリが先に**出る
- [ ] 6. 続けて詳細レビュー（Correctness / Strengths / Gaps / In practice / Model answer / 到達の区別）が出る
- [ ] 6. 最後に**記録ブロック**が出る（Drill と Design が**1つに統合**されている）
- [ ] 6. 記録ブロックに `drill_ai:` `drill_lang:` `drill_network:` `drill_misses:` の4行がある
- [ ] 6. 本文に `## 0. Drill` セクションがある
- [ ] 6. 記録ブロックの点数が、直前の採点と一致している
- [ ] 6. `time_spent_min` が「15分」ではなく実測（不明なら0）になっている
- [ ] 6. 記録ブロックをコピーして Issue #1 へ貼れた
- [ ] 6. 記録のために新しいIssueを作っていない
- [ ] 6. 1〜2分後、同じIssueに「記録しました」のコメントが返った
- [ ] 6. `04-sessions/daily/` に新しいコミットが入った

### フォールバックの確認（1回だけやっておく）

Project で「今日の1問」と送り、raw URL の取得に失敗したときに次のように振る舞うこと。

- [ ] 割り当てを取得できなかったら、**1文だけ**で「貼る」か「おまかせ」を聞いてくる
- [ ] 「おまかせ」と送ると、**8問出る**（0問で終わらない）
- [ ] 出題の1行目に `（おまかせ・TODAY取得失敗）` が付いている

## 1週間後の確認

- [ ] 5日分以上、記録が溜まっている
- [ ] `TODAY.md` の生成時刻が毎朝 07:00 より前になっている（ファイル冒頭の「生成:」行）
- [ ] `05-failures/drill-misses.md` に日付セクションが追記されている
- [ ] 翌日の `TODAY.md` の Drill 題材枠に「直近miss」が出た
- [ ] `07-scorecard/scores.csv` の `drill_*` 列が埋まっている
- [ ] `weakness-log.md` に Closed が1件以上ある
- [ ] 日曜17:35に `WEEKLY_CONTEXT.md` が更新された（`gh run list --workflow=review-facts.yml` で実行を確認）
- [ ] 日曜21:00に Claude が講評を投函口へ投稿した
- [ ] 新しいIssueが立っていない

Open弱点が増える一方でClosedが0件の場合は、試験官が `retest:` を書いていません。
Projectの指示欄を確認してください。
