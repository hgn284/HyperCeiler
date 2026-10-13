import json
import os
import re
# Subprocess is needed for the reviewed argv-only fixture/tool calls below.
import subprocess  # nosec B404
from pathlib import Path

W = Path(__file__).resolve().parents[2]
D = Path(__file__).resolve().parent
out = D / "java"
out.mkdir(exist_ok=True)
jdk = Path(os.environ.get("JAVA_HOME", "D:/build-tools/jdk-25.0.4.1+1")) / "bin"
sources = (
    list((W / "tests/home-layout-native/stubs").rglob("*.java"))
    + list((W / "tests/home-dock-window/stubs").rglob("*.java"))
    + [
        W
        / "library/libhook/src/main/java/com/sevtinge/hyperceiler/libhook/provider/HomeLayoutPrefsSnapshot.java",
        W
        / "library/libhook/src/main/java/com/sevtinge/hyperceiler/libhook/rules/home/dock/HomeLayoutNativeEndpointOS4.java",
        D / "FolderAutoCloseEndpointTest.java",
    ]
)
# Local compiler/JVM or fixture binary with separate, harness-owned arguments.
subprocess.run(  # nosec B603
    [str(jdk / "javac.exe"), "-encoding", "UTF-8", "-d", str(out)]
    + list(map(str, sources)),
    check=True,
)
# Local compiler/JVM or fixture binary with separate, harness-owned arguments.
subprocess.run(  # nosec B603
    [
        str(jdk / "java.exe"),
        "-ea",
        "-cp",
        str(out),
        "com.sevtinge.hyperceiler.libhook.rules.home.dock.FolderAutoCloseEndpointTest",
    ],
    check=True,
)
stubs = json.loads(
    (W / "tests/home-os4-gate-controls/stubs.json").read_text(encoding="utf8")
)
gate = (
    W
    / "library/core/src/main/java/com/sevtinge/hyperceiler/hooker/home/HomeOS4AdaptationGate.java"
)
res = {}
for kind, name in re.findall(r"R\.(\w+)\.(\w+)", gate.read_text(encoding="utf8")):
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
stubs["FolderAutoGateTest.java"] = (
    "import androidx.preference.*;import com.sevtinge.hyperceiler.hooker.home.Hom"
    "eOS4AdaptationGate;import com.sevtinge.hyperceiler.core.R;import com.sevting"
    "e.hyperceiler.libhook.utils.api.DeviceHelper;\n"
    "public class FolderAutoGateTest {public static void main(String[]a){int chec"
    "ks=0;for(float version:new float[]{3,4})for(boolean prior:new boolean[]{fals"
    "e,true}){DeviceHelper.System.version=version;PreferenceGroup g=new Preferenc"
    'eGroup();Preference auto=new Preference();auto.key="prefs_key_home_folder_au'
    'to_close";auto.enabled=prior;g.addPreference(auto);Preference other=new Pref'
    'erence();other.key="prefs_key_home_other_disable_prestart";g.addPreference(o'
    "ther);HomeOS4AdaptationGate.apply(g,R.xml.home_other_new);if(auto.enabled!=p"
    'rior)throw new AssertionError("dependency overwritten");checks++;if(other.en'
    'abled!=(version!=4))throw new AssertionError("other gate changed");checks++;'
    '}System.out.println("FOLDER_AUTO_CLOSE_UI="+checks+" checks; failed=0");}}'
)
keep = [
    "androidx/preference/Preference.java",
    "androidx/preference/PreferenceGroup.java",
    "com/sevtinge/hyperceiler/libhook/utils/api/DeviceHelper.java",
    "com/sevtinge/hyperceiler/core/R.java",
    "FolderAutoGateTest.java",
]
files = []
for n in keep:
    p = out / "stubs" / n
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(stubs[n], encoding="utf8")
    files.append(str(p))
# Local compiler/JVM or fixture binary with separate, harness-owned arguments.
subprocess.run(  # nosec B603
    [str(jdk / "javac.exe"), "-encoding", "UTF-8", "-d", str(out / "gate"), str(gate)]
    + files,
    check=True,
)
# Local compiler/JVM or fixture binary with separate, harness-owned arguments.
subprocess.run(  # nosec B603
    [str(jdk / "java.exe"), "-ea", "-cp", str(out / "gate"), "FolderAutoGateTest"],
    check=True,
)
