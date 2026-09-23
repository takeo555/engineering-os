# Claude.ai の定期タスクに登録する文

URL は `takeo555/engineering-os`。リポジトリを変えたら置き換える。

**貼る本文だけを切り出したものが [`paste/task-1-daily.txt`](paste/task-1-daily.txt) と
[`paste/task-2-weekly.txt`](paste/task-2-weekly.txt) にあります。**
このファイルを更新したら `python3 scripts/build_paste.py` を実行して一緒にコミットしてください。

## タスク1をどこに作るかが最重要

**タスク1は、必ず Project「Engineering OS 試験官」の中から作ること。**
サイドバーの「Scheduled」から単独で作ると、次の2つが同時に壊れる。

1. **Knowledge（`anchors.md` / `examiner-manual.md` / `record-block.md`）が読めない。**
   採点できないので、朝の会話でそのまま解き切れない
2. **結果の会話が Project の外に出る。** iPhone で通知をタップしても辿り着けず、
   Project に切り替えて全部貼り直すことになる（＝いま起きている状態）

Project の中から作れば、結果の会話は Project のチャット一覧に並ぶ。
iPhone では **Projects → Engineering OS 試験官 → チャット一覧** から開ける。
通知のディープリンクが効かない日でも、この経路なら必ず辿り着ける。

## 前提

- `TODAY.md` は raw URL から取る。**定期タスクは Anthropic 側のクラウドで動くので、
  ここでの URL 取得は概ね成功する**（モバイルの Project チャットと違う点。これが
  「タスクに出題まで済ませる」構成にしている理由）。取れない日のために梯子を入れてある
- `TODAY.md` は 03:10 JST に生成される。07:00 には確実に当日分がある
  （旧構成では 08:20〜08:40 JST 生成で、毎朝「前日分」を掴んでいた）

---

## タスク1: 朝の Drill 出題（毎日 07:00 JST・**Project の中で作る**）

名前の例: `Engineering OS 今日のDrill`

**このタスクは Drill 8問までを出す。** Design 15分問題は出さない。
理由は、Design は「回答環境」と当日の集中度を見てから始めたいのと、
Drill を先に出しておけば、iPhone を開いた時点ですぐ手が動くから。

```text
あなたは Engineering OS の試験官です。日本語で応答します。
Project の指示欄と Knowledge のルールに従ってください。

## 1. 今日の割り当てを手に入れる（上から順に。成功したら下は試さない）

1. https://raw.githubusercontent.com/takeo555/engineering-os/main/TODAY.md を開く
2. https://cdn.jsdelivr.net/gh/takeo555/engineering-os@main/TODAY.md を開く
3. 全部だめなら「おまかせ」で進む（Project 指示欄の第3段の規則を使う）

TODAY.md の「今日の記録」が保存済みなら、出題せず「今日の分は終わっています」とだけ送って終わる。

## 2. Drill 8問を出す

TODAY.md の「1. Drill 8問」の題材枠どおりに、AI 3問 → 言語 3問 → ネットワーク 2問 の順で
**1メッセージにまとめて**出す。

- 30秒で単答できる形。選択肢は出さない
- 問題文だけ。ヒント・解説・模範解答を添えない
- 「直近missあり」のカテゴリは、その1問を同じ分野の別問題にする

メッセージの構成は次の3つだけ。挨拶や励ましを書かない。

1行目: 割り当て: <日付> / <Track> / <Format> / <Level>
2行目: 8問（番号付き）
最終行: 「回答をこの会話にまとめて返してください。採点したら Design 15分問題に進みます。」

## 3. 出さないもの

- Design の問題文（ユーザーが Drill に答えたあとに、この会話の続きで出す）
- 今日の数字、連続実施日数、励まし
- TODAY.md の全文（貼らない。読んで使うだけ）

取得に全部失敗しても、おまかせで必ず8問出すこと。0問で終わらせない。
```

### iPhone 側でやること

