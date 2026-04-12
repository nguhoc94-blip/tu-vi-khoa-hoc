"""
TuVi MVP v1 core: Mệnh/Thân/Cục, 12 cung, 14 chính tinh, đại vận — deterministic, rulebook tuvi_mvp_v1.
"""

from __future__ import annotations

from datetime import date
from typing import Any

from app.schemas.reading import SCHEMA_VERSION, NormalizedBirthInput
from app.services.tuvi_calendar_engine import CALENDAR_ENGINE_VERSION, resolve_solar_for_chart
from app.services.tuvi_can_chi_engine import civil_time_to_hour_branch, compute_can_chi_bundle
from app.services.tuvi_can_chi_engine import month1_stem_on_dan
from app.services.tuvi_constants import (
    BRANCH_CODES,
    CUC_NUMBER,
    ELEMENT_TO_CUC,
    HOUSE_CODES,
    MAIN_STAR_CODES,
    NAP_AM,
    STEM_CODES,
    branch_index,
    stem_index,
)


def _mirror_branch_ty(b: int) -> int:
    return (4 - b) % 12


def _menh_and_than_branch_idx(lunar_month: int, hour_branch_code: str) -> tuple[int, int]:
    dan_idx = branch_index("dan")
    p = (dan_idx + (lunar_month - 1)) % 12
    h = branch_index(hour_branch_code)
    menh = (p - h) % 12
    than = (p + h) % 12
    return menh, than


def _am_duong_gender_group(year_stem: str, gender: str) -> str:
    ys = stem_index(year_stem)
    yang = ys in (0, 2, 4, 6, 8)
    if gender == "male":
        return "duong_nam" if yang else "am_nam"
    return "duong_nu" if yang else "am_nu"


def _stem_for_branch(year_stem_idx: int, branch_b_idx: int) -> str:
    """An can 12 cung: gốc Dần theo Ngũ Hổ Độn của năm (stem năm âm)."""
    sd = month1_stem_on_dan(year_stem_idx)
    delta = (branch_b_idx - branch_index("dan") + 12) % 12
    return STEM_CODES[(sd + delta) % 10]


def _compute_cuc(menh_stem: str, menh_branch: str) -> str:
    elem = NAP_AM.get((menh_stem, menh_branch))
    if elem is None:
        raise ValueError(f"nap am missing for menh {menh_stem} {menh_branch}")
    return ELEMENT_TO_CUC[elem]


def _tu_vi_palace_index(
    *,
    lunar_day: int,
    cuc_number: int,
    menh_branch_idx: int,
) -> int:
    """Rulebook §15.1 — palace index 0 = cung Mệnh."""
    a = (cuc_number - (lunar_day % cuc_number)) % cuc_number
    b = (lunar_day + a) // cuc_number
    dan_idx = branch_index("dan")
    pos_branch = (dan_idx + b - 1) % 12
    if a % 2 == 1:
        pos_branch = (pos_branch - a) % 12
    else:
        pos_branch = (pos_branch + a) % 12
    return (pos_branch - menh_branch_idx) % 12


def _place_main_stars(
    *,
    tu_vi_idx: int,
    menh_branch_idx: int,
) -> dict[str, int]:
    tv = tu_vi_idx
    stars: dict[str, int] = {
        "tu_vi": tv,
        "thien_co": (tv - 1) % 12,
        "thai_duong": (tv - 3) % 12,
        "vu_khuc": (tv - 4) % 12,
        "thien_dong": (tv - 5) % 12,
        "liem_trinh": (tv - 8) % 12,
    }
    b_tv = (menh_branch_idx + tv) % 12
    mirror_b = _mirror_branch_ty(b_tv)
    tp = (mirror_b - menh_branch_idx) % 12
    stars["thien_phu"] = tp
    stars["thai_am"] = (tp + 1) % 12
    stars["tham_lang"] = (tp + 2) % 12
    stars["cu_mon"] = (tp + 3) % 12
    stars["thien_tuong"] = (tp + 4) % 12
    stars["thien_luong"] = (tp + 5) % 12
    stars["that_sat"] = (tp + 6) % 12
    stars["pha_quan"] = (tp - 2) % 12
    return stars


