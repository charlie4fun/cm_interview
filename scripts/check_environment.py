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
PYTHON_MIN_VERSION = (3, 12)
PREREQUISITES = "See docs/developer-setup.md."


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


def check_tool(name: str, minimum: tuple[int, ...], args: list[str]) -> str | None:
    command = executable(name)
    required = ".".join(map(str, minimum))
    if command is None:
        return f"{name} >= {required} is required. {PREREQUISITES}"

    result = subprocess.run(
        [command, *args], capture_output=True, text=True, check=False
    )
    detected = version_from(f"{result.stdout}\n{result.stderr}")
    if result.returncode != 0 or detected is None:
        return f"Could not determine the {name} version. {PREREQUISITES}"
    if detected < minimum:
        current = ".".join(map(str, detected))
        return f"{name} >= {required} is required; found {current}. {PREREQUISITES}"
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-pre-commit", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    errors: list[str] = []

    if sys.version_info < PYTHON_MIN_VERSION:
        errors.append(f"Python >= 3.12 is required. {PREREQUISITES}")

    for name, (minimum, version_args) in REQUIREMENTS.items():
        if error := check_tool(name, minimum, version_args):
            errors.append(error)

    if not args.skip_pre_commit:
        if error := check_tool("pre-commit", (4, 0), ["--version"]):
            errors.append(error)

    docker = executable("docker")
    if docker and subprocess.run(
        [docker, "info"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    ).returncode:
        errors.append("Docker daemon is unavailable. Start Docker and try again.")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("Environment looks good")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
