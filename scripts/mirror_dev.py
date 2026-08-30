#!/usr/bin/env python3
"""Build a self-contained static GitHub Pages snapshot from the Green Tank dev site.

The ChatGPT Green Tank site is the development/update source. This script mirrors
all public routes and all research downloads, removes framework JavaScript so the
snapshot works as plain static HTML, copies same-origin presentation assets, and
rewrites internal paths for the GitHub Pages repository prefix.
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

PUBLIC_ASSETS = {"/favicon.svg", "/og.png", "/file.svg", "/globe.svg", "/window.svg"}
USER_AGENT = "TheGreenTank-GitHub-Mirror/1.1 (+public backup deployment)"
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
        original = match.group("url")
        normalized = normalize_same_origin(original)
        if normalized is None:
            return match.group(0)
        return f'{match.group("attr")}={match.group("q")}{prefixed_path(normalized)}{match.group("q")}'

    return ATTR_URL_RE.sub(repl, text)


def clean_html(text: str) -> str:
    # Static Pages do not need Next/Vinext hydration. Removing framework JS also
    # prevents client-side navigation from requesting server-only RSC endpoints.
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
        # Keep relative CSS URLs relative; patch only root/same-origin absolute ones.
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
        "Twenty-six publications",
        "Forty-three downloadable files",
        "P—23",
    ]
    missing = [marker for marker in required_home if marker not in home]
    if missing:
        raise RuntimeError(f"Dev homepage is missing expected current markers: {missing}")
    if "Release 17" not in library:
        raise RuntimeError("Dev library is not Release 17; refusing to publish an older snapshot")

    research_urls = sorted(
        {
            normalized
            for match in ATTR_URL_RE.finditer(library)
            if (normalized := normalize_same_origin(match.group("url")))
            and normalized.startswith("/research/")
        }
    )
    if len(research_urls) != 43:
        raise RuntimeError(f"Expected 43 public research downloads; found {len(research_urls)}")

    # Framework styles/images and public assets are mirrored locally. Navigational
    # routes are already handled above as HTML rather than fetched as binary assets.
    asset_urls = {
        u for u in discovered_urls
        if u.startswith("/_next/") or u.startswith("/research/") or u in PUBLIC_ASSETS
    }
    asset_urls.update(PUBLIC_ASSETS)
    asset_urls.update(research_urls)

    seen: set[str] = set()
    for asset in sorted(asset_urls):
        save_asset(asset, seen)
        if asset.startswith("/research/"):
            print(f"mirrored download {asset.rsplit('/', 1)[-1]}")

    research_dir = OUT / "research"
    research_files = sorted(p for p in research_dir.iterdir() if p.is_file()) if research_dir.exists() else []
    if len(research_files) != 43:
        raise RuntimeError(f"Expected 43 downloaded research files on disk; found {len(research_files)}")

    # Require at least one presentation asset in addition to the routes/downloads.
    presentation_assets = [
        p for p in OUT.rglob("*")
        if p.is_file() and ("_next" in p.parts or p.name in {x.lstrip('/') for x in PUBLIC_ASSETS})
    ]
    if not presentation_assets:
        raise RuntimeError("No presentation assets were mirrored; refusing a text-only/incomplete deployment")

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
        "presentation_asset_count": len(presentation_assets),
        "integrity_markers": required_home + ["Release 17"],
        "files": manifest_files,
    }
    write_bytes(OUT / "mirror-manifest.json", (json.dumps(manifest, indent=2) + "\n").encode())
    write_bytes(OUT / ".nojekyll", b"")

    print(
        f"ready: {len(ROUTES)} routes, {len(research_files)} research downloads, "
        f"{len(presentation_assets)} presentation assets, {len(manifest_files)} files"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"mirror failed: {exc}", file=sys.stderr)
        raise
