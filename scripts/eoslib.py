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

DESIGN_TRACKS = [
    "Layered Architecture",
    "DB / Table Design",
    "Web / API / HTTP",
    "Code Review",
]

DRILL_CATEGORIES = [
    "AI",
    "Coding Language",
    "Network",
]

# 2026-09 の二層構造改修で Design から外した旧Track。
# 新しい出題には使わないが、過去の記録（scores.csv / 04-sessions）を読むために残す。
LEGACY_TRACKS = [
    "Network / Infra",
    "Coding / Go / Next.js",
    "AI / LLM",
]

# 後方互換のため TRACKS も残すが、以下は非推奨。使うのは DESIGN_TRACKS
TRACKS = DESIGN_TRACKS

# 正規化のときだけ旧Track名も受け入れる（過去記録を落とさないため）
KNOWN_TRACKS = DESIGN_TRACKS + LEGACY_TRACKS

FORMATS = ["Design", "Review", "Debug", "Explain"]
DRILL_FORMAT = "Recall"  # Drill専用
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
TODAY_FILE = os.path.join(ROOT, "TODAY.md")
WEEKLY_CONTEXT_FILE = os.path.join(ROOT, "WEEKLY_CONTEXT.md")
PROMOTION_QUEUE = os.path.join(ROOT, "03-banks", "promotion-queue.md")
INBOX_DIR = os.path.join(ROOT, "04-sessions", "inbox")
DRILL_MISSES = os.path.join(ROOT, "05-failures", "drill-misses.md")
ROADMAP = os.path.join(ROOT, "ROADMAP.md")


def today_jst():
    return datetime.now(JST).date()


def now_jst_str():
    """TODAY.md の鮮度判定に使う。生成が朝の着火より遅れていないかを目で見る。"""
    return datetime.now(JST).strftime("%Y-%m-%d %H:%M")


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
# 試験官が返す文字列は日によって揺れる。落とさずに寄せる。

TRACK_ALIASES = {
    "DB / Table Design": ["db", "database", "table", "テーブル", "データベース", "dbdesign"],
    "Layered Architecture": ["arch", "architecture", "layered", "アーキテクチャ", "レイヤ"],
    "Web / API / HTTP": ["api", "http", "web", "rest", "エーピーアイ"],
    "Code Review": ["codereview", "code review", "review", "コードレビュー", "レビュー"],
    "Network / Infra": ["network", "infra", "ネットワーク", "インフラ", "infrastructure"],
    "Coding / Go / Next.js": ["go", "golang", "next", "nextjs", "next.js", "coding",
                             "コーディング", "実装"],
    "AI / LLM": ["ai", "llm", "生成ai", "chatgpt", "人工知能"],
}


def normalize_track(value, default=""):
    raw = (value or "").strip()
    if not raw:
        return default
    for t in KNOWN_TRACKS:
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
                "reasoning", "practicality", "clarity", "total", "time_spent_min",
                "drill_ai_correct", "drill_ai_total",
                "drill_lang_correct", "drill_lang_total",
                "drill_network_correct", "drill_network_total"]

# 5軸・合計・所要時間だけを整数として読む。drill 列は空欄を空欄のまま残す
NUMERIC_SCORE_COLS = SCORE_HEADER[4:11]
DRILL_SCORE_COLS = SCORE_HEADER[11:]


