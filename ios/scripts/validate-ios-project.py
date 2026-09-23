#!/usr/bin/env python3
"""Check the iOS project references the bundled game and that those files resolve.

This does not compile the app or launch a simulator. It checks the Xcode project,
Info.plist, the copy script, and that index.html can reach its scripts, styles,
and images when the bundle layout is preserved.
"""

from __future__ import annotations

import pathlib
import plistlib
import re
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
IOS = ROOT / "ios"
DIST = ROOT / "dist"
PBXPROJ = IOS / "LowTide.xcodeproj" / "project.pbxproj"
PLIST = IOS / "LowTide" / "Info.plist"
SCHEME = IOS / "LowTide.xcodeproj" / "xcshareddata" / "xcschemes" / "LowTide.xcscheme"
COPY_SCRIPT = IOS / "scripts" / "copy-web-bundle.sh"
SWIFT_DIR = IOS / "LowTide"

errors: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


def dist_files() -> list[str]:
    files = []
    for path in sorted(DIST.rglob("*")):
        if path.is_file():
            files.append(path.relative_to(DIST).as_posix())
    return files


def main() -> int:
    pbx = PBXPROJ.read_text()
    if pbx.count("{") != pbx.count("}"):
        fail("project.pbxproj has unbalanced braces")
    if pbx.count("(") != pbx.count(")"):
        fail("project.pbxproj has unbalanced parentheses")

    files = dist_files()
    if not files:
        fail("dist/ has no files")

    copy_text = COPY_SCRIPT.read_text()
    copied = re.findall(r'copy_file "([^"]+)"', copy_text)
    if copied != files:
        fail(f"copy script list {copied} does not match dist/ {files}")

    for rel in files:
        input_token = f'"$(SRCROOT)/../dist/{rel}"'
        output_token = f'"$(TARGET_BUILD_DIR)/$(UNLOCALIZED_RESOURCES_FOLDER_PATH)/dist/{rel}"'
        if input_token not in pbx:
            fail(f"project is missing copy input for {rel}")
        if output_token not in pbx:
            fail(f"project is missing copy output for {rel}")
        name = pathlib.PurePosixPath(rel).name
        if f"path = {name};" not in pbx and f'path = "{name}";' not in pbx:
            fail(f"project has no file reference for {name}")

    required_snippets = [
        "GENERATE_INFOPLIST_FILE = NO;",
        "IPHONEOS_DEPLOYMENT_TARGET = 16.0;",
        "PRODUCT_BUNDLE_IDENTIFIER = com.mooandidesign.lowtide;",
        "TARGETED_DEVICE_FAMILY = 1;",
        "INFOPLIST_FILE = LowTide/Info.plist;",
        "PRODUCT_NAME = \"$(TARGET_NAME)\";",
        'shellScript = "/bin/sh \\"${SRCROOT}/scripts/copy-web-bundle.sh\\"\\n";',
        "ENABLE_USER_SCRIPT_SANDBOXING = NO;",
        "SDKROOT = iphoneos;",
        'SUPPORTED_PLATFORMS = "iphoneos iphonesimulator";',
        "SUPPORTS_MACCATALYST = NO;",
    ]
    for snippet in required_snippets:
        if snippet not in pbx:
            fail(f"project.pbxproj missing setting: {snippet}")

    # Web files are referenced for the navigator and the copy phase, not flattened
    # into Copy Bundle Resources (that would drop the assets/ directory).
    resources = pbx.split("/* Begin PBXResourcesBuildPhase section */", 1)[-1].split(
        "/* End PBXResourcesBuildPhase section */", 1
    )[0]
    for rel in files:
        if pathlib.PurePosixPath(rel).name in resources:
            fail(f"{rel} is in Copy Bundle Resources and would be flattened")

    sources = pbx.split("/* Begin PBXSourcesBuildPhase section */", 1)[-1].split(
        "/* End PBXSourcesBuildPhase section */", 1
    )[0]
    for swift in sorted(SWIFT_DIR.glob("*.swift")):
        token = f"{swift.name} in Sources"
        if token not in sources:
            fail(f"{swift.name} is not in Compile Sources")

    plist = plistlib.loads(PLIST.read_bytes())
    if plist.get("CFBundleDisplayName") != "Low Tide":
        fail("CFBundleDisplayName is not Low Tide")
    orientations = plist.get("UISupportedInterfaceOrientations")
    if orientations != ["UIInterfaceOrientationPortrait"]:
        fail(f"unexpected iPhone orientations: {orientations}")
    ipad = plist.get("UISupportedInterfaceOrientations~ipad")
    if ipad != ["UIInterfaceOrientationPortrait"]:
        fail(f"unexpected iPad orientations: {ipad}")
    launch = plist.get("UILaunchScreen") or {}
    if launch.get("UIColorName") != "LaunchBackground":
        fail("launch screen does not use LaunchBackground")
    if plist.get("UIStatusBarStyle") != "UIStatusBarStyleLightContent":
        fail("status bar style is not light content")
    if plist.get("LSRequiresIPhoneOS") is not True:
        fail("LSRequiresIPhoneOS is not set")
    if plist.get("CFBundleIconName") != "AppIcon":
        fail("CFBundleIconName is not AppIcon")
    scene = plist.get("UIApplicationSceneManifest") or {}
    if scene.get("UIApplicationSupportsMultipleScenes") is not False:
        fail("scene manifest is missing")
    if "UISceneConfigurations" in scene:
        fail("scene manifest should not point at a storyboard")

    scheme = SCHEME.read_text()
    if "C10000000000000000000001" not in scheme or "LowTide.app" not in scheme:
        fail("shared scheme does not reference the LowTide target")
    object_ids = re.findall(r"^\t\t([A-Za-z0-9]{24}) ", pbx, flags=re.M)
    if len(object_ids) < 40:
        fail(f"project.pbxproj only has {len(object_ids)} object ids")
    if len(object_ids) != len(set(object_ids)):
        fail("project.pbxproj has duplicate object ids")
    bad_ids = [i for i in object_ids if not re.fullmatch(r"[0-9A-F]{24}", i)]
    if bad_ids:
        fail("project.pbxproj object ids are not 24 hex chars: " + ", ".join(bad_ids))

    handler = (SWIFT_DIR / "BundleSchemeHandler.swift").read_text()
    host = (SWIFT_DIR / "GameWebView.swift").read_text()
    if 'static let scheme = "lowtide"' not in handler or 'static let origin = "lowtide://localhost"' not in handler:
        fail("scheme handler origin changed")
    if "appendingPathComponent(\"dist\"" not in handler:
        fail("scheme handler does not read the bundled dist directory")
    if "WKWebsiteDataStore.default()" not in host or "nonPersistent" in host:
        fail("web view is not using the persistent website data store")
    if "loadFileURL" in host or "https://" in host or "http://" in host:
        fail("web view should load the bundled lowtide:// page, not a remote or file URL")
    content = (SWIFT_DIR / "ContentView.swift").read_text()
    if "Color(uiColor: HarborColor.ui).ignoresSafeArea()" not in content:
        fail("the ink background does not extend outside the safe area")
    if "GameWebView()\n            .ignoresSafeArea()" in content:
        fail("the web view should stay inside the safe area")
    for anchor in ("view.topAnchor", "view.bottomAnchor", "view.leadingAnchor", "view.trailingAnchor"):
        if anchor not in host:
            fail(f"web view is not pinned to {anchor}")
    if "allowsContentJavaScript = true" not in host:
        fail("JavaScript is not explicitly enabled")

    check_web_graph(files)
    check_javascript()
    check_copy_script(files)
    check_icon()

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"ok: {len(files)} bundled files referenced, linked, and copied")
    return 0


