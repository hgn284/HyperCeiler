import bisect
import struct
# Subprocess is needed for the reviewed argv-only fixture/tool calls below.
import subprocess  # nosec B404
import sys
from pathlib import Path

D = Path(__file__).resolve().parent
W = D.parents[1]
R = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else W
src = (R / "app/src/main/cpp/targets/home/home_layout_hooks.cpp").read_text(
    encoding="utf8"
)
if "bool bind_grid_autofit()" not in src:
    print(
        "AUTOFIT=absent; stock fixed-row height capped by width; NEW_FEATURE_TEST=FAIL"
    )
    sys.exit(1)
sys.path.insert(0, str(W / "tests/home-layout-native"))
from dart_dump import Elf, Symbols

A = Path(
    "C:/Users/XiaoYe/.codex/visualizations/2026/09/29/01a0eb2b-4de7-7442-83d8-db3197b7610f"
)
elf = Elf(A / "launcher-7722-libapp.so")
mini = Elf(A / "launcher-7722-mini.elf")
symbols = Symbols(A / "launcher-7722-mini.elf")
sec = mini.sections[mini.section_names[".symtab"]]
vas = sorted(
    set(
        v
        for _, info, _, _, v, _ in (
            struct.unpack_from("<IBBHQQ", mini.data, a)
            for a in range(sec[4], sec[4] + sec[5], 24)
        )
        if info & 15 == 2 and v
    )
)


def fun(name):
    a = src.index(name)
    a = src.rfind("\n", 0, a) + 1
    j = src.index("{", a) + 1
    depth = 1
    while depth:
        depth += (src[j] == "{") - (src[j] == "}")
        j += 1
    return src[a:j]


