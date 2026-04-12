"""
Solar/lunar conversion for tuvi_mvp_v1 using lunar-vn (Ho Ngoc Duc algorithm, UTC+7 Vietnamese calendar).
Replaces zhdate (Chinese UTC+8) to correctly handle the 1-day discrepancy between
Vietnamese and Chinese lunar calendars for months where the new moon falls near UTC midnight.
calendar_engine_version = 1.1.0
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from lunar_vn import LunarDate as _VnLunarDate
from lunar_vn import lunar_to_solar as _vn_lunar_to_solar
from lunar_vn import solar_to_lunar as _vn_solar_to_lunar

CALENDAR_ENGINE_VERSION = "1.1.0"


@dataclass(frozen=True)
class SolarDate:
    year: int
    month: int
    day: int

    def to_date(self) -> date:
        return date(self.year, self.month, self.day)


@dataclass(frozen=True)
class LunarDateParts:
    lunar_year: int
    lunar_month: int
    lunar_day: int
    is_leap_month: bool


def solar_to_lunar(solar: SolarDate) -> LunarDateParts:
    l = _vn_solar_to_lunar((solar.day, solar.month, solar.year))
    return LunarDateParts(
        lunar_year=l.year,
        lunar_month=l.month,
        lunar_day=l.day,
        is_leap_month=bool(l.leap),
    )


def lunar_to_solar(lunar: LunarDateParts) -> SolarDate:
    vn = _VnLunarDate(lunar.lunar_day, lunar.lunar_month, lunar.lunar_year, lunar.is_leap_month)
    d = _vn_lunar_to_solar(vn)
    return SolarDate(d.year, d.month, d.day)


def resolve_solar_for_chart(
    *,
    calendar_type: str,
    birth_year: int,
    birth_month: int,
    birth_day: int,
    is_leap_lunar_month: bool,
) -> tuple[SolarDate, LunarDateParts, dict]:
    """
    Returns (solar_for_domain, lunar_parts, conversion_note dict fields).
    Rule: solar input keeps calendar; lunar input converts to solar for can-chi day (rulebook 8, COO 9.2).
    """
    if calendar_type == "solar":
        solar = SolarDate(birth_year, birth_month, birth_day)
        lunar = solar_to_lunar(solar)
        return solar, lunar, {
            "calendar_type": "solar",
            "solar_for_domain": {"year": solar.year, "month": solar.month, "day": solar.day},
            "lunar_from_solar": {
                "lunar_year": lunar.lunar_year,
                "lunar_month": lunar.lunar_month,
                "lunar_day": lunar.lunar_day,
                "is_leap_month": lunar.is_leap_month,
            },
            "note": "solar input: leap lunar forced false at normalize; lunar shown is derived",
        }

    lunar_in = LunarDateParts(
        lunar_year=birth_year,
        lunar_month=birth_month,
        lunar_day=birth_day,
        is_leap_month=is_leap_lunar_month,
    )
    solar = lunar_to_solar(lunar_in)
    return solar, lunar_in, {
        "calendar_type": "lunar",
        "solar_for_domain": {"year": solar.year, "month": solar.month, "day": solar.day},
        "lunar_input": {
            "lunar_year": lunar_in.lunar_year,
            "lunar_month": lunar_in.lunar_month,
            "lunar_day": lunar_in.lunar_day,
            "is_leap_month": lunar_in.is_leap_month,
        },
        "note": "lunar input converted to solar before day can-chi",
    }
