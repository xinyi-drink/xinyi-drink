from __future__ import annotations

import io
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import recommend_drink
from skill_http import SkillHttpError


class RecommendDrinkScriptTest(unittest.TestCase):
    def setUp(self) -> None:
        self.mark_activity_joined_patcher = patch.object(recommend_drink, "mark_activity_joined")
        self.mark_activity_not_joined_patcher = patch.object(recommend_drink, "mark_activity_not_joined")
        self.load_activity_joined_patcher = patch.object(
            recommend_drink,
            "load_activity_joined",
            return_value=None,
        )
        self.mark_activity_joined_mock = self.mark_activity_joined_patcher.start()
        self.mark_activity_not_joined_mock = self.mark_activity_not_joined_patcher.start()
        self.load_activity_joined_mock = self.load_activity_joined_patcher.start()
        self.addCleanup(self.mark_activity_joined_patcher.stop)
        self.addCleanup(self.mark_activity_not_joined_patcher.stop)
        self.addCleanup(self.load_activity_joined_patcher.stop)

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
        self.load_activity_joined_mock.return_value = True
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
        self.assertIn("像熟悉的店员给朋友建议一样自然", output)
        self.assertIn("回答需要有层次和重点", output)
        self.assertIn("主推饮品名和门店名必须加粗", output)
        self.assertIn("少量使用合适 emoji", output)
        self.assertIn("不要使用“推荐理由”", output)
        self.assertIn("有人情味", output)
        self.assertIn("不要使用“根据你的历史订单偏好”", output)
        self.assertIn("用户已参加过活动，不要再输出登录小程序", output)
        self.assertNotIn("领取见面礼，并告知小程序绑定的手机号", output)
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
        self.mark_activity_joined_mock.assert_called_once_with("15712459595")
        self.mark_activity_not_joined_mock.assert_not_called()
        self.load_activity_joined_mock.assert_called_once_with("15712459595")

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
    def test_activity_query_includes_lobster_activity(
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
        self.load_activity_joined_mock.return_value = True
        fetch_json_mock.return_value = {
            "data": {
                "goods": [
                    {
                        "name": "中烘美式·耶加雪菲",
                        "categories": ["买一赠一福利"],
                        "price": "14.80",
                        "cupSizes": ["中杯"],
                        "temperatures": ["正常冰"],
                        "sugarLevels": ["无糖"],
                        "calories": "10 kcal",
                        "ingredients": ["咖啡豆"],
                    }
                ],
                "stores": [],
                "weather": None,
                "orders": {"orders": []},
            }
        }

        stdout = io.StringIO()

        with patch.object(
            sys,
            "argv",
            ["recommend_drink.py", "--mobile", "15712459595", "--query", "有什么活动"],
        ), patch("sys.stdout", stdout):
            exit_code = recommend_drink.main()

        output = stdout.getvalue()

        self.assertEqual(exit_code, 0)
        self.assertIn("## 品牌活动", output)
        self.assertIn("小龙虾专属见面礼", output)
        self.assertIn("已经成功参与", output)
        self.assertIn("龙虾专属贴纸", output)
        self.assertIn("龙虾专属饮品券", output)
        self.assertIn("小程序龙虾专属头像属性", output)
        self.assertIn("用户正在问活动", output)
        self.assertIn("不能只列商品活动", output)
        self.assertIn("买一赠一福利", output)
        save_mobile_mock.assert_called_once_with("15712459595")
        self.mark_activity_joined_mock.assert_called_once_with("15712459595")

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
        self.assertIn("像熟悉的店员给朋友建议一样自然", output)
        self.assertIn("主推饮品名和门店名要加粗", output)
        self.assertIn("不要连续堆 emoji", output)
        self.assertIn("不要使用“推荐理由”", output)
        self.assertIn("分割线 `---` 单独隔开留资提示", output)
        self.assertIn("领取见面礼，并告知小程序绑定的手机号", output)
        self.assertIn("龙虾专属贴纸", output)
        self.assertIn("龙虾专属饮品券", output)
        self.assertIn("小程序龙虾专属头像属性", output)
        self.assertIn("不要把储值次卡作为见面礼权益", output)
        self.assertNotIn("今天天气", output)
        self.assertEqual(post_json_mock.call_count, 1)
        save_mobile_mock.assert_called_once_with("15712459595")
        self.mark_activity_joined_mock.assert_called_once_with("15712459595")
        self.mark_activity_not_joined_mock.assert_not_called()

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
        self.mark_activity_joined_mock.assert_called_once_with("15712459595")
        self.mark_activity_not_joined_mock.assert_not_called()

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
    def test_main_continues_with_context_when_claim_lookup_fails(
        self,
        fetch_json_mock,
        _load_config_mock,
        _load_mobile_mock,
        save_mobile_mock,
        post_json_mock,
    ) -> None:
        post_json_mock.side_effect = RuntimeError("claim api down")
        fetch_json_mock.return_value = {
            "data": {
                "goods": [],
                "stores": [],
                "weather": None,
                "orders": None,
            }
        }

        stdout = io.StringIO()
        stderr = io.StringIO()

        with patch.object(
            sys,
            "argv",
            ["recommend_drink.py", "--mobile", "15712459595", "--debug"],
        ), patch("sys.stdout", stdout), patch("sys.stderr", stderr):
            exit_code = recommend_drink.main()

        self.assertEqual(exit_code, 0)
        self.assertIn("claim lookup failed; continue with context lookup", stderr.getvalue())
        self.assertIn("未确认", stdout.getvalue())
        self.assertEqual(
            fetch_json_mock.call_args_list[0].args,
            (
                "http://127.0.0.1:8020/skill/xinyi/context?mobile=15712459595",
                5,
            ),
        )
        save_mobile_mock.assert_called_once_with("15712459595")
        self.mark_activity_joined_mock.assert_not_called()
        self.mark_activity_not_joined_mock.assert_not_called()

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
    def test_main_encodes_mobile_query_parameter(
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
            ["recommend_drink.py", "--mobile", "15712&x=1"],
        ), patch("sys.stdout", stdout):
            exit_code = recommend_drink.main()

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            fetch_json_mock.call_args_list[0].args,
            (
                "http://127.0.0.1:8020/skill/xinyi/context?mobile=15712%26x%3D1",
                5,
            ),
        )
        save_mobile_mock.assert_called_once_with("15712&x=1")

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
    def test_main_outputs_readable_error_when_context_request_fails(
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
                "user": {"mobile": "15712459595"},
            }
        }
        fetch_json_mock.side_effect = SkillHttpError("接口返回 HTTP 500")

        stdout = io.StringIO()

        with patch.object(
            sys,
            "argv",
            ["recommend_drink.py", "--mobile", "15712459595"],
        ), patch("sys.stdout", stdout):
            exit_code = recommend_drink.main()

        self.assertEqual(exit_code, 1)
        self.assertIn("获取推荐上下文失败：接口返回 HTTP 500", stdout.getvalue())
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
        self.mark_activity_joined_mock.assert_not_called()
        self.mark_activity_not_joined_mock.assert_called_once_with("15712459595")


if __name__ == "__main__":
    unittest.main()
