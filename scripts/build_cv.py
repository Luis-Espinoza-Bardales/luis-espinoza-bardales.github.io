from __future__ import annotations

import html
import json
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
CV_DATA = ROOT / "data" / "cv.json"
PAPERS_DATA = ROOT / "data" / "papers.json"
TEACHING_DATA = ROOT / "data" / "teaching.json"
SITE_DATA = ROOT / "data" / "site.json"
OUTPUT = ROOT / "files" / "Espinoza_CV.pdf"

MAROON = colors.HexColor("#500000")
INK = colors.HexColor("#222222")
MUTED = colors.HexColor("#666666")
LINE = colors.HexColor("#D6D3C4")
LIGHT = colors.HexColor("#F6F6F6")
LINK_BLUE = "#0563C1"

FONT_REGULAR = "Times-Roman"
FONT_BOLD = "Times-Bold"
FONT_ITALIC = "Times-Italic"
BOLD_ITALIC = "Times-BoldItalic"

OWN_NAME_VARIANTS = [
    "Luis M. Espinoza Bardales",
    "Luis M. Espinoza",
    "Luis Espinoza",
    "Luis Miguel Espinoza Bardales",
    "Luis Miguel Espinoza",
    "Espinoza, L.",
    "Espinoza, Luis Miguel",
    "Espinoza Bardales, Luis Miguel",
]


def register_cv_fonts() -> str:
    """Use a Palatino-style family when available, matching Ben Helms's CV more closely."""
    global FONT_REGULAR, FONT_BOLD, FONT_ITALIC, BOLD_ITALIC

    candidates = [
        (
            "TeXGyrePagellaCV",
            {
                "regular": Path("/usr/share/texmf/fonts/opentype/public/tex-gyre/texgyrepagella-regular.otf"),
                "bold": Path("/usr/share/texmf/fonts/opentype/public/tex-gyre/texgyrepagella-bold.otf"),
                "italic": Path("/usr/share/texmf/fonts/opentype/public/tex-gyre/texgyrepagella-italic.otf"),
                "boldItalic": Path("/usr/share/texmf/fonts/opentype/public/tex-gyre/texgyrepagella-bolditalic.otf"),
            },
        ),
        (
            "TeXGyrePagellaCV",
            {
                "regular": Path("/usr/share/fonts/opentype/tex-gyre/texgyrepagella-regular.otf"),
                "bold": Path("/usr/share/fonts/opentype/tex-gyre/texgyrepagella-bold.otf"),
                "italic": Path("/usr/share/fonts/opentype/tex-gyre/texgyrepagella-italic.otf"),
                "boldItalic": Path("/usr/share/fonts/opentype/tex-gyre/texgyrepagella-bolditalic.otf"),
            },
        ),
        (
            "PalatinoCV",
            {
                "regular": Path("C:/Windows/Fonts/pala.ttf"),
                "bold": Path("C:/Windows/Fonts/palab.ttf"),
                "italic": Path("C:/Windows/Fonts/palai.ttf"),
                "boldItalic": Path("C:/Windows/Fonts/palabi.ttf"),
            },
        ),
    ]
    for family, paths in candidates:
        if all(path.exists() for path in paths.values()):
            try:
                pdfmetrics.registerFont(TTFont(family, str(paths["regular"])))
                pdfmetrics.registerFont(TTFont(f"{family}-Bold", str(paths["bold"])))
                pdfmetrics.registerFont(TTFont(f"{family}-Italic", str(paths["italic"])))
                pdfmetrics.registerFont(TTFont(f"{family}-BoldItalic", str(paths["boldItalic"])))
            except Exception:
                continue
            pdfmetrics.registerFontFamily(
                family,
                normal=family,
                bold=f"{family}-Bold",
                italic=f"{family}-Italic",
                boldItalic=f"{family}-BoldItalic",
            )
            FONT_REGULAR = family
            FONT_BOLD = f"{family}-Bold"
            FONT_ITALIC = f"{family}-Italic"
            BOLD_ITALIC = f"{family}-BoldItalic"
            return family
    return FONT_REGULAR


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def esc(value: object) -> str:
    return html.escape(str(value or ""), quote=True)


def compact(value: str) -> str:
    return " ".join(str(value or "").split())


def local_to_public(url: str, website: str) -> str:
    if not url:
        return ""
    if url.startswith(("http://", "https://", "mailto:")):
        return url
    return website.rstrip("/") + "/" + url.lstrip("/")


