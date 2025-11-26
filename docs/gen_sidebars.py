#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import sys
from urllib.parse import quote

# allowed extensions
ALLOW_EXT = {".md"}

# names to ignore entirely
IGNORE_NAMES = {
    "uploads",
    "index.html",
    "_sidebar.md",
}
TITLE_OVERRIDE = {
    "airflow-contrib": "Airflow Contributions",
    "open-source": "Open Source",
}

def is_markdown(p: str) -> bool:
    if ALLOW_EXT is None:
        return True
    _, ext = os.path.splitext(p)
    return ext.lower() in ALLOW_EXT


def display_name_from_filename(fn: str) -> str:
    """
    - strip extension
    - replace '_' / '-' with spaces
    - escape '[' and ']'
    """
    name, _ = os.path.splitext(fn)
    name = name.replace("_", " ").replace("-", " ")
    name = name.replace("[", r"\[").replace("]", r"\]")
    return name


def rel_url(path_from_root: str) -> str:
    """URL encode each path segment for docsify."""
    parts = path_from_root.split(os.sep)
    return "/".join(quote(p) for p in parts)


def has_readme(dirpath: str) -> str | None:
    for cand in ["README.md", "readme.md"]:
        p = os.path.join(dirpath, cand)
        if os.path.isfile(p) and is_markdown(p):
            return p
    return None


def natural_key(s: str):
    return s.casefold()


def should_ignore(name: str) -> bool:
    return name in IGNORE_NAMES


def build_tree(root: str):
    """
    Return (dirs, files):
    - dirs: visible subdirectories
    - files: .md files in this dir (excluding README + ignored)
    """
    entries = [
        e
        for e in os.listdir(root)
        if not e.startswith(".") and not should_ignore(e)
    ]

    dirs = sorted(
        [e for e in entries if os.path.isdir(os.path.join(root, e))],
        key=natural_key,
    )
    files = sorted(
        [
            e
            for e in entries
            if os.path.isfile(os.path.join(root, e)) and is_markdown(e)
        ],
        key=natural_key,
    )

    files_wo_readme = [f for f in files if f.lower() != "readme.md"]
    return dirs, files_wo_readme


def write_sidebar(root_dir: str, out_fp, base_dir: str, depth: int = 0):
    dirs, files = build_tree(root_dir)

    # files in this folder
    for f in files:
        full = os.path.join(root_dir, f)
        rel = os.path.relpath(full, base_dir)  # now relative to docs root
        url = rel_url(rel)
        title = display_name_from_filename(f)
        indent = "  " * depth
        out_fp.write(f"{indent}- [{title}]({url})\n")

    # subfolders
    for d in dirs:
        child = os.path.join(root_dir, d)
        folder_title = display_name_from_filename(d)
        indent = "  " * depth

        child_readme = has_readme(child)
        if child_readme:
            rel = os.path.relpath(child_readme, base_dir)
            url = rel_url(rel)
            out_fp.write(f"{indent}- [{folder_title}]({url})\n")
        else:
            out_fp.write(f"{indent}- {folder_title}\n")

        write_sidebar(child, out_fp, base_dir, depth + 1)

def generate_single_sidebar(root_abs: str, out_path: str):
    """Old behavior: one _sidebar.md for the whole tree."""
    with open(out_path, "w", encoding="utf-8") as f:
        top_readme = has_readme(root_abs)
        if top_readme:
            rel = os.path.relpath(top_readme, root_abs)
            title = display_name_from_filename(os.path.basename(root_abs) or "Home")
            f.write(f"- [{title}]({rel_url(rel)})\n")
        write_sidebar(root_abs, f, base_dir=root_abs, depth=0)
    print(f"generated: {out_path}")


def generate_per_folder_sidebars(root_abs: str):
    """
    Create _sidebar.md in every folder under root, EXCEPT the root itself.

    Each sidebar will contain:
      - A '🏠 Dashboard' link to the root README.md (if it exists)
      - A '⬅ Back to <Parent>' link to the parent folder's README (if it exists)
      - A link to this folder's own README (if it exists)
      - Auto-generated list of files and subfolders (paths root-relative)
    """
    root_readme = has_readme(root_abs)
    root_readme_rel = (
        os.path.relpath(root_readme, root_abs) if root_readme else None
    )

    for dirpath, dirnames, filenames in os.walk(root_abs):
        # filter out hidden / ignored dirs
        dirnames[:] = [
            d for d in dirnames
            if not d.startswith(".") and not should_ignore(d)
        ]

        basename = os.path.basename(dirpath)

        # skip ignored dirs completely (except root itself)
        if should_ignore(basename) and dirpath != root_abs:
            continue

        # DO NOT generate _sidebar.md for root itself
        if dirpath == root_abs:
            continue

        sidebar_path = os.path.join(dirpath, "_sidebar.md")

        # figure out parent README (for the "../" link)
        parent_dir = os.path.dirname(dirpath)
        parent_readme = None
        parent_rel = None
        parent_title = None

        if parent_dir.startswith(root_abs) and parent_dir != root_abs:
            parent_readme = has_readme(parent_dir)
            if parent_readme:
                parent_rel = os.path.relpath(parent_readme, root_abs)
                parent_title = display_name_from_filename(
                    os.path.basename(parent_dir)
                )

        with open(sidebar_path, "w", encoding="utf-8") as f:
            # 1) Dashboard link (always root README)
            if root_readme_rel:
                f.write(
                    f"- [🏠 Dashboard]({rel_url(root_readme_rel)})\n"
                )

            # 2) "../" link to parent folder (if it has README)
            if parent_rel and parent_title:
                f.write(
                    f"- [⬅ Back to {parent_title}]({rel_url(parent_rel)})\n\n"
                )
            else:
                f.write("\n")  # blank line spacer

            # 3) This folder's own README, if any (root-relative)
            readme = has_readme(dirpath)
            if readme:
                rel = os.path.relpath(readme, root_abs)
                title = display_name_from_filename(
                    os.path.basename(dirpath) or "Home"
                )
                f.write(f"- [{title}]({rel_url(rel)})\n")

            # 4) The rest of the tree inside this folder (root-relative paths)
            write_sidebar(dirpath, f, base_dir=root_abs, depth=0)

        print(f"generated: {sidebar_path}")



def main():
    parser = argparse.ArgumentParser(
        description="Generate Docsify _sidebar.md from a folder tree"
    )
    parser.add_argument("--root", default=".", help="project root (default: .)")
    parser.add_argument(
        "--out", default="_sidebar.md", help="output file when NOT using --per-folder"
    )
    parser.add_argument(
        "--include-non-md",
        action="store_true",
        help="include non-.md files (not recommended)",
    )
    parser.add_argument(
        "--per-folder",
        action="store_true",
        help="generate a _sidebar.md inside every folder under root",
    )
    args = parser.parse_args()

    if args.include_non_md:
        global ALLOW_EXT

        ALLOW_EXT = None  # disable ext filtering

        def is_all(_p: str) -> bool:
            return True

        globals()["is_markdown"] = is_all

    root_abs = os.path.abspath(args.root)
    if not os.path.isdir(root_abs):
        print(f"folder not found: {root_abs}", file=sys.stderr)
        sys.exit(1)

    if args.per_folder:
        generate_per_folder_sidebars(root_abs)
    else:
        out_path = os.path.join(root_abs, args.out)
        generate_single_sidebar(root_abs, out_path)


if __name__ == "__main__":
    main()
