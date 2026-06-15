#!/usr/bin/env python3
"""Validate the Awesome Human Motion resource data and generated README."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "resources.yml"
README_PATH = ROOT / "README.md"

CATEGORIES = [
    "Motion Capture",
    "Motion Generation",
    "Motion Interaction",
    "Humanoid Simulation",
    "Motion Video Generation",
    "Datasets",
    "Surveys and Benchmarks",
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
    if not 60 <= len(items) <= 90:
        fail(f"expected 60-90 resources, found {len(items)}")

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
    if motion_capture[0].get("venue") != "Tech Report 2026" or not motion_capture[0].get("featured"):
        fail("AIMoCap must use venue Tech Report 2026 and featured=true")

    readme = README_PATH.read_text(encoding="utf-8")
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
