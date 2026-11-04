"""Escaped, server-rendered HTML; the core workflow works without JavaScript."""
from datetime import datetime
from html import escape
from urllib.parse import urlencode

from .service import BLANK_CODEPOINTS, FIELDS, LABELS, LIMITS, SEVERITIES, STATUSES, TRANSITIONS, has_text
from .rules import GUIDANCE, completeness

ICONS = {
    "reports": '<path d="M8 3h8l4 4v14H4V3h4m8 0v5h4M8 12h8M8 16h6"/>',
    "plus": '<path d="M12 5v14M5 12h14"/>',
    "arrow": '<path d="M5 12h14m-5-5 5 5-5 5"/>',
    "check": '<path d="m5 12 4 4L19 6"/>',
    "open": '<circle cx="12" cy="12" r="8"/><path d="M12 8v5m0 3h.01"/>',
    "progress": '<circle cx="12" cy="12" r="8"/><path d="M12 7v5l3 2"/>',
    "resolved": '<rect x="4" y="4" width="16" height="16" rx="5"/><path d="m8 12 3 3 5-6"/>',
}


def icon(name):
    return f'<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>'


def e(value):
    return escape(str(value), quote=True)


def badge(value, kind):
    return f'<span class="badge {kind}-{e(value.lower().replace(" ", "-"))}"><span class="dot" aria-hidden="true"></span>{e(value.capitalize() if kind == "severity" else value)}</span>'


def shell(title, content, total=0, active="reports"):
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light"><title>{e(title)} · Bug Report Helper</title>
<meta name="description" content="Write clear bug reports, track progress and give your team the context they need.">
<link rel="icon" type="image/svg+xml" href="/static/mark.svg"><link rel="stylesheet" href="/static/app.css"><script src="/static/app.js" defer></script></head>
<body><a class="skip-link" href="#main">Skip to content</a>
<aside class="sidebar"><a class="brand" href="/">{icon("reports")}<span>Bug Report<br><strong>Helper</strong></span></a>
<div class="workspace-label">TEAM WORKSPACE</div><nav aria-label="Main navigation">
<a href="/" class="nav-link {"active" if active == "reports" else ""}" {"aria-current=page" if active == "reports" else ""}>{icon("reports")}<span>Reports</span><span class="nav-count">{total}</span></a>
<a href="/reports/new" class="nav-link {"active" if active == "new" else ""}" {"aria-current=page" if active == "new" else ""}>{icon("plus")}<span>New report</span></a></nav>
<div class="sidebar-note"><span class="connection-dot" aria-hidden="true"></span>Local workspace<p>A little more context.<br>A better place to start.</p></div></aside>
<div class="app"><header class="topbar"><span class="workspace-title"><span class="workspace-avatar" aria-hidden="true">ST</span>Student team workspace<span class="workspace-context">/ Bug reports</span></span><span class="prototype-label"><span class="connection-dot" aria-hidden="true"></span>Local prototype</span></header>
<main id="main" tabindex="-1">{content}</main><footer>Structured reports. Shared understanding.</footer></div></body></html>'''


def date_label(value):
    return datetime.fromisoformat(value).strftime("%d %b %Y, %H:%M UTC")


def list_url(*, severity="", status="", page=1):
    query = {key: value for key, value in (("severity", severity), ("status", status)) if value}
    if page != 1:
        query["page"] = page
    return "/?"+urlencode(query) if query else "/"


def report_list(reports, counts, *, message="", severity="", status="", pagination=None):
    notice = f'<div class="notice" role="status">{e(message)}</div>' if message else ""
    pagination = pagination or dict(total=len(reports), page=1, pages=1, page_size=25)
    rows = []
    for report in reports:
        assessment = completeness(report)
        rows.append(f'''<tr role="row" data-report-id="{e(report['id'])}"><td role="cell" class="report-name-cell"><a class="report-title" href="/reports/{e(report['id'])}">{e(report['title'])}</a>
<span class="row-subtitle">{e(report['environment']) if has_text(report['environment']) else "Environment not provided"}</span></td>
<td role="cell" data-label="Severity">{badge(report['severity'], 'severity')}</td><td role="cell" data-label="Status">{badge(report['status'], 'status')}</td>
<td role="cell" data-label="Completeness"><span class="list-score">{assessment['score']}%</span><progress class="list-progress" max="100" value="{assessment['score']}" aria-label="Completeness: {assessment['completed']} of 7 fields"></progress><span class="row-subtitle">{assessment['completed']} of 7 fields</span></td>
<td role="cell" class="date-cell" data-label="Created"><time datetime="{e(report['created_at'])}">{date_label(report['created_at'])}</time></td>
<td role="cell" class="row-action"><a class="view-link" href="/reports/{e(report['id'])}" aria-label="View {e(report['title'])}">{icon('arrow')}</a></td></tr>''')
    empty = f'''<div class="empty-state"><div class="empty-icon">{icon('reports')}</div><h2>Your next fix starts with a clear report</h2>
