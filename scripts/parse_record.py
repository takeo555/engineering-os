#!/usr/bin/env python3
"""Issueに貼られた「記録ブロック」を読み、Repositoryへ反映する。

使い方: parse_record.py <issue_body.txt> [--out result.json]

設計方針
- **絶対に落ちない。** フォーマットが崩れていても、原文は必ず 04-sessions/inbox/ に残す
- 表記ゆれ（Track名、点数の「18/30」表記、優先度の「高」など）は寄せて受け入れる
- 必須なのは date と Track だけ。他は欠けても既定値で埋める
"""
import json
import os
import re
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import eoslib as E  # noqa: E402

AXES = ["correctness", "completeness", "reasoning", "practicality", "clarity"]
MAXES = {"correctness": 30, "completeness": 25, "reasoning": 25,
         "practicality": 10, "clarity": 10}
LABELS = {
    "correctness": "Correctness（正確さ）",
    "completeness": "Completeness（網羅性）",
    "reasoning": "Reasoning（根拠の言語化）",
    "practicality": "Practicality（実務妥当性）",
    "clarity": "Clarity（説明の明快さ）",
}
SECTION_TITLES = {
    1: "1. Problem", 2: "2. My answer", 3: "3. Review", 4: "4. Score",
    5: "5. Weaknesses", 6: "6. What I learned", 7: "7. Next",
}

FENCE = re.compile(r"```[a-zA-Z0-9_-]*\n(.*?)```", re.S)
FM = re.compile(r"^\s*---\s*\n(.*?)\n---\s*(?:\n|$)", re.S)
HEADING = re.compile(r"^##\s+(\d)\s*[.．]?\s*(.*)$", re.M)


# ---------------------------------------------------------------- 取り出し

def extract_record(raw):
    """Issue本文から frontmatter 付きの記録ブロックを取り出す。

    戻り値: (frontmatter dict, body markdown) / 見つからなければ (None, None)
    """
    candidates = [m.group(1) for m in FENCE.finditer(raw)] + [raw]
    for c in candidates:
        c = c.strip("\n")
        # コードブロックの前に説明文が付いていても拾えるよう、--- の直前まで捨てる
        idx = c.find("---")
        if idx > 0 and not c[:idx].strip().startswith("#"):
            c = c[idx:]
        m = FM.match(c)
        if m:
            return parse_frontmatter(m.group(1)), c[m.end():].strip("\n")
    return None, None


def parse_frontmatter(text):
    """`key: value` の平坦なfrontmatterを読む。ネストは受け付けない。"""
    out = {}
    for line in text.splitlines():
        line = line.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        k = k.strip().lstrip("-").strip().lower().replace(" ", "_")
        v = v.strip().strip('"').strip("'")
        if k:
            out[k] = v
    return out


def split_sections(body):
    """`## 1. Problem` のような見出しで本文を分ける。"""
    out, marks = {}, list(HEADING.finditer(body))
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(body)
        out[int(m.group(1))] = body[m.end():end].strip("\n").strip()
    if not marks and body.strip():
        out[2] = body.strip()  # 見出しが無ければ全文を回答として扱う
    return out


def collect_indexed(fm, prefix):
    """weakness_1, weakness_2 ... を順に集める。"""
    keys = sorted((k for k in fm if re.fullmatch(prefix + r"_?\d*", k)),
                  key=lambda k: E.parse_int(k, 0))
    return [fm[k] for k in keys if fm[k].strip() and fm[k].strip() not in ("-", "—", "なし")]


def parse_retests(value):
    """`W001=passed, W002=failed(note)` などを読む。"""
    out = []
    for chunk in re.split(r"[,\n、]+", value or ""):
        chunk = chunk.strip()
        if not chunk:
            continue
        m = re.match(r"(W\d+)\s*[=:：>\-\s]+\s*([^\s(（]+)\s*[(（]?([^)）]*)", chunk, re.I)
        if not m:
            continue
        out.append({"id": m.group(1).upper(), "result": m.group(2), "note": m.group(3).strip()})
    return out


SHORT_TRACK_TOKENS = {"db", "api", "http", "web", "arch", "architecture",
                      "network", "infra", "rest", "database"}


