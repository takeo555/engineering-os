# Operating Rules

## 1. This repository is the source of truth

- North Star、Skill定義、Track目標、Bank、Session記録、Review、ScorecardはこのRepositoryを正本とする
- ChatGPTの回答を保存するだけではOSを更新したことにならない
- 目的や構造を変える場合は[Decision Log](decision-log.md)へ理由を残す
- 自動生成ファイル（`CONTEXT.md`、`STATUS.md`、`weakness-log.md`、`scores.csv`、`promotion-queue.md`）は手で並べ替えない
- `07-scorecard/anchors.md`は変更しない。変えると過去のスコアと比較できなくなる

## 2. One day, one problem

- 1日1問。目安30分。その日のうちに完結させる
- 30分で終わらなくても、その時点の回答を提出する
- 未完成の課題を翌日へ持ち越さない。持ち越すのは弱点だけ
- 1日に2問以上やらない。休んだ日の埋め合わせをしない
- 今は長期プロジェクト型の課題を扱わない

## 3. Cadence

### Daily（`session_days` に指定した曜日。既定は平日5日）

- 06:30 出題が生成され、Issueが立つ
- 06:31 スマホに通知が届く（GitHub Mobile。ChatGPT定期タスクを併用してもよい）
- 07:00–07:30 解く
- 07:30 60秒サマリを読む。詳細レビューは夜に記録ファイルで読んでよい

週5が重い場合は`session_days`を`["Mon","Wed","Fri"]`に落とします。記録が飛び飛びになるより、週3を確実に埋めたほうがスコアの信頼性もBankの質も上がります。

### Weekly

- 日曜21:00にWeekly Reviewが自動生成される（English OSの週次20:00と重ならない）
- 出力を5分読み、`CURRENT_FOCUS.md`の書き換え内容を確認する
- [Bank Promotion Queue](../03-banks/promotion-queue.md)の`adopt`を該当Bankへ書き写し、行を削除する（3分）
- 週1回20分、[Foundation](../09-foundation/README.md)で実機確認を行う

### Monthly

- 毎月1日21:00にMonthly Reviewが自動生成される
- 出力を確認し、Track別レベルの推奨を`eos.config.json`へ反映するか判断する
- North Starとの整合、Track比率、低価値な活動を確認する

## 4. Work-in-progress limits

- Weekly Focus Skills: 最大2
- Open High weaknesses: 最大5
- Open weaknesses 合計: 最大15
- Bankのアクティブ項目: 各20件

上限を超える場合は、新規追加の前に既存項目をCloseまたは優先外へ移します。

## 5. Difficulty control

**`base_level`を書き換えるのは週次レビューだけです。** 日次は空白期間による一時的な引き下げのみを行い、設定ファイルには書きません。両方が同じ条件で判定すると、悪い週の翌週に2段落ちます。

| 観測 | 担当 | 対応 |
|---|---|---|
| 30分内完了率が50%未満（今週3セッション以上） | 週次 | `base_level`を1段下げる |
| 5セッション移動平均が85点以上（今週3セッション以上） | 週次 | `base_level`を1段上げる |
| 今週のセッションが3回未満 | 週次 | 難易度は変えず、原因の特定を優先する |
| 前回から3日以上空いた | 日次 | その日だけ1段下げて出題する |
| 特定Trackの平均が最も低い | 日次 | そのTrackの出題確率を自動で上げる |
| 再テストで2回以上不合格 | 手動 | Foundationへ移し、実機で確認する |

難易度は気分で変えません。上の表の条件だけで変えます。判定は`scripts/weekly_review.py`の`decide_base_level()`がコード側で行い、LLMには任せません。

### 回答環境による出題形式の切替

`keyboard_days`（既定: 月・水・金）はDesign / Review、それ以外の日はExplain / Debug / Reviewが出ます。スマホで30分DDLを書く朝を作らないためです。自分の生活に合わせて`eos.config.json`で変えてください。

## 6. Evidence over feelings

「分かった気がする」ではなく、記録で判定します。

- 要件から30分で設計を書けたか
- 判断の根拠を1文で言えたか
- レビューで指摘された弱点を、再テストで閉じられたか
- 実務で自分の設計案が通ったか

## 7. Git workflow

- 自動コミットのメッセージ形式:
  - 出題: `chore(session): add problem for 2026-09-03`
  - 記録: `feat(session): record 2026-09-03 DB / Table Design (68/100)`
  - 週次: `chore(review): weekly 2026-W36`
  - 月次: `chore(review): monthly 2026-09`
- 手動更新は小さく意味のある単位で行う
- 勤務先・顧客の実名、非公開の構成、本番のホスト名やIP、認証情報は記録しない
- 仮名と抽象化したスキーマを使う（例: `社内システムA`, `prospect B`）
- Public repositoryへ変更する前に、直近のSession記録を必ず再確認する

## 8. Minimum viable week

忙しい週でも、次だけは行います。

1. 2 Sessions（平日のうち2日）
2. 1 Weekly Review
3. `CURRENT_FOCUS.md`の更新

未実施分を翌週に大量に持ち越しません。

## 9. Quarterly reset

3か月ごとに確認します。

- North Starは今も正しいか
- 4 Tracksの比率は現在の実務に合っているか
- Core Skillsの追加・統合・卒業が必要か
- Bankに使われない情報が溜まっていないか
- 出題形式（Design / Review / Debug / Explain）の比率は適切か

## 10. Automation ownership

- 自動化の構成は[10-automation](../10-automation/README.md)を正本とする
- 出題プロンプト・レビュー基準を変えた場合はDecision Logへ記録する
- Workflowが2日連続で失敗したら、手動運用へ切り替えて原因を記録する
- 外部APIキーは使わない構成にしてある。増やす場合は必ずGitHub Secretsに置き、Repositoryへ書かない
- LLMが生成した文字列を`${{ }}`でWorkflowの`run:`に展開しない。ファイル経由で受け渡す（`record.yml` は環境変数経由でIssue本文を受け取っている）
- `CONTEXT.md` の内容を手で書き換えない。出題の割り当てはコードが決める。変えたいときは `eos.config.json` を直す
- 60日以上休止するとscheduled workflowが自動無効化される。復帰時は`gh workflow enable`で戻す
