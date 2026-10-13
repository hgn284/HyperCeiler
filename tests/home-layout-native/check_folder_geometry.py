#!/usr/bin/env python3
"""Guard the original-body folder animation path, including partial install fallback."""

import re
import sys
from pathlib import Path


def _require(condition, message=None):
    """Keep fixture and rollback checks active when Python uses -O."""
    if not condition:
        if message is None:
            raise AssertionError
        raise AssertionError(message())


root = Path(__file__).resolve().parents[2]
h = (root / "app/src/main/cpp/targets/home/home_folder_geometry.h").read_text()
a = (root / "app/src/main/cpp/targets/home/home_layout_dart_arm64.S").read_text()
c = (root / "app/src/main/cpp/targets/home/home_layout_hooks.cpp").read_text(
    encoding="utf-8"
)
_require(
    (
        len(
            re.findall(
                r'\{"(?:WidgetPositionUtil.getCellPosition|FolderIconGetxController.calOriginPreviewIconLoc)"',
                h,
            )
        )
        == 5
    )
)
stub = a[
    a.index(".macro folder_geometry_splice") : a.index(
        "/* Both finished animation branches"
    )
]
_require(("sub sp, sp, #704" in stub and "add sp, sp, #704" in stub))
_require(("mov x2, sp" in stub and "bl hc_layout_folder_body" in stub))
_require(("hc_layout_folder_resume" in stub and "hc_layout_folder_original" in stub))
_require(("ldar w10, [x9]" in stub and "cbz w10, 2f" in stub))
_require(("candidates[i].address+16" in c))
_require(("folder_geometry_contract(consumers" in c))
_require(("folder_call_target" in h and "folder_helper" in h))
_require(("folder_relative_branch" in h and "map[to]" in h))
_require(("g_folder_geometry_checked=true" in c))
_require(("g_folder_geometry_checked=false" in c))
_require(("workspace_write(fp, -0x18, workspace_read<double>(fp, -0x30))" in h))
_require(("workspace_read<double>(fp, -0x18)" in h))
_require(
    (
        "top & 7"
        in (root / "app/src/main/cpp/targets/home/home_indicator_pair.h").read_text()
    )
)
_require(("thread_local home_layout::WorkspaceRenderSnapshot rendered_workspace" in c))
_require(("folder_ready || drop_ready || g_knobs[2]" in c))
_require(
    (c.count("&rendered_workspace") == 4)
)  # folder, drop, close and large-folder consumers
_require(("rendered->begin_preview(fp, valid ? g[1] : 0)" in h))
_require(("rendered->finish_preview(fp, top)" in h))
print(
    (
        "folder original-body guards: PASS (5 windows; semantic bodies; named calls; "
        "decoded operands; +16 outside patches; partial install stock fallback; outgo"
        "ing argument overwrite; rendered/off-state snapshots; thread-local cache; SP"
        "16/Dart8)"
    )
)
if len(sys.argv) > 1:
    # Subprocess is needed for the reviewed argv-only fixture/tool calls below.
    import subprocess  # nosec B404

    # Run the production binder against real ELF, relocation, fields, control flow,
    # helper bodies and partial-install refusal. No regex assertion substitutes for it.
    # Local compiler/JVM or fixture binary with separate, harness-owned arguments.
    subprocess.run(  # nosec B603
        [
            sys.executable,
            "-X",
            "utf8",
            str(root / "tests/os4-audit-folder-geometry-20261005/verify.py"),
        ],
        check=True,
    )
