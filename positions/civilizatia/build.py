#!/usr/bin/env python3
"""Собирает index.html, вставляя фото из photo_b64.txt в шаблон."""
import re

TEMPLATE_PATH = "template.html"
PHOTO_PATH = "photo_b64.txt"
OUTPUT_PATH = "index.html"

with open(PHOTO_PATH) as f:
    photo_b64 = f.read().strip()

with open(TEMPLATE_PATH) as f:
    html = f.read()

html = html.replace("__PHOTO_BASE64__", photo_b64)

with open(OUTPUT_PATH, "w") as f:
    f.write(html)

print(f"Written {OUTPUT_PATH}, {len(html)} chars")
