"""CONTEXT → 出題 → 採点 → 記録 の状態を一貫して扱う。

試験官側の手順の正本は prompts/ だが、同じ判定をコードでも固定する。
Importer（parse_record.py）とテストがこれを呼ぶ。
"""
import os
import re

import eoslib as E

AXES = ["correctness", "completeness", "reasoning", "practicality", "clarity"]

REQUIRED_CONTEXT_FIELDS = [
    "date", "track", "format", "level",
    "answer_environment", "expected_time",
    "is_session_day", "record_status",
    "target_weaknesses", "recent_history",
    "drill_plan", "phase",
]

REQUIRED_RECORD_KEYS = [
    "date", "track", "format", "level", "title", "time_spent_min",
    *AXES, "weakness_1",
]

# Drill のヘッダは「必須だが、欠けても記録全体は弾かない」。
# 試験官が1行書き忘れただけで、その日の Design 採点・レビュー・弱点まで失うほうが損失が大きい。
# 欠落は parse_record.py の警告としてIssueコメントに出す。
DRILL_RECORD_KEYS = ["drill_ai", "drill_lang", "drill_network", "drill_misses"]

# 日次の状態遷移。Drill を飛ばして design_out へ進めない
STATES = ["idle", "drill_out", "drill_answered", "design_out", "design_answered",
          "reviewed", "recorded", "posted"]

# ``` の情報文字列（text / yaml / id="..."）を無視して中身だけ取る
FENCE = re.compile(r"```[^\n]*\n(.*?)```", re.S)
FM = re.compile(r"^\s*---\s*\n(.*?)\n---\s*(?:\n|$)", re.S)
TABLE_ROW = re.compile(r"^\|\s*([^|]+?)\s*\|\s*([^|]*?)\s*\|$")

ASSIGN_LABELS = {
    "日付": "date",
    "track": "track",
    "format": "format",
    "level": "level",
    "回答環境": "answer_environment",
    "想定所要時間": "expected_time",
    "今日はセッション日か": "is_session_day",
    "今日の記録": "record_status",
}


def _strip_md(value):
    value = (value or "").strip()
    value = re.sub(r"\*\*([^*]+)\*\*", r"\1", value)
    value = value.replace("`", "")
    return value.strip()


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


def extract_record(raw):
    """Issue本文から frontmatter 付きの記録ブロックを取り出す。

    ``` / ```text / ```yaml / ``` id="..." を許容する。
    戻り値: (frontmatter dict, body markdown) / 見つからなければ (None, None)
    """
    candidates = [m.group(1) for m in FENCE.finditer(raw or "")] + [raw or ""]
    for c in candidates:
        c = c.strip("\n")
        idx = c.find("---")
        if idx > 0 and not c[:idx].strip().startswith("#"):
            c = c[idx:]
        m = FM.match(c)
        if m:
            return parse_frontmatter(m.group(1)), c[m.end():].strip("\n")
    return None, None


def parse_context(text):
    """CONTEXT.md から今日の割り当てを辞書で返す。欠けは空文字 / 空リスト。"""
    ctx = {k: "" for k in REQUIRED_CONTEXT_FIELDS}
    ctx["target_weaknesses"] = []
    ctx["recent_history"] = []
    ctx["drill_plan"] = []
    if not text or not text.strip():
        return ctx

    in_assign = False
    for line in text.splitlines():
        if line.startswith("## "):
            # 見出しは「今日の Design 割り当て」。Drill 題材枠の表は読まない
            in_assign = "割り当て" in line and "Drill" not in line
            continue
        if not in_assign:
            continue
        m = TABLE_ROW.match(line.strip())
        if not m:
            continue
        label, value = _strip_md(m.group(1)), _strip_md(m.group(2))
        if label in ("項目", "---") or set(label) <= {"-", ":"}:
            continue
        key = ASSIGN_LABELS.get(label.lower(), ASSIGN_LABELS.get(label))
        if key:
            ctx[key] = value

    dm = re.search(r"(\d{4}-\d{2}-\d{2})", ctx.get("date") or "")
    if dm:
        ctx["date"] = dm.group(1)

    ctx["track"] = E.normalize_track(ctx.get("track"), ctx.get("track") or "")
    ctx["format"] = E.normalize_format(ctx.get("format"), ctx.get("format") or "")
    if ctx.get("level"):
        ctx["level"] = E.normalize_level(ctx["level"], ctx["level"])

    weak_sec = _section(text, "今日狙う弱点")
    ctx["target_weaknesses"] = _parse_target_weaknesses(weak_sec)
    hist_sec = _section(text, "直近の出題履歴")
    ctx["recent_history"] = _parse_history(hist_sec)
    ctx["drill_plan"] = _parse_drill_plan(_section(text, "Drill 題材枠"))
    ctx["phase"] = _parse_phase(_section(text, "今日のフェーズ"))
    ctx["_raw"] = text
    return ctx


