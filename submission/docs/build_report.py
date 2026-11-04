"""Build the editable report text, counted main text and visually reviewable PDF."""
from __future__ import annotations

import html
import json
import math
import re
from pathlib import Path

import fitz
from reportlab.graphics import renderSVG
from reportlab.graphics.shapes import Drawing, Line, Polygon, Rect, String
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle, PageBreak,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "docs/report-content.json").read_text(encoding="utf-8"))
TEAM = json.loads((ROOT.parent / "docs/team.json").read_text(encoding="utf-8"))["members"]
OUT = ROOT / "output/pdf"
QA = ROOT / "tmp/pdfs/report-render"
OUT.mkdir(parents=True, exist_ok=True)
QA.mkdir(parents=True, exist_ok=True)
REPO = "https://github.com/alwaysgoodz/aut-bug-report-helper"
SHA = "0eed2879192c3b6d4feb55484dbb040dd39c6560"

for name, file in (("Body", "calibri.ttf"), ("Body-Bold", "calibrib.ttf"),
                   ("Body-Italic", "calibrii.ttf"), ("Body-BoldItalic", "calibriz.ttf")):
    pdfmetrics.registerFont(TTFont(name, str(Path("C:/Windows/Fonts") / file)))
pdfmetrics.registerFontFamily("Body", normal="Body", bold="Body-Bold", italic="Body-Italic",
                            boldItalic="Body-BoldItalic")
INK = colors.HexColor("#172B3A")
MUTED = colors.HexColor("#536171")
ACCENT = colors.HexColor("#17646D")
PALE = colors.HexColor("#F0F5F6")
styles = getSampleStyleSheet()
styles.add(ParagraphStyle("Main", fontName="Body", fontSize=11, leading=14,
                          textColor=INK, spaceAfter=7, allowWidows=0, allowOrphans=0))
styles.add(ParagraphStyle("Section", parent=styles["Main"], fontName="Body-Bold",
                          fontSize=13.2, leading=17, spaceBefore=10, spaceAfter=8, keepWithNext=True))
styles.add(ParagraphStyle("Cell", parent=styles["Main"], fontSize=9.5, leading=12,
                          spaceAfter=0, allowWidows=1, allowOrphans=1))
styles.add(ParagraphStyle("Small", parent=styles["Main"], fontSize=9.2, leading=12,
                          textColor=MUTED, spaceAfter=7))
styles.add(ParagraphStyle("Caption", parent=styles["Small"], fontName="Body-Bold",
                          textColor=INK, keepWithNext=True, spaceBefore=6, spaceAfter=5))
styles.add(ParagraphStyle("Reference", parent=styles["Main"], fontSize=10.4, leading=14,
                          leftIndent=36, firstLineIndent=-36, spaceAfter=10))
styles.add(ParagraphStyle("CoverTitle", parent=styles["Main"], fontName="Body-Bold",
                          fontSize=30, leading=35, spaceAfter=14))
styles.add(ParagraphStyle("CoverSub", parent=styles["Main"], fontSize=16, leading=22,
                          textColor=ACCENT, spaceAfter=24))


def para(text, style="Main", rich=False):
    value = text if rich else html.escape(text)
    value = re.sub(r"https://[^\s<]+", lambda m: '<link href="' + m[0] + '">' + m[0] + '</link>', value)
    return Paragraph(value, styles[style])


def table(headers, rows, widths):
    cells = [[para(x, "Cell") for x in headers]]
    cells += [[para(x, "Cell") for x in row] for row in rows]
    result = Table(cells, colWidths=widths, hAlign="LEFT", repeatRows=1)
    result.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PALE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW", (0, 0), (-1, 0), .7, ACCENT),
        ("LINEBELOW", (0, 1), (-1, -1), .3, colors.HexColor("#D7E0E5")),
    ]))
    return result


