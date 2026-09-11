#!/usr/bin/env python3
"""Build a guarded static GitHub Pages snapshot of The Green Tank.

The current ChatGPT Green Tank site is the development/update source. The
version 51 portable deployment backup is the baseline. This script requires the
exact known version 51 route and research-file set and refuses removals or
unexpected additions.
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
BACKUP_SHA256 = "8c9fa9978f953917d76067e5bfbedb0acedcf17d974bb74c84b22613d73e74bb"
BACKUP_LABEL = "The_Green_Tank_Development_Backup_v51_2026-09-11.zip"

ROUTES = [
    "/",
    "/library",
    "/finances",
    "/finances/universal-payment-and-shared-growth",
    "/psy-chology",
    "/psy-chology/learning-is-a-matter-of-perspective",
    "/psy-chology/ocd-to-curl",
    "/music",
    "/music/knots-untying-through-perspective",
    "/music/knots-1",
    "/simulators",
    "/press",
    "/submit",
    "/phantom-concorde",
    "/climate-technology/bubble-butt",
    "/economic-fairness/universal-basic-income",
    "/social-technology",
    "/social-technology/care-for-those-who-care-for-us",
    "/social-technology/drugs-and-society",
    "/social-technology/drugs-and-society/drug-knowledge-body-autonomy-and-patient-choice",
    "/social-technology/friendship-love-respect",
    "/social-technology/friendship-two",
    "/social-technology/inner-and-outer-world",
    "/social-technology/lion-king-or-big-cat",
    "/social-technology/monkey-banana",
    "/social-technology/perception-learning-expansion",
    "/social-technology/psy-body-psychology-communication",
    "/social-technology/voting-without-fear",
    "/social-technology/health-systems-and-patient-choice",
]

BASELINE_LIBRARY_RESEARCH = {
    "/research/Affordable_Green_Security_China_UK_Paper.docx",
    "/research/Alex_Anderson_Alice_Emotion_and_Feeling_Technology.docx",
    "/research/Alex_Anderson_Alice_Emotion_and_Feeling_Technology.pdf",
    "/research/Alex_Anderson_Alice_Emotion_and_Feeling_Technology.pptx",
    "/research/Alex_Anderson_Concordance_Administration_V1.docx",
    "/research/Alex_Anderson_Concordance_Administration_V1.pdf",
    "/research/Alex_Anderson_From_Prohibition_to_Regulation_Revised_2026.docx",
    "/research/Alex_Anderson_From_Prohibition_to_Regulation_Revised_2026.pdf",
    "/research/Alex_Anderson_From_Punishment_to_Care_Revised_2026.docx",
    "/research/Alex_Anderson_From_Punishment_to_Care_Revised_2026.pdf",
    "/research/Alex_Anderson_Full_Submission_to_Prime_Minister.pdf",
    "/research/Alex_Anderson_Guardians_Not_Enforcers_UK_Policy_Paper.docx",
    "/research/Alex_Anderson_Guardians_Not_Enforcers_UK_Policy_Paper.pdf",
    "/research/Alex_Anderson_How_Fear_Can_Be_Turned_Into_Far_Left_Authoritarianism.docx",
    "/research/Alex_Anderson_How_Fear_Can_Be_Turned_Into_Far_Left_Authoritarianism.pdf",
    "/research/Alex_Anderson_How_Fear_Can_Be_Turned_Into_Far_Right_Extremism.docx",
    "/research/Alex_Anderson_How_Fear_Can_Be_Turned_Into_Far_Right_Extremism.pdf",
    "/research/Alex_Anderson_Neighbourhood_Communal_Recycling_Bins_Reconciled.docx",
    "/research/Alex_Anderson_Neighbourhood_Communal_Recycling_Bins_Reconciled.pdf",
    "/research/Alex_Anderson_No_More_Landlords_Mortgage.docx",
    "/research/Alex_Anderson_No_More_Landlords_Mortgage.pdf",
    "/research/Alex_Anderson_Peoples_European_Reconstruction_Programme.pdf",
    "/research/Alex_Anderson_Peoples_European_Reconstruction_Programme.pptx",
    "/research/Alex_Anderson_Stop_Refrigerating_The_Aisle.docx",
    "/research/Alex_Anderson_Stop_Refrigerating_The_Aisle.pdf",
    "/research/Alex_Anderson_Stop_Refrigerating_The_Aisle.pptx",
    "/research/Alex_Anderson_The_Ladder_Prison_Reform_Proposal.docx",
    "/research/Alex_Anderson_The_Ladder_Prison_Reform_Proposal.pdf",
    "/research/Alex_Anderson_Trust_Is_The_Temple_Of_Medicine_UK_Evidence_Based_Submission.pdf",
    "/research/Alex_Anderson_Words_That_Trap_Functions.docx",
    "/research/Alex_Anderson_Words_That_Trap_Functions.pdf",
    "/research/Alex_Anderson_You_Cant_Expect_to_Resolve_Conflict_If_You_Come_Dressed_as_It.docx",
    "/research/Alex_Anderson_You_Cant_Expect_to_Resolve_Conflict_If_You_Come_Dressed_as_It.pdf",
    "/research/Bubble_Butt_Chemistry_Capture_Concept.png",
    "/research/Bubble_Butt_Retrofit_Concept.png",
    "/research/Enough_A_Democratic_Wealth_Ceiling_for_Tom.docx",
    "/research/Enough_A_Democratic_Wealth_Ceiling_for_Tom.pdf",
    "/research/Help_First_Policing_Figure_1_Aid_and_Safety_Tools.png",
    "/research/Help_First_Policing_Figure_2_Uniform_Concept.png",
    "/research/How_Fear_Can_Be_Turned_Into_Far_Right_Extremism_Infographic.png",
    "/research/How_Fear_Can_Be_Turned_Into_Far_Left_Authoritarianism_Infographic.png",
    "/research/Letter_to_President_Xi_Jinping_Bilingual.pdf",
    "/research/PHANTOM_CONCORDE_Gate_1_Research_Pack.zip",
    "/research/UK_Neighbourhood_Communal_Bin_Simulation_Reconciled.xlsx",
    "/research/UK_Perennial_Resilience_Plan_2026.pptx",
    "/research/UK_Perennial_Resilience_Plan_Technical_Proposal_2026.docx",
    "/research/LOVE-0_Machine-Neutral_Love_Module_v0.1.docx",
    "/research/LOVE0_Paper_Comparison_Review_Record_1.0.docx",
    "/research/Learning_Is_a_Matter_of_Perspective_v0.1.docx",
    "/research/Learning_Is_a_Matter_of_Perspective_v0.2.docx",
    "/research/Learning_Is_a_Matter_of_Perspective_v0.3.docx",
    "/research/Learning_Is_a_Matter_of_Perspective_v0.3_Supplied_Duplicate.docx",
    "/research/Loss_Is_Not_Nothing_MRRAF.docx",
    "/research/Loss_Is_Not_Nothing_MRRAF.pdf",
    "/research/MRRAF_LOVE0_Integrity.json",
    "/research/MRRAF_LOVE0_Processed.docx",
    "/research/MRRAF_LOVE0_Processed.pdf",
    "/research/MRRAF_LOVE0_Side_by_Side.docx",
    "/research/MRRAF_LOVE0_Side_by_Side.pdf",
    "/research/Monkey_Banana_Page_Map.png",
    "/research/Monkey_Bandana.png",
    "/research/Monkey_Sees_People_Using_Human_Tech.png",
    "/research/People_Trying_to_Be_Monkeys.png",
    "/research/What_the_Monkeys_Let_Us_See.png",
    "/research/Capacity_Uncertainty_Regulation_Loop_CURL_Medical_Hypothesis.docx",
    "/research/Drug_Knowledge_Body_Autonomy_and_Patient_Choice.docx",
    "/research/Drug_Knowledge_Body_Autonomy_and_Patient_Choice.pdf",
    "/research/Universal_Payment_Working_Paper_Stage_1.md",
    "/research/Universal_Payment_Working_Paper_Stage_2.md",
    "/research/Universal_Payment_Working_Paper_Stage_3.md",
    "/research/Universal_Payment_Working_Paper_Stage_4.md",
    "/research/Universal_Payment_and_Shared_Growth_Financial_Policy_v1.docx",
}

EXTRA_BASELINE_PUBLIC_FILES = {
    "/research/Buddha_Net_Simulator_Standalone.html",
    "/research/NHS_Right_to_Choose_Data_Acquisition_Survey.docx",
    "/simulators/Buddha_Net_Simulator_Standalone.html",
}
PUBLIC_ASSETS = {"/favicon.svg", "/og.png", "/file.svg", "/globe.svg", "/window.svg"}
USER_AGENT = "TheGreenTank-GitHub-Mirror/2.0-v51-health-systems-guard"
ATTR_URL_RE = re.compile(r'''(?P<attr>href|src)=(?P<q>["'])(?P<url>[^"']+)(?P=q)''', re.I)
SCRIPT_RE = re.compile(r"<script\b[^>]*>.*?</script\s*>", re.I | re.S)
SCRIPT_PRELOAD_RE = re.compile(r"<link\b(?=[^>]*\bas=[\"']script[\"'])[^>]*>", re.I | re.S)
CLOUDFLARE_CHALLENGE_RE = re.compile(
    r'<script\b[^>]*>'
    r'(?=(?:(?!</script\s*>)[\s\S])*(?:__CF\$cv\$params|challenge-platform/scripts/jsd/main\.js))'
    r'(?:(?!</script\s*>)[\s\S])*</script\s*>',
    re.I,
)
CSS_URL_RE = re.compile(r"url\((?P<q>[\"']?)(?P<url>[^)\"']+)(?P=q)\)", re.I)

MONKEY_BANANA_SCRIPT = r"""
(() => {
  const facts = [
    ["Banana", "Yes—if it is ripe and safe for you."],
    ["Pepper", "Possibly. It is food, but it is still a pepper."],
    ["Squash", "Possibly—after preparing it as squash."],
    ["Melon", "Possibly. Check the fruit, not only the name."],
    ["Passionfruit", "Possibly. Its name describes a variety, not its identity."],
    ["Shallot", "Possibly—but expect an onion relative, not dessert."],
    ["Electrical connector", "No. It carries electrical signals, not lunch."],
    ["Computer storage", "No. Save a file on it; do not serve it for pudding."],
    ["Single-board computer", "No. It computes; it is not produce."],
    ["Telephone", "No—unless somebody has handed you an actual banana as a joke."]
  ];
  const cards = [...document.querySelectorAll(".banana-card")];
  const allButton = document.querySelector(".banana-check-intro > button");
  const opened = new Set();

  function render(index, show) {
    const card = cards[index];
    const answer = card?.querySelector(".banana-card-answer");
    if (!card || !answer) return;
    card.classList.toggle("is-open", show);
    card.setAttribute("aria-expanded", String(show));
    answer.innerHTML = show
      ? "<small>Actually</small><strong>" + facts[index][0] + "</strong><em>" + facts[index][1] + "</em>"
      : "<small>Actually</small><strong>Tap to check</strong>";
    if (show) opened.add(index); else opened.delete(index);
  }

  function updateAllButton() {
    if (!allButton) return;
    const allOpen = opened.size === cards.length;
    allButton.innerHTML = (allOpen ? "Hide the answers" : "Would you eat it?") +
      '<span aria-hidden="true">' + (allOpen ? "↑" : "?") + "</span>";
  }

  cards.forEach((card, index) => {
    card.addEventListener("click", () => {
      render(index, !opened.has(index));
      updateAllButton();
    });
  });

  allButton?.addEventListener("click", () => {
    const show = opened.size !== cards.length;
    cards.forEach((_, index) => render(index, show));
    updateAllButton();
  });
})();
"""


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
    parsed = urlparse(urljoin(base_url, value))
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
    return OUT / "index.html" if route == "/" else OUT / route.strip("/") / "index.html"


def prefixed_path(path: str) -> str:
    return path if path == PREFIX or path.startswith(PREFIX + "/") else PREFIX + path


def patch_html_paths(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        normalized = normalize_same_origin(match.group("url"))
        if normalized is None:
            return match.group(0)
        return f'{match.group("attr")}={match.group("q")}{prefixed_path(normalized)}{match.group("q")}'
    return ATTR_URL_RE.sub(repl, text)


def clean_html(text: str) -> str:
    return patch_html_paths(SCRIPT_PRELOAD_RE.sub("", SCRIPT_RE.sub("", text)))


def collect_same_origin_urls(text: str) -> set[str]:
    urls = set()
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
            q = match.group("q") or ""
            return f"url({q}{prefixed_path(normalized)}{q})"
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
        text = CLOUDFLARE_CHALLENGE_RE.sub("", text)
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
        text = fetch(urljoin(BASE, route)).decode("utf-8", errors="strict")
        original_pages[route] = text
        discovered_urls.update(collect_same_origin_urls(text))
        cleaned = clean_html(text)
        if route == "/social-technology/monkey-banana":
            mirror_script = f"{PREFIX}/assets/monkey-banana.js"
            cleaned = cleaned.replace("</body>", f'<script src="{mirror_script}" defer></script>\n</body>', 1)
        write_bytes(route_output(route), cleaned.encode("utf-8"))
        print(f"mirrored route {route}")

    write_bytes(OUT / "assets" / "monkey-banana.js", MONKEY_BANANA_SCRIPT.encode("utf-8"))

    home = original_pages["/"]
    library = original_pages["/library"]
    required_home = [
        "Before we judge",
        "Thirty-six publications",
        "P—29",
        "P—30",
        "P—31",
        "P—32",
        "P—33",
        "P—34",
        "P—35",
        "P—36",
        "Drugs &amp; Society",
        "NHS Right to Choose",
        "Finances",
        "Universal Payment and Shared Growth",
        "Psy-chology",
        "Loss Is Not Nothing",
        "Learning Is a Matter of Perspective",
        "Monkey Banana",
        "OCD to CURL",
        "Simulators",
        "https://ministryofducks.github.io/",
        ">MOD<",
    ]
    missing_home = [m for m in required_home if m not in home]
    if missing_home:
        raise RuntimeError(f"Dev homepage lost expected v51 structure: {missing_home}")

    required_library = [
        "Release 26",
        "36 publications",
        "73 public files",
        "P—29",
        "P—30",
        "P—31",
        "P—32",
        "P—33",
        "P—34",
        "P—35",
        "P—36",
        "Drugs &amp; Society",
        "Health Systems and Patient Choice",
        "NHS Right to Choose",
        "Finances",
        "Universal Payment and Shared Growth",
        "Psy-chology",
        "Loss Is Not Nothing",
        "Learning Is a Matter of Perspective",
        "Monkey Banana",
        "OCD to CURL",
        "Voting Without Fear",
        "Friendship Two - From Ducks to Humans",
    ]
    missing_library = [m for m in required_library if m not in library]
    if missing_library:
        raise RuntimeError(f"Dev library lost expected v51 structure: {missing_library}")

    music = original_pages["/music"]
    required_music = [
        "Hear the influence. Keep the choice.",
        "Mini Knots – Let Me Untie You Tuo",
        "/music/knots-untying-through-perspective",
        "/music/knots-1",
        "Six stages of one developing experiment",
        "CC0 — No Rights Reserved",
    ]
    missing_music = [m for m in required_music if m not in music]
    if missing_music:
        raise RuntimeError(f"Dev Music page lost expected version 49 structure: {missing_music}")

    journey = original_pages["/music/knots-untying-through-perspective"]
    required_journey = [
        "Untying Through Perspective",
        "Mini Knots – Let Me Untie You Tuo",
        "dynamic children’s book",
        "60 recordings",
        "CC0 — No Rights Reserved",
        "knots-Let-me-untie-you",
        "knots-let-me-auntie-uoo-say-hello",
        "knots-let-me-untie-you-3",
        "knots-pop-say-hello-a",
        "knots-commercial-Let-me-untie-you",
        "knots-Universal-Let-me-untie-you",
    ]
    missing_journey = [m for m in required_journey if m not in journey]
    if missing_journey:
        raise RuntimeError(f"Knots chronology verification failed: {missing_journey}")

    protocol = original_pages["/music/knots-1"]
    required_protocol = [
        "KNOTS/1.0",
        "prompt-injection resistance",
        "not</strong> a complete technical security solution",
        "Emotion and feeling are not stripped away",
        "automatic_response != verified_truth",
        "input → internal state → test → decision → action → feedback",
    ]
    missing_protocol = [m for m in required_protocol if m not in protocol]
    if missing_protocol:
        raise RuntimeError(f"KNOTS/1.0 verification failed: {missing_protocol}")

    social = original_pages["/social-technology"]
    required_social = [
        "Technology is also",
        "Drugs:",
        "Evidence, Experience &amp; Supply.",
        "Health Systems",
        "What happens to NHS Right to Choose funding after referral?",
        "/social-technology/drugs-and-society",
        "/social-technology/health-systems-and-patient-choice",
    ]
    missing_social = [m for m in required_social if m not in social]
    if missing_social:
        raise RuntimeError(f"Social Technology verification failed: {missing_social}")

    drugs = original_pages["/social-technology/drugs-and-society"]
    required_drugs = [
        "Four kinds of knowledge.",
        "Drug Knowledge, Body Autonomy and Patient Choice",
        "How fentanyl is making its way to UK streets",
        "Investigation announced · findings not yet published",
        "What happens to NHS Right to Choose funding after referral?",
        "/social-technology/drugs-and-society/drug-knowledge-body-autonomy-and-patient-choice",
        "/social-technology/health-systems-and-patient-choice",
    ]
    missing_drugs = [m for m in required_drugs if m not in drugs]
    if missing_drugs:
        raise RuntimeError(f"Drugs & Society verification failed: {missing_drugs}")

    drug_paper = original_pages[
        "/social-technology/drugs-and-society/drug-knowledge-body-autonomy-and-patient-choice"
    ]
    required_drug_paper = [
        "P—36 · discussion draft",
        "From punishment to care",
        "A signal is not proof.",
        "Transformation,",
        "not abolition.",
        "Drug_Knowledge_Body_Autonomy_and_Patient_Choice.pdf",
        "Drug_Knowledge_Body_Autonomy_and_Patient_Choice.docx",
    ]
    missing_drug_paper = [m for m in required_drug_paper if m not in drug_paper]
    if missing_drug_paper:
        raise RuntimeError(f"Drug paper verification failed: {missing_drug_paper}")

    health_study = original_pages["/social-technology/health-systems-and-patient-choice"]
    required_health_study = [
        "Study in formation",
        "Follow public money through",
        "private provision.",
        "Five links must remain connected.",
        "A suspicion is not a finding.",
        "NHS Right to Choose Data Acquisition Survey",
        "NHS_Right_to_Choose_Data_Acquisition_Survey.docx",
        "does not establish financial loss, fraud, unlawful billing",
    ]
    missing_health_study = [m for m in required_health_study if m not in health_study]
    if missing_health_study:
        raise RuntimeError(f"Health Systems study verification failed: {missing_health_study}")

    research_urls = {
        normalized
        for match in ATTR_URL_RE.finditer(library)
        if (normalized := normalize_same_origin(match.group("url")))
        and normalized.startswith("/research/")
    }
    removed = sorted(BASELINE_LIBRARY_RESEARCH - research_urls)
    added = sorted(research_urls - BASELINE_LIBRARY_RESEARCH)
    if removed:
        raise RuntimeError(f"Research files were removed unexpectedly: {removed}")
    if added:
        raise RuntimeError(f"Unexpected research files were added: {added}")
    print("Version 51 research library file set verified unchanged")

    asset_urls = {
        u for u in discovered_urls
        if u.startswith(("/_next/", "/assets/", "/research/", "/simulators/")) or u in PUBLIC_ASSETS
    }
    asset_urls.update(PUBLIC_ASSETS)
    asset_urls.update(research_urls)
    asset_urls.update(EXTRA_BASELINE_PUBLIC_FILES)

    seen: set[str] = set()
    for asset in sorted(asset_urls):
        save_asset(asset, seen)
        if asset.startswith("/research/"):
            print(f"mirrored research file {asset.rsplit('/', 1)[-1]}")

    research_dir = OUT / "research"
    research_files = sorted(p for p in research_dir.iterdir() if p.is_file()) if research_dir.exists() else []
    extra_research_count = sum(path.startswith("/research/") for path in EXTRA_BASELINE_PUBLIC_FILES)
    expected_research_folder_count = len(research_urls) + extra_research_count
    if len(research_files) != expected_research_folder_count:
        raise RuntimeError(
            f"Expected {expected_research_folder_count} public/research files; found {len(research_files)}"
        )

    simulator_file = OUT / "simulators" / "Buddha_Net_Simulator_Standalone.html"
    if not simulator_file.is_file():
        raise RuntimeError("Standalone Buddha Net simulator was not mirrored")

    stylesheets = sorted(OUT.rglob("*.css"))
    if not stylesheets:
        raise RuntimeError("No stylesheet was mirrored; refusing an unstyled deployment")

    presentation_assets = [
        p for p in OUT.rglob("*")
        if p.is_file() and ("_next" in p.parts or "assets" in p.parts or p.name in {x.lstrip('/') for x in PUBLIC_ASSETS})
    ]
    if not presentation_assets:
        raise RuntimeError("No presentation assets were mirrored; refusing an incomplete deployment")

    manifest_files = {}
    for path in sorted(p for p in OUT.rglob("*") if p.is_file()):
        rel = path.relative_to(OUT).as_posix()
        manifest_files[rel] = {"bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}

    manifest = {
        "source": BASE,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "github_pages_prefix": PREFIX,
        "backup_reference": BACKUP_LABEL,
        "backup_reference_sha256": BACKUP_SHA256,
        "routes": ROUTES,
        "baseline_library_research_count": len(BASELINE_LIBRARY_RESEARCH),
        "library_linked_research_count": len(research_urls),
        "unexpected_library_research": added,
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
        f"{len(research_files)} total public/research files, "
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