def _section(text, heading_contains):
    chunks = re.split(r"^##\s+", text, flags=re.M)
    for ch in chunks:
        first, _, rest = ch.partition("\n")
        if heading_contains in first:
            nxt = rest.split("\n## ")[0]
            return nxt
    return ""


def _parse_target_weaknesses(sec):
    ids = []
    if not sec.strip():
        return ids
    if re.search(r"なし", sec) and not re.search(r"`W\d+`", sec, re.I):
        return ids
    for m in re.finditer(r"`?(W\d+)`?", sec, re.I):
        wid = m.group(1).upper()
        if wid not in ids:
            ids.append(wid)
    return ids


DRILL_ROW_LABELS = {"ai": "AI", "言語": "Coding Language", "ネットワーク": "Network"}


def _parse_drill_plan(sec):
    """「今日の Drill 題材枠」の表を [{'category','count','slots','miss'}] で返す。"""
    rows = []
    for line in sec.splitlines():
        st = line.strip()
        if not st.startswith("|"):
            continue
        cells = [c.strip() for c in st.strip("|").split("|")]
        if len(cells) < 4:
            continue
        if cells[0] in ("カテゴリ", "---") or set(cells[0]) <= {"-", ":"}:
            continue
        category = DRILL_ROW_LABELS.get(cells[0].lower(),
                                        DRILL_ROW_LABELS.get(cells[0], cells[0]))
        rows.append({
            "category": category,
            "count": E.parse_int(cells[1], 0),
            "slots": [x.strip() for x in cells[2].split("；") if x.strip()],
            "miss": not cells[3].startswith("なし"),
        })
    return rows


def _parse_phase(sec):
    m = re.search(r"Phase\s*(\d+)", sec or "")
    return m.group(0) if m else ""


def _parse_history(sec):
    rows = []
    for line in sec.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) < 5:
            continue
        if cells[0] in ("Date", "---") or set(cells[0]) <= {"-", ":"}:
            continue
        if cells[0] == "—":
            continue
        rows.append({
            "date": cells[0], "track": cells[1], "format": cells[2],
            "level": cells[3], "title": cells[4],
        })
    return rows


def context_errors(ctx):
    """CONTEXTが出題に使えない理由。空なら使える。"""
    if not ctx:
        return ["CONTEXT.md が空"]
    errors = []
    labels = {
        "date": "date（日付）",
        "track": "track",
        "format": "format",
        "level": "level",
        "answer_environment": "answer environment（回答環境）",
        "expected_time": "expected time（想定所要時間）",
        "is_session_day": "today session status（今日はセッション日か）",
        "record_status": "today session status（今日の記録）",
    }
    for key, label in labels.items():
        if not (ctx.get(key) or "").strip():
            errors.append(f"{label} が取得できない")
    if not ctx.get("drill_plan"):
        errors.append("drill 題材枠（AI / 言語 / ネットワークの表）が取得できない")
    if not (ctx.get("phase") or "").strip():
        errors.append("phase（今日のフェーズ）が取得できない")
    if "target_weaknesses" not in ctx:
        errors.append("today's target weakness が取得できない")
    if "recent_history" not in ctx:
        errors.append("recent history が取得できない")
    # 履歴セクション自体が無い（キー未セット）と、初回で0件なのは別
    if ctx.get("recent_history") is None:
        errors.append("recent history が取得できない")
    return errors


def record_already_saved(ctx):
    status = ctx.get("record_status") or ""
    return "保存済み" in status


