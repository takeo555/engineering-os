#!/usr/bin/env python3
"""CONTEXT.md を生成する。ChatGPTが毎朝読む唯一のファイル。

出題内容そのものはChatGPTが書くが、**何を出すか（Track / Format / Level / 狙う弱点）は
ここで決定論的に決める。** ChatGPTに選ばせるとブレて、弱点が放置されるため。

- 同じ日に何度実行しても同じ割り当てになる（日付をシードにする）
- OpenAI APIは使わない。標準ライブラリのみ
- 出力: CONTEXT.md、STATUS.md
"""
import json
import os
import random
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
            return level, f"{gap}日空いたため {base} から一時的に1段下げた"
    return base, f"base_level {base} のまま"


def pick_track(cfg, rows, sessions, weaknesses, today, rnd):
    weights = dict(cfg.get("track_weights", {}))
    for t in E.TRACKS:
        weights.setdefault(t, 25)

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

    # 週内カバレッジ: 木曜以降は未出題のTrackを優先する
    monday = today - timedelta(days=today.weekday())
    this_week = {s["track"] for s in sessions if s["date"] >= monday.isoformat()}
    if today.weekday() >= 3:
        missing = [t for t in E.TRACKS if t not in this_week]
        if missing:
            due_missing = [w for w in due if w["track"] in missing]
            if due_missing:
                due_missing.sort(
                    key=lambda w: E.PRIORITIES.index(w["priority"])
                    if w["priority"] in E.PRIORITIES else 1, reverse=True)
                return due_missing[0]["track"], due, "週内未出題かつ再テスト期限のTrackを優先"
            return rnd.choice(sorted(missing)), due, "週内未出題のTrackを補完"

    pool = sorted([t for t, w in weights.items() if w > 0]) or list(E.TRACKS)
    chosen = rnd.choices(pool, weights=[weights[t] for t in pool], k=1)[0]
    return chosen, due, "重み・弱点・連続回避から選択"


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
    track, due, track_reason = pick_track(cfg, rows, sessions, weaknesses, today, rnd)
    fmt, mode = pick_format(cfg, sessions, today, rnd)

    targets = [w for w in due if w["track"] == track][:2]
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
        f"| {t} | {f'{tavg[t]:.1f}' if t in tavg else '—'} |" for t in E.TRACKS)

    avg5 = E.moving_avg(rows, 5)
    rate = E.ontime_rate(rows, cfg.get("target_minutes", 30))

    body = f"""# CONTEXT — {today.isoformat()}（{weekday}）

> **自動生成。手で編集しないこと。** 毎朝{cfg.get('generate_time_jst', '06:00')} JSTと、
> 記録が保存されるたびに再生成されます。
> ChatGPTはこのファイルだけを読めば出題できます。他のファイルを読みに行く必要はありません。

## 今日の割り当て（この通りに出題すること）

| 項目 | 値 |
|---|---|
| 日付 | {today.isoformat()}（{weekday}） |
| Track | **{track}** |
| Format | **{fmt}** |
| Level | **{level}** |
| 回答環境 | {mode} |
| 想定所要時間 | {cfg.get('target_minutes', 30)}分 |
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
| 直近5回の平均スコア | {f'{avg5:.1f}' if avg5 is not None else '—'} |
| {cfg.get('target_minutes', 30)}分内完了率（直近10回） | {f'{rate:.0%}' if rate is not None else '—'} |
| 記録済みセッション数 | {len(rows)} |
| Open弱点 | {len(weaknesses)}件（High {sum(1 for w in weaknesses if w['priority'] == 'High')}件） |
| 再テスト期限切れ | {len(due)}件 |

### Track別平均（直近20回）

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

- **Design:** 要件を渡し、スキーマ・構成・インターフェースを設計させる
- **Review:** ありそうな「悪い設計」を提示し、問題点の指摘と修正を求める。悪い設計は自然に見えるものにする
- **Debug:** 症状と観測できる事実だけを渡し、切り分け手順を書かせる。原因は明かさない
- **Explain:** 「〜とは」ではなく「この状況で相手に説明せよ」の形にする

---

<!-- eos:context date={today.isoformat()} track={track} format={fmt} level={level}
     targets={",".join(w["id"] for w in targets) or "-"} -->
"""

    E.write_text(E.CONTEXT_FILE, body)
    status = E.update_status(cfg)

    print(json.dumps({
        "date": today.isoformat(), "track": track, "format": fmt, "level": level,
        "mode": mode, "targets": [w["id"] for w in targets],
        "is_session_day": is_session_day, "done_today": done_today,
        "status": status,
        "commit_message": f"chore(context): {today.isoformat()} {track} / {fmt} / {level}",
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
