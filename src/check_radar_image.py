"""
check_radar_image.py - Meteocat Radar Tile Download & Stitch Test

Usage:
    1. Ensure you have installed dependencies:
        uv pip install opencv-python requests numpy
    2. Run the script:
        python src/check_radar_image.py
    3. The script downloads radar tiles for the configured timestamp and region,
       stitches them into a single image, and saves it as
       radar_YYYYMMDD_HHMM.png in the current directory.

Edit the RADAR_TIMESTAMP, TILE_X_RANGE, and TILE_Y variables to select
different times or regions as needed.
"""

import os
import cv2
import numpy as np
import requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# --- CONFIGURABLE ---
RADAR_TIMESTAMP = datetime.now(ZoneInfo("Europe/Madrid")) - timedelta(minutes=120)
ZOOM = 7  # Meteocat radar zoom level (7 or 8)
TILE_SIZE = 1024  # px (for radar tiles at zoom 7)
# Tiles to download (x, y indices) for a region covering Catalonia
# These are example values; adjust as needed for your area
TILE_X_RANGE = [64, 65]  # inclusive
TILE_Y = 80  # fixed for this example

# --- FUNCTIONS ---
def get_tile_url(dt, zoom, x, y):
    """Generate Meteocat radar tile URL for given datetime, zoom, x, y."""
    return (
        f"https://static-m.meteo.cat/tiles/radar/"
        f"{dt.year:04d}/{dt.month:02d}/{dt.day:02d}/"
        f"{dt.hour:02d}/{dt.minute:02d}/07/000/000/"
        f"{x:03d}/000/000/{y:03d}.png"
    )

def download_tile(url):
    """Download a single tile image from URL and return as numpy array."""
    resp = requests.get(url)
    if resp.status_code == 200:
        arr = np.asarray(bytearray(resp.content), dtype=np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_UNCHANGED)
        return img
    else:
        print(f"Failed to download {url}")
        return None

def stitch_tiles(tiles, x_range, y):
    """Stitch tiles horizontally for a single row (y)."""
    row_imgs = []
    for x in x_range:
        img = tiles.get((x, y))
        if img is None:
            # Create blank tile if missing
            img = np.zeros((TILE_SIZE, TILE_SIZE, 4), dtype=np.uint8)
        row_imgs.append(img)
    return np.hstack(row_imgs)

def main():
    tiles = {}
    print("Downloading tiles...")
    for x in range(TILE_X_RANGE[0], TILE_X_RANGE[1] + 1):
        url = get_tile_url(RADAR_TIMESTAMP, ZOOM, x, TILE_Y)
        print(f"Downloading: {url}")
        img = download_tile(url)
        tiles[(x, TILE_Y)] = img
    print("Stitching tiles...")
    stitched = stitch_tiles(tiles, range(TILE_X_RANGE[0], TILE_X_RANGE[1] + 1), TILE_Y)
    # Ensure output directory exists
    out_dir = os.path.join(os.path.dirname(__file__), '../radar_images')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"radar_{RADAR_TIMESTAMP.strftime('%Y%m%d_%H%M')}.png")
    cv2.imwrite(out_path, stitched)
    print(f"Saved stitched radar image to {out_path}")

if __name__ == "__main__":
    main()
