"""Engineering OS の共有ロジック。標準ライブラリのみを使う。"""
import csv
import difflib
import json
import os
import re
import unicodedata
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JST = timezone(timedelta(hours=9))

TRACKS = [
    "DB / Table Design",
    "Layered Architecture",
    "Web / API / HTTP",
    "Network / Infra",
]
FORMATS = ["Design", "Review", "Debug", "Explain"]
LEVELS = ["L1", "L2", "L3", "L4"]
PRIORITIES = ["Low", "Med", "High"]
WEEKDAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

SESSIONS_DIR = os.path.join(ROOT, "04-sessions", "daily")
SCORES_CSV = os.path.join(ROOT, "07-scorecard", "scores.csv")
WEAKNESS_LOG = os.path.join(ROOT, "05-failures", "weakness-log.md")
CURRENT_FOCUS = os.path.join(ROOT, "CURRENT_FOCUS.md")
CONFIG = os.path.join(ROOT, "eos.config.json")
STATUS_FILE = os.path.join(ROOT, "STATUS.md")
CONTEXT_FILE = os.path.join(ROOT, "CONTEXT.md")
WEEKLY_CONTEXT_FILE = os.path.join(ROOT, "WEEKLY_CONTEXT.md")
PROMOTION_QUEUE = os.path.join(ROOT, "03-banks", "promotion-queue.md")
INBOX_DIR = os.path.join(ROOT, "04-sessions", "inbox")


def today_jst():
    return datetime.now(JST).date()


def load_config():
    with open(CONFIG, encoding="utf-8") as f:
        cfg = json.load(f)
    # 旧キー `level` からの移行を許容する
    if "base_level" not in cfg and "level" in cfg:
        cfg["base_level"] = cfg["level"]
    return cfg


def save_config(cfg):
    write_text(CONFIG, json.dumps(cfg, ensure_ascii=False, indent=2) + "\n")


def read_text(path, default=""):
    if not os.path.exists(path):
        return default
    with open(path, encoding="utf-8") as f:
        return f.read()


def write_text(path, content):
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def session_path(d):
    return os.path.join(SESSIONS_DIR, f"{d.year:04d}", f"{d.isoformat()}.md")


def shift_level(level, delta):
    idx = LEVELS.index(level) if level in LEVELS else 1
    return LEVELS[max(0, min(len(LEVELS) - 1, idx + delta))]


def shift_priority(priority, delta):
    idx = PRIORITIES.index(priority) if priority in PRIORITIES else 1
    return PRIORITIES[max(0, min(len(PRIORITIES) - 1, idx + delta))]


# ------------------------------------------------- 表記ゆれの吸収
# ChatGPTが返す文字列は日によって揺れる。落とさずに寄せる。

TRACK_ALIASES = {
    "DB / Table Design": ["db", "database", "table", "テーブル", "データベース", "dbdesign"],
    "Layered Architecture": ["arch", "architecture", "layered", "アーキテクチャ", "レイヤ"],
    "Web / API / HTTP": ["api", "http", "web", "rest", "エーピーアイ"],
    "Network / Infra": ["network", "infra", "ネットワーク", "インフラ", "infrastructure"],
}


def normalize_track(value, default=""):
    raw = (value or "").strip()
    if not raw:
        return default
    for t in TRACKS:
        if _normalize(raw) == _normalize(t):
            return t
    low = unicodedata.normalize("NFKC", raw).lower()
    for t, keys in TRACK_ALIASES.items():
        if any(k in low for k in keys):
            return t
    return default or raw


def normalize_format(value, default="Design"):
    low = unicodedata.normalize("NFKC", (value or "")).strip().lower()
    for f in FORMATS:
        if low.startswith(f.lower()):
            return f
    return default


def normalize_level(value, default="L2"):
    m = re.search(r"l\s*([1-4])", unicodedata.normalize("NFKC", (value or "")).lower())
    return f"L{m.group(1)}" if m else default


