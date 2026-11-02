"""
AiSpy — turn the report template into a one-page A4 PDF.

What this does:
  1. reads aispy-report-template.html
  2. replaces __FONTS__ with embedded @font-face rules (Inter + JetBrains Mono)
  3. replaces __LOGO__ with the AiSpy wordmark SVG
  4. prints the result to PDF with headless Chromium

Why fonts are embedded rather than linked: the PDF must look identical
everywhere, including when printed, and must not depend on an internet
connection at the moment it is generated.

Setup (once):
    pip install playwright
    playwright install chromium

Fonts needed in ./fonts/ :
    Inter-Regular.ttf  Inter-Medium.ttf  Inter-SemiBold.ttf
    Inter-Bold.ttf     Inter-ExtraBold.ttf
    JetBrainsMono-Regular.ttf  JetBrainsMono-Medium.ttf

Both are free for commercial use:
    Inter           https://github.com/rsms/inter/releases
    JetBrains Mono  https://github.com/JetBrains/JetBrainsMono/releases

Run:
    python generate-report.py
"""

import base64
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).parent
TEMPLATE = HERE / "aispy-report-template.html"
LOGO = HERE / "logo.svg"
FONT_DIR = HERE / "fonts"
OUTPUT = HERE / "aispy-check.pdf"

FONTS = [
    ("Inter", 400, "Inter-Regular.ttf"),
    ("Inter", 500, "Inter-Medium.ttf"),
    ("Inter", 600, "Inter-SemiBold.ttf"),
    ("Inter", 700, "Inter-Bold.ttf"),
    ("Inter", 800, "Inter-ExtraBold.ttf"),
    ("JetBrains Mono", 400, "JetBrainsMono-Regular.ttf"),
    ("JetBrains Mono", 500, "JetBrainsMono-Medium.ttf"),
]


def font_css() -> str:
    rules = []
    for family, weight, filename in FONTS:
        data = base64.b64encode((FONT_DIR / filename).read_bytes()).decode()
        rules.append(
            f"@font-face{{font-family:'{family}';font-style:normal;"
            f"font-weight:{weight};"
            f"src:url(data:font/ttf;base64,{data}) format('truetype');}}"
        )
    return "\n".join(rules)


def logo_svg() -> str:
    svg = LOGO.read_text()
    # strip the fixed size so CSS controls it, crop to the artwork,
    # and make the dark lettering white for the dark header
    svg = svg.replace(' width="2000"', "").replace(' height="1000"', "")
    svg = svg.replace('viewBox="0 0 1500 749.999995"', 'viewBox="8 156 1485 519"')
    svg = svg.replace('fill="#000000"', 'fill="#FFFFFF"')
    svg = svg.replace("<svg ", '<svg class="logo" ', 1)
    return svg


def build_html() -> str:
    html = TEMPLATE.read_text()
    return html.replace("__FONTS__", font_css()).replace("__LOGO__", logo_svg())


def render(html: str, out_path: Path) -> None:
    tmp = HERE / "_built.html"
    tmp.write_text(html)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(tmp.as_uri(), wait_until="networkidle")

        # The layout is designed to fill exactly one A4 page (1123 CSS px at
        # 96dpi). If content grows past that it silently spills onto page 2,
        # so fail loudly instead.
        height = page.evaluate("document.body.scrollHeight")
        if height > 1123:
            print(f"WARNING: content is {height}px tall, A4 is 1123px — "
                  f"this will run to two pages. Trim it.")

        page.pdf(
            path=str(out_path),
            format="A4",
            print_background=True,
            margin={"top": "0", "bottom": "0", "left": "0", "right": "0"},
        )
        browser.close()
    tmp.unlink()


if __name__ == "__main__":
    render(build_html(), OUTPUT)
    print(f"written: {OUTPUT}")
