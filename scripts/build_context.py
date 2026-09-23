#!/usr/bin/env python3
"""CONTEXT.md を生成する。試験官が毎朝読む唯一のファイル。

Drill と Design の両方の割り当てを決定する。
- Drill: AI 3 / 言語 3 / ネットワーク 2 の題材枠を決める（直近3日の drill-misses から類題1問を混ぜる）
- Design: Track / Format / Level / 狙う弱点を決める（4Track・各25%）

出題内容そのものは試験官が書くが、**何を出すかはここで決定論的に決める。**
試験官に選ばせるとブレて、弱点が放置されるため。

- 同じ日に何度実行しても同じ割り当てになる（日付をシードにする）
- 外部APIは使わない。標準ライブラリのみ
- 出力: TODAY.md（始めるのに要るものだけ・貼れる）, CONTEXT.md（全量）, STATUS.md
"""
import json
import os
import random
import re
import sys
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import eoslib as E  # noqa: E402

RAW_BASE = "https://raw.githubusercontent.com"


def pick_level(cfg, rows, today):
    """base_level を基準に、空白期間だけを見て一時的に下げる。"""
    base = cfg.get("base_level", "L2")
    rules = cfg.get("difficulty_rules", {})
    if len(rows) >= 2:
        last = date.fromisoformat(rows[0]["date"])
        gap = (today - last).days
        if gap >= rules.get("level_down_if_gap_days", 3):
            level = E.shift_level(base, -1)
            if level != base:
                return level, f"{gap}日空いたため {base} から一時的に1段下げた"
            return level, f"{gap}日空いたが {base} が最下位のため据え置き"
    return base, f"base_level {base} のまま"


def pick_design_track(cfg, rows, sessions, weaknesses, today, rnd):
    weights = {t: cfg.get("design_track_weights", {}).get(t, 25)
               for t in E.DESIGN_TRACKS}

    avgs = E.track_averages(rows)
    if avgs:
        worst = min(avgs, key=avgs.get)
        if worst in weights:
            weights[worst] += 15

    due = [w for w in weaknesses
           if w["retest_on"] not in ("—", "", "-") and w["retest_on"] <= today.isoformat()]
    for w in due:
        if w["track"] in weights:
            weights[w["track"]] += 30 if w["priority"] == "High" else 15

    # 直近2回が同じTrackなら除外（3日連続で同じTrackを出さない）
    recent = [s["track"] for s in sessions[:2]]
    for t in set(recent):
        if recent.count(t) >= 2 and t in weights:
            weights[t] = 0

    # 週内カバレッジ: 木曜以降は、今週まだ出ていない Design Track を優先する
    monday = today - timedelta(days=today.weekday())
    this_week = {s["track"] for s in sessions if s["date"] >= monday.isoformat()}
    if today.weekday() >= 3:
        missing = [t for t in E.DESIGN_TRACKS if t not in this_week]
        if missing:
            due_missing = [w for w in due if w["track"] in missing]
            if due_missing:
                due_missing.sort(
                    key=lambda w: E.PRIORITIES.index(w["priority"])
                    if w["priority"] in E.PRIORITIES else 1, reverse=True)
                return due_missing[0]["track"], due, "週内未出題かつ再テスト期限のDesign Trackを優先"
            return rnd.choice(sorted(missing)), due, "週内未出題のDesign Trackを補完"

    pool = sorted([t for t, w in weights.items() if w > 0]) or list(E.DESIGN_TRACKS)
    chosen = rnd.choices(pool, weights=[weights[t] for t in pool], k=1)[0]
    return chosen, due, "重み・弱点・連続回避から選択"


# ---------------------------------------------------------------- Drill

# 分野の枠。試験官はこの枠に沿って具体的な問題文を作る。
NETWORK_CHAPTERS = [
    "1章 Webブラウザがメッセージを作る",
    "2章 プロトコル・スタックとLANアダプタ",
    "3章 ハブ・スイッチ・ルータ",
    "4章 アクセス回線とプロバイダ",
    "5章 ファイアウォール・キャッシュ・負荷分散",
    "6章 Webサーバ側の処理",
]