def system_diagram():
    d = Drawing(475, 180)
    # Every visible label is present in the counted JSON figure labels.
    d.add(Rect(3, 3, 469, 147, rx=5, fillColor=None, strokeColor=colors.HexColor("#BCCAD2")))
    d.add(String(12, 12, "Local application boundary", fontName="Body-Italic", fontSize=9, fillColor=MUTED))
    d.add(String(12, 165, "Reporter / developer / QA", fontName="Body-Bold", fontSize=10, fillColor=INK))

    def box(x, y, w, h, label, sub=None, planned=False):
        r = Rect(x, y, w, h, rx=4, fillColor=PALE if not planned else colors.white,
                 strokeColor=ACCENT if not planned else MUTED, strokeWidth=.9)
        if planned:
            r.strokeDashArray = [4, 3]
        d.add(r)
        d.add(String(x+w/2, y+h/2+(3 if sub else -3), label, textAnchor="middle",
                     fontName="Body-Bold", fontSize=9.5, fillColor=INK))
        if sub:
            d.add(String(x+w/2, y+h/2-11, sub, textAnchor="middle", fontName="Body", fontSize=8.8, fillColor=MUTED))

    def arrow(x1, y1, x2, y2, planned=False):
        ln = Line(x1, y1, x2, y2, strokeColor=ACCENT, strokeWidth=1)
        if planned:
            ln.strokeDashArray = [4, 3]
        d.add(ln)
        angle = math.atan2(y2-y1, x2-x1)
        dx, dy = math.cos(angle), math.sin(angle)
        points = [x2, y2, x2-5*dx-3*dy, y2-5*dy+3*dx,
                  x2-5*dx+3*dy, y2-5*dy-3*dx]
        d.add(Polygon(points, fillColor=ACCENT, strokeColor=ACCENT))

    box(12, 93, 142, 45, "Browser forms and list", "I1 browser adapter", True)
    box(181, 93, 146, 45, "Python report service", "Validation; create; read")
    box(351, 93, 109, 45, "SQLite report store")
    box(12, 30, 142, 40, "Local CLI")
    box(181, 30, 146, 40, "Completeness rules", "I2 guidance", True)
    arrow(83, 160, 83, 138, True)
    arrow(154, 115, 181, 115, True)
    arrow(327, 115, 351, 115)
    arrow(154, 50, 181, 93)
    arrow(254, 93, 254, 70, True)
    return d


def counted_text():
    chunks = []
    by_section = {}
    for section in DATA["sections"]:
        texts = [section["heading"], *section.get("paragraphs", [])]
        if "table" in section:
            t = section["table"]
            texts += [t["caption"], *t["headers"], *sum(t["rows"], [])]
        texts += section.get("after", [])
        if "figure" in section:
            texts += [section["figure"]["caption"], *section["figure"]["labels"]]
        texts += section.get("end", [])
        by_section[section["heading"]] = len(" ".join(texts).split())
        chunks.extend(texts)
    text = "\n\n".join(chunks)
    conservative = re.findall(r"\b[\w]+(?:['’][\w]+)*\b", text)
    report = dict(whitespace_words=len(text.split()), conservative_tokens=len(conservative),
                  includes="All main headings, paragraphs, table captions/headers/cells, figure caption/labels, in-text citations and contribution statements",
                  excludes="Cover page, reference list and supporting appendix; recurring page furniture",
                  limit=1500, by_section=by_section,
                  reserve_under_conservative_count=1500-len(conservative))
    if report["conservative_tokens"] > 1500:
        raise ValueError("Main report exceeds the conservative 1,500-word check")
    (ROOT / "docs/main-text-counted.txt").write_text(text+"\n", encoding="utf-8")
    (ROOT / "docs/word-count.json").write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    return report


def markdown_report(count):
    team_table = "\n".join(["| Member | Name | Student ID | GitHub |", "| --- | --- | --- | --- |",
                             *[f'| {m["role"]} | {m["name"]} | {m["student_id"]} | {m["github"]} |' for m in TEAM]])
    parts = ["# "+DATA["title"], DATA["subtitle"],
             "AUT Contemporary Methods in Software Engineering — Assignment 1",
             "**Working draft: names supplied; IDs/accounts blank by request. Equal shares are planned, not verified contributions. Independent review and assessor access remain pending.**",
             team_table,
             f"Conservative main-text count: {count['conservative_tokens']} (limit 1,500).", ""]
    for section in DATA["sections"]:
        parts += ["## "+section["heading"], *section.get("paragraphs", [])]
        if "table" in section:
            t = section["table"]
            parts += [t["caption"], "\n".join(["| "+" | ".join(t["headers"])+" |", "| "+" | ".join(["---"]*len(t["headers"]))+" |",
                                              *["| "+" | ".join(row)+" |" for row in t["rows"]]])]
        parts += section.get("after", [])
        if "figure" in section:
            parts += [section["figure"]["caption"], "![System overview](system-overview.svg)"]
        parts += section.get("end", [])
    parts += ["## References", *[x.replace("<i>", "*").replace("</i>", "*") for x in DATA["references"]],
              "## Appendix A. Supporting evidence index", appendix_markdown()]
    (ROOT / "docs/assignment-1-report.md").write_text("\n\n".join(parts)+"\n", encoding="utf-8")


