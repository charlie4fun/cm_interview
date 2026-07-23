import subprocess
import unittest
from unittest.mock import patch

from scripts.check_environment import check_docker_daemon, check_tool, version_from


class EnvironmentCheckTest(unittest.TestCase):
    def test_version_from_common_tool_output(self) -> None:
        self.assertEqual(version_from("Docker version 27.1.2"), (27, 1, 2))
        self.assertEqual(version_from("Client Version: v1.31.4"), (1, 31, 4))

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


if __name__ == "__main__":
    unittest.main()
