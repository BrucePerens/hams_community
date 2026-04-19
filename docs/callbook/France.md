# France Amateur Radio Operator Database

## Source Information
- **Agency:** Agence Nationale des Fréquences (ANFR)
- **Database Name:** Observatoire des radioamateurs
- **Source URL:** https://data.anfr.fr/explore/dataset/radioamateurs/
- **License/Redistribution:** French Open Data (Etalab Licence Ouverte v2.0), unrestricted public data.

## Download Process
The ANFR provides an Open Data portal. While the main frontend uses interactive visualization, the underlying data is accessible via standard OpenDataSoft APIs.

It can be downloaded natively as a CSV file. Unlike Brazil or the UK, the ANFR Open Data platform generally does not block automated `curl` or `wget` requests for data exports, provided the correct API endpoint is used.

```bash
# Example OpenDataSoft export endpoint format for CSV
wget "https://data.anfr.fr/api/explore/v2.1/catalog/datasets/radioamateurs/exports/csv" -O france_callbook.csv

# Note: The exact dataset slug might occasionally change, but "radioamateurs" is the standard identifier.
```

## Data Format & Schema
The OpenDataSoft API returns a standard semicolon-separated or comma-separated CSV file (depending on the requested delimiter parameters).

**Expected Columns:**
- `indicatif` (Callsign, e.g., F4...)
- `classe` (License Class: e.g., Classe 2, Classe 3, HAREC)
- `departement` (Department number/code)
- `region` (Region name)
- *Note: Due to GDPR compliance, specific names and precise street addresses are anonymized or omitted entirely in the Open Data dump, providing only geographic aggregates (Department/Region) and license status.*

### Processing Strategy
1. Download the CSV via the `/exports/csv` API endpoint.
2. Filter the `indicatif` column to verify a callsign exists.
3. Validate the operator's active status based on the provided columns.
