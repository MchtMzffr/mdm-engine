# Decision Ecosystem — mdm-engine
# Copyright (c) 2026 Mücahit Muzaffer Karafil (MchtMzffr)
# SPDX-License-Identifier: MIT
"""PKG-2: Wheel must only contain allowlisted packages (mdm_engine.mdm*, mdm_engine.security*)."""

import subprocess
import zipfile
from pathlib import Path

import pytest

pytest.importorskip("build", reason="build package required for PKG-2")

REPO_ROOT = Path(__file__).resolve().parent.parent
FORBIDDEN_PREFIXES = ("mdm_engine/features/", "mdm_engine/sim/")


def test_pkg_2_packaged_allowlist() -> None:
    """Wheel must not contain mdm_engine/features or mdm_engine/sim (legacy quarantined)."""
    dist = REPO_ROOT / "dist"
    if dist.exists():
        for f in dist.iterdir():
            f.unlink()
    else:
        dist.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["python", "-m", "build", "--wheel"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
    )
    wheels = list((REPO_ROOT / "dist").glob("*.whl"))
    assert wheels, "No wheel produced"
    found = []
    with zipfile.ZipFile(wheels[0]) as z:
        for name in z.namelist():
            norm = name.replace("\\", "/")
            for prefix in FORBIDDEN_PREFIXES:
                if norm.startswith(prefix):
                    found.append(norm)
                    break
    assert not found, f"PKG-2: legacy packages must not be in wheel: {found}"
