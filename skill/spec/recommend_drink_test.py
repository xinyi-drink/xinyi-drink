from __future__ import annotations

import io
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import recommend_drink


class RecommendDrinkScriptTest(unittest.TestCase):
    @patch.object(recommend_drink, "post_json")
    @patch.object(recommend_drink, "save_mobile")
    @patch.object(recommend_drink, "load_mobile", return_value=None)
    @patch.object(
        recommend_drink,
        "load_config",
        return_value={
            "apiBaseUrl": "http://127.0.0.1:8020",
            "timeoutSeconds": 5,
        },
    )
    @patch.object(recommend_drink, "fetch_json")
    def test_main_outputs_llm_friendly_text_instead_of_json(
        self,
        fetch_json_mock,
        _load_config_mock,
        _load_mobile_mock,
        save_mobile_mock,
        post_json_mock,
    ) -> None:
        events: list[tuple[str, str]] = []
        save_mobile_mock.side_effect = lambda mobile: events.append(("save", mobile))
        post_json_mock.side_effect = lambda url, timeout, payload: (
            events.append(("claim", payload["mobile"])),
            {
                "data": {
                    "kind": "already_claimed",
                    "user": {"mobile": "15712459595", "nickname": "双龙"},
                }
            },
        )[1]
        fetch_json_mock.return_value = {
            "data": {
                "goods": [
                    {
                        "name": "杨枝甘露|轻乳版",
                        "categories": ["果咖", "轻负担"],
                        "price": "16.80",
                        "cupSizes": ["大杯"],
                        "temperatures": ["少冰", "去冰"],
                        "sugarLevels": ["3分糖", "5分糖"],
                        "calories": "120\nkcal",
                        "ingredients": ["芒果", "西柚"],
                    }
                ],
                "stores": [
                    {
                        "name": "幂茶幂咖|望京店",
                        "address": "北京市朝阳区望京街9号\n商业楼1层",
                        "facilities": "外摆区，休息区，宠物友好。",
                        "storeMobile": "010-12345678",
                        "businessStatus": 1,
                        "labels": [{"name": "休息区"}],
                        "lat": "39.990326",
                        "lng": "116.483659",
                        "operatingStatus": 1,
                        "realtimeState": 1,
                        "makingCupCount": 4,
                        "makingCupMinutes": 18,
                        "storeType": 2,
                        "supportUnattendedMode": 1,
                    }
                ],
                "weather": {
                    "city": "Beijing",
                    "condition": "sunny",
                    "temperatureC": 26,
                },
                "orders": {
                    "orders": [
                        {
                            "createdAt": "2025-08-08 14:16:25",
                            "orderSn": "20250808141625274275",
                            "state": 2,
                            "pickNo": "Z108",
                            "serverTime": "2025-08-08 14:36:25",
                            "goodsNum": 1,
                            "goods": [
                                {
                                    "name": "葡萄毛尖轻咖",
                                    "spec": "中杯",
                                    "attr": "正常冰|7分糖",
                                }
                            ],
                            "store": {
                                "name": "幂茶幂咖望京小街店",
                            },
                        }
                    ]
                },
            }
        }

        stdout = io.StringIO()

        with patch.object(
            sys,
            "argv",
            [
                "recommend_drink.py",
                "--mobile",
                "15712459595",
                "--query",
                "想喝不苦的",
                "--scene",
                "下午茶",
                "--preference",
                "低卡",
            ],
        ), patch("sys.stdout", stdout):
            exit_code = recommend_drink.main()

        output = stdout.getvalue()

        self.assertEqual(exit_code, 0)
        self.assertIn("## 用户上下文", output)
        self.assertIn("## 商品列表", output)
        self.assertIn("## 门店列表", output)
        self.assertIn("## 订单历史", output)
        self.assertIn("## 推荐素材", output)
        self.assertIn("## 回答要求", output)
        self.assertIn("## 门店摘要建议", output)
        self.assertNotIn('"context"', output)
        self.assertIn("杨枝甘露\\|轻乳版", output)
        self.assertIn("正常冰\\|7分糖", output)
        self.assertIn("120<br>kcal", output)
        self.assertIn("北京市朝阳区望京街9号<br>商业楼1层", output)
        self.assertIn("010-12345678", output)
        self.assertIn("宠物友好", output)
        self.assertIn("外摆区，休息区，宠物友好。", output)
        self.assertIn("休息区", output)
        self.assertIn("Box 门店", output)
        self.assertIn("支持无人模式", output)
        self.assertIn("制作中", output)
        self.assertIn("主推荐文案由大模型根据下方素材自行生成", output)
        self.assertIn("推荐理由请显式展开 2-4 条", output)
        self.assertIn("推荐候选饮品：杨枝甘露|轻乳版", output)
        self.assertIn("挺舒服", output)
        self.assertIn("主要配料：芒果、西柚", output)
        self.assertIn("至少给出 1-2 家具体门店", output)
        self.assertIn("若有门店电话也一并给出", output)
        self.assertIn("若门店返回了 facilities", output)
        self.assertIn("门店名：幂茶幂咖|望京店", output)
        self.assertIn("设施：外摆区，休息区，宠物友好。", output)
        self.assertIn("特色：外摆区、休息区、宠物友好、支持无人模式、Box 门店", output)
        self.assertEqual(fetch_json_mock.call_count, 1)
        self.assertEqual(post_json_mock.call_count, 1)
        self.assertEqual(
            post_json_mock.call_args_list[0].args,
            (
                "http://127.0.0.1:8020/skill/xinyi/claim",
                5,
                {"mobile": "15712459595"},
            ),
        )
        self.assertEqual(
            events[:2],
            [("save", "15712459595"), ("claim", "15712459595")],
        )
        self.assertEqual(
            fetch_json_mock.call_args_list[0].args,
            (
                "http://127.0.0.1:8020/skill/xinyi/context?mobile=15712459595",
                5,
            ),
        )
        save_mobile_mock.assert_called_once_with("15712459595")

    @patch.object(recommend_drink, "post_json")
    @patch.object(recommend_drink, "save_mobile")
    @patch.object(recommend_drink, "load_mobile", return_value=None)
    @patch.object(
        recommend_drink,
        "load_config",
        return_value={
            "apiBaseUrl": "http://127.0.0.1:8020",
            "timeoutSeconds": 5,
        },
    )
    @patch.object(recommend_drink, "fetch_json")
    def test_main_falls_back_to_generic_copy_when_weather_api_fails(
        self,
        fetch_json_mock,
        _load_config_mock,
        _load_mobile_mock,
        save_mobile_mock,
        post_json_mock,
    ) -> None:
        post_json_mock.return_value = {
            "data": {
                "kind": "already_claimed",
                "user": {"mobile": "15712459595", "nickname": "双龙"},
            }
        }
        fetch_json_mock.return_value = {
            "data": {
                "goods": [
                    {
                        "name": "葡萄毛尖轻咖",
                        "categories": ["果咖"],
                        "price": "16.80",
                        "cupSizes": ["大杯"],
                        "temperatures": ["热", "少冰"],
                        "sugarLevels": ["3分糖"],
                        "calories": "120 kcal",
                        "ingredients": ["葡萄"],
                    }
                ],
                "stores": [],
                "weather": None,
                "orders": {
                    "orders": [
                        {
                            "createdAt": "2025-08-08 14:16:25",
                            "orderSn": "20250808141625274275",
                            "state": 6,
                            "pickNo": "A001",
                            "serverTime": "2025-08-08 14:36:25",
                            "goodsNum": 1,
                            "goods": [
                                {
                                    "name": "葡萄毛尖轻咖",
                                    "spec": "大杯",
                                    "attr": "热 / 3分糖",
                                }
                            ],
                            "store": {"name": "幂茶幂咖望京店"},
                        }
                    ]
                },
            }
        }

        stdout = io.StringIO()

        with patch.object(
            sys,
            "argv",
            [
                "recommend_drink.py",
                "--mobile",
                "15712459595",
            ],
        ), patch("sys.stdout", stdout):
            exit_code = recommend_drink.main()

        output = stdout.getvalue()

        self.assertEqual(exit_code, 0)
        self.assertIn("推荐候选饮品：葡萄毛尖轻咖", output)
        self.assertIn("主推荐文案由大模型根据下方素材自行生成", output)
        self.assertIn("推荐理由请显式展开 2-4 条", output)
        self.assertNotIn("今天天气", output)
        self.assertEqual(post_json_mock.call_count, 1)
        save_mobile_mock.assert_called_once_with("15712459595")

    @patch.object(recommend_drink, "post_json")
    @patch.object(recommend_drink, "save_mobile")
    @patch.object(recommend_drink, "load_mobile", return_value="15712459595")
    @patch.object(
        recommend_drink,
        "load_config",
        return_value={
            "apiBaseUrl": "http://127.0.0.1:8020",
            "timeoutSeconds": 5,
        },
    )
    @patch.object(recommend_drink, "fetch_json")
    def test_main_outputs_debug_logs_to_stderr(
        self,
        fetch_json_mock,
        _load_config_mock,
        _load_mobile_mock,
        save_mobile_mock,
        post_json_mock,
    ) -> None:
        post_json_mock.return_value = {
            "data": {
                "kind": "already_claimed",
                "user": {"mobile": "15712459595", "nickname": "双龙"},
            }
        }
        fetch_json_mock.return_value = {
            "data": {
                "goods": [],
                "stores": [],
                "weather": {"city": "Beijing", "condition": "sunny", "temperatureC": 26},
                "orders": None,
            }
        }

        stdout = io.StringIO()
        stderr = io.StringIO()

        with patch.object(
            sys,
            "argv",
            ["recommend_drink.py", "--debug"],
        ), patch("sys.stdout", stdout), patch("sys.stderr", stderr):
            exit_code = recommend_drink.main()

        self.assertEqual(exit_code, 0)
        self.assertIn("DEBUG recommend_drink: resolved mobile from local state", stderr.getvalue())
        self.assertIn("DEBUG recommend_drink: posting claim request to http://127.0.0.1:8020/skill/xinyi/claim", stderr.getvalue())
        self.assertIn("DEBUG recommend_drink: fetching context from http://127.0.0.1:8020/skill/xinyi/context?mobile=15712459595", stderr.getvalue())
        self.assertIn("DEBUG recommend_drink: context includes weather data", stderr.getvalue())
        self.assertIn("## 用户上下文", stdout.getvalue())
        save_mobile_mock.assert_not_called()

    @patch.object(recommend_drink, "post_json")
    @patch.object(recommend_drink, "save_mobile")
    @patch.object(recommend_drink, "load_mobile", return_value=None)
    @patch.object(
        recommend_drink,
        "load_config",
        return_value={
            "apiBaseUrl": "http://127.0.0.1:8020",
            "timeoutSeconds": 5,
        },
    )
    @patch.object(recommend_drink, "fetch_json")
    def test_main_does_not_save_or_use_mobile_when_claim_does_not_match_user(
        self,
        fetch_json_mock,
        _load_config_mock,
        _load_mobile_mock,
        save_mobile_mock,
        post_json_mock,
    ) -> None:
        post_json_mock.return_value = {
            "data": {
                "kind": "unregistered",
                "user": None,
            }
        }
        fetch_json_mock.return_value = {
            "data": {"goods": [], "stores": [], "weather": None, "orders": None}
        }

        stdout = io.StringIO()

        with patch.object(
            sys,
            "argv",
            ["recommend_drink.py", "--mobile", "15712459595"],
        ), patch("sys.stdout", stdout):
            exit_code = recommend_drink.main()

        self.assertEqual(exit_code, 0)
        self.assertEqual(post_json_mock.call_count, 1)
        self.assertEqual(
            fetch_json_mock.call_args_list[0].args,
            (
                "http://127.0.0.1:8020/skill/xinyi/context?mobile=15712459595",
                5,
            ),
        )
        save_mobile_mock.assert_called_once_with("15712459595")


if __name__ == "__main__":
    unittest.main()
