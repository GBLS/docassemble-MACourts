# docassemble.MACourts

A utility package that includes JSON files representing all of the courts in Massachusetts.

Courts automatically scraped from Mass.gov and geocoded with Google Maps.

If the court has a PO box, the PO box will be available in court.address.orig_address

## Tests

Mypy:

```bash
mypy .
```

Unittests:

```bash
python3 -m unittest discover docassemble
```