def _looks_like_track(part):
    """弱点の本文をTrack名と取り違えないよう、厳しめに判定する。"""
    if any(E._normalize(part) == E._normalize(t) for t in E.TRACKS):
        return True
    return part.strip().lower() in SHORT_TRACK_TOKENS


def parse_weakness_items(values, default_track):
    """`High | DB / Table Design | 〜できない` を読む。順序は入れ替わってもよい。"""
    out = []
    for v in values:
        parts = [p.strip() for p in re.split(r"\s*\|\s*", v) if p.strip()]
        if not parts:
            continue
        priority, track, text = None, None, None
        for p in parts:
            if priority is None and re.fullmatch(r"(high|med|medium|low|高|中|低)", p, re.I):
                priority = E.normalize_priority(p)
            elif track is None and _looks_like_track(p):
                track = E.normalize_track(p, default_track)
            else:
                text = p if text is None else f"{text} {p}"
        if not text:
            continue
        out.append({"weakness": text, "track": track or default_track,
                    "priority": priority or "Med"})
    return out[:5]


def parse_bank_items(values):
    out = []
    for v in values:
        parts = [p.strip() for p in re.split(r"\s*\|\s*", v) if p.strip()]
        if not parts:
            continue
        bank, summary = "未定", None
        for p in parts:
            if re.fullmatch(r"(pattern|pitfall|tradeoff|term)", p, re.I):
                bank = p.lower()
            else:
                summary = p if summary is None else f"{summary} {p}"
        if summary:
            out.append({"summary": summary, "bank": bank})
    return out[:3]


# ---------------------------------------------------------------- 組み立て

def build_score_table(fm):
    lines = ["| Axis | Weight | Score | Note |", "|---|---|---|---|"]
    total = 0
    for a in AXES:
        v = max(0, min(MAXES[a], E.parse_int(fm.get(a), 0)))
        total += v
        lines.append(f"| {LABELS[a]} | {MAXES[a]} | {v}/{MAXES[a]} | {fm.get(a + '_note', '')} |")
    declared = E.parse_int(fm.get("total"), 0)
    if total == 0 and declared:
        total = max(0, min(100, declared))
        lines.append(f"| **Total**（軸別の内訳なし） | **100** | **{total}/100** | |")
    else:
        lines.append(f"| **Total** | **100** | **{total}/100** | |")
    return "\n".join(lines), total


def append_promotion_queue(d, items):
    if not items:
        return
    text = E.read_text(E.PROMOTION_QUEUE)
    if not text:
        text = ("# Bank Promotion Queue\n\n"
                "| Date | Candidate | Target bank | Status |\n|---|---|---|---|\n")
    rows = "".join(f"| {d} | {it['summary']} | {it['bank']} | Pending |\n" for it in items)
    E.write_text(E.PROMOTION_QUEUE, text.rstrip("\n") + "\n" + rows)


def save_to_inbox(raw, reason):
    stamp = E.today_jst().isoformat()
    path = os.path.join(E.INBOX_DIR, f"{stamp}-unparsed.md")
    n = 2
    while os.path.exists(path):
        path = os.path.join(E.INBOX_DIR, f"{stamp}-unparsed-{n}.md")
        n += 1
    E.write_text(path, f"<!-- 取り込めなかった記録: {reason} -->\n\n{raw}\n")
    return path


# ---------------------------------------------------------------- session

