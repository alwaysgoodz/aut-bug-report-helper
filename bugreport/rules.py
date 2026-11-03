"""BR-04: deterministic information-presence guidance, not a quality predictor."""
from .service import FIELDS, SEVERITIES

GUIDANCE = {
    "title": "Summarise one observable problem, for example: Login opens a blank page.",
    "description": "Describe the task and any useful context. Add relevant error text or a trace if available.",
    "steps": "List numbered actions from a known starting state so a teammate can reproduce the issue.",
    "expected": "Describe the result you expected to see.",
    "actual": "Describe the result you actually saw, including any error message.",
    "environment": "Include the app version, browser and operating system you used.",
    "severity": "Choose the observed impact: low, medium, high or critical.",
}


def completeness(report) -> dict:
    missing = []
    for field in FIELDS:
        value = report.get(field, "")
        present = isinstance(value, str) and bool(value.strip())
        if field == "severity":
            present = isinstance(value, str) and value in SEVERITIES
        if not present:
            missing.append(field)
    completed = len(FIELDS)-len(missing)
    return dict(score=round(100*completed/len(FIELDS)), completed=completed,
                total=len(FIELDS), missing=missing)
