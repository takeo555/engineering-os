/**
 * Engineering OS の MCP サーバ（Cloudflare Workers）。
 *
 * claude.ai のカスタムコネクタとして登録し、Web・デスクトップ・**モバイル**の
 * すべてから同じツールが使えるようにする。日次が7日連続で止まった原因は、
 * モバイルの Project チャットが raw URL を取りに行かないことだった。
 * 指示文では直らないので、経路そのものを差し替える。
 *
 * ツールは3つだけにしてある。GitHub 公式 MCP を丸ごと繋ぐと数十個のツールが見え、
 * 試験官が朝からコード検索へ寄り道する余地を作るため。
 *
 *   eos_today           TODAY.md を返す（出題前に必ず呼ぶ）
 *   eos_weekly_context  WEEKLY_CONTEXT.md を返す（日曜の週次レビューだけ）
 *   eos_post_record     記録ブロックを Issue #1 へ投函する
 *
 * 認証は「推測できないURLパス」で行う（MCP_PATH）。claude.ai のカスタムコネクタは
 * 任意ヘッダを付けられないため。URLが漏れた場合にできることは
 * 「公開リポジトリのファイルを読む」「Issue #1 にコメントする」の2つだけで、
 * PAT 自体は Worker の secret にあり外に出ない。
 */

const PROTOCOL_VERSION = "2025-06-18";
const GH_API = "https://api.github.com";
const MAX_COMMENT_CHARS = 60000; // GitHub の上限は 65536

const TOOLS = [
  {
    name: "eos_today",
    description:
      "Engineering OS の今日の割り当て（TODAY.md）を返す。Drill 8問と Design 1問を出す前に必ず最初に呼ぶこと。" +
      "Project の Knowledge には入っていないので、ファイル検索ではなくこのツールで取る。",
    inputSchema: { type: "object", properties: {}, additionalProperties: false },
  },
  {
    name: "eos_weekly_context",
    description:
      "週次レビュー用の数字（WEEKLY_CONTEXT.md）を返す。日曜の週次レビューのときだけ呼ぶ。日次では呼ばない。",
    inputSchema: { type: "object", properties: {}, additionalProperties: false },
  },
  {
    name: "eos_post_record",
    description:
      "記録ブロックを「📥 記録の投函口」Issue へコメントとして投函する。" +
      "採点が終わって記録ブロックを出したら、ユーザーに確認を求めずにそのまま呼ぶ。新しい Issue は作られない。",
    inputSchema: {
      type: "object",
      properties: {
        body: {
          type: "string",
          description:
            "記録ブロックの全文。開きの --- からヘッダ、本文の最後までをそのまま渡す。要約・整形・改変をしない。",
        },
      },
      required: ["body"],
      additionalProperties: false,
    },
  },
];

function ghHeaders(env) {
  return {
    Authorization: `Bearer ${env.GITHUB_TOKEN}`,
    "User-Agent": "engineering-os-mcp",
    "X-GitHub-Api-Version": "2022-11-28",
  };
}

/**
 * raw.githubusercontent.com ではなく API から読む。
 * raw は CDN キャッシュで数分古いことがあり、朝の「前日分を掴む」事故を再発させるため。
 */
async function readRepoFile(env, path) {
  const res = await fetch(
    `${GH_API}/repos/${env.GITHUB_REPO}/contents/${path}?ref=${env.GITHUB_BRANCH || "main"}`,
    { headers: { ...ghHeaders(env), Accept: "application/vnd.github.raw" } },
  );
  if (!res.ok) {
    throw new Error(`${path} を読めませんでした（GitHub ${res.status}）`);
  }
  return res.text();
}

async function postIssueComment(env, body) {
  const res = await fetch(
    `${GH_API}/repos/${env.GITHUB_REPO}/issues/${env.ISSUE_NUMBER || "1"}/comments`,
    {
      method: "POST",
      headers: { ...ghHeaders(env), Accept: "application/vnd.github+json", "Content-Type": "application/json" },
      body: JSON.stringify({ body }),
    },
  );
  if (!res.ok) {
    throw new Error(`投函に失敗しました（GitHub ${res.status}）: ${(await res.text()).slice(0, 300)}`);
  }
  return (await res.json()).html_url;
}

