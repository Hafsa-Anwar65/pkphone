import pytest

from pkphone import extract_all, is_valid, normalize, parse


@pytest.mark.parametrize("raw", [
    "03001234567", "0300-1234567", "0300 123 4567", "+92 300 1234567",
    "923001234567", "00923001234567", "(0300) 1234567", "3001234567",
])
def test_mobile_formats(raw):
    assert normalize(raw) == "+923001234567"


def test_operator_and_local():
    p = parse("0345-1112223")
    assert p.kind == "mobile" and p.operator == "Telenor"
    assert p.local == "0345-1112223"
    assert p.whatsapp == "923451112223"


def test_karachi_landline():
    p = parse("021-34567890")
    assert p.kind == "landline" and p.city == "Karachi"
    assert p.e164 == "+922134567890"
    assert p.local == "021-34567890"


def test_islamabad_landline():
    assert parse("051 2345678").city == "Islamabad/Rawalpindi"


@pytest.mark.parametrize("raw", ["0300123", "0390-1234567", "021-123", "abc", "", "0000000000"])
def test_invalid(raw):
    assert not is_valid(raw)


def test_extract_all():
    text = "Call 0300-1234567 or +92 321 7654321, office 021-34567890. Again 03001234567."
    found = [p.e164 for p in extract_all(text)]
    assert found == ["+923001234567", "+923217654321", "+922134567890"]


def test_bad_format():
    with pytest.raises(ValueError):
        normalize("03001234567", fmt="xyz")