def appendix_markdown():
    return f"""| ID | Evidence | Current status |
| --- | --- | --- |
| E1 | [Issues #1–6]({REPO}/issues), [Backlog]({REPO}/blob/feat/1-create-report/docs/backlog.md) | Prioritised requirements and acceptance criteria exist. |
| E2 | [Issue #1]({REPO}/issues/1), [Draft PR #7]({REPO}/pull/7) | Implementation exists; independent review and approved merge pending. |
| E3 | [Implementation]({REPO}/commit/{SHA}), [CI run]({REPO}/actions/runs/41673631149) | Implementation SHA: {SHA}; both Python jobs passed. |
| E4 | [Trial record]({REPO}/blob/feat/1-create-report/docs/trial-record.md), [logs]({REPO}/tree/feat/1-create-report/docs/evidence) | Actual test evidence and corrective lesson; no user evaluation results. |
| E5 | [Contribution ledger]({REPO}/blob/feat/team-study-preparation/docs/contributions.md) | Names supplied; IDs/accounts blank and actual activity links unverified. |
| E6 | [Setup/test README]({REPO}/blob/feat/1-create-report/README.md), [workflow rules]({REPO}/blob/feat/1-create-report/CONTRIBUTING.md) | Reproducible feature instructions; manual review gate. |

Repository access is private. Invite the real team and assessor and verify their access. The implementation SHA is a verified review snapshot, not a final submission release. Final release identity must follow independent approval and complete contribution records.

Preparation assistance: Codex assisted with literature discovery, synthesis, report drafting, diagram, code, tests and repository setup. This acknowledgement describes actual assistance; the team must adapt it to the course's rules and verify all submitted material. No independent team review or user study is claimed by these generated materials.
"""


def page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont("Body", 8.5)
    canvas.setFillColor(MUTED)
    if doc.page > 1:
        canvas.drawString(20*mm, A4[1]-14*mm, "AUT  /  Contemporary Methods in Software Engineering")
    canvas.drawRightString(A4[0]-20*mm, 13*mm, str(doc.page))
    canvas.restoreState()


