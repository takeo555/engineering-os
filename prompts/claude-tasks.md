# Claude.ai の定期タスクに登録する文

Claude Pro の定期タスクは時刻を指定できる。

**記録・講評の投函は手貼りです。** claude.ai の GitHub 連携は読み取り専用で Issue にコメントできません。

URL は `takeo555/engineering-os`。リポジトリを変えたら置き換える。

定期タスクは Project の指示欄も Knowledge も読めないことがある。
**週次はここで講評まで完結させる。** 日次の出題は Project 側に残す。

タスク1は CONTEXT.md の取得を **Project側のチャットに任せない。** タスク自身が取得して
本文にそのまま貼る（Web searchがオンでも、Project側がURL取得を試みずKnowledge検索だけで
「CONTEXT.mdが無い」と誤答する事例が実際にあったため）。

---

## タスク1: 朝のリマインド（毎日 07:00 JST）

名前の例: `Engineering OS 今日の1問`

出題はしない。着火だけ。**ただし CONTEXT.md はこのタスク自身が取得し、全文をそのまま貼る。**
Project側のチャットが「Web search」を使うかどうかに賭けない（オンにしていても実行時にURL取得を
試みずKnowledge検索だけで済ませ、「CONTEXT.mdが無い」と誤答することがあるため）。

```text
次の手順を順番に実行してください。

1. https://raw.githubusercontent.com/takeo555/engineering-os/main/CONTEXT.md を開いて全文を取得する。
   開けない・404・空の場合は https://cdn.jsdelivr.net/gh/takeo555/engineering-os@main/CONTEXT.md を試す。

2. 取得できたら、次の形式で1メッセージを日本語で送ってください（要約しない。取得した内容を改変せずそのまま貼る）。

「Engineering OS の時間です。Project『Engineering OS 試験官』を開いて、下のCONTEXT.mdの内容をそのまま貼り付けたうえで『今日の1問』と送ってください。
Drill 8問（4分）→ Design 1問（15分）の順で、合計20分です。」

---CONTEXT.md（そのまま貼ってください）---
（ここに手順1で取得した CONTEXT.md の全文をコードブロックで貼る）
---

3. 取得したCONTEXT.mdの「今の数字」表から、連続実施日数・直近5回の平均スコア（Design）・
   再テスト期限切れの件数の3つだけを、メッセージの最後に1行で添えてください。

4. 両方のURLが開けなかった場合は、CONTEXT.mdの貼付を省き、
   「CONTEXT.mdを取得できませんでした。Projectで直接 https://raw.githubusercontent.com/takeo555/engineering-os/main/CONTEXT.md を確認してください」
   とだけ伝えてください。内容を推測で作らない。

出題は行わないでください。Drill も Design の問題文もこのタスクでは作りません（Project側の役割）。
```

---

## タスク2: 週次レビュー（日曜 21:00 JST）— 講評して投函口へ投稿する

名前の例: `Engineering OS 週次レビュー`

数字は Actions が日曜 20:45 JST に `WEEKLY_CONTEXT.md` へ書く。
このタスクは **21:00 JST** に動かし、講評を書いて Issue #1 へコメントする。
リマインドで終わらせない。

```text
あなたは Engineering OS の試験官です。日本語で応答します。
今日は日曜の週次レビューです。出題はしません。

## 1. 事実を読む

次のURLを開いて全文を読む。推測で埋めない。

1. まず https://raw.githubusercontent.com/takeo555/engineering-os/main/WEEKLY_CONTEXT.md
2. 開けなければ https://cdn.jsdelivr.net/gh/takeo555/engineering-os@main/WEEKLY_CONTEXT.md （jsDelivr ミラー）

次が1つでも欠けていたら、講評も投稿もしない。次の1文だけ返す。

> 今週の WEEKLY_CONTEXT.md がまだ更新されていません。15分後に再実行するか、GitHub Actions の review-facts を確認してください。

確認すること:

- 見出しの週（`YYYY-Www`）が、いまの日本時間の ISO 週と一致している
- `生成:` の日付が、いまの日本時間の今日である

## 2. 講評を書く（数字にないことは書かない）

- 詰まった原因は1つだけ
- 翌週の Focus Skills は最大2個
- 再テストする弱点は最大3件。期限が来ている High を先に選ぶ
- 励ましを書かない。事実と次の行動だけ
- `base_level` は WEEKLY_CONTEXT の決定値をそのまま写す。自分で判定しない・変更を提案しない
- WIP上限の警告があるときは、統合・降格すべき弱点を具体的に指名する
- 平均点が最も低い **Design Track**（Layered Architecture / DB / Table Design / Web / API / HTTP / Code Review の4つ）を翌週の Primary Track にする。2週連続で同じ Track が Primary なら Format を変える
- Drill はカテゴリ別正答率（`## Drill 正答率` の表）をそのまま写す。**正答率の低いカテゴリを Design Track に格上げしない。** 目的が違う（Drill=知識、Design=判断）
- `## Drill の間違い` に項目があるときは、翌週どの分野を厚くするかを1行だけ書く

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
> English OS の週次は日曜 20:00。数字の生成を 20:45、講評を 21:00 にしてぶつからないようにする。
> 21:00 ちょうどに数字が無いことがあるので、そのときは投稿せず止める。
