"""check_all.py: run `check --quick` on many engines at once and summarize.

Use it after changing gm_base.py or gm_checks.py, to re-validate the saved library, or to audit old engines.

    python check_all.py "library/*/engine.py"
    python check_all.py "output/playtest2*/game_*/engine.py" --full      (slower: full tuning check, not the quick one)
"""

import glob
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
GM_ROOT = os.path.dirname(HERE)


def run_one(path, full):
    cmd = [sys.executable, path, "check", "--free"] if full else [sys.executable, path, "check", "--quick"]
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=os.path.dirname(path), timeout=1200, check=False)
    try:
        return json.loads(r.stdout)
    except ValueError:
        return {"verdict": "ERROR", "flags": [f"unparseable output: {(r.stdout + r.stderr)[-300:]}"], "warnings": []}


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    full = "--full" in sys.argv
    if not args:
        raise SystemExit(__doc__)
    paths = []
    for pat in args:
        paths += sorted(glob.glob(pat if os.path.isabs(pat) else os.path.join(GM_ROOT, pat)))
    with ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(lambda p: (p, run_one(p, full)), paths))
    clean = 0
    for path, res in results:
        name = os.path.relpath(os.path.dirname(path), GM_ROOT)
        flags = res.get("flags", [])
        clean += not flags
        print(f"{res.get('verdict', '?'):6} {len(flags):2} flags {len(res.get('warnings', [])):2} warnings  {name}")
        for f in flags[:6]:
            print(f"         - {f[:170]}")
    print(f"\n{clean} of {len(results)} engines clean")


if __name__ == "__main__":
    main()