<p>No reports yet. Capture what happened, what you expected,<br class="desktop-only"> and how someone else can reproduce it.</p>
<a class="button primary" href="/reports/new">{icon('plus')}Create your first report</a></div>'''
    filtered = bool(severity or status)
    if filtered and not reports:
        empty = '<div class="empty-state"><h2>No reports match these filters</h2><p>Try a different severity or status to find what you need.</p><a href="/" class="button secondary">Clear filters</a></div>'
    listing = f'''<div class="table-scroll"><table role="table"><caption class="sr-only">Bug reports</caption><thead role="rowgroup"><tr role="row"><th scope="col">Report</th><th scope="col">Severity</th><th scope="col">Status</th><th scope="col">Completeness</th><th scope="col">Created</th><th scope="col"><span class="sr-only">Open report</span></th></tr></thead><tbody role="rowgroup">{''.join(rows)}</tbody></table></div>''' if reports else empty
    sev_options = '<option value="">All severities</option>' + ''.join(f'<option value="{x}" {"selected" if x == severity else ""}>{x.capitalize()}</option>' for x in SEVERITIES)
    status_options = '<option value="">All statuses</option>' + ''.join(f'<option value="{e(x)}" {"selected" if x == status else ""}>{e(x)}</option>' for x in STATUSES)
    filters = f'<form action="/" method="get" class="filters" aria-label="Filter reports"><div><label for="filter-severity">Severity</label><select id="filter-severity" name="severity">{sev_options}</select></div><div><label for="filter-status">Status</label><select id="filter-status" name="status">{status_options}</select></div><button class="button secondary" type="submit">Apply filters</button><a href="/" class="clear-filters">Clear</a></form>'
    chips = ''.join(f'<a class="filter-chip" href="{e(list_url(severity="" if key == "severity" else severity, status="" if key == "status" else status))}" aria-label="Remove {e(key)} filter: {e(value)}">{e(value.capitalize() if key == "severity" else value)}<span aria-hidden="true">×</span></a>' for key, value in (("severity", severity), ("status", status)) if value)
    active_filters = f'<div class="active-filters"><span>Active filters</span>{chips}</div>' if filtered else ''
    first = (pagination["page"]-1)*pagination["page_size"]+1 if pagination["total"] else 0
    last = first+len(reports)-1 if reports else 0
    navigation = ''
    if pagination["pages"] > 1:
        previous = f'<a class="button secondary" rel="prev" href="{e(list_url(severity=severity, status=status, page=pagination["page"]-1))}">← Previous</a>' if pagination["page"] > 1 else '<span class="button secondary unavailable" aria-disabled="true">← Previous</span>'
        following = f'<a class="button secondary" rel="next" href="{e(list_url(severity=severity, status=status, page=pagination["page"]+1))}">Next →</a>' if pagination["page"] < pagination["pages"] else '<span class="button secondary unavailable" aria-disabled="true">Next →</span>'
        navigation = f'<nav class="pagination" aria-label="Report pages"><span>Page {pagination["page"]} of {pagination["pages"]}</span><div>{previous}{following}</div></nav>'
    stat_items = (("", "Total reports", "total", "All captured reports", "reports"),
                  ("Open", "To investigate", "Open", "Open and ready for triage", "open"),
                  ("In progress", "In progress", "In progress", "Currently being worked on", "progress"),
                  ("Resolved", "Resolved", "Resolved", "Ready to verify or reopen", "resolved"))
    stats = ''.join(f'<a class="stat {"selected" if status == value and not severity else ""}" href="{e(list_url(status=value))}"><div class="stat-top"><span>{label}</span><span class="stat-icon">{icon(mark)}</span></div><strong>{counts[key]}</strong><small>{hint}</small></a>' for value, label, key, hint, mark in stat_items)
    content = f'''<div class="page-heading"><div><p class="eyebrow">ISSUE TRACKING</p><h1>Reports</h1><p class="subtitle">Capture the context. Track the next step.</p></div>
