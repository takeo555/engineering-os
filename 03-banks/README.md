# Banks

日次セッションから生まれた、再利用できる資産だけを置きます。教科書の要約は置きません。

| Bank | Purpose | Promotion rule |
|---|---|---|
| [Pattern Bank](pattern-bank.md) | 繰り返し使える設計の型 | 2回以上の出題で有効だったものだけ |
| [Pitfall Bank](pitfall-bank.md) | 自分が実際に踏んだ落とし穴 | レビューで指摘された事実があるものだけ |
| [Tradeoff Bank](tradeoff-bank.md) | 条件付きの判断基準 | 選択肢と条件をセットで書けるものだけ |
| [Term Bank](term-bank.md) | 説明できなかった用語 | 自分の言葉で30秒説明できるようになるまで |

## 昇格の流れ

```text
日次セッション
  ↓ 試験官Projectが 記録ブロックに bank_N を書く
promotion-queue.md に Pending として自動で積まれる
  ↓ Weekly Reviewが adopt / reject を判定
自分で該当ファイルへ書き写し、queueの行を削除
```

**Bankへの書き込みは自動化していません。** 自動で流し込むとBankが機械的な要約で埋まり、実際に使われない情報の山になります。週1回、[promotion-queue.md](promotion-queue.md)を見て、採用したものだけを手で書き写してください。3分の作業です。

## Hygiene

- 用語集ではなく、Functionと場面で整理する
- 同じ内容の言い換えを増やさない
- Activeは実際の出題で複数回使えたものだけ
- 使わないものは月次ReviewでArchiveへ移す
- 1Bankあたりのアクティブ項目は最大20件
