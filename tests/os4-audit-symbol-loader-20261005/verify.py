import json
import struct
# Subprocess is needed for the reviewed argv-only fixture/tool calls below.
import subprocess  # nosec B404
import sys
from pathlib import Path


def _require(condition, message=None):
    """Keep fixture and rollback checks active when Python uses -O."""
    if not condition:
        if message is None:
            raise AssertionError
        raise AssertionError(message())


D = Path(__file__).resolve().parent
W = D.parents[1]
R = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else W
sys.path.insert(0, str(W / "tests/home-layout-native"))
from dart_dump import Elf

A = Path(
    "C:/Users/XiaoYe/.codex/visualizations/2026/09/29/01a0eb2b-4de7-7442-83d8-db3197b7610f"
)
outer = Elf(A / "launcher-7722-libapp.so")
mini = Elf(A / "launcher-7722-mini.elf")
S = (R / "app/src/main/cpp/targets/home/tweaks/symtab.cpp").read_text(encoding="utf8")
INCLUDE_DIR = (R / "app/src/main/cpp/targets/home/tweaks/image.cpp").read_text(
    encoding="utf8"
)


def fun(s, n):
    a = s.index(n)
    a = s.rfind("\n", 0, a) + 1
    j = s.index("{", a) + 1
    depth = 1
    while depth:
        depth += (s[j] == "{") - (s[j] == "}")
        j += 1
    return s[a:j]