async function callTool(env, name, args) {
  switch (name) {
    case "eos_today":
      return readRepoFile(env, "TODAY.md");

    case "eos_weekly_context":
      return readRepoFile(env, "WEEKLY_CONTEXT.md");

    case "eos_post_record": {
      const body = (args && args.body) || "";
      if (!body.trim()) {
        throw new Error("body が空です。記録ブロックの全文を渡してください。");
      }
      if (body.length > MAX_COMMENT_CHARS) {
        throw new Error(
          `記録ブロックが長すぎます（${body.length}文字）。回答やレビューを削らず、` +
            `Model answer を短くして ${MAX_COMMENT_CHARS} 文字以内にしてください。`,
        );
      }
      // record.yml はこの行が無いと起動しない。投函前に弾いて「投函したのに保存されない」を防ぐ
      if (!/^type:\s*(session|weekly)\s*$/m.test(body)) {
        throw new Error(
          "記録ブロックに `type: session` または `type: weekly` の行がありません。" +
            "この行が無いと GitHub 側の取り込みが起動しません。record-block.md の形に直してから投函してください。",
        );
      }
      const url = await postIssueComment(env, body);
      return `投函しました: ${url}\n1〜2分で同じIssueに「記録しました」が返ります。`;
    }

    default:
      throw new Error(`未知のツール: ${name}`);
  }
}

function rpcResult(id, result) {
  return { jsonrpc: "2.0", id, result };
}

function rpcError(id, code, message) {
  return { jsonrpc: "2.0", id, error: { code, message } };
}

async function handleRpc(env, msg) {
  const { id, method, params } = msg;

  switch (method) {
    case "initialize":
      return rpcResult(id, {
        protocolVersion: (params && params.protocolVersion) || PROTOCOL_VERSION,
        capabilities: { tools: { listChanged: false } },
        serverInfo: { name: "engineering-os", version: "1.0.0" },
      });

    case "ping":
      return rpcResult(id, {});

    case "tools/list":
      return rpcResult(id, { tools: TOOLS });

    case "tools/call": {
      const name = params && params.name;
      try {
        const text = await callTool(env, name, params && params.arguments);
        return rpcResult(id, { content: [{ type: "text", text }], isError: false });
      } catch (e) {
        // ツールの失敗はプロトコルエラーではなく isError で返す（モデルが読んで対処できる）
        return rpcResult(id, { content: [{ type: "text", text: String(e.message || e) }], isError: true });
      }
    }

    default:
      return rpcError(id, -32601, `Method not found: ${method}`);
  }
}

// Streamable HTTP はレスポンスを JSON でも SSE でも返してよいが、
// claude.ai のクライアントは SSE を期待することがある（「Couldn't reach the MCP server」の
// 報告の多くがここ）。Accept ヘッダを見て両方に対応する。
const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "content-type, authorization, mcp-session-id, mcp-protocol-version",
  "Access-Control-Expose-Headers": "mcp-session-id",
};

// ステートレスなのでセッションIDは固定でよい。返さないクライアントもあるので常に付ける
const SESSION_ID = "engineering-os";

function sseResponse(payloads) {
  const body = payloads.map((p) => `event: message\ndata: ${JSON.stringify(p)}\n\n`).join("");
  return new Response(body, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
      Connection: "keep-alive",
      "Mcp-Session-Id": SESSION_ID,
      ...CORS,
    },
  });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: CORS });
    }
    if (!env.MCP_PATH || url.pathname !== `/${env.MCP_PATH}`) {
      return new Response("Not found", { status: 404 });
    }

    // GET は SSE ストリームの要求。このサーバは自発的な通知を送らないので、
    // 405 を返すのも仕様上は正しいが、先に GET を試すクライアントがいるため
    // 空のストリームを 200 で返して接続チェックを通す。
    if (request.method === "GET") {
      return new Response(": ok\n\n", {
        headers: {
          "Content-Type": "text/event-stream",
          "Cache-Control": "no-cache",
          "Mcp-Session-Id": SESSION_ID,
          ...CORS,
        },
      });
    }
    if (request.method !== "POST") {
      return new Response("Method not allowed", { status: 405, headers: CORS });
    }

    let payload;
    try {
      payload = await request.json();
    } catch {
      return Response.json(rpcError(null, -32700, "Parse error"), { status: 400, headers: CORS });
    }

    const messages = Array.isArray(payload) ? payload : [payload];
    const responses = [];
    for (const msg of messages) {
      // 通知（id が無い）には応答を返さない
      if (msg.id === undefined || msg.id === null) continue;
      responses.push(await handleRpc(env, msg));
    }

    if (responses.length === 0) {
      return new Response(null, { status: 202, headers: { "Mcp-Session-Id": SESSION_ID, ...CORS } });
    }

    const wantsSse = (request.headers.get("accept") || "").includes("text/event-stream");
    if (wantsSse) return sseResponse(responses);

    return Response.json(Array.isArray(payload) ? responses : responses[0], {
      headers: { "Mcp-Session-Id": SESSION_ID, ...CORS },
    });
  },
};
