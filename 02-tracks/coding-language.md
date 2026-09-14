# Category: Coding Language（Drill専用）

## Role in Engineering OS

**Drill専用カテゴリ。Design 15分では言語ドリルとしては出題しない**（ただし Design 問題の材料としてこれらの言語を使う）。

Go / Next.js / Python / Terraform の基礎文法・基本概念を反復で身体に入れる。公式ドキュメントを自習しながら、ドリルで抜けを検知する。

## Daily quota

- 毎日 **3問**、30秒・単答
- 記録は正答率のみ（例: `drill_lang: 2/3`）
- 3問の言語配分は `eos.config.json` の `coding_language_weights` に従ってランダム選択
  - Go 35% / Next.js 35% / Python 20% / Terraform 10%

## 学習リソース

| 言語 | 一次資料 |
|---|---|
| Go | https://go.dev/doc/ |
| Next.js | https://nextjs.org/docs |
| Python | https://docs.python.org/3/ |
| Terraform | https://developer.hashicorp.com/terraform/docs |

**書籍は買わない**。公式ドキュメントで詰まったら、ドリルの間違い履歴が示す分野に絞って追加調査する。

## 題材の例（言語別）

### Go
- goroutine と channel の基礎（send/receive、close、range）
- error handling（`errors.Is`, `errors.As`, `fmt.Errorf("...: %w", err)`）
- interface の暗黙実装
- スライスとマップの挙動（コピー・参照）
- struct のタグとJSON
- context.Context の使い方

### Next.js（App Router想定）
- Server Component と Client Component の区別
- `fetch` のキャッシュ挙動（`cache: 'no-store'` 等）
- `generateStaticParams`, `revalidatePath`
- ルーティング（動的セグメント、平行ルート）
- Server Actions
- Middleware

### Python
- 型ヒント（`Optional`, `Union`, `TypedDict`）
- iterator / generator（`yield`）
- decorator の書き方
- context manager（`with`, `__enter__`, `__exit__`）
- dataclass と Pydantic の違い
- 非同期（`async`/`await`）

### Terraform
- HCL の基本構文（block, argument, expression）
- variable / output / locals の使い分け
- resource と data source
- state の役割と backend
- module の作り方
- workspace と環境分離

## Miss handling

- ドリルで間違えた問題は `drill-misses.md` に「日付・Language(Go|Next.js|Python|Terraform)・分野・問題テーマ」で記録
- 翌日の言語ドリル3問のうち1問を、同じ言語・同じ分野の別問題に置き換える
- 特定の言語で連続2回間違えた → 翌週の weight を臨時+10%（Weekly Review で判断）

## Design問題の材料として

Design 15分問題（Layered Architecture / Code Review 等）では、これらの言語のコードを題材として使う。ただし言語の細かい文法問題は Design では出題しない（それは Drill の役割）。
