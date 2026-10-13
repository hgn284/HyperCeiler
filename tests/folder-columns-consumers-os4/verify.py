import struct
# Subprocess is needed for the reviewed argv-only fixture/tool calls below.
import subprocess  # nosec B404
import sys
from pathlib import Path

W = Path.cwd()
R = Path(sys.argv[1]) if len(sys.argv) > 1 else W
D = W / "tests/folder-columns-consumers-os4"
D.mkdir(exist_ok=True)
S = (R / "app/src/main/cpp/targets/home/tweaks/ht_plan.cpp").read_text(encoding="utf8")
H = (R / "app/src/main/cpp/targets/home/tweaks/ht_plan.h").read_text(encoding="utf8")
legacy = "colsReadCount" not in H


def fun(key):
    a = S.index(key)
    b = S.index("{", a)
    n = 1
    j = b + 1
    while n:
        n += (S[j] == "{") - (S[j] == "}")
        j += 1
    return S[a:j]


sys.path.insert(0, str(W / "tests/home-layout-native"))
from dart_dump import Elf, Symbols

P = Path(
    "C:/Users/XiaoYe/.codex/visualizations/2026/09/29/01a0eb2b-4de7-7442-83d8-db3197b7610f"
)
e = Elf(P / "launcher-7722-libapp.so")
sy = Symbols(P / "launcher-7722-mini.elf")
va, size = sy.by_name["GridController.init"]
# executable ELF segments only; preserve actual VAs in the offline test image
segments = []
for i in range(struct.unpack_from("<H", e.data, 56)[0]):
    off = (
        struct.unpack_from("<Q", e.data, 32)[0]
        + i * struct.unpack_from("<H", e.data, 54)[0]
    )
    t, fl, fo, v, _, fs, ms, _ = struct.unpack_from("<IIQQQQQQ", e.data, off)
    if t == 1 and fl & 1:
        segments.append((v, fs, e.data[fo : fo + fs]))
pre = (
    """#include <vector>
#include <map>
#include <array>
#include <algorithm>
#include <cstring>
#include <cstdarg>
#include <cstdio>
#include <fstream>
#include <iostream>
#include "a64.h"
namespace hometweaks {
"""
    + H[
        H.index("constexpr uint32_t kMaxNoClearSites") : H.index(
            "uint32_t WantedFeatureMask"
        )
    ]
    + (
        "\n"
        "constexpr uint32_t kColsUnset=0,kFolderColsOrigSmi=8,kFolderColsOffset=0x263"
        "8,kFolderColsOfficial=4;\n"
        "struct Config{uint32_t folderCols=4;};\n"
        "struct Segment{uintptr_t begin,end;uint32_t flags;};struct Image{uintptr_t b"
        "ase=0;size_t segmentCount=0;Segment segments[8];};\n"
        "std::map<uint32_t,uint32_t> words;Image im;uint32_t initVa,initSize;\n"
        "struct CodeView{static constexpr size_t kReadChunkWords=16384;bool Executabl"
        "eRangesOk()const{return true;}const Image& image()const{return im;}\n"
        "bool Word(uint32_t va,uint32_t*out)const{auto p=words.find(va);if(p==words.e"
        "nd())return false;*out=p->second;return true;}\n"
        "bool ReadWords(uint32_t va,uint32_t*out,size_t n)const{for(size_t i=0;i<n;++"
        "i)if(!Word(va+i*4,out+i))return false;return true;}};\n"
        "struct SymbolIndex{static SymbolIndex& Instance(){static SymbolIndex s;retur"
        'n s;}bool Find(const char*n,uint32_t*v,uint32_t*z){if(strcmp(n,"GridControll'
        'er.init"))return false;*v=initVa;*z=initSize;return true;}};\n'
        "bool LocateFeature16Square(const CodeView&,LocatedSites*){return false;}\n"
    )
)
for key in [
    "void SetWhy(",
    "template <typename Fn>",
    "bool LocateFeature16(",
    "void Rollback(",
    "void DeriveFeature16(",
    "struct ByteWriter",
    "struct ByteReader",
]:
    pre += fun(key) + (";\n" if key.startswith("struct") else "\n")
if not legacy:
    pre += (
        (
            "constexpr uint32_t kPadGridMin=2,kPadGridMax=32,kPhoneRowsMax=32,kCellCountX"
            "Offset=19;\n"
            "bool ValidateFeature21Shape(const CodeView&, LocatedSites&){return true;}\n"
        )
        + fun("bool IsConditionalBranch(")
        + "\n"
        + fun("bool ValidateSitesImpl(")
        + "\n"
    )
