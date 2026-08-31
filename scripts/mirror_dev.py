#!/usr/bin/env python3
"""Build a self-contained static GitHub Pages snapshot from the Green Tank dev site.

The ChatGPT Green Tank site is the development/update source. The manually supplied
v36 backup (31 Aug 2026) is the integrity reference for expected routes and public
files. The script mirrors public routes/downloads/assets, removes framework JS so
GitHub Pages can serve plain static HTML, rewrites internal paths for the repository
prefix, and refuses to deploy when the live dev site does not match the backup's
published structure.
"""

from __future__ import annotations

import hashlib
import html
import json
import re
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse
from urllib.request import Request, urlopen

BASE = "https://the-green-tank.alexiscoderpenguy.chatgpt.site"
BASE_HOST = urlparse(BASE).netloc
PREFIX = "/Thegreentank-deployment-2"
OUT = Path("site")
BACKUP_SHA256 = "c6b86b06128a70b96108c814fa1e9c3f707ece8fd266f3f2c06b1909cd9379cb"
BACKUP_LABEL = "The_Green_Tank_Full_Backup_2026-08-31_v36.zip"

ROUTES = [
    "/",
    "/library",
    "/music",
    "/simulators",
    "/press",
    "/submit",
    "/phantom-concorde",
    "/climate-technology/bubble-butt",
    "/economic-fairness/universal-basic-income",
    "/social-technology/care-for-those-who-care-for-us",
    "/social-technology/friendship-love-respect",
    "/social-technology/inner-and-outer-world",
    "/social-technology/lion-king-or-big-cat",
    "/social-technology/perception-learning-expansion",
    "/social-technology/psy-body-psychology-communication",
]

# v36 contains 45 library-linked research files plus a duplicate copy of the
# standalone Buddha Net simulator in public/research. Preserve both public copies.
EXTRA_BACKUP_PUBLIC_FILES = {
    "/research/Buddha_Net_Simulator_Standalone.html",
    "/simulators/Buddha_Net_Simulator_Standalone.html",
}
PUBLIC_ASSETS = {"/favicon.svg", "/og.png", "/file.svg", "/globe.svg", "/window.svg"}
USER_AGENT = "TheGreenTank-GitHub-Mirror/1.3-v36 (+public backup deployment)"
ATTR_URL_RE = re.compile(r'''(?P<attr>href|src)=(?P<q>["'])(?P<url>[^"']+)(?P=q)''', re.I)
SCRIPT_RE = re.compile(r"<script\b[^>]*>.*?</script\s*>", re.I | re.S)
SCRIPT_PRELOAD_RE = re.compile(r"<link\b(?=[^>]*\bas=[\"']script[\"'])[^>]*>", re.I | re.S)
CSS_URL_RE = re.compile(r"url\((?P<q>[\"']?)(?P<url>[^)\"']+)(?P=q)\)", re.I)


def fetch(url: str, attempts: int = 3) -> bytes:
    last = None
    for attempt in range(1, attempts + 1):
        try:
            req = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
            with urlopen(req, timeout=45) as response:
                if response.status >= 400:
                    raise RuntimeError(f"HTTP {response.status}: {url}")
                return response.read()
        except Exception as exc:  # noqa: BLE001
            last = exc
            if attempt < attempts:
                time.sleep(attempt * 2)
    raise RuntimeError(f"Could not fetch {url}: {last}")


def normalize_same_origin(value: str, base_url: str = BASE) -> str | None:
    value = html.unescape(value).strip()
    if not value or value.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
        return None
    absolute = urljoin(base_url, value)
    parsed = urlparse(absolute)
    if parsed.scheme not in {"http", "https"} or parsed.netloc != BASE_HOST:
        return None
    path = parsed.path or "/"
    if parsed.query:
        path += "?" + parsed.query
    return path


def local_path_for_url(path: str) -> Path:
    clean = unquote(path.split("?", 1)[0].split("#", 1)[0]).lstrip("/")
    return OUT / clean


def write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def route_output(route: str) -> Path:
    if route == "/":
        return OUT / "index.html"
    return OUT / route.strip("/") / "index.html"


def prefixed_path(path: str) -> str:
    if path == PREFIX or path.startswith(PREFIX + "/"):
        return path
    return PREFIX + path