LANGUAGE_TOPICS = {
    "Go": ["goroutine/channel", "error handling", "interface",
           "slice/map の挙動", "struct タグとJSON", "context"],
    "Next.js": ["Server/Client Component", "fetch のキャッシュ", "ルーティング",
                "Server Actions", "Middleware", "revalidate"],
    "Python": ["型ヒント", "generator", "decorator", "context manager",
               "dataclass/Pydantic", "async/await"],
    "Terraform": ["HCL 基本構文", "variable/output/locals", "resource と data source",
                  "state と backend", "module", "workspace"],
}


def _miss_note(items):
    """題材枠の「直近のmiss類題」欄に出す1行。"""
    if not items:
        return "なし"
    m = items[0]
    label = m["subtopic"] or m["theme"][:20]
    if m.get("language"):
        label = f"{m['language']}/{label}"
    return f"あり: {label}（{m['date']} miss）"


def _miss_suffix(items):
    """TODAY.md の1行版。miss が無い日は何も足さない。"""
    note = _miss_note(items)
    return "" if note == "なし" else f" ／ 直近miss{note[2:]}"


def pick_ai_drill(cfg, phase, misses, rnd):
    """フェーズの AI 題材から、今日の3問分の分野枠を決める。"""
    n = cfg.get("daily_drill", {}).get("ai", 3)
    pool = list(phase.get("ai_topics") or [])
    hit = misses.get("AI") or []
    if not pool:
        # ROADMAP.md が読めない日でも止めない
        return ["現フェーズのAI範囲"] * n, hit
    picked = rnd.sample(pool, k=min(n, len(pool)))
    while len(picked) < n:
        picked.append(rnd.choice(pool))
    if hit:
        # 1問を直近missの分野に差し替える（同じ問題文の再出題ではない）
        picked[-1] = f"{hit[0]['subtopic']}（直近missの類題）"
    return picked, hit


def pick_language_drill(cfg, misses, rnd):
    """coding_language_weights に従って3問の言語と分野枠を決める。"""
    n = cfg.get("daily_drill", {}).get("coding_language", 3)
    weights = cfg.get("coding_language_weights", {}) or {"Go": 25, "Next.js": 25,
                                                         "Python": 25, "Terraform": 25}
    langs = sorted(weights)
    chosen = rnd.choices(langs, weights=[weights[l] for l in langs], k=n)
    picked = [f"{l} / {rnd.choice(LANGUAGE_TOPICS.get(l, ['基礎']))}" for l in chosen]
    hit = misses.get("Coding Language") or []
    if hit:
        m = hit[0]
        lang = m.get("language") or chosen[-1]
        picked[-1] = f"{lang} / {m['subtopic']}（直近missの類題）"
    return picked, hit


def pick_network_drill(cfg, misses, rnd):
    """読了章の枠から2問分の分野枠を決める。"""
    n = cfg.get("daily_drill", {}).get("network", 2)
    picked = rnd.sample(NETWORK_CHAPTERS, k=min(n, len(NETWORK_CHAPTERS)))
    hit = misses.get("Network") or []
    if hit:
        picked[-1] = f"{hit[0]['subtopic']}（直近missの類題）"
    return picked, hit


