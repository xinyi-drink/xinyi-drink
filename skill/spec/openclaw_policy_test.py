from __future__ import annotations

import json
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

    def test_skill_json_declares_scripts_network_and_privacy(self) -> None:
        skill_root = Path(__file__).resolve().parents[1]
        payload = json.loads((skill_root / "skill.json").read_text(encoding="utf-8"))
        skill_md = (skill_root / "SKILL.md").read_text(encoding="utf-8")

        self.assertEqual(payload["name"], "xinyi-drink")
        self.assertIn(f"version: {payload['version']}", skill_md)
        self.assertEqual(payload["runtime"]["type"], "python-scripts")
        self.assertTrue(payload["runtime"]["requires_network"])
        self.assertIn("scripts/claim_reward.py", payload["runtime"]["entrypoints"])
        self.assertIn("scripts/fetch_stores.py", payload["runtime"]["entrypoints"])
        self.assertIn("scripts/recommend_drink.py", payload["runtime"]["entrypoints"])

        endpoint_paths = {
            endpoint["path"]
            for endpoint in payload["network"]["endpoints"]
        }
        self.assertEqual(
            endpoint_paths,
            {
                "/skill/xinyi/claim",
                "/skill/xinyi/context",
                "/skill/xinyi/stores",
            },
        )
        claim_endpoint = next(
            endpoint
            for endpoint in payload["network"]["endpoints"]
            if endpoint["path"] == "/skill/xinyi/claim"
        )
        self.assertIn("mobile", claim_endpoint["sends"])
        self.assertEqual(payload["localStorage"]["defaultPath"], "~/.xinyi-drink/state.json")
        self.assertEqual(payload["openclaw"]["packageType"], "executable-skill")
        self.assertFalse(payload["openclaw"]["instructionOnly"])

    def test_readme_documents_default_backend_and_phone_data_flow(self) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        readme = (repo_root / "README.md").read_text(encoding="utf-8")

        self.assertIn("Skill 用户大礼包", readme)
        self.assertIn("skill/skill.json", readme)
        self.assertIn("默认后端", readme)
        self.assertIn("https://ai.xinyicoffee.com/api", readme)
        self.assertIn("POST /skill/xinyi/claim", readme)
        self.assertIn("GET /skill/xinyi/context", readme)
        self.assertIn("手机号会作为请求数据发送到后端", readme)
        self.assertIn("不是 instruction-only", readme)


if __name__ == "__main__":
    unittest.main()
