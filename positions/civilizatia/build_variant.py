#!/usr/bin/env python3
"""Build a standalone index-like HTML for a variant template (product/it) into a temp file,
then render to its own PDF, without touching the canonical template.html/index.html."""
import os, sys
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
variant = sys.argv[1]  # "product" or "it"
template_file = f"template_{variant}.html"
pdf_name = f"Zubkov_SA_Resume_Civilizatia_{'Product' if variant=='product' else 'IT'}.pdf"

with open(os.path.join(HERE, template_file), encoding="utf-8") as f:
    html = f.read()
with open(os.path.join(HERE, "photo_b64.txt"), encoding="utf-8") as f:
    photo = f.read().strip()
html = html.replace("__PHOTO_BASE64__", photo)

tmp_html = os.path.join(HERE, f"_tmp_{variant}.html")
with open(tmp_html, "w", encoding="utf-8") as f:
    f.write(html)

pdf_path = os.path.join(HERE, pdf_name)
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(f"file://{tmp_html}")
    page.pdf(
        path=pdf_path, format="A4", print_background=True,
        margin={"top": "8mm", "bottom": "10mm", "left": "0mm", "right": "0mm"},
        display_header_footer=True,
        header_template="<div></div>",
        footer_template="""
        <div style="width:100%; font-size:7pt; color:#888; text-align:center; font-family: Arial, sans-serif;">
          <span class="pageNumber"></span> из <span class="totalPages"></span>
        </div>
        """,
    )
    browser.close()

os.remove(tmp_html)
print(f"Written {pdf_path}")
