"""Explicit fictional examples; refuse to change a database that already has reports."""
import argparse

from bugreport.service import ReportStore


def main():
    parser = argparse.ArgumentParser(description="Create fictional Study Planner demonstration defects")
    parser.add_argument("--db", default="demo.db")
    args = parser.parse_args()
    store = ReportStore(args.db)
    if store.counts()["total"]:
        parser.error("Demo seeding requires an empty database; existing reports were not changed")
    examples = [
        ("Login screen stays blank after sign-in", "high", "Open", "Sign in with the demo account", "The weekly planner opens", "A blank panel appears", "Study Planner demo / Chrome / Windows"),
        ("Task reminders arrive twice", "medium", "In progress", "Create a task and enable one reminder", "One reminder is delivered", "Two reminders arrive together", "Study Planner demo / Firefox"),
        ("Completed tasks remain in the active list", "low", "Resolved", "Complete a task, then open Active tasks", "The completed task is hidden", "The task remains visible", "Study Planner demo / Safari"),
        ("Changes disappear after refreshing the planner", "critical", "Open", "", "", "A new task disappears after reload", ""),
    ]
    for title, severity, status, steps, expected, actual, environment in examples:
        report = store.create(title=title, severity=severity,
                              description="Fictional Study Planner defect for a course demonstration; not a known defect in this helper.",
                              steps=steps, expected=expected, actual=actual, environment=environment)
        if status in ("In progress", "Resolved"):
            store.update_status(report["id"], "In progress")
        if status == "Resolved":
            store.update_status(report["id"], "Resolved")
        print(report["id"], title)


if __name__ == "__main__":
    main()
