import bisect
import json
import os
import struct
# Subprocess is needed for the reviewed argv-only fixture/tool calls below.
import subprocess  # nosec B404
import sys
from pathlib import Path

D = Path(__file__).resolve().parent
ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else D.parents[1]
sys.path.insert(0, str(D.parents[1] / "tests/home-layout-native"))
from dart_dump import Elf, Symbols

R = Path(
    "C:/Users/XiaoYe/.codex/visualizations/2026/09/29/01a0eb2b-4de7-7442-83d8-db3197b7610f"
)
e = Elf(R / "launcher-7722-libapp.so")
sym = Symbols(R / "launcher-7722-mini.elf")
mini = Elf(R / "launcher-7722-mini.elf")
sec = mini.sections[mini.section_names[".symtab"]]
vas = []
for i in range(sec[4], sec[4] + sec[5], 24):
    n, t, o, sh, v, z = struct.unpack_from("<IBBHQQ", mini.data, i)
    if t & 15 == 2 and v:
        vas.append(v)
vas = sorted(set(vas))
source = (ROOT / "app/src/main/cpp/targets/home/home_layout_hooks.cpp").read_text(
    encoding="utf8"
)


def fun(name):
    a = source.index(name)
    a = source.rfind("\n", 0, a) + 1
    b = source.index("{", a)
    dep = 1
    j = b + 1
    while dep:
        dep += (source[j] == "{") - (source[j] == "}")
        j += 1
    return source[a:j]


