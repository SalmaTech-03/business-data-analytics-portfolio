"""Minimal test runner (pytest was not installable in the build environment).
Usage: python tests/run_tests.py [-k substring]   |   pytest also works if installed."""
import importlib
import sys
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def main(argv):
    pat = argv[argv.index("-k") + 1] if "-k" in argv else ""
    passed = failed = 0
    for f in sorted(Path(__file__).parent.glob("test_*.py")):
        mod = importlib.import_module(f.stem)
        for name in sorted(n for n in dir(mod) if n.startswith("test_")):
            if pat and pat not in name and pat not in f.stem:
                continue
            t0 = time.time()
            try:
                getattr(mod, name)()
                passed += 1; print(f"PASS  {f.stem}::{name}  ({time.time() - t0:.1f}s)")
            except Exception:
                failed += 1; print(f"FAIL  {f.stem}::{name}"); traceback.print_exc()
    print(f"\n{passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
