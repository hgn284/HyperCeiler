import bisect
import re
import struct
# Subprocess is needed for the reviewed argv-only fixture/tool calls below.
import subprocess  # nosec B404
import sys
from pathlib import Path

D = Path(__file__).resolve().parent
W = D.parents[1]
ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else W
src = (ROOT / "app/src/main/cpp/targets/home/home_layout_hooks.cpp").read_text(
    encoding="utf8"
)
if "bool bind_folder_layout()" not in src:
    print(
        "FOLDER_LAYOUT=legacy baseline; title/width/padding native transport absent; NEW_FEATURE_TEST=FAIL"
    )
    sys.exit(1)
sys.path.insert(0, str(W / "tests/home-layout-native"))
from dart_dump import Elf, Symbols

R = Path(
    "C:/Users/XiaoYe/.codex/visualizations/2026/09/29/01a0eb2b-4de7-7442-83d8-db3197b7610f"
)
e = Elf(R / "launcher-7722-libapp.so")
s = Symbols(R / "launcher-7722-mini.elf")
m = Elf(R / "launcher-7722-mini.elf")
sec = m.sections[m.section_names[".symtab"]]
vas = sorted(
    set(
        v
        for _, t, _, _, v, _ in (
            struct.unpack_from("<IBBHQQ", m.data, a)
            for a in range(sec[4], sec[4] + sec[5], 24)
        )
        if t & 15 == 2 and v
    )
)


def fun(source, name):
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
    "FolderGridViewGetxController.calGridWidth",
    "FolderGridViewGetxController.folderCellWidth",
    "FolderGridViewGetxController.folderGridOuterHorizontalPadding",
    "FolderGridViewGetxController.folderGridPaddingLeft",
    "FolderHeaderWidget._buildText",
    "FolderHeaderWidget._buildEditor",
    "FolderClingWidget.getFolderClingWidth",
    "FolderClingGetxController._calcFolderPaddingTop",
    "_FlutterTextViewState._resolveEffectiveTextAlign",
    "GridController.currentConfig",
    "RxObjectMixin.value",
    "AndroidAttributeUtils.convertGravity",
    "_encodeParagraphStyle",
    "AndroidAttributeUtils.convertTextAlignment",
    "Container.build",
    "Container._paddingIncludingDecoration",
]
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
    "#include <cstring>\n"
    "#include <optional>\n"
    "#include <cmath>\n"
    "#ifdef _WIN32\n"
    "#ifndef NOMINMAX\n"
    "#define NOMINMAX\n"
    "#endif\n"
    "#include <windows.h>\n"
    "#else\n"
    "#include <sys/mman.h>\n"
    "#endif\n"
    '#include "home_layout_config.h"\n'
    '#include "home_dart_fields.h"\n'
    '#include "home_widget_move.h"\n'
    '#include "home_gadget_bridge.h"\n'
    '#include "home_folder_layout.h"\n'
    "std::map<uint32_t,std::vector<uint32_t>> images;std::map<std::string,std::pa"
    "ir<uint32_t,uint32_t>> symbols;\n"
    "bool dart_function_words(uint32_t va,uint32_t n,std::vector<uint32_t>&out){i"
    "f(!images.count(va)||images[va].size()*4!=n)return false;out=images[va];retu"
    "rn true;}\n"
    "bool production_accept(const char*,uint32_t,uint32_t);\n"
    "namespace hometweaks{bool HomeTweaksFindSymbol(const char*n,uint32_t*v,uint3"
    "2_t*z){if(!symbols.count(n))return false;auto p=symbols[n];if(!production_ac"
    "cept(n,p.first,p.second))return false;*v=p.first;*z=p.second;return true;}}\n"
    "int bl_imm_words(uint32_t w){int n=int(w&0x3ffffff);if(n&0x2000000)n-=0x4000"
    "000;return n;}\n"
)
registry_source = (ROOT / "app/src/main/cpp/targets/home/tweaks/symtab.cpp").read_text(
    encoding="utf8"
)
pre += (
    "struct Segment{uintptr_t begin,end;uint32_t flags;};struct Image{uintptr_t b"
    "ase;Segment segments[16];size_t segmentCount;};constexpr uint32_t kMaxFuncti"
    "onBytes=0x4000;\n"
)
if "CodeView(image)" in registry_source:
    sys.path.insert(0, str(W / "tests/os4-audit-symbol-prologue-20261005"))
    from fixture_support import codeview_fixture

    pre += codeview_fixture(
        ROOT,
        (
            "for(const auto& [va,b]:images){const uintptr_t begin=reinterpret_cast<uintpt"
            "r_t>(b.data());const size_t bytes=b.size()*4;if(address>=begin&&address-begi"
            "n<=bytes&&out.size()<=bytes-(address-begin)){std::memcpy(out.data(),reinterp"
            "ret_cast<void*>(address),out.size());return true;}}return false;"
        ),
        True,
    )
