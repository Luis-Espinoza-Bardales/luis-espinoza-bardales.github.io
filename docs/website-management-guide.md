# Website Management Guide

This site is a static GitHub Pages website. That means it is just files: HTML, CSS, JavaScript, images, PDFs, and JSON data. There is no server bill, no database, and no AcademicPages/Jekyll machinery.

## Where the files are stored

On this computer, the website files are stored here:

`C:\Users\Luis\Documents\Personal website`

The important files are:

- `index.html`: the homepage/about page.
- `research.html`: the research page.
- `teaching.html`: the teaching page.
- `assets/css/styles.css`: the visual design.
- `assets/js/main.js`: the small script that reads your data files and builds the research/teaching lists.
- `data/papers.json`: the paper list, paper abstracts, PDF links, and new-badge dates.
- `data/teaching.json`: the teaching list.
- `data/cv.json`: CV-only information such as presentations, awards, experience, service, languages, and skills.
- `data/site.json`: profile/contact metadata, including the CV PDF path.
- `files/`: PDFs and other downloadable files.
- `assets/img/`: photos and research images.
- `docs/`: explanations for you.

## What the web address is

If this is pushed to your GitHub repository named `Luis-Espinoza-Bardales.github.io`, GitHub Pages will publish it at:

`https://luis-espinoza-bardales.github.io/`

That is the same address you already use.

## Do you need to pay?

No, not for the website as currently designed.

GitHub Pages is free for public repositories. Your site can stay at:

`https://luis-espinoza-bardales.github.io/`

You only need to pay if you want a custom domain such as:

`luisespinoza.com`

In that case, you would buy the domain from a registrar, usually around 10 to 25 dollars per year, and point it to GitHub Pages. GitHub still hosts the website for free.

## Are we still using GitHub?

Yes. The site is designed for GitHub Pages.

The difference is that we are no longer relying on the AcademicPages theme. This version is simpler: GitHub only needs to serve the files in the repository.

## Do you still need AcademicPages?

No, not for this redesigned version.

AcademicPages was the old theme/framework. Once this new version is safely pushed and you confirm the live site looks right, the old AcademicPages files can be removed from the repository. Do not delete the old repository itself unless you intentionally want to take the whole website offline. The repository name is still important because GitHub uses it to publish your website.

## How to update a paper

Open `data/papers.json`.

Each paper has a block like this:

```json
{
  "slug": "proximity-contract-enforcement-specialized-trade",
  "title": "Proximity as a Substitute of Contract Enforcement in Specialized Trade",
  "updated": "2026-03-17",
  "links": [
    {
      "label": "Most recent version",
      "url": "files/Institutions__trade_and_travel_2026-REStat.pdf",
      "primary": true
    }
  ]
}
```

To update the newest PDF:

1. Put the new PDF in `files/`.
2. In `data/papers.json`, make the `url` point to that PDF.
3. Change `updated` to today's date in `YYYY-MM-DD` format.
4. Commit and push to GitHub.

The red `new!` badge appears automatically for papers updated within the last 90 days.

## How research thumbnails work

The research thumbnails are not invented images. For papers with PDFs, `scripts/generate_research_thumbnails.py` extracts a selected embedded figure or image from the actual PDF.

In `data/papers.json`, each paper can have:

```json
"thumbnail": {
  "sourcePdf": "files/example-paper.pdf",
  "sourcePage": 22,
  "sourceImage": 0
}
```

- `sourcePdf` is the local PDF file.
- `sourcePage` is the page where the figure/image appears.
- `sourceImage` is which embedded image on that page to use, starting from 0.

After changing those values, run:

```powershell
python scripts/generate_research_thumbnails.py
```

If a project has no public draft yet, leave `image` blank and set `thumbnail` to `null`. The website will show a simple WIP marker instead of a fake figure.

## How bilingual publications work

Bilingual policy papers use one publication entry with a `versions` list. The first version is the default language shown when someone opens the paper.

```json
"versions": [
  {
    "code": "en",
    "label": "English",
    "links": [
      {
        "label": "English PDF",
        "url": "files/example_english.pdf",
        "primary": true
      }
    ]
  },
  {
    "code": "es",
    "label": "Spanish",
    "links": [
      {
        "label": "PDF en español",
        "url": "files/example_spanish.pdf",
        "primary": true
      }
    ]
  }
]
```

For the Growth Lab reports, English appears first by default. The modal has English/Spanish buttons that swap the title, abstract, citation, and links. The Growth Lab source link is included so readers can verify the publication record.

For Spanish-only publications, use `languageNote`, as in the PUCP book chapter.

## How the Texas A&M palette is used

The site uses Texas A&M's brand palette, centered on Aggie Maroon (`#500000`), with white and neutral gray/tan backgrounds. The main colors live in `assets/css/styles.css` near the top of the file.

## How to add a new paper

In `data/papers.json`, copy an existing paper block and paste it as a new item in the list.

Change:

- `slug`: short lowercase ID, with hyphens.
- `title`
- `authors`
- `year`
- `category`: for example `Working Papers`, `Policy Papers`, `Book Chapters`, or `Work in Progress`.
- `updated`
- `image`
- `short`
- `abstract`
- `citation`
- `links`

Then run:

```powershell
python scripts/generate_research_thumbnails.py
```

If Python on your machine does not recognize the image library, ask Codex to run the bundled Python version.

## How Overleaf fits in

The stable idea is this:

- Overleaf is where you write.
- GitHub Pages is where the public PDF appears.
- The website link should always be called `Most recent version`.

The simplest workflow is manual: download the PDF from Overleaf, put it in `files/`, update `data/papers.json`, and push.

The more automated workflow requires Overleaf premium or university/Commons access, because Overleaf's Git and GitHub sync features are premium. See `docs/overleaf-workflow.md`.

## What you should not edit casually

Avoid editing these unless you are changing the design or behavior:

- `assets/css/styles.css`
- `assets/js/main.js`
- `.github/workflow-templates/overleaf-sync.yml.example`

Most routine updates should happen in:

- `data/papers.json`
- `data/teaching.json`
- `data/site.json`
- `files/`

## How to update the CV

The site links directly to `files/Espinoza_CV.pdf`. That PDF is generated from structured data instead of edited by hand in Word.

Edit:

- `data/papers.json` for working papers, policy papers, and book chapters.
- `data/teaching.json` for courses.
- `data/cv.json` for presentations, awards, experience, service, languages, and skills.

Then run:

```powershell
python scripts/build_cv.py
```

On GitHub, `.github/workflows/build-cv.yml` rebuilds and commits the CV PDF automatically whenever the CV, paper, teaching, or build-script data changes. See `docs/cv-workflow.md`.

## How publishing works

The cycle is:

1. Edit files locally.
2. Preview locally.
3. Commit changes with Git.
4. Push to GitHub.
5. GitHub Pages updates the public site.

The public site usually updates within a minute or two after pushing.

## What to ask Codex for later

Good requests:

- "Add this new paper to my website."
- "Replace the PDF for my proximity paper and mark it new."
- "Update my teaching page with this course."
- "Show me what changed before we push."
- "Commit and push the website."

Less good requests:

- "Fix GitHub." GitHub has several parts. It is better to say what outcome you want, such as "publish the website" or "connect this folder to my GitHub repository."
