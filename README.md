# Engineering OS

エンジニアリングを「勉強する」だけで終わらせず、実務の設計判断ができるようになるための個人運用システムです。

> 知識を増やすこと自体が目的ではない。足りなければ先に埋めるが、使えて初めて得たものとする。設計を書き、根拠を説明し、自分の案をレビューで通し、他人の設計もレビューできるようになる。

## Start here

1. [North Star](00-north-star/README.md) — 目的と、変えない判断基準
2. [Status](STATUS.md) — 今の数字（連続実施・平均点・期限切れの弱点）
3. [Current Focus](CURRENT_FOCUS.md) — 今月・今週の重点
4. [Skill Map](01-skill-map/README.md) — 優先して鍛える8つの能力
5. [Track](02-tracks/README.md) — Design 4 Track の到達目標と、Drill 3カテゴリ
6. [Daily Session](04-sessions/README.md) — 1日完結型の出題を回す方法
7. [Automation](10-automation/README.md) — Claude Pro での通知・出題・レビュー・保存の構成
8. [Operating Rules](08-operating-rules/README.md) — 更新頻度と正本のルール

## The loop

```text
North Star
    ↓
毎朝07:00、Projectの定期タスクが Drill 8問を出しておく
    ↓
iPhoneで Projects → 試験官 → 最新チャット を開いて答える（4分）
    ↓
採点 → 続けて Design 15分問題が出る → 解く（1日完結・持ち越さない）
    ↓
30秒サマリ → 詳細レビュー（正誤 / 良かった点 / 不足 / 実務ならどう考えるか / 点数）
    ↓
試験官がコネクタ経由で記録ブロックを「記録の投函口」へ投稿する
    ↓
Session RecordがGitHubへ保存され、再テストの合否が判定される
    ↓
弱点がClosedへ移動し、翌日の出題が期限の来た弱点から選ばれる
```

学習時間ではなく、**解いた問題数と、弱点が閉じた回数**を重視します。

## Claudeと使う日常運用 — Q&A

### Q. 普段、このRepositoryとClaudeを使って何をするの？

毎朝7時に、Projectの定期タスクが Drill 8問を出しておきます。iPhoneで Projects → 試験官 → 最新チャット を開いて答えると、採点のあと Design 15分問題が出ます。合計20分。試験官が記録ブロックを Issue #1「📥 記録の投函口」へ投稿すれば、あとは自動です。新しいIssueは作りません。

```text
03:10 GitHub Actions（build-context）：弱点と履歴から、今日のTrack / Format / Level / 狙う弱点を決めて
      TODAY.md に書く（問題文は作らない）。05:40 に予備実行
  ↓
07:00 Projectの定期タスク：TODAY.md を読んで Drill 8問を出し、そのまま待つ
  ↓
自分：iPhoneで Projects → 試験官 → 最新チャット を開き、8問にまとめて答える
  ↓
Claude：正答率と、間違えた問題の正解を返す → 続けて Design 15分問題を出す
  ↓
自分：15分で解いて、同じ会話に回答を書く
  ↓
Claude：必要ならヒント（答えは出さない）→ 30秒サマリ → 詳細レビュー → 採点確定
      → 記録ブロックを出力 → コネクタで投函口へ投稿
  ↓
GitHub Actions：記録をコミットし、弱点を開閉し、TODAY.md を翌日用に更新して結果を返す
```

Claude側は**1本の会話で完結**します。出題・採点・投稿まで、開くのは1つの画面だけです。

試験官は **Claude.ai の Pro** です。Claude Code は使いません。Anthropic APIも使いません。
詳細は[Automation](10-automation/README.md)。

Repositoryは記録の正本、Claudeは出題・レビューを担当するパートナーです。

### Q. 出題される問題はどんなもの？

1日完結で合計20分。**Drill 8問（30秒×8＝4分）→ Design 1問（15分）** の二層です。長期プロジェクト型は扱いません。

**Drill**（知識の床。単答・選択肢なし。記録はカテゴリ別正答率のみ）

| カテゴリ | 問数 | 題材 |
|---|---|---|
| AI | 3 | [ROADMAP.md](ROADMAP.md) の現フェーズ（いまは生成AIパスポート範囲） |
| コーディング言語 | 3 | Go 35% / Next.js 35% / Python 20% / Terraform 10% |
| ネットワーク | 2 | 『ネットワークはなぜつながるのか』の読了章まで |

