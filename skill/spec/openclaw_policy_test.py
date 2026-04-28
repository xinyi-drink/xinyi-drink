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
        self.assertIn("各门店现在有多少杯在做、要等多久", skill_md)
        self.assertIn("苦尽甘来拿铁热量多少", skill_md)
        self.assertIn("今天北京21°C，想喝茶饮，推荐一杯", skill_md)
        self.assertIn("实时接口失败", skill_md)
        self.assertNotIn("如果你在附近", skill_md)

    def test_skill_json_declares_scripts_network_and_privacy(self) -> None:
        skill_root = Path(__file__).resolve().parents[1]
        payload = json.loads((skill_root / "skill.json").read_text(encoding="utf-8"))
        skill_md = (skill_root / "SKILL.md").read_text(encoding="utf-8")

        self.assertEqual(payload["name"], "xinyi-drink")
        self.assertIn(f"version: {payload['version']}", skill_md)
        self.assertEqual(payload["homepage"], "https://github.com/xinyi-drink/xinyi-drink")
        self.assertEqual(payload["repository"], "https://github.com/xinyi-drink/xinyi-drink")
        self.assertEqual(payload["source"]["type"], "git")
        self.assertEqual(payload["source"]["url"], "https://github.com/xinyi-drink/xinyi-drink")
        self.assertEqual(payload["source"]["directory"], "skill")
        self.assertEqual(payload["install"]["type"], "local-script")
        self.assertEqual(payload["install"]["script"], "install.sh")
        self.assertEqual(payload["install"]["dry_run"], "install.sh --dry-run")
        self.assertIn("~/.openclaw/skills/xinyi-drink", payload["install"]["writes_to"])
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
        for keyword in ("今天喝什么", "困了", "下午茶", "上班犯困", "提神", "清爽", "热量", "果茶", "等待时长", "饮品偏好"):
            self.assertIn(keyword, keywords)

        tool_descriptions = {
            tool["name"]: tool["description"]
            for tool in payload["tools"]
        }
        self.assertIn("用户问“大礼包怎么领取”", tool_descriptions["claim_reward"])
        self.assertIn("用户问“新一有哪些门店”", tool_descriptions["fetch_stores"])
        self.assertIn("今天北京21°C想喝茶饮", tool_descriptions["recommend_drink"])
        self.assertIn("苦尽甘来拿铁热量多少", tool_descriptions["recommend_drink"])
        self.assertIn("我购买过多少杯", tool_descriptions["recommend_drink"])

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

    def test_user_facing_capability_examples_are_specific(self) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        readme = (repo_root / "README.md").read_text(encoding="utf-8")
        intro_section = readme.split("## Skill用户大礼包", 1)[0]

        self.assertIn("高质量问法", intro_section)
        self.assertNotIn("数据来源", intro_section)
        self.assertNotIn("/skill/xinyi/", intro_section)
        for example in (
            "我想领取Skill用户大礼包，需要发哪个手机号？",
            "我购买过多少杯新一？我的饮品偏好是什么？",
            "各门店现在有多少杯在做？大概要等多久？",
            "苦尽甘来拿铁热量多少？",
            "新一有哪些果茶？想喝清爽不太甜的",
            "今天北京21°C，想喝茶饮，推荐一杯",
            "下午犯困但不想喝太苦，有什么适合的？",
        ):
            self.assertIn(example, intro_section)


if __name__ == "__main__":
    unittest.main()
