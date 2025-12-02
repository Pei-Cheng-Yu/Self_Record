#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
from urllib.parse import quote
from typing import List

# Names to ignore completely
IGNORE_NAMES = {
    "uploads",
    "_sidebar.md",
    "index.html",
    "gen_sidebars.py",
    "gen_readmes.py",
}

# Optional: pretty titles + emojis per folder
TITLE_OVERRIDE = {
    "daily": "📅 Daily Log",
    "projects": "🧪 Personal Projects",
    "learning-note": "📖 Learning Notes",
    "open-sources": "🌏 Open Source Contributions",
    "school-lab": "🏫 School Lab / Internship",
    "school-courses": "📚 School Courses",
    "reviews": "⭐ Reviews",
    "airflow-contrib": "🌍 Airflow Contributions",
}

ICON_FOR_FILE = "📄"
ICON_FOR_FOLDER = "📁"


def is_ignored(name: str) -> bool:
    return name in IGNORE_NAMES or name.startswith(".")


def url_path_from_rel(rel_path: str) -> str:
    """
    Convert a path relative to docs root to a docsify hash URL.
    e.g. "projects/airflow-contrib/README.md" -> "#/projects/airflow-contrib/README.md"
         "projects/ai-hackathon.md"          -> "#/projects/ai-hackathon"
    """
    parts = rel_path.split(os.sep)
    encoded = "/".join(quote(p) for p in parts)
    return f"#/{encoded}"


def display_name(name: str) -> str:
    base, _ = os.path.splitext(name)
    base = base.replace("_", " ").replace("-", " ")
    return base.strip().title()


def folder_title(folder_name: str) -> str:
    if folder_name in TITLE_OVERRIDE:
        return TITLE_OVERRIDE[folder_name]
    # default: 📁 + Pretty Name
    return f"{ICON_FOR_FOLDER} {display_name(folder_name)}"


def ensure_readme(
    root_abs: str,
    dirpath: str,
    overwrite: bool = False,
) -> None:
    """
    Generate README.md for a given folder, unless it already exists
    and overwrite=False.
    """
    readme_path = os.path.join(dirpath, "README.md")
    if os.path.exists(readme_path) and not overwrite:
        return  # do not touch existing README

    rel_dir = os.path.relpath(dirpath, root_abs)
    # For root itself, rel_dir will be "."
    folder_name = os.path.basename(dirpath) if rel_dir != "." else ""
    title = "📘 My Personal Dashboard" if rel_dir == "." else folder_title(folder_name)

    # Collect children: direct subfolders + md files (excluding README/_sidebar)
    entries = [
        e for e in os.listdir(dirpath)
        if not is_ignored(e)
    ]
    child_dirs = sorted(
        [e for e in entries if os.path.isdir(os.path.join(dirpath, e))],
        key=str.casefold,
    )
    child_files = sorted(
        [
            e for e in entries
            if os.path.isfile(os.path.join(dirpath, e))
            and e.lower().endswith(".md")
            and e.lower() != "readme.md"
        ],
        key=str.casefold,
    )

    lines: List[str] = []

    # H1
    lines.append(f"<h1>{title}</h1>")
    lines.append("")

    if rel_dir == ".":
        # Root dashboard description
        lines.append("Welcome to my self-record workspace.  ")
        lines.append("Use this dashboard to track what I do, what I learn, and how I grow.")
    else:
        pretty = display_name(folder_name) if folder_name else "this section"
        lines.append(f"This section contains notes, logs, and links related to **{pretty}**.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append('<div class="dashboard-grid">')
    lines.append("")

    # Helper to build href for a child folder
    def href_for_child_folder(child_name: str) -> str:
        # path: rel_dir / child / README.md  (from root)
        if rel_dir == ".":
            rel = os.path.join(child_name, "README.md")
        else:
            rel = os.path.join(rel_dir, child_name, "README.md")
        return url_path_from_rel(rel)

    # Helper for a child file
    def href_for_child_file(child_file: str) -> str:
        # path: rel_dir / child_file (we drop .md in URL, docsify handles that)
        base, _ = os.path.splitext(child_file)
        if rel_dir == ".":
            rel = base
        else:
            rel = os.path.join(rel_dir, base)
        return url_path_from_rel(rel)

    # 1) child folders → cards
    for d in child_dirs:
        child_href = href_for_child_folder(d)
        child_title = folder_title(d)
        lines.append(f'  <a class="card" href="{child_href}">')
        lines.append(f"    <h2>{child_title}</h2>")
        lines.append("    <p>Notes, logs, and links for this section.</p>")
        lines.append("  </a>")
        lines.append("")

    # 2) child files (markdown) → cards
    for f in child_files:
        child_href = href_for_child_file(f)
        title_text = f"{ICON_FOR_FILE} {display_name(f)}"
        lines.append(f'  <a class="card" href="{child_href}">')
        lines.append(f"    <h2>{title_text}</h2>")
        lines.append("    <p>Page in this section.</p>")
        lines.append("  </a>")
        lines.append("")

    lines.append("</div>")
    lines.append("")

    with open(readme_path, "w", encoding="utf-8") as fp:
        fp.write("\n".join(lines))

    print(f"generated README: {readme_path}")


def generate_readmes(root_abs: str, overwrite: bool = False) -> None:
    """
    Walk all folders under root_abs and ensure each has a README.md.
    By default, existing READMEs are left untouched.
    """
    for dirpath, dirnames, filenames in os.walk(root_abs):
        # filter out ignored dirs
        dirnames[:] = [
            d for d in dirnames
            if not is_ignored(d)
        ]

        ensure_readme(root_abs, dirpath, overwrite=overwrite)


def main():
    parser = argparse.ArgumentParser(
        description="Auto-generate README.md dashboards for each docs folder."
    )
    parser.add_argument(
        "--root",
        default=".",
        help="docs root folder (default: .)",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="overwrite existing README.md files",
    )
    args = parser.parse_args()

    root_abs = os.path.abspath(args.root)
    if not os.path.isdir(root_abs):
        print(f"folder not found: {root_abs}")
        raise SystemExit(1)

    generate_readmes(root_abs, overwrite=args.overwrite)


if __name__ == "__main__":
    main()