def patch_html_paths(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        normalized = normalize_same_origin(match.group("url"))
        if normalized is None:
            return match.group(0)
        return f'{match.group("attr")}={match.group("q")}{prefixed_path(normalized)}{match.group("q")}'

    return ATTR_URL_RE.sub(repl, text)


def clean_html(text: str) -> str:
    text = SCRIPT_RE.sub("", text)
    text = SCRIPT_PRELOAD_RE.sub("", text)
    return patch_html_paths(text)


def collect_same_origin_urls(text: str) -> set[str]:
    urls: set[str] = set()
    for match in ATTR_URL_RE.finditer(text):
        normalized = normalize_same_origin(match.group("url"))
        if normalized:
            urls.add(normalized)
    return urls


def patch_css_paths(text: str, css_source_url: str) -> tuple[str, set[str]]:
    nested: set[str] = set()

    def repl(match: re.Match[str]) -> str:
        value = match.group("url")
        normalized = normalize_same_origin(value, base_url=css_source_url)
        if normalized is None:
            return match.group(0)
        nested.add(normalized)
        if value.startswith("/") or value.startswith(BASE):
            quote = match.group("q") or ""
            return f"url({quote}{prefixed_path(normalized)}{quote})"
        return match.group(0)

    return CSS_URL_RE.sub(repl, text), nested


def save_asset(path: str, seen: set[str]) -> None:
    normalized = normalize_same_origin(path)
    if normalized is None or normalized in seen:
        return
    seen.add(normalized)

    source_url = urljoin(BASE, normalized)
    data = fetch(source_url)
    dest = local_path_for_url(normalized)

    if dest.suffix.lower() == ".css":
        text = data.decode("utf-8", errors="replace")
        patched, nested = patch_css_paths(text, source_url)
        write_bytes(dest, patched.encode("utf-8"))
        for nested_url in sorted(nested):
            save_asset(nested_url, seen)
    elif dest.suffix.lower() in {".html", ".htm"}:
        text = data.decode("utf-8", errors="replace")
        write_bytes(dest, patch_html_paths(text).encode("utf-8"))
    else:
        write_bytes(dest, data)


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    original_pages: dict[str, str] = {}
    discovered_urls: set[str] = set()

    for route in ROUTES:
        raw = fetch(urljoin(BASE, route))
        text = raw.decode("utf-8", errors="strict")
        original_pages[route] = text
        discovered_urls.update(collect_same_origin_urls(text))
        write_bytes(route_output(route), clean_html(text).encode("utf-8"))
        print(f"mirrored route {route}")

    home = original_pages["/"]
    library = original_pages["/library"]
    required_home = [
        "Before we judge",
        "Twenty-eight publications",
        "Forty-five research files",
        "P—23",
        "Simulators",
    ]
    missing = [marker for marker in required_home if marker not in home]
    if missing:
        raise RuntimeError(f"Dev homepage does not match v36 markers: {missing}")

    required_library = ["Release 17", "28 publications", "45 public files", "P—27", "P—28"]
    missing_library = [marker for marker in required_library if marker not in library]
    if missing_library:
        raise RuntimeError(f"Dev library does not match v36 markers: {missing_library}")

    research_urls = sorted(
        {
            normalized
            for match in ATTR_URL_RE.finditer(library)
            if (normalized := normalize_same_origin(match.group("url")))
            and normalized.startswith("/research/")
        }
    )
    if len(research_urls) != 45:
        raise RuntimeError(f"Expected 45 library-linked public research files; found {len(research_urls)}")

    asset_urls = {
        u for u in discovered_urls
        if u.startswith(("/_next/", "/assets/", "/research/", "/simulators/")) or u in PUBLIC_ASSETS
    }
    asset_urls.update(PUBLIC_ASSETS)
    asset_urls.update(research_urls)
    asset_urls.update(EXTRA_BACKUP_PUBLIC_FILES)

    seen: set[str] = set()
    for asset in sorted(asset_urls):
        save_asset(asset, seen)
        if asset.startswith("/research/"):
            print(f"mirrored research file {asset.rsplit('/', 1)[-1]}")
        elif asset.startswith("/simulators/"):
            print(f"mirrored simulator file {asset.rsplit('/', 1)[-1]}")

    research_dir = OUT / "research"
    research_files = sorted(p for p in research_dir.iterdir() if p.is_file()) if research_dir.exists() else []
    if len(research_files) != 46:
        raise RuntimeError(
            f"Expected all 46 v36 public/research files (45 library files + simulator duplicate); "
            f"found {len(research_files)}"
        )

    simulator_file = OUT / "simulators" / "Buddha_Net_Simulator_Standalone.html"
    if not simulator_file.is_file():
        raise RuntimeError("Standalone Buddha Net simulator was not mirrored")

    stylesheets = sorted(OUT.rglob("*.css"))
    if not stylesheets:
        raise RuntimeError("No stylesheet was mirrored; refusing an unstyled deployment")

    presentation_assets = [
        p for p in OUT.rglob("*")
        if p.is_file()
        and (
            "_next" in p.parts
            or "assets" in p.parts
            or p.name in {x.lstrip('/') for x in PUBLIC_ASSETS}
        )
    ]
    if not presentation_assets:
        raise RuntimeError("No presentation assets were mirrored; refusing an incomplete deployment")

    manifest_files = {}
    for path in sorted(p for p in OUT.rglob("*") if p.is_file()):
        rel = path.relative_to(OUT).as_posix()
        manifest_files[rel] = {
            "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }

    manifest = {
        "source": BASE,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "github_pages_prefix": PREFIX,
        "backup_reference": BACKUP_LABEL,
        "backup_reference_sha256": BACKUP_SHA256,
        "routes": ROUTES,
        "library_linked_research_count": len(research_urls),
        "public_research_folder_count": len(research_files),
        "standalone_simulator": "simulators/Buddha_Net_Simulator_Standalone.html",
        "stylesheet_count": len(stylesheets),
        "presentation_asset_count": len(presentation_assets),
        "integrity_markers": required_home + required_library,
        "files": manifest_files,
    }
    write_bytes(OUT / "mirror-manifest.json", (json.dumps(manifest, indent=2) + "\n").encode())
    write_bytes(OUT / ".nojekyll", b"")

    print(
        f"ready: {len(ROUTES)} routes, {len(research_urls)} library research files, "
        f"{len(research_files)} total public/research files, standalone simulator present, "
        f"{len(stylesheets)} stylesheets, {len(presentation_assets)} presentation assets, "
        f"{len(manifest_files)} files"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"mirror failed: {exc}", file=sys.stderr)
        raise