run = D / ("run-" + R.name)
run.mkdir(exist_ok=True)
# Only XZ decompression is substituted: the ELF metadata parser, registry, code guard,
# selection loop and public index methods below are the actual production implementation.
code = "\n".join(line for line in S.splitlines() if not line.startswith("#include"))
code = code.replace('extern "C" {\n}', "")
dec = fun(code, "enum xz_ret RunDecoder(")
code = code.replace(
    dec,
    (
        "enum xz_ret RunDecoder(const std::vector<uint8_t>&,uint32_t,std::vector<uint"
        "8_t>*out,uint64_t=0){if(slowDecode){auto until=std::chrono::steady_clock::no"
        "w()+std::chrono::milliseconds(5);while(std::chrono::steady_clock::now()<unti"
        "l){}}*out=decoded;return XZ_STREAM_END;}"
    ),
)
header = "\n".join(
    line
    for line in (R / "app/src/main/cpp/targets/home/tweaks/symtab.h")
    .read_text()
    .splitlines()
    if not line.startswith("#include") and not line.startswith("#pragma")
)
pre = (
    "\n"
    "#define LOGI(...) ((void)0)\n"
    "#include <chrono>\n"
    "#include <array>\n"
    "#include <cstdint>\n"
    "#include <cstddef>\n"
    "#include <vector>\n"
    "#include <string>\n"
    "#include <cstring>\n"
    "#include <cstdlib>\n"
    "#include <cstdio>\n"
    "#include <cstdarg>\n"
    "#include <iostream>\n"
    "#include <fstream>\n"
    "#include <algorithm>\n"
    "#include <limits>\n"
    "#include <cerrno>\n"
    "#include <stdexcept>\n"
    "static bool blockLargeString=false;static int blocked=0;\n"
    "void* operator new(std::size_t n){if(blockLargeString&&n==2097153){blocked++"
    ";throw std::bad_alloc();}if(auto p=std::malloc(n))return p;throw std::bad_al"
    "loc();}\n"
    "void operator delete(void*p) noexcept{std::free(p);}\n"
    "void operator delete(void*p,std::size_t) noexcept{std::free(p);}\n"
    "struct Elf64_Ehdr{unsigned char e_ident[16];uint16_t e_type,e_machine;uint32"
    "_t e_version;uint64_t e_entry,e_phoff,e_shoff;uint32_t e_flags;uint16_t e_eh"
    "size,e_phentsize,e_phnum,e_shentsize,e_shnum,e_shstrndx;};\n"
    "struct Elf64_Shdr{uint32_t sh_name,sh_type;uint64_t sh_flags,sh_addr,sh_offs"
    "et,sh_size;uint32_t sh_link,sh_info;uint64_t sh_addralign,sh_entsize;};\n"
    "struct Elf64_Sym{uint32_t st_name;uint8_t st_info,st_other;uint16_t st_shndx"
    ";uint64_t st_value,st_size;};\n"
    "struct Elf64_Phdr{uint32_t p_type,p_flags;uint64_t p_offset,p_vaddr,p_paddr,"
    "p_filesz,p_memsz,p_align;};\n"
    "static_assert(sizeof(Elf64_Ehdr)==64&&sizeof(Elf64_Shdr)==64&&sizeof(Elf64_S"
    "ym)==24);\n"
    '#define ELFMAG "\\177ELF"\n'
    "constexpr int SELFMAG=4,EI_CLASS=4,ELFCLASS64=2,EI_DATA=5,ELFDATA2LSB=1,EI_V"
    "ERSION=6,EV_CURRENT=1,EM_AARCH64=183;\n"
    "constexpr int SHT_SYMTAB=2,SHT_STRTAB=3,SHN_UNDEF=0,STT_FUNC=2,SHF_EXECINSTR"
    "=4;\n"
    "#define ELF64_ST_TYPE(info) ((info)&15)\n"
    "#define LOGW(...) ((void)0)\n"
    "enum xz_ret{XZ_OK,XZ_STREAM_END,XZ_MEM_ERROR,XZ_UNSUPPORTED_CHECK};\n"
    "uint32_t xz_crc32(const unsigned char*,size_t,uint32_t){return 0;}void xz_cr"
    "c32_init(){}\n"
    "bool slowDecode=false;std::vector<uint8_t> outerFile,decoded,mapped;std::vec"
    "tor<std::pair<uintptr_t,size_t>> readable;unsigned fileReads=0;bool faultAll"
    "=false;uintptr_t faultAddress=0;\n"
    "namespace hometweaks{\n"
    "struct Segment{uintptr_t begin,end;uint32_t flags;};\n"
    "struct Image{uintptr_t base=0;char path[512]{};Segment segments[16]{};size_t"
    " segmentCount=0;uint64_t apkEntryOffset=0;bool fromApkEntry=false;uint64_t f"
    "ileViewBytes=0,sourceDevice=0,sourceInode=0;};\n"
    "uint64_t ImageIdentity(const Image&){return 123;}\n"
    "int saves=0;bool saveFault=false;std::vector<uint8_t> cached;bool cacheOn=fa"
    "lse;\n"
    "bool LoadSymbolCache(uint64_t,std::vector<uint8_t>*out){if(!cacheOn)return f"
    "alse;*out=cached;return true;}\n"
    "bool SaveSymbolCache(uint64_t,const std::vector<uint8_t>&p){++saves;cached=p"
    ";return !saveFault;}\n"
    "bool ReadImageFile(const Image&,uint64_t offset,void*out,size_t n){fileReads"
    "++;if(offset>outerFile.size()||n>outerFile.size()-offset)return false;std::m"
    "emcpy(out,outerFile.data()+offset,n);return true;}\n"
    "using off_t=int64_t;using ssize_t=int64_t;int opened=0;\n"
    "constexpr int O_RDONLY=0,O_CLOEXEC=0,O_NONBLOCK=0;\n"
    "struct stat{int st_mode=1;int64_t st_size=0;uint64_t st_dev=0,st_ino=0;};\n"
    "#define S_ISREG(m) ((m)==1)\n"
    "int fstat(int,struct stat*s){s->st_size=outerFile.size();s->st_dev=123;s->st"
    "_ino=456;return 0;}\n"
    "bool StatMatches(const Image& image,const struct stat& st){return S_ISREG(st"
    ".st_mode)&&st.st_size>=0&&st.st_dev==image.sourceDevice&&st.st_ino==image.so"
    "urceInode&&(image.fromApkEntry?image.apkEntryOffset:0)<=uint64_t(st.st_size)"
    "&&image.fileViewBytes<=uint64_t(st.st_size)-(image.fromApkEntry?image.apkEnt"
    "ryOffset:0);}\n"
    "int open(const char*,int){opened++;return 3;}int close(int){return 0;}\n"
    "ssize_t pread(int,void*out,size_t n,off_t at){if(at<0||uint64_t(at)>outerFil"
    "e.size()||n>outerFile.size()-at)return -1;memcpy(out,outerFile.data()+at,n);"
    "return n;}\n"
    "}\n"
)
if "CodeView(image)" in S:
    sys.path.insert(0, str(W / "tests/os4-audit-symbol-prologue-20261005"))
    from fixture_support import codeview_fixture

    pre += codeview_fixture(
        R,
        (
            "if(faultAll || (faultAddress && address==faultAddress))return false;for(cons"
            "t auto& [begin,bytes]:readable)if(address>=begin&&address-begin<=bytes&&out."
            "size()<=bytes-(address-begin)){std::memcpy(out.data(),reinterpret_cast<void*"
            ">(address),out.size());return true;}return false;"
        ),
    )
