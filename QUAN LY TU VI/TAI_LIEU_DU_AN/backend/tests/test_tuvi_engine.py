"""Loop 2A evidence + §11.2 golden sample tests."""

from __future__ import annotations

import hashlib
import json
import os
from datetime import date

from app.schemas.reading import NormalizedBirthInput
from app.services.final_message_builder import build_messenger_outbound
from app.services.tuvi_calendar_engine import lunar_to_solar, resolve_solar_for_chart
from app.services.tuvi_can_chi_engine import day_pillar_from_solar
from app.services.tuvi_core_engine import build_chart_dict


def test_anchor_1911_01_01_tan_mui() -> None:
    """SoT: 1911-01-01 → Tân Mùi (index 7 trong chu kỳ 60)."""
    p = day_pillar_from_solar(date(1911, 1, 1))
    assert p.stem == "tan"
    assert p.branch == "mui"


def test_no_day_shift_hour_does_not_change_day_pillar() -> None:
    """Rule COO §7 / rulebook no-day-shift: cùng ngày dương solar, giờ 23:xx không được
    đẩy sang ngày hôm sau. Test qua full-path build_chart_dict với birth_hour=23 vs
    birth_hour=0 trên cùng ngày 2000-06-15; can_chi.day.pair phải giống nhau.
    QA repro: 2000-06-15 ở 23:30, 23:45, 00:30 → can_chi.day.pair = giap_thin.
    """
    def _day_pair(hour: int) -> str:
        n = NormalizedBirthInput(
            full_name="no-day-shift-test",
            birth_day=15,
            birth_month=6,
            birth_year=2000,
            birth_hour=hour,
            birth_minute=30,
            gender="male",
            calendar_type="solar",
            is_leap_lunar_month=False,
            timezone="Asia/Bangkok",
            rule_set_id="tuvi_mvp_v1",
        )
        return build_chart_dict(n)["can_chi"]["day"]["pair"]

    pair_at_23 = _day_pair(23)
    pair_at_0 = _day_pair(0)
    assert pair_at_23 == pair_at_0, (
        f"no-day-shift FAIL: hour=23 → {pair_at_23}, hour=0 → {pair_at_0}"
    )
    assert pair_at_23 == "giap_thin", (
        f"day pair mismatch for 2000-06-15: expected giap_thin, got {pair_at_23}"
    )


def test_lunar_input_path_converts_to_solar_before_domain() -> None:
    """Lunar + is_leap_lunar_month -> solar_for_domain trong conversion."""
    solar, lunar, conv = resolve_solar_for_chart(
        calendar_type="lunar",
        birth_year=1990,
        birth_month=5,
        birth_day=1,
        is_leap_lunar_month=False,
    )
    assert conv["calendar_type"] == "lunar"
    assert "solar_for_domain" in conv
    assert solar.year >= 1990
    assert lunar.lunar_month == 5


def test_lunar_roundtrip_solar_present() -> None:
    lp = __import__(
        "app.services.tuvi_calendar_engine", fromlist=["LunarDateParts"]
    ).LunarDateParts(1990, 5, 1, False)
    s = lunar_to_solar(lp)
    assert s.year > 1900