def handle_session(fm, body, raw, cfg):
    d = fm.get("date") or E.today_jst().isoformat()
    try:
        the_date = date.fromisoformat(d[:10])
    except ValueError:
        the_date = E.today_jst()
    d = the_date.isoformat()

    track = E.normalize_track(fm.get("track"), "")
    if not track:
        return {"ok": False, "reason": "track が読めない",
                "inbox": save_to_inbox(raw, "track が読めない")}

    fmt = E.normalize_format(fm.get("format"))
    level = E.normalize_level(fm.get("level"), cfg.get("base_level", "L2"))
    minutes = max(0, min(600, E.parse_int(fm.get("time_spent_min") or fm.get("minutes"), 0)))
    title = (fm.get("title") or "").strip() or "（タイトルなし）"

    sections = split_sections(body)
    score_table, total = build_score_table(fm)

    # 1) 再テストの合否（先に反映する。passed は Closed へ）
    closed, failed, unknown = E.apply_retests(
        parse_retests(fm.get("retest") or fm.get("retests")), d, cfg)

    # 2) 新規の弱点（類似は重複登録せず優先度を上げる）
    incoming = parse_weakness_items(collect_indexed(fm, "weakness"), track)
    for w in incoming:
        w["detected"] = d
    added, bumped = E.register_weaknesses(incoming, cfg)

    weak_lines = ["| ID | Weakness | Track | Priority | Retest on | 種別 |",
                  "|---|---|---|---|---|---|"]
    for w in added:
        weak_lines.append(f"| {w['id']} | {w['weakness']} | {w['track']} | "
                          f"{w['priority']} | {w['retest_on']} | 新規 |")
    for w in bumped:
        weak_lines.append(f"| {w['id']} | {w['weakness']} | {w['track']} | "
                          f"{w['priority']} | {w['retest_on']} | 再発（優先度を1段上げた） |")
    if not added and not bumped:
        weak_lines.append("| — | 新規の弱点なし | — | — | — | — |")

    retest_lines = [f"- `{w['id']}` **合格 → Closed** — {w['weakness']}" for w in closed]
    retest_lines += [f"- `{w['id']}` **不合格** — {w['weakness']}"
                     f"（priority {w['priority']} / 再テスト {w['retest_on']}）" for w in failed]
    retest_lines += [f"- `{wid}` 該当する弱点が見つからなかった（IDを確認）" for wid in unknown]

    banks = parse_bank_items(collect_indexed(fm, "bank"))
    append_promotion_queue(d, banks)

    next_md = (
        "- Bank昇格候補: "
        + (", ".join(f"{it['summary']}（{it['bank']}）" for it in banks) or "—")
        + f"\n- 次回の出題に反映する点: {fm.get('next_hint', '—') or '—'}"
        + "\n- 再テスト予定: "
        + (", ".join(f"{w['id']} → {w['retest_on']}" for w in added + bumped + failed) or "—"))

    sections[4] = score_table
    sections[5] = ("### 再テスト結果\n\n" + ("\n".join(retest_lines) or "- 今日は再テスト対象なし")
                   + "\n\n### 今日の弱点\n\n" + "\n".join(weak_lines))
    sections[7] = next_md

    out = [
        "---",
        f"date: {d}",
        f"track: {track}",
        f"format: {fmt}",
        f"level: {level}",
        f"weakness_targets: [{', '.join(w['id'] for w in closed + failed)}]",
        f"time_spent_min: {minutes}",
        f"score_total: {total}",
        "status: done",
        "---",
        "",
        f"# {d} — {title}",
        "",
    ]
    for n in sorted(SECTION_TITLES):
        out.append(f"## {SECTION_TITLES[n]}")
        out.append("")
        out.append(sections.get(n, "（記載なし）"))
        out.append("")

    path = E.session_path(the_date)
    overwritten = os.path.exists(path)
    E.write_text(path, "\n".join(out).rstrip() + "\n")

    if not any(r["date"] == d for r in E.read_scores()):
        E.append_score({
            "date": d, "track": track, "format": fmt, "level": level,
            **{a: max(0, min(MAXES[a], E.parse_int(fm.get(a), 0))) for a in AXES},
            "total": total, "time_spent_min": minutes,
        })
        score_note = ""
    else:
        score_note = "（同じ日付の行が既にあるため scores.csv には追記しなかった）"

    warnings = E.wip_warnings(cfg)
    status = E.update_status(cfg)

    comment = "\n".join([
        f"### 記録しました — {d}",
        "",
        f"**{total}/100** ・ {track} / {fmt} / {level} ・ {minutes}分 {score_note}",
        "",
        "| 反映 | 内容 |",
        "|---|---|",
        f"| クローズした弱点 | {', '.join(w['id'] for w in closed) or '—'} |",
        f"| 不合格（再テスト前倒し） | {', '.join(w['id'] for w in failed) or '—'} |",
        f"| 新規の弱点 | {', '.join(w['id'] for w in added) or '—'} |",
        f"| 再発（優先度+1） | {', '.join(w['id'] for w in bumped) or '—'} |",
        f"| Bank昇格候補 | {len(banks)}件 |",
        f"| 連続実施 | {status['streak']}日 |",
        "",
        f"記録: [`{os.path.relpath(path, E.ROOT)}`]({os.path.relpath(path, E.ROOT)})",
    ])
    if unknown:
        comment += f"\n\n> 不明な弱点ID: {', '.join(unknown)}"
    if warnings:
        comment += "\n\n> " + "\n> ".join(warnings)

    return {
        "ok": True, "type": "session", "date": d, "path": path, "total": total,
        "closed": [w["id"] for w in closed], "failed": [w["id"] for w in failed],
        "added": [w["id"] for w in added], "bumped": [w["id"] for w in bumped],
        "unknown_retest_ids": unknown, "overwritten": overwritten,
        "warnings": warnings, "comment": comment,
        "commit_message": f"feat(session): record {d} {track} ({total}/100)",
    }