pre += (
    header
    + "\n"
    + code
    + "\nnamespace hometweaks {\n"
    + fun(INCLUDE_DIR, "bool ReadImageFile(").replace(
        "bool ReadImageFile(", "bool audit_read_image_file("
    )
    + "\n}\n"
)
pre += (
    "\n"
    "std::vector<uint8_t> read(const char*p){std::ifstream f(p,std::ios::binary|s"
    "td::ios::ate);if(!f)return {};const auto size=f.tellg();std::vector<uint8_t>"
    "b(size);f.seekg(0);f.read(reinterpret_cast<char*>(b.data()),b.size());return"
    " b;}\n"
    "int main(int argc,char**argv){if(argc!=5)return 2;std::string test=argv[1];o"
    "uterFile=read(argv[2]);decoded=read(argv[3]);auto full=read(argv[4]);\n"
    "using namespace hometweaks;Elf64_Ehdr h{};memcpy(&h,full.data(),64);uint64_t"
    " end=0;\n"
    "for(unsigned i=0;i<h.e_phnum;i++){Elf64_Phdr p{};memcpy(&p,full.data()+h.e_p"
    "hoff+i*sizeof p,sizeof p);if(p.p_type==1)end=std::max(end,p.p_vaddr+p.p_mems"
    "z);}\n"
    "mapped.resize(end+4096);readable.push_back({uintptr_t(mapped.data()),mapped."
    "size()});Image image{};image.base=uintptr_t(mapped.data());strcpy(image.path"
    ',"fixture.so");\n'
    "for(unsigned i=0;i<h.e_phnum;i++){Elf64_Phdr p{};memcpy(&p,full.data()+h.e_p"
    "hoff+i*sizeof p,sizeof p);if(p.p_type!=1)continue;\n"
    " memcpy(mapped.data()+p.p_vaddr,full.data()+p.p_offset,p.p_filesz);image.seg"
    "ments[image.segmentCount++]={image.base+p.p_vaddr,image.base+p.p_vaddr+p.p_m"
    "emsz,p.p_flags};}\n"
    'if(test=="fault_all")faultAll=true;\n'
    "int checks=0,failed=0;auto ok=[&](bool v,const char*m){checks++;if(!v){faile"
    'd++;std::cout<<"FAIL "<<m<<"\\n";}};\n'
    'if(test=="exec_bounds"){\n'
    " alignas(4) uint32_t words[64]{};words[0]=0xa9bf79fd;words[1]=0xaa0f03fd;rea"
    "dable.push_back({uintptr_t(words),sizeof(words)});\n"
    " Image small{};small.base=uintptr_t(words)-0x100;small.segmentCount=1;small."
    "segments[0]={uintptr_t(words),uintptr_t(words)+4,5};\n"
    ' ok(!LooksLikeDartFunction(small,0x100,"Fixture",8),"second prologue word mu'
    'st be inside executable segment");\n'
    " small.segments[0].end+=4;\n"
    ' ok(LooksLikeDartFunction(small,0x100,"Fixture",8),"exact 8-byte prologue re'
    'mains supported");\n'
    ' ok(!LooksLikeDartFunction(small,0x100,"Fixture",12),"entire advertised func'
    'tion extent must fit exec segment");\n'
    ' ok(!LooksLikeDartFunction(small,0x100,"Fixture",4),"four-byte frame claim r'
    'ejected");\n'
    ' ok(!LooksLikeDartFunction(small,0x100,"Fixture",9),"unaligned byte extent r'
    'ejected");\n'
    ' ok(!LooksLikeDartFunction(small,0x100,nullptr,8),"null name rejected before'
    ' opcode reads");\n'
    " words[0]=0xf94001e2;words[1]=0x93407c42;\n"
    ' ok(!LooksLikeDartFunction(small,0x100,"allocateTwoByteString",0xec),"verifi'
    'ed stub reads require full declared exec extent too");\n'
    '}else if(test=="io_bounds"){\n'
    " unsigned char dst[16]{};image.fileViewBytes=outerFile.size();image.sourceDe"
    "vice=123;image.sourceInode=456;image.fromApkEntry=true;image.apkEntryOffset="
    "UINT64_MAX-15;opened=0;\n"
    ' ok(!audit_read_image_file(image,32,dst,16)&&opened==0,"APK origin+offset ov'
    'erflow rejected before IO");\n'
    " image.apkEntryOffset=0;opened=0;\n"
    ' ok(!audit_read_image_file(image,UINT64_MAX,dst,16)&&opened==0,"signed off_t'
    ' conversion overflow rejected before IO");\n'
    ' opened=0;ok(!audit_read_image_file(image,INT64_MAX-3,dst,16)&&opened==0,"en'
    'd offset overflow rejected before IO");\n'
    " opened=0;ok(audit_read_image_file(image,16,dst,16)&&opened==1&&!memcmp(dst,"
    'outerFile.data()+16,16),"valid original pread behavior remains exact");\n'
    "}else{\n"
    ' if(test=="fault_target"){\n'
    " Elf64_Ehdr mini{};memcpy(&mini,decoded.data(),64);std::vector<Elf64_Shdr> s"
    "h(mini.e_shnum);memcpy(sh.data(),decoded.data()+mini.e_shoff,sh.size()*64);\n"
    " for(auto &sy:sh)if(sy.sh_type==SHT_SYMTAB){auto &st=sh[sy.sh_link];for(size"
    "_t at=0;at<sy.sh_size;at+=24){Elf64_Sym row{};memcpy(&row,decoded.data()+sy."
    "sh_offset+at,24);if(!strcmp(reinterpret_cast<char*>(decoded.data()+st.sh_off"
    'set+row.st_name),"BigFolderCommonStrategy.calItemSize"))faultAddress=image.b'
    "ase+row.st_value;}}}\n"
    ' blockLargeString=test=="oversize_shstr";auto &index=SymbolIndex::Instance()'
    ";bool loaded=false;bool threw=false;\n"
    " try{loaded=index.EnsureLoaded(image);}catch(const std::exception&e){threw=t"
    'rue;std::cout<<"EXCEPTION "<<e.what()<<"\\n";}\n'
    ' blockLargeString=false;uint32_t va=0,size=0,span=0;const char* target="BigF'
    'olderCommonStrategy.calItemSize";\n'
    ' if(test=="fault_all"||test=="fault_target"){\n'
    '  ok(!threw&&loaded==(test=="fault_target"),"read fault drops affected roots'
    ' without crashing unrelated roots");\n'
    "  va=0xabcdef;size=0xabcdef;ok(!index.Find(target,&va,&size)&&va==0xabcdef&&"
    'size==0xabcdef,"failed prologue never publishes target/out fields");\n'
    ' }else if(test=="real"){\n'
    '  ok(loaded&&!threw,"real 7722 ELF loads");ok(index.Find(target,&va,&size)&&'
    'va==0x15e0088,"actual original root address preserved");\n'
    '  ok(index.SpanFrom(va,&span)&&span==0x3b8,"full STT_FUNC boundary retained '
    'for large-folder body");\n'
    '  ok(!index.Find("HotseatLayerGetxController.calculatePositionX",&va,&size),'
    '"real duplicate function name is ambiguous, not largest-body wins");\n'
    '  ok(!index.Find("HotseatLayerGetxController.calHotseatCenterPosition",&va,&'
    'size),"second real same-name alias is not guessed");\n'
    "  const auto reads=fileReads;for(int i=0;i<1000;i++)index.EnsureLoaded(image"
    ");\n"
    '  ok(fileReads==reads,"ready symbol index never rescans file on repeated loo'
    'kup");\n'
    "\n"
    "    auto good=cached;cacheOn=true;index.ResetForTest();auto before=fileReads"
    ";\n"
    '    ok(index.TryLoadCached(image,123)&&fileReads==before,"cache loads real r'
    'oots without ELF/XZ reread");\n'
    '    ok(index.Find(target,&va,&size)&&va==0x15e0088,"cache restores original '
    'target");\n'
    "    for(size_t off: {size_t(0),size_t(4),size_t(8),size_t(12)}){cached=good;"
    "cached[off]^=0xff;index.ResetForTest();ok(!index.TryLoadCached(image,123)&&!"
    'index.loaded(),"corrupt registry/count/flag rejects atomic publication");}\n'
    "    cached=good;cached.pop_back();index.ResetForTest();ok(!index.TryLoadCach"
    'ed(image,123),"truncated cache rejects");\n'
    "    cached=good;faultAll=true;index.ResetForTest();ok(!index.TryLoadCached(i"
    'mage,123),"cached address still requires original live code guard");faultAll'
    "=false;\n"
    '    cached=good;index.ResetForTest();ok(index.TryLoadCached(image,123),"vali'
    'd cache recovers after rejected attempts");\n'
    "cacheOn=false;slowDecode=true;index.ResetForTest();\n"
    '    ok(!index.EnsureLoaded(image,1)&&!index.loaded()&&!index.attempted(),"de'
    'adline discards partial index and permits worker retry");\n'
    "    slowDecode=false;ok(index.EnsureLoaded(image)&&index.Find(target,&va,&si"
    'ze),"unbounded worker recovers timed out startup");\n'
    '    saveFault=true;index.ResetForTest();ok(index.EnsureLoaded(image),"persis'
    't failure does not discard ready index");\n'
    "    const auto failedSaveCount=saves;for(int n=0;n<1000;++n)index.EnsureLoad"
    "ed(image);\n"
    '    ok(saves==failedSaveCount,"failed persistence attempted once, not per lo'
    'okup");saveFault=false;\n'
    '    std::cout<<"FOUND="<<index.foundCount()<<"/"<<TargetFunctionCount()<<"\\n'
    '";\n'
    "  for(size_t i=0;i<TargetFunctionCount();i++){uint32_t v=0,z=0,s=0;const aut"
    "o& target=TargetFunctionAt(i);\n"
    '   if(index.Find(target.needle,&v,&z)){index.SpanFrom(v,&s);std::cout<<"ROOT'
    '\\t"<<target.needle<<"\\t"<<v<<"\\t"<<z<<"\\t"<<s<<"\\n";}}\n'
    ' }else if(test=="foreign_boundary"){\n'
    "  ok(loaded&&!threw&&index.Find(target,&va,&size)&&index.SpanFrom(va,&span)&"
    '&span==0x3b8,"non-executable fake function record cannot truncate genuine ow'
    'ning body");\n'
    ' }else if(test=="valid_unaligned_tables"){\n'
    '  ok(loaded&&!threw&&index.Find(target,&va,&size)&&va==0x15e0088,"unaligned '
    'packed records read via memcpy without dereference UB");\n'
    ' }else if(test=="bad_type"||test=="high_va"||test=="high_size"||test=="undef'
    'ined"||test=="wrong_section"){\n'
    '  ok(loaded&&!threw,"unrelated valid original roots remain loaded");\n'
    '  ok(!index.Find(target,&va,&size),"invalid typed/ranged named function neve'
    'r survives narrowing");\n'
    " }else{\n"
    '  ok(!loaded&&!threw,"malformed metadata cleanly rejected");\n'
    '  if(test=="oversize_shstr")ok(blocked==0,"oversized shstr checked BEFORE al'
    'location");\n'
    '  if(test=="wrap_section_headers")ok(std::string(index.status()).find("调试数据不'
    '是预期的 ELF")!=std::string::npos,"wrapped section table rejected before derefer'
    'ence");\n'
    " }\n"
    " const auto reads=fileReads;for(int i=0;i<1000;i++)index.EnsureLoaded(image)"
    ';ok(fileReads==reads,"immutable parsed or rejected image never rescans on re'
    'peat lookup");\n'
    ' std::cout<<"STATUS="<<index.status()<<"\\n";\n'
    "}\n"
    'std::cout<<"SYMBOL_LOADER "<<test<<": "<<checks<<" checks; failed="<<failed<'
    '<"\\n";return failed?1:0;\n'
    "}\n"
)
(run / "test.cpp").write_text(pre, encoding="utf8")
zig = W / "tests/dynamic-address-audit/runtime/zig-windows-x86_64-0.13.0/zig.exe"
# Local compiler/JVM or fixture binary with separate, harness-owned arguments.
p = subprocess.run(  # nosec B603
    [
        str(zig),
        "c++",
        "-std=c++20",
        "-O0",
        str(run / "test.cpp"),
        "-o",
        str(run / "test.exe"),
    ],
    capture_output=True,
    text=True,
    encoding="utf8",
)
print(p.stdout + p.stderr, end="")
if p.returncode:
    sys.exit(p.returncode)