pre += (
    "constexpr uint32_t kSitesPayloadVersion=10;\n"
    + fun("bool SerializeSites(")
    + "\n"
    + fun("bool ParseSites(")
    + "\n}\n"
)
main = (
    (
        "using namespace hometweaks;\n"
        "int main(int argc,char**argv){std::ifstream f(argv[1],std::ios::binary);uint"
        "32_t count;f.read((char*)&count,4);for(uint32_t i=0;i<count;++i){uint32_t v,"
        "n;f.read((char*)&v,4);f.read((char*)&n,4);im.segments[im.segmentCount++]={v,"
        "v+n,5};for(uint32_t j=0;j<n;j+=4){uint32_t w;f.read((char*)&w,4);words[v+j]="
        "w;}}initVa="
    )
    + str(va)
    + """;initSize="""
    + str(size)
    + (
        ";CodeView code;LocatedSites sites;int checks=0;auto ck=[&](bool b){++checks;"
        'if(!b){std::cerr<<"FAIL check "<<checks<<"\\n";exit(1);}};\n'
        "ck(LocateFeature16(code,&sites));ck(sites.colsReadCount>0);ck(ValidateSitesI"
        'mpl(code,sites));std::cout<<"DYNAMIC_READERS="<<sites.colsReadCount<<" OFFSE'
        'T="<<sites.colsOffset<<"\\n";\n'
        "auto baseline=words;for(uint32_t cols:{4u,5u,2u,16u}){Config cfg{cols};PlanR"
        "esult p;DeriveFeature16(code,cfg,sites,&p);ck(p.ok16);for(auto x:p.patches){"
        "ck(words[x.va]==x.expect);words[x.va]=x.patch;}for(uint32_t i=0;i<sites.cols"
        "ReadCount;++i){ck(a64::IsMovz(words[sites.colsReadVa[i]]));ck(a64::MovzImm(w"
        "ords[sites.colsReadVa[i]])==cols*2);}std::vector<uint8_t> bytes;ck(Serialize"
        "Sites(sites,&bytes));LocatedSites round;ck(ParseSites(bytes.data(),bytes.siz"
        "e(),&round));ck(round.colsReadCount==sites.colsReadCount);ck(round.colsReadW"
        "ord[0]==sites.colsReadWord[0]);ck(ValidateSitesImpl(code,round));round.colsR"
        "eadWord[0]^=1u<<10;ck(!ValidateSitesImpl(code,round));ck(words[sites.movzVa]"
        "==baseline[sites.movzVa]);ck(words[sites.gateVa]==baseline[sites.gateVa]);}\n"
        "words=baseline;Config unset{0};PlanResult disabled;DeriveFeature16(code,unse"
        "t,sites,&disabled);ck(disabled.patches.empty());\n"
        "words[sites.colsReadVa[0]]=0xd503201f;ck(!ValidateSitesImpl(code,sites));Con"
        "fig c{4};PlanResult bad;DeriveFeature16(code,c,sites,&bad);ck(!bad.ok16&&bad"
        ".patches.empty());words=baseline;\n"
        "// Change both the static-table offset and the columns offset; discover anew"
        ".\n"
        "uint32_t oldTable=sites.colsThreadLoad,oldCols=sites.colsOffset;\n"
        "for(auto&[v,w]:words){if((w&~31u)==oldTable)w+=1u<<10;if((w&0xffc00000u)==0x"
        "f9400000u&&((w>>10)&0xfff)*8==oldCols)w+=2u<<10;}\n"
        "words[sites.storeVa]+=2u<<10;LocatedSites relocated;ck(LocateFeature16(code,"
        "&relocated));ck(relocated.colsOffset==oldCols+16);ck(relocated.colsThreadLoa"
        "d==oldTable+(1u<<10));ck(relocated.colsReadCount==sites.colsReadCount);\n"
        'std::cout<<"FOLDER_CONSUMERS_CHECKS="<<checks<<" FAILED=0; late init correct'
        "ed; defaults unpatched; dynamic offsets; cache roundtrip; foreign word rejec"
        'ted\\n";}\n'
    )
)
if legacy:
    main = (
        main[: main.index("ck(LocateFeature16")]
        + r"""if(!LocateFeature16(code,&sites))return 2;
 auto original=words;Config c{4};PlanResult result;DeriveFeature16(code,c,sites,&result);
 for(auto patch:result.patches)words[patch.va]=patch.patch;
 unsigned unchanged=0;for(auto [v,w]:original){if((w&0xffc00000u)==0xf9400000u&&((w>>10)&0xfff)*8==sites.colsOffset&&words[v]==w)++unchanged;}
 std::cout<<"BASELINE_INITIALIZED=3 REQUESTED=4 UNCHANGED_READERS="<<unchanged<<"; FAIL late initialization persists\n";
 return unchanged?1:0;}
"""
    )
run = D / ("run-" + R.name)
run.mkdir(exist_ok=True)
(run / "test.cpp").write_text(pre + main, encoding="utf8")
fixture = run / "image.bin"
with fixture.open("wb") as f:
    f.write(struct.pack("<I", len(segments)))
    for v, n, b in segments:
        f.write(struct.pack("<II", v, n))
        f.write(b)
zig = W / "tests/dynamic-address-audit/runtime/zig-windows-x86_64-0.13.0/zig.exe"
# Local compiler/JVM or fixture binary with separate, harness-owned arguments.
subprocess.run(  # nosec B603
    [
        str(zig),
        "c++",
        "-std=c++20",
        "-I" + str(W / "app/src/main/cpp/targets/home/tweaks"),
        str(run / "test.cpp"),
        "-o",
        str(run / "test.exe"),
    ],
    check=True,
)
# Local compiler/JVM or fixture binary with separate, harness-owned arguments.
# nosemgrep: python_exec_rule-subprocess-call, python_exec_rule-subprocess-call-array
sys.exit(subprocess.run([str(run / "test.exe"), str(fixture)]).returncode)  # nosec B603
