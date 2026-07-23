"""Validate local development prerequisites without changing the system."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path


REQUIREMENTS = {
    "docker": ((24, 0), ["--version"]),
    "kubectl": ((1, 31), ["version", "--client"]),
    "kind": ((0, 27), ["version"]),
    "helm": ((3, 15), ["version", "--short"]),
}
DISPLAY_NAMES = {
    "docker": "Docker",
    "kubectl": "kubectl",
    "kind": "kind",
    "helm": "Helm",
    "pre-commit": "pre-commit",
}
PYTHON_MIN_VERSION = (3, 12)


def version_from(output: str) -> tuple[int, ...] | None:
    match = re.search(r"(?:v|version[=:]?\s*)?(\d+)\.(\d+)(?:\.(\d+))?", output, re.I)
    if not match:
        return None
    return tuple(int(part) for part in match.groups(default="0"))


def executable(name: str) -> str | None:
    if name == "pre-commit":
        local = Path(".venv/bin/pre-commit")
        if local.is_file():
            return str(local)
    return shutil.which(name)


def format_version(version: tuple[int, ...]) -> str:
    return ".".join(map(str, version))


def check_tool(
    name: str, minimum: tuple[int, ...], args: list[str]
) -> tuple[bool, str]:
    display_name = DISPLAY_NAMES[name]
    command = executable(name)
    required = format_version(minimum)
    if command is None:
        return False, f"MISSING: {display_name} - not found"

    result = subprocess.run(
        [command, *args], capture_output=True, text=True, check=False
    )
    detected = version_from(f"{result.stdout}\n{result.stderr}")
    if result.returncode != 0 or detected is None:
        return (
            False,
            f"MISSING: {display_name} - version could not be determined; "
            f"desired version: >= {required}",
        )
    if detected < minimum:
        return (
            False,
            f"MISSING: {display_name} - current version: "
            f"{format_version(detected)}; desired version: >= {required}",
        )
    return True, f"OK: {display_name} {format_version(detected)}"


def check_docker_daemon() -> tuple[bool, str]:
    docker = executable("docker")
    if docker is None:
        return False, "MISSING: Docker daemon - Docker not found"
    result = subprocess.run(
        [docker, "info"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    if result.returncode:
        return False, "MISSING: Docker daemon - inaccessible"
    return True, "OK: Docker daemon accessible"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-pre-commit", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    checks: list[tuple[bool, str]] = []

    python_version = tuple(sys.version_info[:3])
    if python_version < PYTHON_MIN_VERSION:
        checks.append(
            (
                False,
                f"MISSING: Python - current version: "
                f"{format_version(python_version)}; desired version: "
                f">= {format_version(PYTHON_MIN_VERSION)}",
            )
        )
    else:
        checks.append((True, f"OK: Python {format_version(python_version)}"))

    for name, (minimum, version_args) in REQUIREMENTS.items():
        checks.append(check_tool(name, minimum, version_args))
        if name == "docker":
            checks.append(check_docker_daemon())

    if not args.skip_pre_commit:
        checks.append(check_tool("pre-commit", (4, 0), ["--version"]))

    for _, message in checks:
        print(message)
    return 0 if all(passed for passed, _ in checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
