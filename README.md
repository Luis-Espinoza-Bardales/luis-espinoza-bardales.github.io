# Luis M. Espinoza Bardales academic website

This is a lightweight static website for GitHub Pages. It does not require Ruby, Jekyll, npm, or a build step.

## Common updates

- Homepage text: edit `index.html`.
- Papers: edit `data/papers.json`.
- Teaching: edit `data/teaching.json`.
- CV-only material: edit `data/cv.json`.
- Contact/profile links: edit `data/site.json`.
- PDFs: replace files in `files/`.
- Research thumbnails from real PDF figures/images: run `python scripts/generate_research_thumbnails.py`.
- Generated CV PDF: run `python scripts/build_cv.py`.
- New draft badge only: run `python scripts/mark_paper_updated.py paper-slug`.

## Paper fields

Each paper in `data/papers.json` has:

- `title`, `authors`, `year`, `category`, `abstract`, and `citation`.
- `updated`, which controls the automatic `new!` badge for 90 days.
- `links`, where the primary link should be the stable "Most recent version" PDF.
- `featured`, which controls whether the paper appears on the homepage.

## Publishing

Push these files to `Luis-Espinoza-Bardales/luis-espinoza-bardales.github.io`. GitHub Pages can serve this directly from the repository root.

## Overleaf automation

See `docs/overleaf-workflow.md`.

## CV automation

See `docs/cv-workflow.md`. The CV PDF is generated from `data/cv.json`, `data/papers.json`, and `data/teaching.json`.

## Managing the site

See `docs/website-management-guide.md` for a plain-language explanation of where everything lives, how GitHub Pages works, what costs money, and how to update papers.
