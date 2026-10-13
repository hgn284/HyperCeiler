import json
import re
# Subprocess is needed for the reviewed argv-only fixture/tool calls below.
import subprocess  # nosec B404
import sys
from pathlib import Path

D = Path(__file__).resolve().parent
W = D.parents[1]
R = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else W
out = D / ("java-" + R.name)
out.mkdir(exist_ok=True)
jdk = Path("D:/build-tools/jdk-25.0.4.1+1/bin")
sources = (
    list((W / "tests/home-layout-native/stubs").rglob("*.java"))
    + list((W / "tests/home-dock-window/stubs").rglob("*.java"))
    + [
        R
        / "library/libhook/src/main/java/com/sevtinge/hyperceiler/libhook/provider/HomeLayoutPrefsSnapshot.java",
        R
        / "library/libhook/src/main/java/com/sevtinge/hyperceiler/libhook/rules/home/dock/HomeLayoutNativeEndpointOS4.java",
        D / "BackGestureEndpointTest.java",
    ]
)
# Local compiler/JVM or fixture binary with separate, harness-owned arguments.
r = subprocess.run(  # nosec B603
    [str(jdk / "javac.exe"), "-encoding", "UTF-8", "-d", str(out)]
    + list(map(str, sources)),
    capture_output=True,
    text=True,
)
print(r.stdout + r.stderr, end="")
if r.returncode:
    sys.exit(r.returncode)
# Local compiler/JVM or fixture binary with separate, harness-owned arguments.
r = subprocess.run(  # nosec B603
    [
        str(jdk / "java.exe"),
        "-ea",
        "-cp",
        str(out),
        "com.sevtinge.hyperceiler.libhook.rules.home.dock.BackGestureEndpointTest",
    ],
    capture_output=True,
    text=True,
)
print(r.stdout + r.stderr, end="")
if r.returncode:
    sys.exit(r.returncode)
# Run actual settings and adaptation gate with Android preference stubs.
stubs = json.loads(
    (W / "tests/home-os4-gate-controls/stubs.json").read_text(encoding="utf8")
)
base = R / "library/core/src/main/java/com/sevtinge/hyperceiler/hooker/home"
sources = [
    base / (n + ".java") for n in ["HomeGestureSettings", "HomeOS4AdaptationGate"]
]
res = {}
for kind, name in re.findall(
    r"R\.(\w+)\.(\w+)", "".join(p.read_text(encoding="utf8") for p in sources)
):
    res.setdefault(kind, set()).add(name)
stubs["com/sevtinge/hyperceiler/core/R.java"] = (
    "package com.sevtinge.hyperceiler.core;public class R {"
    + "".join(
        "public static class "
        + k
        + "{"
        + "".join(
            "public static final int " + n + "=" + str(i) + ";"
            for i, n in enumerate(sorted(v), 1)
        )
        + "}"
        for k, v in res.items()
    )
    + "}"
)
stubs["BackGestureGateTest.java"] = (
    "\n"
    "import androidx.preference.*;import fan.preference.*;\n"
    "import com.sevtinge.hyperceiler.hooker.home.HomeGestureSettings;\n"
    "import com.sevtinge.hyperceiler.libhook.utils.api.DeviceHelper;\n"
    "import com.sevtinge.hyperceiler.common.utils.PrefsBridge;\n"
    "public class BackGestureGateTest {\n"
    " static int checks;static void check(boolean b){checks++;if(!b)throw new Ass"
    'ertionError("check "+checks);}\n'
    ' static Preference add(HomeGestureSettings f,String k,Preference p){p.key="p'
    'refs_key_home_"+k;f.prefs.put(p.key,p);f.screen.addPreference(p);return p;}\n'
    " public static void main(String[]a){for(float v:new float[]{3,4})for(boolean"
    " pad:new boolean[]{false,true})for(boolean disable:new boolean[]{false,true}"
    "){\n"
    "  DeviceHelper.System.version=v;DeviceHelper.Miui.pad=pad;PrefsBridge.values"
    ".clear();PrefsBridge.writes.clear();\n"
    '  PrefsBridge.values.put("prefs_key_home_navigation_disable_full_screen_back'
    '_gesture",disable);\n'
    '  HomeGestureSettings f=new HomeGestureSettings();add(f,"gesture_enable",new'
    ' SwitchPreference());add(f,"navigation_quick_back",new SwitchPreference());\n'
    '  var off=add(f,"navigation_disable_full_screen_back_gesture",new SwitchPref'
    'erence());add(f,"gesture_back_haptic",new DropDownPreference());\n'
    '  var h=add(f,"navigation_back_area_height",new SeekBarPreferenceCompat());v'
    'ar w=add(f,"navigation_back_area_width",new SeekBarPreferenceCompat());add(f'
    ',"gesture_actions",new PreferenceCategory());f.initPrefs();\n'
    "  if(v==4){check(h.enabled&&w.enabled);check(!off.enabled);off.change.onPref"
    "erenceChange(off,false);check(h.enabled&&w.enabled);}\n"
    "  else if(!pad){check(h.enabled==disable&&w.enabled==disable);}\n"
    "  if(v==4)check(PrefsBridge.writes.isEmpty());\n"
    ' }System.out.println("BACK_GESTURE_UI="+checks+" checks; failed=0");}\n'
    "}"
)
for n, s in stubs.items():
    p = out / "stubs" / n
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(s)
# Local compiler/JVM or fixture binary with separate, harness-owned arguments.
r = subprocess.run(  # nosec B603
    [str(jdk / "javac.exe"), "-encoding", "UTF-8", "-d", str(out / "gate")]
    + list(map(str, sources))
    + list(map(str, (out / "stubs").rglob("*.java"))),
    capture_output=True,
    text=True,
)
print(r.stdout + r.stderr, end="")
if r.returncode:
    sys.exit(r.returncode)
# Local compiler/JVM or fixture binary with separate, harness-owned arguments.
r = subprocess.run(  # nosec B603
    [str(jdk / "java.exe"), "-ea", "-cp", str(out / "gate"), "BackGestureGateTest"],
    capture_output=True,
    text=True,
)
print(r.stdout + r.stderr, end="")
sys.exit(r.returncode)