def read_scores():
    """scores.csv を新しい順のリストで返す。"""
    if not os.path.exists(SCORES_CSV):
        return []
    with open(SCORES_CSV, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        for k in NUMERIC_SCORE_COLS:
            try:
                r[k] = int(float(r.get(k) or 0))
            except (TypeError, ValueError):
                r[k] = 0
        for k in DRILL_SCORE_COLS:
            raw = (r.get(k) or "").strip() if isinstance(r.get(k), str) else r.get(k)
            if raw in (None, ""):
                r[k] = None  # ドリル導入前の行。0件と混ぜない
                continue
            try:
                r[k] = int(float(raw))
            except (TypeError, ValueError):
                r[k] = None
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


def design_target_minutes(cfg):
    """Design 1問の想定時間。旧キー `target_minutes` からの移行を許容する。"""
    return cfg.get("target_minutes_design", cfg.get("target_minutes", 15))


def drill_rates(rows, window=14):
    """直近window件のカテゴリ別ドリル正答率を {key: (correct, total)} で返す。"""
    out = {}
    for key in ("ai", "lang", "network"):
        c = sum(r[f"drill_{key}_correct"] for r in rows[:window]
                if r.get(f"drill_{key}_correct") is not None)
        t = sum(r[f"drill_{key}_total"] for r in rows[:window]
                if r.get(f"drill_{key}_total"))
        if t:
            out[key] = (c, t)
    return out


def ontime_rate(rows, target_minutes=15, window=10):
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


# ---------------------------------------------------------------- drill

# セパレータに素の `x` は使わない。`Next.js` の x に食われるため
DRILL_MISS_LINE = re.compile(
    r"^[-*]\s*(?P<cat>.+?)\s*(?:×|✕|\sx\s)\s*(?P<sub>[^:：\n]+?)\s*[:：]\s*(?P<theme>.+)$")
DATE_SECTION = re.compile(r"^##\s*(\d{4}-\d{2}-\d{2})\s*$")
LANG_IN_CAT = re.compile(r"[(（]\s*([^)）]+?)\s*[)）]")

# drill-misses.md に書き出すときの表示名（DRILL_CATEGORIES の逆引き）
DRILL_CATEGORY_LABELS = {
    "AI": "AI",
    "Coding Language": "言語",
    "Network": "ネットワーク",
}

# 自動追記はこの行より下だけに書く。上は形式の説明とサンプル
APPEND_MARKER = "<!-- 以下、日次記録の追記が続く"

# drill-misses.md に書かれるカテゴリ表記 → DRILL_CATEGORIES
DRILL_CATEGORY_ALIASES = {
    "AI": ["ai", "エーアイ", "生成ai"],
    "Coding Language": ["言語", "language", "lang", "コーディング言語",
                        "go", "next", "python", "terraform"],
    "Network": ["ネットワーク", "network", "net", "インフラ"],
}


def normalize_drill_category(value, default=""):
    """「言語(Go)」「ネットワーク」「AI」を DRILL_CATEGORIES のいずれかに寄せる。"""
    raw = unicodedata.normalize("NFKC", (value or "")).strip()
    if not raw:
        return default
    for c in DRILL_CATEGORIES:
        if _normalize(raw) == _normalize(c):
            return c
    low = raw.lower()
    for cat, keys in DRILL_CATEGORY_ALIASES.items():
        if any(k in low for k in keys):
            return cat
    return default or raw


def parse_drill_misses(text=None):
    """drill-misses.md 全体を [{'date','category','language','subtopic','theme'}] で返す。"""
    text = read_text(DRILL_MISSES) if text is None else text
    out, current, in_fence = [], None, False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue  # 形式の説明に置いたサンプルを実データとして拾わない
        m = DATE_SECTION.match(line.strip())
        if m:
            current = m.group(1)
            continue
        if current is None:
            continue  # 見出し前の説明文は無視する
        m = DRILL_MISS_LINE.match(line.strip())
        if not m:
            continue
        cat_raw = m.group("cat").strip()
        lang = LANG_IN_CAT.search(cat_raw)
        out.append({
            "date": current,
            "category": normalize_drill_category(cat_raw, cat_raw),
            "language": lang.group(1).strip() if lang else "",
            "subtopic": m.group("sub").strip(),
            "theme": m.group("theme").strip(),
        })
    return out


def load_recent_drill_misses(days=3, today=None):
    """直近N日分の間違いを {category: [{'subtopic','theme','date','language'}]} で返す。

    N日は「今日を含めた直近N日」ではなく「今日より前のN日分」。
    翌日のドリルに類題を混ぜるための入力なので、当日分も含める（同日に貼り直した場合に効く）。
    """
    today = today or today_jst()
    floor = (today - timedelta(days=days)).isoformat()
    out = {c: [] for c in DRILL_CATEGORIES}
    for m in parse_drill_misses():
        if m["date"] < floor:
            continue
        out.setdefault(m["category"], []).append(m)
    for v in out.values():
        v.sort(key=lambda m: m["date"], reverse=True)
    return out


def append_drill_misses(on_date, misses):
    """drill-misses.md にその日の間違いを追記する。

    同じ日付のセクションがあれば末尾に追記、なければ新規セクションを作る。
    再取り込み（Issueコメントの編集）では、その日のセクションを丸ごと入れ替える。
    戻り値: 書き込んだ件数
    """
    if not misses:
        return 0
    lines = []
    for m in misses:
        cat = DRILL_CATEGORY_LABELS.get(m.get("category"), m.get("category") or "")
        lang = m.get("language") or ""
        label = f"{cat}({lang})" if lang and "(" not in cat else cat
        answer = (m.get("answer") or "").strip()
        tail = f"（正解: {answer}）" if answer else ""
        lines.append(f"- {label} × {m.get('subtopic','')}: {m.get('theme','')}{tail}")

    text = read_text(DRILL_MISSES)
    if not text.strip():
        text = "# Drill Misses\n\n" + APPEND_MARKER + "\n"
    body = text.rstrip("\n").splitlines()

    # 追記領域の開始位置。マーカーが無ければファイル全体を見る
    head_end = 0
    for i, line in enumerate(body):
        if APPEND_MARKER in line:
            head_end = i + 1
            break
    head, tail_body = body[:head_end], body[head_end:]

    # 既存の同じ日付セクションを探し、あればその範囲を差し替える。
    # 形式の説明に置いたサンプル（```で囲まれた部分）は触らない
    start = end = None
    in_fence = False
    for i, line in enumerate(tail_body):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = DATE_SECTION.match(line.strip())
        if m and m.group(1) == on_date:
            start = i
        elif start is not None and end is None and line.strip().startswith("## "):
            end = i
    if start is not None:
        end = end if end is not None else len(tail_body)
        tail_body = (tail_body[:start] + [f"## {on_date}", ""] + lines + [""]
                     + tail_body[end:])
    else:
        tail_body += ["", f"## {on_date}", ""] + lines

    write_text(DRILL_MISSES, "\n".join(head + tail_body).rstrip("\n") + "\n")
    return len(lines)


# ---------------------------------------------------------------- roadmap

PHASE_MARKER = re.compile(
    r"<!--\s*eos:phase\s+id=(?P<id>\d+)\s+name=(?P<name>\S+)\s+"
    r"start=(?P<start>\d{4}-\d{2}-\d{2})\s+end=(?P<end>\d{4}-\d{2}-\d{2})\s*-->")

# 「**AI drill 題材**:」に続く箇条書きを拾う
AI_TOPIC_HEAD = re.compile(r"\*\*AI drill 題材\*\*\s*[:：]\s*(.*)$")


def parse_phases(text=None):
    """ROADMAP.md の機械可読マーカーを [{'phase','name','start','end'}] で返す。"""
    text = read_text(ROADMAP) if text is None else text
    out = []
    for m in PHASE_MARKER.finditer(text):
        out.append({
            "phase": int(m.group("id")),
            "name": m.group("name"),
            "start": m.group("start"),
            "end": m.group("end"),
        })
    out.sort(key=lambda p: p["start"])
    return out


def _phase_ai_topics(text, phase_id):
    """`## Phase N:` セクションから AI drill 題材の箇条書きを拾う。"""
    chunks = re.split(r"^##\s+", text, flags=re.M)
    for ch in chunks:
        if not re.match(rf"Phase\s*{phase_id}\s*[:：]", ch.strip()):
            continue
        topics, collecting = [], False
        for line in ch.splitlines():
            m = AI_TOPIC_HEAD.search(line)
            if m:
                collecting = True
                inline = m.group(1).strip()
                if inline:
                    topics.append(inline)
                continue
            if not collecting:
                continue
            st = line.strip()
            if st.startswith(("- ", "* ")) and line.startswith(("  ", "\t")):
                topics.append(st[2:].strip())
            elif st.startswith(("- ", "* ", "#")) or not st:
                if st.startswith(("- ", "* ", "#")):
                    break
        return topics
    return []


def current_phase(today=None):
    """ROADMAP.md を読み、今日が Phase 1/2/3 のどれか、および題材の指針を返す。

    どのフェーズにも入らない日（最初のフェーズより前 / 最後のフェーズより後）は、
    いちばん近いフェーズを返し `in_range: False` を立てる。出題は止めない。
    """
    today = (today or today_jst())
    key = today.isoformat() if hasattr(today, "isoformat") else str(today)
    text = read_text(ROADMAP)
    phases = parse_phases(text)
    if not phases:
        return {"phase": None, "name": "", "start": "", "end": "",
                "ai_topics": [], "in_range": False}
    chosen, in_range = None, False
    for p in phases:
        if p["start"] <= key <= p["end"]:
            chosen, in_range = p, True
            break
    if chosen is None:
        chosen = phases[0] if key < phases[0]["start"] else phases[-1]
    return {**chosen, "in_range": in_range,
            "ai_topics": _phase_ai_topics(text, chosen["phase"])}


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
    target = design_target_minutes(cfg)
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
    drills = drill_rates(rows, 14)
    phase = current_phase(today)
    phase_label = ("Phase {}（{}）".format(phase["phase"], phase["name"])
                   if phase["phase"] else "—")
    if phase["phase"] and not phase["in_range"]:
        phase_label += " ※ROADMAP.md の期間外。月次レビューでフェーズを更新すること"

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
        f"| 直近5回の平均スコア（Design） | {f'{avg5:.1f}' if avg5 is not None else '—'} |",
        f"| {target}分内完了率（直近10回） | {f'{rate:.0%}' if rate is not None else '—'} |",
        f"| Base level | {cfg.get('base_level', 'L2')} |",
        f"| Phase | {phase_label} |",
        f"| Open弱点 | {len(weak)}件（High {sum(1 for w in weak if w['priority'] == 'High')}件） |",
        f"| 再テスト期限切れ | {len(due)}件 |",
        "",
        "## Design Track別平均（直近20回）",
        "",
        "| Track | Avg |",
        "|---|---|",
    ]
    shown = list(DESIGN_TRACKS) + [t for t in LEGACY_TRACKS if t in tavg]
    for t in shown:
        v = tavg.get(t)
        suffix = "（旧Track・参考）" if t in LEGACY_TRACKS else ""
        lines.append(f"| {t}{suffix} | {f'{v:.1f}' if v is not None else '—'} |")

    lines += ["", "## Drill 正答率（直近14回）", "",
              "| Category | Rate |", "|---|---|"]
    for key, label in (("ai", "AI"), ("lang", "言語"), ("network", "ネットワーク")):
        if key in drills:
            c, t = drills[key]
            lines.append(f"| {label} | {c}/{t}（{c / t:.0%}） |")
        else:
            lines.append(f"| {label} | — |")

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
              "- 試験官が毎朝読む入り口: [`CONTEXT.md`](CONTEXT.md)",
              "- 今週の重点: [`CURRENT_FOCUS.md`](CURRENT_FOCUS.md)",
              "- 弱点一覧: [`05-failures/weakness-log.md`](05-failures/weakness-log.md)",
              "- ドリルの間違い: [`05-failures/drill-misses.md`](05-failures/drill-misses.md)",
              "- 学習フェーズ: [`ROADMAP.md`](ROADMAP.md)",
              ""]
    write_text(STATUS_FILE, "\n".join(lines))
    return {"streak": streak, "open_weaknesses": len(weak), "due": len(due)}