c = (
    "\n"
    "#include <vector>\n"
    "#include <map>\n"
    "#include <string>\n"
    "#include <array>\n"
    "#include <iostream>\n"
    "#include <cstring>\n"
    '#include "home_grid_autofit.h"\n'
    "std::map<uint32_t,std::vector<uint32_t>> images;\n"
    "std::map<std::string,std::pair<uint32_t,uint32_t>> symbols;\n"
    "namespace hometweaks {bool HomeTweaksFindSymbol(const char*n,uint32_t*v,uint"
    "32_t*z){if(!symbols.count(n))return false;auto p=symbols[n];*v=p.first;*z=p."
    "second;return true;}}\n"
    "namespace dartscan {bool body(uint32_t v,std::vector<uint32_t>&b){if(!images"
    ".count(v))return false;b=images[v];return true;}}\n"
    "struct Dart { uintptr_t load_base=0x100000000; } data;Dart*g_dart=&data;\n"
    "struct Slot {uintptr_t address=0;void*replacement=nullptr;void**original=nul"
    "lptr;int source=0;std::array<uint32_t,4>original_words{};bool registered=fal"
    "se;};\n"
    "Slot g_slots[2];constexpr int kGridAutofitSlotBase=0;constexpr uint32_t kDar"
    "tPrologue=0xa9bf79fd;\n"
    "bool g_grid_autofit_bound=false,g_grid_autofit_checked=false;home_layout::Gr"
    "idAutofitSites g_grid_autofit_fields;\n"
    "void*hc_grid_autofit_original[2]{};uintptr_t hc_grid_autofit_resume[2]{};uin"
    "t32_t hc_grid_autofit_requested=1|(6<<8);\n"
    "void hc_grid_autofit_0_entry(){}void hc_grid_autofit_1_entry(){}\n"
    "bool bind_dart_target(uint32_t va,uintptr_t&a,int&,std::array<uint32_t,4>&w)"
    "{for(const auto&[base,b]:images){if(va>=base&&va+16<=base+b.size()*4){a=data"
    ".load_base+va;for(int i=0;i<4;i++)w[i]=b[(va-base)/4+i];return true;}}return"
    " false;}\n"
    'constexpr int ANDROID_LOG_INFO=4;const char*kTag="test";int __android_log_pr'
    "int(int,const char*,const char*,...){return 0;}\n"
)
c += (
    fun("bool bind_grid_autofit()") + "\n" + fun('extern "C" int hc_grid_autofit_body(')
)
c += r"""
int checks=0,failed=0;void ok(bool b,const char*m){++checks;if(!b){++failed;std::cout<<"FAIL "<<m<<"\n";}}
template<class T>void put(uintptr_t p,T v){std::memcpy((void*)p,&v,sizeof(v));}
template<class T>T get(uintptr_t p){T v;std::memcpy(&v,(void*)p,sizeof(v));return v;}
bool near(double a,double b){return std::abs(a-b)<1e-8;}
void reset(){g_grid_autofit_bound=g_grid_autofit_checked=false;for(auto&s:g_slots)s={};}
int main(){
"""
names = [
    "GridSizeCalRules._calVariableHeight",
    "GridSizeCalRules.calVarCellHeight",
    "PhoneCellSizeHandler.calVariableValues",
]
for n in names:
    va, _ = symbols.by_name[n]
    size = vas[bisect.bisect_right(vas, va)] - va
    words = struct.unpack("<" + "I" * (size // 4), elf.read(va, size))
    c += (
        f'symbols["{n}"]={{{va},{size}}};images[{va}]={{'
        + ",".join(hex(w) for w in words)
        + "};\n"
    )
c += (
    "\n"
    "const auto original_images=images;\n"
    'const uint32_t a=symbols["GridSizeCalRules._calVariableHeight"].first,b=symb'
    'ols["PhoneCellSizeHandler.calVariableValues"].first,cap=symbols["GridSizeCal'
    'Rules.calVarCellHeight"].first;\n'
    "home_layout::GridAutofitSites f;\n"
    'ok(home_layout::grid_autofit_sites(images[a],images[cap],images[b],f),"real '
    '7722 final owning windows admitted");\n'
    'ok(f.legacy==0x90&&f.handler==0x248,"sites derived dynamically after origina'
    'l final caps");\n'
    "ok(f.legacy_height==0x4f&&f.legacy_dock==0x87&&f.width==0xb&&f.height==0x13&"
    '&f.dock==0x23&&f.rows==0x7b,"fields derive from independent cap and exporter'
    ' consumers");\n'
    'ok(bind_grid_autofit()&&g_grid_autofit_bound,"production bind admits both fi'
    'nal splices");\n'
    "for(int i=0;i<2;i++)ok(g_slots[i].address&&hc_grid_autofit_resume[i]==g_slot"
    's[i].address+16,"rejoin original unrelocated PC");\n'
    "images[a].insert(images[a].begin()+f.legacy/4-2,0xd503201f);images[b].insert"
    "(images[b].begin()+6,0xd503201f);reset();\n"
    "ok(bind_grid_autofit()&&g_grid_autofit_fields.legacy==f.legacy+4&&g_grid_aut"
    'ofit_fields.handler==f.handler+4,"inserted code shifts sites dynamically");\n'
    "images=original_images;auto duplicate=images[a];for(int i=-2;i<4;i++)images["
    "a].push_back(duplicate[f.legacy/4+i]);\n"
    'reset();ok(!bind_grid_autofit()&&!g_grid_autofit_bound,"duplicate owner wind'
    'ow rejected");\n'
    "images=original_images;images[b][f.handler/4+1]^=0x400;reset();ok(!bind_grid"
    '_autofit(),"different gap producer rejected");\n'
    "images=original_images;images[a][2]=0xd10181ef;reset();ok(!bind_grid_autofit"
    '(),"different frame ABI rejected");\n'
    "images=original_images;images[a][0x30/4]=0x94000000;reset();ok(!bind_grid_au"
    'tofit(),"foreign cap callee rejected");\n'
    "images=original_images;\n"
    "auto change_field=[](uint32_t w,int old,int n){return (w&~(511u<<12))|(uint3"
    "2_t(n)<<12);};\n"
    "for(auto&w:images[cap])if((w&0xffe00fffu)==0xfc000022u&&((w>>12)&511)==unsig"
    "ned(f.legacy_height))w=change_field(w,f.legacy_height,0x5f);\n"
    "for(auto&w:images[a])if((w&0xffe00fffu)==0xfc400020u&&((w>>12)&511)==unsigne"
    "d(f.legacy_height))w=change_field(w,f.legacy_height,0x5f);\n"
    'reset();ok(bind_grid_autofit()&&g_grid_autofit_fields.legacy_height==0x5f,"m'
    'oved height field is derived from both owning consumers");\n'
    "images=original_images;reset();hc_grid_autofit_requested=0;ok(!bind_grid_aut"
    'ofit()&&!g_grid_autofit_checked,"disabled feature performs no scan");\n'
    'hc_grid_autofit_requested=1|(6<<8);ok(bind_grid_autofit(),"re-enabled before'
    ' first admission");\n'
    "double h=123;\n"
    'ok(!home_layout::grid_autofit_height(60,100,60,6,7,h)&&h==123,"wrong-layout '
    'rows retain original");\n'
    'ok(!home_layout::grid_autofit_height(23,100,60,6,6,h)&&h==123,"too small wid'
    'th unchanged");\n'
    'ok(!home_layout::grid_autofit_height(60,-900,60,13,13,h)&&h==123,"invalid de'
    'nse cell unchanged");\n'
    'ok(!home_layout::grid_autofit_height(NAN,100,60,6,6,h)&&h==123,"nonfinite bo'
    'unds unchanged");\n'
    'ok(home_layout::grid_autofit_height(60,300,60,6,6,h)&&h==110,"previous cappe'
    'd layout fills usable area");\n'
    'ok(home_layout::grid_autofit_height(60,300,90,6,6,h)&&h==105,"original dock '
    'growth still reserved, not enlarged again");\n'
    "unsigned layouts=0;\n"
    "for(int cols=3;cols<=9;cols++)for(int rows=4;rows<=13;rows++)for(int availab"
    "le=360;available<=1600;available+=17){\n"
    " double width=std::min(328.0/cols,double(available)/(rows+1)),height,remaini"
    "ng=available-width*(rows+1);\n"
    " const double dock=width*1.15;\n"
    " if(!home_layout::grid_autofit_height(width,remaining,dock,rows,rows,height)"
    ")continue;\n"
    ' ok(near(height*rows+dock,available),"all rows fill area while preserving or'
    'iginal dock height");layouts++;\n'
    "}\n"
    "alignas(16) unsigned char buffer[4096]{};\n"
    "uintptr_t saved=(uintptr_t)buffer,fp=(uintptr_t)buffer+1024,owner=(uintptr_t"
    ")buffer+1536+1,box=(uintptr_t)buffer+2048+1;\n"
    "auto q=[&](int i){return saved+160+i*16;};\n"
    "put(fp-8,uint64_t(owner));put(saved,uint64_t(7));put(fp-0x30,90.0);put(fp-0x"
    "38,30.0);put(fp-0x28,300.0);\n"
    "put(owner+f.legacy_dock,90.0);put(owner+f.legacy_height,90.0);\n"
    'ok(hc_grid_autofit_body(saved,fp,0)==1,"production legacy common final splic'
    'e");\n'
    "ok(get<double>(owner+f.legacy_height)==105&&get<double>(owner+f.legacy_dock)"
    '==90,"height fits and stock dock unchanged");\n'
    'ok(get<double>(q(0))==300&&get<double>(q(1))==0&&get<double>(q(2))==300,"leg'
    'acy gap arithmetic replayed with zero leftover");\n'
    "put(saved,uint64_t(box));put(box+7,300.0);put(owner+f.rows,int64_t(6));put(o"
    "wner+f.width,60.0);put(owner+f.height,90.0);put(owner+f.dock,90.0);\n"
    'ok(hc_grid_autofit_body(saved,fp,1)==1,"production handler common final spli'
    'ce");\n'
    "ok(get<double>(owner+f.height)==105&&get<double>(owner+f.width)==60&&get<dou"
    'ble>(owner+f.dock)==90,"workspace-only vertical stride, width and dock untou'
    'ched");\n'
    'ok(get<double>(q(0))==300&&get<double>(q(1))==300&&get<double>(q(2))==0,"han'
    'dler gap arithmetic replayed with zero leftover");\n'
    'ok(get<double>(box+7)==300,"original boxed input immutable");\n'
    "unsigned char before[4096];std::memcpy(before,buffer,sizeof(buffer));hc_grid"
    "_autofit_requested=0;\n"
    "ok(hc_grid_autofit_body(saved,fp,1)==0&&std::memcmp(before,buffer,sizeof(buf"
    'fer))==0,"disabled splice exact no-op before original replay");\n'
    "hc_grid_autofit_requested=1|(7<<8);std::memcpy(before,buffer,sizeof(buffer))"
    ";\n"
    "ok(hc_grid_autofit_body(saved,fp,1)==0&&std::memcmp(before,buffer,sizeof(buf"
    'fer))==0,"other row configuration never written");\n'
    "hc_grid_autofit_requested=1|(6<<8);put(box+7,double(NAN));std::memcpy(before"
    ",buffer,sizeof(buffer));\n"
    "ok(hc_grid_autofit_body(saved,fp,1)==0&&std::memcmp(before,buffer,sizeof(buf"
    'fer))==0,"nonfinite input never writes heap or saved registers");\n'
    "put(box+7,300.0);\n"
    "for(int i=0;i<1000;i++){\n"
    ' ok(hc_grid_autofit_body(saved,fp,1)==1&&get<double>(owner+f.height)==105,"1'
    '000 recalculations do not compound");\n'
    "}\n"
    'std::cout<<"AUTOFIT_NATIVE="<<checks<<" checks; failed="<<failed<<"; layouts'
    '="<<layouts<<"\\n";return failed?1:0;}\n'
)
out = D / ("run-" + R.name)
out.mkdir(exist_ok=True)
(out / "test.cpp").write_text(c, encoding="utf8")
zig = W / "tests/dynamic-address-audit/runtime/zig-windows-x86_64-0.13.0/zig.exe"
# Local compiler/JVM or fixture binary with separate, harness-owned arguments.
p = subprocess.run(  # nosec B603
    [
        str(zig),
        "c++",
        "-std=c++20",
        "-O0",
        "-I" + str(R / "app/src/main/cpp/targets/home"),
        str(out / "test.cpp"),
        "-o",
        str(out / "test.exe"),
    ],
    capture_output=True,
    text=True,
    encoding="utf8",
)
print(p.stdout + p.stderr, end="")
if p.returncode:
    sys.exit(p.returncode)
# Local compiler/JVM or fixture binary with separate, harness-owned arguments.
p = subprocess.run(  # nosec B603
    [str(out / "test.exe")], capture_output=True, text=True, encoding="utf8"
)
print(p.stdout + p.stderr, end="")
sys.exit(p.returncode)