cases = {}


def add(name, out=None, debug=None):
    cases[name] = (
        bytes(outer.data if out is None else out),
        bytes(mini.data if debug is None else debug),
    )


for n in ["real", "exec_bounds", "io_bounds"]:
    add(n)
if "CodeView(image)" in S:
    for n in ["fault_all", "fault_target"]:
        add(n)
# All mutation offsets come from the actual ELF metadata, never production patch offsets.
shoff = mini.shoff
syidx = mini.section_names[".symtab"]
sysec = mini.sections[syidx]
stsec = mini.sections[sysec[6]]
strs = mini.data[stsec[4] : stsec[4] + stsec[5]]
target_entry = None
for at in range(sysec[4], sysec[4] + sysec[5], 24):
    n, info, other, ndx, v, z = struct.unpack_from("<IBBHQQ", mini.data, at)
    if strs[n : strs.find(b"\0", n)] == b"BigFolderCommonStrategy.calItemSize":
        target_entry = at
        break
_require((target_entry is not None))
for n, o, b in [
    ("inner_class", 4, 1),
    ("inner_endian", 5, 2),
    ("inner_ident_version", 6, 0),
]:
    d = bytearray(mini.data)
    d[o] = b
    add(n, debug=d)
for n, o, fmt, v in [
    ("inner_machine", 18, "H", 62),
    ("inner_version", 20, "I", 0),
    ("wrap_section_headers", 40, "Q", 2**64 - 8),
    ("large_section_count", 60, "H", 300),
]:
    d = bytearray(mini.data)
    struct.pack_into("<" + fmt, d, o, v)
    add(n, debug=d)
