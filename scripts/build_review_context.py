#!/usr/bin/env python3
"""週次・月次レビュー用の「事実」をMarkdownで書き出す。

講評はChatGPTが書く。ここは数字だけを担当する。OpenAI APIは使わない。
難易度（base_level）の判定はここで決定論的に行い、ChatGPTには判定させない。

使い方: build_review_context.py [--period week|month]
出力: WEEKLY_CONTEXT.md（週次）/ MONTHLY_CONTEXT.md（月次）
"""
import json
import os
import sys
from collections import defaultdict
from datetime import timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import eoslib as E  # noqa: E402


def decide_base_level(cfg, rows, period_rows):
    """base_level を動かすのは週次だけ。1週あたり±1段。"""
    base = cfg.get("base_level", "L2")
    rules = cfg.get("difficulty_rules", {})
    min_sessions = rules.get("weekly_min_sessions_to_adjust", 3)
    target = cfg.get("target_minutes", 30)

    if len(period_rows) < min_sessions:
        return base, (f"今週のセッションが{len(period_rows)}回（{min_sessions}回未満）のため"
                      "難易度は変えない。まず回数を戻すこと")

    rate = E.ontime_rate(rows, target)
    avg5 = E.moving_avg(rows, 5)
    if rate is not None and rate < rules.get("weekly_level_down_if_ontime_rate_below", 0.5):
        new = E.shift_level(base, -1)
        return new, f"{target}分内完了率が{rate:.0%}のため {base} → {new}"
    if avg5 is not None and avg5 >= rules.get("weekly_level_up_if_avg5_above", 85):
        new = E.shift_level(base, 1)
        return new, f"直近5回平均が{avg5:.0f}点のため {base} → {new}"
    return base, f"条件を満たさないため {base} のまま"


def main():
    period = "week"
    if "--period" in sys.argv:
        period = sys.argv[sys.argv.index("--period") + 1]

    cfg = E.load_config()
    today = E.today_jst()

    if period == "month":
        start = today.replace(day=1)
        end = (start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        label = start.strftime("%Y-%m")
        out_file = E.WEEKLY_CONTEXT_FILE.replace("WEEKLY_", "MONTHLY_")
        title = f"MONTHLY_CONTEXT — {label}"
    else:
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)
        iso_year, iso_week, _ = today.isocalendar()
        label = f"{iso_year}-W{iso_week:02d}"
        out_file = E.WEEKLY_CONTEXT_FILE
        title = f"WEEKLY_CONTEXT — {label}"

    rows = E.read_scores()
    period_rows = [r for r in rows if start.isoformat() <= r["date"] <= end.isoformat()]
    weaknesses = E.parse_weaknesses()
    all_weak = E.parse_weaknesses(include_closed=True)
    sessions = E.recent_sessions(30)

    per_track = defaultdict(list)
    for r in period_rows:
        per_track[r["track"]].append(r["total"])

    if period == "week":
        new_level, level_reason = decide_base_level(cfg, rows, period_rows)
    else:
        new_level = cfg.get("base_level", "L2")
        level_reason = "難易度を動かすのは週次だけ。月次では変更しない"
    closed_in_period = [w for w in all_weak if w["status"] == "Closed"]

    target = cfg.get("target_minutes", 30)
    avg = (sum(r["total"] for r in period_rows) / len(period_rows)) if period_rows else None
    ontime = (sum(1 for r in period_rows
                  if r["time_spent_min"] and r["time_spent_min"] <= target)
              / len(period_rows)) if period_rows else None
    planned = len(cfg.get("session_days", E.WEEKDAY_NAMES))
    if period == "month":
        planned = "—"

    session_lines = "\n".join(
        f"| {r['date']} | {r['track']} | {r['format']} | {r['level']} | "
        f"{r['total']} | {r['time_spent_min']}分 |" for r in sorted(period_rows,
                                                                   key=lambda r: r["date"])
    ) or "| — | — | — | — | — | 記録なし |"

    track_lines = "\n".join(
        f"| {t} | {f'{sum(per_track[t])/len(per_track[t]):.1f}' if per_track.get(t) else '—'} "
        f"| {len(per_track.get(t, []))} |" for t in E.TRACKS)

    weak_lines = "\n".join(
        f"| {w['id']} | {w['priority']} | {w['weakness']} | {w['track']} | "
        f"{w['detected']} | {w['retest_on']} | {w['retest_result']} |"
        for w in sorted(weaknesses,
                        key=lambda w: (E.PRIORITIES.index(w["priority"])
                                       if w["priority"] in E.PRIORITIES else 1),
                        reverse=True)) or "| — | — | Open弱点なし | — | — | — | — |"

    closed_lines = "\n".join(
        f"- `{w['id']}` {w['weakness']}（{w['track']}）" for w in closed_in_period[-10:]
    ) or "- なし"

    warnings = E.wip_warnings(cfg)
    warn_lines = "\n".join(f"- {w}" for w in warnings) or "- なし"

    titles = "\n".join(f"- {s['date']} [{s['track']}/{s['format']}] {s['title']}"
                       for s in sessions[:15]) or "- なし"

    queue = E.read_text(E.PROMOTION_QUEUE).strip() or "（空）"

    body = f"""# {title}

> **自動生成。手で編集しないこと。** レビューの講評はChatGPTが書きます。
> ここにあるのは数字だけです。ここに無い事実を推測で補わないでください。

- 期間: {start.isoformat()} – {end.isoformat()}
- 生成: {today.isoformat()}

## 集計

| Metric | Value |
|---|---|
| 実施セッション | {len(period_rows)}回（予定 {planned}） |
| 平均スコア | {f'{avg:.1f}' if avg is not None else '—'} |
| {target}分内完了率 | {f'{ontime:.0%}' if ontime is not None else '—'} |
| Open弱点 | {len(weaknesses)}件（High {sum(1 for w in weaknesses if w['priority'] == 'High')}件） |
| 通算セッション | {len(rows)}回 |

## この期間のセッション

| Date | Track | Format | Level | Score | Time |
|---|---|---|---|---|---|
{session_lines}

## Track別

| Track | Avg（期間内） | 回数 |
|---|---|---|
{track_lines}

## Open弱点（全件）

| ID | Priority | Weakness | Track | Detected | Retest on | 直近結果 |
|---|---|---|---|---|---|---|
{weak_lines}

## Closed済みの弱点（直近10件）

{closed_lines}

## WIP上限の警告

{warn_lines}

## 直近の出題タイトル

{titles}

## Bank昇格キュー

{queue}

## 難易度の判定（決定済み。ChatGPTは変更してはならない）

- **base_level: {new_level}**
- 理由: {level_reason}

---

<!-- eos:review period={period} label={label} base_level={new_level} -->
"""

    E.write_text(out_file, body)

    if period == "week" and new_level != cfg.get("base_level"):
        cfg["base_level"] = new_level
        cfg.pop("level", None)
        E.save_config(cfg)

    print(json.dumps({
        "period": period, "label": label, "path": os.path.relpath(out_file, E.ROOT),
        "sessions": len(period_rows), "avg": round(avg, 1) if avg is not None else None,
        "base_level": new_level, "level_reason": level_reason,
        "commit_message": f"chore(review): {period} facts {label}",
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
