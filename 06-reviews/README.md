# Reviews

| Cadence | When | Who runs it | Output |
|---|---|---|---|
| Weekly | 日曜 20:45 数字 / 21:00 講評 | `review-facts.yml` + Claude定期タスク | `weekly/YYYY-Www.md`、`CURRENT_FOCUS.md`、`base_level` |
| Monthly | 毎月1日 21:00 JST | `review-facts.yml` | `MONTHLY_CONTEXT.md`（講評は別） |

日曜21:00に講評するのは、English OSの週次（日曜20:00 JST）と重ならないようにするためです。
数字は20:45に出し、21:00の試験官が今週分を読めるようにします。講評は Issue #1 へ自動投稿します。

## Weekly Review

- 直近1週間のSessionとスコアを確認
- Track別の平均点と、最も低いTrackを特定
- Closeできた弱点と、再テストで再び落ちた弱点を整理
- 実際に使えたBank資産を確認
- 翌週のPrimary Trackを決定
- Focus Skillsを最大2つに限定
- `CURRENT_FOCUS.md`を翌週向けに更新

Sessionが3回未満の週は、原因（時間・難易度・通知）を1つだけ特定し、翌週は**難易度を1段下げて5回**に戻すことを目標にします。埋め合わせの補講はしません。

## Monthly Review

- Track別の到達度と、L2→L3へ進めるTrackの判定
- Sessions実施率、平均スコア、30分内完了率
- 頻出弱点と、Activeになった資産
- Core SkillsのScorecard更新
- 続けること / やめること / 始めること
- 翌月のPrimary Outcome（= 翌月の Current horizon）、Track比率、Focus Skills
- `00-north-star/README.md` の Current horizon を翌月分に書き換える

Scorecardは**出題の証拠がある項目だけ**更新します。記録のない能力を推測で採点しません。

軸別平均（Correctness / Completeness / Reasoning / Practicality / Clarity）のうち最も低いものが、弱点の構造を示します。Reasoningが低い場合は「答えは合うが根拠が言えない」状態で、実務で最も効く欠陥として扱います。

## Templates

- [weekly-review.md](templates/weekly-review.md)
- [monthly-review.md](templates/monthly-review.md)
