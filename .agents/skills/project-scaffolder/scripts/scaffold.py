from __future__ import annotations

import argparse
import re
import shutil
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
TEMPLATES = ROOT / "docs" / "templates"
PROJECTS = ROOT / "projects"


WINDOWS_RESERVED_NAMES = {
    "con",
    "prn",
    "aux",
    "nul",
    "com1",
    "com2",
    "com3",
    "com4",
    "com5",
    "com6",
    "com7",
    "com8",
    "com9",
    "lpt1",
    "lpt2",
    "lpt3",
    "lpt4",
    "lpt5",
    "lpt6",
    "lpt7",
    "lpt8",
    "lpt9",
}


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).strip()
    normalized = re.sub(r"\s+", "-", normalized)
    normalized = re.sub(r'[<>:"/\\\\|?*]+', "-", normalized)
    normalized = re.sub(r"[\x00-\x1f]+", "", normalized)
    normalized = re.sub(r"-{2,}", "-", normalized).strip("-. ")

    if not normalized:
        raise ValueError("project name could not be converted to a safe folder name")

    if normalized.casefold() in WINDOWS_RESERVED_NAMES:
        normalized = f"project-{normalized}"

    return normalized


def replace_once(text: str, old: str, new: str) -> str:
    if old in text:
        return text.replace(old, new, 1)
    return text


def prepare_text(path: Path, project_slug: str, summary: str) -> str:
    text = path.read_text(encoding="utf-8")

    if path.name == "START_HERE.template.md":
        text = replace_once(text, "- 1-2 行で project の目的を書く", f"- {summary}")
        text = replace_once(
            text,
            "- 初見で最初に確認することを 1-3 行で書く",
            "- `AGENTS.md` と `PROJECT_SUMMARY.md` を読んで正本候補を確認する",
        )
    elif path.name == "PROJECT_SUMMARY.template.md":
        text = replace_once(text, "- この project が何をするものか", f"- {summary}")
        text = replace_once(
            text,
            "- 初見で最初に確認することを 1-3 行で書く",
            "- `START_HERE.md` を読み、正本コードと未確定項目を切り分ける",
        )
    elif path.name == "project-AGENTS.template.md":
        text = replace_once(text, "- 何をするツールか", f"- {summary}")

    header = f"<!-- scaffolded: {project_slug} -->\n"
    return header + text


def copy_template(src: Path, dest: Path, project_slug: str, summary: str) -> None:
    text = prepare_text(src, project_slug, summary)
    dest.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a new project scaffold from workspace templates.")
    parser.add_argument("--name", required=True, help="Project name. It will be converted to a slug.")
    parser.add_argument("--summary", required=True, help="One-line purpose of the project.")
    args = parser.parse_args()

    project_slug = slugify(args.name)
    project_dir = PROJECTS / project_slug
    docs_dir = project_dir / "docs"

    if project_dir.exists():
        raise SystemExit(f"project already exists: {project_dir}")

    project_dir.mkdir(parents=True)
    docs_dir.mkdir(parents=True, exist_ok=True)

    copy_template(TEMPLATES / "project-AGENTS.template.md", project_dir / "AGENTS.md", project_slug, args.summary)
    copy_template(TEMPLATES / "START_HERE.template.md", project_dir / "START_HERE.md", project_slug, args.summary)
    copy_template(TEMPLATES / "PROJECT_SUMMARY.template.md", project_dir / "PROJECT_SUMMARY.md", project_slug, args.summary)

    shutil.copy2(TEMPLATES / "current-state-check.template.md", docs_dir / "current-state-check.md")
    shutil.copy2(TEMPLATES / "implementation-plan-template.md", docs_dir / "implementation-plan.md")
    shutil.copy2(TEMPLATES / "pre-implementation-decision.template.md", docs_dir / "pre-implementation-decision.md")

    print(f"created: {project_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