for n, o, b in [("outer_endian", 5, 2), ("outer_ident_version", 6, 0)]:
    d = bytearray(outer.data)
    d[o] = b
    add(n, out=d)
d = bytearray(outer.data)
struct.pack_into("<H", d, 18, 62)
add("outer_machine", out=d)
d = bytearray(outer.data)
outersh = outer.shoff + outer.shstrndx * 64
struct.pack_into("<Q", d, outersh + 32, 2**21)
add("oversize_shstr", out=d)
for n, o, fmt, v in [
    ("wrap_symtab", shoff + syidx * 64 + 24, "Q", 2**64 - 8),
    ("trailing_symbol_bytes", shoff + syidx * 64 + 32, "Q", sysec[5] + 1),
    ("bad_strtab_type", shoff + sysec[6] * 64 + 4, "I", 0),
    ("wrap_strtab", shoff + sysec[6] * 64 + 24, "Q", 2**64 - 8),
]:
    d = bytearray(mini.data)
    struct.pack_into("<" + fmt, d, o, v)
    add(n, debug=d)
for n, o, fmt, v in [
    ("bad_type", target_entry + 4, "B", 17),
    ("high_va", target_entry + 8, "Q", 0x100000000 + 0x15E0088),
    ("high_size", target_entry + 16, "Q", 0x100000000 + 0x3B8),
    ("undefined", target_entry + 6, "H", 0),
    ("wrong_section", target_entry + 6, "H", sysec[6]),
]:
    d = bytearray(mini.data)
    struct.pack_into("<" + fmt, d, o, v)
    add(n, debug=d)
