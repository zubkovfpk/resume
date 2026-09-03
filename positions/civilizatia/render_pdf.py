#!/usr/bin/env python3
"""Рендерит index.html в PDF через headless Chromium (Playwright)."""
import os
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
HTML_PATH = os.path.join(HERE, "index.html")
PDF_PATH = os.path.join(HERE, "Zubkov_SA_Resume_Civilizatia.pdf")

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(f"file://{HTML_PATH}")
    page.wait_for_timeout(500)
    page.pdf(
        path=PDF_PATH,
        format="A4",
        print_background=True,
        margin={"top": "8mm", "bottom": "6mm", "left": "0mm", "right": "0mm"},
    )
    browser.close()

print(f"Written {PDF_PATH}")
