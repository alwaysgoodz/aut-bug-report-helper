"""Escaped, server-rendered HTML; the core workflow works without JavaScript."""
from datetime import datetime
from html import escape

from .service import FIELDS, LABELS, LIMITS, SEVERITIES, TRANSITIONS

ICONS = {
    "reports": '<path d="M8 3h8l4 4v14H4V3h4m8 0v5h4M8 12h8M8 16h6"/>',
    "plus": '<path d="M12 5v14M5 12h14"/>',
    "arrow": '<path d="M5 12h14m-5-5 5 5-5 5"/>',
    "check": '<path d="m5 12 4 4L19 6"/>',
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
<link rel="icon" href="data:,"><link rel="stylesheet" href="/static/app.css"><script src="/static/app.js" defer></script></head>
<body><a class="skip-link" href="#main">Skip to content</a>
<aside class="sidebar"><a class="brand" href="/">{icon("reports")}<span>Bug Report<br><strong>Helper</strong></span></a>
<div class="workspace-label">TEAM WORKSPACE</div><nav aria-label="Main navigation">
<a href="/" class="nav-link {"active" if active == "reports" else ""}" {"aria-current=page" if active == "reports" else ""}>{icon("reports")}<span>Reports</span><span class="nav-count">{total}</span></a>
<a href="/reports/new" class="nav-link {"active" if active == "new" else ""}" {"aria-current=page" if active == "new" else ""}>{icon("plus")}<span>New report</span></a></nav>
<div class="sidebar-note"><span class="connection-dot" aria-hidden="true"></span>Local workspace<p>A little more context.<br>A better place to start.</p></div></aside>
<div class="app"><header class="topbar"><span>Student team workspace</span><span class="prototype-label">Local prototype</span></header>
<main id="main" tabindex="-1">{content}</main><footer>Structured reports. Shared understanding.</footer></div></body></html>'''


def date_label(value):
    return datetime.fromisoformat(value).strftime("%d %b %Y, %H:%M UTC")


def report_list(reports, counts, *, message=""):
    notice = f'<div class="notice" role="status">{e(message)}</div>' if message else ""
    rows = "".join(f'''<tr><td><a class="report-title" href="/reports/{e(report['id'])}">{e(report['title'])}</a>
<span class="row-subtitle">{e(report['environment'] or "Environment not provided")}</span></td>
<td>{badge(report['severity'], 'severity')}</td><td>{badge(report['status'], 'status')}</td>
<td class="date-cell">{date_label(report['created_at'])}</td><td><a class="view-link" href="/reports/{e(report['id'])}" aria-label="View {e(report['title'])}">{icon('arrow')}</a></td></tr>''' for report in reports)
    empty = f'''<div class="empty-state"><div class="empty-icon">{icon('reports')}</div><h2>Your next fix starts with a clear report</h2>
<p>No reports yet. Capture what happened, what you expected,<br class="desktop-only"> and how someone else can reproduce it.</p>
<a class="button primary" href="/reports/new">{icon('plus')}Create your first report</a></div>'''
    listing = f'''<div class="table-scroll"><table><caption class="sr-only">Bug reports</caption><thead><tr><th scope="col">REPORT</th><th scope="col">SEVERITY</th><th scope="col">STATUS</th><th scope="col">CREATED</th><th scope="col"><span class="sr-only">Open report</span></th></tr></thead><tbody>{rows}</tbody></table></div>''' if reports else empty
    content = f'''<div class="page-heading"><div><p class="eyebrow">YOUR PROJECT, IN FOCUS</p><h1>Reports</h1><p class="subtitle">Turn a vague problem into a clear next step.</p></div>
<a class="button primary" href="/reports/new">{icon('plus')}New report</a></div>{notice}
<section class="stats" aria-label="Report summary"><div class="stat"><span>Total reports</span><strong>{counts['total']:02}</strong><small>All captured reports</small></div>
<div class="stat"><span>To investigate</span><strong>{counts['Open']:02}</strong><small>Open and ready for triage</small></div>
<div class="stat"><span>In progress</span><strong>{counts['In progress']:02}</strong><small>Currently being worked on</small></div>
<div class="stat"><span>Resolved</span><strong>{counts['Resolved']:02}</strong><small>Ready to verify or reopen</small></div></section>
<section class="panel reports-panel"><div class="panel-heading"><div><h2>All reports <span class="count-pill">{len(reports)}</span></h2><p>One place for the context your team needs.</p></div></div>{listing}</section>'''
    return shell("Reports", content, counts["total"])


HELP = {
    "title": "A short, specific summary of the problem.",
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


def report_form(token, total, values=None, errors=None):
    values, errors = values or {}, errors or {}
    controls = []
    for field in FIELDS:
        required = field in ("title", "severity")
        help_id = f'{field}-help'
        error_id = f'{field}-error'
        describedby = help_id + (f' {error_id}' if field in errors else '')
        attrs = f'id="{field}" name="{field}" aria-describedby="{describedby}"'
        attrs += ' required' if required else ''
        attrs += ' aria-invalid="true"' if field in errors else ''
        value = values.get(field, "")
        if field == "severity":
            options = '<option value="">Select severity</option>' + ''.join(f'<option value="{x}" {"selected" if value == x else ""}>{x.capitalize()}</option>' for x in SEVERITIES)
            control = f'<select {attrs}>{options}</select>'
        elif field in ("title", "environment"):
            control = f'<input {attrs} type="text" maxlength="{LIMITS[field]}" value="{e(value)}">'
        else:
            control = f'<textarea {attrs} rows="{4 if field == "steps" else 3}" maxlength="{LIMITS[field]}">{e(value)}</textarea>'
        inline_error = f'<p class="field-error" id="{error_id}">{e(errors[field])}</p>' if field in errors else ''
        controls.append(f'<div class="field field-{field}"><label for="{field}">{LABELS[field]}<span class="field-option">{"Required" if required else "Optional"}</span></label><p class="field-help" id="{help_id}">{HELP[field]}</p>{control}{inline_error}</div>')
    content = f'''<a class="back-link" href="/">← Back to reports</a><div class="page-heading"><div><p class="eyebrow">GIVE YOUR TEAM A HEAD START</p><h1>New report</h1><p class="subtitle">The details you add now make the next step easier.</p></div></div>
<div class="editor-layout"><section class="panel form-panel"><div class="panel-heading"><h2>Describe the issue</h2><p>Only title and severity are required. You can still submit an incomplete report.</p></div>
<form action="/reports" method="post" class="report-form" novalidate><input type="hidden" name="_csrf" value="{e(token)}">{error_summary(errors)}<div class="field-grid">{''.join(controls)}</div>
<div class="form-actions"><a class="button secondary" href="/">Cancel</a><button type="submit" class="button primary">{icon('plus')}Create report</button></div></form></section>
<aside class="editor-aside"><section class="panel guidance-card"><span class="small-mark">{icon('check')}</span><h2>Make it reproducible</h2><p>A useful report helps someone else see the same problem.</p><ol><li>Describe one issue at a time.</li><li>Start your steps from a known state.</li><li>Separate expected and actual results.</li><li>Include the environment you used.</li></ol><p class="muted-note">Use synthetic examples. Keep passwords and personal information out of your report.</p></section></aside></div>'''
    return shell("New report", content, total, "new")


def report_detail(report, token, total, *, created=False, error=""):
    notice = '<div class="notice" role="status">Report created. Your team now has a place to start.</div>' if created else ''
    if error:
        notice += f'<div class="error-summary" id="form-errors" tabindex="-1" role="alert">{e(error)} <a href="/reports/{e(report["id"])}">Reload report</a></div>'
    blocks = ''.join(f'<section class="detail-field"><h2>{LABELS[field]}</h2><p class="report-text {"not-provided" if not report[field].strip() else ""}">{e(report[field]) if report[field].strip() else "Not provided"}</p></section>' for field in ("description", "steps", "expected", "actual", "environment"))
    allowed = (report["status"], *TRANSITIONS[report["status"]])
    options = ''.join(f'<option value="{e(x)}">{e(x)}</option>' for x in allowed)
    content = f'''<a class="back-link" href="/">← Back to reports</a><div class="page-heading"><div><p class="eyebrow">REPORT DETAILS</p><h1 class="detail-title">{e(report['title'])}</h1><div class="detail-badges">{badge(report['severity'], 'severity')}{badge(report['status'], 'status')}</div></div></div>{notice}
<div class="editor-layout"><article class="panel detail-panel">{blocks}</article><aside class="editor-aside"><section class="panel status-card"><h2>Move the work forward</h2><p>Update the status when your team has made progress.</p>
<form action="/reports/{e(report['id'])}/status" method="post"><input type="hidden" name="_csrf" value="{e(token)}"><input type="hidden" name="expected_status" value="{e(report['status'])}">
<label for="status">Status</label><select id="status" name="status">{options}</select><button type="submit" class="button primary full-width">Update status{icon('arrow')}</button></form>
<p class="muted-note">Open → In progress → Resolved.<br>Resolved reports can be reopened.</p></section><section class="metadata"><h2>Report information</h2><dl><dt>Created</dt><dd>{date_label(report['created_at'])}</dd><dt>Reference</dt><dd class="reference">{e(report['id'])}</dd></dl></section></aside></div>'''
    return shell(report["title"], content, total)


def error_page(status, message, total=0):
    return shell(str(status), f'<section class="panel error-page"><p class="eyebrow">{status}</p><h1>{e(message)}</h1><p>Your reports have not been changed.</p><a class="button primary" href="/">Back to reports</a></section>', total)
