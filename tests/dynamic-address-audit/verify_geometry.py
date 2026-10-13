import json
import os
# Subprocess is needed for the reviewed argv-only fixture/tool calls below.
import subprocess  # nosec B404
from pathlib import Path

D = Path("tests/dynamic-address-audit").resolve()
ROOT = D.parents[1]
out = D / "geometry"
out.mkdir(exist_ok=True)
os.environ["ZIG_GLOBAL_CACHE_DIR"] = str(D / "runtime/cache")
os.environ["ZIG_LOCAL_CACHE_DIR"] = str(out / "cache")
# Audit gate, not a re-shaper. It used to declare its own `contract` and call the helper with
# it, which silently re-inserted a field at whatever position the OLD signature wanted. The
# test sources now pass their own resolved GridFieldOffsets (the offsets are decoded per
# launcher image, so a fixture-owned set is the only honest thing to pass), and the wrapper's
# parameter list no longer matched: the renamed call sites passed an extra argument the
# wrapper could not accept, and the audit failed to compile for a reason that had nothing to
# do with the code under test. Each gate below now takes exactly the production signature and
# forwards it unchanged, adding one thing the raw helper cannot: a refusal when the caller
# leaves the field null or unresolved. `usable()` is the production admission rule, so a call
# site that reaches the helper with a half-decoded set is rejected here rather than being
# quietly no-op'd on device.
wrap = (
    '#include "targets/home/home_drop_geometry.h"\n'
    "#include <cstdio>\n"
    "static const home_layout::GridFieldOffsets *audit_field(const home_layout::G"
    "ridFieldOffsets *f, const char *who) {\n"
    '    if (f == nullptr) { std::printf("AUDIT FAIL %s: null field\\n", who); ret'
    "urn nullptr; }\n"
    '    if (!f->usable()) { std::printf("AUDIT FAIL %s: unresolved field set\\n",'
    " who); return nullptr; }\n"
    "    return f;\n"
    "}\n"
    "static bool audit_hotseat(uintptr_t f,uint64_t h,double s,double*out,const h"
    "ome_layout::GridFieldOffsets*fld){return home_layout::inset_hotseat_frame(f,"
    'h,s,out,audit_field(fld,"inset_hotseat_frame"));}\n'
    "static bool audit_inset(uintptr_t f,uint64_t h,bool o,const home_layout::Gri"
    "dFieldOffsets*fld,double t,double b,double s,double*out,home_layout::Workspa"
    "ceRenderSnapshot*r=nullptr){return home_layout::inset_workspace_frame(f,h,o,"
    'audit_field(fld,"inset_workspace_frame"),t,b,s,out,r);}\n'
    "static bool audit_folder_grid(uintptr_t f,double t,double b,double s,double*"
    "out,const home_layout::WorkspaceRenderSnapshot*r,const home_layout::GridFiel"
    "dOffsets*fld){return home_layout::folder_grid_geometry(f,t,b,s,out,r,audit_f"
    'ield(fld,"folder_grid_geometry"));}\n'
    "static bool audit_folder_body(uintptr_t f,uint64_t h,uintptr_t v,unsigned k,"
    "double t,double b,double s,home_layout::WorkspaceRenderSnapshot*r,const home"
    "_layout::GridFieldOffsets*fld){return home_layout::folder_geometry_body(f,h,"
    'v,k,t,b,s,r,audit_field(fld,"folder_geometry_body"));}\n'
    "static bool audit_drop_body(uintptr_t f,uint64_t h,uintptr_t v,unsigned k,co"
    "nst home_layout::GridFieldOffsets*fld,double t,double b,double s,home_layout"
    "::WorkspaceRenderSnapshot*r){return home_layout::drop_geometry_body(f,h,v,k,"
    'audit_field(fld,"drop_geometry_body"),t,b,s,r);}\n'
)
records = []
for name in [
    "workspace_geometry_test",
    "folder_geometry_test",
    "folder_render_snapshot_test",
    "drop_render_snapshot_test",
    "hotseat_capacity_test",
    "indicator_pair_test",
]:
    s = (ROOT / "tests/home-layout-native" / f"{name}.cpp").read_text(encoding="utf8")
    for a, b in [
        ("inset_hotseat_frame", "audit_hotseat"),
        ("inset_workspace_frame", "audit_inset"),
        ("folder_grid_geometry", "audit_folder_grid"),
        ("folder_geometry_body", "audit_folder_body"),
        ("drop_geometry_body", "audit_drop_body"),
    ]:
        s = s.replace("home_layout::" + a, b).replace(a + "(", b + "(")
    cpp = out / (name + ".cpp")
    cpp.write_text(wrap + s, encoding="utf8")
    for cmd in [
        [
            str(D / "runtime/zig-windows-x86_64-0.13.0/zig.exe"),
            "c++",
            "-std=c++20",
            "-Wall",
            "-Wextra",
            "-Wno-unused-function",
            "-I" + str(ROOT / "app/src/main/cpp"),
            str(cpp),
            "-o",
            str(out / (name + ".exe")),
        ],
        [str(out / (name + ".exe"))],
    ]:
        # Known local geometry fixture and build tool selected by this harness; no shell.
        r = subprocess.run(  # nosec B603
            cmd, capture_output=True, text=True, encoding="utf8", errors="replace"
        )
        rec = dict(
            command=cmd, input=name, stdout=r.stdout, stderr=r.stderr, exit=r.returncode
        )
        records.append(rec)
        print(name, r.returncode, r.stdout + r.stderr)
        if r.returncode:
            (D / "geometry-results.json").write_text(
                json.dumps(records, indent=2), encoding="utf8"
            )
            raise SystemExit(r.returncode)
(D / "geometry-results.json").write_text(json.dumps(records, indent=2), encoding="utf8")