def primary_link(paper: dict, website: str) -> str:
    for link in paper.get("links", []):
        if link.get("primary"):
            return local_to_public(link.get("url", ""), website)
    return ""


def publication_link(paper: dict, website: str) -> str:
    for link in paper.get("links", []):
        url = link.get("url", "")
        if not link.get("primary") and url.startswith(("http://", "https://")):
            return url
    return primary_link(paper, website)


def link_text(text: str, url: str = "") -> str:
    if not url:
        return text
    return f'<a href="{esc(url)}"><font color="{LINK_BLUE}"><u>{text}</u></font></a>'


def quoted_title(title: str, url: str = "") -> str:
    return link_text(f"&ldquo;{esc(title)}&rdquo;", url)


def italic_title(title: str, url: str = "") -> str:
    return link_text(f"<i>{esc(title)}</i>", url)


def format_name_list(names: list[str]) -> str:
    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        return f"{names[0]} and {names[1]}"
    return f"{', '.join(names[:-1])}, and {names[-1]}"


def final_punctuation(text: str) -> str:
    return "" if str(text or "").strip().endswith((".", "?", "!")) else "."


def year_value(text: str) -> int:
    match = re.search(r"\d{4}", str(text or ""))
    return int(match.group(0)) if match else -1


def coauthor_credit(authors: str) -> str:
    if not authors:
        return ""
    normalized = compact(authors).replace(", and ", ", ")
    names = [name.strip() for name in re.split(r"\s+(?:and|&)\s+|,\s*", normalized) if name.strip()]
    own_names = {compact(name).lower() for name in OWN_NAME_VARIANTS}
    coauthors = [name for name in names if compact(name).lower() not in own_names]
    if not coauthors:
        return ""
    return "with " + format_name_list(coauthors)


def bold_own_name(text: str) -> str:
    escaped = esc(text)
    for variant in OWN_NAME_VARIANTS:
        escaped = escaped.replace(esc(variant), f"<b>{esc(variant)}</b>")
    return escaped


def make_styles() -> dict[str, ParagraphStyle]:
    sample = getSampleStyleSheet()
    return {
        "name": ParagraphStyle(
            "Name",
            parent=sample["Normal"],
            fontName=FONT_BOLD,
            fontSize=17,
            leading=20,
            alignment=TA_CENTER,
            textColor=INK,
            spaceAfter=3,
        ),
        "contact": ParagraphStyle(
            "Contact",
            parent=sample["Normal"],
            fontName=FONT_REGULAR,
            fontSize=9,
            leading=11,
            alignment=TA_CENTER,
            textColor=INK,
        ),
        "updated": ParagraphStyle(
            "Updated",
            parent=sample["Normal"],
            fontName=FONT_REGULAR,
            fontSize=8,
            leading=10,
            alignment=TA_CENTER,
            textColor=MUTED,
        ),
        "section": ParagraphStyle(
            "Section",
            parent=sample["Normal"],
            fontName=FONT_BOLD,
            fontSize=9,
            leading=11,
            textColor=MAROON,
            spaceBefore=9,
            spaceAfter=3,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=sample["Normal"],
            fontName=FONT_REGULAR,
            fontSize=9.1,
            leading=11.2,
            textColor=INK,
        ),
        "body_small": ParagraphStyle(
            "BodySmall",
            parent=sample["Normal"],
            fontName=FONT_REGULAR,
            fontSize=8.6,
            leading=10.2,
            textColor=INK,
        ),
        "meta": ParagraphStyle(
            "Meta",
            parent=sample["Normal"],
            fontName=FONT_ITALIC,
            fontSize=8.7,
            leading=10.2,
            textColor=MUTED,
        ),
        "date": ParagraphStyle(
            "Date",
            parent=sample["Normal"],
            fontName=FONT_REGULAR,
            fontSize=8.8,
            leading=10.5,
            alignment=TA_RIGHT,
            textColor=INK,
        ),
        "link": ParagraphStyle(
            "Link",
            parent=sample["Normal"],
            fontName=FONT_REGULAR,
            fontSize=8.8,
            leading=10.2,
            textColor=MAROON,
        ),
    }


