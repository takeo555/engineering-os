# Pattern Bank

繰り返し使える設計の型。「いつ使うか」と「使わない条件」を必ず書きます。

| ID | Pattern | When to use | When NOT to use | Status |
|---|---|---|---|---|
| P001 | 予約テーブル + 複合一意制約（resource_id, time_slot） | 同一枠の二重予約を構造的に防ぎたい | 枠が可変長・重なり判定が必要な場合 | Active |
| P002 | 冪等キーテーブル（key, request_hash, response, expires_at） | 決済など再送が起きうるPOST | 副作用のない読み取り | Active |
| P003 | 有効期間モデル（valid_from, valid_to） | 履歴を保持しつつ現在値を引きたい | 履歴が不要な設定値 | Active |
| P004 | ポート/アダプタ（Domainがインターフェースを持つ） | ドメインが外部I/Oに依存しそうなとき | 単一実装で置換予定がない薄い処理 | Draft |

## Template

```markdown
### PXXX — <名前>

- **問題:** どんな状況で困るか
- **構造:** テーブル/クラス/インターフェースの形
- **効果:** 何が構造的に防げるか
- **代償:** 何が複雑になるか
- **使わない条件:** いつ避けるか
- **出典:** 使えたSession（YYYY-MM-DD）
```