def should_generate_question(ctx):
    """出題してよいか。不可なら (False, reason)。"""
    errs = context_errors(ctx)
    if errs:
        return False, "CONTEXTが不正: " + " / ".join(errs)
    if record_already_saved(ctx):
        return False, "今日の分は終わっています"
    return True, ""


# ---------------------------------------------------------------- 状態遷移

# Drill → Design の順を固定する。前の状態からしか進めない
_NEXT_STATE = {
    "idle": "drill_out",
    "drill_out": "drill_answered",
    "drill_answered": "design_out",
    "design_out": "design_answered",
    "design_answered": "reviewed",
    "reviewed": "recorded",
    "recorded": "posted",
    "posted": None,
}


def next_state(state):
    """その状態の次に来るべき状態。終端なら None。"""
    return _NEXT_STATE.get(state)


def can_advance(state, target):
    """state から target へ進んでよいか。不可なら (False, reason)。"""
    if state not in STATES:
        return False, f"未知の状態: {state}"
    if target not in STATES:
        return False, f"未知の状態: {target}"
    expected = next_state(state)
    if target == expected:
        return True, ""
    if STATES.index(target) <= STATES.index(state):
        return False, f"{state} から {target} へは戻れない"
    skipped = STATES[STATES.index(state) + 1:STATES.index(target)]
    if "drill_out" in skipped or "drill_answered" in skipped:
        return False, ("Drill を飛ばして Design に進めない"
                       f"（飛ばした: {', '.join(skipped)}）")
    return False, f"{state} の次は {expected}。{target} へは飛べない"


def drill_is_complete(drill_plan, drill_scores):
    """CONTEXT の題材枠どおりにドリルを消化したか。不足があれば理由のリスト。"""
    errors = []
    by_key = {"AI": "ai", "Coding Language": "lang", "Network": "network"}
    for row in drill_plan or []:
        key = by_key.get(row["category"])
        if key is None:
            continue
        got = (drill_scores or {}).get(key)
        if not got:
            errors.append(f"{row['category']} の正答率が無い")
            continue
        correct, total = got
        if row["count"] and total != row["count"]:
            errors.append(
                f"{row['category']} の出題数が CONTEXT と違う"
                f"（CONTEXT {row['count']}問 / 記録 {total}問）")
        if correct > total:
            errors.append(f"{row['category']} の正答数が出題数を超えている")
    return errors


def check_design_can_start(state, drill_plan, drill_scores):
    """Design 出題に進んでよいか。Drill が未消化なら (False, reason)。"""
    if state not in ("drill_answered",):
        return False, f"Drill が終わっていない（現在: {state}）"
    errors = drill_is_complete(drill_plan, drill_scores)
    if errors:
        return False, "Drill が CONTEXT どおりに消化されていない: " + " / ".join(errors)
    return True, ""


def session_from_context(ctx, title="", problem=""):
    """出題時点で凍結するセッション。採点・記録はこれを正本にする。"""
    return {
        "date": ctx.get("date", ""),
        "track": ctx.get("track", ""),
        "format": ctx.get("format", ""),
        "level": ctx.get("level", ""),
        "title": title,
        "problem": problem,
        "target_weaknesses": list(ctx.get("target_weaknesses") or []),
        "answer_environment": ctx.get("answer_environment", ""),
        "expected_time": ctx.get("expected_time", ""),
        "drill_plan": list(ctx.get("drill_plan") or []),
        "drill_scores": {},
        "drill_misses": [],
        "phase": ctx.get("phase", ""),
        "context": {
            "date": ctx.get("date", ""),
            "track": ctx.get("track", ""),
            "format": ctx.get("format", ""),
            "level": ctx.get("level", ""),
            "target_weaknesses": list(ctx.get("target_weaknesses") or []),
            "recent_history": list(ctx.get("recent_history") or []),
            "record_status": ctx.get("record_status", ""),
            "drill_plan": list(ctx.get("drill_plan") or []),
            "phase": ctx.get("phase", ""),
        },
    }