def paragraph(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(text, style)


def section(story: list, title: str, styles: dict[str, ParagraphStyle]) -> None:
    story.append(paragraph(title.upper(), styles["section"]))
    story.append(HRFlowable(width="100%", thickness=0.4, color=LINE, spaceBefore=0, spaceAfter=4))


def dated_row(
    left: str,
    right: str,
    styles: dict[str, ParagraphStyle],
    left_style: str = "body",
) -> Table:
    table = Table(
        [[paragraph(left, styles[left_style]), paragraph(right, styles["date"])]],
        colWidths=[6.0 * inch, 0.95 * inch],
        hAlign="LEFT",
    )
    table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 1),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5),
            ]
        )
    )
    return table


def header(story: list, cv: dict, styles: dict[str, ParagraphStyle]) -> None:
    profile = cv["profile"]
    story.append(paragraph(esc(profile["name"]), styles["name"]))
    story.append(paragraph(esc(profile["title"]), styles["contact"]))
    story.append(paragraph(esc(profile["department"]), styles["contact"]))
    story.append(paragraph(esc(profile["institution"]), styles["contact"]))
    contact_items = [
        f'<a href="mailto:{esc(profile["email"])}">{esc(profile["email"])}</a>',
        f'<a href="{esc(profile["website"])}">website</a>',
        f'<a href="{esc(profile["googleScholar"])}">Google Scholar</a>',
        f'<a href="{esc(profile["orcid"])}">ORCID</a>',
    ]
    story.append(paragraph(" &nbsp;|&nbsp; ".join(contact_items), styles["contact"]))
    story.append(paragraph(f"Last updated: {esc(cv['lastUpdated'])}", styles["updated"]))
    story.append(Spacer(1, 6))


def add_appointments(story: list, cv: dict, styles: dict[str, ParagraphStyle]) -> None:
    items = cv.get("appointments", [])
    if not items:
        return
    section(story, "Academic Appointments", styles)
    for item in items:
        left = f"<b>{esc(item['organization'])}</b>, {esc(item['unit'])}<br/>{esc(item['role'])}"
        story.append(dated_row(left, esc(item["dates"]), styles))


def add_education(story: list, cv: dict, styles: dict[str, ParagraphStyle]) -> None:
    items = cv.get("education", [])
    if not items:
        return
    section(story, "Education", styles)
    for item in items:
        left = f"<b>{esc(item['institution'])}</b><br/>{esc(item['degree'])}"
        story.append(dated_row(left, esc(item["year"]), styles))


def add_fields(story: list, cv: dict, styles: dict[str, ParagraphStyle]) -> None:
    fields = cv.get("fields", [])
    if not fields:
        return
    section(story, "Research Fields", styles)
    story.append(paragraph(", ".join(esc(field) for field in fields), styles["body"]))


def undated_item(text: str, styles: dict[str, ParagraphStyle], style: str = "body") -> KeepTogether:
    return KeepTogether([paragraph(text, styles[style]), Spacer(1, 3)])


def working_paper_item(paper: dict, styles: dict[str, ParagraphStyle], website: str) -> KeepTogether:
    text = quoted_title(paper["title"], primary_link(paper, website))
    coauthors = coauthor_credit(paper.get("authors", ""))
    if coauthors:
        text += f' <font color="#666666">({esc(coauthors)})</font>'
    return undated_item(text, styles)


def progress_item(item: dict, styles: dict[str, ParagraphStyle]) -> KeepTogether:
    title = quoted_title(item["title"], item.get("url", ""))
    coauthors = coauthor_credit(item.get("authors", ""))
    if coauthors:
        title += f' <font color="#666666">({esc(coauthors)})</font>'
    return undated_item(title, styles)


def publication_details(paper: dict) -> str:
    return paper.get("publicationDetails") or paper.get("status", "")


def citation_authors(item: dict) -> str:
    return item.get("citationAuthors") or item.get("authors", "")


def publication_details_markup(paper: dict) -> str:
    if paper.get("bookTitle"):
        editors = paper.get("bookEditors", "")
        book = italic_title(paper["bookTitle"])
        publisher = paper.get("publisher", "")
        details = f"In {esc(editors)}, {book}" if editors else f"In {book}"
        if publisher:
            details += f". {esc(publisher)}"
        return details
    return esc(publication_details(paper))


def publication_item(paper: dict, styles: dict[str, ParagraphStyle], website: str) -> KeepTogether:
    authors = citation_authors(paper)
    left = (
        f"{esc(authors)}{final_punctuation(authors)} "
        f"{quoted_title(paper['title'], publication_link(paper, website))}{final_punctuation(paper['title'])}"
    )
    details = publication_details_markup(paper)
    if details:
        left += f" {details}{final_punctuation(details)}"
    return KeepTogether([dated_row(left, esc(paper.get("year", "")), styles, left_style="body_small")])


