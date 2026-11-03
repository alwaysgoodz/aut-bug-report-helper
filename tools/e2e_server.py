"""An isolated database for each Playwright run; never modifies the user's DB."""
from pathlib import Path
import tempfile

from bugreport.web import serve


if __name__ == "__main__":
    with tempfile.TemporaryDirectory(prefix="bugreport-e2e-") as directory:
        serve(Path(directory)/"reports.db", port=8780)
