"""Isolated test-only study data. Never points at the real participant directory."""
import tempfile
from tools.peer_study import StudyServer, StudyStore


def main():
    with tempfile.TemporaryDirectory(prefix="peer-study-browser-test-") as directory:
        with StudyStore(directory, test_only=True) as store:
            with StudyServer(("127.0.0.1", 8790), store) as server:
                print("TEST-ONLY peer-study server: http://127.0.0.1:8790", flush=True)
                try:
                    server.serve_forever()
                except KeyboardInterrupt:
                    pass


if __name__ == "__main__":
    main()
