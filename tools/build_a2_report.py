"""Build the A2 report PDF and an identifier-free public Markdown copy."""

import argparse
import html
import json
from pathlib import Path
import re

import fitz
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "docs/a2/report-content.json").read_text(encoding="utf-8"))
REPO = "https://github.com/alwaysgoodz/aut-bug-report-helper"
TAG = "a2-submission-v1.0.1"
TREE = f"{REPO}/blob/{TAG}"
RELEASE = f"{REPO}/releases/tag/{TAG}"
INK = colors.HexColor("#182B37")
MUTED = colors.HexColor("#465C69")
TEAL = colors.HexColor("#11656B")
for name, file in (("A2", "calibri.ttf"), ("A2-Bold", "calibrib.ttf"), ("A2-Italic", "calibrii.ttf")):
    pdfmetrics.registerFont(TTFont(name, f"C:/Windows/Fonts/{file}"))
pdfmetrics.registerFontFamily("A2", normal="A2", bold="A2-Bold", italic="A2-Italic")
STYLES = {
    "body": ParagraphStyle("body", fontName="A2", fontSize=10.8, leading=13.5, spaceAfter=6, textColor=INK),
    "heading": ParagraphStyle("heading", fontName="A2-Bold", fontSize=14, leading=17, spaceBefore=8, spaceAfter=6, keepWithNext=True, textColor=INK),
    "cell": ParagraphStyle("cell", fontName="A2", fontSize=9.8, leading=12.1, textColor=INK),
    "headcell": ParagraphStyle("headcell", fontName="A2-Bold", fontSize=9.8, leading=12.1, textColor=INK),
    "caption": ParagraphStyle("caption", fontName="A2-Bold", fontSize=10, leading=13, spaceBefore=4, spaceAfter=5, keepWithNext=True, textColor=INK),
    "small": ParagraphStyle("small", fontName="A2", fontSize=9.4, leading=12.6, spaceAfter=7, textColor=MUTED),
    "ref": ParagraphStyle("ref", fontName="A2", fontSize=10.4, leading=14, leftIndent=36, firstLineIndent=-36, spaceAfter=10, textColor=INK),
    "title": ParagraphStyle("title", fontName="A2-Bold", fontSize=32, leading=36, spaceAfter=13, textColor=INK),
    "subtitle": ParagraphStyle("subtitle", fontName="A2", fontSize=16, leading=22, spaceAfter=16, textColor=TEAL),
}


def p(value, style="body", rich=False):
    markup = html.escape(value)
    if rich:
        markup = markup.replace("&lt;i&gt;", "<i>").replace("&lt;/i&gt;", "</i>")
        markup = re.sub(r"https://[^\s<]+", lambda m: f'<link color="#11656B" href="{m[0]}">{m[0]}</link>', markup)
    return Paragraph(markup, STYLES[style])


def link(label, url, style="body"):
    return Paragraph(f'<link color="#11656B" href="{html.escape(url)}">{html.escape(label)}</link>', STYLES[style])


def tab(headers, rows, widths):
    cells = [[p(x, "headcell") for x in headers], *[[p(x, "cell") for x in row] for row in rows]]
    result = Table(cells, colWidths=widths, repeatRows=1, hAlign="LEFT")
    result.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EAF2F3")),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LINEBELOW", (0, 0), (-1, 0), 0.75, TEAL),
        ("LINEBELOW", (0, 1), (-1, -1), 0.35, colors.HexColor("#CDDADD")),
    ]))
    return result