**Design**（判断力。5軸100点で採点し、弱点を Weakness Log に登録）— 4 Track を25%ずつ

| Track | 例 |
|---|---|
| DB / Table Design | 「予約システムのダブルブッキングを防ぐテーブル設計とロック戦略を書け」 |
| Layered Architecture | 「このユースケースをレイヤードアーキテクチャで分割し、依存方向を図示せよ」 |
| Web / API / HTTP | 「決済APIを冪等にする設計と、リトライ時の挙動を定義せよ」 |
| Code Review | 「このPRの問題点を、責務・命名・境界の順に指摘せよ」 |

Design は次の4形式をローテーションします。

- **Design:** 要件からスキーマ・構成・インターフェースを設計する
- **Review:** 与えられた設計やコードの問題点を指摘し、修正案を出す
- **Debug:** 症状から原因を切り分け、確認手順を組む
- **Explain:** 実務で説明できるレベルで根拠を言語化する

### Q. 15分で終わらなかったらどうする？

その日のうちに完結させます。未完成でも「どこまで考えたか」「何が分からなかったか」を回答として提出します。中断点そのものが[Weakness Log](05-failures/weakness-log.md)の材料になります。

翌日へ持ち越しません。持ち越すのは弱点だけです。

### Q. スマホで15分DDLを書くのは無理では？

そのため、曜日で出題形式が変わります。`keyboard_days`（既定: 月・水・金）はDesign / Reviewが出て、それ以外の日は散文と箇条書きで答えられるExplain / Debug / Reviewが出ます。移動中の朝に長いSQLを書かされることはありません。

### Q. 週5がきついときは？

`eos.config.json` の `session_days` を `["Mon","Wed","Fri"]` に変えるだけです。記録が飛び飛びになるより、週3を確実に埋めたほうがスコアの信頼性もBankの質も上がります。

### Q. Claudeは何をレビューする？

| 観点 | 内容 |
|---|---|
| Correctness | 正誤。事実として誤っている箇所 |
| Strengths | 良かった点。どの判断が実務的に妥当だったか |
| Gaps | 間違い・不足。抜けている考慮点 |
| In practice | 実務ならどう考えるか。現場の制約を入れた判断 |
| Score | 理解度・点数（100点満点、5軸） |
| Review points | 復習すべきポイント。次にいつ再テストするか |

点数は励ましのためではなく、翌日以降の出題を選ぶための入力です。甘くつけません。レビューで一度確定した点数を、GitHubへ記録するときに付け直しません。

ヒントを使っても評価基準は変えません。ヒントで補えた重要な観点は、最終回答として正しくても弱点として残し、次回再テストできるようにします。

採点は[`07-scorecard/anchors.md`](07-scorecard/anchors.md)の見本（50点 / 70点 / 85点）を基準に行われます。LLMの採点基準は数週間でドリフトするため、固定した見本を毎回参照させて、月をまたいでも点数の意味を一定に保ちます。

朝は**30秒サマリだけ**読めば十分です。スコアと、いちばん重い抜け3件と、再テストの合否が出ます。詳細レビューと参考解答は記録に残るので、夜に読み返してください。

### Q. 記録は何が残る？

`04-sessions/daily/YYYY/YYYY-MM-DD.md` に1日1ファイル。

- 問題
- 自分の回答（原文のまま）
- 試験官のレビュー
- 点数
- 弱点
- 学んだこと

加えて、弱点は[Weakness Log](05-failures/weakness-log.md)、点数は[Scorecard](07-scorecard/README.md)、Bank昇格候補は[Promotion Queue](03-banks/promotion-queue.md)へ自動で積まれます。今の状態は[STATUS.md](STATUS.md)で一覧できます。

### Q. 弱点はどうやって閉じるの？

出題側が再テスト期限の来た弱点のTrackを優先的に出し、その日の問題に「狙う弱点」として埋め込みます。試験官は**その弱点の合否を必ず判定します**。合格すればClosedへ移動し、不合格なら優先度が1段上がって3日後に再テストされます。

