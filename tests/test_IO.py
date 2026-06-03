"""IO test"""

import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
GYS_IO = REPO_ROOT / "build" / "apps" / "io" / "gys_io"
IO_DIR = REPO_ROOT / "apps" / "io"


def test_gys_io_runs():
    assert GYS_IO.is_file(), f"Build gys_io first (missing {GYS_IO})"

    result = subprocess.run(
        ["mpirun", "-n", "1", str(GYS_IO), "gys_io.yaml", "pdi_default.yaml"],
        cwd=IO_DIR,
    )
    assert result.returncode == 0