def build():
    count = counted_text()
    diagram = system_diagram()
    renderSVG.drawToFile(diagram, str(ROOT / "docs/system-overview.svg"))
    markdown_report(count)
    story = [Spacer(1, 32*mm), para("ASSIGNMENT 1  ·  GROUP REPORT", "Caption"),
             Spacer(1, 7*mm), para(DATA["title"], "CoverTitle"), para(DATA["subtitle"], "CoverSub"),
             para("AUT · Contemporary Methods in Software Engineering", "Main"),
             para("Prepared 4 November 2026 · Topic approval confirmed by the owner", "Small"),
             Spacer(1, 8*mm),
             table(["Role", "Name", "Student ID", "GitHub"], [[m["role"], m["name"], m["student_id"], m["github"]] for m in TEAM], [40,180,105,150]),
             Spacer(1, 10*mm),
             para(f"Main text: {count['conservative_tokens']} conservative tokens / {count['whitespace_words']} whitespace words; limit 1,500. Includes tables, diagram labels, citations and contribution statements.", "Small"),
             para("Working draft. Names supplied; student IDs and GitHub accounts left blank by request. Workload is planned at 25% each; actual contributions, independent review, final reference and assessor access remain unverified.", "Main"),
             para(REPO, "Small"), PageBreak()]
    for section in DATA["sections"]:
        story.append(para(section["heading"], "Section"))
        story.extend(KeepTogether([para(p)]) for p in section.get("paragraphs", []))
        if "table" in section:
            t = section["table"]
            story += [para(t["caption"], "Caption"), table(t["headers"], t["rows"],
                       [98, 186, 191] if section["heading"].startswith("2") else [86, 286, 103]), Spacer(1, 7)]
        story.extend(KeepTogether([para(p)]) for p in section.get("after", []))
        if "figure" in section:
            story.append(KeepTogether([para(section["figure"]["caption"], "Caption"), diagram]))
        story.extend(KeepTogether([para(p)]) for p in section.get("end", []))
    story += [PageBreak(), para("References", "Section")]
    story.extend(para(p, "Reference", rich=True) for p in DATA["references"])
    story += [PageBreak(), para("Appendix A. Supporting evidence index", "Section"),
              para("Supporting links only; assessed explanations and limitations are in the main text.", "Small")]
    appendix = [
        ("E1", "Backlog / requirements", REPO+"/issues", "Six actual Issues; detailed acceptance criteria and priorities."),
        ("E2", "Tracked requirement", REPO+"/issues/1", "BR-01 recorded before implementation."),
        ("E2", "Proposed change", REPO+"/pull/7", "Draft PR; independent review and merge pending."),
        ("E3", "Implementation SHA", REPO+"/commit/"+SHA, SHA),
        ("E3", "Remote checks", REPO+"/actions/runs/41673631149", "Passed: Python 3.11 and 3.12, 16 test methods per job plus compile check."),
        ("E4", "Trial and logs", REPO+"/blob/feat/1-create-report/docs/trial-record.md", "Execution findings, correction and preserved evidence."),
        ("E5", "Individual contributions", REPO+"/blob/feat/team-study-preparation/docs/contributions.md", "Names supplied; IDs/accounts blank; actual activity links unverified."),
        ("E6", "Setup and tests", REPO+"/blob/feat/1-create-report/README.md", "Clone and check out the feature branch or exact SHA before running tests."),
    ]
    rows = [[para("ID", "Cell"), para("Evidence link", "Cell"), para("Verified meaning / limit", "Cell")]]
    for key, label, url, limit in appendix:
        rows.append([para(key, "Cell"), Paragraph(f'<link color="#17646D" href="{url}">{html.escape(label)}</link>', styles["Cell"]), para(limit, "Cell")])
    t = Table(rows, colWidths=[33, 155, 287], repeatRows=1, hAlign="LEFT")
    t.setStyle(TableStyle([("VALIGN", (0,0),(-1,-1),"TOP"), ("BACKGROUND",(0,0),(-1,0),PALE),
                           ("BOTTOMPADDING",(0,0),(-1,-1),9), ("TOPPADDING",(0,0),(-1,-1),6),
                           ("LINEBELOW",(0,0),(-1,-1),.3,colors.HexColor("#D7E0E5"))]))
    story += [t, Spacer(1, 12),
              para("Access and submission identity. The repository is private. The owner must invite the actual teammates and assessor and verify access. The implementation SHA is a reproducible review snapshot; select the final submission commit or release after independent approval and completion of contributions.", "Small"),
              para("Preparation assistance. Codex assisted with literature discovery, synthesis, report drafting, diagram, code, tests and repository setup. The team must adapt this acknowledgement to course requirements and verify submitted material. These generated materials do not establish four students' contributions or an independent review.", "Small")]
    pdf_path = OUT / "assignment-1-report-draft.pdf"
    doc = SimpleDocTemplate(str(pdf_path), pagesize=A4, rightMargin=20*mm, leftMargin=20*mm,
                            topMargin=23*mm, bottomMargin=20*mm,
                            title=DATA["title"], author=", ".join(m["name"] for m in TEAM),
                            subject="AUT Assignment 1: structured bug-report helper")
    doc.build(story, onFirstPage=page_number, onLaterPages=page_number)
    pdf = fitz.open(pdf_path)
    pages = []
    for i, page in enumerate(pdf):
        page.get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(str(QA / f"page-{i+1:02}.png"))
        pages.append({"page": i+1, "words": len(page.get_text().split()),
                      "links": len(page.get_links()), "text": page.get_text()})
    (ROOT / "tmp/pdfs/layout-inspection.json").write_text(json.dumps(pages, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"pdf":str(pdf_path),"pages":len(pdf),"count":count,"page_words":[p['words'] for p in pages]},ensure_ascii=False,indent=2))


if __name__ == "__main__":
    build()
