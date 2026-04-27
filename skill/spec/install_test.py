from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path


class InstallScriptTest(unittest.TestCase):
    def test_install_script_excludes_pycache_directories(self) -> None:
        skill_root = Path(__file__).resolve().parents[1]

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            home_dir = tmp_path / "home"
            home_dir.mkdir()
            (home_dir / ".agents").mkdir()

            result = subprocess.run(
                ["sh", str(skill_root / "install.sh")],
                cwd=skill_root,
                env={
                    **dict(__import__("os").environ),
                    "HOME": str(home_dir),
                },
                capture_output=True,
                check=True,
                text=True,
            )

            installed_root = home_dir / ".agents" / "skills" / "xinyi-drink"
            self.assertTrue(installed_root.exists())
            self.assertFalse(any(installed_root.rglob("__pycache__")))
            self.assertIn("已安装 xinyi-drink 到", result.stdout)
            self.assertIn("/xinyi-drink 给我推荐一杯新一的咖啡", result.stdout)
            self.assertIn(
                "如果仿生人会梦见电子羊，那小龙虾也需要一杯充满灵魂的赛博咖啡",
                result.stdout,
            )
            self.assertIn("告知小程序绑定的手机号", result.stdout)

    def test_install_script_maps_openclaw_to_openclaw_skills_dir(self) -> None:
        skill_root = Path(__file__).resolve().parents[1]

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            home_dir = tmp_path / "home"
            home_dir.mkdir()

            result = subprocess.run(
                ["sh", str(skill_root / "install.sh"), "--dry-run", "--platform", "openclaw"],
                cwd=skill_root,
                env={
                    **dict(__import__("os").environ),
                    "HOME": str(home_dir),
                },
                capture_output=True,
                check=True,
                text=True,
            )

            self.assertIn(
                str(home_dir / ".openclaw" / "skills" / "xinyi-drink"),
                result.stdout,
            )

    def test_install_script_maps_hermes_to_hermes_skills_dir(self) -> None:
        skill_root = Path(__file__).resolve().parents[1]

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            home_dir = tmp_path / "home"
            home_dir.mkdir()

            result = subprocess.run(
                ["sh", str(skill_root / "install.sh"), "--dry-run", "--platform", "hermes"],
                cwd=skill_root,
                env={
                    **dict(__import__("os").environ),
                    "HOME": str(home_dir),
                },
                capture_output=True,
                check=True,
                text=True,
            )

            self.assertIn(
                str(home_dir / ".hermes" / "skills" / "xinyi-drink"),
                result.stdout,
            )

    def test_install_script_backs_up_existing_installation_before_overwrite(self) -> None:
        skill_root = Path(__file__).resolve().parents[1]

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            home_dir = tmp_path / "home"
            home_dir.mkdir()
            (home_dir / ".agents").mkdir()

            env = {
                **dict(__import__("os").environ),
                "HOME": str(home_dir),
            }
            subprocess.run(
                ["sh", str(skill_root / "install.sh")],
                cwd=skill_root,
                env=env,
                capture_output=True,
                check=True,
                text=True,
            )
            installed_root = home_dir / ".agents" / "skills" / "xinyi-drink"
            marker = installed_root / "local-marker.txt"
            marker.write_text("previous install", encoding="utf-8")

            result = subprocess.run(
                ["sh", str(skill_root / "install.sh")],
                cwd=skill_root,
                env=env,
                capture_output=True,
                check=True,
                text=True,
            )

            backups = sorted((home_dir / ".agents" / "skills").glob("xinyi-drink.backup.*"))
            self.assertTrue(backups)
            self.assertTrue((backups[-1] / "local-marker.txt").exists())
            self.assertIn("已备份旧版本到", result.stdout)


if __name__ == "__main__":
    unittest.main()