# ---------------------------------------------------------------- weekly

FOCUS_HEADING = re.compile(r"^##\s*NEXT[ _]CURRENT[ _]FOCUS\s*$", re.M | re.I)


def handle_weekly(fm, body, cfg):
    today = E.today_jst()
    iso_year, iso_week, _ = today.isocalendar()
    week = (fm.get("week") or f"{iso_year}-W{iso_week:02d}").strip()

    focus_updated = False
    m = FOCUS_HEADING.search(body)
    if m:
        review, focus = body[:m.start()].rstrip(), body[m.end():].strip()
        if focus:
            E.write_text(E.CURRENT_FOCUS, focus.rstrip() + "\n")
            focus_updated = True
    else:
        review = body

    path = os.path.join(E.ROOT, "06-reviews", "weekly", f"{week}.md")
    E.write_text(path, f"---\nweek: {week}\ncreated: {today.isoformat()}\n---\n\n"
                       + review.strip() + "\n")

    new_level = E.normalize_level(fm.get("base_level"), "")
    level_note = "—"
    if new_level and new_level != cfg.get("base_level"):
        cfg["base_level"] = new_level
        cfg.pop("level", None)
        E.save_config(cfg)
        level_note = f"base_level を {new_level} に更新"

    status = E.update_status(cfg)
    comment = "\n".join([
        f"### 週次レビューを記録しました — {week}",
        "",
        f"- レビュー: `{os.path.relpath(path, E.ROOT)}`",
        f"- CURRENT_FOCUS.md: {'更新した' if focus_updated else '変更なし'}",
        f"- 難易度: {level_note}",
        f"- Open弱点: {status['open_weaknesses']}件",
    ])
    return {"ok": True, "type": "weekly", "week": week, "path": path,
            "focus_updated": focus_updated, "comment": comment,
            "commit_message": f"chore(review): weekly {week}"}


# ---------------------------------------------------------------- main

def main():
    if len(sys.argv) < 2:
        raise SystemExit("使い方: parse_record.py <issue_body.txt> [--out result.json]")
    raw = E.read_text(sys.argv[1])
    out_path = None
    if "--out" in sys.argv:
        out_path = sys.argv[sys.argv.index("--out") + 1]

    cfg = E.load_config()
    fm, body = extract_record(raw)

    if fm is None:
        result = {
            "ok": False,
            "reason": "`---` で挟んだヘッダが見つからない",
            "inbox": save_to_inbox(raw, "frontmatter が無い"),
            "comment": ("### 取り込めませんでした\n\n"
                        "`---` で挟んだヘッダ行（date / track / format / level / 各軸の点数）が"
                        "見つかりませんでした。原文は `04-sessions/inbox/` に保存したので、"
                        "ChatGPTに「記録ブロックをテンプレート通りに出し直して」と言って、"
                        "このIssueを編集して貼り直してください。\n\n"
                        "見本は [`prompts/record-block.md`](prompts/record-block.md) にあります。"),
        }
    elif (fm.get("type") or "session").strip().lower().startswith("week"):
        result = handle_weekly(fm, body, cfg)
    else:
        result = handle_session(fm, body, raw, cfg)
        if not result.get("ok"):
            result["comment"] = (
                "### 取り込めませんでした\n\n"
                f"理由: {result.get('reason')}\n\n"
                "原文は `04-sessions/inbox/` に保存しました。ヘッダの `track:` を"
                "4Trackのいずれかにして、このIssueを編集し直してください。")

    print(json.dumps(result, ensure_ascii=False))
    if out_path:
        E.write_text(out_path, json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
