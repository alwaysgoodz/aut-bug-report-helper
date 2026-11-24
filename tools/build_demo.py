"""Versioned allowlisted Windows portable ZIP; no pip/runtime installation."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
RUNTIME_URL = "https://www.python.org/ftp/python/3.13.17/python-3.13.17-embed-amd64.zip"
RUNTIME_SHA256 = "9e35319bffedab8b36ad44d8f377cb4f1733bcec257a0b6d04d94f01486ddb38"
RUNTIME_VERSION = "3.13.17"
PACKAGE_NAME = "BugReportHelper-Windows-x64-v1.0.0-demo"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def archive(directory, destination):
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as bundle:
        for path in sorted(directory.rglob("*")):
            if path.is_file():
                bundle.write(path, Path(directory.name) / path.relative_to(directory))


def build(output, runtime_zip=None, evidence_dir=None):
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    cache = ROOT / "tmp/runtime-cache"
    cache.mkdir(parents=True, exist_ok=True)
    runtime = Path(runtime_zip).resolve() if runtime_zip else cache / "python-3.13.17-embed-amd64.zip"
    if not runtime.exists():
        with urllib.request.urlopen(RUNTIME_URL, timeout=45) as source, runtime.open("wb") as target:
            shutil.copyfileobj(source, target)
    if digest(runtime) != RUNTIME_SHA256:
        raise ValueError("Embedded Python SHA-256 does not match the official release; refusing to package")
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    with tempfile.TemporaryDirectory(prefix="demo-build-", dir=ROOT / "tmp") as temporary:
        package = Path(temporary) / PACKAGE_NAME
        app = package / "app"
        app.mkdir(parents=True)
        # Only actual application and required launcher/seed code enter the runtime.
        for source in sorted((ROOT / "bugreport").rglob("*")):
            if source.is_file() and "__pycache__" not in source.parts:
                destination = app / source.relative_to(ROOT)
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)
        (app / "tools").mkdir()
        for name in ("__init__.py", "demo_launcher.py", "seed_demo.py"):
            shutil.copy2(ROOT / "tools" / name, app / "tools" / name)
        runtime_dir = package / "runtime"
        runtime_dir.mkdir()
        with zipfile.ZipFile(runtime) as bundle:
            for member in bundle.infolist():
                target = (runtime_dir / member.filename).resolve()
                if not target.is_relative_to(runtime_dir.resolve()):
                    raise ValueError("Unsafe path in runtime archive")
            bundle.extractall(runtime_dir)
        # Isolated runtime: ignore machine Python, PATH and site-packages.
        (runtime_dir / "python313._pth").write_text("python313.zip\n.\n../app\n", encoding="utf-8")
        for name in ("StartDemo.cmd", "ResetDemo.cmd", "CheckDemo.cmd"):
            content = (ROOT / "packaging" / name).read_text(encoding="utf-8")
            (package / name).write_bytes(content.replace("\r\n", "\n").replace("\n", "\r\n").encode("ascii"))
        shutil.copy2(ROOT / "packaging/DEMO-GUIDE.html", package / "DEMO-GUIDE.html")
        shutil.copy2(ROOT / "packaging/START-HERE.txt", package / "START-HERE.txt")
        shutil.copy2(ROOT / "packaging/THIRD-PARTY-NOTICES.txt", package / "THIRD-PARTY-NOTICES.txt")
        app_files = {p.relative_to(app).as_posix(): digest(p) for p in sorted(app.rglob("*")) if p.is_file()}
        evidence_hashes = {}
        tested_source = None
        if evidence_dir:
            evidence_dir = Path(evidence_dir).resolve()
            tested = json.loads((evidence_dir / "tested-build.json").read_text(encoding="utf-8"))
            if tested["app_sha256"] != app_files or tested["runtime_sha256"] != RUNTIME_SHA256:
                raise ValueError("Delivery application/runtime differs from the tested build; rerun verification before packaging")
            tested_source = tested["source_commit"]
            selected_evidence = ("VALIDATION.txt", "tested-build.json", "dashboard.png", "guidance-86.png",
                                 "report-detail.png", "phone.png", "guide.png", "python.log", "browser.log",
                                 "browser-results.json", "portable-smoke.json", "offline-rehearsal.json",
                                 "implementation-ci.json", "implementation-ci.log")
            (package / "Evidence").mkdir()
            for name in selected_evidence:
                path = evidence_dir / name
                if path.is_file():
                    shutil.copy2(path, package / "Evidence" / name)
                    evidence_hashes[name] = digest(path)
        else:
            (package / "Evidence").mkdir()
            (package / "Evidence/VALIDATION.txt").write_text(
                "Development build: archived verification was not attached.\n"
                "Run source tests and verify the extracted runtime before presentation.\n"
                "Use --evidence-dir with a matching tested-build.json to include delivery evidence.\n",
                encoding="utf-8")
        dirty = subprocess.check_output(["git", "status", "--porcelain", "--", "bugreport", "tools/demo_launcher.py", "tools/seed_demo.py", "tools/build_demo.py", "packaging"], cwd=ROOT, text=True)
        if dirty:
            raise ValueError("Commit application/packaging changes before producing a versioned delivery")
        manifest = dict(package=PACKAGE_NAME, built_at=datetime.now(timezone.utc).isoformat(),
                        source_commit=revision, runtime_url=RUNTIME_URL, runtime_sha256=RUNTIME_SHA256,
                        runtime_version=RUNTIME_VERSION, app_sha256=app_files,
                        tested_application_commit=tested_source, evidence_sha256=evidence_hashes,
                        excludes=["personal data", "real peer-study data", "credentials", "node_modules", "uncommitted A1 reports"],
                        data_policy="A fresh fictional demonstration database is created at first launch only")
        (package / "BUILD-INFO.json").write_text(json.dumps(manifest, indent=2)+"\n", encoding="utf-8")
        portable = output / f"{PACKAGE_NAME}.zip"
        archive(package, portable)
        source_dir = Path(temporary) / "BugReportHelper-Source"
        source_dir.mkdir()
        tracked = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode().split("\0")
        selected = []
        for name in tracked:
            if not name:
                continue
            path = Path(name)
            if path.parts[0] in ("bugreport", "tools", "tests", "packaging", "design-system") or name in ("README.md", "CONTRIBUTING.md", "package.json", "package-lock.json", "playwright.config.cjs", ".gitattributes", ".gitignore"):
                selected.append(name)
                target = source_dir / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(subprocess.check_output(["git", "show", f"{revision}:{name}"], cwd=ROOT))
        (source_dir / "SOURCE-INFO.json").write_text(json.dumps(dict(source_commit=revision, included=selected), indent=2)+"\n", encoding="utf-8")
        (source_dir / "SOURCE-START.txt").write_text(
            "Bug Report Helper source companion\n\n"
            "Requires Python 3.11+ with SQLite. From this directory:\n"
            "  python -m tools.demo_launcher\n"
            "  python -m unittest discover -s tests -v\n\n"
            "Browser development checks additionally require Node.js 22 and npm ci.\n"
            "  npm run test:browser\n\n"
            "Build a portable ZIP (downloads the pinned official runtime at build time):\n"
            "  python -m tools.build_demo --output dist\n"
            "The builder expects a Git checkout. For rebuilding, use the exact source_commit\n"
            "in SOURCE-INFO.json from https://github.com/alwaysgoodz/aut-bug-report-helper .\n"
            "The source companion excludes assessment PDFs/history and participant data;\n"
            "README links to those historical materials require the full Git repository.\n",
            encoding="utf-8")
        source_zip = output / "BugReportHelper-Source.zip"
        archive(source_dir, source_zip)
    checksums = {path.name: digest(path) for path in (portable, source_zip)}
    (output / "SHA256SUMS.txt").write_text("".join(f"{value}  {key}\n" for key, value in checksums.items()), encoding="utf-8")
    print(json.dumps(dict(output=str(output), source_commit=revision, checksums=checksums), indent=2))
    return portable, source_zip


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    parser.add_argument("--runtime-zip", type=Path)
    parser.add_argument("--evidence-dir", type=Path, help="Add allowlisted verified evidence; app/runtime hashes must match")
    args = parser.parse_args()
    build(args.output, args.runtime_zip, args.evidence_dir)