for name in [
    "bool NameEquals(",
    "bool VaInExecSegment(",
    "bool LooksLikeDartFunction(",
]:
    pre += fun(registry_source, name) + "\n"
pre += (
    "bool production_accept(const char*n,uint32_t va,uint32_t size){if(!images.co"
    "unt(va))return false;auto&b=images[va];uintptr_t begin=(uintptr_t)b.data();I"
    "mage im{};im.base=begin-va;im.segmentCount=1;im.segments[0]={begin,begin+b.s"
    "ize()*4,5};return LooksLikeDartFunction(im,va,n,size); }\n"
)
for n in [
    "bool is_ldur_double(",
    "bool is_ldur_word(",
    "int imm9(",
    "uint32_t rn(",
    "uint32_t rt(",
    "bool bl_target(uint32_t word, uint32_t pc, uint32_t *target) {",
]:
    pre += fun(src, n) + "\n"
pre += "namespace dartscan { bool function_span(uint32_t va,uint32_t*out){if(!images.count(va))return false;*out=images[va].size()*4;return true;}\n"
for n in [
    "bool unique_sequence(",
    "bool body(uint32_t va",
    "bool site(uint32_t va, std::span",
    "bool site(uint32_t va, std::initializer_list",
]:
    pre += fun(src, n) + "\n"
pre += (
    "}\n"
    "constexpr uint32_t kDartPrologue=0xa9bf79fd;constexpr int ANDROID_LOG_INFO=4"
    ';constexpr int ANDROID_LOG_WARN=5;const char*kTag="test";int __android_log_p'
    "rint(int,const char*,const char*,...){return 0;}\n"
)
pre += (
    "namespace nhk{struct CodeSource{};}using Words=std::array<uint32_t,4>;struct"
    " Slot{uintptr_t address=0;void*replacement=nullptr;void**original=nullptr;nh"
    "k::CodeSource source;Words original_words{};bool registered=false;};\n"
    'struct Dart{uintptr_t load_base=0x100000000;std::string path="libapp.so";};D'
    "art data;Dart*g_dart=&data;Slot g_slots[8];constexpr int kFolderLayoutSlotBa"
    "se=0;\n"
)
if "g_folder_layout_retry_at_ms" in src:
    pre += (
        "uint64_t test_clock=1;uint64_t monotonic_ms(){return test_clock;}uint64_t g_"
        "folder_layout_retry_at_ms=0;unsigned g_folder_layout_retry_failures=0;\n"
    )
pre += (
    "void*hc_folder_layout_original[8]{};uint64_t hc_folder_layout_requested=3;ui"
    "nt32_t hc_folder_layout_ready=0;bool g_folder_layout_bound=false,g_folder_la"
    "yout_checked=false,g_folder_layout_attempted=false;int g_folder_cell_width_f"
    "ield=-1,g_folder_gap_field=-1,g_folder_screen_width_field=-1,g_folder_screen"
    "_height_field=-1,g_folder_cling_width_field=-1,g_folder_controller_config_fi"
    "eld=-1,g_folder_rx_value_field=-1,g_folder_enum_index_field=-1;uint32_t g_fo"
    "lder_center_pool=0;\n"
)
# The inner-Container plan and its owner-local distance. Mirrors production exactly:
# the kind7 body reads the Container owner through the POST-dart_save x15 that the
# splice stored in the native save block, not through x29.
pre += "home_layout::FolderInnerContainer g_folder_inner;uint32_t g_folder_inner_owner_local=0;bool g_folder_inner_ready=false;\n"
for i in range(8):
    pre += f"void hc_folder_layout_{i}_entry(){{}}\n"
