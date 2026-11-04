"""Generate the A2 draft, editable text and page previews; document-only dependencies."""
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
from reportlab.platypus import KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT/"docs/a2/report-content.json").read_text(encoding="utf-8"))
TEAM = json.loads((ROOT/"docs/team.json").read_text(encoding="utf-8"))["members"]
OUT = ROOT/"submission-a2"
QA = ROOT/"tmp/a2-report-render"
OUT.mkdir(exist_ok=True)
QA.mkdir(parents=True, exist_ok=True)
REPO = "https://github.com/alwaysgoodz/aut-bug-report-helper"
INK, MUTED, TEAL = (colors.HexColor(x) for x in ("#172F35", "#536771", "#17646D"))
for name, filename in (("A2", "calibri.ttf"), ("A2-Bold", "calibrib.ttf"), ("A2-Italic", "calibrii.ttf"), ("A2-BoldItalic", "calibriz.ttf")):
    pdfmetrics.registerFont(TTFont(name, "C:/Windows/Fonts/"+filename))
pdfmetrics.registerFontFamily("A2", normal="A2", bold="A2-Bold", italic="A2-Italic", boldItalic="A2-BoldItalic")
STYLES = {
    "body": ParagraphStyle("body", fontName="A2", fontSize=11, leading=14.2, spaceAfter=8, textColor=INK),
    "heading": ParagraphStyle("heading", fontName="A2-Bold", fontSize=13.3, leading=17, spaceBefore=10, spaceAfter=8, keepWithNext=True, textColor=INK),
    "cell": ParagraphStyle("cell", fontName="A2", fontSize=9.5, leading=12.3, textColor=INK),
    "caption": ParagraphStyle("caption", fontName="A2-Bold", fontSize=9.6, leading=13, spaceBefore=5, spaceAfter=5, keepWithNext=True, textColor=INK),
    "small": ParagraphStyle("small", fontName="A2", fontSize=9.3, leading=12.6, spaceAfter=8, textColor=MUTED),
    "reference": ParagraphStyle("reference", fontName="A2", fontSize=10.3, leading=14, leftIndent=36, firstLineIndent=-36, spaceAfter=11, textColor=INK),
    "title": ParagraphStyle("title", fontName="A2-Bold", fontSize=28, leading=34, spaceAfter=15, textColor=INK),
    "subtitle": ParagraphStyle("subtitle", fontName="A2", fontSize=16, leading=22, spaceAfter=22, textColor=TEAL),
}


def p(text, style="body", rich=False):
    value = text if rich else html.escape(text)
    value = re.sub(r"https://[^\s<]+", lambda m: f'<link href="{m[0]}">{m[0]}</link>', value)
    return Paragraph(value, STYLES[style])


def tab(headers, rows, widths):
    result = Table([[p(x, "cell") for x in row] for row in [headers, *rows]], colWidths=widths, repeatRows=1, hAlign="LEFT")
    result.setStyle(TableStyle([
        ("VALIGN", (0,0),(-1,-1),"TOP"), ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#EEF4F3")),
        ("LEFTPADDING",(0,0),(-1,-1),7), ("RIGHTPADDING",(0,0),(-1,-1),7),
        ("TOPPADDING",(0,0),(-1,-1),7), ("BOTTOMPADDING",(0,0),(-1,-1),7),
        ("LINEBELOW",(0,0),(-1,0),.7,TEAL), ("LINEBELOW",(0,1),(-1,-1),.3,colors.HexColor("#D6E1DE")),
    ]))
    return result