同じ弱点が再発した場合、新しいIDでは登録されません。既存の項目の優先度が上がるだけなので、ログが同じ内容で膨らみません。

### Q. GitHubへの保存はどうやる？

採点が終わると、試験官が **記録ブロック** を出し、MCP コネクタ（`eos_post_record`）でそのまま Issue #1「📥 記録の投函口」へ投稿します。**新しいIssueは作りません。**

- **読み取り:** `eos_today` で `TODAY.md` を読む（落ちたら raw URL → jsDelivr → おまかせ出題）
- **書き込み:** `eos_post_record` で投函口へコメントし、Workflowがパースしてコミットする

コネクタの設定は [connector.md](10-automation/connector.md)。**これを繋がないと iPhone では回りません。**
繋がっていない環境では、記録ブロックを自分で貼ります（30秒）。

貼ったあとは全部自動です。セッション記録の作成、弱点の開閉、スコアの追記、`CONTEXT.md` の更新、結果の返信まで1〜2分で終わります。

フォーマットが崩れていても記録は失われません。パースできなかった原文は `04-sessions/inbox/` に残り、その旨がコメントで返ります。貼ったコメントを**編集**すれば再実行されます。

手貼りの予備は[inbox.md](10-automation/inbox.md)。
構成手順は[Automation](10-automation/README.md)、チェックリストは[setup-checklist.md](10-automation/setup-checklist.md)にあります。

### Q. 自分とClaudeの役割分担は？

| You | Claude |
|---|---|
| Drill 8問に4分で答える | 毎朝07:00に Drill 8問を出しておく |
| 15分、自分の頭で設計を書く | 弱点に合った Design 問題を出す |
| 分からない箇所を隠さず提出する | 正誤・不足・実務観点でレビューする |
| 実務で試す機会を作る | 見本基準で採点し、再テストの合否を判定する |
| 週1回、Bank昇格候補を書き写す（3分） | 記録ブロックを投函口へ投稿する |
| 週1回20分、実機で確認する | Weekly Reviewの講評を書いて投稿する |
| 機密情報を除いて共有する | — |

手動で残るのは2つです。**20分解いて答えを書く / 週1回Bank昇格を書き写す。** Bankへの書き込みを自動化していないのは、自動で流し込むとBankが使われない要約の山になるからです。

Claudeに設計判断そのものを任せるのではなく、**自分の設計を評価し記録に変える作業**を任せます。

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
| [`02-tracks`](02-tracks/README.md) | Design 4 Track の到達設計と、Drill の題材一覧 |
| [`03-banks`](03-banks/README.md) | Pattern / Pitfall / Tradeoff / Termの再利用資産 |
| [`04-sessions`](04-sessions/README.md) | 日次セッションの問題と記録 |
| [`05-failures`](05-failures/README.md) | 解けなかった・説明できなかった点の改善 |
| [`06-reviews`](06-reviews/README.md) | Weekly / Monthly Review |
| [`07-scorecard`](07-scorecard/README.md) | 能力と点数の推移 |
| [`08-operating-rules`](08-operating-rules/README.md) | 継続運用、命名、更新ルール |
| [`09-foundation`](09-foundation/README.md) | 基礎の穴埋めと再テスト |
| [`10-automation`](10-automation/README.md) | 通知・出題・保存の自動化構成 |
| [`TODAY.md`](TODAY.md) | 自動生成。**試験官が毎朝読む唯一の入り口**（約30行）。今日の割り当てだけ |
| [`CONTEXT.md`](CONTEXT.md) | 自動生成。TODAY.md の全量版。弱点一覧・履歴・Level/Formatの定義まで含む |
| [`STATUS.md`](STATUS.md) | 自動生成。連続実施・平均点・期限切れの弱点 |
| [`prompts/`](prompts/record-block.md) | Claudeに貼る文（Project指示 / 定期タスク / 記録ブロックの雛形） |

## Definition of success

成功は「用語を知っていること」ではありません。

- 要件から15分でスキーマと構成を書き、根拠を説明できる
- 他人の設計をレビューし、リスクを言語化できる
- 障害の切り分けを上位レイヤーから順に進められる
- 同じ弱点を2回目で閉じられる
- 実務のレビューで自分の設計案が通る
