# Engineering OS

エンジニアリングを「勉強する」だけで終わらせず、実務の設計判断ができるようになるための個人運用システムです。

> 知識を増やすこと自体が目的ではない。足りなければ先に埋めるが、使えて初めて得たものとする。設計を書き、根拠を説明し、自分の案をレビューで通し、他人の設計もレビューできるようになる。

## Start here

1. [North Star](00-north-star/README.md) — 目的と、変えない判断基準
2. [Status](STATUS.md) — 今の数字（連続実施・平均点・期限切れの弱点）
3. [Current Focus](CURRENT_FOCUS.md) — 今月・今週の重点
4. [Skill Map](01-skill-map/README.md) — 優先して鍛える8つの能力
5. [Track](02-tracks/README.md) — DB / Architecture / Web-API / Network-Infra の到達目標
6. [Daily Session](04-sessions/README.md) — 1日完結型の出題を回す方法
7. [Automation](10-automation/README.md) — ChatGPT無料プランでの通知・出題・レビュー・保存の構成
8. [Operating Rules](08-operating-rules/README.md) — 更新頻度と正本のルール

## The loop

```text
North Star
    ↓
毎朝スマホにリマインドが届く（ChatGPTの定期タスク）
    ↓
Projectで「今日の1問」と送ると、今日の弱点を狙った問題が出る
    ↓
30分で解く（1日完結・持ち越さない）
    ↓
60秒サマリ → 詳細レビュー（正誤 / 良かった点 / 不足 / 実務ならどう考えるか / 点数）
    ↓
ChatGPTが出した記録ブロックを、GitHubの「記録の投函口」に貼る（15秒）
    ↓
Session RecordがGitHubへ保存され、再テストの合否が判定される
    ↓
弱点がClosedへ移動し、翌日の出題が期限の来た弱点から選ばれる
```

学習時間ではなく、**解いた問題数と、弱点が閉じた回数**を重視します。

## ChatGPTと使う日常運用 — Q&A

### Q. 普段、このRepositoryとChatGPTを使って何をするの？

毎朝リマインドが届きます。Projectで「今日の1問」と送って30分で解き、回答を貼るとレビューと採点が返ります。最後に出てくる「記録ブロック」をGitHubの投函口に貼れば、あとは自動です。

```text
06:00 GitHub Actions：弱点と履歴から、今日のTrack / Format / Level / 狙う弱点を決めて
      CONTEXT.md に書く（問題文は作らない）
  ↓
朝    ChatGPTの定期タスク：「Projectを開いて『今日の1問』と送って」と通知するだけ
  ↓
自分：Project「Engineering OS 試験官」を開いて「今日の1問」と送る
  ↓
ChatGPT：CONTEXT.md を読み、その割り当て通りに1問出す
  ↓
自分：30分で解いて、同じ会話に回答を貼る
  ↓
ChatGPT：60秒サマリ → 詳細レビュー → 5軸採点 → 再テストの合否判定 → 記録ブロックを出力
  ↓
自分：記録ブロックをコピーし、GitHubの「記録の投函口」にコメントで貼る（15秒）
  ↓
GitHub Actions：記録をコミットし、弱点を開閉し、CONTEXT.md を翌日用に更新して結果を返す
```

ChatGPT側は**1本の会話で完結**します。出題・採点・記録ブロックまで、開くのは1つの画面だけです。

ChatGPTは**個人アカウントの無料プラン**で使います。追加課金はありません（OpenAI APIも使いません）。
無料プランでは**ChatGPTからGitHubへ書き込めない**ため、記録ブロックを貼る一手だけが手作業として残ります。詳細は[Automation](10-automation/README.md)。

Repositoryは記録の正本、ChatGPTは出題・レビューを担当するパートナーです。

### Q. 出題される問題はどんなもの？

1日完結・目安30分の設計問題です。長期プロジェクト型は今は扱いません。

| Track | 例 |
|---|---|
| DB / Table Design | 「予約システムのダブルブッキングを防ぐテーブル設計とロック戦略を書け」 |
| Architecture | 「このユースケースをレイヤードアーキテクチャで分割し、依存方向を図示せよ」 |
| Web / API / HTTP | 「決済APIを冪等にする設計と、リトライ時の挙動を定義せよ」 |
| Network / Infra | 「特定ユーザーだけ画面が遅い。切り分け手順を上位レイヤーから書け」 |

