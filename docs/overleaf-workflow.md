# Overleaf-to-Website Workflow

This site is set up so each paper has one stable "Most recent version" link in `data/papers.json`.

## The simple workflow

1. Replace the PDF in `files/` with the newest draft.
2. Update that paper's `updated` date in `data/papers.json`.
3. Commit and push the website.

The site automatically shows `new!` for papers updated in the last 90 days.

## The automated workflow

Overleaf has two official premium options that can support automation:

- Git integration: each Overleaf project can be cloned/pulled as a Git repository.
- GitHub synchronization: an Overleaf project can be linked to a GitHub repository.

Recommended automation design:

1. Keep each paper in Overleaf.
2. Use Overleaf Git or GitHub synchronization to make the TeX source available to GitHub Actions.
3. Have a GitHub Action compile the paper, copy the PDF into this website's `files/` folder, update the paper's `updated` date, and commit the result.
4. The website immediately points to the newest PDF because the URL does not change.
5. If the draft's figures changed, update the `thumbnail` page/image selection in `data/papers.json` and rerun `scripts/generate_research_thumbnails.py`.

This repository includes `.github/workflow-templates/overleaf-sync.yml.example` as a starter. Rename it into `.github/workflows/` only after the Overleaf project, GitHub secret, and LaTeX build command are confirmed.

Official docs:

- https://docs.overleaf.com/integrations-and-add-ons/git-integration-and-github-synchronization/git
- https://docs.overleaf.com/integrations-and-add-ons/git-integration-and-github-synchronization/github-synchronization

Important note: Overleaf states that Git integration and GitHub synchronization are premium features. If you do not have Overleaf premium or Overleaf Commons access, use the simple workflow above or publish PDFs through a stable external service such as OSF, Dropbox, or Google Drive and paste that stable URL into `data/papers.json`.