def check_problem_matches_session(session, problem):
    """出題メタデータがSESSIONと矛盾していればエラーリスト。"""
    errors = []
    for field in ("track", "format", "level"):
        got = problem.get(field) or ""
        exp = session.get(field) or ""
        if field == "track":
            got, exp = E.normalize_track(got, got), E.normalize_track(exp, exp)
        elif field == "format":
            got, exp = E.normalize_format(got, got), E.normalize_format(exp, exp)
        elif field == "level":
            got, exp = E.normalize_level(got, got), E.normalize_level(exp, exp)
        if got != exp:
            errors.append(f"{field} がSESSIONと不一致（出題 {got} / SESSION {exp}）")
    targets = session.get("target_weaknesses") or []
    if targets and not problem.get("surfaces_target_weakness"):
        errors.append("今日の弱点が問題設定に表面化していない")
    if problem.get("duplicates_recent_topic"):
        errors.append("最近の出題題材と重複している")
    gaps = problem.get("embedded_requirement_gaps")
    if gaps is not None and gaps != 1:
        errors.append("要件の意図的な矛盾/不足が1つではない")
    if problem.get("fits_15min") is False:
        errors.append("15分で回答可能な分量ではない")
    return errors


def check_record_matches_session(session, fm):
    """記録ヘッダが、実際に出題したSESSIONと違うならエラーリスト。"""
    if not session:
        return ["SESSIONが無い。出題時の割り当てを保持していない"]
    errors = []
    if (fm.get("date") or "")[:10] != (session.get("date") or "")[:10]:
        errors.append(
            f"date がSESSIONと不一致（record {fm.get('date')} / SESSION {session.get('date')}）")
    st = E.normalize_track(session.get("track"), "")
    rt = E.normalize_track(fm.get("track"), "")
    if st != rt:
        errors.append(f"track がSESSIONと不一致（record {rt} / SESSION {st}）")
    sf = E.normalize_format(session.get("format"), "")
    rf = E.normalize_format(fm.get("format"), "")
    if sf != rf:
        errors.append(f"format がSESSIONと不一致（record {rf} / SESSION {sf}）")
    sl = E.normalize_level(session.get("level"), "")
    rl = E.normalize_level(fm.get("level"), "")
    if sl != rl:
        errors.append(f"level がSESSIONと不一致（record {rl} / SESSION {sl}）")
    return errors


def field_is_int(value):
    if value is None or str(value).strip() == "":
        return False
    return re.search(r"-?\d+", str(value)) is not None


def validate_session_record(fm):
    """必須キーと整数。不足キーのリストを返す（空ならOK）。"""
    if not fm:
        return list(REQUIRED_RECORD_KEYS)
    missing = []
    for k in REQUIRED_RECORD_KEYS:
        v = (fm.get(k) or "").strip()
        if not v or v in ("-", "—", "なし"):
            missing.append(k)
    if "time_spent_min" not in missing and not field_is_int(fm.get("time_spent_min")):
        missing.append("time_spent_min（整数ではない）")
    for a in AXES:
        if a not in missing and not field_is_int(fm.get(a)):
            missing.append(f"{a}（整数ではない）")
    return missing


def missing_keys_message(missing):
    return "不足しているキー: " + ", ".join(f"`{k}`" for k in missing)


def grading_materials_ready(anchors_text, manual_text):
    """anchors.md と examiner-manual.md が採点に使えるか。"""
    reasons = []
    if not (anchors_text or "").strip():
        reasons.append("anchors.md が取得できない")
    else:
        low = anchors_text
        if not (re.search(r"50\s*点", low) and re.search(r"70\s*点", low)
                and re.search(r"85\s*点", low)):
            reasons.append("anchors.md に 50点・70点・85点の見本が無い")
    if not (manual_text or "").strip():
        reasons.append("examiner-manual.md が取得できない")
    return (not reasons), reasons


def load_grading_materials(anchors_path, manual_path):
    anchors = E.read_text(anchors_path) if os.path.exists(anchors_path) else ""
    manual = E.read_text(manual_path) if os.path.exists(manual_path) else ""
    ok, reasons = grading_materials_ready(anchors, manual)
    return ok, reasons, anchors, manual


def my_answer_is_verbatim(original, recorded):
    """記録の My answer が原文か（前後空白のみ許容）。"""
    if original is None or recorded is None:
        return False
    return original.strip("\n") == recorded.strip("\n")