pre += (
    "bool bind_dart_target(uint32_t va,uintptr_t&a,nhk::CodeSource&,Words&w){for("
    "auto&[v,b]:images)if(va>=v&&!((va-v)&3)&&(va-v)/4+4<=b.size()){a=data.load_b"
    "ase+va;std::copy_n(b.begin()+(va-v)/4,4,w.begin());return true;}return false"
    ";}\n"
)
pre += (
    fun(src, "bool folder_layout_anchors(")
    + "\n"
    + fun(src, "bool bind_folder_layout()")
    + "\n"
)
# Test the actual callbacks, not a separately reimplemented width/alignment formula.
a = src.index("static thread_local double folder_layout_gap")
b = src.index('extern "C" uint64_t hc_title_custom_label(', a)
pre += src[a:b]
cs = (ROOT / "app/src/main/cpp/targets/home/home_layout_config.cpp").read_text(
    encoding="utf8"
)
a = cs.index("constexpr char kCacheMagic")
b = cs.index(
    (
        "bool write_config_cache("
        if "bool write_config_cache(" in cs
        else "void write_config_cache("
    ),
    a,
)
pre += "namespace home_layout {\n" + cs[a:b] + "\n}\n"
pre += 'int checks=0,failed=0;void ok(bool v,const char*n){++checks;if(!v){++failed;std::cout<<"FAIL "<<n<<"\\n";}}\nint main(){\n'
for n in names:
    v, z = s.by_name[n]
    span = vas[bisect.bisect_right(vas, v)] - v
    words = struct.unpack("<" + "I" * (span // 4), e.read(v, span))
    pre += (
        f'symbols["{n}"]={{{v},{z}}};images[{v}]={{'
        + ",".join(hex(w) for w in words)
        + "};\n"
    )
registry = (ROOT / "app/src/main/cpp/targets/home/tweaks/symtab.cpp").read_text(
    encoding="utf8"
)
pairs = set(re.findall(r'\{\s*"([^"\n]+)"\s*,\s*"([^"\n]+)"', registry))
registered = all((n, n) in pairs for n in names)
pre += (
    "ok("
    + ("true" if registered else "false")
    + ',"required semantic roots registered in production kTargets");\n'
)
pre += (
    "\n"
    "using namespace home_layout;\n"
    'ok(bind_folder_layout(),"actual 7722 complete bank admitted");\n'
    "ok(g_folder_cell_width_field==15&&g_folder_gap_field==67&&g_folder_screen_wi"
    "dth_field==11&&g_folder_screen_height_field==19&&g_folder_cling_width_field="
    '=175,"owning width/spacing fields decoded");\n'
    'ok(g_folder_controller_config_field==43&&g_folder_rx_value_field==19,"contro'
    'ller and Rx payload not confused with GridConfig");\n'
    'ok(g_folder_center_pool==0x5eb0,"TextAlign center independently decoded");\n'
    'ok(g_folder_inner_ready,"inner Container plan admitted");\n'
    'ok(g_slots[7].address==data.load_base+g_folder_inner.window,"slot7 targets t'
    'he derived inner-Container replay window");\n'
    "ok(g_slots[7].original_words[0]==0xf85e83a0&&g_slots[7].original_words[2]==0"
    'xf81f83a3,"alignment replay preserves the original Container handoff");\n'
    "ok(g_folder_inner.window==0x146fbcc&&g_folder_inner.frame==0x50&&g_folder_in"
    'ner.owner_slot==0x20,"window/frame/owner derived from the closure prologue")'
    ";\n"
    "ok(g_folder_inner.alignment==0x0f&&g_folder_inner.padding==0x13&&g_folder_in"
    'ner.inset==0x7,"Container field offsets derived, not assumed");\n'
    "ok(g_folder_inner.center_pool==0x8180&&g_folder_inner.direction_pool[0]==0x7"
    '0288&&g_folder_inner.direction_pool[1]==0x71048,"center and both direction r'
    'oots derived from distinct code paths");\n'
    'ok(g_folder_inner.direction_bit==4,"the selecting bit derived from the TBNZ '
    'diamond");\n'
    'ok(g_folder_inner_owner_local==0x50,"owner local reachable from the saved x1'
    '5 with no assembly change");\n'
    "ok(g_folder_inner_owner_local==32u+g_folder_inner.frame-g_folder_inner.owner"
    '_slot,"folded formula agrees with the prologue walk");\n'
    'for(auto &slot:g_slots)ok(slot.address&&slot.original,"eight replay windows '
    'bound");\n'
    "auto old=images;\n"
    "// A real editor branch enters the former patch at +4. Cover B/BL and all\n"
    "// immediate conditional families; refuse a bank with ANY interior entry.\n"
    "{\n"
    ' const auto bt=symbols["FolderHeaderWidget._buildText"].first;\n'
    " auto &w=images[bt];const auto pc=bt+uint32_t(w.size()*4);\n"
    " const auto target=g_folder_inner.window+4;\n"
    " const int32_t words=int32_t(int64_t(target)-pc)/4;\n"
    " const uint32_t ops[]={0x14000000u|(uint32_t(words)&0x3ffffff),\n"
    "     0x94000000u|(uint32_t(words)&0x3ffffff),\n"
    "     0x54000000u|((uint32_t(words)&0x7ffff)<<5),\n"
    "     0xb4000000u|((uint32_t(words)&0x7ffff)<<5),\n"
    "     0x36000000u|((uint32_t(words)&0x3fff)<<5)};\n"
    " for(auto op:ops){\n"
    "     images[bt].push_back(op);g_folder_layout_bound=g_folder_layout_checked="
    "false;\n"
    '     ok(!bind_folder_layout(),"interior control-flow entry refuses the whole'
    ' bank");images=old;\n'
    " }\n"
    " g_folder_layout_bound=g_folder_layout_checked=false;\n"
    ' ok(bind_folder_layout(),"original common join readmitted after branch injec'
    'tion");\n'
    "}\n"
    "\n"
    "// Relocation, done as a BASE move rather than an instruction edit. Every sy"
    "mbol keeps\n"
    "// byte-identical instructions and simply starts 16 bytes higher, which is w"
    "hat a\n"
    "// rebuilt launcher actually looks like to the scanners. The earlier version"
    " of this\n"
    "// test spliced NOPs into the middle of each body, but that leaves bl_target"
    "()'s\n"
    "// `va + i*4` program counter 16 bytes below the instruction it is really de"
    "coding, so\n"
    "// every cross-function xref resolved to the wrong callee and the test faile"
    "d for a\n"
    "// reason that had nothing to do with offset derivation. Moving the base als"
    "o tests\n"
    "// the stronger claim: nothing may be anchored to an absolute module address"
    ".\n"
    "{\n"
    "constexpr uint32_t kRelocated=0x10;\n"
    "std::map<uint32_t,std::vector<uint32_t>> moved;\n"
    "for(auto&[va,b]:old)moved[va+kRelocated]=b;\n"
    "for(auto&[n,s]:symbols)s.first+=kRelocated;\n"
    "images=moved;\n"
    "g_folder_layout_bound=false;g_folder_layout_checked=false;\n"
    'ok(bind_folder_layout(),"relocated code resolves without old offsets");\n'
    'ok(g_folder_inner.window==0x146fbcc+kRelocated,"the replay window followed t'
    'he base, it was not memorised");\n'
    'ok(g_folder_inner_owner_local==0x50,"the frame arithmetic is base-independen'
    't");\n'
    "// Put everything back exactly as it was: the fault-injection cases below ad"
    "dress\n"
    "// symbols by the original VAs, so a half-restored map would silently test n"
    "othing.\n"
    "for(auto&[n,s]:symbols)s.first-=kRelocated;\n"
    "images=old;\n"
    "g_folder_layout_bound=false;g_folder_layout_checked=false;\n"
    'ok(bind_folder_layout(),"the original base is restored exactly");\n'
    "}\n"
    "// Include the actual production leaf/prologue filter, not just a synthetic "
    "symbol map.\n"
    'auto leafva=symbols["AndroidAttributeUtils.convertTextAlignment"].first;\n'
    'auto leafsize=symbols["AndroidAttributeUtils.convertTextAlignment"].second;\n'
    'ok(production_accept("AndroidAttributeUtils.convertTextAlignment",leafva,lea'
    'fsize),"production resolver admits actual read-only leaf ABI");\n'
    'ok(!production_accept("Unrelated.leaf",leafva,leafsize),"no arbitrary leaf a'
    'dmission");\n'
    'ok(!production_accept("AndroidAttributeUtils.convertTextAlignment",leafva,8)'
    ',"short leaf rejected before third instruction");\n'
    'for(size_t k=0;k<3;++k){images[leafva][k]^=1;ok(!production_accept("AndroidA'
    'ttributeUtils.convertTextAlignment",leafva,leafsize),"foreign leaf dispatch '
    'opcode rejected");images=old;}\n'
    "// An independent named converter must identify the same TextAlign.center ro"
    "ot.\n"
    'uint32_t converter=symbols["AndroidAttributeUtils.convertTextAlignment"].fir'
    "st;\n"
    "auto &cb=images[converter];\n"
    "size_t center_load=0;\n"
    "for(size_t j=0;j+3<cb.size();++j)if(cb[j]==0xf100107f&&cb[j+2]==0xf96f5b60)c"
    "enter_load=j+2;\n"
    'ok(center_load>0,"independent center branch found");\n'
    "cb[center_load]+=0x400; // Change only its pool displacement.\n"
    "g_folder_layout_bound=g_folder_layout_checked=false;\n"
    'ok(!bind_folder_layout(),"disagreeing converter center declines whole bank")'
    ";images=old;\n"
    'uint32_t resolver=symbols["_FlutterTextViewState._resolveEffectiveTextAlign"'
    "].first;\n"
    "auto &rb=images[resolver];\n"
    "for(size_t j=0;j+3<rb.size();++j)if(rb[j]==0x7100043f)rb[j]=0x7100143f;\n"
    "g_folder_layout_bound=g_folder_layout_checked=false;\n"
    'ok(!bind_folder_layout(),"RIGHT-only branch never admitted as center");image'
    "s=old;\n"
    "// Change both owning center pool loads: the current symbol is followed, not"
    " a fixed offset.\n"
    "for(auto v:{resolver,converter}){\n"
    " auto &body=images[v];\n"
    " for(size_t j=0;j+3<body.size();++j)\n"
    "  if(body[j]==(v==resolver?0x7100043fu:0xf100107fu))body[j+2]+=0x800;\n"
    "}\n"
    "g_folder_layout_bound=g_folder_layout_checked=false;\n"
    'ok(bind_folder_layout()&&g_folder_center_pool==0x5ec0,"center pool displacem'
    'ent relocates with both semantic branches");images=old;\n'
    "// Admission must also reject duplicate semantic branches and a foreign comm"
    "on join.\n"
    "images[converter].insert(images[converter].end(),old[converter].begin(),old["
    "converter].end());\n"
    "g_folder_layout_bound=g_folder_layout_checked=false;\n"
    'ok(!bind_folder_layout(),"duplicate converter center branch rejects ambiguit'
    'y");images=old;\n'
    "for(size_t j=0;j+3<images[resolver].size();++j)if(images[resolver][j]==0x710"
    "0043f){images[resolver][j+3]=0x14000001;break;}\n"
    "g_folder_layout_bound=g_folder_layout_checked=false;\n"
    'ok(!bind_folder_layout(),"foreign gravity join does not resolve center");ima'
    "ges=old;\n"
    "for(size_t j=0;j+3<images[converter].size();++j)if(images[converter][j]==0xf"
    "100107f){images[converter][j+1]^=1;break;}\n"
    "g_folder_layout_bound=g_folder_layout_checked=false;\n"
    'ok(!bind_folder_layout(),"inverted converter selection rejected");images=old'
    ";\n"
    'uint32_t rp=0;ok(folder_center_pool(images[resolver],rp)&&rp==0x5eb0,"gravit'
    'y1 selects center rather than gravity5");\n'
    "g_folder_layout_bound=g_folder_layout_checked=false;ok(bind_folder_layout(),"
    '"original semantic root restored");\n'
    'auto va=symbols["FolderGridViewGetxController.folderGridOuterHorizontalPaddi'
    'ng"].first;\n'
    "auto original=images[va];images[va].insert(images[va].end(),original.begin()"
    "+0x90/4,original.begin()+0xa0/4);\n"
    "g_folder_layout_bound=false;g_folder_layout_checked=false;ok(!bind_folder_la"
    'yout(),"ambiguous return store rejected atomically");images=old;\n'
    'va=symbols["FolderGridViewGetxController.folderCellWidth"].first;\n'
    "images[va][0x58/4]^=1;g_folder_layout_bound=false;g_folder_layout_checked=fa"
    'lse;ok(!bind_folder_layout(),"foreign currentConfig producer rejected");imag'
    "es=old;\n"
    'va=symbols["FolderGridViewGetxController.folderGridPaddingLeft"].first;\n'
    "images[va][0xac/4]^=1;g_folder_layout_bound=false;g_folder_layout_checked=fa"
    'lse;ok(!bind_folder_layout(),"GC rejoin into wrong instruction rejected");im'
    "ages=old;\n"
    'va=symbols["RxObjectMixin.value"].first;\n'
    "images[va][0x40/4]^=1;g_folder_layout_bound=false;g_folder_layout_checked=fa"
    'lse;ok(!bind_folder_layout(),"RX payload change rejected");images=old;\n'
    "g_folder_layout_bound=false;g_folder_layout_checked=false;ok(bind_folder_lay"
    'out(),"bank restored after fault injection");\n'
    "FolderLayoutConfig f{1,1,1,20,120,60,0};auto packed=pack_folder_layout(f,4);"
    "\n"
    'ok(unpack_folder_layout(packed)==f,"one atomic snapshot roundtrip");\n'
    'ok(std::abs(folder_cell_width(90,400,900,4,packed)-87)<1e-9,"phone side padd'
    'ing and four columns");\n'
    "f.padding_enabled=0;ok(std::abs(folder_cell_width(90,400,900,4,pack_folder_l"
    'ayout(f,4))-97)<1e-9,"width gate independent of padding");\n'
    "f.full_width=0;ok(folder_cell_width(90,400,900,4,pack_folder_layout(f,4))==9"
    '0,"switch off exact original width");\n'
    "f={0,1,1,20,120,60,1};\n"
    "ok(std::abs(folder_cell_width(90,1000,700,4,pack_folder_layout(f,4))-187)<1e"
    '-9,"tablet landscape uses h slider");\n'
    "ok(std::abs(folder_cell_width(90,700,1000,4,pack_folder_layout(f,4))-142)<1e"
    '-9,"tablet portrait uses v slider");\n'
    "f.landscape_padding=450;ok(folder_cell_width(90,700,600,4,pack_folder_layout"
    '(f,6))>=24,"extreme padding retains positive cells");\n'
    'f.phone_padding=51;ok(!valid_folder_layout(f)&&!pack_folder_layout(f,4),"out'
    ' of range values refused");\n'
    "f={1,1,1,20,120,60,0};std::vector<int32_t> packet={kFolderLayoutMagic,1,1,1,"
    "20,120,60,0};size_t at=0;FolderLayoutConfig output;\n"
    "auto read=[&](int32_t&n){if(at>=packet.size())return false;n=packet[at++];re"
    "turn true;};\n"
    'ok(read_folder_layout(read,output)&&output==f,"Binder extension roundtrip");'
    "\n"
    "for(size_t size=1;size<8;++size){packet.resize(size);at=0;output=f;ok(!read_"
    'folder_layout(read,output)&&output==f,"partial extension never overwrites sn'
    'apshot");}\n'
    "packet.clear();at=0;output=f;ok(read_folder_layout(read,output)&&output==Fol"
    'derLayoutConfig{},"legacy endpoint uses stock defaults");\n'
    "Config config;config.cell_x=4;config.cell_y=6;config.folder=f;config.widget_"
    "allow_move=true;\n"
    "std::vector<uint8_t> cache;serialize_config(config,cache);Config restored;\n"
    "ok(parse_config(cache,restored)&&restored.folder==f&&restored.widget_allow_m"
    'ove,"version10 cache roundtrip");\n'
    "auto legacy=cache;legacy.resize(legacy.size()-52);legacy[4]=9;restored.folde"
    "r=f;\n"
    "ok(parse_config(legacy,restored)&&restored.folder==FolderLayoutConfig{}&&res"
    'tored.widget_allow_move,"version9 cache compatibility preserves existing wid'
    'get setting");\n'
    'cache.pop_back();ok(!parse_config(cache,restored),"truncated v10 rejected");'
    "\n"
    "alignas(8) unsigned char buffer[2048]{};uintptr_t saved=(uintptr_t)buffer, c"
    "ontroller=(uintptr_t)buffer+800+1, root=(uintptr_t)buffer+1000+1, child=(uin"
    "tptr_t)buffer+1200+1;\n"
    "auto set64=[&](uintptr_t addr,uint64_t v){std::memcpy((void*)addr,&v,8);};\n"
    "auto setd=[&](uintptr_t addr,double v){std::memcpy((void*)addr,&v,8);};\n"
    "auto getd=[&](uintptr_t addr){double v=0;std::memcpy(&v,(void*)addr,8);retur"
    "n v;};\n"
    "hc_folder_layout_requested=pack_folder_layout(f,4);\n"
    "set64(saved+8,controller);setd(controller+g_folder_gap_field,4);hc_folder_la"
    "yout_body(saved,0,0,0);\n"
    "set64(saved,root);set64(saved+8,child);setd(root+g_folder_screen_width_field"
    ",400);setd(root+g_folder_screen_height_field,900);setd(child+g_folder_cell_w"
    "idth_field,90);\n"
    'hc_folder_layout_body(saved,0,1,0);ok(getd(saved+160)==87,"production callba'
    'ck computes fresh cell size");\n'
    'hc_folder_layout_body(saved,0,1,0);ok(getd(saved+160)==87,"repeat does not c'
    'ompound original config");\n'
    "ok(getd(child+g_folder_cell_width_field)==90&&getd(root+g_folder_screen_widt"
    'h_field)==400,"shared GridConfig never modified");\n'
    "setd(saved+160,12);hc_folder_layout_body(saved,0,2,0);ok(getd(saved+160)==0,"
    '"no extra outer padding on wide grid");\n'
    "uint64_t heap=controller&~uint64_t(0xffffffff);uintptr_t rx=(uintptr_t)buffe"
    "r+1400+1;\n"
    "uint32_t crx=uint32_t(rx),croot=uint32_t(root);std::memcpy((void*)(controlle"
    "r+g_folder_controller_config_field),&crx,4);std::memcpy((void*)(rx+g_folder_"
    "rx_value_field),&croot,4);\n"
    "set64(saved,controller);setd(controller+g_folder_cling_width_field,300);hc_f"
    'older_layout_body(saved,0,6,heap);ok(getd(saved+160)==400,"tablet popup expa'
    'nds through original controller RX chain");\n'
    "hc_folder_layout_requested=0;set64(saved,root);set64(saved+8,child);hc_folde"
    'r_layout_body(saved,0,1,0);ok(getd(saved+160)==90,"production callback switc'
    'h off original scalar");\n'
    "hc_folder_layout_requested=pack_folder_layout(f,4);\n"
    "uintptr_t start=(uintptr_t)buffer+1504+1,center=(uintptr_t)buffer+1600+1;\n"
    "std::vector<uint64_t> pool((0x67580+8)/8+1);\n"
    "set64(start-1,uint64_t(1234)<<12);set64(center-1,uint64_t(1234)<<12);set64(s"
    "tart+7,4);set64(center+7,2);\n"
    "pool[g_folder_center_pool/8]=center;set64(saved+8,start);hc_folder_layout_bo"
    "dy(saved,(uintptr_t)pool.data(),4,0);\n"
    'ok(*(uint64_t*)(saved+8)==center,"Text uses original center enum");\n'
    "set64(saved+8,start);hc_folder_layout_body(saved,(uintptr_t)pool.data(),5,0)"
    ";\n"
    'ok(*(uint64_t*)(saved+8)==center,"rename TextField uses same alignment");\n'
    "// Slot 7 now rewrites the freshly built Container's alignment field in plac"
    "e, reached\n"
    "// through the POST-dart_save x15 in the native save block. The owner must s"
    "it above\n"
    "// 4 GiB or `base + compressed` degenerates to base == 0 and proves nothing."
    "\n"
    "void *const high=[]()->void * {\n"
    "#ifdef _WIN32\n"
    "  return VirtualAlloc((void *)0x1'0000'0000ull, 0x1000, MEM_RESERVE | MEM_CO"
    "MMIT, PAGE_READWRITE);\n"
    "#else\n"
    "  return mmap((void *)0x1'0000'0000ull, 0x1000, PROT_READ | PROT_WRITE,\n"
    "      MAP_PRIVATE | MAP_ANONYMOUS | MAP_FIXED_NOREPLACE, -1, 0);\n"
    "#endif\n"
    "}();\n"
    "if (!high || (uintptr_t)high < 0x1'0000'0000ull) { std::cout << \"FAIL cannot"
    ' map a page above 4 GiB\\n"; return 1; }\n'
    "const uintptr_t x15_saved=saved+0x40;\n"
    "const uintptr_t owner_real=((uintptr_t)high+8)|uintptr_t(1);\n"
    "const uintptr_t inner_heap=owner_real&~uintptr_t(0xffffffff);\n"
    'ok(inner_heap!=0&&(owner_real&7)==1,"the fake Container has a real compresse'
    'd-pointer shape");\n'
    "set64(saved+128,x15_saved);set64(saved+24,owner_real);\n"
    "set64(x15_saved+g_folder_inner_owner_local,owner_real-inner_heap);\n"
    "const uint32_t ctr_pool=0x40|1, ctr_lo=0x50|1, ctr_hi=0x60|1;\n"
    "auto set32=[&](uintptr_t a,uint32_t v){std::memcpy((void*)a,&v,4);};\n"
    "auto get32=[&](uintptr_t a){uint32_t v=0;std::memcpy(&v,(void*)a,4);return v"
    ";};\n"
    "auto get64=[&](uintptr_t a){uint64_t v=0;std::memcpy(&v,(void*)a,8);return v"
    ";};\n"
    "uint32_t pool_span=g_folder_inner.center_pool;\n"
    "if(g_folder_inner.direction_pool[0]>pool_span)pool_span=g_folder_inner.direc"
    "tion_pool[0];\n"
    "if(g_folder_inner.direction_pool[1]>pool_span)pool_span=g_folder_inner.direc"
    "tion_pool[1];\n"
    "std::vector<uint64_t> ip7(pool_span/8+2);\n"
    "ip7[g_folder_inner.center_pool/8]=ctr_pool;\n"
    "ip7[g_folder_inner.direction_pool[0]/8]=ctr_hi;\n"
    "ip7[g_folder_inner.direction_pool[1]/8]=ctr_lo;\n"
    "set64(saved+8,0);\n"
    "set32(owner_real+g_folder_inner.alignment,ctr_hi);\n"
    "hc_folder_layout_body(saved,(uintptr_t)ip7.data(),7,inner_heap);\n"
    'ok(get32(owner_real+g_folder_inner.alignment)==ctr_pool,"direction alignment'
    ' rewritten to the center root");\n'
    "// At the common join the editor's selected child is NOT the Container local"
    ".\n"
    "set32(owner_real+g_folder_inner.alignment,ctr_hi);set64(saved+24,owner_real+"
    "8);\n"
    "hc_folder_layout_body(saved,(uintptr_t)ip7.data(),7,inner_heap);\n"
    'ok(get32(owner_real+g_folder_inner.alignment)==ctr_hi,"editor child mismatch'
    ' preserves all Container fields");\n'
    "set64(saved+24,owner_real);set32(owner_real+g_folder_inner.alignment,ctr_poo"
    "l);\n"
    'ok(get64(saved+8)==0,"slot 7 never forges the returned pointer any more");\n'
    "set32(owner_real+g_folder_inner.alignment,ctr_lo);\n"
    "hc_folder_layout_body(saved,(uintptr_t)ip7.data(),7,inner_heap);\n"
    'ok(get32(owner_real+g_folder_inner.alignment)==ctr_pool,"the other direction'
    ' root is rewritten too");\n'
    "set32(owner_real+g_folder_inner.alignment,0);\n"
    "hc_folder_layout_body(saved,(uintptr_t)ip7.data(),7,inner_heap);\n"
    'ok(get32(owner_real+g_folder_inner.alignment)==ctr_pool,"a null alignment is'
    ' centred too");\n'
    "set32(owner_real+g_folder_inner.alignment,ctr_pool);\n"
    "hc_folder_layout_body(saved,(uintptr_t)ip7.data(),7,inner_heap);\n"
    'ok(get32(owner_real+g_folder_inner.alignment)==ctr_pool,"already-centred hea'
    'der is left alone");\n'
    "set32(owner_real+g_folder_inner.alignment,0x7777);\n"
    "hc_folder_layout_body(saved,(uintptr_t)ip7.data(),7,inner_heap);\n"
    'ok(get32(owner_real+g_folder_inner.alignment)==0x7777,"a foreign alignment i'
    's never rewritten");\n'
    "set32(owner_real+g_folder_inner.alignment,ctr_hi);set64(saved+128,0);\n"
    "hc_folder_layout_body(saved,(uintptr_t)ip7.data(),7,inner_heap);\n"
    'ok(get32(owner_real+g_folder_inner.alignment)==ctr_hi,"a missing saved x15 r'
    'efuses the write instead of faulting");\n'
    "set64(saved+128,x15_saved);set64(saved+24,owner_real);\n"
    "hc_folder_layout_requested=0;set32(owner_real+g_folder_inner.alignment,ctr_h"
    "i);\n"
    "hc_folder_layout_body(saved,(uintptr_t)ip7.data(),7,inner_heap);\n"
    'ok(get32(owner_real+g_folder_inner.alignment)==ctr_hi,"disabled centring is '
    'an exact no-op");\n'
    "hc_folder_layout_requested=pack_folder_layout(f,4);\n"
    "set64(saved+8,start);\n"
    'ok(*(uint64_t*)(start+7)==4,"pooled original TextAlign enums are immutable")'
    ";\n"
    "set64(center+7,3);set64(saved+8,start);hc_folder_layout_body(saved,(uintptr_"
    "t)pool.data(),4,0);\n"
    'ok(*(uint64_t*)(saved+8)==start,"wrong enum index retains stock text");\n'
    "set64(center+7,2);set64(center-1,uint64_t(4321)<<12);hc_folder_layout_body(s"
    "aved,(uintptr_t)pool.data(),4,0);\n"
    'ok(*(uint64_t*)(saved+8)==start,"wrong enum class retained");\n'
    "hc_folder_layout_requested=0;hc_folder_layout_body(saved,(uintptr_t)pool.dat"
    'a(),4,0);ok(*(uint64_t*)(saved+8)==start,"title default exact original");\n'
    "g_folder_layout_bound=g_folder_layout_checked=false;ok(!bind_folder_layout()"
    '&&!g_folder_layout_checked,"disabled folder features never scan APK");\n'
    'std::cout<<"FOLDER_NATIVE="<<checks<<" checks; failed="<<failed<<"\\n";return'
    " failed?1:0;}\n"
)
out = D / ("run-" + ROOT.name)
out.mkdir(exist_ok=True)
(out / "test.cpp").write_text(pre, encoding="utf8")
zig = W / "tests/dynamic-address-audit/runtime/zig-windows-x86_64-0.13.0/zig.exe"
# Local compiler/JVM or fixture binary with separate, harness-owned arguments.
r = subprocess.run(  # nosec B603
    [
        str(zig),
        "c++",
        "-std=c++20",
        "-O0",
        "-I" + str(ROOT / "app/src/main/cpp/targets/home"),
        "-I" + str(ROOT / "app/src/main/cpp"),
        str(out / "test.cpp"),
        "-o",
        str(out / "test.exe"),
    ],
    capture_output=True,
    text=True,
    encoding="utf8",
)
print(r.stdout + r.stderr, end="")
if r.returncode:
    sys.exit(r.returncode)
# Local compiler/JVM or fixture binary with separate, harness-owned arguments.
r = subprocess.run(  # nosec B603
    [str(out / "test.exe")], capture_output=True, text=True, encoding="utf8"
)
print(r.stdout + r.stderr, end="")
sys.exit(r.returncode)
