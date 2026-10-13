# Subprocess is needed for the reviewed argv-only fixture/tool calls below.
import subprocess  # nosec B404
import sys
from pathlib import Path

D = Path(__file__).resolve().parent
W = D.parents[1]
R = Path(sys.argv[1]) if len(sys.argv) > 1 else W
source = (R / "app/src/main/cpp/targets/home/home_layout_hooks.cpp").read_text(
    encoding="utf8"
)
if "hc_back_window_body" not in source:
    print("WINDOW_APPLY=absent; stock GestureStub region persists")
    sys.exit(1)
a = source.index('extern "C" void hc_back_gesture_body(')
b = source.index('extern "C" void hc_back_window_entry();', a)
core = source[a:b]
a = source.index('extern "C" void hc_back_window_body(')
b = source.index("std::string g_container_path;", a)
body = source[a:b]
c = (
    "\n"
    '#include "home_back_gesture.h"\n'
    "#include <atomic>\n"
    "#include <fstream>\n"
    "#include <iostream>\n"
    "using Words=std::array<uint32_t,4>;\n"
    "struct Slot{uintptr_t address=0;Words original_words{};};\n"
    "std::atomic_uint32_t g_back_gesture_config{60u|(100u<<16)},g_back_stock_widt"
    "h{0},g_back_stock_sequence{0};\n"
    "std::atomic_uint64_t g_back_stock{0};\n"
    "std::atomic_flag g_back_stock_writer=ATOMIC_FLAG_INIT;\n"
    "std::atomic_uint32_t g_back_window_applied[2]{{60u|(100u<<16)},{60u|(100u<<1"
    "6)}};\n"
    "home_layout::BackWindowShape g_back_window_shape{};Slot g_back_window_update"
    "{};\n"
    "bool read_ok=true,words_ok=true;\n"
    "bool stable_read(const Slot &s,Words &out){out=s.original_words;if(!words_ok"
    ")out[0]^=1;return read_ok;}\n"
    "BODY\n"
    "CORE\n"
    "unsigned calls=0,checks=0,failed=0;std::byte *saved_for_nested=nullptr;home_"
    "layout::BackWindowRect applied{};\n"
    "void update(uint32_t side,const home_layout::BackWindowRect *r){++calls;appl"
    "ied=*r;if(saved_for_nested)hc_back_window_body(saved_for_nested);}\n"
    'void ok(bool b){++checks;if(!b){++failed;std::cout<<"FAIL_CHECK="<<checks<<"'
    '\\\\n";}}\n'
    "int main(int argc,char**argv){\n"
    " std::ifstream f(argv[1],std::ios::binary);std::vector<char> raw((std::istre"
    "ambuf_iterator<char>(f)),{});\n"
    " auto bytes=std::span<const std::byte>(reinterpret_cast<const std::byte*>(ra"
    "w.data()),raw.size());\n"
    " auto image=home_layout::elf_targets::parse(bytes);auto shape=home_layout::r"
    "esolve_back_window(bytes);ok(bool(shape));if(!shape)return 1;\n"
    ' std::cout<<"WINDOW_RESOLVED="<<std::hex<<shape->apply<<" "<<shape->update<<'
    '" "<<shape->splice<<" "<<shape->rect_sp<<" "<<shape->side_field<<std::dec<<"'
    '\\n";\n'
    " for(auto site:{shape->splice,shape->splice+4,shape->splice+8,shape->splice+"
    "24}){auto mutant=raw;auto at=image->file_offset(site,4);uint32_t nop=0xd5032"
    "01f;std::memcpy(mutant.data()+*at,&nop,4);ok(!home_layout::resolve_back_wind"
    "ow({reinterpret_cast<const std::byte*>(mutant.data()),mutant.size()}));}\n"
    " std::array<std::byte,1024> saved{};std::array<std::byte,512> receiver{};\n"
    " auto set=[&](unsigned at,auto value){std::memcpy(saved.data()+at,&value,siz"
    "eof(value));};\n"
    " auto incoming=[&](home_layout::BackWindowRect r){set(784+shape->rect_sp,r);"
    "};\n"
    " auto get=[&](){home_layout::BackWindowRect r;std::memcpy(&r,saved.data()+78"
    "4+shape->rect_sp,16);return r;};\n"
    " auto baseline=[&](unsigned side){saved.fill(std::byte{0x5a});set(64,int32_t"
    "(280));set(168,int32_t(2576));set(192,int32_t(1200));set(224,int32_t(2670));"
    "set(176,int32_t(520));set(384,21.0f);hc_back_gesture_body(saved.data());set("
    "160,reinterpret_cast<uintptr_t>(receiver.data()));set(152,int32_t(122));rece"
    "iver[shape->side_field]=std::byte(side);g_back_window_applied[side]=60u|(100"
    "u<<16);incoming(side?home_layout::BackWindowRect{1132,280,1200,2576}:home_la"
    "yout::BackWindowRect{0,280,68,2576});};\n"
    " g_back_window_shape=*shape;g_back_window_update.address=reinterpret_cast<ui"
    "ntptr_t>(update);saved_for_nested=saved.data();\n"
    " for(unsigned side:{0u,1u})for(int height:{10,25,60,100})for(int width:{100,"
    "200,400}){\n"
    "  g_back_gesture_config=uint32_t(height)|(uint32_t(width)<<16);baseline(side"
    ");const auto before=saved;const auto old_calls=calls;const auto old_rect=get"
    "();\n"
    "  hc_back_window_body(saved.data());auto expected=home_layout::back_window_r"
    "ect(1200,2670,280,2576,68,side,{height,width});ok(expected&&get()==*expected"
    ");\n"
    "  ok(calls==old_calls+((expected&&old_rect==*expected)?0:1));\n"
    "  auto after=saved;auto n=calls;hc_back_window_body(saved.data());ok(saved=="
    "after&&calls==n);\n"
    "  // No multiplication of an already-applied 200%/400% width; default restor"
    "es stock immediately.\n"
    "  g_back_gesture_config=60u|(100u<<16);hc_back_window_body(saved.data());aut"
    "o stock=home_layout::back_window_rect(1200,2670,280,2576,68,side,{});ok(get("
    ")==*stock);\n"
    "  for(size_t i=0;i<784;++i)if(i<152||i>=156)ok(saved[i]==before[i]);\n"
    " }\n"
    " g_back_gesture_config=25u|(200u<<16);baseline(0);auto before=saved;read_ok="
    "false;hc_back_window_body(saved.data());ok(saved==before);read_ok=true;words"
    "_ok=false;hc_back_window_body(saved.data());ok(saved==before);words_ok=true;"
    "\n"
    " baseline(0);incoming({0,2200,68,2576});before=saved;hc_back_window_body(sav"
    "ed.data());ok(saved==before); // app exclusion preserved\n"
    " baseline(0);g_back_stock_sequence.fetch_add(1);before=saved;hc_back_window_"
    "body(saved.data());ok(saved==before);g_back_stock_sequence.fetch_add(1);\n"
    ' std::cout<<"WINDOW_APPLY="<<checks<<" checks; failed="<<failed<<"; original'
    " update call nested guard/idempotence/default restoration/exclusions/source "
    'guard\\n";return failed?1:0;\n'
    "}\n"
)
c = c.replace("BODY", body).replace("CORE", core)
(D / "test.cpp").write_text(c)
cmd = [
    str(W / "tests/dynamic-address-audit/runtime/zig-windows-x86_64-0.13.0/zig.exe"),
    "c++",
    "-std=c++20",
    "-O0",
    "-I" + str(R / "app/src/main/cpp/targets/home"),
    "-I" + str(W / "app/src/main/cpp"),
    str(D / "test.cpp"),
    "-o",
    str(D / "test.exe"),
]
# Local compiler/JVM or fixture binary with separate, harness-owned arguments.
p = subprocess.run(cmd, capture_output=True, text=True)  # nosec B603
print(p.stdout + p.stderr, end="")
if p.returncode:
    sys.exit(p.returncode)
# Local compiler/JVM or fixture binary with separate, harness-owned arguments.
p = subprocess.run(  # nosec B603
    [str(D / "test.exe"), str(W / "tests/back-gesture-os4/libapp_launcher.so")],
    capture_output=True,
    text=True,
)
print(p.stdout + p.stderr, end="")
sys.exit(p.returncode)
