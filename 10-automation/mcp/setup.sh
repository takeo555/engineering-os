#!/usr/bin/env bash
# Engineering OS の MCP サーバを Cloudflare Workers に立てて、
# claude.ai のカスタムコネクタに登録する URL を出すまでを一度に行う。
#
#   bash 10-automation/mcp/setup.sh
#
# 入力はGitHubのPAT 1つだけ。PATは画面に表示せず、Workerのsecretへ直接渡す。
# このスクリプトはPATをファイルにも変数の履歴にも残さない。
set -euo pipefail

cd "$(dirname "$0")"

say() { printf '\n\033[1m%s\033[0m\n' "$*"; }
err() { printf '\n\033[31m%s\033[0m\n' "$*" >&2; }

# ---------------------------------------------------------------- 1. 前提確認
command -v node >/dev/null || { err "node が見つかりません"; exit 1; }
command -v openssl >/dev/null || { err "openssl が見つかりません"; exit 1; }

say "1/5 Cloudflare にログインしているか確認します"
if ! npx --yes wrangler whoami >/dev/null 2>&1; then
  echo "ログインしていません。ブラウザが開くので許可してください。"
  npx --yes wrangler login
fi
npx --yes wrangler whoami | sed -n '1,6p'

# ---------------------------------------------------------------- 2. PAT
say "2/5 GitHub の fine-grained PAT を貼ってください（表示されません）"
cat <<'HOWTO'
  まだ作っていない場合:
    https://github.com/settings/personal-access-tokens/new
    Repository access : Only select repositories → takeo555/engineering-os
    Permissions       : Issues = Read and write
                        Contents = Read-only
    Expiration        : 1年
  これ以外の権限は付けないこと。
HOWTO
printf '\nPAT: '
read -rs GH_PAT
printf '\n'
[ -n "$GH_PAT" ] || { err "PATが空です"; exit 1; }

say "  PATが有効か確認します"
code=$(curl -s -o /dev/null -w '%{http_code}' \
  -H "Authorization: Bearer $GH_PAT" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/takeo555/engineering-os/issues/1)
if [ "$code" != "200" ]; then
  err "GitHub が $code を返しました。PATの権限かリポジトリ名を確認してください。"
  exit 1
fi
echo "  OK（Issue #1 に到達できました）"

# ---------------------------------------------------------------- 3. secret
MCP_PATH=$(openssl rand -hex 16)

say "3/5 secret を登録します"
printf '%s' "$GH_PAT"    | npx --yes wrangler secret put GITHUB_TOKEN >/dev/null
printf '%s' "$MCP_PATH"  | npx --yes wrangler secret put MCP_PATH     >/dev/null
unset GH_PAT
echo "  GITHUB_TOKEN と MCP_PATH を登録しました"

# ---------------------------------------------------------------- 4. deploy
say "4/5 デプロイします"
out=$(npx --yes wrangler deploy 2>&1) || { err "$out"; exit 1; }
echo "$out" | grep -Eo 'https://[a-z0-9.-]+workers\.dev' | head -1 > /tmp/.eos_worker_host || true
HOST=$(head -1 /tmp/.eos_worker_host 2>/dev/null || true)
rm -f /tmp/.eos_worker_host
if [ -z "$HOST" ]; then
  err "デプロイ出力からURLを取れませんでした。以下を確認してください。"
  echo "$out"
  exit 1
fi
URL="$HOST/$MCP_PATH"

# ---------------------------------------------------------------- 5. 疎通確認
say "5/5 疎通を確認します"
sleep 3
tools=$(curl -s -X POST "$URL" -H 'content-type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' \
  | node -e 'let s="";process.stdin.on("data",d=>s+=d).on("end",()=>{
      try{console.log(JSON.parse(s).result.tools.map(t=>t.name).join(", "))}catch{console.log("PARSE_ERROR")}})')
echo "  ツール: $tools"
[ "$tools" = "PARSE_ERROR" ] && { err "応答を解釈できませんでした"; exit 1; }

today=$(curl -s -X POST "$URL" -H 'content-type: application/json' \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"eos_today","arguments":{}}}' \
  | node -e 'let s="";process.stdin.on("data",d=>s+=d).on("end",()=>{
      try{console.log(JSON.parse(s).result.content[0].text.split("\n")[0])}catch{console.log("PARSE_ERROR")}})')
echo "  eos_today: $today"

cat <<EOF

================================================================
 完了しました。次は claude.ai に登録します。

 設定 → コネクタ → カスタムコネクタを追加
   名前: Engineering OS
   URL :

   $URL

   OAuth の欄は空のまま「追加」

 そのあと Project「Engineering OS 試験官」で
 このコネクタが有効になっていることを確認してください。
 一度繋げば iPhone にも同期します。

 ※ このURLが実質のアクセスキーです。人に共有しないでください。
   作り直すときは:  npx wrangler secret put MCP_PATH
================================================================
EOF