def furniture(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(MUTED)
    canvas.setFont("A2", 8.5)
    if doc.page > 1:
        canvas.drawString(20*mm, A4[1]-14*mm, "AUT  /  Contemporary Methods in Software Engineering  /  Assignment 2")
    canvas.drawRightString(A4[0]-20*mm, 13*mm, str(doc.page))
    canvas.restoreState()


def build():
    counted, md = [], ["# "+DATA["title"], DATA["subtitle"],
                       "**Preparation draft. Names supplied; IDs/accounts blank by request. Planned equal shares do not establish completed contributions, meetings or peer evaluation.**",
                       "\n".join(["| Role | Name | Student ID | GitHub |", "| --- | --- | --- | --- |",
                                    *[f'| {m["role"]} | {m["name"]} | {m["student_id"]} | {m["github"]} |' for m in TEAM]])]
    for section in DATA["sections"]:
        chunks = [section["heading"], *section.get("paragraphs", [])]
        md += ["## "+section["heading"], *section.get("paragraphs", [])]
        if "table" in section:
            t = section["table"]
            chunks += [t["caption"], *t["headers"], *sum(t["rows"], [])]
            md += [t["caption"], "\n".join(["| "+" | ".join(t["headers"])+" |", "| "+" | ".join(["---"]*len(t["headers"]))+" |",
                                           *["| "+" | ".join(row)+" |" for row in t["rows"]]])]
        chunks += section.get("after", [])
        md += section.get("after", [])
        counted.extend(chunks)
    main = "\n\n".join(counted)
    words = len(main.split())
    conservative = len(re.findall(r"\b[\w]+(?:['’][\w]+)*\b", main))
    if conservative > 2500:
        raise ValueError("A2 main text exceeds conservative 2,500-word check")
    count = dict(whitespace_words=words, conservative_tokens=conservative, limit=2500,
                 includes="Main headings, paragraphs, table captions, headers/cells and in-text citations",
                 excludes="Cover, references, supporting appendix and separate individual statements")
    (ROOT/"docs/a2/word-count.json").write_text(json.dumps(count, indent=2)+"\n", encoding="utf-8")
    (ROOT/"docs/a2/main-text-counted.txt").write_text(main+"\n", encoding="utf-8")
    md += ["## References", *[x.replace("<i>", "*").replace("</i>", "*") for x in DATA["references"]],
           "## Supporting evidence", "See [evidence index](../docs/a2/evidence-index.md), [demo runbook](../docs/a2/demo-runbook.md) and [individual statement template](../docs/a2/individual-statements/template.md)."]
    (OUT/"assignment-2-report.md").write_text("\n\n".join(md)+"\n", encoding="utf-8")
    story = [Spacer(1, 28*mm), p("GROUP EVALUATION REPORT  ·  ASSIGNMENT 2", "caption"), Spacer(1,6*mm),
             p(DATA["title"], "title"), p(DATA["subtitle"], "subtitle"),
             p("AUT · Contemporary Methods in Software Engineering", "body"),
             p("Software candidate: a2-review-v0.4. Historical I1/I2 snapshots and workload conditions remain explicit; team allocation and study preparation are unverified plans.", "small"),
             Spacer(1,7*mm), tab(["Role", "Name", "Student ID", "GitHub"], [[m["role"],m["name"],m["student_id"],m["github"]] for m in TEAM], [40,180,105,150]),
             Spacer(1,9*mm), p(f"Main text: {words} whitespace words / {conservative} conservative tokens; limit 2,500. Tables and citations are included.", "small"),
             p("Preparation draft. Names supplied; IDs/accounts left blank by request. Planned workload is 25% each. Discussion drafts and a study tool are prepared; actual meetings, peer outcomes, contributions, reviews and assessor access remain unverified.", "body"),
             p(REPO+"/tree/feat/team-study-preparation", "small"), PageBreak()]
    table_number = 0
    widths = [[65,185,225], [205,125,145], [205,130,140], [100,188,187]]
    for section in DATA["sections"]:
        paragraphs = section.get("paragraphs", [])
        story.append(KeepTogether([p(section["heading"], "heading"), p(paragraphs[0])]))
        story.extend(KeepTogether([p(value)]) for value in paragraphs[1:])
        if "table" in section:
            t = section["table"]
            story += [p(t["caption"], "caption"), tab(t["headers"],t["rows"],widths[table_number]),Spacer(1,7)]
            table_number += 1
        story.extend(KeepTogether([p(value)]) for value in section.get("after", []))
    story += [PageBreak(), p("References", "heading")]
    story.extend(KeepTogether([p(value, "reference", rich=True)]) for value in DATA["references"])
    story += [PageBreak(), p("Appendix A. Supporting evidence and review references", "heading"),
              p("Assessed analysis is in the main report. The following links preserve supporting activities and raw results; all repository links require assessor access.", "small")]
    evidence = [
        ("Current application candidate v0.4", REPO+"/tree/a2-review-v0.4"),
        ("Current application CI", REPO+"/actions/runs/41854085423"),
        ("Team allocation and discussion drafts", REPO+"/tree/feat/team-study-preparation/docs/team"),
        ("Prepared peer-study protocol (not results)", REPO+"/blob/feat/team-study-preparation/docs/peer-study/README.md"),
        ("Requirements and traceability", REPO+"/blob/a2-review-v0.1/docs/a2/traceability.md"),
        ("I1 draft PR #8", REPO+"/pull/8"), ("I2 draft PR #10", REPO+"/pull/10"),
        ("I1 checks and logs", REPO+"/actions/runs/41677785458"),
        ("I2 checks: actual browser gate", REPO+"/actions/runs/41680263474"),
        ("Prospective PI-01 plan", REPO+"/blob/a2-review-v0.1/docs/a2/process-improvement-plan.md"),
        ("I1/I2 mutation evidence", REPO+"/blob/a2-review-v0.1/docs/a2/evidence-index.md"),
        ("Raw performance and fingerprints", REPO+"/blob/a2-review-v0.1/docs/a2/evidence/performance.json"),
        ("Original-resolution product screenshots", REPO+"/tree/a2-review-v0.1/docs/a2/evidence"),
        ("Demo and individual statement templates", REPO+"/blob/a2-review-v0.1/docs/a2/demo-runbook.md"),
        ("Historical I2 review candidate", REPO+"/tree/a2-review-v0.1"),
    ]
    for label, url in evidence:
        story += [Paragraph(f'<link color="#17646D" href="{url}">{html.escape(label)}</link>',STYLES["body"])]
    story += [Spacer(1,10),p("Reproducible source snapshot", "heading"),
              p("I1: cee24aaa908991a9ff38967bfc2a46f973493934. Historical I2 measurement: f36dfc792c4467c0726598cce401629f7a9e7fe5. Current application: 8a0f4bbc3bc28ee1925513b4d599a5e9dad54458 (v0.4 preserves that application with later evidence). Prepared study tools are separate from actual participant results. Final assessed submission requires real independent approval.","small"),
              p("Assistance and outstanding activities", "heading"),
              p("Codex assisted with research, implementation, checks, study-tool preparation, discussion drafts and reports through the authorised owner's account. Names and planned 25% allocations do not establish completed student work or meetings. IDs/accounts remain blank by request. Genuine activities, statements, peer study, reviews and access still require team action.","small")]
    output = OUT/"assignment-2-report-draft.pdf"
    doc = SimpleDocTemplate(str(output), pagesize=A4, leftMargin=20*mm, rightMargin=20*mm,
                            topMargin=23*mm,bottomMargin=20*mm,title=DATA["title"],
                            author=", ".join(m["name"] for m in TEAM))
    doc.build(story,onFirstPage=furniture,onLaterPages=furniture)
    pdf = fitz.open(output)
    summary = []
    for index, page in enumerate(pdf):
        page.get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(str(QA/f"page-{index+1:02}.png"))
        summary.append(dict(page=index+1,words=len(page.get_text().split()),links=len(page.get_links()),text=page.get_text()))
    (ROOT/"tmp/a2-layout.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(dict(output=str(output),pages=len(pdf),count=count,page_words=[x["words"]for x in summary]),indent=2))


if __name__ == "__main__":
    build()
