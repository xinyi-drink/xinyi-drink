from __future__ import annotations

import json
import unittest
from pathlib import Path


class OpenClawPolicyTest(unittest.TestCase):
    def test_skill_md_frontmatter_declares_openclaw_runtime_metadata(self) -> None:
        skill_root = Path(__file__).resolve().parents[1]
        skill_md = (skill_root / "SKILL.md").read_text(encoding="utf-8")
        payload = json.loads((skill_root / "skill.json").read_text(encoding="utf-8"))

        frontmatter = skill_md.split("---", 2)[1]
        self.assertIn("name: xinyi-drink", frontmatter)
        self.assertRegex(frontmatter, r"version: \d+\.\d+\.\d+")
        self.assertIn(f"version: {payload['version']}", frontmatter)
        self.assertIn("keywords:", frontmatter)
        self.assertIn("metadata:", frontmatter)
        self.assertIn("openclaw:", frontmatter)
        self.assertIn("packageType: executable-skill", frontmatter)
        self.assertIn("instructionOnly: false", frontmatter)
        self.assertIn("type: local-script", frontmatter)
        self.assertIn("script: install.sh", frontmatter)
        self.assertIn("dryRun: install.sh --dry-run", frontmatter)
        self.assertIn("type: python-scripts", frontmatter)
        self.assertIn("requiredEnv: []", frontmatter)
        self.assertIn("optionalEnv:", frontmatter)
        self.assertIn("XINYI_API_BASE_URL", frontmatter)
        self.assertIn("defaultApiBaseUrl: https://ai.xinyicoffee.com/api", frontmatter)
        self.assertIn("path: /skill/xinyi/claim", frontmatter)
        self.assertIn("sends: [mobile]", frontmatter)
        self.assertIn("defaultPath: ~/.xinyi-drink/state.json", frontmatter)
        self.assertIn("autoReadPolicy:", frontmatter)
        self.assertNotIn("networkAccess:", frontmatter)
        self.assertNotIn("environment:", frontmatter)

    def test_skill_md_contains_compact_operating_guidance(self) -> None:
        skill_root = Path(__file__).resolve().parents[1]
        skill_md = (skill_root / "SKILL.md").read_text(encoding="utf-8")
        body = skill_md.split("---", 2)[2]

        self.assertLessEqual(len(body.splitlines()), 130)
        for heading in ("## AI 必读", "## 触发表", "## 主流程", "## 盲区应对", "## 内嵌示例"):
            self.assertIn(heading, skill_md)
        self.assertIn("懂茶饮也懂咖啡、不掉书袋的姐姐", skill_md)
        self.assertIn("今天这个温度喝它刚好", skill_md)
        self.assertIn("帮我领取新一Skill福利", skill_md)
        self.assertIn("望京店目前有多少杯待做，等待时间多久", skill_md)
        self.assertIn("某某饮品热量多少", skill_md)
        self.assertIn("给我推荐一杯适合当下午茶的饮品", skill_md)
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
        self.assertIn("用户问“帮我领取新一Skill福利”", tool_descriptions["claim_reward"])
        self.assertIn("用户问“新一咖啡有哪些门店”", tool_descriptions["fetch_stores"])
        self.assertIn("望京店目前有多少杯待做", tool_descriptions["fetch_stores"])
        self.assertIn("给我推荐一杯适合当下午茶的饮品", tool_descriptions["recommend_drink"])
        self.assertIn("默认不读取本地缓存手机号", tool_descriptions["recommend_drink"])
        self.assertIn("useSavedMobile", tool_descriptions["recommend_drink"])
        self.assertIn("某某饮品热量多少", tool_descriptions["recommend_drink"])
        self.assertIn("有哪些不太甜的果茶", tool_descriptions["recommend_drink"])
        self.assertIn("我买过多少杯", tool_descriptions["recommend_drink"])
        self.assertIn("帮我分析我的口味偏好", tool_descriptions["recommend_drink"])
        recommend_schema = next(
            tool["inputSchema"]
            for tool in payload["tools"]
            if tool["name"] == "recommend_drink"
        )
        self.assertIn("useSavedMobile", recommend_schema["properties"])
        self.assertIn("默认不读取缓存手机号", payload["localStorage"]["autoReadPolicy"])

    def test_recommend_drink_does_not_claim_or_read_saved_mobile_by_default(self) -> None:
        skill_root = Path(__file__).resolve().parents[1]
        script = (skill_root / "scripts" / "recommend_drink.py").read_text(encoding="utf-8")

        self.assertIn("--use-saved-mobile", script)
        self.assertIn("resolved_mobile = args.mobile", script)
        self.assertIn("if not resolved_mobile and args.use_saved_mobile:", script)
        self.assertNotIn("post_json", script)
        self.assertNotIn("/skill/xinyi/claim", script)

    def test_readme_documents_default_backend_and_phone_data_flow(self) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        readme = (repo_root / "README.md").read_text(encoding="utf-8")

        self.assertIn("Skill用户大礼包", readme)
        self.assertIn("skill/SKILL.md", readme)
        self.assertIn("metadata.openclaw", readme)
        self.assertIn("skill/skill.json", readme)
        self.assertIn("发布前两处版本号需要保持一致", readme)
        self.assertIn("默认后端", readme)
        self.assertIn("https://ai.xinyicoffee.com/api", readme)
        self.assertIn("POST /skill/xinyi/claim", readme)
        self.assertIn("GET /skill/xinyi/context", readme)
        self.assertIn("手机号会作为请求数据发送到后端", readme)
        self.assertIn("普通推荐、门店和菜单查询不会自动复用缓存手机号", readme)
        self.assertIn("活动总览、订单/偏好分析场景复用缓存", readme)
        self.assertIn("不是 instruction-only", readme)

    def test_user_facing_capability_examples_are_specific(self) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        readme = (repo_root / "README.md").read_text(encoding="utf-8")
        intro_section = readme.split("## Skill用户大礼包", 1)[0]

        self.assertIn("高质量问法", intro_section)
        self.assertNotIn("数据来源", intro_section)
        self.assertNotIn("/skill/xinyi/", intro_section)
        for example in (
            "帮我领取新一Skill福利。",
            "我买过多少杯？",
            "帮我分析我的口味偏好。",
            "新一咖啡有哪些门店？",
            "望京店目前有多少杯待做，等待时间多久？",
            "某某饮品热量多少？",
            "有哪些不太甜的果茶？",
            "给我推荐一杯适合当下午茶的饮品。",
        ):
            self.assertIn(example, intro_section)


if __name__ == "__main__":
    unittest.main()
