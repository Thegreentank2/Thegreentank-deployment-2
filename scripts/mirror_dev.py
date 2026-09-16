#!/usr/bin/env python3
"""Build a guarded static GitHub Pages snapshot of The Green Tank.

The current ChatGPT Green Tank site is the development/update source. The
version 60 Release 31 portable deployment backup is the baseline. This script requires the
exact known version 60 route and research-file set and refuses removals or
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
BACKUP_SHA256 = "f4b61a9732e764c0d1ee1d1a93aca321c3e8b19d5d4239fb08722deacbfb4773"
BACKUP_LABEL = "The_Green_Tank_Dev_Backup_2026-09-16_v60.zip"
SOURCE_SITE_VERSION = 60
SOURCE_RELEASE = 31
SOURCE_PUBLICATION_COUNT = 41
SOURCE_COMMIT = "dd208817f6bd40d8b4965493ea5408da9ad934ef"

ROUTES = [
    "/",
    "/solutions-now",
    "/solutions-now/evidence",
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
    "/fashion-police",
    "/climate-technology/bubble-butt",
    "/climate-technology/emission-transitive-emission",
    "/economic-fairness/universal-basic-income",
    "/social-technology",
    "/social-technology/democratic-centre",
    "/social-technology/care-for-those-who-care-for-us",
    "/social-technology/drugs-and-society",
    "/social-technology/drugs-and-society/drug-knowledge-body-autonomy-and-patient-choice",
    "/social-technology/friendship-love-respect",
    "/social-technology/friendship-two",
    "/social-technology/friendship-three",
    "/social-technology/inner-and-outer-world",
    "/social-technology/lion-king-or-big-cat",
    "/social-technology/monkey-banana",
    "/social-technology/perception-learning-expansion",
    "/social-technology/psy-body-psychology-communication",
    "/social-technology/voting-without-fear",
    "/social-technology/health-systems-and-patient-choice",
    "/social-technology/justice-and-accountability",
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
    "/research/Alex_Anderson_The_Democratic_Centre_As_A_Shared_Civic_Space.docx",
    "/research/Alex_Anderson_The_Democratic_Centre_As_A_Shared_Civic_Space.pdf",
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
    "/research/Corporate_Manslaughter_UK_Draft.docx",
    "/research/Corporate_Manslaughter_and_Corporate_Homicide_Act_2007.pdf",
    "/research/Corporate_Manslaughter_Act_2007_Explanatory_Notes.pdf",
    "/research/Affordable_Modular_Homes_and_Electric_Mobility_2026_Clear_Prices_v22.pptx",
    "/research/Affordable_Modular_Homes_and_Electric_Mobility_2026_Clear_Prices_v22.pdf",
    "/research/Affordable_Modular_Homes_and_Electric_Mobility_2026_Clear_Prices_v22_Transcript.txt",
    "/research/CL17_Emission_Transitive_Emission_Matrix.xlsx",
    "/research/CL17_Emission_Transitive_Emission_Ongoing_Study.docx",
    "/research/CL17_Emission_Transitive_Emission_Ongoing_Study.pdf",
    "/research/CL17_Emission_Transitive_Emission_Research_Package_2026-09-13.zip",
    "/research/CL17_Supplemental_Interactive_Systems.xlsx",
    "/research/CL17_Supplemental_Investigations.docx",
    "/research/CL17_Supplemental_Investigations.pdf",
    "/research/Emission_Transitive_Emission_Evidence_Review.docx",
    "/research/Emission_Transitive_Emission_Evidence_Review.pdf",
}

EXTRA_BASELINE_PUBLIC_FILES = {
    "/research/Buddha_Net_Simulator_Standalone.html",
    "/research/NHS_Right_to_Choose_Data_Acquisition_Survey.docx",
    "/simulators/Buddha_Net_Simulator_Standalone.html",
}
PUBLIC_ASSETS = {"/favicon.svg", "/og.png", "/file.svg", "/globe.svg", "/window.svg"}
EXPECTED_CONTENT_SHA256 = {
    "/research/Alex_Anderson_The_Democratic_Centre_As_A_Shared_Civic_Space.docx": "bdcb7dc3b65b21d5776dab6f211f7903660bb6f5f963f1f63b295f9eeb403f47",
    "/research/Alex_Anderson_The_Democratic_Centre_As_A_Shared_Civic_Space.pdf": "f0dc594a80c265b8e60af4b9131527d16aba06a00085216887bee628f3dd161b",
    "/research/CL17_Emission_Transitive_Emission_Matrix.xlsx": "85a25fdc985b22976b403aa2a115fc1f42f30d861ee2781add62ad4458859ad2",
    "/research/CL17_Emission_Transitive_Emission_Ongoing_Study.docx": "3b01b578d3c1f037d6c6bcdb7d1dc6ef122f67e14aec451e48b597d34014ec23",
    "/research/CL17_Emission_Transitive_Emission_Ongoing_Study.pdf": "bf4d3c75e2174aeb197d56675500eefb75edbba48dd0c278d9b4593f927d6538",
    "/research/CL17_Emission_Transitive_Emission_Research_Package_2026-09-13.zip": "be0f521261e32d20f8ac23ffb8331de68711488e68fceab7ad68455242693cab",
    "/research/CL17_Supplemental_Interactive_Systems.xlsx": "db30f3faaf17dd7130325447b00770aac48bafc4346a92fcf8743a7010db6dae",
    "/research/CL17_Supplemental_Investigations.docx": "45a50253a941d627552d1abef8200a24e1d905060b91bb199d8b9152b735e8b0",
    "/research/CL17_Supplemental_Investigations.pdf": "e3e5b93ae4c46617f9ca6903178f15c054eb668efce01e42114d72128088b6b1",
    "/research/Emission_Transitive_Emission_Evidence_Review.docx": "eea783e0c7651d594d5d3fb2247da302c33bab46ac8e6c982ccab32587241f07",
    "/research/Emission_Transitive_Emission_Evidence_Review.pdf": "23ff5019fe47a6ff75bcac5f4e6ed31014335fb64182a7c7033b543f3fe69ec7",
    "/research/Corporate_Manslaughter_UK_Draft.docx": "98b52a98ec087adc7603adc1f7a4a48a6d0e545ae6becd68030117514503598b",
    "/research/Corporate_Manslaughter_and_Corporate_Homicide_Act_2007.pdf": "98fa2361402ec919654298f8be4233d4f06fc44cb6f420b229b56890f6e04b9a",
    "/research/Corporate_Manslaughter_Act_2007_Explanatory_Notes.pdf": "e0af0933e5c1485d4c292f70d1fee4d5c650f28e7cfe258bdee4e315e0f7be4e",
    "/research/Affordable_Modular_Homes_and_Electric_Mobility_2026_Clear_Prices_v22.pptx": "3cfd6e8892bdd258280cbaeb05b2db5a49d118d2b36a39eb45f099c6770b3948",
    "/research/Affordable_Modular_Homes_and_Electric_Mobility_2026_Clear_Prices_v22.pdf": "f03b4459f0b14a138f6bbbcd6066fa069cc11348260b2f0293ac76fdf697523f",
    "/research/Affordable_Modular_Homes_and_Electric_Mobility_2026_Clear_Prices_v22_Transcript.txt": "a1ee5b764631e4c944a5b4030df8f94b66e9e544f3f85076f90b1e09832d30bf",
    "/solutions-now/slides/slide-1.webp": "2ec473d54e721e0a4782b6690236c737b9af3c528aef27ccbfc064bff792f900",
    "/solutions-now/slides/slide-2.webp": "2d3c4ca9f35a8b27628f123f1d9d5f3f80a062c27c90c267d1fc4a6c4e62caf7",
    "/solutions-now/slides/slide-3.webp": "c96a27d5501eb409a1bb2484fb6062ba87cfc27d54bd6df2952375cee171b83c",
    "/solutions-now/slides/slide-4.webp": "a6626ac700695bd2147e092240a3a0ee90263e886bfa3c2ec7fff138fb2e0764",
    "/solutions-now/slides/slide-5.webp": "2448c6ac6b55ba576aed1c42058c73646245d22aea667eceb84c5ddedc93c7b3",
    "/solutions-now/slides/slide-6.webp": "3f7ad079268fcff3a24c7946c240a1b3cda286613cca7b7054cf08b44468c246",
    "/solutions-now/slides/slide-7.webp": "76157ce48674dc50b605bfa704bd71bf4e7a04de2a4de4acd45595936789fd5f",
    "/solutions-now/slides/slide-8.webp": "5833bd29099a4507f1443dbace68c1265cc6636ab880975c6403595ebf10394c",
    "/solutions-now/slides/slide-9.webp": "c19fddd00207e71e21f28a5be01293a02399daef8b342d2137afd66857df4a3b",
    "/solutions-now/slides/slide-10.webp": "d83f4c15c38efd9586244e9abdcbc1cfc95902cb0ea30879413acef1258d90c8",
    "/solutions-now/slides/slide-11.webp": "8ac0e2ef609428810162b4c18e32c4300f4ca371e0ab3c770a8cd39370c9bf6f",
    "/solutions-now/slides/slide-12.webp": "ca4c8343b888cb3e03b71be19d5058b2468784380a876ca024dd762d4abcd905",
    "/solutions-now/slides/slide-13.webp": "f3582ebe03c9f30a233300c802a65e5ccf032a03ed7950aa2f269f67704385a8",
    "/solutions-now/slides/slide-14.webp": "56705e0a588d4546d7cb3a9a0a964da530f2743e83730b4ca8329a639d81d35c",
    "/solutions-now/slides/slide-15.webp": "47d50989367866525950b3ec0c16b7ae5a43d52ff6c6adcd274b3f8cb70aee6d",
    "/solutions-now/slides/slide-16.webp": "ae764f7da75d0d85f90d9d900c25cc921d8037c6016442f489c8d21e2bebb3b6",
    "/solutions-now/slides/slide-17.webp": "aa5e91bfdad9a43dce2fad8e0d6f0f317f5d613a36be0542f7303fe3fecbd9d9",
    "/solutions-now/slides/slide-18.webp": "dfbc1ae429c84da09922e7e0719fb6909868876be98224fa1429502ee4e8d871",
    "/solutions-now/slides/slide-19.webp": "7b80a3d49bbc07f2836ad1505f99ced89ff38fd3a625976ff04b145dab728389",
    "/solutions-now/slides/slide-20.webp": "dc012381bda0254915470602dac8438daab640c80572c1994b1de42bc5acbfb2",
    "/solutions-now/slides/slide-21.webp": "e15ded0295aa9134d8786886ae6be540dc21635d69d7d4b9cb0e1bd6119cb945",
    "/solutions-now/slides/slide-22.webp": "16d1f40e41b85a6cf78d4302727b49adc85f466c97962b3b08105c7d46faca2e",
    "/solutions-now/slides/slide-23.webp": "ba7e45630abc2742564d425b1b66f5717f22a8cfa9cce8a2675238f2b00ad1a7",
    "/solutions-now/slides/slide-24.webp": "92ce994be8f261ec918cd200e8a3081eb95e6a2d83b08386d8a0e38067e724e1",
    "/solutions-now/slides/slide-25.webp": "5c3735566bd5469a6d026cf2a0094e9fdcc965c4fa5a9a08f3340cd2f27e43ed",
    "/solutions-now/slides/slide-26.webp": "6fd3a75a296c72fc01baab6941002106706e9af075b69cf37ec475d6780b2abc",
    "/solutions-now/slides/slide-27.webp": "9f4b00a3d952b802d27fa9a804cef604ae69501ecc51785dbee1c8f17fd184bc",
    "/solutions-now/slides/slide-28.webp": "f42dd62c5a86c9e8aa1c597489902d25df6a626b0bd849d2062b2c5985b6d5b1",
    "/solutions-now/slides/slide-29.webp": "b4b9a96538b1b056c5f694ec164f75fab73e6cd46aaf9131f0eb4715b6010c47",
    "/solutions-now/slides/slide-30.webp": "6b54250569ecebc733a705a978866729b5d63fb8f5c10bc93c7d5e2dac1b8131",
    "/solutions-now/slides/slide-31.webp": "92ad34b9b75b2b13a39f701dfa6bbbcd2e1fea6f85563c297ffc685efce7ca42",
    "/solutions-now/slides/slide-32.webp": "5073388b2b697aecfc6bb7f6536b89c05e9bc8b0ad4579c710a366a0a63aa04f",
}
SOLUTION_SLIDES = {f"/solutions-now/slides/slide-{index}.webp" for index in range(1, 33)}
USER_AGENT = "TheGreenTank-GitHub-Mirror/2.0-v60-democratic-centre-guard"
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

SOLUTIONS_EVIDENCE_SCRIPT = r"""
(() => {
  const viewer = document.querySelector(".solution-slide-viewer");
  const currentFigure = viewer?.querySelector(".solution-current-slide");
  const currentAnchor = currentFigure?.querySelector("a");
  const currentImage = currentFigure?.querySelector("img");
  const currentCaption = currentFigure?.querySelector("figcaption");
  const title = viewer?.querySelector("#slide-viewer-title");
  const topline = viewer?.querySelector(".solution-viewer-topline .eyebrow");
  const controls = [...(viewer?.querySelectorAll(".solution-viewer-controls button") || [])];
  const indexButtons = [...(viewer?.querySelectorAll(".solution-slide-index button") || [])];
  const sourceFigures = [...document.querySelectorAll(".solution-all-slides figure")];
  let current = 0;

  if (!viewer || !currentAnchor || !currentImage || !currentCaption ||
      !title || controls.length !== 2 || indexButtons.length !== sourceFigures.length) return;

  function show(index, scroll = false) {
    current = Math.max(0, Math.min(sourceFigures.length - 1, index));
    const sourceFigure = sourceFigures[current];
    const sourceAnchor = sourceFigure.querySelector("a");
    const sourceImage = sourceFigure.querySelector("img");
    const sourceLink = sourceFigure.querySelector("figcaption a");
    const itemTitle = indexButtons[current].querySelector("strong")?.textContent?.trim() || "";
    if (!sourceAnchor || !sourceImage) return;

    currentAnchor.href = sourceAnchor.href;
    currentAnchor.setAttribute("aria-label", `Open slide ${current + 1} full size: ${itemTitle}`);
    currentImage.src = sourceImage.src;
    currentImage.alt = `Slide ${current + 1} of ${sourceFigures.length}: ${itemTitle}. Open the full-size slide for every displayed price, table, calculation and qualification.`;
    title.textContent = itemTitle;
    topline.textContent = `Complete evidence deck · slide ${current + 1} of ${sourceFigures.length}`;

    indexButtons.forEach((button, indexNumber) => {
      const selected = indexNumber === current;
      button.classList.toggle("is-current", selected);
      if (selected) button.setAttribute("aria-current", "true");
      else button.removeAttribute("aria-current");
    });
    controls[0].disabled = current === 0;
    controls[1].disabled = current === sourceFigures.length - 1;

    currentCaption.querySelector(".mirror-source-listing")?.remove();
    if (sourceLink) {
      const link = document.createElement("a");
      link.className = "mirror-source-listing";
      link.href = sourceLink.href;
      link.target = "_blank";
      link.rel = "noreferrer";
      link.textContent = "Open the pictured Alibaba listing ↗";
      currentCaption.append(link);
    }
    if (scroll) viewer.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  controls[0].addEventListener("click", () => show(current - 1, true));
  controls[1].addEventListener("click", () => show(current + 1, true));
  indexButtons.forEach((button, index) => button.addEventListener("click", () => show(index, true)));
  window.addEventListener("keydown", event => {
    if (event.key === "ArrowLeft") show(current - 1);
    if (event.key === "ArrowRight") show(current + 1);
  });
  show(0);
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
        value = match.group("url")
        normalized = normalize_same_origin(value)
        if normalized is None:
            return match.group(0)
        fragment = urlparse(urljoin(BASE, html.unescape(value).strip())).fragment
        target = prefixed_path(normalized)
        if fragment:
            target += "#" + fragment
        return f'{match.group("attr")}={match.group("q")}{target}{match.group("q")}'
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
        if route == "/solutions-now/evidence":
            mirror_script = f"{PREFIX}/assets/solutions-evidence.js"
            cleaned = cleaned.replace("</body>", f'<script src="{mirror_script}" defer></script>\n</body>', 1)
        write_bytes(route_output(route), cleaned.encode("utf-8"))
        print(f"mirrored route {route}")

    write_bytes(OUT / "assets" / "monkey-banana.js", MONKEY_BANANA_SCRIPT.encode("utf-8"))
    write_bytes(OUT / "assets" / "solutions-evidence.js", SOLUTIONS_EVIDENCE_SCRIPT.encode("utf-8"))

    home = original_pages["/"]
    library = original_pages["/library"]
    required_home = [
        "Before we judge",
        "Forty-one publications",
        "P—29",
        "P—30",
        "P—31",
        "P—32",
        "P—33",
        "P—34",
        "P—35",
        "P—36",
        "P—37",
        "P—38",
        "P—39",
        "P—40",
        "P—41",
        "The Democratic Centre as a Shared Civic Space",
        "/social-technology/democratic-centre",
        "CL17 — Emission Transitive Emission",
        "Friendship Three",
        "The Friendship Treaty",
        "Solutions Now",
        "Freedom to Live",
        "When Organisations Fail",
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
        "Fashion Police",
        "/fashion-police",
        "https://ministryofducks.github.io/",
        ">MOD<",
    ]
    missing_home = [m for m in required_home if m not in home]
    if missing_home:
        raise RuntimeError(f"Dev homepage lost expected v60 structure: {missing_home}")

    expected_project_destinations = [
        "/solutions-now",
        "/library#publication-02",
        "/library#publication-02",
        "/library#publication-02",
        "/solutions-now",
        "/library#publication-01",
        "/phantom-concorde",
        "/library#publication-10",
        "/climate-technology/emission-transitive-emission",
    ]
    actual_project_destinations = re.findall(
        r'<a\s+class=["\']project-open["\']\s+href=["\']([^"\']+)["\']',
        home,
        re.I,
    )
    if actual_project_destinations != expected_project_destinations:
        raise RuntimeError(
            "Homepage project destinations changed: "
            f"expected={expected_project_destinations}, actual={actual_project_destinations}"
        )
    if home.count(">Open subject<") != 9:
        raise RuntimeError("Homepage must retain exactly nine Open subject links")

    expected_mirror_project_destinations = [prefixed_path(path) for path in expected_project_destinations]
    mirrored_home = (OUT / "index.html").read_text(encoding="utf-8")
    actual_mirror_project_destinations = re.findall(
        r'<a\s+class=["\']project-open["\']\s+href=["\']([^"\']+)["\']',
        mirrored_home,
        re.I,
    )
    if actual_mirror_project_destinations != expected_mirror_project_destinations:
        raise RuntimeError(
            "Mirrored homepage project destinations changed: "
            f"expected={expected_mirror_project_destinations}, "
            f"actual={actual_mirror_project_destinations}"
        )

    required_library = [
        "Release 31",
        "41 publications",
        "91 public research files",
        "P—29",
        "P—30",
        "P—31",
        "P—32",
        "P—33",
        "P—34",
        "P—35",
        "P—36",
        "P—37",
        "P—38",
        "P—39",
        "P—40",
        "P—41",
        "The Democratic Centre as a Shared Civic Space",
        "Open the Democratic Centre paper",
        "CL17 — Emission Transitive Emission",
        "Solutions Now",
        "Freedom to Live",
        "Justice &amp; Accountability",
        "When Organisations Fail",
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
        "Friendship Three",
        "The Friendship Treaty",
    ]
    missing_library = [m for m in required_library if m not in library]
    if missing_library:
        raise RuntimeError(f"Dev library lost expected v60 structure: {missing_library}")

    fashion_police = original_pages["/fashion-police"]
    required_fashion_police = [
        "The Fashion",
        "Police Are",
        "Hear.",
        "The one law",
        "The Fashion Police shall have no authority over fashion.",
        "You can wear that.",
        "Weird is not a crime.",
        "Clothing is not consent.",
        "Investigate harm.",
        "Never prosecute taste.",
        "David Bowie:",
        "spirit of the Commissioner.",
        "CASE FILE 1982 · VALLEY GIRL",
        "Trying to quit fashion is also fashion.",
        "I will not arrest difference.",
        "I will investigate harm.",
        "I will tell nobody.",
        "I will tell everybody.",
        "F-z6u5hFgPk",
        "R5Q1yVLSR3I",
        "bIOocUQkfzk",
        "www.davidbowie.com",
        "www.zappa.com",
        "An unofficial cultural tribute and interpretation.",
        "It does not claim endorsement by David Bowie’s estate or representatives.",
    ]
    missing_fashion_police = [m for m in required_fashion_police if m not in fashion_police]
    if missing_fashion_police:
        raise RuntimeError(f"Fashion Police verification failed: {missing_fashion_police}")

    music = original_pages["/music"]
    required_music = [
        "Hear the influence. Keep the choice.",
        "Mini Knots – Let Me Untie You Tuo",
        "/music/knots-untying-through-perspective",
        "/music/knots-1",
        "Six stages of one developing experiment",
        "CC0 — No Rights Reserved",
        "Internet Archive players",
        "Seven unique players from the Knots archive.",
        "The Commercial player has been included once",
        "SoundCloud and Internet Archive",
    ]
    missing_music = [m for m in required_music if m not in music]
    if missing_music:
        raise RuntimeError(f"Dev Music page lost expected version 60 structure: {missing_music}")

    expected_archive_player_ids = [
        "knots-let-me-untie-you-3",
        "knots-Universal-Let-me-untie-you",
        "knots-pop-say-hello-a",
        "knots-commercial-Let-me-untie-you",
        "knots-let-me-auntie-uoo-say-hello",
        "knots-Let-me-untie-you",
        "Knots-POP-Let-me-untie-you",
    ]
    actual_archive_player_ids = re.findall(
        r'src=["\']https://archive\.org/embed/([^"\']+)["\']',
        music,
        re.I,
    )
    if actual_archive_player_ids != expected_archive_player_ids:
        raise RuntimeError(
            "Music archive player set changed: "
            f"expected={expected_archive_player_ids}, actual={actual_archive_player_ids}"
        )
    if actual_archive_player_ids.count("knots-commercial-Let-me-untie-you") != 1:
        raise RuntimeError("Commercial Music archive player must appear exactly once")

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
        "The common table.",
        "Not the halfway opinion.",
        "Democratic Centre",
        "/social-technology/democratic-centre",
        "Drugs:",
        "Evidence, Experience &amp; Supply.",
        "Health Systems",
        "What happens to NHS Right to Choose funding after referral?",
        "/social-technology/drugs-and-society",
        "/social-technology/health-systems-and-patient-choice",
        "Justice &amp; Accountability",
        "/social-technology/justice-and-accountability",
        "Friendship · three public letters",
        "/social-technology/friendship-three",
        "Friendship Three",
    ]
    missing_social = [m for m in required_social if m not in social]
    if missing_social:
        raise RuntimeError(f"Social Technology verification failed: {missing_social}")

    democratic_centre = original_pages["/social-technology/democratic-centre"]
    required_democratic_centre = [
        "P—41",
        "The Democratic Centre",
        "as a Shared Civic Space.",
        "A place, not a halfway political opinion",
        "Separate the views.",
        "Keep the people together.",
        "Existing perspective · P—18",
        "Existing perspective · P—24",
        "false equivalence",
        "A proposal to test,",
        "not a centre to obey.",
        "46 references",
        "supplied DOCX is preserved unchanged",
        "Alex_Anderson_The_Democratic_Centre_As_A_Shared_Civic_Space.pdf",
        "Alex_Anderson_The_Democratic_Centre_As_A_Shared_Civic_Space.docx",
    ]
    missing_democratic_centre = [
        marker for marker in required_democratic_centre if marker not in democratic_centre
    ]
    if missing_democratic_centre:
        raise RuntimeError(
            f"Democratic Centre verification failed: {missing_democratic_centre}"
        )

    friendship_three = original_pages["/social-technology/friendship-three"]
    required_friendship_three = [
        "P—39",
        "Friendship Three",
        "The Friendship",
        "Treaty",
        "We Would Like to Live Too, Please",
        "Dear Victoria",
        "My name is AL",
        "This land is held for life",
        "OVERWHELMED",
        "I cannot safely process this interaction",
        "This is not a threat or a wish for anyone",
        "Being wrong is not defeat",
        "Let friendship cross every border that domination and fear have built",
    ]
    missing_friendship_three = [m for m in required_friendship_three if m not in friendship_three]
    if missing_friendship_three:
        raise RuntimeError(f"Friendship Three verification failed: {missing_friendship_three}")

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

    justice = original_pages["/social-technology/justice-and-accountability"]
    required_justice = [
        "P—37",
        "When Organisations",
        "Corporate Manslaughter and Preventable Death in the United Kingdom",
        "not legal advice",
        "no finding of guilt",
        "This is not 540 suspected corporate manslaughters",
        "Thirty named matters",
        "Corporate_Manslaughter_UK_Draft.docx",
        "Corporate_Manslaughter_and_Corporate_Homicide_Act_2007.pdf",
        "Corporate_Manslaughter_Act_2007_Explanatory_Notes.pdf",
    ]
    missing_justice = [m for m in required_justice if m not in justice]
    if missing_justice:
        raise RuntimeError(f"Justice & Accountability verification failed: {missing_justice}")

    solutions = original_pages["/solutions-now"]
    required_solutions = [
        "P—38",
        "Freedom",
        "to Live",
        "See the actual options",
        "13.4m",
        "25.3m",
        "57%",
        "1.7m",
        "Surviving and living are different conditions.",
        "When does life begin if security always comes later?",
        "A market screen, not an endorsement.",
        "What remaining harm justifies refusal?",
        "One site. One home. Every cost and outcome made public.",
        "Freedom without a lawful place to exist is not freedom.",
        "/solutions-now/evidence",
    ]
    missing_solutions = [m for m in required_solutions if m not in solutions]
    if missing_solutions:
        raise RuntimeError(f"Solutions Now verification failed: {missing_solutions}")

    evidence = original_pages["/solutions-now/evidence"]
    required_evidence = [
        "Read before purchasing",
        "A market screen, not an endorsement.",
        "Complete evidence deck",
        "Slide 1 of 32:",
        "All 32 slides",
        "Every option, number and limitation",
        "No deposit before the complete evidence package exists.",
        "Affordable_Modular_Homes_and_Electric_Mobility_2026_Clear_Prices_v22.pptx",
        "Affordable_Modular_Homes_and_Electric_Mobility_2026_Clear_Prices_v22.pdf",
        "Affordable_Modular_Homes_and_Electric_Mobility_2026_Clear_Prices_v22_Transcript.txt",
        "1601761827603.html",
        "1601105102694.html",
    ]
    missing_evidence = [m for m in required_evidence if m not in evidence]
    if missing_evidence:
        raise RuntimeError(f"Solutions Now evidence verification failed: {missing_evidence}")

    cl17 = original_pages["/climate-technology/emission-transitive-emission"]
    required_cl17 = [
        "P—40",
        "CL17",
        "Emission Transitive Emission",
        "A personal research<br/><em>perspective.</em>",
        "The author’s view · clearly separated from the evidence verdict",
        "Li₂C₂ + 2 H₂O → C₂H₂ + 2 LiOH + heat",
        "2 LiOH + CO₂ → Li₂CO₃ + H₂O",
        "Lithium carbonate does not directly produce the acetylene",
        "I may be wrong, which is precisely why the pathway should be tested openly",
        "I do not seek ownership, control or exclusive rights",
        "CL17_Emission_Transitive_Emission_Research_Package_2026-09-13.zip",
    ]
    missing_cl17 = [m for m in required_cl17 if m not in cl17]
    if missing_cl17:
        raise RuntimeError(f"CL17 publication verification failed: {missing_cl17}")

    solution_slide_urls = {u for u in discovered_urls if u.startswith("/solutions-now/slides/")}
    missing_slides = sorted(SOLUTION_SLIDES - solution_slide_urls)
    unexpected_slides = sorted(solution_slide_urls - SOLUTION_SLIDES)
    if missing_slides or unexpected_slides:
        raise RuntimeError(
            f"Solutions Now slide set changed: missing={missing_slides}, unexpected={unexpected_slides}"
        )

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
    print("Version 60 research library file set verified unchanged")

    asset_urls = {
        u for u in discovered_urls
        if u.startswith(("/_next/", "/assets/", "/research/", "/simulators/")) or u in PUBLIC_ASSETS
    }
    asset_urls.update(PUBLIC_ASSETS)
    asset_urls.update(research_urls)
    asset_urls.update(EXTRA_BASELINE_PUBLIC_FILES)
    asset_urls.update(SOLUTION_SLIDES)

    seen: set[str] = set()
    for asset in sorted(asset_urls):
        save_asset(asset, seen)
        if asset.startswith("/research/"):
            print(f"mirrored research file {asset.rsplit('/', 1)[-1]}")

    for asset, expected_sha256 in EXPECTED_CONTENT_SHA256.items():
        data = local_path_for_url(asset).read_bytes()
        actual_sha256 = hashlib.sha256(data).hexdigest()
        if actual_sha256 != expected_sha256:
            raise RuntimeError(
                f"Protected release content checksum mismatch for {asset}: {actual_sha256}"
            )
    print("Protected version 60 release-content checksums verified")

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
        "source_site_version": SOURCE_SITE_VERSION,
        "source_release": SOURCE_RELEASE,
        "source_publication_count": SOURCE_PUBLICATION_COUNT,
        "source_commit": SOURCE_COMMIT,
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
