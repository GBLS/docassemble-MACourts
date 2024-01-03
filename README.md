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

## How to update `lower_court_code`

When e-filing into appeals cases, Tyler expects a very specific code for the lower court that the case is being appealed from. We got a confirmation from Tyler that these values aren't publicly available, so for now they are stored in the `tyler_lower_court_code` and `tyler_prod_lower_court_code` attributes
for each object.

These values may occasionally change. And again, as we've gotten little information from Tyler about these values, we don't know when these values change. The only indication is if you start receiving `168, Lower court code not found` errors when filing.

To update these values:
* visit and login to https://massachusetts-stage.tylertech.cloud/ofsweb/ (or the production site, https://massachusetts.tylertech.cloud/ofsweb/)
* Once logged in, under "New Filing", click "Start a new case" (or visit https://massachusetts-stage.tylertech.cloud/OfsWeb/FileAndServeModule/Envelope/AddOrEdit).
* Pull up your browser's network tools, refresh the page, and set the location field to be "Appeals Court (Single Justice)".
* In your browser's network tools, look for the request to `GetEnvelopeCodeConfigs`. The full URL queried is https://massachusetts-stage.tylertech.cloud/OfsWeb/FileAndServeModule/Envelope/GetEnvelopeCodeConfigs?isLocationChanged=true&locationId=120.

The values we need will be in the JSON returned from that endpoint, under `obj["DropDownsLocation"]["LowerCourtCodes"]`.

**Note**: I wasn't able to give Lower Court codes to the "Metro South Housing Courts". Tyler's list only includes:

* Housing Court Central
* Housing Court Eastern
* Housing Court, Northeast
* Housing Court, Southeast
* Housing Court, Western