def normalize_priority(value, default="Med"):
    low = unicodedata.normalize("NFKC", (value or "")).strip().lower()
    if low.startswith("h") or "高" in low:
        return "High"
    if low.startswith("l") or "低" in low:
        return "Low"
    if low.startswith("m") or "中" in low:
        return "Med"
    return default


def parse_int(value, default=0):
    """「32」「32分」「18/30」「約32」から先頭の整数を拾う。"""
    m = re.search(r"-?\d+", str(value if value is not None else ""))
    return int(m.group(0)) if m else default


# ---------------------------------------------------------------- scores

SCORE_HEADER = ["date", "track", "format", "level", "correctness", "completeness",
                "reasoning", "practicality", "clarity", "total", "time_spent_min"]


def read_scores():
    """scores.csv を新しい順のリストで返す。"""
    if not os.path.exists(SCORES_CSV):
        return []
    with open(SCORES_CSV, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        for k in SCORE_HEADER[4:]:
            try:
                r[k] = int(float(r.get(k) or 0))
            except (TypeError, ValueError):
                r[k] = 0
    rows.sort(key=lambda r: r.get("date", ""), reverse=True)
    return rows


def append_score(row):
    exists = os.path.exists(SCORES_CSV)
    os.makedirs(os.path.dirname(SCORES_CSV), exist_ok=True)
    with open(SCORES_CSV, "a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=SCORE_HEADER)
        if not exists:
            w.writeheader()
        w.writerow({k: row.get(k, "") for k in SCORE_HEADER})


def upsert_score(row):
    """同じ日付の行があれば置き換える。

    Issueのコメントを直して貼り直したとき（＝再実行）に、古い点数が残らないようにする。
    """
    date_key = row.get("date")
    existing = []
    if os.path.exists(SCORES_CSV):
        with open(SCORES_CSV, encoding="utf-8", newline="") as f:
            existing = [r for r in csv.DictReader(f) if r.get("date") != date_key]
    os.makedirs(os.path.dirname(SCORES_CSV), exist_ok=True)
    with open(SCORES_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=SCORE_HEADER)
        w.writeheader()
        for r in sorted(existing, key=lambda r: r.get("date", "")):
            w.writerow({k: r.get(k, "") for k in SCORE_HEADER})
        w.writerow({k: row.get(k, "") for k in SCORE_HEADER})


def track_averages(rows, window=15):
    buckets = defaultdict(list)
    for r in rows[:window]:
        buckets[r.get("track", "")].append(r["total"])
    return {t: sum(v) / len(v) for t, v in buckets.items() if v}


def moving_avg(rows, n=5):
    vals = [r["total"] for r in rows[:n]]
    return sum(vals) / len(vals) if vals else None


def ontime_rate(rows, target_minutes=30, window=10):
    vals = [r["time_spent_min"] for r in rows[:window] if r["time_spent_min"]]
    if not vals:
        return None
    return sum(1 for v in vals if v <= target_minutes) / len(vals)


# ---------------------------------------------------------------- weaknesses

WEAK_ROW = re.compile(r"^\|\s*(W\d+)\s*\|")
OPEN_COLS = 8


def _normalize(text):
    text = unicodedata.normalize("NFKC", text or "").lower()
    return re.sub(r"[\s、。，．・:：/（）()「」\-—–_]", "", text)


def _split_log(text):
    """(header_lines, open_lines, closed_lines) に分ける。"""
    lines = text.splitlines()
    closed_at = len(lines)
    for i, line in enumerate(lines):
        if line.strip().startswith("## Closed"):
            closed_at = i
            break
    return lines[:closed_at], lines[closed_at:]


def parse_weaknesses(include_closed=False):
    """Open セクションの弱点を辞書リストで返す。"""
    open_part, closed_part = _split_log(read_text(WEAKNESS_LOG))
    out = []
    for line in open_part:
        s = line.strip()
        if not WEAK_ROW.match(s):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) < OPEN_COLS:
            continue
        out.append({
            "id": cells[0], "weakness": cells[1], "track": cells[2],
            "priority": cells[3], "status": cells[4], "detected": cells[5],
            "retest_on": cells[6], "retest_result": cells[7],
        })
    if include_closed:
        for line in closed_part:
            s = line.strip()
            if not WEAK_ROW.match(s):
                continue
            cells = [c.strip() for c in s.strip("|").split("|")]
            if len(cells) < 5:
                continue
            out.append({
                "id": cells[0], "weakness": cells[1], "track": cells[2],
                "priority": "—", "status": "Closed", "detected": "",
                "retest_on": "—", "retest_result": cells[4],
            })
    return out


def _render_open_row(w):
    return (f"| {w['id']} | {w['weakness']} | {w.get('track','')} | "
            f"{w.get('priority','Med')} | {w.get('status','Open')} | "
            f"{w.get('detected','')} | {w.get('retest_on','—')} | "
            f"{w.get('retest_result','—')} |")


def _write_log(open_rows, open_part, closed_part):
    """Openテーブルを open_rows で置き換えて書き戻す。"""
    head, tail, first_row = [], [], None
    for i, line in enumerate(open_part):
        if WEAK_ROW.match(line.strip()):
            if first_row is None:
                first_row = i
        elif first_row is not None:
            tail = open_part[i:]
            break
    if first_row is None:
        # 行が1つも無い場合は区切り線の直後に入れる
        for i, line in enumerate(open_part):
            if line.strip().startswith("|---"):
                first_row = i + 1
                tail = open_part[i + 1:]
                break
        if first_row is None:
            return False
    head = open_part[:first_row]
    body = [_render_open_row(w) for w in open_rows]
    write_text(WEAKNESS_LOG, "\n".join(head + body + tail + closed_part).rstrip() + "\n")
    return True


def find_similar_weakness(text, candidates, threshold=0.82):
    """既存のOpen弱点と重複していれば、その弱点を返す。"""
    norm = _normalize(text)
    if not norm:
        return None
    best, best_ratio = None, 0.0
    for c in candidates:
        ratio = difflib.SequenceMatcher(None, norm, _normalize(c["weakness"])).ratio()
        if ratio > best_ratio:
            best, best_ratio = c, ratio
    return best if best_ratio >= threshold else None


def register_weaknesses(items, cfg=None):
    """弱点を登録する。重複はpriorityを1段上げて再テスト日を前倒しする。

    戻り値: (added, bumped)
    """
    cfg = cfg or load_config()
    wcfg = cfg.get("weakness", {})
    threshold = wcfg.get("dedup_similarity", 0.82)
    retest_days = wcfg.get("retest_days", {"High": 5, "Med": 9, "Low": 14})

    open_part, closed_part = _split_log(read_text(WEAKNESS_LOG))
    rows = parse_weaknesses()
    nums = [int(w["id"][1:]) for w in parse_weaknesses(include_closed=True)
            if w["id"][1:].isdigit()]
    next_num = max(nums) + 1 if nums else 1

    added, bumped = [], []
    for it in items:
        text = (it.get("weakness") or "").strip()
        if not text:
            continue
        dup = find_similar_weakness(text, rows, threshold)
        if dup:
            dup["priority"] = shift_priority(dup["priority"], 1)
            base = it.get("detected") or today_jst().isoformat()
            days = retest_days.get(dup["priority"], 9)
            dup["retest_on"] = (date.fromisoformat(base) + timedelta(days=days)).isoformat()
            dup["retest_result"] = f"再発 {base}"
            bumped.append(dup)
            continue
        wid = f"W{next_num:03d}"
        next_num += 1
        priority = it.get("priority") if it.get("priority") in PRIORITIES else "Med"
        detected = it.get("detected") or today_jst().isoformat()
        retest_on = it.get("retest_on") or (
            date.fromisoformat(detected) +
            timedelta(days=retest_days.get(priority, 9))).isoformat()
        row = {"id": wid, "weakness": text, "track": it.get("track", ""),
               "priority": priority, "status": "Open", "detected": detected,
               "retest_on": retest_on, "retest_result": "—"}
        rows.append(row)
        added.append(row)

    _write_log(rows, open_part, closed_part)
    return added, bumped


def apply_retests(retests, on_date, cfg=None):
    """再テスト結果を反映する。passed→Closed、failed→priority+1 かつ再テスト前倒し。

    戻り値: (closed, failed, unknown_ids)
    """
    cfg = cfg or load_config()
    wcfg = cfg.get("weakness", {})
    fail_days = wcfg.get("failed_retest_days", 3)

    open_part, closed_part = _split_log(read_text(WEAKNESS_LOG))
    rows = parse_weaknesses()
    by_id = {w["id"]: w for w in rows}

    closed, failed, unknown = [], [], []
    for r in retests or []:
        wid = (r.get("id") or "").strip().upper()
        w = by_id.get(wid)
        if not w:
            unknown.append(wid or "(no id)")
            continue
        result = (r.get("result") or "").strip().lower()
        note = (r.get("note") or "").strip()
        if result in ("passed", "pass", "ok", "closed"):
            w["_closed_evidence"] = f"{on_date} {note}".strip()
            closed.append(w)
        else:
            w["priority"] = shift_priority(w["priority"], 1)
            w["retest_on"] = (date.fromisoformat(on_date) +
                              timedelta(days=fail_days)).isoformat()
            w["retest_result"] = (f"不合格 {on_date} {note}").strip()[:60]
            failed.append(w)

    remaining = [w for w in rows if w not in closed]

    if closed:
        closed_lines = []
        for w in closed:
            closed_lines.append(
                f"| {w['id']} | {w['weakness']} | {w.get('track','')} | "
                f"{on_date} | {w.pop('_closed_evidence', on_date)} |")
        inserted = False
        new_closed = []
        for line in closed_part:
            new_closed.append(line)
            if not inserted and line.strip().startswith("|---"):
                new_closed.extend(closed_lines)
                inserted = True
        if not inserted:
            new_closed.extend([""] + closed_lines)
        # プレースホルダ行を掃除する
        new_closed = [l for l in new_closed
                      if l.strip() != "| — | — | — | — | — |"]
        closed_part = new_closed

    _write_log(remaining, open_part, closed_part)
    return closed, failed, unknown


def wip_warnings(cfg=None):
    cfg = cfg or load_config()
    limits = cfg.get("wip_limits", {})
    rows = parse_weaknesses()
    high = [w for w in rows if w["priority"] == "High"]
    out = []
    if len(high) > limits.get("open_high", 5):
        out.append(f"Open High弱点が{len(high)}件（上限{limits.get('open_high', 5)}）。"
                   "Weekly Reviewで統合か降格を行うこと")
    if len(rows) > limits.get("open_total", 15):
        out.append(f"Open弱点が{len(rows)}件（上限{limits.get('open_total', 15)}）。"
                   "Weekly Reviewで整理すること")
    return out


# ---------------------------------------------------------------- sessions

FRONTMATTER = re.compile(r"^---\n(.*?)\n---", re.S)


def parse_frontmatter(text):
    meta = {}
    m = FRONTMATTER.search(text)
    if not m:
        return meta
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta


def recent_sessions(limit=30):
    """新しい順に (date, track, format, level, title, status) を返す。"""
    out = []
    if not os.path.isdir(SESSIONS_DIR):
        return out
    for year in sorted(os.listdir(SESSIONS_DIR), reverse=True):
        ydir = os.path.join(SESSIONS_DIR, year)
        if not os.path.isdir(ydir):
            continue
        for name in sorted(os.listdir(ydir), reverse=True):
            if not name.endswith(".md"):
                continue
            text = read_text(os.path.join(ydir, name))
            meta = parse_frontmatter(text)
            tm = re.search(r"^#\s+(.*)$", text, re.M)
            out.append({
                "date": meta.get("date", name[:-3]),
                "track": meta.get("track", ""),
                "format": meta.get("format", ""),
                "level": meta.get("level", ""),
                "status": meta.get("status", ""),
                "title": tm.group(1).strip() if tm else "",
            })
            if len(out) >= limit:
                return out
    return out


# ---------------------------------------------------------------- status

def update_status(cfg=None):
    """STATUS.md を再生成する。数字を見るためだけのファイル。"""
    cfg = cfg or load_config()
    rows = read_scores()
    sessions = recent_sessions(40)
    weak = parse_weaknesses()
    target = cfg.get("target_minutes", 30)
    today = today_jst()

    done = [s for s in sessions if s.get("status") == "done"]
    streak = 0
    cursor = today
    done_dates = {s["date"] for s in done}
    session_days = cfg.get("session_days", WEEKDAY_NAMES)
    while streak < 60:
        if WEEKDAY_NAMES[cursor.weekday()] not in session_days:  # 休む日は連続を切らない
            cursor -= timedelta(days=1)
            continue
        if cursor.isoformat() in done_dates:
            streak += 1
            cursor -= timedelta(days=1)
        elif cursor == today:
            cursor -= timedelta(days=1)  # 今日はまだ猶予がある
        else:
            break

    last14 = [r for r in rows
              if r["date"] >= (today - timedelta(days=14)).isoformat()]
    avg5 = moving_avg(rows, 5)
    rate = ontime_rate(rows, target)
    tavg = track_averages(rows, 20)

    due = sorted(
        [w for w in weak
         if w["retest_on"] not in ("—", "", "-") and w["retest_on"] <= today.isoformat()],
        key=lambda w: (PRIORITIES.index(w["priority"]) if w["priority"] in PRIORITIES else 1),
        reverse=True)

    lines = [
        f"# STATUS — {today.isoformat()}",
        "",
        "> 自動生成。手で編集しても次の実行で上書きされます。",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| 連続実施 | {streak}日 |",
        f"| 直近14日のセッション | {len(last14)}回 |",
        f"| 直近5回の平均スコア | {f'{avg5:.1f}' if avg5 is not None else '—'} |",
        f"| 30分内完了率（直近10回） | {f'{rate:.0%}' if rate is not None else '—'} |",
        f"| Base level | {cfg.get('base_level', 'L2')} |",
        f"| Open弱点 | {len(weak)}件（High {sum(1 for w in weak if w['priority'] == 'High')}件） |",
        f"| 再テスト期限切れ | {len(due)}件 |",
        "",
        "## Track別平均（直近20回）",
        "",
        "| Track | Avg |",
        "|---|---|",
    ]
    for t in TRACKS:
        v = tavg.get(t)
        lines.append(f"| {t} | {f'{v:.1f}' if v is not None else '—'} |")

    lines += ["", "## 今すぐ再テストすべき弱点", ""]
    if due:
        for w in due[:5]:
            lines.append(f"- `{w['id']}` [{w['priority']}] {w['weakness']}（期限 {w['retest_on']}）")
    else:
        lines.append("- なし")

    warnings = wip_warnings(cfg)
    if warnings:
        lines += ["", "## WIP上限の警告", ""] + [f"- {w}" for w in warnings]

    lines += ["", "---", "",
              "- ChatGPTが毎朝読む入り口: [`CONTEXT.md`](CONTEXT.md)",
              "- 今週の重点: [`CURRENT_FOCUS.md`](CURRENT_FOCUS.md)",
              "- 弱点一覧: [`05-failures/weakness-log.md`](05-failures/weakness-log.md)",
              ""]
    write_text(STATUS_FILE, "\n".join(lines))
    return {"streak": streak, "open_weaknesses": len(weak), "due": len(due)}