d = bytearray(mini.data)
for at in range(sysec[4], sysec[4] + sysec[5], 24):
    n, info, other, ndx, v, z = struct.unpack_from("<IBBHQQ", mini.data, at)
    if info & 15 == 2 and v and v < 0x1400000:
        struct.pack_into("<IBBHQQ", d, at, 0, info, other, sysec[6], 0x15E0088 + 4, 0)
        break
add("foreign_boundary", debug=d)
# Shift the actual serialized sections/symbols by one byte, updating all offsets.
d = bytearray(mini.data[:64]) + bytearray(b"\0") + bytearray(mini.data[64:])
struct.pack_into("<Q", d, 40, shoff + 1)
for i, section in mini.sections.items():
    if section[4] >= 64:
        struct.pack_into("<Q", d, shoff + 1 + i * 64 + 24, section[4] + 1)
add("valid_unaligned_tables", debug=d)
failed = 0
results = []
for name, (o, d) in cases.items():
    op = run / (name + "-outer.bin")
    dp = run / (name + "-mini.bin")
    op.write_bytes(o)
    dp.write_bytes(d)
    command = [
        str(run / "test.exe"),
        name,
        str(op),
        str(dp),
        str(A / "launcher-7722-libapp.so"),
    ]
    # Local compiler/JVM or fixture binary with separate, harness-owned arguments.
    p = subprocess.run(  # nosec B603
        command, capture_output=True, text=True, encoding="utf8", errors="replace"
    )
    print(p.stdout + p.stderr, end="", flush=True)
    if p.returncode:
        failed += 1
        print(f"CASE_EXIT {name}={p.returncode}")
    results.append(
        dict(
            case=name,
            # nosemgrep: python_exec_rule-subprocess-call
            command=subprocess.list2cmdline(command),
            output=p.stdout + p.stderr,
            exit_status=p.returncode,
        )
    )
(run / "results.json").write_text(
    json.dumps(results, ensure_ascii=False, indent=2), encoding="utf8"
)
print(
    f"SYMBOL_LOADER_AUDIT={len(cases)} cases; failed={failed}; production parser/code guards; XZ decoder and file/live-read boundaries substituted"
)
sys.exit(1 if failed else 0)
