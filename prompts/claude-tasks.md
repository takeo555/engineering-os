# Claude.ai の定期タスクに登録する文

URL は `takeo555/engineering-os`。リポジトリを変えたら置き換える。

**貼る本文だけを切り出したものが [`paste/task-1-daily.txt`](paste/task-1-daily.txt) と
[`paste/task-2-weekly.txt`](paste/task-2-weekly.txt) にあります。**
このファイルを更新したら `python3 scripts/build_paste.py` を実行して一緒にコミットしてください。

## タスク1は「通知だけ」。出題させない

**2026-09-28 の実測でこうなった。**

| | 結果 |
|---|---|
| タスクの会話（Project内） | デスクトップでは見える。**iPhone のアプリには出ない** |
| タスクの通知 | **iPhone に届く** |
| Project で「今日の1問」 | **iPhone で動く** |

タスクに出題させると、その8問は iPhone から見えない会話の中に埋まる。
ユーザーは別の会話で「今日の1問」と打つので、**同じ日に2つのセッションができる。**

だから **タスクは着火だけ。出題は Project の会話に一本化する。**
動くことが確認できた経路（通知＋「今日の1問」）だけで組む。

## 前提

- タスクは **Project の中から作る**（会話が Project に属し、Knowledge も効く）。
  サイドバーに「Scheduled」が見つからない場合は、**Project の会話で普通に頼めばよい**。
  「毎朝7時にこれを実行するタスクを作って」と言い、下の本文を貼る
- `TODAY.md` は 00:50 JST に生成される（予備 05:40）。07:00 には当日分がある

---

## タスク1: 朝のリマインド（毎日 07:00 JST・**Project の中で作る**）

名前の例: `Engineering OS 今日の1問`

**出題しない。** 通知を出して、今日の割り当てを1行で伝えるだけ。

```text
次の手順を実行してください。出題は行いません。

1. https://raw.githubusercontent.com/takeo555/engineering-os/main/TODAY.md を開いて読む。
   開けなければ https://cdn.jsdelivr.net/gh/takeo555/engineering-os@main/TODAY.md を試す。

2. 次の3行だけを送る。挨拶も励ましも数字も足さない。

Engineering OS の時間です。Project「Engineering OS 試験官」で「今日の1問」と送ってください。
今日: <TODAY.md の日付> / <Track> / <Format> / <Level>（<回答環境>）
Drill 8問（4分）→ Design 1問（15分）の順、合計20分です。

3. どちらのURLも開けなかった場合は、2行目を省いて次だけ送る。

Engineering OS の時間です。Project「Engineering OS 試験官」で「今日の1問」と送ってください。

Drill も Design も、問題文はこのタスクでは作りません。TODAY.md の全文も貼りません。
「今日の記録」が保存済みでも、上のリマインドはそのまま送ってください（記録の修正に使うため）。
```

### iPhone 側でやること

1. 7時の通知を見る（通知が来なくても構わない。下の経路で必ず始められる）
2. Claude アプリ → **Projects → Engineering OS 試験官**
3. **「今日の1問」と送る** ← ここが本体
4. Drill 8問 → Design 1問 → 記録ブロック
5. 記録ブロックをコピーして Issue #1 へ貼る（30秒）

**タスクが作った会話は iPhone には出ません。探さないでください。** 手順3で新しく始めるのが正しい使い方です。

念のため、iPhone の「リマインダー」か「アラーム」を毎朝7:00に設定しておくと、
Claude 側の通知がどうなっても朝が始まります。

---

## タスク2: 週次レビュー（日曜 21:00 JST）— 講評して投函する

名前の例: `Engineering OS 週次レビュー`

数字は Actions が日曜 **11:35 JST** に `WEEKLY_CONTEXT.md` へ書く
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
> English OS の週次は日曜 20:00。数字の生成を 11:35、講評を 21:00 にしてぶつからないようにする。
> 21:00 に数字が無ければ投函せず止める。
