# AI Spy — website

Two static pages. No build step, no framework, nothing to install.

## Files

| File | What it is |
|---|---|
| `index.html` | The homepage. Served at aispy.ie |
| `check.html` | The free check request page. Served at aispy.ie/check |
| `sample-report.pdf` | The sample report the homepage links to |
| `logo.svg` | The AI Spy logo, for use outside the site |
| `aispy-report-template.html` | Source of the one-page report (see below) |
| `generate-report.py` | Turns that template into a PDF |
| `vercel.json` | Serves pages without the .html extension |
| `.gitignore` | Keeps OS and build clutter out of the repo |

## Deploying on Vercel

1. Put these files in the root of the repo — not in a subfolder.
2. Vercel rebuilds automatically when you commit.
3. Framework preset: **Other**. Leave build and output settings empty.

The homepage file must be called `index.html`. Anything else gets its own address instead.

`vercel.json` sets `cleanUrls`, which is what lets `check.html` be served at `/check`. Without it those links 404.

## Before it goes live

**1. The free check form doesn't send anywhere yet.**
Near the bottom of `check.html` there is a line:

```js
var ENDPOINT = "REPLACE_WITH_ENDPOINT";
```

Until that is a real address, the form shows its confirmation but nothing reaches Brendan. Point it at whatever already receives free check requests and triggers a report.

**2. The sample report is fiction.**
Kilbride Dental and its competitors are invented, and the report says so in the header and the footer. Keep those labels if the sample is ever regenerated — putting real competitor names next to "BIGGEST THREAT" on a public page invites trouble.

**3. The testimonial.**
If one goes on the homepage, use a real name and note any connection to the founder.

## The report

`aispy-report-template.html` is a single A4 page with two placeholders, `__FONTS__` and `__LOGO__`, filled at generation time. `generate-report.py` does that and prints the PDF with headless Chromium.

The layout fills exactly one A4 page (1123 CSS px at 96dpi). Longer business names or question text push it over and it spills silently onto a second page — the script warns when that happens.

## Design

- **Violet** `#5E17EB`, from the logo. The dark colour scheme uses `#9A6BFF`.
- **Inter** for anything you read as words; **JetBrains Mono** for anything you read as data — labels, codes, scores, section numbers. Keeping that split is what makes the pages read as an instrument rather than a brochure.
- Both pages follow the visitor's light or dark system setting.
- The feature images on the homepage are crops of the report, embedded in the page. If the report design changes, they need re-exporting or they will go stale.
