"""Core parsing logic for Pakistani phone numbers."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional

COUNTRY_CODE = "92"

# Mobile prefix (first two digits after the 3) -> operator
MOBILE_OPERATORS = {
    "30": "Jazz",
    "32": "Jazz",
    "31": "Zong",
    "33": "Ufone",
    "34": "Telenor",
    "35": "SCOM",
}

# Landline area code -> (city, subscriber number length)
AREA_CODES = {
    "21": ("Karachi", 8),
    "42": ("Lahore", 8),
    "51": ("Islamabad/Rawalpindi", 7),
    "41": ("Faisalabad", 7),
    "61": ("Multan", 7),
    "91": ("Peshawar", 7),
    "81": ("Quetta", 7),
    "22": ("Hyderabad", 7),
    "52": ("Sialkot", 7),
    "55": ("Gujranwala", 7),
}

# Candidate pattern used to find numbers inside free text
_CANDIDATE = re.compile(r"(?:\+|00)?[\d][\d\s\-().]{8,16}\d")


@dataclass(frozen=True)
class PhoneNumber:
    """A parsed Pakistani phone number."""

    national: str  # national significant number, no leading 0 (e.g. 3001234567)
    kind: str  # "mobile" or "landline"
    operator: Optional[str] = None
    city: Optional[str] = None

    @property
    def e164(self) -> str:
        """International format, e.g. +923001234567."""
        return f"+{COUNTRY_CODE}{self.national}"

    @property
    def local(self) -> str:
        """Local format, e.g. 0300-1234567 or 021-34567890."""
        if self.kind == "mobile":
            return f"0{self.national[:3]}-{self.national[3:]}"
        code = _area_code_of(self.national) or self.national[:2]
        return f"0{code}-{self.national[len(code):]}"

    @property
    def whatsapp(self) -> str:
        """Format accepted by wa.me links, e.g. 923001234567."""
        return f"{COUNTRY_CODE}{self.national}"

    def __str__(self) -> str:
        return self.e164


def _digits(raw: str) -> str:
    return re.sub(r"\D", "", raw)


def _to_national(raw: str) -> Optional[str]:
    """Strip country code / trunk prefix and return the national number."""
    s = raw.strip()
    d = _digits(s)
    if not d:
        return None
    if d.startswith("0092"):
        d = d[4:]
    elif d.startswith("92") and (s.startswith("+") or len(d) >= 11):
        d = d[2:]
    if d.startswith("0"):
        d = d[1:]
    return d


def _area_code_of(national: str) -> Optional[str]:
    for code in AREA_CODES:
        if national.startswith(code):
            return code
    return None


def parse(raw: str) -> Optional[PhoneNumber]:
    """Parse any common Pakistani format. Returns None if invalid."""
    if not isinstance(raw, str):
        return None
    n = _to_national(raw)
    if not n:
        return None

    # Mobile: 3XX XXXXXXX (10 digits)
    if n.startswith("3"):
        if len(n) == 10 and n[:2] in MOBILE_OPERATORS:
            return PhoneNumber(n, "mobile", operator=MOBILE_OPERATORS[n[:2]])
        return None

    # Known city landline
    code = _area_code_of(n)
    if code:
        city, sub_len = AREA_CODES[code]
        if len(n) == len(code) + sub_len:
            return PhoneNumber(n, "landline", city=city)
        return None

    # Other area codes: accept 9-10 digit national numbers starting 2-9
    if n[0] in "2456789" and len(n) in (9, 10):
        return PhoneNumber(n, "landline")
    return None


def normalize(raw: str, fmt: str = "e164") -> Optional[str]:
    """Return the number in the given format: e164, local or whatsapp."""
    p = parse(raw)
    if p is None:
        return None
    if fmt not in ("e164", "local", "whatsapp"):
        raise ValueError("fmt must be 'e164', 'local' or 'whatsapp'")
    return getattr(p, fmt)


def is_valid(raw: str) -> bool:
    """True if the string is a valid Pakistani number."""
    return parse(raw) is not None


def extract_all(text: str) -> List[PhoneNumber]:
    """Find every valid Pakistani number inside free text (deduplicated)."""
    seen, out = set(), []
    for m in _CANDIDATE.finditer(text or ""):
        p = parse(m.group())
        if p and p.national not in seen:
            seen.add(p.national)
            out.append(p)
    return out
