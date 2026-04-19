# Germany Amateur Radio Operator Database

## Source Information
- **Agency:** Bundesnetzagentur (BNetzA) - Federal Network Agency
- **Database Name:** Rufzeichenliste der Funkamateure (Callsign List of Radio Amateurs)
- **Source URL:** https://data.bundesnetzagentur.de/Bundesnetzagentur/SharedDocs/Downloads/DE/Sachgebiete/Telekommunikation/Unternehmen_Institutionen/Frequenzen/Amateurfunk/Rufzeichenliste/rufzeichenliste_afu.pdf
- **Information Page:** https://www.bundesnetzagentur.de/DE/Fachthemen/Telekommunikation/Frequenzen/SpezielleAnwendungen/Amateurfunk/start.html
- **License/Redistribution:** Published officially by the German government. Publicly available list, no explicit restrictions on redistribution found, commonly parsed by the community.

## Download Process
The Bundesnetzagentur provides the complete, updated list of callsigns as a single PDF document. It does not appear to provide a native CSV or database dump.
It can be downloaded using standard HTTP tools, but it may require managing cookies or providing a standard User-Agent.

```bash
wget "https://data.bundesnetzagentur.de/Bundesnetzagentur/SharedDocs/Downloads/DE/Sachgebiete/Telekommunikation/Unternehmen_Institutionen/Frequenzen/Amateurfunk/Rufzeichenliste/rufzeichenliste_afu.pdf" -O germany_callbook.pdf
```

## Data Format & Schema
The data is embedded inside a large PDF file. Extracting the data requires a PDF parsing tool.

### Processing Strategy
Because the data is locked in a PDF, the daemon will need to use a library like `pdfplumber` (Python) or an existing community parser to extract the tables.

Existing open-source parsers exist on GitHub (e.g., `joergschultzelutter/bundesnetzagentur-rufzeichenliste-parser` or `robinolejnik/bnetza-rufzeichenliste-parser`) which demonstrate how to extract the tabular data into CSV format.

**Expected Data Fields (based on standard PDF layout):**
- Rufzeichen (Callsign)
- Klasse (License Class: e.g., A, E, N)
- Name (First and Last Name, if consented)
- Anschrift (Address / City, if consented)

*Note: Like the UK, German data privacy laws (GDPR) mean many operators choose to withhold their name and address from the public list. In those cases, only the callsign and license class are published.*

### Example Python parsing concept (using pdfplumber)
```python
import pdfplumber
import pandas as pd

with pdfplumber.open("germany_callbook.pdf") as pdf:
    # Skip preamble pages, find table pages
    # Extract table rows
    # Note: BNetzA PDF tables often have multiple columns of callsigns per page to save space,
    # so the parser needs to handle multi-column wrapping layouts.
    pass
```
