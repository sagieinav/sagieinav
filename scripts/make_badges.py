#!/usr/bin/env python3
"""Render every tech-stack badge once with shields.io and save it under assets/badges/.

The README points at these local SVGs, so the profile never depends on shields.io
being up, and badges whose logo Simple Icons doesn't have (Microsoft products, Hilt)
use an SVG from assets/icons/ instead.

Run from the repo root:  python3 scripts/make_badges.py
"""
import base64
import pathlib
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
ICONS = ROOT / "assets" / "icons"
OUT = ROOT / "assets" / "badges"
BG = "30363D"  # GitHub dark-mode border gray: blends into both themes

# (file name, label, logo). Logo is either ("si", simple-icons slug, hex color)
# or ("file", icon file name in assets/icons/).
BADGES = [
    ("kotlin", "Kotlin", ("si", "kotlin", "7F52FF")),
    ("java", "Java", ("si", "openjdk", "ED8B00")),
    ("python", "Python", ("si", "python", "4B8BBE")),
    ("c", "C", ("si", "c", "A8B9CC")),
    ("bash", "Bash", ("si", "gnubash", "4EAA25")),
    ("android", "Android", ("si", "android", "3DDC84")),
    ("compose", "Jetpack Compose", ("si", "jetpackcompose", "4285F4")),
    ("coroutines", "Coroutines & Flow", ("si", "kotlin", "7F52FF")),
    ("hilt", "Hilt", ("file", "hilt.svg")),
    ("material3", "Material 3", ("si", "materialdesign", "FFFFFF")),
    ("firebase", "Firebase", ("si", "firebase", "FFCA28")),
    ("postgresql", "PostgreSQL", ("si", "postgresql", "4169E1")),
    ("git", "Git", ("si", "git", "F05032")),
    ("gradle", "Gradle", ("si", "gradle", "FFFFFF")),
    ("docker", "Docker", ("si", "docker", "2496ED")),
    ("junit5", "JUnit 5", ("si", "junit5", "25A162")),
    ("azure", "Azure", ("file", "azure.svg")),
    ("m365", "Microsoft 365", ("file", "microsoft-365.svg")),
    ("powershell", "PowerShell", ("file", "powershell.svg")),
    ("active-directory", "Active Directory", ("file", "active-directory.svg")),
    ("intune", "Intune", ("file", "intune.svg")),
    # contact
    ("linkedin", "LinkedIn", ("file", "linkedin.svg")),
    ("email", "Email", ("si", "gmail", "EA4335")),
]


def badge_url(label, logo):
    # shields path syntax: "-" and "_" in the label must be doubled
    text = urllib.parse.quote(label.replace("-", "--").replace("_", "__"))
    params = {"style": "flat"}
    if logo[0] == "si":
        params["logo"], params["logoColor"] = logo[1], logo[2]
    else:
        svg = (ICONS / logo[1]).read_bytes()
        params["logo"] = "data:image/svg+xml;base64," + base64.b64encode(svg).decode()
    return f"https://img.shields.io/badge/{text}-{BG}?{urllib.parse.urlencode(params)}"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, label, logo in BADGES:
        req = urllib.request.Request(badge_url(label, logo), headers={"User-Agent": "badge-builder"})
        svg = urllib.request.urlopen(req, timeout=30).read()
        if b"<image" not in svg:
            raise SystemExit(f"{name}: shields returned a badge with no logo")
        (OUT / f"{name}.svg").write_bytes(svg)
        print(f"ok  {name}")


if __name__ == "__main__":
    main()