names = [
    "_CapsuleIndicatorState.build",
    "Workspace._createIndicator",
    "GridCellDelegate.performLayout",
    "GridOccupiedCellDelegate.performLayout",
    "CellLayoutGetxController.calculateCenterGlobalPosition",
    "CellLayoutGetxController.isItemPosEmpty",
    "GridController.currentConfig",
    "HotSeatLayoutDelegate.cellLayout",
    "LauncherIndicatorState.build",
    "LauncherIndicatorState._wrapWithAnimation",
    "LauncherIndicatorState._buildScreenIndicator",
    "LauncherIndicatorState.isInEditing",
    "LauncherIndicatorState._showIndicator",
    "LauncherIndicatorState._animateIndicator",
    "LauncherIndicatorState._refreshIndicator",
    "LauncherIndicatorState._getCurrentIndicatorType",
    "Container.build",
    "Padding.createRenderObject",
    "ShortcutIconWidget.getTextColor",
    "Color.withAlpha",
    "ShortcutIconWidget._buildTextWidget",
    "ShortcutInfoModel.getPackageName",
    "ShortcutInfoModel.getComponentName",
    "PinShortcutInfoModel.getComponentName",
    "allocateTwoByteString",
    "ShortcutInfoModel.copyShortcutModel",
    "PinShortcutInfoModel.copyShortcutModel",
    "PinShortcutInfoModel.makePinAppComponentName",
    "ShortcutIconWidget.getPrefixAssetName",
    "GridConfig.getTitleTextSize",
    "AppIcon.build",
    "ShortcutIconWidgetConfig.customShortcutIconConfig",
    "FolderInfoModel.hasNewInstalledApp",
    "ShortcutIconWidget._addNewInstallLight",
    "FolderIconGetxController.updateNewInstallNotification",
]
images = {}
spans = {}
for n in names:
    v, z = sym.by_name[n]
    span = vas[bisect.bisect_right(vas, v)] - v
    spans[v] = span
    images[v] = list(struct.unpack("<" + "I" * (span // 4), e.read(v, span)))
for v, words in list(images.items()):
    for i, w in enumerate(words):
        if w & 0xFC000000 != 0x94000000:
            continue
        imm = w & 0x3FFFFFF
        if imm & 0x2000000:
            imm -= 0x4000000
        t = v + i * 4 + imm * 4
        if t not in images:
            images[t] = list(struct.unpack("<32I", e.read(t, 128)))
for v, words in list(images.items()):
    if len(words) > 2 and words[2] & 0xFC000000 == 0x14000000:
        imm = words[2] & 0x3FFFFFF
        if imm & 0x2000000:
            imm -= 0x4000000
        t = v + 8 + imm * 4
        if t not in images:
            images[t] = list(struct.unpack("<32I", e.read(t, 128)))
pre = (
    "\n"
    "#include <vector>\n"
    "#include <map>\n"
    "#include <string>\n"
    "#include <span>\n"
    "#include <array>\n"
    "#include <algorithm>\n"
    "#include <atomic>\n"
    "#include <iostream>\n"
    "#include <cstdint>\n"
    "#include <initializer_list>\n"
    '#include "home_dart_fields.h"\n'
    "std::map<uint32_t,std::vector<uint32_t>> images;std::map<uint32_t,uint32_t> "
    "spans;\n"
    "std::map<std::string,std::pair<uint32_t,uint32_t>> symbols;\n"
    "bool dart_words(uint32_t va,size_t n,std::vector<uint32_t>&out){for(auto it="
    "images.rbegin();it!=images.rend();++it){auto&[v,b]=*it;if(va>=v&&!((va-v)&3)"
    "&&(va-v)/4+n<=b.size()){out.assign(b.begin()+(va-v)/4,b.begin()+(va-v)/4+n);"
    "return true;}}return false;}\n"
    "bool dart_function_words(uint32_t va,uint32_t n,std::vector<uint32_t>&out){r"
    "eturn dart_words(va,n/4,out);}\n"
    "namespace hometweaks {bool HomeTweaksFindSymbol(const char*n,uint32_t*v,uint"
    "32_t*z){auto i=symbols.find(n);if(i==symbols.end())return false;*v=i->second"
    ".first;*z=i->second.second;return true;}}\n"
)
pre += fun("bool bl_target(uint32_t word, uint32_t pc, uint32_t *target) {") + (
    "\n"
    "namespace dartscan {\n"
    "bool function_span(uint32_t va,uint32_t*out){if(!spans.count(va))return fals"
    "e;*out=spans[va];return *out>=4&&*out<=0x4000&&!(*out&3);}\n"
)
pre += fun("bool unique_sequence(") + "\n"
if "bool body(uint32_t va" not in source:
    print("BINDINGS_AUDIT=missing dynamic sites; exit=1")
    sys.exit(1)
pre += (
    fun("bool body(uint32_t va")
    + "\n"
    + fun("bool site(uint32_t va, std::span")
    + "\n"
    + fun("bool site(uint32_t va, std::initializer_list")
    + "\n"
    + fun("bool tagged_call(")
    + "\n}\n"
)
pre += (
    fun("bool capsule_wrapper_layout_compatible(")
    + "\nstruct IndicatorPolicyAnchors { uint32_t gate=0,result=0; };\n"
    + fun("bool indicator_policy_compatible(")
    + "\n"
    + fun("bool indicator_slide_compatible(")
    + "\n"
)
pre += (
    "\n"
    "constexpr uint32_t kDartPrologue=0xa9bf79fd; constexpr int ANDROID_LOG_INFO="
    '4;const char*kTag="test";\n'
    "int __android_log_print(int,const char*,const char*,...){return 0;}\n"
    "namespace nhk{struct CodeSource{};}using Words=std::array<uint32_t,4>;\n"
    "struct Dart{uintptr_t load_base=0x100000000;};Dart data;Dart*g_dart=&data;\n"
    "struct Slot{uintptr_t address;void*replacement;void**original;nhk::CodeSourc"
    "e source;Words words;};Slot g_slots[32];\n"
    "constexpr int kTitleColorSlot=0,kTitleCustomSlot=1,kDrawerTitleSlot=2,kDrawe"
    "rTitleHeightSlot=3,kDesktopTitleSlot=4,kDesktopTitleHeightSlot=5,kTitlePrefi"
    "xSlot=6,kTitleFolderNewSlot=7,kTitleLightSlot=8;\n"
    "bool g_title_color_bound=false,g_title_custom_bound=false,g_drawer_title_bou"
    "nd=false,g_desktop_title_bound=false;\n"
    "std::atomic<int> g_title_color{1},g_title_drawer_sp{18},g_title_desktop_sp{1"
    "8};uint32_t hc_title_custom_enabled=1,hc_title_hide_new_install=1;bool g_tit"
    "le_hide_bound=false;\n"
    "uintptr_t g_title_component_method=0,g_title_pin_method=0;\n"
)
for n in [
    "hc_title_color",
    "hc_title_custom",
    "hc_drawer_title",
    "hc_drawer_title_height",
    "hc_desktop_title",
    "hc_desktop_title_height",
    "hc_title_prefix",
    "hc_title_folder_new",
    "hc_title_light",
]:
    pre += f"void {n}_entry(){{}} void*{n}_original=nullptr;uintptr_t {n}_continue=0;\n"
pre += (
    "uintptr_t hc_drawer_title_caller=0,hc_title_folder_new_caller=0;std::vector<"
    "uint32_t> binds;bool bind_dart_target(uint32_t va,uintptr_t&a,nhk::CodeSourc"
    "e&,Words&w){std::vector<uint32_t>b;if(!dart_words(va,4,b))return false;binds"
    ".push_back(va);a=g_dart->load_base+va;std::copy(b.begin(),b.end(),w.begin())"
    ";return true;}\n"
)
pre += (
    "home_layout::GridFieldOffsets g_grid_field{};\n"
    + fun("void resolve_grid_fields(const char *symbol) {")
    + "\n"
)
for n in [
    "bind_title_color",
    "bind_title_custom",
    "bind_drawer_title",
    "bind_desktop_title",
    "bind_title_hide",
]:
    pre += fun("bool " + n + "(") + "\n"
pre += 'int checks=0,failed=0;void ok(bool v,const char*n){++checks;if(!v){++failed;std::cout<<"FAIL "<<n<<"\\n";}}\nint main(){\n'
for n in names:
    v, z = sym.by_name[n]
    pre += f'symbols["{n}"]={{{v},{z}}};spans[{v}]={spans[v]};\n'
for v, w in images.items():
    pre += f"images[{v}]={{" + ",".join(hex(x) for x in w) + "};\n"
W = sym.by_name["LauncherIndicatorState._wrapWithAnimation"][0]
L = sym.by_name["LauncherIndicatorState.build"][0]
P = sym.by_name["LauncherIndicatorState._buildScreenIndicator"][0]
B = sym.by_name["ShortcutIconWidget._buildTextWidget"][0]
A = sym.by_name["AppIcon.build"][0]
new_insets = "inset_original_frame" in source
if new_insets:
    W = L = sym.by_name["Workspace._createIndicator"][0]
site_offset = (0x488 if "frame-preserved" in source else 0x480) if new_insets else 0x230
C = sym.by_name["Container.build"][0]
PD = sym.by_name["Padding.createRenderObject"][0]
PF = sym.by_name["ShortcutIconWidget.getPrefixAssetName"][0]
HC = sym.by_name["FolderIconGetxController.updateNewInstallNotification"][0]
pre += (
    'resolve_grid_fields("CellLayoutGetxController.calculateCenterGlobalPosition"'
    ");ok(g_grid_field.usable()&&g_grid_field.columns==0x1b&&g_grid_field.rows==0"
    "x23&&g_grid_field.origin==0x3b&&g_grid_field.item_col==0x37&&g_grid_field.it"
    'em_row==0x3f&&g_grid_field.dock_columns==0x13,"complete production GridInfo '
    'resolver publishes actual owning contract");\n'
)
pre += (
    'uint32_t patch=0;IndicatorPolicyAnchors anchors;ok(capsule_wrapper_l'
    'ayout_compatible('
    f'{W}'
    ',0,&patch)&&patch=='
    f'{L + site_offset}'
    ',"real indicator original-insets or legacy packing splice");ok(indic'
    'ator_policy_compatible('
    f'{P}'
    ',0,&anchors)&&anchors.gate==0x3d8&&anchors.result==0x3fc,"real indic'
    'ator gate/result");\n'
)
SH = sym.by_name["LauncherIndicatorState._showIndicator"][0]
RF = sym.by_name["LauncherIndicatorState._refreshIndicator"][0]
pre += f'uint32_t sp=0,idle=0;ok(indicator_slide_compatible({SH},&sp,&idle)&&sp==0xe0&&idle=={RF+0x140},"real slide and idle-caller anchors");\n'
pre += (
    'ok(bind_title_color(),"real title color allocator, fields and splice");ok(bi'
    'nd_title_custom(),"real custom title model and allocators");ok(bind_drawer_t'
    'itle(),"real drawer getter call and font/height sites");ok(bind_desktop_titl'
    'e(),"real desktop font/config/height sites");\n'
)
pre += (
    'ok(g_slots[0].address==data.load_base+'
    f'{B + 240}'
    '&&g_slots[1].address==data.load_base+'
    f'{B + 532}'
    '&&g_slots[2].address==data.load_base+'
    f'{A + 532}'
    '&&g_slots[3].address==data.load_base+'
    f'{A + 688}'
    '&&g_slots[4].address==data.load_base+'
    f'{B + 180}'
    '&&g_slots[5].address==data.load_base+'
    f'{B + 416}'
    ',"all six production title banks use scanned sites");\n'
)
pre += (
    'ok(bind_title_hide()&&g_slots[6].address==data.load_base+'
    f'{PF + 100}'
    '&&hc_title_folder_new_caller==data.load_base+'
    f'{HC + 120}'
    ',"real hide prefix and folder caller");\n'
)
pre += (
    'for(auto va:{'
    f'{L}'
    'u,'
    f'{P}'
    'u,'
    f'{B}'
    'u,'
    f'{A}'
    'u,'
    f'{SH}'
    'u,'
    f'{RF}'
    'u}){auto&v=images[va];for(auto&w:v)if((w&0xfc000000)==0x94000000)w=('
    'w&0xfc000000)|((w-8)&0x03ffffff);v.insert(v.begin(),8,0xd503201f);sp'
    'ans[va]+=32;}\ng_title_color_bound=g_title_custom_bound=g_drawer_titl'
    'e_bound=g_desktop_title_bound=false;\nok(capsule_wrapper_layout_compa'
    'tible('
    f'{W}'
    ',0,&patch)&&patch=='
    f'{L + site_offset + 32}'
    ',"indicator shifted window follows original allocator");\nok(indicato'
    'r_policy_compatible('
    f'{P}'
    ',0,&anchors)&&anchors.gate==0x3f8&&anchors.result==0x41c,"shifted in'
    'dicator bank and continuations");\nok(indicator_slide_compatible('
    f'{SH}'
    ',&sp,&idle)&&sp==0x100&&idle=='
    f'{RF + 352}'
    ',"shifted slide and idle return PC");\nok(bind_title_color()&&bind_ti'
    'tle_custom()&&bind_drawer_title()&&bind_desktop_title(),"all product'
    'ion title binders survive shifted builders");\nok(g_slots[0].address='
    '=data.load_base+'
    f'{B + 272}'
    '&&g_slots[1].address==data.load_base+'
    f'{B + 564}'
    '&&g_slots[2].address==data.load_base+'
    f'{A + 564}'
    '&&g_slots[3].address==data.load_base+'
    f'{A + 720}'
    '&&g_slots[4].address==data.load_base+'
    f'{B + 212}'
    '&&g_slots[5].address==data.load_base+'
    f'{B + 448}'
    ',"no title bank retains old offsets");\n'
)
pre += (
    'auto&pv=images['
    f'{PF}'
    '];pv.insert(pv.begin()+4,4,0xd503201f);spans['
    f'{PF}'
    ']+=16;auto&cv=images['
    f'{HC}'
    '];for(auto&w:cv)if((w&0xfc000000)==0x94000000)w=(w&0xfc000000)|((w-8'
    ')&0x3ffffff);cv.insert(cv.begin(),8,0xd503201f);spans['
    f'{HC}'
    ']+=32;g_title_hide_bound=false;ok(bind_title_hide()&&g_slots[6].addr'
    'ess==data.load_base+'
    f'{PF + 116}'
    '&&hc_title_folder_new_caller==data.load_base+'
    f'{HC + 152}'
    ',"hide prefix and folder caller follow moved code");\n'
)
pre += (
    'auto save=images['
    f'{B}'
    '];images['
    f'{B}'
    '].insert(images['
    f'{B}'
    '].end(),save.begin()+0x110/4,save.begin()+0x120/4);spans['
    f'{B}'
    ']+=16;g_title_color_bound=false;ok(!bind_title_color(),"ambiguous ti'
    'tle replay window rejected");images['
    f'{B}'
    ']=save;spans['
    f'{B}'
    ']-=16;\nauto policy=images['
    f'{P}'
    '];images['
    f'{P}'
    '][0x418/4]^=1;ok(!indicator_policy_compatible('
    f'{P}'
    ',0,&anchors),"foreign editing call refused");images['
    f'{P}'
    ']=policy;\nauto cap=images['
    f'{L}'
    '];images['
    f'{L}'
    ']['
    f'{(site_offset + 32) // 4}'
    ']^=1;ok(!capsule_wrapper_layout_compatible('
    f'{W}'
    ',0,&patch),"capsule replay register mismatch refused");\nstd::cout<<"'
    'BINDINGS_AUDIT="<<checks<<" checks; failed="<<failed<<"\\n";return fa'
    'iled?1:0;}\n'
)
out = D / ("bindings-" + ROOT.name)
out.mkdir(exist_ok=True)
(out / "test.cpp").write_text(pre, encoding="utf8")
os.environ["ZIG_GLOBAL_CACHE_DIR"] = str(D / "runtime/cache")
os.environ["ZIG_LOCAL_CACHE_DIR"] = str(out / "cache")
for cmd in [
    [
        str(D / "runtime/zig-windows-x86_64-0.13.0/zig.exe"),
        "c++",
        "-std=c++20",
        "-Wall",
        "-Wextra",
        "-Werror",
        "-Wno-sign-compare",
        "-I" + str(ROOT / "app/src/main/cpp/targets/home"),
        str(out / "test.cpp"),
        "-o",
        str(out / "test.exe"),
    ],
    [str(out / "test.exe")],
]:
    # Local compiler/JVM or fixture binary with separate, harness-owned arguments.
    r = subprocess.run(  # nosec B603
        cmd, capture_output=True, text=True, encoding="utf8", errors="replace"
    )
    print(r.stdout + r.stderr)
    with (D / "commands.jsonl").open("a", encoding="utf8") as f:
        f.write(
            json.dumps(
                dict(
                    command=cmd,
                    input=str(ROOT),
                    stdout=r.stdout,
                    stderr=r.stderr,
                    exit=r.returncode,
                )
            )
            + "\n"
        )
    if r.returncode:
        sys.exit(r.returncode)
