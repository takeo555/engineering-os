# Scoring Anchors

**このファイルは試験官ProjectのKnowledgeにアップロードします。** 採点のたびに必ず参照させ、「今回の回答はどの見本に近いか」を先に決めてから±10点で調整させます。

LLMの採点基準は数週間で自然にドリフトします。9月の68点と12月の68点が別物になると、`scores.csv` を根拠にした難易度調整とTrack比重調整が土台から崩れます。それを防ぐための固定基準です。

見本は同じ1問に対する3種類の回答です。**問題が違っても、判断の粒度と根拠の量を見比べる基準として使えます。**

**この見本はすべて Design 15分想定の分量です。** 30分想定で書かれた旧版は使いません。

## 改訂履歴

| 版 | 日付 | 変更 |
|---|---|---|
| v1 | 2026-09-02 | 30分想定で作成 |
| v2 | 2026-09-14 | **二層構造改修に伴い15分想定へ縮小。** 提出物を4→2項目、DDLを3〜5テーブル→2〜3テーブルに。5軸の意味と50/70/85の閾値は据え置き |

v1 と v2 の点数は厳密には比較できません。`scores.csv` の 2026-09-13 以前の行と以後の行を1本の移動平均で読むときは、この境目を意識してください。**v2 を今後は変えません。**

---

## 共通の問題（見本用・15分想定）

> **前提:** 社内向けの会議室予約システム。会議室20室、利用者300名、予約は30分単位、営業時間09:00–21:00。PostgreSQL 16。
>
> **要件:** (1) 同じ会議室の同じ時間帯を2人が予約できない (2) キャンセルでき、キャンセル済みの枠は再予約できる (3) 誰がいつキャンセルしたか確認できる
>
> **提出物:** 主要テーブルのDDL（2〜3テーブル）、要件1を構造で防ぐ方法
>
> **制約:** アプリ側の排他制御に依存しない

要件2と要件1は、素直に実装すると衝突します（論理削除 + UNIQUE制約）。**これに気づけるかが最大の分岐点です。**

---

## Anchor A — 50点

### 回答の要旨

```sql
CREATE TABLE reservations (
  id BIGSERIAL PRIMARY KEY,
  room_id BIGINT NOT NULL,
  user_id BIGINT NOT NULL,
  start_at TIMESTAMPTZ NOT NULL,
  end_at TIMESTAMPTZ NOT NULL,
  is_deleted BOOLEAN DEFAULT FALSE
);
```

「ダブルブッキングはアプリ側で予約前にSELECTして確認する。キャンセルは is_deleted を立てる。」

### 採点

| 軸 | 点 | 理由 |
|---|---|---|
| Correctness | 14/30 | 制約に明示的に違反している（アプリ側の排他に依存しない、という制約を無視）。SELECT後にINSERTする方式は競合状態を防げない |
| Completeness | 11/25 | 要件3が完全に未対応。要件1を構造で防ぐ方法が提出されていない |
| Reasoning | 11/25 | 「アプリ側で確認する」以上の根拠がない。なぜその構造かの説明が無い |
| Practicality | 7/10 | 動く。運用は単純 |
| Clarity | 7/10 | 短く読みやすいが、判断が書かれていない |
| **合計** | **50** | |

### 50点の特徴

- 制約や要件を1つ以上**明示的に無視している**
- 外部キー・NOT NULL・一意制約といった整合性の道具が使われていない
- 「アプリ側で」「バリデーションで」に逃げている
- 説明が構造の描写だけで、判断になっていない

---

## Anchor B — 70点

### 回答の要旨

```sql
CREATE TABLE reservations (
  id BIGSERIAL PRIMARY KEY,
  room_id BIGINT NOT NULL REFERENCES rooms(id),
  user_id BIGINT NOT NULL REFERENCES users(id),
  start_at TIMESTAMPTZ NOT NULL,
  end_at TIMESTAMPTZ NOT NULL,
  is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (room_id, start_at)
);
```

「ダブルブッキングは `UNIQUE (room_id, start_at)` で構造的に防ぐ。アプリ側の排他には頼らない。キャンセルは `is_deleted`。キャンセル履歴は `canceled_by` / `canceled_at` を足せばいいと思うが、複数回のキャンセルと再予約を繰り返した履歴までは取れない。**ここは分からない。**」

### 採点

| 軸 | 点 | 理由 |
|---|---|---|
| Correctness | 18/30 | UNIQUE制約が要件2と矛盾する（`is_deleted = true` の行が再予約を阻む）。複数枠予約の重なりを `start_at` の一意性だけでは検知できない |
| Completeness | 16/25 | 要件1・2に触れたが要件3が未達 |
| Reasoning | 19/25 | 「アプリ側の排他に頼らずDB制約で防ぐ」という方針を明示できている。ただし一意制約の列の選び方に根拠がない |
| Practicality | 8/10 | 外部キーとNOT NULLを最初から入れている |
| Clarity | 8/10 | 分からない箇所を隠さず明示した。実務のレビューでも望ましい振る舞い |
| **合計** | **69** | |