def check_web_graph(files: list[str]) -> None:
    available = set(files)
    html = (DIST / "index.html").read_text()
    if not html.lstrip().lower().startswith("<!doctype html>"):
        fail("index.html is missing a doctype")
    if html.count("<") == 0 or not balanced_html(html):
        fail("index.html is not well-formed")
    if 'type="module"' not in html or 'src="rpg.mjs"' not in html:
        fail("index.html does not load rpg.mjs as a module")
    if "viewport-fit=cover" not in html:
        fail("index.html is missing the mobile viewport")

    refs = re.findall(r'''(?:src|href)=["']([^"']+)["']''', html)
    for ref in refs:
        if ref.startswith(("data:", "http:", "https:", "#")):
            if ref.startswith(("http:", "https:")):
                fail(f"index.html links to a remote URL: {ref}")
            continue
        if ref not in available:
            fail(f"index.html reference is not in the bundle: {ref}")

    for sheet in ("rpg.css", "arcade.css"):
        text = (DIST / sheet).read_text()
        if text.count("{") != text.count("}"):
            fail(f"{sheet} has unbalanced braces")
        for raw in re.findall(r"url\(([^)]+)\)", text):
            target = raw.strip().strip("'\"")
            if target.startswith(("data:", "http:", "https:")):
                fail(f"{sheet} uses a remote url: {target}")
                continue
            resolved = pathlib.PurePosixPath(sheet).parent.joinpath(target).as_posix()
            if resolved not in available:
                fail(f"{sheet} url does not resolve: {target} -> {resolved}")

    seen = set()

    def walk_module(rel: str) -> None:
        if rel in seen:
            return
        if rel not in available:
            fail(f"missing module {rel}")
            return
        seen.add(rel)
        text = (DIST / rel).read_text()
        for spec in re.findall(r"""(?:from|import)\s+['"]([^'"]+)['"]""", text):
            if spec.startswith(("http:", "https:")):
                fail(f"{rel} imports a remote module: {spec}")
                continue
            if not spec.startswith("."):
                fail(f"{rel} has a non-relative import: {spec}")
                continue
            nxt = pathlib.PurePosixPath(rel).parent.joinpath(spec).as_posix()
            walk_module(nxt)

    walk_module("rpg.mjs")
    for name in ("rpg-model.mjs", "engine.mjs", "pieces.mjs"):
        if name not in seen:
            fail(f"rpg.mjs never reaches {name}")

    ids = set(re.findall(r'''id=["']([^"']+)["']''', html))
    script = (DIST / "rpg.mjs").read_text()
    direct = set(re.findall(r"""\$\(['"]([^'"]+)['"]\)""", script))
    indirect_blocks = re.findall(r"for\s*\(const id of \[([^\]]+)\]\)\s*\$\(id\)", script)
    for block in indirect_blocks:
        direct.update(re.findall(r"'([^']+)'", block))
    absent = sorted(direct - ids)
    if absent:
        fail("rpg.mjs looks up missing elements: " + ", ".join(absent))
    if "low-tide-guild-v1" not in script:
        fail("save key low-tide-guild-v1 is missing")


