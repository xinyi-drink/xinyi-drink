from __future__ import annotations

import json
import unittest
from pathlib import Path


class OpenClawPolicyTest(unittest.TestCase):
    def test_skill_md_frontmatter_stays_llm_focused(self) -> None:
        skill_root = Path(__file__).resolve().parents[1]
        skill_md = (skill_root / "SKILL.md").read_text(encoding="utf-8")

        frontmatter = skill_md.split("---", 2)[1]
        self.assertIn("name: xinyi-drink", frontmatter)
        self.assertRegex(frontmatter, r"version: \d+\.\d+\.\d+")
        self.assertIn("keywords:", frontmatter)
        self.assertNotIn("networkAccess:", frontmatter)
        self.assertNotIn("localStorage:", frontmatter)
        self.assertNotIn("environment:", frontmatter)
        self.assertNotIn("openclaw:", frontmatter)
        self.assertNotIn("defaultApiBaseUrl", frontmatter)

    def test_skill_md_contains_compact_operating_guidance(self) -> None:
        skill_root = Path(__file__).resolve().parents[1]
        skill_md = (skill_root / "SKILL.md").read_text(encoding="utf-8")

        self.assertLessEqual(len(skill_md.splitlines()), 130)
        for heading in ("## AI 必读", "## 触发表", "## 主流程", "## 盲区应对", "## 内嵌示例"):
            self.assertIn(heading, skill_md)
        self.assertIn("懂茶饮也懂咖啡、不掉书袋的姐姐", skill_md)
        self.assertIn("今天这个温度喝它刚好", skill_md)
        self.assertIn("实时接口失败", skill_md)
        self.assertNotIn("如果你在附近", skill_md)

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

        keywords = set(payload["keywords"])
        for keyword in ("今天喝什么", "困了", "下午茶", "上班犯困", "提神", "清爽"):
            self.assertIn(keyword, keywords)

        tool_descriptions = {
            tool["name"]: tool["description"]
            for tool in payload["tools"]
        }
        self.assertIn("用户问“大礼包怎么领取”", tool_descriptions["claim_reward"])
        self.assertIn("用户问“新一有哪些门店”", tool_descriptions["fetch_stores"])
        self.assertIn("用户问“今天喝什么”", tool_descriptions["recommend_drink"])

    def test_readme_documents_default_backend_and_phone_data_flow(self) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        readme = (repo_root / "README.md").read_text(encoding="utf-8")

        self.assertIn("Skill用户大礼包", readme)
        self.assertIn("skill/skill.json", readme)
        self.assertIn("默认后端", readme)
        self.assertIn("https://ai.xinyicoffee.com/api", readme)
        self.assertIn("POST /skill/xinyi/claim", readme)
        self.assertIn("GET /skill/xinyi/context", readme)
        self.assertIn("手机号会作为请求数据发送到后端", readme)
        self.assertIn("不是 instruction-only", readme)


if __name__ == "__main__":
    unittest.main()
