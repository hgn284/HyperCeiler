#!/usr/bin/env python3
"""Pin the original drop-back center calculation to the known launcher image."""

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
header = root / "app/src/main/cpp/targets/home/home_drop_geometry.h"
_require((header.exists()), lambda: ("drop-back geometry path missing"))
h = header.read_text()
a = (root / "app/src/main/cpp/targets/home/home_layout_dart_arm64.S").read_text()
c = (root / "app/src/main/cpp/targets/home/home_layout_hooks.cpp").read_text()
s = (root / "app/src/main/cpp/targets/home/tweaks/symtab.cpp").read_text()
_require(("CellLayoutGetxController.calculateCenterGlobalPosition" in s))
_require(("drop_ready ||" in c and "bind_drop_geometry();" in c))
_require(("hc_layout_drop_enabled" in a and "hc_layout_drop_body" in a))
_require(("hc_layout_drop_resume" in a and "hc_layout_drop_original" in a))
_require((a.count("drop_geometry_splice hc_layout_drop_") == 2))
_require(("rendered->begin_drop(fp, g[1])" in h))
_require(("rendered->finish_drop(fp, 0)" in h))
_require(
    (
        "top & 7"
        in (root / "app/src/main/cpp/targets/home/home_indicator_pair.h").read_text()
    )
)
print(
    "drop-back original-body guards: PASS (two no-call windows; atomic bank; rendered frame; Dart8/nativeSP16)"
)

if len(sys.argv) > 1:
    from dart_dump import Elf, Symbols, engine

    e, syms = Elf(sys.argv[1]), Symbols(sys.argv[2])
    name = "CellLayoutGetxController.calculateCenterGlobalPosition"
    va, size = max(
        ((v, z) for v, z, n in syms.entries if n == name), key=lambda x: x[1]
    )
    _require((size == 0x5C0))
    data = e.read(va, size)
    digest = 0xCBF29CE484222325
    for byte in data:
        digest = ((digest ^ byte) * 0x100000001B3) & 0xFFFFFFFFFFFFFFFF
    _require(
        (digest == int(re.search(r"kDropGeometryHash = (0x[0-9a-f]+)", h).group(1), 16))
    )
    sites = re.findall(r"\{(0x[0-9a-f]+), \{(0x[0-9a-f, ]+)\}\}", h)
    _require((len(sites) == 2))
    for offset, words in sites:
        off = int(offset, 16)
        expected = b"".join(
            int(w.strip(), 16).to_bytes(4, "little") for w in words.split(",")
        )
        _require((e.read(va + off, 16) == expected))
        _require(
            (
                all(
                    i.mnemonic not in ("bl", "blr", "b", "ret")
                    for i in engine().disasm(expected, va + off)
                )
            )
        )
    print(
        "launcher 7722 drop-back body: PASS (0x5c0 bytes; full hash; +0x120/+0x1b8 exact windows)"
    )
