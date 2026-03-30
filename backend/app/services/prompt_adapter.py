from __future__ import annotations

from typing import Any


def _as_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    return {}


def _as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    return []


def _as_text(value: Any, default: str = "unknown") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text or default


def _pick_palace(palaces: dict[str, Any], key: str) -> dict[str, Any]:
    value = palaces.get(key)
    return value if isinstance(value, dict) else {}


def to_prompt_input_json(engine_raw_json: dict[str, Any]) -> dict[str, Any]:
    """
    Maps engine_raw_json into a safe prompt_input_json shape.
    Only normalize/map fields; do not infer TuVi formulas.
    Missing fields are filled with unknown / {} / [].
    """
    raw = _as_dict(engine_raw_json)

    input_normalized = _as_dict(raw.get("input_normalized"))
    conversion = _as_dict(raw.get("conversion"))
    chart_metadata = _as_dict(raw.get("chart_metadata"))
    validation = _as_dict(raw.get("validation"))
    palaces_raw = _as_dict(raw.get("palaces"))

    # Some payloads may provide palaces as list in previous mock versions.
    if not palaces_raw:
        palaces_list = _as_list(raw.get("palaces"))
        if palaces_list:
            # Keep list as-is under _raw_list for compatibility, do not invent mapping.
            palaces_raw = {"_raw_list": palaces_list}

    dai_van = _as_dict(raw.get("dai_van"))
    if not dai_van:
        dai_van = {
            "current": _as_dict(raw.get("major_fortunes")),
            "all": _as_list(raw.get("major_fortunes")),
        }

    profile = {
        "gender": _as_text(input_normalized.get("gender")),
        "calendar_type": _as_text(input_normalized.get("calendar_type")),
        "birth_year": _as_text(input_normalized.get("birth_year")),
        "birth_month": _as_text(input_normalized.get("birth_month")),
        "birth_day": _as_text(input_normalized.get("birth_day")),
        "birth_hour": _as_text(input_normalized.get("birth_hour")),
        "birth_minute": _as_text(input_normalized.get("birth_minute")),
        "timezone": _as_text(raw.get("timezone")),
    }

    chart_core = {
        "schema_version": _as_text(raw.get("schema_version")),
        "rule_set_id": _as_text(raw.get("rule_set_id")),
        "menh": _as_dict(raw.get("menh")),
        "conversion": conversion,
        "chart_metadata": chart_metadata,
        "validation": validation,
    }

    palaces = {
        "quan_loc": _pick_palace(palaces_raw, "quan_loc"),
        "tai_bach": _pick_palace(palaces_raw, "tai_bach"),
        "dien_trach": _pick_palace(palaces_raw, "dien_trach"),
        "phu_the": _pick_palace(palaces_raw, "phu_the"),
        "phuc_duc": _pick_palace(palaces_raw, "phuc_duc"),
    }

    reading_constraints = {
        "tong_quan_source": ["chart_core", "dai_van.current"],
        "cong_viec_source": ["palaces.quan_loc", "chart_core.menh", "dai_van.current"],
        "tai_chinh_source": ["palaces.tai_bach", "palaces.dien_trach", "dai_van.current"],
        "tinh_cam_source": ["palaces.phu_the", "palaces.phuc_duc", "chart_core.menh", "dai_van.current"],
        "note": "mapping-only adapter; no TuVi formula inference",
    }

    return {
        "profile": profile,
        "chart_core": chart_core,
        "palaces": palaces,
        "dai_van": {
            "current": _as_dict(dai_van.get("current")),
            "all": _as_list(dai_van.get("all")),
        },
        "reading_constraints": reading_constraints,
    }