def test_determinism_same_normalized_same_chart_hash() -> None:
    n = NormalizedBirthInput(
        full_name="Test User",
        birth_day=15,
        birth_month=6,
        birth_year=1990,
        birth_hour=14,
        birth_minute=30,
        gender="male",
        calendar_type="solar",
        is_leap_lunar_month=False,
        timezone="Asia/Bangkok",
        rule_set_id="tuvi_mvp_v1",
    )
    a = build_chart_dict(n)
    b = build_chart_dict(n)
    # input_normalized is model — compare serializable subset
    def digest(d: dict) -> str:
        payload = json.dumps(
            {"houses": d["houses"], "major_fortunes": d["major_fortunes"], "menh": d["menh"]},
            sort_keys=True,
            ensure_ascii=False,
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    assert digest(a) == digest(b)


def test_final_message_order() -> None:
    """Thứ tự outbound; giá trị bank/CEO lấy từ env (conftest autouse)."""
    bank = os.environ["MESSENGER_PART_2_BANK_BLOCK"]
    ceo = os.environ["MESSENGER_PART_3_CEO_NOTE"]
    out = build_messenger_outbound(reading_body="BODY")
    i_body = out.index("BODY")
    i_bank = out.index(bank)
    i_ceo = out.index(ceo)
    assert i_body < i_bank < i_ceo


# ---------------------------------------------------------------------------
# §11.2 Golden sample tests — reference: tuvi.vn screenshots
# ---------------------------------------------------------------------------


def _stars_in_house(chart: dict, house_code: str) -> list[str]:
    for h in chart["houses"]:
        if h["house_code"] == house_code:
            return [s["code"] for s in h["main_stars"]]
    return []


def _build_sample_a() -> NormalizedBirthInput:
    return NormalizedBirthInput(
        full_name="aaa",
        birth_day=1,
        birth_month=1,
        birth_year=1911,
        birth_hour=12,
        birth_minute=30,
        gender="male",
        calendar_type="solar",
        is_leap_lunar_month=False,
        timezone="Asia/Bangkok",
        rule_set_id="tuvi_mvp_v1",
    )


def test_golden_sample_a_anchor_1911() -> None:
    """Golden sample A — 'aaa', solar 1911-01-01, 12:30, male.
    Source: goden_sample1.png from tuvi.vn.
    lunar-vn (Ho Ngoc Duc, UTC+7) converts 1911-01-01 → lunar 1910/12/2,
    which is correct per Vietnamese calendar (new moon on Dec 31, 1910 local time).
    """
    chart = build_chart_dict(_build_sample_a())
    meta = chart["chart_metadata"]
    cc = chart["can_chi"]

    assert meta["menh_branch"] == "mui", f"menh_branch={meta['menh_branch']}"
    assert meta["than_branch"] == "mui", f"than_branch={meta['than_branch']}"
    assert meta["cuc"] == "moc_3", f"cuc={meta['cuc']}"
    assert cc["day"]["pair"] == "tan_mui", f"day pair={cc['day']['pair']}"

    expected: dict[str, list[str]] = {
        "menh":      ["thien_tuong"],
        "phu_mau":   ["thien_dong", "thien_luong"],
        "phuc_duc":  ["vu_khuc", "that_sat"],
        "dien_trach":["thai_duong"],
        "quan_loc":  [],
        "no_boc":    ["thien_co"],
        "thien_di":  ["tu_vi", "pha_quan"],
        "tat_ach":   [],
        "tai_bach":  ["thien_phu"],
        "tu_tuc":    ["thai_am"],
        "phu_the":   ["liem_trinh", "tham_lang"],
        "huynh_de":  ["cu_mon"],
    }
    for house_code, exp_stars in expected.items():
        got = sorted(_stars_in_house(chart, house_code))
        assert got == sorted(exp_stars), (
            f"house '{house_code}': expected {sorted(exp_stars)}, got {got}"
        )


def test_golden_sample_b_nguyen_manh_linh_1994() -> None:
    """Golden sample B — nguyễn mạnh linh, âm 15/12/1994, 12:30, male.
    Source: goden_sample_2.png from tuvi.vn.
    Thổ Ngũ Cục, Mệnh+Thân tại Mùi, can chi ngày Bính Ngọ (solar 1995-01-15).
    """
    n = NormalizedBirthInput(
        full_name="nguyen manh linh",
        birth_day=15,
        birth_month=12,
        birth_year=1994,
        birth_hour=12,
        birth_minute=30,
        gender="male",
        calendar_type="lunar",
        is_leap_lunar_month=False,
        timezone="Asia/Bangkok",
        rule_set_id="tuvi_mvp_v1",
    )
    chart = build_chart_dict(n)
    meta = chart["chart_metadata"]
    cc = chart["can_chi"]

    # Mệnh / Thân / Cục
    assert meta["menh_branch"] == "mui", f"menh_branch={meta['menh_branch']}"
    assert meta["than_branch"] == "mui", f"than_branch={meta['than_branch']}"
    assert meta["cuc"] == "tho_5", f"cuc={meta['cuc']}"

    # Solar 1995-01-15 → Bính Ngọ
    assert cc["day"]["pair"] == "binh_ngo", f"day pair={cc['day']['pair']}"

    # 14 chính tinh
    expected: dict[str, list[str]] = {
        "menh":      [],
        "phu_mau":   ["liem_trinh"],
        "phuc_duc":  [],
        "dien_trach":["pha_quan"],
        "quan_loc":  ["thien_dong"],
        "no_boc":    ["vu_khuc", "thien_phu"],
        "thien_di":  ["thai_duong", "thai_am"],
        "tat_ach":   ["tham_lang"],
        "tai_bach":  ["thien_co", "cu_mon"],
        "tu_tuc":    ["tu_vi", "thien_tuong"],
        "phu_the":   ["thien_luong"],
        "huynh_de":  ["that_sat"],
    }
    for house_code, exp_stars in expected.items():
        got = sorted(_stars_in_house(chart, house_code))
        assert got == sorted(exp_stars), (
            f"house '{house_code}': expected {sorted(exp_stars)}, got {got}"
        )
