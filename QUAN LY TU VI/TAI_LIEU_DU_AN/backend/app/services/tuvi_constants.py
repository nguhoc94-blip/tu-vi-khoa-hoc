"""Shared constants for tuvi_mvp_v1 engine (rulebook internal names)."""

from __future__ import annotations

# Địa chi: Tý=0 ... Hợi=11 (vòng dương lịch quen thuộc)
BRANCH_CODES: tuple[str, ...] = (
    "ty",
    "suu",
    "dan",
    "mao",
    "thin",
    "ti",
    "ngo",
    "mui",
    "than",
    "dau",
    "tuat",
    "hoi",
)

# Thiên can
STEM_CODES: tuple[str, ...] = (
    "giap",
    "at",
    "binh",
    "dinh",
    "mau",
    "ky",
    "canh",
    "tan",
    "nham",
    "quy",
)

# 60 hoa giáp: index 0 = giap_ty ... index 7 = tan_mui (COO master plan)
SEXAGENARY_PAIRS: tuple[tuple[str, str], ...] = tuple(
    (STEM_CODES[i % 10], BRANCH_CODES[i % 12]) for i in range(60)
)

HOUSE_CODES: tuple[str, ...] = (
    "menh",
    "phu_mau",
    "phuc_duc",
    "dien_trach",
    "quan_loc",
    "no_boc",
    "thien_di",
    "tat_ach",
    "tai_bach",
    "tu_tuc",
    "phu_the",
    "huynh_de",
)

MAIN_STAR_CODES: tuple[str, ...] = (
    "tu_vi",
    "thien_co",
    "thai_duong",
    "vu_khuc",
    "thien_dong",
    "liem_trinh",
    "thien_phu",
    "thai_am",
    "tham_lang",
    "cu_mon",
    "thien_tuong",
    "thien_luong",
    "that_sat",
    "pha_quan",
)

# Nạp âm 60 → ngũ hành nền (để suy Cục)
# key: (stem, branch) lowercase
_NAP_AM_RAW: list[tuple[tuple[str, str], str]] = [
    (("giap", "ty"), "kim"),
    (("at", "suu"), "kim"),
    (("binh", "dan"), "hoa"),
    (("dinh", "mao"), "hoa"),
    (("mau", "thin"), "moc"),
    (("ky", "ti"), "moc"),
    (("canh", "ngo"), "tho"),
    (("tan", "mui"), "tho"),
    (("nham", "than"), "kim"),
    (("quy", "dau"), "kim"),
    (("giap", "tuat"), "hoa"),
    (("at", "hoi"), "hoa"),
    (("binh", "ty"), "thuy"),
    (("dinh", "suu"), "thuy"),
    (("mau", "dan"), "tho"),
    (("ky", "mao"), "tho"),
    (("canh", "thin"), "kim"),
    (("tan", "ti"), "kim"),
    (("nham", "ngo"), "moc"),
    (("quy", "mui"), "moc"),
    (("giap", "than"), "thuy"),
    (("at", "dau"), "thuy"),
    (("binh", "tuat"), "tho"),
    (("dinh", "hoi"), "tho"),
    (("mau", "ty"), "hoa"),
    (("ky", "suu"), "hoa"),
    (("canh", "dan"), "moc"),
    (("tan", "mao"), "moc"),
    (("nham", "thin"), "thuy"),
    (("quy", "ti"), "thuy"),
    (("giap", "ngo"), "kim"),
    (("at", "mui"), "kim"),
    (("binh", "than"), "hoa"),
    (("dinh", "dau"), "hoa"),
    (("mau", "tuat"), "moc"),
    (("ky", "hoi"), "moc"),
    (("canh", "ty"), "tho"),
    (("tan", "suu"), "tho"),
    (("nham", "dan"), "kim"),
    (("quy", "mao"), "kim"),
    (("giap", "thin"), "hoa"),
    (("at", "ti"), "hoa"),
    (("binh", "ngo"), "thuy"),
    (("dinh", "mui"), "thuy"),
    (("mau", "than"), "tho"),
    (("ky", "dau"), "tho"),
    (("canh", "tuat"), "kim"),
    (("tan", "hoi"), "kim"),
    (("nham", "ty"), "moc"),
    (("quy", "suu"), "moc"),
    (("giap", "dan"), "thuy"),
    (("at", "mao"), "thuy"),
    (("binh", "thin"), "hoa"),
    (("dinh", "ti"), "hoa"),
    (("mau", "ngo"), "tho"),
    (("ky", "mui"), "tho"),
    (("canh", "than"), "moc"),
    (("tan", "dau"), "moc"),
    (("nham", "tuat"), "thuy"),
    (("quy", "hoi"), "thuy"),
]

NAP_AM: dict[tuple[str, str], str] = {k: v for k, v in _NAP_AM_RAW}

ELEMENT_TO_CUC: dict[str, str] = {
    "thuy": "thuy_2",
    "moc": "moc_3",
    "kim": "kim_4",
    "tho": "tho_5",
    "hoa": "hoa_6",
}

CUC_NUMBER: dict[str, int] = {
    "thuy_2": 2,
    "moc_3": 3,
    "kim_4": 4,
    "tho_5": 5,
    "hoa_6": 6,
}


def branch_index(code: str) -> int:
    return BRANCH_CODES.index(code)


def stem_index(code: str) -> int:
    return STEM_CODES.index(code)