問題は次の4形式をローテーションします。

- **Design:** 要件からスキーマ・構成・インターフェースを設計する
- **Review:** 与えられた設計やコードの問題点を指摘し、修正案を出す
- **Debug:** 症状から原因を切り分け、確認手順を組む
- **Explain:** 実務で説明できるレベルで根拠を言語化する

### Q. 30分で終わらなかったらどうする？

その日のうちに完結させます。未完成でも「どこまで考えたか」「何が分からなかったか」を回答として提出します。中断点そのものが[Weakness Log](05-failures/weakness-log.md)の材料になります。

翌日へ持ち越しません。持ち越すのは弱点だけです。

### Q. スマホで30分DDLを書くのは無理では？

そのため、曜日で出題形式が変わります。`keyboard_days`（既定: 月・水・金）はDesign / Reviewが出て、それ以外の日は散文と箇条書きで答えられるExplain / Debug / Reviewが出ます。移動中の朝に長いSQLを書かされることはありません。

### Q. 週5がきついときは？

`eos.config.json` の `session_days` を `["Mon","Wed","Fri"]` に変えるだけです。記録が飛び飛びになるより、週3を確実に埋めたほうがスコアの信頼性もBankの質も上がります。

### Q. ChatGPTは何をレビューする？

| 観点 | 内容 |
|---|---|
| Correctness | 正誤。事実として誤っている箇所 |
| Strengths | 良かった点。どの判断が実務的に妥当だったか |
| Gaps | 間違い・不足。抜けている考慮点 |
| In practice | 実務ならどう考えるか。現場の制約を入れた判断 |
| Score | 理解度・点数（100点満点、5軸） |
| Review points | 復習すべきポイント。次にいつ再テストするか |

点数は励ましのためではなく、翌日以降の出題を選ぶための入力です。甘くつけません。

採点は[`07-scorecard/anchors.md`](07-scorecard/anchors.md)の見本（50点 / 70点 / 85点）を基準に行われます。LLMの採点基準は数週間でドリフトするため、固定した見本を毎回参照させて、月をまたいでも点数の意味を一定に保ちます。

朝は**60秒サマリだけ**読めば十分です。スコアと、いちばん重い抜け3件と、再テストの合否が出ます。詳細レビューと参考解答は記録に残るので、夜に読み返してください。

### Q. 記録は何が残る？

`04-sessions/daily/YYYY/YYYY-MM-DD.md` に1日1ファイル。

- 問題
- 自分の回答（原文のまま）
- ChatGPTのレビュー
- 点数
- 弱点
- 学んだこと

加えて、弱点は[Weakness Log](05-failures/weakness-log.md)、点数は[Scorecard](07-scorecard/README.md)、Bank昇格候補は[Promotion Queue](03-banks/promotion-queue.md)へ自動で積まれます。今の状態は[STATUS.md](STATUS.md)で一覧できます。

### Q. 弱点はどうやって閉じるの？

出題側が再テスト期限の来た弱点のTrackを優先的に出し、その日の問題に「狙う弱点」として埋め込みます。ChatGPTは**その弱点の合否を必ず判定します**。合格すればClosedへ移動し、不合格なら優先度が1段上がって3日後に再テストされます。

同じ弱点が再発した場合、新しいIDでは登録されません。既存の項目の優先度が上がるだけなので、ログが同じ内容で膨らみません。

### Q. GitHubへの保存はどうやる？

**コピペ1回だけです。** ChatGPTの無料プランはGitHubへ書き込めません（コネクタは読み取り専用、カスタムGPTのActionsは無料では作れない）。そこで、ChatGPTが最後に出す**記録ブロック**を、開きっぱなしにしたIssue「記録の投函口」へコメントとして貼ります。タイトルを考える必要も、Issueを探す必要もありません。

- **読み取り:** ChatGPTが `CONTEXT.md` のraw URLを開く（Publicリポジトリなのでコネクタ不要）
- **書き込み:** Issueに貼られた記録ブロックを、Workflowがパースしてコミットする

