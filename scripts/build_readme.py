#!/usr/bin/env python3
"""Build README.md from data/resources.yml.

The data file is JSON-compatible YAML so the project has no Python package
dependency. Keep this generator deterministic; the README is the public surface.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "resources.yml"
README_PATH = ROOT / "README.md"

UTM = "utm_source=awesome_human_motion&utm_medium=readme&utm_campaign=curation"
CATEGORIES = [
    "Motion Capture",
    "Motion Generation",
    "Motion Interaction",
    "Humanoid Simulation",
    "Motion Video Generation",
    "Datasets",
    "Surveys and Benchmarks",
]


def load_data() -> dict:
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def with_utm(url: str) -> str:
    if not url:
        return ""
    joiner = "&" if "?" in url else "?"
    return f"{url}{joiner}{UTM}"


def badge(label: str, color: str, url: str) -> str:
    safe_label = label.replace("-", "--").replace(" ", "%20")
    src = f"https://img.shields.io/badge/{safe_label}-{color}"
    return f'<a href="{url}"><img alt="{label}" src="{src}"></a>'


def star_badge(repo: str, target_url: str | None = None) -> str:
    target = target_url or f"https://github.com/{repo}"
    return (
        f"[![Star](https://img.shields.io/github/stars/{repo}.svg?"
        f"style=social&label=Star)]({target})"
    )


def link_or_dash(label: str, url: str) -> str:
    return f"[{label}]({url})" if url else "-"


def resource_row(item: dict) -> str:
    project_url = item.get("project", "")
    hf_url = item.get("hf", "")
    paper_url = item.get("paper", "")
    github_target = None
    if item.get("featured"):
        project_url = with_utm(project_url)
        hf_url = with_utm(hf_url)
        paper_url = with_utm(paper_url)
        github_target = with_utm(f"https://github.com/{item['github']}") if item.get("github") else None

    work = link_or_dash(item["title"], project_url or paper_url)
    repo = item.get("github", "")
    github = star_badge(repo, github_target) if repo else "-"
    hf = link_or_dash("HF Demo", hf_url)
    paper = link_or_dash("Paper", paper_url)
    project = link_or_dash("Project", project_url)
    featured = " **Featured**" if item.get("featured") else ""
    return (
        f"| {item['date']} | {item['venue']}{featured} | {work} | "
        f"{project} | {github} | {hf} | {paper} |"
    )


def sorted_items(items: list[dict], category: str) -> list[dict]:
    group = [item for item in items if item["category"] == category]
    if category == "Motion Capture":
        group.sort(key=lambda item: (not item.get("featured", False), item["date"]), reverse=False)
        featured = [item for item in group if item.get("featured")]
        rest = sorted([item for item in group if not item.get("featured")], key=lambda i: i["date"], reverse=True)
        return featured + rest
    return sorted(group, key=lambda item: item["date"], reverse=True)


def render_readme(data: dict) -> str:
    project_url = with_utm("https://animate-x.github.io/aimocap/")
    hf_url = with_utm("https://huggingface.co/spaces/animtex/AIMoCap")
    report_url = with_utm("https://github.com/animate-x/aimocap-video2motion")

    lines: list[str] = [
        "# Awesome Human Motion [![Awesome](https://awesome.re/badge.svg)](https://awesome.re)",
        "",
        "A curated list of papers, projects, demos, and datasets for **motion capture, "
        "motion generation, humanoid motion, motion interaction, motion video generation, "
        "and human motion datasets**.",
        "",
        "<p align=\"center\">",
        f"  {badge('PRs Welcome', 'brightgreen', 'CONTRIBUTING.md')}",
        f"  {badge('AIMoCap Project Page', '80efa9', project_url)}",
        f"  {badge('HF Space', 'ffcc4d', hf_url)}",
        f"  {badge('AIMoCap Video2Motion', '84b7ff', report_url)}",
        "</p>",
        "",
        "## Featured",
        "",
        "- **[AIMoCap Video2Motion]({})**: video-to-motion for FBX animation and Unitree G1 robot motion. "
        "Try the [HF Space]({}) or read the [technical report]({}).".format(project_url, hf_url, report_url),
        "",
        "## Table of Contents",
        "",
    ]

    for category in CATEGORIES:
        anchor = category.lower().replace(" ", "-")
        lines.append(f"- [{category}](#{anchor})")

    lines += [
        "",
        "## Format",
        "",
        "| Date | Venue | Work | Project | GitHub | HF Demo | Paper |",
        "| --- | --- | --- | --- | --- | --- | --- |",
        "",
    ]

    items = data["resources"]
    for category in CATEGORIES:
        lines += [
            f"## {category}",
            "",
            "| Date | Venue | Work | Project | GitHub | HF Demo | Paper |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
        for item in sorted_items(items, category):
            lines.append(resource_row(item))
        lines.append("")

    lines += [
        "## Contributing",
        "",
        "Pull requests are welcome. Please add new items to `data/resources.yml` and run:",
        "",
        "```bash",
        "python scripts/build_readme.py --check",
        "python scripts/validate_resources.py",
        "```",
        "",
        "Entries are curated for relevance to human motion capture, generation, interaction, "
        "humanoid simulation, human-centric video generation, and datasets.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if README.md is stale")
    args = parser.parse_args()

    rendered = render_readme(load_data())
    if args.check:
        current = README_PATH.read_text(encoding="utf-8") if README_PATH.exists() else ""
        if current != rendered:
            print("README.md is out of date. Run python scripts/build_readme.py")
            return 1
        print("README.md is up to date.")
        return 0

    README_PATH.write_text(rendered, encoding="utf-8", newline="\n")
    print(f"Wrote {README_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
