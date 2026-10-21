# pkphone

Clean, validate and normalize **Pakistani phone numbers** (mobile + landline).
Useful when scraping leads, cleaning CRM exports, or building WhatsApp links.

## Install

```bash
pip install pkphone            # once published on PyPI
pip install -e .               # from a local clone
```

## Usage

```python
from pkphone import parse, normalize, is_valid, extract_all

normalize("0300-1234567")              # '+923001234567'
normalize("+92 300 1234567", "local")  # '0300-1234567'
normalize("03001234567", "whatsapp")   # '923001234567'  -> https://wa.me/923001234567

p = parse("021-34567890")
p.kind, p.city                         # ('landline', 'Karachi')

parse("0345 1112223").operator         # 'Telenor'
is_valid("0390-1234567")               # False

extract_all("Call 0300-1234567 or office 021-34567890")
# [PhoneNumber(+923001234567), PhoneNumber(+922134567890)]
```

## CLI

```bash
pkphone 0300-1234567 "+92 21 34567890" 12345
pkphone --csv leads.csv --column phone --out leads_clean.csv
```

The CSV mode adds `phone_clean` and `phone_valid` columns.

## Notes

- Operator is based on the original prefix; ported numbers (MNP) may differ.
- Landline lengths are checked for major cities; other area codes get a general length check.

## License

MIT
