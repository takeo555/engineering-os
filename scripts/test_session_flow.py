#!/usr/bin/env python3
"""CONTEXT → 出題 → 記録 の事故を固定するテスト。"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import session_flow as S  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def sample_context(*, track="DB / Table Design", fmt="Review", level="L1",
                   weakness="W001", saved=False, history=True):
    record = "保存済み。2問目は出さない" if saved else "未保存"
    weak = (f"- `{weakness}` [High] 論理削除と一意制約の衝突に気づけない（期限 2026-09-08）"
            if weakness else "- なし（今日は新しい題材でよい）")
    hist = """| Date | Track | Format | Level | Title |
|---|---|---|---|---|
| 2026-09-03 | DB / Table Design | Design | L2 | 会議室予約のダブルブッキングを構造で防ぐ |
""" if history else """| Date | Track | Format | Level | Title |
|---|---|---|---|---|
| — | — | — | — | 履歴なし（初回） |
"""
    return f"""# CONTEXT — 2026-09-08（Tue）

## 今日の割り当て（この通りに出題すること）

| 項目 | 値 |
|---|---|
| 日付 | 2026-09-08（Tue） |
| Track | **{track}** |
| Format | **{fmt}** |
| Level | **{level}** |
| 回答環境 | キーボード想定 |
| 想定所要時間 | 30分 |
| 今日はセッション日か | はい |
| 今日の記録 | {record} |

## 今日狙う弱点（問題文に弱点名を書かず、必ず表面化させること）

{weak}

## 直近の出題履歴（題材の重複を避ける。同じ題材は10回空ける）

{hist}
"""


VALID_FM = {
    "type": "session",
    "date": "2026-09-08",
    "track": "DB / Table Design",
    "format": "Review",
    "level": "L1",
    "title": "与えられた予約スキーマの問題を指摘する",
    "time_spent_min": "20",
    "correctness": "12",
    "completeness": "14",
    "reasoning": "11",
    "practicality": "5",
    "clarity": "6",
    "weakness_1": "High | DB / Table Design | 論理削除と一意制約の衝突に気づけない",
    "next_hint": "次は制約の衝突を問う",
}

RECORD_BODY = """
## 1. Problem

与えられたスキーマをレビューせよ。

## 2. My answer

handler層でバリデーションする。

## 3. Review

ok

## 6. What I learned

