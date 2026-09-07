# Bank Promotion Queue

日次セッションから出た昇格候補です。Weekly Reviewで採否が判定され、レビューファイルの「Bank昇格の判定」表に結果が出ます。

**adopt になったものだけを `03-banks/` の該当ファイルへ書き写し、この表の行を削除してください。** ここに溜めたままではBankになりません。自動でBankへ書き込まないのは、Bankの質を人が守るためです。

| Date | Candidate | Target bank | Status |
|---|---|---|---|
| 2026-09-03 | 複合一意制約による枠の排他（P001） | pattern | Adopted |
| 2026-09-03 | 論理削除とUNIQUEの衝突（E001） | pitfall | Adopted |
| 2026-09-03 | 物理削除 vs 論理削除（T002） | tradeoff | Adopted |
| 2026-09-07 | HTTP固有の処理はHandlerで値に変換してUsecaseへ渡す | pattern | Pending |
| 2026-09-07 | Usecaseは具象Repositoryではなくinterfaceに依存させる | pattern | Pending |