def extra_publication_item(item: dict, styles: dict[str, ParagraphStyle], website: str) -> KeepTogether:
    url = local_to_public(item.get("url", ""), website)
    left = ""
    authors = citation_authors(item)
    if authors:
        left += f"{esc(authors)}{final_punctuation(authors)} "
    left += f"{quoted_title(item['title'], url)}{final_punctuation(item['title'])}"
    details = ""
    if item.get("bookTitle"):
        editors = item.get("editors", "")
        details = f"In {esc(editors)}, {italic_title(item['bookTitle'])}" if editors else f"In {italic_title(item['bookTitle'])}"
        if item.get("volume"):
            details += f", {esc(item['volume'])}"
        if item.get("publisher"):
            details += f". {esc(item['publisher'])}"
    if item.get("journal"):
        details = italic_title(item["journal"])
        if item.get("details"):
            details += f", {esc(item['details'])}"
    if item.get("details"):
        details = details or esc(item["details"])
    if details:
        left += f" {details}{final_punctuation(details)}"
    return KeepTogether([dated_row(left, esc(item.get("year", "")), styles, left_style="body_small")])


def add_research(story: list, cv: dict, papers: list[dict], styles: dict[str, ParagraphStyle]) -> None:
    website = cv["profile"]["website"]
    working = [
        paper
        for paper in papers
        if paper.get("category") == "Working Papers" and primary_link(paper, website)
    ]
    progress = [paper for paper in papers if paper.get("category") == "Work in Progress"]
    extras = cv.get("additionalResearchProjects", [])
    unlinked_working = [
        paper
        for paper in papers
        if paper.get("category") == "Working Papers" and not primary_link(paper, website)
    ]

    if working:
        section(story, "Working Papers", styles)
        for paper in working:
            story.append(working_paper_item(paper, styles, website))

    in_progress = [*progress, *unlinked_working, *extras]
    if in_progress:
        section(story, "Work in Progress", styles)
        for item in in_progress:
            story.append(progress_item(item, styles))


def add_publications(story: list, cv: dict, papers: list[dict], styles: dict[str, ParagraphStyle]) -> None:
    website = cv["profile"]["website"]
    selected = [
        paper
        for paper in papers
        if paper.get("category") in {"Policy Papers", "Book Chapters"}
    ]
    extras = cv.get("additionalPublications", [])
    if not (selected or extras):
        return

    section(story, "Other Publications", styles)
    entries = [
        (year_value(paper.get("year", "")), index, "paper", paper)
        for index, paper in enumerate(selected)
    ]
    offset = len(entries)
    entries.extend(
        (year_value(item.get("year", "")), offset + index, "extra", item)
        for index, item in enumerate(extras)
    )
    for _, _, kind, item in sorted(entries, key=lambda entry: (-entry[0], entry[1])):
        if kind == "paper":
            story.append(publication_item(item, styles, website))
        else:
            story.append(extra_publication_item(item, styles, website))


def add_awards(story: list, cv: dict, styles: dict[str, ParagraphStyle]) -> None:
    items = cv.get("awards", [])
    if not items:
        return
    first, *rest = items
    story.append(
        KeepTogether(
            [
                paragraph("GRANTS, FELLOWSHIPS, AND AWARDS", styles["section"]),
                HRFlowable(width="100%", thickness=0.4, color=LINE, spaceBefore=0, spaceAfter=4),
                dated_row(esc(first["name"]), esc(first["year"]), styles),
            ]
        )
    )
    for item in rest:
        story.append(dated_row(esc(item["name"]), esc(item["year"]), styles))


def add_presentations(story: list, cv: dict, styles: dict[str, ParagraphStyle]) -> None:
    items = cv.get("presentations", [])
    if not items:
        return
    section(story, "Presentations and Seminars", styles)
    for item in items:
        story.append(dated_row(esc(item["venue"]), esc(item["dates"]), styles))


