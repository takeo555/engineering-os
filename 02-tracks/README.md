# Tracks

6つのTrackを持つ。出題比率は`eos.config.json`の `track_weights` と、今月の `horizon_tracks` で決まる。
毎週6本全部は出さない。今月の出口がある Track を厚くする。

| Track | File | Default weight | Primary skills |
|---|---|---|---|
| DB / Table Design | [db-design.md](db-design.md) | 10% | Data Modeling, Consistency Design |
| Layered Architecture | [architecture.md](architecture.md) | 35% | Layering, Trade-off Articulation |
| Web / API / HTTP | [web-api.md](web-api.md) | 7% | Interface Design, Requirement Reading |
| Network / Infra | [network-infra.md](network-infra.md) | 5% | Failure Analysis, Performance Reasoning |
| Coding / Go / Next.js | [coding.md](coding.md) | 35% | Layering, Interface Design |
| AI / LLM | [ai.md](ai.md) | 0% | Requirement Reading, Trade-off Articulation |

Default weight は 2026-09 の Horizon に合わせた値。AI は10月の生成AIパスポートまで日次に出さない（weight 0）。月次レビューで書き換える。

## Rotation rules

- 同じTrackを3日連続で出さない
- Weakness Logに未クローズの高優先項目があるTrackを優先する
- 平均スコアが最も低いTrackの比重を翌週+10%する
- 木曜以降は、`horizon_tracks` のうちその週まだ出ていないものを補完する
- 6Track全てを1週間で出す必要はない
