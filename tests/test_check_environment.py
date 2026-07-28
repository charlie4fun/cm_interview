import subprocess
import unittest
from unittest.mock import patch

from scripts.check_environment import (
    check_docker_daemon,
    check_python_venv,
    check_python_version,
    check_tool,
    version_from,
)


class EnvironmentCheckTest(unittest.TestCase):
    def test_version_from_common_tool_output(self) -> None:
        self.assertEqual(version_from("Docker version 27.1.2"), (27, 1, 2))
        self.assertEqual(version_from("Client Version: v1.31.4"), (1, 31, 4))

    def test_python_version_below_supported_range(self) -> None:
        self.assertEqual(
            check_python_version((3, 11, 9)),
            (
                False,
                "MISSING: Python - current version: 3.11.9; "
                "desired version: >= 3.12, < 3.14",
            ),
        )

    def test_python_version_in_supported_range(self) -> None:
        self.assertEqual(
            check_python_version((3, 12, 0)),
            (True, "OK: Python 3.12.0"),
        )

    def test_python_version_at_upper_bound(self) -> None:
        self.assertEqual(
            check_python_version((3, 14, 0)),
            (
                False,
                "MISSING: Python - current version: 3.14.0; "
                "desired version: >= 3.12, < 3.14",
            ),
        )

    @patch("scripts.check_environment.executable", return_value=None)
    def test_missing_tool(self, _executable: object) -> None:
        self.assertEqual(
            check_tool("kubectl", (1, 31), ["version"]),
            (False, "MISSING: kubectl - not found"),
        )

    @patch("scripts.check_environment.executable", return_value="/usr/bin/docker")
    @patch("scripts.check_environment.subprocess.run")
    def test_outdated_tool(self, run: object, _executable: object) -> None:
        run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="Docker version 23.0.6", stderr=""
        )
        self.assertEqual(
            check_tool("docker", (24, 0), ["--version"]),
            (
                False,
                "MISSING: Docker - current version: 23.0.6; "
                "desired version: >= 24.0",
            ),
        )

    @patch("scripts.check_environment.executable", return_value="/usr/bin/docker")
    @patch("scripts.check_environment.subprocess.run")
    def test_available_tool(self, run: object, _executable: object) -> None:
        run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="Docker version 27.1.2", stderr=""
        )
        self.assertEqual(
            check_tool("docker", (24, 0), ["--version"]),
            (True, "OK: Docker 27.1.2"),
        )

    @patch(
        "scripts.check_environment.executable",
        return_value=".venv/bin/pre-commit",
    )
    @patch("scripts.check_environment.subprocess.run")
    def test_project_local_pre_commit(self, run: object, _executable: object) -> None:
        run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="pre-commit 4.6.1", stderr=""
        )
        self.assertEqual(
            check_tool("pre-commit", (4, 0), ["--version"]),
            (True, "OK: pre-commit 4.6.1 (.venv)"),
        )

    @patch("scripts.check_environment.executable", return_value="/usr/bin/docker")
    @patch("scripts.check_environment.subprocess.run")
    def test_inaccessible_docker_daemon(
        self, run: object, _executable: object
    ) -> None:
        run.return_value = subprocess.CompletedProcess(args=[], returncode=1)
        self.assertEqual(
            check_docker_daemon(),
            (False, "MISSING: Docker daemon - inaccessible"),
        )

    @patch("scripts.check_environment.subprocess.run")
    def test_python_venv_is_available(self, run: object) -> None:
        run.return_value = subprocess.CompletedProcess(args=[], returncode=0)
        self.assertEqual(
            check_python_venv(),
            (True, "OK: Python venv available"),
        )

    @patch("scripts.check_environment.subprocess.run")
    @patch("scripts.check_environment.sys.version_info")
    def test_python_venv_is_missing(
        self, version_info: object, run: object
    ) -> None:
        version_info.major = 3
        version_info.minor = 12
        run.return_value = subprocess.CompletedProcess(args=[], returncode=1)
        self.assertEqual(
            check_python_venv(),
            (
                False,
                "MISSING: Python venv - install python3.12-venv on Debian/Ubuntu",
            ),
        )


if __name__ == "__main__":
    unittest.main()
