# Canada Amateur Radio Operator Database

## Source Information
- **Agency:** Innovation, Science and Economic Development Canada (ISED) / Spectrum Management System
- **Source URL:** https://apc-cap.ic.gc.ca/datafiles/amateur.zip
- **Information Page:** https://ised-isde.canada.ca/site/amateur-radio-operator-certificate-services/en/downloads
- **License/Redistribution:** Provided as a dynamic display and downloadable list by the Government of Canada under Open Government terms (unrestricted public data).

## Download Process
The database is available as a ZIP file. It can be downloaded directly using a standard HTTP GET request without any special headers or authentication required.

```bash
wget https://apc-cap.ic.gc.ca/datafiles/amateur.zip
unzip amateur.zip
```

The ZIP file contains:
- `amateur.txt` (The main data file)
- `readme_amat.txt` (English instructions)
- `lisezmoi_amat.txt` (French instructions)

## Data Completeness (Validation)
**Test Download Results:** Successfully downloaded the bulk ZIP.
- **Records Count:** ~91,562 records.
- **Completeness:** Excellent. Contains the full national registry of certified Canadian operators.

## Data Format & Schema
The data is in a fixed-width or space-delimited text format, not a standard CSV.

**Snippet:**
```
2026-04-17  Canadian Amateur Call Sign List / List d'indicatif d'appel canadien
 
There are 91557 call signs in this report. / Il y a 91557 indicatifs d'appels dans ce rapport.
 
VA1AA  Bill                                McFadden                            188 MILLWOOD DRIVE                                                     MIDDLE SACKVILLE                    NS B4E 2X8    A   C D   
VA1AAA Jeffrey                             Taylor                              381B Pleasant Street                                                   Dartmouth                           NS B2Y 3S5    A B C D E 
```

### Parsing Strategy
1. Skip the first 4 lines (header and empty lines).
2. The remaining lines are fixed-width records.
3. The column widths will need to be inferred or read from `readme_amat.txt`. Typically they represent:
   - Call Sign
   - First Name
   - Last Name
   - Address
   - City
   - Province
   - Postal Code
   - Qualifications (e.g., A, B, C, D, E indicating Basic, Advanced, Morse Code, etc.)
