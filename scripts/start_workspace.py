from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    workspace_root = Path(__file__).resolve().parent.parent
    launcher = workspace_root / ".vscode" / "start-workspace.ps1"
    command = [
        "powershell",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(launcher),
    ] + sys.argv[1:]
    completed = subprocess.run(command, cwd=workspace_root)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
