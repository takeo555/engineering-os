# Scorecard

## Sources

| File | Content | Updated by |
|---|---|---|
| [scores.csv](scores.csv) | 全セッションの点数（5軸 + 合計） | 日次Workflow |
| [anchors.md](anchors.md) | **採点基準の見本（50 / 70 / 85点）** | 変更しない |
| [skills.md](skills.md) | Core Skills 8項目の到達度 | 月次Workflow |

## anchors.md の役割

LLMの採点基準は数週間で自然にドリフトします。9月の68点と12月の68点が別物になると、`scores.csv` を根拠にした難易度調整とTrack比重調整が土台から崩れます。

`anchors.md` は同じ1問に対する3種類の回答（50点 / 70点 / 85点）を固定した基準です。**試験官ProjectのKnowledgeにアップロードし、毎回参照させます。** これが入っていないと、Scorecardの数字は時系列で比較できません。

見本は変えません。Levelが上がって易しすぎると感じたら、既存の3本を残して `Anchor D` を追記します。

## scores.csv の列

```text
date,track,format,level,correctness,completeness,reasoning,practicality,clarity,total,time_spent_min
```

## Reading rules

- 単日の点数は見ない。5セッション移動平均で見る
- Track別の平均が最も低いものを翌週の重点にする（出題側が自動で加点する）
- 点数が上がらないのに時間が伸びている場合は、難易度が高すぎる
- 軸別平均で最も低いものが、実際の弱点の構造を示す（Reasoningが低い場合は実務で最も効く欠陥）

## Skill levels

| Score | 意味 |
|---|---|
| 1 | 用語を知っている |
| 2 | 例を見れば真似できる |
| 3 | 要件から自分で書ける |
| 4 | 根拠を説明し、レビューを通せる |
| 5 | 他人の設計をレビューし、判断を教えられる |

推測で採点しません。証拠となるセッション日付を必ず添えます。