1. 制約で防ぐ
"""


def fence(info, fm=None, body=RECORD_BODY):
    fm = fm or VALID_FM
    header = "\n".join(f"{k}: {v}" for k, v in fm.items())
    inner = f"---\n{header}\n---\n{body}"
    return f"```{info}\n{inner}\n```"


class TestARejectWrongAssignment(unittest.TestCase):
    def test_context_db_review_l1_but_problem_is_arch_design_l2(self):
        ctx = S.parse_context(sample_context())
        ok, reason = S.should_generate_question(ctx)
        self.assertTrue(ok, reason)
        session = S.session_from_context(ctx, title="x")
        self.assertEqual(session["track"], "DB / Table Design")
        self.assertEqual(session["format"], "Review")
        self.assertEqual(session["level"], "L1")
        errors = S.check_problem_matches_session(session, {
            "track": "Layered Architecture",
            "format": "Design",
            "level": "L2",
            "surfaces_target_weakness": True,
            "duplicates_recent_topic": False,
            "embedded_requirement_gaps": 1,
            "fits_30min": True,
        })
        self.assertTrue(errors)
        self.assertTrue(any("track" in e for e in errors))
        self.assertTrue(any("format" in e for e in errors))
        self.assertTrue(any("level" in e for e in errors))


class TestBSavedNoQuestion(unittest.TestCase):
    def test_record_already_saved_does_not_generate(self):
        ctx = S.parse_context(sample_context(saved=True))
        ok, reason = S.should_generate_question(ctx)
        self.assertFalse(ok)
        self.assertIn("今日の分は終わっています", reason)


class TestCTextFence(unittest.TestCase):
    def test_text_fence_is_recognized(self):
        fm, body = S.extract_record(fence("text"))
        self.assertIsNotNone(fm)
        self.assertEqual(fm["track"], "DB / Table Design")
        self.assertEqual(fm["time_spent_min"], "20")
        self.assertIn("My answer", body)


class TestDIdFence(unittest.TestCase):
    def test_fence_with_id_attribute_is_recognized(self):
        fm, body = S.extract_record(fence(' id="xxx"'))
        self.assertIsNotNone(fm)
        self.assertEqual(fm["type"], "session")
        self.assertEqual(fm["weakness_1"].split("|")[0].strip(), "High")
        self.assertIn("handler層", body)


class TestEMissingMinutes(unittest.TestCase):
    def test_missing_time_spent_min_is_rejected(self):
        fm = dict(VALID_FM)
        del fm["time_spent_min"]
        missing = S.validate_session_record(fm)
        self.assertIn("time_spent_min", missing)


class TestFMissingAxis(unittest.TestCase):
    def test_missing_one_axis_is_rejected(self):
        fm = dict(VALID_FM)
        del fm["reasoning"]
        missing = S.validate_session_record(fm)
        self.assertIn("reasoning", missing)


class TestGMissingWeakness(unittest.TestCase):
    def test_missing_weakness_1_is_rejected(self):
        fm = dict(VALID_FM)
        del fm["weakness_1"]
        missing = S.validate_session_record(fm)
        self.assertIn("weakness_1", missing)


class TestHAnchorsRequired(unittest.TestCase):
    def test_missing_anchors_blocks_grading(self):
        manual = os.path.join(ROOT, "prompts", "examiner-manual.md")
        ok, reasons, _, _ = S.load_grading_materials(
            "/tmp/eos-missing-anchors-does-not-exist.md", manual)
        self.assertFalse(ok)
        self.assertTrue(any("anchors.md" in r for r in reasons))

    def test_present_anchors_and_manual_are_ready(self):
        ok, reasons, _, _ = S.load_grading_materials(
            os.path.join(ROOT, "07-scorecard", "anchors.md"),
            os.path.join(ROOT, "prompts", "examiner-manual.md"))
        self.assertTrue(ok, reasons)


class TestIRecordTrackMismatch(unittest.TestCase):
    def test_record_track_different_from_session_is_rejected(self):
        ctx = S.parse_context(sample_context())
        session = S.session_from_context(ctx, title="x", problem="問題文")
        fm = dict(VALID_FM)
        fm["track"] = "Layered Architecture"
        errors = S.check_record_matches_session(session, fm)
        self.assertTrue(errors)
        self.assertTrue(any("track" in e for e in errors))


class TestVerbatimAnswer(unittest.TestCase):
    def test_my_answer_must_match_original(self):
        original = "handler層でバリデーションする。\nusecaseは触らない。"
        self.assertTrue(S.my_answer_is_verbatim(original, original))
        self.assertFalse(S.my_answer_is_verbatim(
            original, "handler層でバリデーションする（要約）。"))


class TestContextParse(unittest.TestCase):
    def test_required_fields_roundtrip(self):
        ctx = S.parse_context(sample_context())
        self.assertEqual(S.context_errors(ctx), [])
        self.assertEqual(ctx["date"], "2026-09-08")
        self.assertEqual(ctx["track"], "DB / Table Design")
        self.assertEqual(ctx["format"], "Review")
        self.assertEqual(ctx["level"], "L1")
        self.assertEqual(ctx["answer_environment"], "キーボード想定")
        self.assertEqual(ctx["expected_time"], "30分")
        self.assertEqual(ctx["target_weaknesses"], ["W001"])
        self.assertTrue(ctx["recent_history"])


if __name__ == "__main__":
    unittest.main()