<a class="button primary" href="/reports/new">{icon('plus')}New report</a></div>{notice}
<section class="stats" aria-label="Report summary">{stats}</section>
<section class="panel reports-panel"><div class="panel-heading"><div><h2>{'Filtered reports' if filtered else 'All reports'} <span class="count-pill">{pagination['total']}</span></h2><p id="results-summary">Showing {first}–{last} of {pagination['total']} reports{f' ({counts["total"]} total)' if filtered else ''}. Newest first.</p></div><span class="panel-note">Completeness = information present</span></div>{filters}{active_filters}{listing}{navigation}</section>'''
    return shell("Reports", content, counts["total"])


HELP = {
    "title": "A short, specific summary of the problem. Up to 160 characters.",
    "description": "What were you trying to do? Add any useful context.",
    "steps": "Use numbered steps so a teammate can try the same thing.",
    "expected": "What should have happened?",
    "actual": "What happened instead? Include error text if available.",
    "environment": "App version, browser, operating system or device.",
    "severity": "Choose the impact of the defect, rather than its priority.",
}


def error_summary(errors):
    if not errors:
        return ""
    links = "".join(f'<li><a href="#{e(field)}">{e(LABELS.get(field, field))}: {e(message)}</a></li>' for field, message in errors.items())
    return f'<div class="error-summary" id="form-errors" role="alert" tabindex="-1"><h2>There is a problem with your report</h2><ul>{links}</ul></div>'


def completeness_card(values, *, live=False):
    assessment = completeness(values)
    suggestions = ''.join(f'<li data-field="{field}" {"hidden" if field not in assessment["missing"] else ""}><a class="guidance-link" href="#{"" if live else "detail-"}{field}"><strong>{LABELS[field]}</strong>{icon("arrow")}</a><span>{GUIDANCE[field]}</span></li>' for field in FIELDS)
    output = f'<output id="completeness-score" for="{" ".join(FIELDS)}" aria-live="polite">{assessment["score"]}%</output>' if live else f'<strong id="completeness-score">{assessment["score"]}%</strong>'
    return f'''<section class="panel completeness-card" aria-labelledby="completeness-heading"><p class="eyebrow">A LITTLE CONTEXT GOES A LONG WAY</p><h2 id="completeness-heading">Report completeness</h2><div class="score-line">{output}<span id="completeness-count">{assessment['completed']} of 7 fields</span></div>
<progress id="completeness-progress" max="100" value="{assessment['score']}" aria-label="Report completeness"></progress><p class="score-disclaimer">Information presence, not correctness. A complete report may still need clarification.</p>
<details class="guidance-details" open><summary><span>What to add</span><span id="missing-count">{len(assessment['missing'])} missing</span></summary><ul class="guidance-list" id="missing-fields">{suggestions}</ul><p id="guidance-complete" {"hidden" if assessment['missing'] else ""}>All seven fields are present. Check that your steps reproduce the problem.</p></details>
{'<p class="muted-note">Updates as you type. Optional information will not block submission.</p>' if live else ''}</section>'''


def report_form(token, total, values=None, errors=None):
    values, errors = values or {}, errors or {}
    controls = {}
    for field in FIELDS:
        required = field in ("title", "severity")
        help_id = f'{field}-help'
        error_id = f'{field}-error'
        describedby = help_id + (f' {error_id}' if field in errors else '')
        attrs = f'id="{field}" name="{field}" data-report-field aria-describedby="{describedby}"'
        attrs += ' required' if required else ''
        attrs += ' aria-invalid="true"' if field in errors else ''
        value = values.get(field, "")
        if field == "severity":
            options = '<option value="">Select severity</option>' + ''.join(f'<option value="{x}" {"selected" if value == x else ""}>{x.capitalize()}</option>' for x in SEVERITIES)
            control = f'<select {attrs}>{options}</select>'
        elif field in ("title", "environment"):
            # Native maxlength counts UTF-16 units and can silently truncate valid
            # Unicode. Keep the code-point limit authoritative at the server.
            control = f'<input {attrs} type="text" data-character-limit="{LIMITS[field]}" value="{e(value)}">'
        else:
            control = f'<textarea {attrs} rows="{4 if field == "steps" else 3}" data-character-limit="{LIMITS[field]}">{e(value)}</textarea>'
        inline_error = f'<p class="field-error" id="{error_id}">{e(errors[field])}</p>' if field in errors else ''
        counter = f'<span class="field-count {"over-limit" if len(value) > LIMITS[field] else ""}" id="title-count" aria-hidden="true">{len(value)} / {LIMITS[field]}</span>' if field == "title" else ''
        controls[field] = f'<div class="field field-{field}"><label for="{field}">{LABELS[field]}<span class="field-option {"is-required" if required else ""}">{"Required" if required else "Optional"}</span></label><p class="field-help" id="{help_id}">{HELP[field]}</p>{control}{counter}{inline_error}</div>'
    groups = (("01", "The issue", "Summarise what went wrong.", ("title", "description")),
              ("02", "Reproduce it", "Help someone else see the same problem.", ("steps", "expected", "actual")),
              ("03", "Add context", "Capture where it happened and its impact.", ("environment", "severity")))
    sections = ''.join(f'<section class="form-section" aria-labelledby="group-{number}"><div class="section-heading"><span class="section-number" aria-hidden="true">{number}</span><div><h3 id="group-{number}">{title}</h3><p>{hint}</p></div></div><div class="field-grid">{"".join(controls[field] for field in fields)}</div></section>' for number, title, hint, fields in groups)
    blanks = " ".join(str(point) for point in BLANK_CODEPOINTS)
    content = f'''<a class="back-link" href="/">← Back to reports</a><div class="page-heading"><div><p class="eyebrow">CAPTURE AN ISSUE</p><h1>New report</h1><p class="subtitle">Give your team the details they need to reproduce it.</p></div></div>
