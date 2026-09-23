# eos-mcp — 15分でデプロイする

claude.ai のカスタムコネクタとして登録する、**ツール3つだけ**の MCP サーバです。
これを繋ぐと iPhone の Claude から `TODAY.md` を読み、Issue #1 へ投函できるようになります。

なぜ必要かは [../connector.md](../connector.md)。

## 必要なもの

- Cloudflare アカウント（無料枠で足りる。この用途の実行回数は1日数十回）
- Node.js（`npx` が使えればよい）
- GitHub の fine-grained PAT

## 1. PAT を作る

GitHub → **Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token**

| 項目 | 値 |
|---|---|
| Repository access | **Only select repositories** → `takeo555/engineering-os` |
| Permissions → Issues | **Read and write** |
| Permissions → Contents | **Read-only** |
| Expiration | 1年（カレンダーに更新日を入れておく） |

**これ以外の権限を付けないこと。** 漏れても「このリポジトリのIssueにコメントできる」以上のことは起きません。

## 2. デプロイする（1コマンド）

リポジトリのルートで：

```bash
bash 10-automation/mcp/setup.sh
```

Cloudflare へのログイン確認 → PATの入力（画面に出ません）→ PATの有効性チェック →
secret 登録 → デプロイ → 疎通確認 まで通しで行い、最後に
**claude.ai に登録するURL**を表示します。

`MCP_PATH`（URLの末尾に付くランダム文字列）はスクリプトが生成します。控える必要はありません。

<details>
<summary>手で順にやる場合</summary>

```bash
cd 10-automation/mcp
openssl rand -hex 16                   # 控える
npx wrangler login
npx wrangler secret put GITHUB_TOKEN   # 手順1のPATを貼る
npx wrangler secret put MCP_PATH       # 上のランダム文字列を貼る
npx wrangler deploy
```

コネクタに登録するURLは `https://eos-mcp.<サブドメイン>.workers.dev/<MCP_PATH>`。

</details>

## 3. 動作確認

```bash
URL="https://eos-mcp.<サブドメイン>.workers.dev/<MCP_PATH>"

# ツール一覧が3つ返ること
curl -s -X POST "$URL" -H 'content-type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | python3 -m json.tool

# 今日の TODAY.md が返ること
curl -s -X POST "$URL" -H 'content-type: application/json' \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"eos_today","arguments":{}}}' \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["result"]["content"][0]["text"][:200])'
```

パスを1文字でも間違えると `404 Not found` になります（意図した挙動）。

## 4. claude.ai に登録する

1. Claude.ai → **設定 → コネクタ → カスタムコネクタを追加**
2. 名前: `Engineering OS`
3. URL: 手順2で作った `https://.../<MCP_PATH>`
4. OAuth の欄は空のまま「追加」
5. Project「Engineering OS 試験官」で、このコネクタが **有効** になっていることを確認
6. **iPhone の Claude アプリでも見えていることを確認**（一度繋げば全サーフェスで使えます）

確認は Project で次を送る。

```
eos_today を呼んで、日付とTrackだけ答えて。
```

## セキュリティの整理

| | 状態 |
|---|---|
| PAT の置き場所 | Worker の secret。端末にも Claude にも渡らない |
| PAT の権限 | 1リポジトリの Issues 読み書き ＋ Contents 読み取りのみ |
| URL が漏れたら | 公開済みファイルを読まれる／Issue #1 にコメントされる。リポジトリは書き換えられない |
| 復旧 | `npx wrangler secret put MCP_PATH` で入れ直し、コネクタのURLを更新する |

URLパスを認証に使っているのは、claude.ai のカスタムコネクタが**任意ヘッダを付けられない**ためです。
OAuth を実装すれば正攻法になりますが、Worker に OAuth プロバイダを載せる分だけ壊れる箇所が増えます。
影響範囲が上表のとおり限定的なので、いまはこの形にしています。

## ツール

| ツール | 動作 | 呼ぶタイミング |
|---|---|---|
| `eos_today` | `TODAY.md` を返す | 毎朝、出題の前に必ず |
| `eos_weekly_context` | `WEEKLY_CONTEXT.md` を返す | 日曜の週次レビューだけ |
| `eos_post_record` | 記録ブロックを Issue #1 へ投函 | 採点後、確認を求めずに |

`eos_post_record` は投函前に2つ検査します。

- `type: session` / `type: weekly` の行があるか（無いと GitHub 側の取り込みが起動しないため）
- 60000文字を超えていないか（GitHub のコメント上限は 65536）

どちらも引っかかったら投函せずエラーを返すので、「投函したのに保存されない」が起きません。

## 更新するとき

```bash
cd 10-automation/mcp && npx wrangler deploy
```

secret は消えません。コネクタの再登録も不要です。
