import json
# Subprocess is needed for the reviewed argv-only fixture/tool calls below.
import subprocess  # nosec B404
from pathlib import Path

D = Path("tests/back-gesture-complete-20261007")
stub = D / "stubs"
stub.mkdir(exist_ok=True)
sources = {
    "android/os/Looper.java": "package android.os;public class Looper{public static Looper getMainLooper(){return new Looper();}}",
    "android/os/Handler.java": (
        "package android.os;public class Handler{public static java.util.List<Runnabl"
        "e> q=new java.util.ArrayList<>();public Handler(Looper l){}public boolean po"
        "st(Runnable r){q.add(r);return true;}public static void drain(){while(!q.isE"
        "mpty())q.remove(0).run();}}"
    ),
    "android/os/AsyncTask.java": (
        "package android.os;public class AsyncTask{public static java.util.List<Runna"
        "ble> q=new java.util.ArrayList<>();public static java.util.concurrent.Execut"
        "or THREAD_POOL_EXECUTOR=r->q.add(r);public static void drain(){while(!q.isEm"
        "pty())q.remove(0).run();}}"
    ),
    "android/net/Uri.java": (
        "package android.net;public class Uri{String s;Uri(String s){this.s=s;}public"
        " static Uri parse(String s){return new Uri(s);}public static Uri withAppende"
        'dPath(Uri u,String p){return new Uri(u.s+"/"+p);}public String toString(){re'
        "turn s;}}"
    ),
    ("android/database/Cursor.java"): (
        "package android.database;public interface Cursor extends AutoCloseable{b"
        "oolean moveToFirst();int getInt(int i);void close();}"
    ),
    "android/database/ContentObserver.java": (
        "package android.database;public class ContentObserver{public ContentObserver"
        "(android.os.Handler h){}public void onChange(boolean b,android.net.Uri u){}}"
    ),
    "android/content/ContentResolver.java": (
        "package android.content;public class ContentResolver{public int value=200;pu"
        "blic boolean fail;public android.database.ContentObserver observer;public vo"
        "id registerContentObserver(android.net.Uri u,boolean b,android.database.Cont"
        "entObserver o){observer=o;}public void unregisterContentObserver(android.dat"
        "abase.ContentObserver o){observer=null;}public android.database.Cursor query"
        "(android.net.Uri u,Object a,Object b,Object c,Object d){if(!u.toString().end"
        'sWith("integer/prefs_key_home_navigation_back_area_width/100"))throw new Ass'
        "ertionError(u);if(fail)return null;int v=value;return new android.database.C"
        "ursor(){public boolean moveToFirst(){return true;}public int getInt(int i){r"
        "eturn v;}public void close(){}};}public void change(){observer.onChange(fals"
        'e,android.net.Uri.parse("content://com.sevtinge.hyperceiler.provider.sharedp'
        'refs/integer/home_navigation_back_area_width"));}}'
    ),
    "android/content/Context.java": (
        "package android.content;public class Context{public final ContentResolver re"
        "solver=new ContentResolver();public Context getApplicationContext(){return t"
        "his;}public ContentResolver getContentResolver(){return resolver;}}"
    ),
    "android/content/SharedPreferences.java": (
        "package android.content;public interface SharedPreferences{interface OnShare"
        "dPreferenceChangeListener{void onSharedPreferenceChanged(SharedPreferences p"
        ",String key);}void registerOnSharedPreferenceChangeListener(OnSharedPreferen"
        "ceChangeListener l);void unregisterOnSharedPreferenceChangeListener(OnShared"
        "PreferenceChangeListener l);}"
    ),
    "com/sevtinge/hyperceiler/common/log/XposedLog.java": (
        "package com.sevtinge.hyperceiler.common.log;public class XposedLog{public st"
        "atic void i(String a,String b){}public static void w(String a,String b){thro"
        "w new AssertionError(b);}}"
    ),
    "com/sevtinge/hyperceiler/common/utils/PrefsBridge.java": (
        "package com.sevtinge.hyperceiler.common.utils;public class PrefsBridge{publi"
        "c static int getInt(String k,int d){return 100;}public static android.conten"
        "t.SharedPreferences getSharedPreferences(){return null;}}"
    ),
    "io/github/lingqiqi5211/ezhooktool/xposed/common/HookParam.java": (
        "package io.github.lingqiqi5211.ezhooktool.xposed.common;public class HookPar"
        "am{Object o;public HookParam(Object o){this.o=o;}public Object getThisObject"
        "(){return o;}}"
    ),
    "io/github/lingqiqi5211/ezhooktool/xposed/java/IMethodHook.java": (
        "package io.github.lingqiqi5211.ezhooktool.xposed.java;public interface IMeth"
        "odHook{default void after(io.github.lingqiqi5211.ezhooktool.xposed.common.Ho"
        "okParam p){}}"
    ),
    "com/sevtinge/hyperceiler/libhook/base/BaseHook.java": (
        "package com.sevtinge.hyperceiler.libhook.base;import io.github.lingqiqi5211."
        "ezhooktool.xposed.java.IMethodHook;public abstract class BaseHook{public fin"
        'al String TAG="Test";public static android.content.Context ctx=new android.c'
        "ontent.Context();public static IMethodHook resource,ctor;public static java."
        "util.List<Runnable> cleanup=new java.util.ArrayList<>();public abstract void"
        " init();public static Class<?> findClassIfExists(String s){try{return Class."
        "forName(s);}catch(Exception e){throw new AssertionError(e);}}public static v"
        "oid hookMethod(java.lang.reflect.Method m,IMethodHook h){resource=h;}public "
        "static void hookAllConstructors(Class<?> c,IMethodHook h){ctor=h;}public sta"
        "tic void registerHotReloadCleanup(Runnable r){cleanup.add(r);}public static "
        "void runOnApplicationAttach(java.util.function.Consumer<android.content.Cont"
        "ext> c){c.accept(ctx);}public static void registerContentObserverHotReloadCl"
        "eanup(android.content.ContentResolver c,android.database.ContentObserver o){"
        "cleanup.add(()->c.unregisterContentObserver(o));}}"
    ),
    "com/android/systemui/navigationbar/gestural/EdgeBackGestureHandler.java": (
        "package com.android.systemui.navigationbar.gestural;import com.sevtinge.hype"
        "rceiler.libhook.base.BaseHook;import io.github.lingqiqi5211.ezhooktool.xpose"
        "d.common.HookParam;public class EdgeBackGestureHandler{public int mEdgeWidth"
        "Left=97,mEdgeWidthRight=97;public EdgeBackGestureHandler(){BaseHook.ctor.aft"
        "er(new HookParam(this));}private void updateCurrentUserResources(){}public v"
        "oid reset(int n){mEdgeWidthLeft=n;mEdgeWidthRight=n;BaseHook.resource.after("
        "new HookParam(this));}}"
    ),
    "RuleTest.java": (
        "import com.sevtinge.hyperceiler.libhook.rules.systemui.navigation.*;import c"
        "om.sevtinge.hyperceiler.libhook.base.BaseHook;import com.android.systemui.na"
        "vigationbar.gestural.EdgeBackGestureHandler;import android.os.*;public class"
        " RuleTest{static int checks;static void ok(boolean x){checks++;if(!x)throw n"
        "ew AssertionError(checks);}static void drain(){AsyncTask.drain();Handler.dra"
        "in();}public static void main(String[] a){BackGestureWidthOS4 r=new BackGest"
        "ureWidthOS4();r.init();EdgeBackGestureHandler h=new EdgeBackGestureHandler()"
        ";ok(h.mEdgeWidthLeft==97);drain();ok(h.mEdgeWidthLeft==194);ok(h.mEdgeWidthR"
        "ight==194);var c=BaseHook.ctx.resolver;c.value=400;c.change();drain();ok(h.m"
        "EdgeWidthLeft==388);h.reset(50);ok(h.mEdgeWidthLeft==200);c.value=100;c.chan"
        "ge();drain();ok(h.mEdgeWidthLeft==50);c.fail=true;c.change();drain();ok(h.mE"
        "dgeWidthLeft==50);c.fail=false;c.value=200;c.change();AsyncTask.drain();c.va"
        "lue=400;c.change();AsyncTask.drain();Handler.drain();ok(h.mEdgeWidthLeft==20"
        "0);c.value=100;c.change();AsyncTask.drain();for(Runnable x:BaseHook.cleanup)"
        "x.run();Handler.drain();ok(h.mEdgeWidthLeft==50);ok(c.observer==null);System"
        '.out.println("SYSTEMUI_RULE="+checks+" checks; failed=0; real production hoo'
        'ks/provider/notifications/stale reply/failure/cleanup");}}'
    ),
}
for n, s in sources.items():
    p = stub / n
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(s, encoding="utf8")
(D / "stubs.json").write_text(json.dumps(sources, indent=2))
jdk = Path("D:/build-tools/jdk-25.0.4.1+1/bin")
out = D / "rule-classes"
out.mkdir(exist_ok=True)
prod = Path(
    "library/libhook/src/main/java/com/sevtinge/hyperceiler/libhook/rules/systemui/navigation"
)
# Local compiler/JVM or fixture binary with separate, harness-owned arguments.
subprocess.run(  # nosec B603
    [str(jdk / "javac.exe"), "-encoding", "UTF-8", "-d", str(out)]
    + [str(p) for p in stub.rglob("*.java")]
    + [
        str(prod / n)
        for n in ["BackGestureWidthState.java", "BackGestureWidthOS4.java"]
    ],
    check=True,
)
# Local compiler/JVM or fixture binary with separate, harness-owned arguments.
subprocess.run([str(jdk / "java.exe"), "-ea", "-cp", str(out), "RuleTest"], check=True)  # nosec B603
