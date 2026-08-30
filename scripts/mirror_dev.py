#!/usr/bin/env python3
"""Build a static GitHub Pages snapshot from the Green Tank dev site.

The ChatGPT Green Tank site is the development/update source. This script mirrors
all public routes and all research downloads, strips framework JavaScript so the
snapshot works as plain static HTML, rewrites internal root paths for the GitHub
Pages repository prefix, and fails if expected integrity markers are missing.
"""

from __future__ import annotations

import hashlib
import html
import json
import os
import re
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse
from urllib.request import Request, urlopen

BASE = "https://the-green-tank.alexiscoderpenguy.chatgpt.site"
PREFIX = "/Thegreentank-deployment-2"
OUT = Path("site")
BACKUP_SHA256 = "3674cf838927e684e3731ed5c792c679a304d30d5ae050a2da549e9130f7e8e3"

ROUTES = [
    "/",
    "/library",
    "/music",
    "/press",
    "/submit",
    "/phantom-concorde",
    "/economic-fairness/universal-basic-income",
    "/social-technology/care-for-those-who-care-for-us",
    "/social-technology/friendship-love-respect",
    "/social-technology/inner-and-outer-world",
    "/social-technology/perception-learning-expansion",
    "/social-technology/psy-body-psychology-communication",
]

USER_AGENT = "TheGreenTank-GitHub-Mirror/1.0 (+public backup deployment)"
ATTR_URL_RE = re.compile(r'''(?P<attr>href|src)=(?P<q>["'])(?P<url>/[^"']*)(?P=q)''', re.I)
SCRIPT_RE = re.compile(r"<script\b[^>]*>.*?</script\s*>", re.I | re.S)
SCRIPT_PRELOAD_RE = re.compile(r"<link\b(?=[^>]*\bas=[\"']script[\"'])[^>]*>", re.I | re.S)
CSS_URL_RE = re.compile(r"url\((?P<q>[\"']?)(?P<url>/[^)\"']+)(?P=q)\)", re.I)


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


def patch_root_paths(text: str) -> str:
    # Root-relative links/assets must include the repository path on GitHub Pages.
    def repl(match: re.Match[str]) -> str:
        url = match.group("url")
        if url.startswith("//") or url.startswith(PREFIX + "/") or url == PREFIX:
            return match.group(0)
        return f'{match.group("attr")}={match.group("q")}{PREFIX}{url}{match.group("q")}'

    return ATTR_URL_RE.sub(repl, text)


def clean_html(text: str) -> str:
    # Static Pages do not need Next/Vinext hydration. Removing framework JS also
    # prevents client-side navigation from requesting server-only RSC endpoints.
    text = SCRIPT_RE.sub("", text)
    text = SCRIPT_PRELOAD_RE.sub("", text)
    return patch_root_paths(text)


def collect_local_urls(text: str) -> set[str]:
    urls: set[str] = set()
    for match in ATTR_URL_RE.finditer(text):
        path = html.unescape(match.group("url"))
        if path.startswith("//"):
            continue
        path = path.split("#", 1)[0]
        if path:
            urls.add(path)
    return urls


def save_asset(path: str, seen: set[str]) -> None:
    path_no_fragment = html.unescape(path).split("#", 1)[0]
    if not path_no_fragment.startswith("/") or path_no_fragment.startswith("//"):
        return
    if path_no_fragment in seen:
        return
    seen.add(path_no_fragment)

    data = fetch(urljoin(BASE, path_no_fragment))
    dest = local_path_for_url(path_no_fragment)

    # Patch root-relative URLs inside stylesheets for the GitHub Pages prefix.
    if dest.suffix.lower() == ".css":
        text = data.decode("utf-8", errors="replace")
        nested = {m.group("url") for m in CSS_URL_RE.finditer(text)}
        text = re.sub(r"url\((['\"]?)/(?!/|Thegreentank-deployment-2/)", rf"url(\1{PREFIX}/", text)
        write_bytes(dest, text.encode("utf-8"))
        for nested_url in nested:
            save_asset(nested_url, seen)
    else:
        write_bytes(dest, data)


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    original_pages: dict[str, str] = {}
    local_urls: set[str] = set()

    for route in ROUTES:
        raw = fetch(urljoin(BASE, route))
        text = raw.decode("utf-8", errors="strict")
        original_pages[route] = text
        local_urls.update(collect_local_urls(text))
        write_bytes(route_output(route), clean_html(text).encode("utf-8"))
        print(f"mirrored route {route}")

    home = original_pages["/"]
    library = original_pages["/library"]
    required_home = [
        "Before we judge",
        "Twenty-six publications",
        "Forty-three downloadable files",
        "P—23",
    ]
    missing = [marker for marker in required_home if marker not in home]
    if missing:
        raise RuntimeError(f"Dev homepage is missing expected current markers: {missing}")
    if "Release 17" not in library:
        raise RuntimeError("Dev library is not Release 17; refusing to publish an older snapshot")

    # The backup contains 43 files under public/research. Require the live public
    # library to expose the same count before deployment.
    research_urls = sorted(
        {
            html.unescape(match.group("url")).split("#", 1)[0]
            for match in ATTR_URL_RE.finditer(library)
            if html.unescape(match.group("url")).startswith("/research/")
        }
    )
    if len(research_urls) != 43:
        raise RuntimeError(f"Expected 43 public research downloads; found {len(research_urls)}")

    # Do not try to fetch navigational routes as binary assets. Fetch framework
    # styles/images plus all research downloads and public image assets.
    asset_urls = {
        u for u in local_urls
        if u.startswith("/_next/")
        or u.startswith("/research/")
        or u in {"/favicon.svg", "/og.png", "/file.svg", "/globe.svg", "/window.svg"}
    }
    asset_urls.update(research_urls)

    seen: set[str] = set()
    for asset in sorted(asset_urls):
        save_asset(asset, seen)
        if asset.startswith("/research/"):
            print(f"mirrored download {asset.rsplit('/', 1)[-1]}")

    # Verify all 43 research files are present on disk.
    research_dir = OUT / "research"
    research_files = sorted(p for p in research_dir.iterdir() if p.is_file()) if research_dir.exists() else []
    if len(research_files) != 43:
        raise RuntimeError(f"Expected 43 downloaded research files on disk; found {len(research_files)}")

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
        "backup_reference_sha256": BACKUP_SHA256,
        "routes": ROUTES,
        "research_download_count": len(research_files),
        "integrity_markers": required_home + ["Release 17"],
        "files": manifest_files,
    }
    write_bytes(OUT / "mirror-manifest.json", (json.dumps(manifest, indent=2) + "\n").encode())
    write_bytes(OUT / ".nojekyll", b"")

    print(f"ready: {len(ROUTES)} routes, {len(research_files)} research downloads, {len(manifest_files)} files")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"mirror failed: {exc}", file=sys.stderr)
        raise
