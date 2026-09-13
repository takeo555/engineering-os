# Category: Network（Drill専用）

## Role in Engineering OS

**Drill専用カテゴリ。Design 15分では出題しない。**

ネットワークは「繋がらない」「遅い」を上位レイヤーから切り分ける力の基礎として、まず知識の床を作る。設計問題は将来検討。

## Daily quota

- 毎日 **2問**、30秒・単答
- 記録は正答率のみ（例: `drill_network: 2/2`）
- 間違えた分野は `05-failures/drill-misses.md` に追記され、翌日類題を混ぜる

## Phase 1 の教材

**『ネットワークはなぜつながるのか』（戸根勤・日経BP）** の読了章まで。

進捗管理：
- 読了章を `CURRENT_FOCUS.md` の "Concepts to activate" に記載
- 未読の章の内容は出題しない
- 読了章が増えたら Weekly Review で範囲を広げる

## 題材の例（章別）

| 章 | 例題 |
|---|---|
| 1章 Webブラウザがメッセージを作る | 「HTTPリクエストのメソッドで冪等でないものを1つ」 |
| 2章 プロトコル・スタック | 「TCPの3-way handshakeの3回目のパケットが持つフラグは」 |
| 3章 LAN内 | 「ARPが解決するのは何と何の対応か」 |
| 4章 ルーティング | 「デフォルトゲートウェイの役割を一言で」 |
| 5章 サーバ側 | 「Well-knownポートで443番の用途は」 |
| 6章 Webサーバ処理 | 「Nginxのworker_processesが1未満に設定できない理由を一言で」 |

## Phase 2以降

- 本読了後、公式ドキュメント（MDN HTTP、AWS/GCP ネットワーク docs、RFCサマリ等）を段階的に追加
- 追加教材の選定は Weekly Review で判断（月次レビューで確定）

## Miss handling

- ドリルで間違えた問題は `drill-misses.md` に「日付・Network・分野・問題テーマ」で記録
- 翌日のネットワークドリル2問のうち1問を、同じ分野の別問題に置き換える
- W番号は振らない

## Design側には出さない

障害切り分けや構成レビューは、将来 Code Review Track で扱う可能性がある。**Phase 1〜3では Design 出題しない。**
