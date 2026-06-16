#!/usr/bin/env python3
"""Validate the Awesome Human Motion resource data and generated README."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "resources.yml"
README_PATH = ROOT / "README.md"
DIAGRAM_PATH = ROOT / "assets" / "human-motion-framework.svg"

CATEGORIES = [
    "Reviews and Surveys",
    "Motion Capture",
    "Human Pose Estimation and Motion Reconstruction",
    "Motion Generation",
    "Motion Editing",
    "Motion Stylization",
    "Motion Interaction",
    "Human-Object and Human-Scene Interaction",
    "Humanoid Simulation and Robot Motion",
    "Motion Video Generation",
    "Human Avatar and Reconstruction",
    "Human Motion Understanding",
    "Datasets and Benchmarks",
    "Bio Motion and Biomechanics",
]
SENSITIVE_TERMS = [
    "wen" + "lin",
    "zhu" + "ang",
    "cloud" + "flare",
    "wran" + "gler",
    r"\br2\b",
    "data" + "base",
    "post" + "gres",
    "ne" + "on",
    "se" + "cret",
    "to" + "ken",
    "inter" + "nal",
    "ad" + "min",
    "run" + "ner",
    "D:" + r"\\",
    "C:" + r"\\",
    "ship" + "any",
    "idou" + "bi",
]
SENSITIVE = re.compile("|".join(SENSITIVE_TERMS))


def load_data() -> dict:
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def fail(message: str) -> None:
    raise SystemExit(message)


def validate_links(item: dict) -> None:
    for field in ("project", "paper", "hf"):
        value = item.get(field, "")
        if value and not value.startswith(("https://", "http://")):
            fail(f"{item['title']}: {field} must be an absolute URL")
    repo = item.get("github", "")
    if repo and (repo.startswith("http") or "/" not in repo):
        fail(f"{item['title']}: github must be OWNER/REPO")


def validate() -> None:
    data = load_data()
    items = data.get("resources", [])
    if not 150 <= len(items) <= 240:
        fail(f"expected 150-240 resources, found {len(items)}")

    seen_titles: set[str] = set()
    for item in items:
        for field in ("title", "category", "date", "venue"):
            if not item.get(field):
                fail(f"missing {field}: {item}")
        if item["category"] not in CATEGORIES:
            fail(f"unknown category for {item['title']}: {item['category']}")
        if not re.fullmatch(r"\d{4}-\d{2}", item["date"]):
            fail(f"{item['title']}: date must be YYYY-MM")
        if item["title"] in seen_titles:
            fail(f"duplicate title: {item['title']}")
        seen_titles.add(item["title"])
        validate_links(item)

    motion_capture = [item for item in items if item["category"] == "Motion Capture"]
    if not motion_capture or motion_capture[0]["title"] != "AIMoCap Video2Motion":
        fail("AIMoCap Video2Motion must be the first Motion Capture data item")
    if motion_capture[0].get("venue") != "Tech Report 2026":
        fail("AIMoCap must use venue Tech Report 2026")
    if "featured" in motion_capture[0]:
        fail("AIMoCap must not use a featured flag")

    required_hf = {
        "AIMoCap Video2Motion": "https://huggingface.co/spaces/animtex/AIMoCap",
        "Kimodo": "https://huggingface.co/spaces/nvidia/Kimodo",
        "HY-Motion-1.0": "https://huggingface.co/spaces/tencent/HY-Motion-1.0",
        "MotionGPT": "https://huggingface.co/spaces/OpenMotionLab/MotionGPT",
    }
    by_title = {item["title"]: item for item in items}
    for title, hf_url in required_hf.items():
        if by_title.get(title, {}).get("hf") != hf_url:
            fail(f"{title}: expected HF demo {hf_url}")

    readme = README_PATH.read_text(encoding="utf-8")
    if "## Featured" in readme or "**Featured**" in readme:
        fail("README must not contain a Featured section or Featured label")
    if "Human Motion Research Map" not in readme:
        fail("README must include the Human Motion Research Map")
    for phrase in (
        "What This List Covers",
        "Related Awesome Lists",
        "awesome human motion",
        "human motion capture",
        "video-to-motion",
        "text-to-motion",
        "motion generation",
        "motion editing",
        "motion stylization",
        "pose estimation",
        "human reconstruction",
        "motion understanding",
        "humanoid robot motion",
        "embodied AI",
    ):
        if phrase not in readme:
            fail(f"README missing search/discovery phrase: {phrase}")
    if not DIAGRAM_PATH.exists():
        fail("assets/human-motion-framework.svg is missing")
    diagram = DIAGRAM_PATH.read_text(encoding="utf-8")
    for phrase in (
        "Data Layer",
        "Technique Layer",
        "Application Layer",
        "Captured Motion Data",
        "Human Motion Datasets",
    ):
        if phrase not in diagram:
            fail(f"diagram missing three-layer map phrase: {phrase}")
    if "utm_source=awesome_human_motion" not in readme:
        fail("AIMoCap UTM links are missing from README")
    if "img.shields.io/github/stars/" not in readme:
        fail("dynamic GitHub star badges are missing")

    for path in [DATA_PATH, README_PATH, ROOT / "CONTRIBUTING.md"]:
        if path.exists():
            text = path.read_text(encoding="utf-8")
            match = SENSITIVE.search(text)
            if match:
                fail(f"sensitive pattern found in {path.relative_to(ROOT)}: {match.group(0)}")

    print(f"Validated {len(items)} resources.")


if __name__ == "__main__":
    validate()