<div class="editor-layout form-page"><section class="panel form-panel"><div class="panel-heading"><h2>Describe the issue</h2><p>Only title and severity are required. You can still submit an incomplete report.</p></div>
<form action="/reports" method="post" class="report-form" data-completeness data-blank-codepoints="{blanks}" novalidate><input type="hidden" name="_csrf" value="{e(token)}">{error_summary(errors)}{sections}
<div class="form-actions"><a class="button secondary" href="/">Cancel</a><button type="submit" class="button primary">{icon('plus')}Create report</button></div></form></section>
<aside class="editor-aside">{completeness_card(values, live=True)}<p class="privacy-note">Use synthetic examples. Keep passwords and personal information out of your report.</p></aside></div>'''
    return shell("New report", content, total, "new")


def report_detail(report, token, total, *, created=False, updated=False, error=""):
    notice = '<div class="notice" role="status">Report created. Your team now has a place to start.</div>' if created else ''
    if updated:
        notice += f'<div class="notice" role="status">{icon("check")}Status updated to <strong>{e(report["status"])}</strong>.</div>'
    if error:
        notice += f'<div class="error-summary" id="form-errors" tabindex="-1" role="alert">{e(error)} <a href="/reports/{e(report["id"])}">Reload report</a></div>'
    blocks = ''.join(f'<section class="detail-field" id="detail-{field}" tabindex="-1"><h2>{LABELS[field]}</h2><p class="report-text {"not-provided" if not has_text(report[field]) else ""}">{e(report[field]) if has_text(report[field]) else "Not provided"}</p></section>' for field in ("description", "steps", "expected", "actual", "environment"))
    allowed = (report["status"], *TRANSITIONS[report["status"]])
    options = ''.join(f'<option value="{e(x)}">{e(x)}</option>' for x in allowed)
    content = f'''<a class="back-link" href="/">← Back to reports</a><div class="page-heading"><div><p class="eyebrow">REPORT DETAILS</p><h1 class="detail-title">{e(report['title'])}</h1><div class="detail-badges">{badge(report['severity'], 'severity')}{badge(report['status'], 'status')}</div></div></div>{notice}
<div class="editor-layout"><article class="panel detail-panel">{blocks}</article><aside class="editor-aside"><section class="panel status-card"><h2>Move the work forward</h2><p>Update the status when your team has made progress.</p>
<form action="/reports/{e(report['id'])}/status" method="post"><input type="hidden" name="_csrf" value="{e(token)}"><input type="hidden" name="expected_status" value="{e(report['status'])}">
<label for="status">Status</label><p class="field-help" id="status-help">Choose a new status before updating.</p><select id="status" name="status" aria-describedby="status-help">{options}</select><button type="submit" class="button primary full-width">Update status{icon('arrow')}</button></form>
<p class="muted-note">Open → In progress → Resolved.<br>Resolved reports can be reopened.</p></section>{completeness_card(report)}<section class="metadata"><h2>Report information</h2><dl><dt>Created</dt><dd>{date_label(report['created_at'])}</dd><dt>Reference</dt><dd class="reference">{e(report['id'])}</dd></dl></section></aside></div>'''
    return shell(report["title"], content, total)


def error_page(status, message, total=0):
    return shell(str(status), f'<section class="panel error-page"><p class="eyebrow">{status}</p><h1>{e(message)}</h1><p>Your reports have not been changed.</p><a class="button primary" href="/">Back to reports</a></section>', total)
