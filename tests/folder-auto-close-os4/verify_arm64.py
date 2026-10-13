import re
import struct
import sys
from pathlib import Path


def _require(condition, message=None):
    """Keep fixture and rollback checks active when Python uses -O."""
    if not condition:
        if message is None:
            raise AssertionError
        raise AssertionError(message())


W = Path(__file__).resolve().parents[2]
D = Path(__file__).resolve().parent
sys.path.insert(0, str(W / "tests/back-gesture-os4/runtime"))
from unicorn import UC_ARCH_ARM64, UC_HOOK_CODE, UC_MODE_ARM, Uc
from unicorn.arm64_const import (
    UC_ARM64_REG_PC,
    UC_ARM64_REG_SP,
    UC_ARM64_REG_X0,
    UC_ARM64_REG_X1,
    UC_ARM64_REG_X15,
    UC_ARM64_REG_X22,
    UC_ARM64_REG_X26,
    UC_ARM64_REG_X27,
    UC_ARM64_REG_X28,
    UC_ARM64_REG_X29,
    UC_ARM64_REG_X30,
)

s = (D / "FolderAutoCloseTest.cpp").read_text(encoding="utf8")
words = [
    int(x.rstrip("u"), 16) for x in re.search(r"words=\{(.*?)\}", s, re.S)[1].split(",")
]
va = 0x144F440
rx = 0x17D148C
registered = 0x89A718
logger = 0x8B3840
close = 0x1931B18
checks = 0


def mapat(uc, mapped, addr, size=0x1000):
    page = addr & ~0xFFF
    for p in range(page, (addr + size + 0xFFF) & ~0xFFF, 0x1000):
        if p not in mapped:
            uc.mem_map(p, 0x1000)
            mapped.add(p)


def make_hook(mode, opened, exists, null, count):
    def hook(uc, pc, size, data):
        if pc == va + 0x400:
            uc.emu_stop()
            return
        if pc in [rx, registered, logger, close]:
            if pc == rx:
                result = mode if uc.reg_read(UC_ARM64_REG_X1) == 0x200101 else opened
            elif pc == registered:
                result = exists
            else:
                result = None
            if pc == close:
                count[0] += 1
            uc.reg_write(
                UC_ARM64_REG_X0,
                (null + (32 if result else 48) if result is not None else null),
            )
            uc.reg_write(UC_ARM64_REG_PC, uc.reg_read(UC_ARM64_REG_X30))

    return hook


def run_case(enabled, mode, exists, opened):
    uc = Uc(UC_ARCH_ARM64, UC_MODE_ARM)
    mapped = set()

    for addr, size in [
        (va, 0x1000),
        (0x100000, 0x10000),
        (0x200000, 0x2000),
        (0x300000, 0x1000),
        (0x400000, 0x1000),
        (0x500000, 0x4000),
        (0x600000, 0x100000),
        (rx, 4),
        (registered, 4),
        (logger, 4),
        (close, 4),
    ]:
        mapat(uc, mapped, addr, size)
    uc.mem_write(va, struct.pack("<" + "I" * len(words), *words))
    if enabled:
        uc.mem_write(va + 0x328, struct.pack("<I", 0xD503201F))
    fp = 0x108000
    thread = 0x100000
    pool = 0x600000
    null = 0x300001
    for reg, val in [
        (UC_ARM64_REG_X29, fp),
        (UC_ARM64_REG_X15, fp - 0x38),
        (UC_ARM64_REG_SP, 0x107000),
        (UC_ARM64_REG_X26, thread),
        (UC_ARM64_REG_X27, pool),
        (UC_ARM64_REG_X28, 0),
        (UC_ARM64_REG_X22, null),
    ]:
        uc.reg_write(reg, val)

    def w64(at, v):
        uc.mem_write(at, struct.pack("<Q", v))

    w64(fp - 0x20, 0x200101)
    w64(thread + 0x78, 0x500000)
    w64(0x500000 + 0x1CD0, 0x600001)
    w64(0x500000 + 0x3990, 0x400001)
    w64(0x500000 + 0x2490, 0x600001)
    uc.mem_write(0x400001 + 0xEF, struct.pack("<I", 0x200201))
    count = [0]

    hook = make_hook(mode, opened, exists, null, count)

    uc.hook_add(UC_HOOK_CODE, hook)
    uc.emu_start(va + 0x320, va + len(words) * 4, count=1000)
    expected = int((mode or enabled) and exists and opened)
    _require(
        (count[0] == expected),
        lambda: (
            (
                enabled,
                mode,
                exists,
                opened,
                count[0],
                expected,
            )
        ),
    )
    return 1


for enabled in [False, True]:
    for mode in [False, True]:
        for exists in [False, True]:
            for opened in [False, True]:
                checks += run_case(enabled, mode, exists, opened)

print(
    f"FOLDER_AUTO_CLOSE_ARM64={checks} cases; failed=0; actual stock mode/registered/open/close instruction path; mocked Dart callees"
)
