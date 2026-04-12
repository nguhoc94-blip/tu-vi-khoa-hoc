"""
Can chi năm/tháng/ngày/giờ — tuvi_can_chi_engine_v1
Ngày: COO master plan mục 9 (epoch 1911-01-01 = tan_mui, index 7, day_offset calendar).
can_chi_engine_version = 1.0.0
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from app.services.tuvi_constants import BRANCH_CODES, SEXAGENARY_PAIRS, STEM_CODES, stem_index

CAN_CHI_ENGINE_VERSION = "1.0.0"

# COO khóa cứng
EPOCH_GREGORIAN = date(1911, 1, 1)
EPOCH_DAY_SEXAGENARY_INDEX = 7  # tan_mui


@dataclass(frozen=True)
class Pillar:
    stem: str
    branch: str

    def as_pair_code(self) -> str:
        return f"{self.stem}_{self.branch}"

    def sexagenary_index(self) -> int:
        for i, (s, b) in enumerate(SEXAGENARY_PAIRS):
            if s == self.stem and b == self.branch:
                return i
        raise ValueError(f"unknown pillar {self}")


def civil_time_to_hour_branch(hour: int, minute: int) -> str:
    """Giờ dân dụng → địa chi giờ (rulebook §6). minute không đổi ngày."""
    _ = minute  # explicit: no day shift from minutes
    if hour == 23 or hour == 0:
        return "ty"
    return BRANCH_CODES[(hour + 1) // 2]


def lunar_year_pillar(lunar_year: int) -> Pillar:
    """Năm âm lịch: (năm - 4) % 60 = index hoa giáp (4 CN = giap_ty convention)."""
    idx = (lunar_year - 4) % 60
    s, b = SEXAGENARY_PAIRS[idx]
    return Pillar(s, b)


def month1_stem_on_dan(year_stem_idx: int) -> int:
    """Ngũ Hổ Độn: can tháng giêng (tháng 1 âm) tại cung Dần."""
    if year_stem_idx in (0, 5):
        return stem_index("binh")
    if year_stem_idx in (1, 6):
        return stem_index("mau")
    if year_stem_idx in (2, 7):
        return stem_index("canh")
    if year_stem_idx in (3, 8):
        return stem_index("nham")
    if year_stem_idx in (4, 9):
        return stem_index("giap")
    raise ValueError(year_stem_idx)


def lunar_month_pillar(lunar_year: int, lunar_month: int) -> Pillar:
    yp = lunar_year_pillar(lunar_year)
    ys = stem_index(yp.stem)
    stem0 = month1_stem_on_dan(ys)
    stem = STEM_CODES[(stem0 + (lunar_month - 1)) % 10]
    branch = BRANCH_CODES[(branch_index("dan") + (lunar_month - 1)) % 12]
    return Pillar(stem, branch)


def branch_index(code: str) -> int:
    return BRANCH_CODES.index(code)


def day_pillar_from_solar(solar: date) -> Pillar:
    day_offset = (solar - EPOCH_GREGORIAN).days
    idx = (EPOCH_DAY_SEXAGENARY_INDEX + day_offset) % 60
    s, b = SEXAGENARY_PAIRS[idx]
    return Pillar(s, b)


def hour_stem0_for_ty(day_stem_idx: int) -> int:
    """Ngũ Thử Độn: can của giờ Tý đầu ngày."""
    if day_stem_idx in (0, 5):
        return stem_index("giap")
    if day_stem_idx in (1, 6):
        return stem_index("binh")
    if day_stem_idx in (2, 7):
        return stem_index("mau")
    if day_stem_idx in (3, 8):
        return stem_index("canh")
    if day_stem_idx in (4, 9):
        return stem_index("nham")
    raise ValueError(day_stem_idx)


def hour_pillar(solar: date, hour: int, minute: int) -> Pillar:
    day_p = day_pillar_from_solar(solar)
    ds = stem_index(day_p.stem)
    h_branch = civil_time_to_hour_branch(hour, minute)
    h_idx = branch_index(h_branch)
    stem0 = hour_stem0_for_ty(ds)
    stem = STEM_CODES[(stem0 + h_idx) % 10]
    return Pillar(stem, h_branch)


def compute_can_chi_bundle(
    *,
    solar: date,
    lunar_year: int,
    lunar_month: int,
    birth_hour: int,
    birth_minute: int,
) -> dict:
    yp = lunar_year_pillar(lunar_year)
    mp = lunar_month_pillar(lunar_year, lunar_month)
    dp = day_pillar_from_solar(solar)
    hp = hour_pillar(solar, birth_hour, birth_minute)
    return {
        "can_chi_engine_version": CAN_CHI_ENGINE_VERSION,
        "year": {"stem": yp.stem, "branch": yp.branch, "pair": yp.as_pair_code()},
        "month": {"stem": mp.stem, "branch": mp.branch, "pair": mp.as_pair_code()},
        "day": {
            "stem": dp.stem,
            "branch": dp.branch,
            "pair": dp.as_pair_code(),
            "sexagenary_index": (EPOCH_DAY_SEXAGENARY_INDEX + (solar - EPOCH_GREGORIAN).days) % 60,
        },
        "hour": {"stem": hp.stem, "branch": hp.branch, "pair": hp.as_pair_code()},
    }