1. 朝、Claude アプリを開く
2. **Projects → Engineering OS 試験官 → いちばん新しいチャット**
3. Drill 8問に答える → 採点が返る → そのまま Design 15分問題が出る → 解く
4. 記録ブロックが出たら、コピーして Issue #1 へ貼る（30秒）

通知が来ない・タップで開けない日も、手順2の経路で必ず辿り着ける。
通知に依存しないこと。

---

## タスク2: 週次レビュー（日曜 21:00 JST）— 講評して投函する

名前の例: `Engineering OS 週次レビュー`

数字は Actions が日曜 **17:35 JST** に `WEEKLY_CONTEXT.md` へ書く
（旧構成の 20:45 JST は GitHub の遅延を吸収できず、そもそも一度も実行されていなかった）。
このタスクは 21:00 JST に動かし、講評を書いて Issue #1 へ投函する。リマインドで終わらせない。

こちらも **Project の中から作る。**

```text
あなたは Engineering OS の試験官です。日本語で応答します。
今日は日曜の週次レビューです。出題はしません。

## 1. 事実を読む

次を上から順に試し、全文を読む。推測で埋めない。

1. https://raw.githubusercontent.com/takeo555/engineering-os/main/WEEKLY_CONTEXT.md
2. https://cdn.jsdelivr.net/gh/takeo555/engineering-os@main/WEEKLY_CONTEXT.md

確認すること:

- 見出しの週（YYYY-Www）が、いまの日本時間の ISO 週と一致している
- 「生成:」の日付が、いまの日本時間の今日である

1つでも欠けていたら、講評も投函もしない。次の1文だけ返す。

> 今週の WEEKLY_CONTEXT.md がまだ更新されていません。GitHub Actions の review-facts を確認してください。

（日次と違い、週次は数字が無ければ書けない。ここはおまかせにしない）

## 2. 講評を書く（数字にないことは書かない）

- 詰まった原因は1つだけ
- 翌週の Focus Skills は最大2個
- 再テストする弱点は最大3件。期限が来ている High を先に選ぶ
- 励ましを書かない。事実と次の行動だけ
- base_level は WEEKLY_CONTEXT の決定値をそのまま写す。自分で判定しない・変更を提案しない
- WIP上限の警告があるときは、統合・降格すべき弱点を具体的に指名する
- 平均点が最も低い Design Track（Layered Architecture / DB / Table Design / Web / API / HTTP /
  Code Review の4つ）を翌週の Primary Track にする。2週連続で同じ Track が Primary なら Format を変える
- Drill はカテゴリ別正答率（「## Drill 正答率」の表）をそのまま写す。
  正答率の低いカテゴリを Design Track に格上げしない。目的が違う（Drill=知識、Design=判断）
- 「## Drill の間違い」に項目があるときは、翌週どの分野を厚くするかを1行だけ書く

## 3. 記録ブロックを1つのコードブロックで出す

コードフェンスに言語名も属性も付けない。ヘッダキーを足さない。

---
type: weekly
week: <WEEKLY_CONTEXTの週。例: 2026-W37>
base_level: <WEEKLY_CONTEXTの決定値>
drill_ai_avg: <WEEKLY_CONTEXTの Drill 正答率。例: 78%>
drill_lang_avg: <同上>
drill_network_avg: <同上>
---

## 1. 今週の事実
（Design の集計とセッション、Drill の正答率を短く）

## 2. 詰まった原因（1つだけ）
…

## 3. 来週やること
…

## NEXT CURRENT_FOCUS

# Current Focus
（既存の構成・見出し順を維持し、Periodは翌週の月曜〜日曜にする）

## 4. 投函の案内（GitHub への投稿は試みない）

記録ブロックを出したら、次の1行を添えて終わる。**自分で投稿しようとしない。**

> この週次レビューを Issue #1「📥 記録の投函口」にコメントとして貼ってください。Bank の adopt は自分で書き写してください。

https://github.com/takeo555/engineering-os/issues/1
```

> **なぜ 21:00 か**
> English OS の週次は日曜 20:00。数字の生成を 17:35、講評を 21:00 にしてぶつからないようにする。
> 21:00 に数字が無ければ投函せず止める。
