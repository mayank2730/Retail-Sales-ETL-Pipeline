
import subprocess
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent

scripts = [
    PROJECT_DIR / "src" / "pipeline.py",
    PROJECT_DIR / "src" / "generate_reports.py",
]

for script in scripts:
    print(f"\nRunning: {script.name}")

    subprocess.run(
        [sys.executable, str(script)],
        cwd=PROJECT_DIR,
        check=True,
    )

print("\nComplete project workflow finished successfully!")
