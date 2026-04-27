from __future__ import annotations

import unittest
from pathlib import Path


class OpenClawPolicyTest(unittest.TestCase):
    def test_skill_metadata_declares_executable_network_and_local_storage(self) -> None:
        skill_root = Path(__file__).resolve().parents[1]
        skill_md = (skill_root / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("packageType: executable-skill", skill_md)
        self.assertIn("instructionOnly: false", skill_md)
        self.assertIn("defaultApiBaseUrl: https://ai.xinyicoffee.com/api", skill_md)
        self.assertIn("/skill/xinyi/claim", skill_md)
        self.assertIn("/skill/xinyi/context", skill_md)
        self.assertIn("~/.xinyi-drink/state.json", skill_md)
        self.assertIn("XINYI_API_BASE_URL", skill_md)
        self.assertIn("XINYI_DRINK_STATE_FILE", skill_md)

    def test_readme_documents_default_backend_and_phone_data_flow(self) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        readme = (repo_root / "README.md").read_text(encoding="utf-8")

        self.assertIn("默认后端", readme)
        self.assertIn("https://ai.xinyicoffee.com/api", readme)
        self.assertIn("POST /skill/xinyi/claim", readme)
        self.assertIn("GET /skill/xinyi/context", readme)
        self.assertIn("手机号会作为请求数据发送到后端", readme)
        self.assertIn("不是 instruction-only", readme)


if __name__ == "__main__":
    unittest.main()