def balanced_html(html: str) -> bool:
    void = {
        "area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "source", "track", "wbr",
    }
    stack: list[str] = []
    saw_tag = False
    for match in re.finditer(r"<!--.*?-->|<!doctype[^>]*>|<(/?)\s*([a-zA-Z0-9]+)\b([^>]*)>", html, flags=re.I | re.S):
        if match.group(0).startswith("<!"):
            continue
        saw_tag = True
        closing, name, attrs = match.group(1), match.group(2).lower(), match.group(3)
        if name in void:
            continue
        if attrs.rstrip().endswith("/") or closing:
            if closing:
                if not stack or stack[-1] != name:
                    return False
                stack.pop()
            continue
        stack.append(name)
    return not stack and saw_tag


def check_javascript() -> None:
    for path in sorted(DIST.glob("*.mjs")):
        result = subprocess.run(["node", "--check", str(path)], capture_output=True, text=True)
        if result.returncode != 0:
            fail(f"node --check failed for {path.name}: {result.stderr.strip()}")


def check_copy_script(files: list[str]) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        env = {
            "SRCROOT": str(IOS),
            "TARGET_BUILD_DIR": tmp,
            "UNLOCALIZED_RESOURCES_FOLDER_PATH": "LowTide.app",
            "PATH": "/usr/bin:/bin",
        }
        result = subprocess.run(["/bin/sh", str(COPY_SCRIPT)], capture_output=True, text=True, env=env)
        if result.returncode != 0:
            fail(f"copy script failed: {result.stderr.strip()}")
            return
        copied = sorted(
            path.relative_to(pathlib.Path(tmp) / "LowTide.app" / "dist").as_posix()
            for path in (pathlib.Path(tmp) / "LowTide.app" / "dist").rglob("*")
            if path.is_file()
        )
        if copied != files:
            fail(f"copied bundle {copied} != dist {files}")


def check_icon() -> None:
    icon = SWIFT_DIR / "Assets.xcassets" / "AppIcon.appiconset" / "AppIcon.png"
    data = icon.read_bytes()
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        fail("AppIcon.png is not a PNG")
        return
    # IHDR width/height
    if data[12:16] != b"IHDR":
        fail("AppIcon.png is missing IHDR")
        return
    width = int.from_bytes(data[16:20], "big")
    height = int.from_bytes(data[20:24], "big")
    if (width, height) != (1024, 1024):
        fail(f"AppIcon.png is {width}x{height}, expected 1024x1024")
    contents = (icon.parent / "Contents.json").read_text()
    if "AppIcon.png" not in contents or "1024x1024" not in contents:
        fail("AppIcon contents do not reference the 1024 image")
    launch = SWIFT_DIR / "Assets.xcassets" / "LaunchBackground.colorset" / "Contents.json"
    if "LaunchBackground" not in str(launch) or not launch.is_file():
        fail("LaunchBackground color set is missing")


if __name__ == "__main__":
    sys.exit(main())
