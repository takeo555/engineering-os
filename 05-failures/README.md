# Weaknesses

解けなかった・説明できなかった点を、次の出題と再テスト予定へ変える場所です。

正本は[weakness-log.md](weakness-log.md)。日次セッションのレビューから自動で追記・移動されます。

## Lifecycle（自動で動きます）

```text
Open（レビューで検出）
  ↓ 出題側が retest_on の期限を見て、そのTrackを優先出題
再テスト出題
  ↓ 試験官Projectが合否を判定（記録ブロックの `retest:` に必ず書く）
passed → Closed へ移動
failed → priority +1、3日後に再テスト
```

- **合否判定は試験官Projectの必須動作です。** CONTEXT.mdの「今日狙う弱点」に挙がった項目は、その日必ず `passed` / `failed` のどちらかが記録されます。これを飛ばすと弱点が永久にOpenのまま溜まります
- 同じ弱点が再発した場合、**新しいIDでは登録されません。** 既存の弱点と内容が近ければ優先度が1段上がり、再テストが前倒しになります（類似判定のしきい値は `eos.config.json` の `weakness.dedup_similarity`）
- 優先度が `High` に達してなお不合格が続く項目は、[Foundation](../09-foundation/README.md)へ移し、実機で確認します
- Closedは30日後に一度だけ抜き打ちで再テストします

## WIP limits

- Open High: 最大5件
- Open 合計: 最大15件

上限を超えると保存時に警告が出て、`STATUS.md` にも表示されます。新規登録の前にPriorityを見直して降格または統合してください。

## 手で触ってよいもの

- `weakness` の文言を分かりやすく直す
- 重複していると自分で気づいた項目を統合する
- Priorityを下げる

## 手で触らないもの

- Open / Closed テーブルの行順（自動処理が行位置を前提にしています）
- ID（採番は追記専用。欠番が出ても振り直さない）
