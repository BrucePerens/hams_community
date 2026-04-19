# Argentina Amateur Radio Operator Database

## Source Information
- **Agency:** Ente Nacional de Comunicaciones (ENACOM)
- **Database Name:** Listado de Radioaficionados Vigentes (Sistema HERTZ)
- **Source URL:** https://hertz.enacom.gob.ar/se/portal/arg/publico/ListadoRadioaficionado.php
- **Information Page:** https://www.enacom.gob.ar/listado-de-radioaficionados_p316
- **License/Redistribution:** Argentine Government public data.

## Download / Verification Process
ENACOM provides an online searchable portal ("Sistema HERTZ") for verifying active amateur radio operators. They occasionally publish PDF updates on their main site, but the dynamic `hertz.enacom.gob.ar` portal is the live query interface.

There is no direct link to download the entire database as a bulk CSV. However, the online database is unauthenticated and can be queried.

### Scraping / Verification Strategy
The daemon should send an HTTP GET or POST request to the `ListadoRadioaficionado.php` endpoint to verify specific callsigns.
*Note: The server uses a self-signed or improperly chained SSL certificate, so the HTTP client (e.g., `curl` or `requests`) must bypass SSL verification (`verify=False` in Python or `-k` in curl).*

```python
# Conceptual Example using Python requests
import requests

url = "https://hertz.enacom.gob.ar/se/portal/arg/publico/ListadoRadioaficionado.php"
# Investigate the form payload required by inspecting the HTML/Network tab
# payload = {"senial_distintiva": "LU1AAA"}
# response = requests.post(url, data=payload, verify=False)
```

## Data Format & Schema
When querying the ENACOM HERTZ portal, the expected fields returned in the HTML table are:
- `Señal Distintiva` (Callsign, e.g., LU..., LW...)
- `Categoría` (License Class: Novicio, General, Superior, Especial)
- `Nombre y Apellido` (Operator Name)
- `Fecha de Vencimiento` (Expiration Date)
- `Provincia` (Province/State)
- `Localidad` (City)

The daemon will need an HTML parser (like `beautifulsoup4`) to extract the data from the search results table.