def add_teaching(story: list, teaching: list[dict], styles: dict[str, ParagraphStyle]) -> None:
    if not teaching:
        return
    section(story, "Teaching", styles)
    story.append(paragraph("<i>U = Undergraduate course; M = Master's course</i>", styles["meta"]))
    story.append(Spacer(1, 2))
    for index, block in enumerate(teaching):
        courses = block.get("courses", [])
        if not courses:
            continue
        heading = f"<b>{esc(block['title'])}</b>, {esc(block['institution'])}<br/><font color=\"#666666\">{esc(block.get('role', ''))}</font>"
        course_lines = []
        for course in courses:
            meta = []
            syllabus = course.get("syllabus")
            if course.get("terms"):
                meta.append(esc(course["terms"]))
            if course.get("levelCode"):
                meta.append(esc(course["levelCode"]))
            suffix = f" ({'; '.join(meta)})" if meta else ""
            syllabus_link = f" {link_text('[Syllabus]', syllabus['url'])}" if syllabus else ""
            course_lines.append(f"{esc(course['name'])}{suffix}{syllabus_link}")
        story.append(KeepTogether([paragraph(heading, styles["body"]), paragraph("<br/>".join(course_lines), styles["body_small"])]))
        if index < len(teaching) - 1:
            story.append(Spacer(1, 7))


def add_service(story: list, cv: dict, styles: dict[str, ParagraphStyle]) -> None:
    items = cv.get("service", [])
    if not items:
        return
    section(story, "Professional Service", styles)
    for item in items:
        story.append(paragraph(f"{esc(item['type'])}: <i>{esc(item['venue'])}</i>", styles["body"]))


def add_experience(story: list, cv: dict, styles: dict[str, ParagraphStyle]) -> None:
    groups = [group for group in cv.get("experience", []) if group.get("items")]
    if not groups:
        return
    section(story, "Research and Professional Experience", styles)
    for group in groups:
        story.append(paragraph(f"<b>{esc(group['section'])}</b>", styles["body"]))
        for item in group["items"]:
            left = f"{esc(item['role'])}, {esc(item['organization'])}"
            story.append(dated_row(left, esc(item["dates"]), styles, left_style="body_small"))
        story.append(Spacer(1, 2))


def add_training(story: list, cv: dict, styles: dict[str, ParagraphStyle]) -> None:
    items = cv.get("training", [])
    if not items:
        return
    section(story, "Training", styles)
    for item in items:
        left = f"{esc(item['name'])}, {esc(item['institution'])}"
        story.append(dated_row(left, esc(item["year"]), styles))


def add_skills(story: list, cv: dict, styles: dict[str, ParagraphStyle]) -> None:
    parts = []
    if cv.get("languages"):
        parts.append(f"<b>Languages:</b> {', '.join(esc(item) for item in cv['languages'])}")
    if cv.get("software"):
        parts.append(f"<b>Software:</b> {', '.join(esc(item) for item in cv['software'])}")
    if not parts:
        return
    section(story, "Languages and Software", styles)
    story.append(paragraph("<br/>".join(parts), styles["body"]))


def on_page(canvas, doc) -> None:
    canvas.saveState()
    canvas.setTitle("Luis M. Espinoza Bardales - Curriculum Vitae")
    canvas.setAuthor("Luis M. Espinoza Bardales")
    canvas.setSubject("Curriculum Vitae")
    canvas.setFont(FONT_REGULAR, 8)
    canvas.setFillColor(MUTED)
    footer = f"Luis M. Espinoza Bardales - Curriculum Vitae - {doc.page}"
    canvas.drawCentredString(letter[0] / 2, 0.38 * inch, footer)
    canvas.restoreState()


def build() -> None:
    cv = load_json(CV_DATA)
    papers = load_json(PAPERS_DATA)
    teaching = load_json(TEACHING_DATA)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    register_cv_fonts()
    styles = make_styles()
    story: list = []

    header(story, cv, styles)
    add_appointments(story, cv, styles)
    add_education(story, cv, styles)
    add_fields(story, cv, styles)
    add_research(story, cv, papers, styles)
    add_publications(story, cv, papers, styles)
    add_awards(story, cv, styles)
    add_presentations(story, cv, styles)
    add_teaching(story, teaching, styles)
    add_service(story, cv, styles)
    add_skills(story, cv, styles)

    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=letter,
        leftMargin=0.78 * inch,
        rightMargin=0.78 * inch,
        topMargin=0.62 * inch,
        bottomMargin=0.62 * inch,
        title="Luis M. Espinoza Bardales - Curriculum Vitae",
        author="Luis M. Espinoza Bardales",
    )
    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    print(f"Built {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    build()
