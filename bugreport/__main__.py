"""Small adapter for the A1 workflow trial; browser UI is a later increment."""
import argparse
import json
import sys

from .service import ReportStore, SEVERITIES


def main():
    parser = argparse.ArgumentParser(description="Create/read structured bug reports locally")
    parser.add_argument("--db", default="reports.db", help="SQLite file (default: reports.db)")
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("create")
    create.add_argument("--title", required=True)
    create.add_argument("--severity", required=True, choices=SEVERITIES)
    for field in ("description", "steps", "expected", "actual", "environment"):
        create.add_argument("--" + field, default="")
    show = commands.add_parser("show")
    show.add_argument("id")
    web = commands.add_parser("serve", help="Run the local browser application")
    web.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    if args.command == "serve":
        from .web import serve
        serve(args.db, args.port)
        return 0
    store = ReportStore(args.db)
    if args.command == "create":
        payload = {key: getattr(args, key) for key in
                   ("title", "severity", "description", "steps", "expected", "actual", "environment")}
        try:
            report = store.create(**payload)
        except ValueError as error:
            parser.error(str(error))
    else:
        report = store.get(args.id)
        if report is None:
            print("Report not found: " + args.id, file=sys.stderr)
            return 1
    # ASCII escapes keep output portable across terminal encodings; json.loads restores Unicode.
    print(json.dumps(report, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
