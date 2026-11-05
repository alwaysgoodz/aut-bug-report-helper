"""Use the existing CI test entry when workflow-file write scope is unavailable."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import unittest


@unittest.skipUnless(os.environ.get("GITHUB_ACTIONS") == "true" and sys.version_info[:2] == (3, 12),
                     "Browser CI bridge runs once in the GitHub Python 3.12 job; use npm run test:browser locally")
class BrowserCIGate(unittest.TestCase):
    def test_committed_browser_acceptance(self):
        root = Path(__file__).resolve().parents[1]
        node, npm = shutil.which("node"), shutil.which("npm")
        self.assertIsNotNone(node, "Existing Ubuntu runner must provide Node.js")
        self.assertIsNotNone(npm, "Existing Ubuntu runner must provide npm")
        print("CI Node:", subprocess.check_output([node, "--version"], text=True).strip(), flush=True)
        subprocess.run([npm, "ci", "--ignore-scripts"], cwd=root, check=True, timeout=180)
        subprocess.run([node, str(root/"node_modules/playwright/cli.js"), "install", "--with-deps", "chromium"],
                       cwd=root, check=True, timeout=360)
        env = {**os.environ, "BUGREPORT_PYTHON": sys.executable}
        # A local Chrome fallback must not silently change the remote browser under test.
        env.pop("BUGREPORT_BROWSER_CHANNEL", None)
        subprocess.run([node, str(root/"node_modules/@playwright/test/cli.js"), "test"],
                       cwd=root, env=env, check=True, timeout=180)
        report = json.loads((root/"test-results/browser-results.json").read_text(encoding="utf-8"))
        print("CI_BROWSER_SUMMARY=" + json.dumps(report["stats"], sort_keys=True), flush=True)
        self.assertEqual(report["stats"]["expected"], 22)
        self.assertEqual(report["stats"]["unexpected"], 0)
        self.assertEqual(report["stats"]["skipped"], 0)
