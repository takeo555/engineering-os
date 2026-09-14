# Tracks

Engineering OS は **Drill 3カテゴリ** と **Design 4Track** を持つ。両者は別モードであり、記録・採点・弱点管理も分離されている。

## Drill categories（30秒・単答・カテゴリ別正答率のみ記録）

| Category | File | 1日の出題数 | 内容 |
|---|---|---|---|
| AI | [ai.md](ai.md) | 3問 | 現フェーズの AI 資格範囲 |
| Coding Language | [coding-language.md](coding-language.md) | 3問 | Go 35% / Next.js 35% / Python 20% / Terraform 10% |
| Network | [network-infra.md](network-infra.md) | 2問 | 『ネットワークはなぜつながるのか』の読了章まで |

## Design tracks（15分・5軸100点採点・Weakness Log登録）

| Track | File | Weight | Primary skills |
|---|---|---|---|
| Layered Architecture | [architecture.md](architecture.md) | 25% | Layering, Trade-off Articulation |
| DB / Table Design | [db-design.md](db-design.md) | 25% | Data Modeling, Consistency Design |
| Web / API / HTTP | [web-api.md](web-api.md) | 25% | Interface Design, Idempotency Design |
| Code Review | [code-review.md](code-review.md) | 25% | Review Prioritization, Trade-off Articulation |

Design tracks の weight は `eos.config.json` の `design_track_weights` に定義されている。

## Rotation rules

### Drill
- カテゴリごとに毎日固定本数（AI 3・言語 3・ネットワーク 2）
- 言語ドリルは `coding_language_weights` に従ってランダムに3問選ぶ
- **直近3日のドリル間違いから、カテゴリ内で1問だけ類題を混ぜる**（`drill-misses.md` を参照）

### Design
- 同じTrackを3日連続で出さない
- 平均スコアが最も低いTrackの比重を翌週+10%する
- 木曜以降は、今週まだ出ていない Design Track を優先する

## 廃止したもの

- 旧 `Coding / Go / Next.js` Track: ファイルごと削除。役割が Coding Language ドリル と Code Review Track に分割吸収された
- 旧 `Network / Infra` の Design Track 扱い: ネットワークはドリル専用になった（Design で出題しない）
- 旧 `AI / LLM` の Design Track 扱い: 同上

過去の記録（`04-sessions/daily/`, `07-scorecard/scores.csv`）には旧Track名が残る。集計側は旧Track名を読めるままにしてあるので、過去の点数は消えない。**新しい出題では使わない。**