def furniture(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(MUTED)
    canvas.setFont("A2", 8.5)
    if doc.page > 1:
        canvas.drawString(24 * mm, A4[1] - 13 * mm, "ENSE701  /  BUG REPORT HELPER  /  ASSIGNMENT 2")
        canvas.setStrokeColor(colors.HexColor("#CDDADD"))
        canvas.line(24 * mm, A4[1] - 15 * mm, A4[0] - 24 * mm, A4[1] - 15 * mm)
    canvas.drawRightString(A4[0] - 24 * mm, 13 * mm, str(doc.page))
    canvas.restoreState()


def write_public_text():
    counted = []
    md = [
        "# " + DATA["title"],
        "Structured Bug Report Helper · ENSE701 Assignment 2",
        f"[Fixed source and demo]({RELEASE}) · [Evidence index](../docs/a2/evidence-index.md)",
    ]
    for section in DATA["sections"]:
        heading, paragraphs, after = section["heading"], section["paragraphs"], section.get("after", [])
        counted.extend([heading, *paragraphs])
        md.extend(["## " + heading, *paragraphs])
        if table := section.get("table"):
            headers, rows = table["headers"], table["rows"]
            counted.extend([table["caption"], *headers, *(cell for row in rows for cell in row)])
            md.extend([table["caption"], "\n".join(
                "| " + " | ".join(row) + " |" for row in [headers, ["---"] * len(headers), *rows]
            )])
        counted.extend(after)
        md.extend(after)
    main = "\n\n".join(counted)
    count = {"whitespace_words": len(main.split()),
             "conservative_tokens": len(re.findall(r"\b[\w]+(?:['’][\w]+)*\b", main)),
             "limit": 2500,
             "includes": "Main headings, paragraphs, table captions, headers/cells and in-text citations",
             "excludes": "Cover, references, supporting appendix and individual statements"}
    if count["conservative_tokens"] > count["limit"]:
        raise ValueError("A2 main text exceeds the conservative 2,500-word check")
    (ROOT / "docs/a2/word-count.json").write_text(json.dumps(count, indent=2) + "\n", encoding="utf-8")
    (ROOT / "docs/a2/main-text-counted.txt").write_text(main + "\n", encoding="utf-8")
    md.extend(["## References", *[x.replace("<i>", "*").replace("</i>", "*") for x in DATA["references"]],
               "## AI assistance", AI_NOTE])
    (ROOT / "submission-a2/assignment-2-report.md").write_text("\n\n".join(md) + "\n", encoding="utf-8")
    return count


AI_NOTE = (
    "OpenAI Codex was used to assist with the implementation and test artefacts, repository preparation, "
    "source review, and drafting and formatting this report. The report links the underlying evidence and identifies "
    "observations from AI-assisted technical work. The submitters are responsible for checking the report, "
    "verifying any account-to-member attribution, and completing their own contribution statements."
)


def build(output, team_file, qa_dir, sha):
    count = write_public_text()
    team = json.loads(team_file.read_text(encoding="utf-8"))["members"]
    if len(team) != 4 or any(not (member["name"] and member["student_id"]) for member in team):
        raise ValueError("The Canvas cover requires all four members' names and student IDs")
    story = [
        Spacer(1, 24 * mm), p("GROUP EVALUATION REPORT  /  ASSIGNMENT 2", "caption"), Spacer(1, 5 * mm),
        p(DATA["title"], "title"), p(DATA["subtitle"], "subtitle"),
        p("Auckland University of Technology", "body"),
        p("ENSE701 · Contemporary Methods in Software Engineering", "body"),
        p("CJLU BCIS Cycle 13 · 2026 A2", "small"), Spacer(1, 4 * mm),
        tab(["Group member", "Student ID"], [[m["name"], m["student_id"]] for m in team], [251, 195]),
        Spacer(1, 8 * mm), link("Fixed software release and demonstration package", RELEASE),
        link("Open the assessment evidence index", TREE + "/docs/a2/evidence-index.md"),
        p(f"Submission commit {sha}" if sha else f"Fixed release {TAG}", "small"),
        p(f'Main text {count["whitespace_words"]:,} words including tables and citations', "small"),
        PageBreak(),
    ]
    widths = [[126, 156, 164], [155, 160, 131], [179, 126, 141], [94, 177, 175]]
    table_number = 0
    for section in DATA["sections"]:
        if section.get("new_page"):
            story.append(PageBreak())
        story.append(p(section["heading"], "heading"))
        story.extend(p(value) for value in section["paragraphs"])
        if table := section.get("table"):
            story.extend([p(table["caption"], "caption"), tab(table["headers"], table["rows"], widths[table_number]), Spacer(1, 7)])
            table_number += 1
        story.extend(p(value) for value in section.get("after", []))
    story.extend([PageBreak(), p("References", "heading")])
    story.extend(p(value, "ref", rich=True) for value in DATA["references"])
    story.extend([
        PageBreak(), p("Appendix A  Supporting evidence", "heading"),
        link("Open the complete evidence index and raw results", TREE + "/docs/a2/evidence-index.md"),
        link("E1  Assignment 1 baseline and requirements traceability", TREE + "/docs/a2/traceability.md"),
        link("E2  Iteration 1 review, acceptance and retrospective", TREE + "/docs/a2/iteration-1.md"),
        link("E3  Iteration 2 and the prospective process measures", TREE + "/docs/a2/process-improvement-plan.md"),
        link("E4  Demo-version benchmark data and source fingerprints", TREE + "/docs/a2/evidence/final/performance.json"),
        link("E5  Demonstration rehearsal and reproduction evidence", TREE + "/docs/a2/evidence/final/offline-rehearsal.json"),
        link("E6  Review and issue snapshot", TREE + "/docs/a2/evidence/final/requirements-and-reviews.json"),
        link("E7  Individual contribution evidence worksheet", TREE + "/docs/a2/contribution-evidence.md"),
        p("AI assistance", "heading"), p(AI_NOTE, "small"),
        p("Figure A1. Guided completion during the Software Demo 1.0.1 rehearsal", "caption"),
        Image(str(ROOT / "docs/a2/evidence/final/guidance-86.png"), width=446, height=291, kind="proportional"),
        link("Open the original-resolution rehearsal screenshot", TREE + "/docs/a2/evidence/final/guidance-86.png", "small"),
    ])
    output.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(output), pagesize=A4, leftMargin=24 * mm, rightMargin=24 * mm,
                            topMargin=22 * mm, bottomMargin=19 * mm, title=DATA["title"],
                            author=", ".join(m["name"] for m in team))
    doc.build(story, onFirstPage=furniture, onLaterPages=furniture)
    qa_dir.mkdir(parents=True, exist_ok=True)
    with fitz.open(output) as pdf:
        for i, page in enumerate(pdf, start=1):
            page.get_pixmap(matrix=fitz.Matrix(1.25, 1.25)).save(qa_dir / f"page-{i:02}.png")
        page_words = [len(page.get_text().split()) for page in pdf]
    print(json.dumps({"output": str(output), "count": count, "page_words": page_words}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--team-file", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--qa-dir", type=Path, required=True)
    parser.add_argument("--sha")
    args = parser.parse_args()
    build(args.output, args.team_file, args.qa_dir, args.sha)