def build_chart_dict(normalized: NormalizedBirthInput) -> dict[str, Any]:
    solar, lunar_parts, conv_extra = resolve_solar_for_chart(
        calendar_type=normalized.calendar_type,
        birth_year=normalized.birth_year,
        birth_month=normalized.birth_month,
        birth_day=normalized.birth_day,
        is_leap_lunar_month=normalized.is_leap_lunar_month,
    )
    solar_date = solar.to_date()
    hour_branch = civil_time_to_hour_branch(normalized.birth_hour, normalized.birth_minute)

    can_chi = compute_can_chi_bundle(
        solar=solar_date,
        lunar_year=lunar_parts.lunar_year,
        lunar_month=lunar_parts.lunar_month,
        birth_hour=normalized.birth_hour,
        birth_minute=normalized.birth_minute,
    )

    year_stem = can_chi["year"]["stem"]
    ys = stem_index(year_stem)
    menh_bidx, than_bidx = _menh_and_than_branch_idx(lunar_parts.lunar_month, hour_branch)
    menh_branch = BRANCH_CODES[menh_bidx]
    menh_stem = _stem_for_branch(ys, menh_bidx)
    cuc = _compute_cuc(menh_stem, menh_branch)
    cuc_n = CUC_NUMBER[cuc]
    group = _am_duong_gender_group(year_stem, normalized.gender)

    tv_idx = _tu_vi_palace_index(
        lunar_day=lunar_parts.lunar_day,
        cuc_number=cuc_n,
        menh_branch_idx=menh_bidx,
    )
    star_to_palace = _place_main_stars(tu_vi_idx=tv_idx, menh_branch_idx=menh_bidx)

    star_order = {c: i for i, c in enumerate(MAIN_STAR_CODES)}
    palace_to_stars: list[list[str]] = [[] for _ in range(12)]
    for star, pi in star_to_palace.items():
        if star not in star_order:
            raise ValueError(f"unknown main star {star}")
        palace_to_stars[pi].append(star)
    for i in range(12):
        palace_to_stars[i].sort(key=lambda c: star_order[c])

    houses: list[dict[str, Any]] = []
    for i, code in enumerate(HOUSE_CODES):
        bidx = (menh_bidx + i) % 12
        branch = BRANCH_CODES[bidx]
        houses.append(
            {
                "house_index": i + 1,
                "house_code": code,
                "branch": branch,
                "is_menh_house": i == 0,
                "is_than_house": bidx == than_bidx,
                "main_stars": [{"code": s} for s in palace_to_stars[i]],
                "secondary_stars": [],
            }
        )

    forward = group in ("duong_nam", "am_nu")
    major_fortunes: list[dict[str, Any]] = []
    for i in range(12):
        age_start = cuc_n + i * 10
        age_end = age_start + 9
        hi = (i if forward else (-i)) % 12
        h = houses[hi]
        major_fortunes.append(
            {
                "index": i,
                "age_start": age_start,
                "age_end": age_end,
                "house_index": h["house_index"],
                "house_code": h["house_code"],
                "branch": h["branch"],
                "main_stars_snapshot": list(h["main_stars"]),
            }
        )

    conversion = {
        **conv_extra,
        "calendar_engine_version": CALENDAR_ENGINE_VERSION,
    }

    chart_metadata: dict[str, Any] = {
        "engine": "tuvi_core_engine",
        "version": "1.0.0",
        "calendar_engine_version": CALENDAR_ENGINE_VERSION,
        "can_chi_engine_version": can_chi.get("can_chi_engine_version"),
        "menh_branch": menh_branch,
        "than_branch": BRANCH_CODES[than_bidx],
        "cuc": cuc,
        "am_duong_gender_group": group,
        "major_fortune_direction": "forward" if forward else "backward",
        "current_context": {
            "as_of_date": solar_date.isoformat(),
            "current_age": None,
            "current_major_fortune_index": None,
        },
    }

    validation = {
        "status": "ok",
        "checks": [
            "houses_count_12",
            "main_stars_subset_14",
            "secondary_stars_empty",
            "major_fortunes_count_12",
            "determinism_inputs_bound",
        ],
    }

    menh_block: dict[str, Any] = {
        "position_branch": menh_branch,
        "than_branch": BRANCH_CODES[than_bidx],
        "cuc": cuc,
        "stem_branch": f"{menh_stem}_{menh_branch}",
    }

    return {
        "schema_version": SCHEMA_VERSION,
        "rule_set_id": normalized.rule_set_id,
        "timezone": normalized.timezone,
        "input_normalized": normalized,
        "conversion": conversion,
        "chart_metadata": chart_metadata,
        "houses": houses,
        "major_fortunes": major_fortunes,
        "validation": validation,
        "menh": menh_block,
        "can_chi": can_chi,
    }
