# コネクタ（これが iPhone で回すための要）

**日次が7日連続で止まった直接の原因はここです。** 2026-09-11 を最後に記録が保存されていません。
GitHub 側（`build-context`）は毎日成功していたので、壊れていたのは Claude 側の入口と出口だけでした。

| | 経路 | モバイルでの実際 |
|---|---|---|
| 入口（読む） | 試験官が raw URL を fetch する | **動かない。** Knowledge検索に落ちて「CONTEXT.mdが無い」と誤答する |
| 出口（書く） | 記録ブロックを手で Issue #1 に貼る | iPhoneで長いコードブロックをコピー＆アプリ切替。毎日は続かない |

指示文を強く書いても直りません。**指示欄（システム側）に書かれただけのURLは取りに行かない**という
挙動が相手なので、「取りに行け」と強調する対処は同じ壁に当たり続けます。実際、
jsDelivrミラー追加・「必ずURLを開け」の明記という2回の修正がどちらも効きませんでした。

MCP コネクタを繋ぐと、この2つが**同時に**消えます。コネクタは接続した時点で
**Web・デスクトップ・モバイルの全部で使えます**（片方だけ設定する必要はありません）。

---

## 結論: 自前の最小MCPサーバを立てる

[`mcp/`](mcp/) にコードがあります。**デプロイ15分**。手順は [`mcp/README.md`](mcp/README.md)。

| ツール | 動作 |
|---|---|
| `eos_today` | `TODAY.md` を返す |
| `eos_weekly_context` | `WEEKLY_CONTEXT.md` を返す |
| `eos_post_record` | 記録ブロックを Issue #1 のコメントとして投函する |

- Cloudflare Workers の無料枠。1日数十リクエストなので費用はかかりません
- GitHub の fine-grained PAT は **Worker の secret** に置きます。iPhone にも Claude にも渡りません
- PAT の権限は `takeo555/engineering-os` の **Issues 読み書き ＋ Contents 読み取り**だけ
- ツールが3つしかないので、試験官が朝からコード検索へ寄り道しません

### なぜ GitHub 公式のリモートMCPではないのか

2026-09-14 の [decision-log](../08-operating-rules/decision-log.md) で一度調べ、
実運用で失敗していました。2026-09-18 に再確認しても状況は変わっていません。

GitHub 公式リポジトリの導入ガイドが、Claude について明記しています。

> the GitHub remote MCP server requires OAuth authentication through a registered GitHub App
> (or OAuth App), which is not currently supported

（`github/github-mcp-server` の `docs/installation-guides/install-claude.md`）

claude.ai のカスタムコネクタは自前 OAuth App の Client ID / Secret を入れられるので
「絶対に無理」とまでは言えませんが、**すでに一度失敗している経路に朝の運用を賭けない**方がよいです。
すぐ試したい場合は下の10分テストをどうぞ。だめでも自前サーバ側の作業は無駄になりません。

<details>
<summary>10分テスト（任意）: GitHub 公式リモートMCPを試す</summary>

1. 設定 → コネクタ → カスタムコネクタを追加
2. URL に `https://api.githubcopilot.com/mcp/x/repos/readonly`
3. 接続 → GitHub の認可画面が出るか

認可画面が出ずに失敗したら、そこで打ち切って自前サーバへ進んでください。
（Copilot 契約は不要です。GitHub MCP サーバ自体は全ユーザーが使えます。
問題は契約ではなく OAuth の対応可否です）

</details>

---

## 繋がったあとに変わること

| | 前 | 後 |
|---|---|---|
| 朝の開始 | CONTEXT.md を手で貼る／取得失敗で0問 | iPhoneで「今日の1問」と打つだけ |
| 投函 | 記録ブロックをコピーしてIssueへ貼る | 試験官がそのまま投稿する |
| 手で残る作業 | 3つ | **1つ（解いて答えを書く）** |

コネクタが無い環境（別端末、Worker障害）でも止まらないよう、
`project-instructions.md` は **コネクタ → URL → 貼付依頼 → おまかせ出題** の4段構えにしてあります。
コネクタは**最速の経路**であって、唯一の経路ではありません。

## 関連

- デプロイ手順: [mcp/README.md](mcp/README.md)
- 全体構成: [README.md](README.md)
- チェックリスト: [setup-checklist.md](setup-checklist.md)
- 手貼りの手順（コネクタが落ちた日の予備）: [inbox.md](inbox.md)
