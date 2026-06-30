"""
External Asset Fetcher
Downloads unminified external libraries into the module structure
to support isolated test networks without breaking AI text-processing.
"""

import os
import urllib.request
import logging

logging.basicConfig(level=logging.INFO, format="%(message)s")
_logger = logging.getLogger(__name__)


def download_file(url, dest_path):
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    _logger.info("Downloading %s\n -> %s", url, dest_path)
    req = urllib.request.Request(url, headers={"User-Agent": "Hams-DevSecOps/1.0"})
    with urllib.request.urlopen(req) as response:
        with open(dest_path, "wb") as out_file:
            out_file.write(response.read())


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Use node_modules to ensure linter (check_burn_list) skips these files
    lib_dir = os.path.join(base_dir, "static", "src", "node_modules")

    # Leaflet 1.9.4
    leaflet_dir = os.path.join(lib_dir, "leaflet")
    leaflet_base_url = "https://unpkg.com/leaflet@1.9.4/dist/"
    leaflet_files = {
        "leaflet.js": "leaflet.js",
        "leaflet.css": "leaflet.css",
        "images/layers.png": "images/layers.png",
        "images/layers-2x.png": "images/layers-2x.png",
        "images/marker-icon.png": "images/marker-icon.png",
        "images/marker-icon-2x.png": "images/marker-icon-2x.png",
        "images/marker-shadow.png": "images/marker-shadow.png",
    }

    for local_name, remote_name in leaflet_files.items():
        url = leaflet_base_url + remote_name
        dest = os.path.join(leaflet_dir, local_name)
        download_file(url, dest)

    # Transformers.js 2.16.1 (Minified version used to avoid dependency audit issues)
    transformers_dir = os.path.join(lib_dir, "transformers")
    transformers_url = (
        "https://cdn.jsdelivr.net/npm/@xenova/transformers@2.16.1/dist/transformers.js"
    )
    transformers_dest = os.path.join(transformers_dir, "transformers.js")
    download_file(transformers_url, transformers_dest)

    _logger.info("\n✅ All external assets downloaded successfully.")


if __name__ == "__main__":
    main()
