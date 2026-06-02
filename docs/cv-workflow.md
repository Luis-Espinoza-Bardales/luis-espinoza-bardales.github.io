# CV Workflow

The website now treats the CV as a generated file.

## Source files

- `data/cv.json`: CV-only information such as education, presentations, grants, experience, service, languages, and skills.
- `data/papers.json`: working papers, policy papers, book chapters, abstracts, and PDF links.
- `data/teaching.json`: teaching history.
- `scripts/build_cv.py`: reads those data files and creates `files/Espinoza_CV.pdf` plus the website-linked copy `files/Espinoza_CV_current.pdf`.
- `requirements-cv.txt`: Python package needed by the CV builder.

The generator skips empty sections and groups thin categories together, so the CV stays compact as your record evolves.

## Local update

After editing any CV-related data, run:

```powershell
& 'C:\Users\Luis\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts\build_cv.py
```

The homepage `Download CV` button points to `files/Espinoza_CV_current.pdf`.

## Automatic update on GitHub

The workflow `.github/workflows/build-cv.yml` rebuilds the CV whenever one of these files changes:

- `data/cv.json`
- `data/papers.json`
- `data/teaching.json`
- `scripts/build_cv.py`
- `requirements-cv.txt`

It commits the regenerated `files/Espinoza_CV.pdf` and `files/Espinoza_CV_current.pdf` back to the repository automatically.

## What still needs manual updating

The CV updates automatically from structured data, but the data itself still needs to be kept current. When you add a new paper or course to the website data, it will flow into the CV. Presentations, awards, service, research experience, and professional experience live in `data/cv.json`.
