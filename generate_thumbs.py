"""
Generate thumbnail images for the microfilm archive viewer.
Thumbnails are resized to a maximum of 300px on the longest side, JPEG quality 75.
Safe to re-run — skips files that already exist in the thumbs folder.

Usage:
    python generate_thumbs.py

After running, upload thumbnails to Cloudflare R2:
    rclone copy "thumbs" r2:meteorologicalobservations/thumbs --progress --transfers 8
"""

import os
from PIL import Image

BASE_DIR   = 'd:/Farmscape Weather Data/Microfilm processed'
IMAGES_DIR = os.path.join(BASE_DIR, 'images')
THUMBS_DIR = os.path.join(BASE_DIR, 'thumbs')
MAX_SIZE   = 300   # longest dimension in pixels
QUALITY    = 75

os.makedirs(THUMBS_DIR, exist_ok=True)

files   = sorted(f for f in os.listdir(IMAGES_DIR) if f.upper().endswith('.JPG'))
total   = len(files)
done    = 0
skipped = 0
errors  = 0

print(f'Generating thumbnails for {total:,} images...')

for i, fname in enumerate(files):
    src = os.path.join(IMAGES_DIR, fname)
    dst = os.path.join(THUMBS_DIR, fname)

    if os.path.exists(dst):
        skipped += 1
        continue

    try:
        with Image.open(src) as img:
            img.thumbnail((MAX_SIZE, MAX_SIZE), Image.LANCZOS)
            img.save(dst, 'JPEG', quality=QUALITY, optimize=True)
        done += 1
    except Exception as e:
        print(f'  ERROR {fname}: {e}')
        errors += 1

    if (i + 1) % 500 == 0 or (i + 1) == total:
        print(f'  {i + 1:,} / {total:,}  —  generated: {done:,}  skipped: {skipped:,}  errors: {errors}')

print(f'\nDone. {done:,} generated, {skipped:,} already existed, {errors} errors.')
print(f'Thumbnails saved to: {THUMBS_DIR}')
if done > 0:
    print(f'\nNext step — upload to R2:')
    print(f'  rclone copy "thumbs" r2:meteorologicalobservations/thumbs --progress --transfers 8')
