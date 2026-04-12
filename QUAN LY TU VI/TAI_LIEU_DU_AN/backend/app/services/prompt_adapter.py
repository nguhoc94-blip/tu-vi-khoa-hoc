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


def _houses_list_to_palaces(raw: dict[str, Any]) -> dict[str, Any]:
    """Map rulebook houses[] -> palace keys used by prompts (nguồn chart thật)."""
    houses_list = _as_list(raw.get("houses"))
    out: dict[str, Any] = {}
    for h in houses_list:
        if not isinstance(h, dict):
            continue
        code = h.get("house_code")
        if not code:
            continue
        out[str(code)] = {
            "house_code": code,
            "house_index": h.get("house_index"),
            "branch": h.get("branch"),
            "main_stars": _as_list(h.get("main_stars")),
            "secondary_stars": _as_list(h.get("secondary_stars")),
            "is_menh_house": h.get("is_menh_house"),
            "is_than_house": h.get("is_than_house"),
        }
    return out


def to_prompt_input_json(engine_raw_json: dict[str, Any]) -> dict[str, Any]:
    """
    Maps chart_json (engine) into prompt_input_json for {{JSON_HOSO}}.
    Nguồn chính: houses / major_fortunes / menh / can_chi — không ép palaces/dai_van cũ làm source of truth.
    """
    raw = _as_dict(engine_raw_json)

    input_normalized = _as_dict(raw.get("input_normalized"))
    conversion = _as_dict(raw.get("conversion"))
    chart_metadata = _as_dict(raw.get("chart_metadata"))
    validation = _as_dict(raw.get("validation"))
    menh = _as_dict(raw.get("menh"))
    can_chi = _as_dict(raw.get("can_chi"))

    palaces_raw = _houses_list_to_palaces(raw)
    if not palaces_raw:
        palaces_raw = _as_dict(raw.get("palaces"))
        if not palaces_raw:
            palaces_list = _as_list(raw.get("palaces"))
            if palaces_list:
                palaces_raw = {"_raw_list": palaces_list}

    major_list = _as_list(raw.get("major_fortunes"))
    dai_van = _as_dict(raw.get("dai_van"))
    if not dai_van:
        current_idx = None
        ctx = _as_dict(chart_metadata.get("current_context"))
        if ctx.get("current_major_fortune_index") is not None:
            try:
                current_idx = int(ctx["current_major_fortune_index"])
            except (TypeError, ValueError):
                current_idx = None
        current_mf: dict[str, Any] = {}
        if major_list and current_idx is not None and 0 <= current_idx < len(major_list):
            current_mf = major_list[current_idx] if isinstance(major_list[current_idx], dict) else {}
        elif major_list and isinstance(major_list[0], dict):
            current_mf = major_list[0]
        dai_van = {
            "current": current_mf,
            "all": major_list,
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
        "menh": menh,
        "can_chi": can_chi,
        "conversion": conversion,
        "chart_metadata": chart_metadata,
        "validation": validation,
        "houses": _as_list(raw.get("houses")),
        "major_fortunes": major_list,
        "adapter_version": "2",
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
        "note": "houses-derived palaces; chart_core carries menh/can_chi",
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
