from __future__ import annotations

import os
from typing import Any

from app.schemas.reading import SCHEMA_VERSION, ChartJson, NormalizedBirthInput


def _build_mock_chart_json(normalized: NormalizedBirthInput) -> ChartJson:
    conversion: dict[str, Any] = {
        "calendar_type": normalized.calendar_type,
        "note": "mock: USE_MOCK_CHART enabled",
    }
    chart_metadata: dict[str, Any] = {
        "engine": "mock",
        "version": "0.0.1",
    }
    houses: list[dict[str, Any]] = [
        {"index": i, "palace_id": f"mock_palace_{i}", "stars": []}
        for i in range(1, 13)
    ]
    major_fortunes: list[dict[str, Any]] = [
        {"id": "mock_major_10y", "label": "mock 10-year fortune", "value": None}
    ]
    validation: dict[str, Any] = {
        "status": "ok",
        "checks": ["input_normalized_present"],
    }
    return ChartJson(
        schema_version=SCHEMA_VERSION,
        rule_set_id=normalized.rule_set_id,
        timezone=normalized.timezone,
        input_normalized=normalized,
        conversion=conversion,
        chart_metadata=chart_metadata,
        houses=houses,
        major_fortunes=major_fortunes,
        validation=validation,
        menh={},
        can_chi={},
    )


def build_chart_json(normalized: NormalizedBirthInput) -> ChartJson:
    flag = (os.environ.get("USE_MOCK_CHART") or "").strip().lower()
    if flag in ("1", "true", "yes"):
        return _build_mock_chart_json(normalized)

    from app.services.tuvi_core_engine import build_chart_dict

    data = build_chart_dict(normalized)
    return ChartJson(
        schema_version=data["schema_version"],
        rule_set_id=data["rule_set_id"],
        timezone=data["timezone"],
        input_normalized=data["input_normalized"],
        conversion=data["conversion"],
        chart_metadata=data["chart_metadata"],
        houses=data["houses"],
        major_fortunes=data["major_fortunes"],
        validation=data["validation"],
        menh=data.get("menh", {}),
        can_chi=data.get("can_chi", {}),
    )