def pick_format(cfg, sessions, today, rnd):
    """キーボードのある日はDesign寄り、移動日は散文で答えられる形式に寄せる。"""
    weekday = E.WEEKDAY_NAMES[today.weekday()]
    keyboard_days = cfg.get("keyboard_days", [])
    allowed = (cfg.get("keyboard_formats", E.FORMATS) if weekday in keyboard_days
               else cfg.get("mobile_formats", E.FORMATS))
    allowed = [f for f in allowed if f in E.FORMATS] or list(E.FORMATS)

    weights = {f: cfg.get("format_weights", {}).get(f, 25) for f in allowed}
    last = sessions[0]["format"] if sessions else None
    if last in weights and len(weights) > 1:
        weights[last] = max(1, weights[last] // 4)
    pool = sorted(weights)
    chosen = rnd.choices(pool, weights=[weights[f] for f in pool], k=1)[0]
    mode = "キーボード想定" if weekday in keyboard_days else "モバイル想定"
    return chosen, mode


def focus_excerpt(text, limit=1200):
    """CURRENT_FOCUS.md から Current cycle と Focus skills だけを抜く。"""
    keep, out = False, []
    for line in text.splitlines():
        if line.startswith("## "):
            keep = line.startswith(("## Current cycle", "## Focus skills",
                                    "## Concepts to activate"))
        if keep:
            out.append(line)
    return "\n".join(out).strip()[:limit] or "（CURRENT_FOCUS.md が空）"


def main():
    cfg = E.load_config()
    today = E.today_jst()
    weekday = E.WEEKDAY_NAMES[today.weekday()]
    rnd = random.Random(today.toordinal())  # 同じ日なら何度実行しても同じ割り当て

    rows = E.read_scores()
    sessions = E.recent_sessions(30)
    weaknesses = E.parse_weaknesses()

    is_session_day = weekday in cfg.get("session_days", E.WEEKDAY_NAMES)
    level, level_reason = pick_level(cfg, rows, today)
    track, due, track_reason = pick_design_track(cfg, rows, sessions, weaknesses,
                                                 today, rnd)
    fmt, mode = pick_format(cfg, sessions, today, rnd)

    phase = E.current_phase(today)
    lookback = cfg.get("drill", {}).get("miss_reinject_lookback_days", 3)
    misses = E.load_recent_drill_misses(lookback, today)
    ai_slots, ai_miss = pick_ai_drill(cfg, phase, misses, rnd)
    lang_slots, lang_miss = pick_language_drill(cfg, misses, rnd)
    net_slots, net_miss = pick_network_drill(cfg, misses, rnd)

    # 1日1件に絞る。15分の問題で2つの弱点を同時に狙うと難度が跳ね上がる
    targets = [w for w in due if w["track"] == track][:1]
    if not targets:
        targets = [w for w in weaknesses
                   if w["priority"] == "High" and w["track"] == track][:1]

    done_today = any(s["date"] == today.isoformat() and s.get("status") == "done"
                     for s in sessions)

    # ---------------------------------------------------------------- 本文
    target_lines = "\n".join(
        f"- `{w['id']}` [{w['priority']}] {w['weakness']}（期限 {w['retest_on']}）"
        for w in targets) or "- なし（今日は新しい題材でよい）"

    open_lines = "\n".join(
        f"| {w['id']} | {w['priority']} | {w['weakness']} | {w['track']} | {w['retest_on']} |"
        for w in sorted(weaknesses,
                        key=lambda w: (E.PRIORITIES.index(w["priority"])
                                       if w["priority"] in E.PRIORITIES else 1,
                                       w["retest_on"]), reverse=True)[:8]
    ) or "| — | — | 未クローズの弱点なし | — | — |"

    hist_lines = "\n".join(
        f"| {s['date']} | {s['track']} | {s['format']} | {s['level']} | {s['title'][:40]} |"
        for s in sessions[:14]) or "| — | — | — | — | 履歴なし（初回） |"

    tavg = E.track_averages(rows, 20)
    tavg_lines = "\n".join(
        f"| {t} | {f'{tavg[t]:.1f}' if t in tavg else '—'} |" for t in E.DESIGN_TRACKS)

    avg5 = E.moving_avg(rows, 5)
    design_minutes = E.design_target_minutes(cfg)
    rate = E.ontime_rate(rows, design_minutes)

    drill_lines = "\n".join([
        f"| AI | {len(ai_slots)} | {'；'.join(ai_slots)} | {_miss_note(ai_miss)} |",
        f"| 言語 | {len(lang_slots)} | {'；'.join(lang_slots)} | {_miss_note(lang_miss)} |",
        f"| ネットワーク | {len(net_slots)} | {'；'.join(net_slots)} | {_miss_note(net_miss)} |",
    ])
    phase_line = (f"Phase {phase['phase']}（{phase['name']}・{phase['start']}〜{phase['end']}）"
                  if phase["phase"] else "未設定（ROADMAP.md を確認）")
    if phase["phase"] and not phase["in_range"]:
        phase_line += " ※今日は ROADMAP.md の期間外。いちばん近いフェーズを採用した"

    body = f"""# CONTEXT — {today.isoformat()}（{weekday}）

> **自動生成。手で編集しないこと。** 毎朝{cfg.get('generate_time_jst', '06:00')} JSTと、
> 記録が保存されるたびに再生成されます。
> 試験官はこのファイルだけを読めば出題できます。他のファイルを読みに行く必要はありません。
> **Drill 8問（30秒・単答）を先に、そのあと Design 1問（{design_minutes}分）。この順を変えないこと。**

## 今日のフェーズ

{phase_line}

AI ドリルの題材はこのフェーズに従います。詳細は `ROADMAP.md`。

## 今日の Drill 題材枠

| カテゴリ | 問題数 | 分野の枠 | 直近のmiss類題 |
|---|---|---|---|
{drill_lines}

（試験官はこの枠に沿って具体的な問題文を生成する。30秒で単答できる形にし、選択肢は出さない。
「直近のmiss類題」が「あり」のカテゴリは、そのカテゴリの1問を同じ分野の**別問題**に差し替える）

Drill の記録はカテゴリ別正答率のみ。5軸採点も Weakness Log 登録もしない。

## 今日の Design 割り当て（この通りに出題すること）

| 項目 | 値 |
|---|---|
| 日付 | {today.isoformat()}（{weekday}） |
| Track | **{track}** |
| Format | **{fmt}** |
| Level | **{level}** |
| 回答環境 | {mode} |
| 想定所要時間 | {design_minutes}分 |
| 今日はセッション日か | {"はい" if is_session_day else "いいえ（休息日。求められたら出題してよい）"} |
| 今日の記録 | {"保存済み。2問目は出さない" if done_today else "未保存"} |

選定理由（本人向け。問題文には書かない）

- Track: {track_reason}
- Level: {level_reason}
- Format: {mode}のため{fmt}を選択

## 今日狙う弱点（問題文に弱点名を書かず、必ず表面化させること）

{target_lines}

## 未クローズの弱点（上位8件）

| ID | Priority | Weakness | Track | Retest on |
|---|---|---|---|---|
{open_lines}

## 直近の出題履歴（題材の重複を避ける。同じ題材は10回空ける）

| Date | Track | Format | Level | Title |
|---|---|---|---|---|
{hist_lines}

## 今の数字

| Metric | Value |
|---|---|
| 直近5回の平均スコア（Design） | {f'{avg5:.1f}' if avg5 is not None else '—'} |
| {design_minutes}分内完了率（直近10回） | {f'{rate:.0%}' if rate is not None else '—'} |
| 記録済みセッション数 | {len(rows)} |
| Open弱点 | {len(weaknesses)}件（High {sum(1 for w in weaknesses if w['priority'] == 'High')}件） |
| 再テスト期限切れ | {len(due)}件 |

### Design Track別平均（直近20回）

| Track | Avg |
|---|---|
{tavg_lines}

## 今週の重点（CURRENT_FOCUS.md 抜粋）

{focus_excerpt(E.read_text(E.CURRENT_FOCUS))}

## Levelの意味

| Level | 出題の重心 |
|---|---|
| L1 | 定義を使って設計を直せるか。選択肢を示してよい |
| L2 | 要件から妥当な設計を自力で書けるか。定石を知っているか |
| L3 | 非機能要件を入れて複数案を比較できるか。代償を語れるか |
| L4 | 制約下でアーキテクチャを選定し、ADRを書けるか |

## Formatの意味

- **Recall:** Drill 専用。30秒で単答できる基礎問題。選択肢は出さない
- **Design:** 要件を渡し、スキーマ・構成・インターフェースを設計させる
- **Review:** ありそうな「悪い設計」を提示し、問題点の指摘と修正を求める。悪い設計は自然に見えるものにする
- **Debug:** 症状と観測できる事実だけを渡し、切り分け手順を書かせる。原因は明かさない
- **Explain:** 「〜とは」ではなく「この状況で相手に説明せよ」の形にする

---

<!-- eos:context date={today.isoformat()} track={track} format={fmt} level={level}
     targets={",".join(w["id"] for w in targets) or "-"}
     phase={phase["phase"] or "-"} drill=ai:{len(ai_slots)},lang:{len(lang_slots)},network:{len(net_slots)} -->
"""

    E.write_text(E.CONTEXT_FILE, body)

    # ------------------------------------------------ TODAY.md（始めるのに要るものだけ）
    # CONTEXT.md は全量（弱点一覧・履歴14件・数字・Level/Formatの定義）で 7KB 近くある。
    # そのうち毎日変わるのはこの30行だけ。モバイルで貼るのも、定期タスクが丸ごと
    # 読み込むのもこちらを使う。静的な定義は Project の Knowledge 側に置く。
    today_targets = "\n".join(
        f"- `{w['id']}` [{w['priority']}] {w['weakness']}" for w in targets
    ) or "- なし（今日は新しい題材でよい）"

    # 旧い記録は title に日付が入っているものがある。1行を短く保つため落とす
    def _short_title(t):
        return re.sub(r"^\d{4}-\d{2}-\d{2}\s*[—–-]\s*", "", t)[:40]

    today_hist = "\n".join(
        f"- {s['date']} {s['track']} / {s['format']} — {_short_title(s['title'])}"
        for s in sessions[:5]) or "- 履歴なし（初回）"

    today_drill = "\n".join([
        f"- **AI {len(ai_slots)}問**: {'；'.join(ai_slots)}{_miss_suffix(ai_miss)}",
        f"- **言語 {len(lang_slots)}問**: {'；'.join(lang_slots)}{_miss_suffix(lang_miss)}",
        f"- **ネットワーク {len(net_slots)}問**: {'；'.join(net_slots)}{_miss_suffix(net_miss)}",
    ])

    today_body = f"""# TODAY — {today.isoformat()}（{weekday}）

生成: {E.now_jst_str()} JST ／ 自動生成・手で編集しない

> **今日の割り当ての正本はこの1ファイル。** 見出しの日付が今日でなければ使わないこと
> （前日分を掴んでいる＝生成が遅れている。`build-context` を手動実行する）。
> 順序は **Drill 8問（30秒・単答）→ Design 1問（{design_minutes}分）**。入れ替えない。

## 1. Drill 8問（合計4分・単答・選択肢なし）

Phase: {phase_line}

{today_drill}

「直近missあり」のカテゴリは、その1問を同じ分野の**別問題**に差し替える。

## 2. Design 1問（{design_minutes}分）

| 項目 | 値 |
|---|---|
| Track | **{track}** |
| Format | **{fmt}** |
| Level | **{level}** |
| 回答環境 | {mode} |
| 想定所要時間 | {design_minutes}分 |
| 今日はセッション日か | {"はい" if is_session_day else "いいえ（休息日。求められたら出題してよい）"} |
| 今日の記録 | {"**保存済み。2問目は出さない**" if done_today else "未保存"} |

Track / Format / Level は AI が選び直さない。この表のとおりに出す。

## 3. 今日狙う弱点（1件だけ。問題文に弱点名を書かず、必ず表面化させる）

{today_targets}

## 4. 直近5回（題材の重複を避ける）

{today_hist}

---

<!-- eos:today date={today.isoformat()} track={track} format={fmt} level={level}
     targets={",".join(w["id"] for w in targets) or "-"}
     phase={phase["phase"] or "-"} done={"1" if done_today else "0"} -->
"""
    E.write_text(E.TODAY_FILE, today_body)

    status = E.update_status(cfg)

    print(json.dumps({
        "date": today.isoformat(), "track": track, "format": fmt, "level": level,
        "mode": mode, "targets": [w["id"] for w in targets],
        "phase": phase["phase"], "drill": {"ai": ai_slots, "lang": lang_slots,
                                           "network": net_slots},
        "is_session_day": is_session_day, "done_today": done_today,
        "status": status,
        "commit_message": f"chore(context): {today.isoformat()} {track} / {fmt} / {level}",
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
