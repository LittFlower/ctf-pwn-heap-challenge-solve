#!/usr/bin/env python3
"""Search a local how2heap repository by version, technique, and keywords."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", help="Path to a local how2heap repository")
    parser.add_argument("--version", help="glibc version, for example 2.35 or glibc_2.35")
    parser.add_argument("--technique", help="Technique name or substring, for example tcache_poisoning")
    parser.add_argument(
        "--keyword",
        action="append",
        default=[],
        help="Keyword that must appear in the file name or file body; repeatable",
    )
    parser.add_argument("--list-versions", action="store_true", help="List discovered glibc versions")
    parser.add_argument("--list-techniques", action="store_true", help="List discovered technique names")
    return parser.parse_args()


def normalize_version(value: str) -> str:
    normalized = value.strip()
    if normalized.startswith("glibc_"):
        normalized = normalized[len("glibc_") :]
    if normalized.startswith("v"):
        normalized = normalized[1:]
    return normalized


def version_key(value: str) -> tuple[int, ...]:
    return tuple(int(part) for part in value.split("."))


def looks_like_how2heap(root: Path) -> bool:
    return (
        root.is_dir()
        and (root / "README.md").is_file()
        and (root / "Makefile").is_file()
        and (root / "glibc_ChangeLog.md").is_file()
        and any(root.glob("glibc_*/*.c"))
    )


def discover_repo(explicit: str | None) -> Path:
    candidates: list[Path] = []
    if explicit:
        candidates.append(Path(explicit).expanduser())
    env_repo = os.environ.get("HOW2HEAP_ROOT")
    if env_repo:
        candidates.append(Path(env_repo).expanduser())

    cwd = Path.cwd().resolve()
    candidates.extend([cwd, *cwd.parents])
    candidates.extend(
        [
            cwd / "how2heap",
            cwd.parent / "how2heap",
            Path.home() / "ctf/problem/how2heap",
            Path.home() / "how2heap",
            Path.home() / "src/how2heap",
        ]
    )

    seen: set[Path] = set()
    for candidate in candidates:
        try:
            resolved = candidate.resolve()
        except FileNotFoundError:
            continue
        if resolved in seen:
            continue
        seen.add(resolved)
        if looks_like_how2heap(resolved):
            return resolved

    raise SystemExit(
        "Could not find a how2heap repository. Pass --repo /path/to/how2heap or set HOW2HEAP_ROOT."
    )


def collect_examples(repo_root: Path) -> list[dict[str, str]]:
    examples: list[dict[str, str]] = []
    for path in sorted(repo_root.glob("glibc_*/*.c")):
        version = path.parent.name.split("_", 1)[1]
        technique = path.stem
        body = path.read_text(encoding="utf-8", errors="ignore")
        examples.append(
            {
                "version": version,
                "technique": technique,
                "path": str(path),
                "body": body,
            }
        )
    return examples


def filter_examples(
    examples: list[dict[str, str]],
    version: str | None,
    technique: str | None,
    keywords: list[str],
) -> list[dict[str, str]]:
    filtered = examples

    if version:
        expected = normalize_version(version)
        filtered = [item for item in filtered if item["version"] == expected]

    if technique:
        needle = technique.lower()
        filtered = [item for item in filtered if needle in item["technique"].lower()]

    for keyword in keywords:
        needle = keyword.lower()
        filtered = [
            item
            for item in filtered
            if needle in item["technique"].lower() or needle in item["body"].lower()
        ]

    return filtered


def print_listing(title: str, items: list[str]) -> None:
    print(title)
    for item in items:
        print(f"- {item}")


def print_matches(matches: list[dict[str, str]]) -> None:
    for item in sorted(matches, key=lambda entry: (version_key(entry["version"]), entry["technique"])):
        print(f"[{item['version']}] {item['technique']}: {item['path']}")


def print_nearby_versions(
    examples: list[dict[str, str]],
    target_version: str | None,
    technique: str,
) -> None:
    needle = technique.lower()
    siblings = [item for item in examples if needle in item["technique"].lower()]
    if not siblings:
        return

    print("\nNo exact match for that version. Nearby versions for the requested technique:")
    for item in sorted(siblings, key=lambda entry: (version_key(entry["version"]), entry["technique"])):
        marker = ""
        if target_version and item["version"] == normalize_version(target_version):
            marker = "  <== requested version"
        print(f"- [{item['version']}] {item['technique']}: {item['path']}{marker}")


def main() -> int:
    args = parse_args()
    repo_root = discover_repo(args.repo)
    examples = collect_examples(repo_root)

    if args.list_versions:
        versions = sorted({item["version"] for item in examples}, key=version_key)
        print_listing(f"how2heap repo: {repo_root}", versions)
        return 0

    if args.list_techniques:
        techniques = sorted({item["technique"] for item in examples})
        print_listing(f"how2heap repo: {repo_root}", techniques)
        return 0

    matches = filter_examples(examples, args.version, args.technique, args.keyword)
    if matches:
        print(f"how2heap repo: {repo_root}")
        print_matches(matches)
        return 0

    print("No matching how2heap examples found.", file=sys.stderr)
    if args.technique:
        print_nearby_versions(examples, args.version, args.technique)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