### 70点の特徴

- **方針は正しいが、要件間の衝突に気づいていない**
- 整合性の道具（FK / NOT NULL / UNIQUE）を使えている
- 判断の理由を1つは述べている（ただし全部ではない）
- 分からない箇所を隠さない

**このレベルが L2（若手）の標準的な到達点です。** 70点は「良い回答」ではなく「想定どおり」です。ここで甘く採点すると難易度調整が壊れます。

---

## Anchor C — 85点

### 回答の要旨

「まず要件1と要件2が衝突します。論理削除を入れると素のUNIQUE制約が再予約を弾くので、**部分インデックスか、状態遷移で行を消す設計に切り替える必要があります。** 予約単位が30分固定か可変かで設計が変わるので、そこは要件確認事項として挙げます。固定と仮定して進めます。」

```sql
CREATE TABLE reservations (
  id BIGSERIAL PRIMARY KEY,
  room_id BIGINT NOT NULL REFERENCES rooms(id),
  user_id BIGINT NOT NULL REFERENCES users(id),
  slot_start TIMESTAMPTZ NOT NULL,
  status TEXT NOT NULL DEFAULT 'active'
         CHECK (status IN ('active','canceled')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX uq_active_slot
  ON reservations (room_id, slot_start) WHERE status = 'active';

CREATE TABLE reservation_events (
  id             BIGSERIAL PRIMARY KEY,
  reservation_id BIGINT NOT NULL REFERENCES reservations(id),
  event_type     TEXT NOT NULL CHECK (event_type IN ('created','canceled')),
  actor_user_id  BIGINT NOT NULL REFERENCES users(id),
  occurred_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

「**部分ユニークインデックス**が要件1と要件2を同時に満たします。`status = 'active'` の行だけが一意なので、キャンセル済みの枠は再予約できます。要件3は履歴をイベント表に逃がして解決します。予約本体は現在の状態だけを持つ純粋な構造に保ちます。

インデックスの列順は `(room_id, slot_start)`。**等価条件の列を先、範囲条件の列を後**にするのが基準です。

可変長の予約を許すなら `EXCLUDE USING gist` が必要になりますが、**読めない制約は事故を呼ぶ**ので、要件が本当にそうでない限り採りません。」

### 採点

| 軸 | 点 | 理由 |
|---|---|---|
| Correctness | 26/30 | 要件間の衝突を先に指摘し、構造で解決している。満点でないのは、予約本体とイベント表の整合（トランザクション境界）に触れていないため |
| Completeness | 22/25 | 要件1〜3すべてに対応。可変長予約を要件確認事項として明示 |
| Reasoning | 22/25 | 部分インデックスを選んだ理由、列順の基準、複雑な制約を避ける理由まで言語化されている |
| Practicality | 9/10 | チームが読める設計を選ぶ判断がある |
| Clarity | 8/10 | 情報量が多く、要点の順序がやや読み取りにくい |
| **合計** | **87** | |

### 85点の特徴

- **要件間の衝突・矛盾を自分で発見し、設計前に指摘している**
- 要件確認事項と、仮定を置いて進める部分を分けている
- すべての判断に基準がある（「等価条件を先」のような一般化された形）
- 採らなかった選択肢とその理由がある
- 実装の複雑さと運用のバランスを判断に入れている

---

## 採点手順

1. 回答を読み、A / B / C のどれに最も近いかを決める
2. その見本の点数を出発点にする
3. 軸ごとに±10点の範囲で調整する
4. 「どの見本に近いと判断したか」をスコアの `note` に書かない（記録が冗長になる）が、内部では必ず経由する

## 点数帯の意味

| 帯 | 意味 | 出題側の対応 |
|---|---|---|
| 〜49 | 制約や要件を無視している | Levelを下げる候補 |
| 50–69 | 方針は立つが衝突に気づけない | 現状の標準。同じ論点を形式を変えて再出題 |
| 70–84 | 衝突に気づき、根拠を1つは言える | 順調。非機能要件を足していく |
| 85– | 要件確認と代替案の棄却まで書ける | Levelを上げる候補 |

## Drill には使わない

このファイルは **Design 15分問題の採点基準です。** Drill（30秒・単答）は完全一致で正誤を判定するだけで、5軸採点も anchors も使いません。

## メンテナンス

見本は**変えません。** 変えると過去のスコアと比較できなくなります（改訂履歴の v1→v2 が唯一の例外で、二層構造への移行に伴う想定時間の変更のためです）。

Levelが上がって見本が易しすぎると感じた場合は、既存の3本を残したまま `Anchor D — L3の85点` を追記します。四半期リセットで見直します。
