"""Explicit fictional examples; refuse to change a database that already has reports."""
import argparse

from bugreport.service import ReportStore


def seed_database(database):
    """Seed a dedicated empty demonstration store; never overwrite reports."""
    store = ReportStore(database)
    if store.counts()["total"]:
        raise ValueError("Demo seeding requires an empty database; existing reports were not changed")
    examples = [
        ("Login screen stays blank after sign-in", "high", "Open", "Sign in with the demo account", "The weekly planner opens", "A blank panel appears", "Study Planner demo / Chrome / Windows"),
        ("Task reminders arrive twice", "medium", "In progress", "Create a task and enable one reminder", "One reminder is delivered", "Two reminders arrive together", "Study Planner demo / Firefox"),
        ("Completed tasks remain in the active list", "low", "Resolved", "Complete a task, then open Active tasks", "The completed task is hidden", "The task remains visible", "Study Planner demo / Safari"),
        ("Changes disappear after refreshing the planner", "critical", "Open", "", "", "A new task disappears after reload", ""),
    ]
    reports = []
    for title, severity, status, steps, expected, actual, environment in examples:
        report = store.create(title=title, severity=severity,
                              description="Fictional Study Planner defect for a course demonstration; not a known defect in this helper.",
                              steps=steps, expected=expected, actual=actual, environment=environment)
        if status in ("In progress", "Resolved"):
            store.update_status(report["id"], "In progress")
        if status == "Resolved":
            store.update_status(report["id"], "Resolved")
        reports.append(store.get(report["id"]))
    return reports


def main():
    parser = argparse.ArgumentParser(description="Create fictional Study Planner demonstration defects")
    parser.add_argument("--db", default="demo.db")
    args = parser.parse_args()
    try:
        reports = seed_database(args.db)
    except ValueError as error:
        parser.error(str(error))
    for report in reports:
        print(report["id"], report["title"])


if __name__ == "__main__":
    main()