貼ったあとは全部自動です。セッション記録の作成、弱点の開閉、スコアの追記、`CONTEXT.md` の更新、結果の返信まで1〜2分で終わります。

フォーマットが崩れていても記録は失われません。パースできなかった原文は `04-sessions/inbox/` に残り、その旨がコメントで返ります。貼ったコメントを**編集**すれば再実行されます。

ホーム画面アイコン化や、iOSショートカットで完全に1タップにする方法は[inbox.md](10-automation/inbox.md)にあります。
構成手順は[Automation](10-automation/README.md)、チェックリストは[setup-checklist.md](10-automation/setup-checklist.md)にあります。

### Q. 自分とChatGPTの役割分担は？

| You | ChatGPT |
|---|---|
| 30分、自分の頭で設計を書く | 弱点に合った問題を出す |
| 分からない箇所を隠さず提出する | 正誤・不足・実務観点でレビューする |
| 実務で試す機会を作る | 見本基準で採点し、再テストの合否を判定する |
| 記録ブロックを投函口に貼る（15秒） | 記録ブロックを固定フォーマットで出力する |
| 週1回、Bank昇格候補を書き写す（3分） | Weekly Reviewの講評を書く |
| 週1回20分、実機で確認する | — |
| 機密情報を除いて共有する | — |

手動で残るのは4つだけです。**「今日の1問」と送る / 30分解いて回答を貼る / 記録ブロックを貼る / 週1回Bank昇格を書き写す。** Bankへの書き込みを自動化していないのは、自動で流し込むとBankが使われない要約の山になるからです。

ChatGPTに設計判断そのものを任せるのではなく、**自分の設計を評価し記録に変える作業**を任せます。

### Q. 最低限、毎週何をすれば継続できる？

```text
session_days のDaily Session（既定: 毎日）
        ↓
週1回20分のFoundation（実機で確認）
        ↓
1回のWeekly Review → 翌週のFocus
```

3日以上空いたら、出題側が自動で難易度を1段下げて再開します。空白を埋めるための補講はしません。

### Q. 何をRepositoryへ書かない方がよい？

- 勤務先や顧客の実名、非公開のシステム構成
- 本番のホスト名、IP、認証情報、スキーマの実物
- 顧客データのサンプル

必要な場合は`社内システムA`、`prospect B`のような仮名と、抽象化したスキーマを使います。

## Repository map

| Area | Purpose |
|---|---|
| [`00-north-star`](00-north-star/README.md) | 最上位目的、原則、非目的 |
| [`01-skill-map`](01-skill-map/README.md) | Core Skillsと習得基準 |
| [`02-tracks`](02-tracks/README.md) | DB / Architecture / Web-API / Network-Infra別の到達設計 |
| [`03-banks`](03-banks/README.md) | Pattern / Pitfall / Tradeoff / Termの再利用資産 |
| [`04-sessions`](04-sessions/README.md) | 日次セッションの問題と記録 |
| [`05-failures`](05-failures/README.md) | 解けなかった・説明できなかった点の改善 |
| [`06-reviews`](06-reviews/README.md) | Weekly / Monthly Review |
| [`07-scorecard`](07-scorecard/README.md) | 能力と点数の推移 |
| [`08-operating-rules`](08-operating-rules/README.md) | 継続運用、命名、更新ルール |
| [`09-foundation`](09-foundation/README.md) | 基礎の穴埋めと再テスト |
| [`10-automation`](10-automation/README.md) | 通知・出題・保存の自動化構成 |
| [`CONTEXT.md`](CONTEXT.md) | 自動生成。**ChatGPTが毎朝読む唯一の入り口**。今日の割り当てと弱点と履歴 |
| [`STATUS.md`](STATUS.md) | 自動生成。連続実施・平均点・期限切れの弱点 |
| [`prompts/`](prompts/record-block.md) | ChatGPTに貼る文（Project指示 / 定期タスク / 記録ブロックの雛形） |

## Definition of success

成功は「用語を知っていること」ではありません。

- 要件から30分でスキーマと構成を書き、根拠を説明できる
- 他人の設計をレビューし、リスクを言語化できる
- 障害の切り分けを上位レイヤーから順に進められる
- 同じ弱点を2回目で閉じられる
- 実務のレビューで自分の設計案が通る
