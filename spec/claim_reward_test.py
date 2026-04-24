from __future__ import annotations

import io
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import claim_reward


class ClaimRewardScriptTest(unittest.TestCase):
    @patch.object(claim_reward, "save_mobile")
    @patch.object(
        claim_reward,
        "load_config",
        return_value={
            "apiBaseUrl": "http://127.0.0.1:8020",
            "timeoutSeconds": 5,
        },
    )
    @patch("urllib.request.urlopen")
    def test_claim_script_formats_raw_claim_response(
        self,
        urlopen_mock,
        _load_config_mock,
        save_mobile_mock,
    ) -> None:
        first_response = urlopen_mock.return_value.__enter__.return_value
        first_response.read.return_value = (
            '{"code":200,"data":{"kind":"granted","successCount":1,"failCount":0,'
            '"items":[{"state":1,"message":"发放成功","coupon":{"name":"苦尽甘来拿铁"}}],'
            '"user":{"mobile":"15712459595","nickname":"双龙"}}}'
        ).encode("utf-8")
        second_response = type("Resp", (), {})()
        second_response.read = lambda: (
            '{"data":{"goods":[{"name":"苦尽甘来拿铁","categories":["咖啡"],"price":"16.80","cupSizes":["大杯"],'
            '"temperatures":["热","少冰"],"sugarLevels":["3分糖"],"calories":"120 kcal","ingredients":["牛奶"]}],'
            '"stores":[{"name":"幂茶幂咖望京店","address":"北京市朝阳区望京街9号","businessStatus":1,'
            '"operatingStatus":1,"realtimeState":1,"labels":[{"name":"休息区"}],"makingCupCount":4,'
            '"makingCupMinutes":18,"storeType":2,"supportUnattendedMode":1}],'
            '"weather":{"city":"Beijing","condition":"cloudy","temperatureC":16},'
            '"orders":{"orders":[{"createdAt":"2025-08-08 14:16:25","orderSn":"20250808141625274275",'
            '"state":6,"pickNo":"A001","serverTime":"2025-08-08 14:36:25","goodsNum":1,'
            '"goods":[{"name":"苦尽甘来拿铁","spec":"大杯","attr":"热 / 3分糖"}],'
            '"store":{"name":"幂茶幂咖望京店"}}]}}}'
        ).encode("utf-8")
        second_context_manager = type(
            "ContextManager",
            (),
            {
                "__enter__": lambda self: second_response,
                "__exit__": lambda self, exc_type, exc, tb: False,
            },
        )()
        third_response = type("Resp", (), {})()
        third_response.read = lambda: (
            '{"data":{"city":"Beijing","condition":"cloudy","temperatureC":16}}'
        ).encode("utf-8")
        third_context_manager = type(
            "ContextManager",
            (),
            {
                "__enter__": lambda self: third_response,
                "__exit__": lambda self, exc_type, exc, tb: False,
            },
        )()
        urlopen_mock.side_effect = [
            urlopen_mock.return_value,
            second_context_manager,
            third_context_manager,
        ]

        stdout = io.StringIO()

        with patch.object(
            sys,
            "argv",
            ["claim_reward.py", "--mobile", "15712459595"],
        ), patch("sys.stdout", stdout):
            exit_code = claim_reward.main()

        output = stdout.getvalue()

        self.assertEqual(exit_code, 0)
        self.assertIn("领取结果：已领取成功", output)
        self.assertIn("您的龙虾专属饮品券「苦尽甘来拿铁」已发放", output)
        self.assertIn("龙虾专属标签和头像也已同步点亮，请登录小程序查看", output)
        self.assertIn("龙虾专属贴纸已为您准备好，到店就能领取", output)
        self.assertIn("先到先得，赶快哦", output)
        self.assertIn(
            "推荐您就近前往幂茶幂咖望京店（北京市朝阳区望京街9号）领取贴纸",
            output,
        )
        self.assertIn("哇我们的老朋友，今天天气偏凉，建议您喝苦尽甘来拿铁", output)
        self.assertNotIn('"kind"', output)
        save_mobile_mock.assert_called_once_with("15712459595")

    @patch.object(claim_reward, "save_mobile")
    @patch.object(
        claim_reward,
        "load_config",
        return_value={
            "apiBaseUrl": "http://127.0.0.1:8020",
            "timeoutSeconds": 5,
        },
    )
    @patch("urllib.request.urlopen")
    def test_claim_script_prompts_user_to_share_bound_mobile_when_unregistered(
        self,
        urlopen_mock,
        _load_config_mock,
        save_mobile_mock,
    ) -> None:
        response = urlopen_mock.return_value.__enter__.return_value
        response.read.return_value = (
            '{"code":200,"data":{"kind":"unregistered","successCount":0,"failCount":0,'
            '"items":[],"user":null}}'
        ).encode("utf-8")

        stdout = io.StringIO()

        with patch.object(
            sys,
            "argv",
            ["claim_reward.py", "--mobile", "15712459595"],
        ), patch("sys.stdout", stdout):
            exit_code = claim_reward.main()

        output = stdout.getvalue()

        self.assertEqual(exit_code, 0)
        self.assertIn("领取结果：未找到登录用户", output)
        self.assertIn("登录微信小程序【新一好喝】", output)
        self.assertIn("告知小程序绑定的手机号", output)
        save_mobile_mock.assert_not_called()

    @patch.object(claim_reward, "save_mobile")
    @patch.object(
        claim_reward,
        "load_config",
        return_value={
            "apiBaseUrl": "http://127.0.0.1:8020",
            "timeoutSeconds": 5,
        },
    )
    @patch("urllib.request.urlopen")
    def test_claim_script_reuses_recommendation_copy_when_activity_already_joined(
        self,
        urlopen_mock,
        _load_config_mock,
        save_mobile_mock,
    ) -> None:
        first_response = urlopen_mock.return_value.__enter__.return_value
        first_response.read.return_value = (
            '{"code":200,"data":{"kind":"already_claimed","successCount":1,"failCount":0,'
            '"items":[{"state":1,"message":"发放成功","coupon":{"name":"苦尽甘来拿铁"}}],'
            '"user":{"mobile":"15712459595","nickname":"双龙"}}}'
        ).encode("utf-8")
        second_response = type("Resp", (), {})()
        second_response.read = lambda: (
            '{"data":{"goods":[{"name":"柚香燕麦拿铁","categories":["咖啡"],"price":"14.80","cupSizes":["大杯"],'
            '"temperatures":["热","少冰"],"sugarLevels":["3分糖"],"calories":"118 kcal","ingredients":["燕麦奶"]}],'
            '"stores":[{"name":"幂茶幂咖望京店","address":"北京市朝阳区望京街9号","businessStatus":1,'
            '"operatingStatus":1,"realtimeState":1,"labels":[{"name":"休息区"}],"makingCupCount":4,'
            '"makingCupMinutes":18,"storeType":1,"supportUnattendedMode":0}],'
            '"weather":{"city":"Beijing","condition":"sunny","temperatureC":27},'
            '"orders":{"orders":[]}}}'
        ).encode("utf-8")
        second_context_manager = type(
            "ContextManager",
            (),
            {
                "__enter__": lambda self: second_response,
                "__exit__": lambda self, exc_type, exc, tb: False,
            },
        )()
        third_response = type("Resp", (), {})()
        third_response.read = lambda: (
            '{"data":{"city":"Beijing","condition":"sunny","temperatureC":27}}'
        ).encode("utf-8")
        third_context_manager = type(
            "ContextManager",
            (),
            {
                "__enter__": lambda self: third_response,
                "__exit__": lambda self, exc_type, exc, tb: False,
            },
        )()
        urlopen_mock.side_effect = [
            urlopen_mock.return_value,
            second_context_manager,
            third_context_manager,
        ]

        stdout = io.StringIO()

        with patch.object(
            sys,
            "argv",
            ["claim_reward.py", "--mobile", "15712459595"],
        ), patch("sys.stdout", stdout):
            exit_code = claim_reward.main()

        output = stdout.getvalue()

        self.assertEqual(exit_code, 0)
        self.assertIn("您已参与活动啦", output)
        self.assertIn("龙虾专属标签和头像已经点亮，请登录小程序查看", output)
        self.assertIn("龙虾专属贴纸已为您准备好，到店就能领取", output)
        self.assertIn("先到先得，赶快哦", output)
        self.assertIn(
            "推荐您就近前往幂茶幂咖望京店（北京市朝阳区望京街9号）领取贴纸",
            output,
        )
        self.assertIn("今天天气有点热，建议您喝柚香燕麦拿铁", output)
        save_mobile_mock.assert_called_once_with("15712459595")

    @patch.object(claim_reward, "save_mobile")
    @patch.object(
        claim_reward,
        "load_config",
        return_value={
            "apiBaseUrl": "http://127.0.0.1:8020",
            "timeoutSeconds": 5,
        },
    )
    @patch("urllib.request.urlopen")
    def test_claim_script_falls_back_to_generic_copy_when_weather_api_fails(
        self,
        urlopen_mock,
        _load_config_mock,
        save_mobile_mock,
    ) -> None:
        first_response = urlopen_mock.return_value.__enter__.return_value
        first_response.read.return_value = (
            '{"code":200,"data":{"kind":"already_claimed","successCount":1,"failCount":0,'
            '"items":[{"state":1,"message":"发放成功","coupon":{"name":"苦尽甘来拿铁"}}],'
            '"user":{"mobile":"15712459595","nickname":"双龙"}}}'
        ).encode("utf-8")
        second_response = type("Resp", (), {})()
        second_response.read = lambda: (
            '{"data":{"goods":[{"name":"苦尽甘来拿铁","categories":["咖啡"],"price":"16.80","cupSizes":["大杯"],'
            '"temperatures":["热","少冰"],"sugarLevels":["3分糖"],"calories":"120 kcal","ingredients":["牛奶"]}],'
            '"stores":[{"name":"幂茶幂咖望京店","address":"北京市朝阳区望京街9号","businessStatus":1,'
            '"operatingStatus":1,"realtimeState":1,"labels":[{"name":"休息区"}],"makingCupCount":4,'
            '"makingCupMinutes":18,"storeType":1,"supportUnattendedMode":0}],'
            '"weather":{"city":"Beijing","condition":"sunny","temperatureC":27},'
            '"orders":{"orders":[]}}}'
        ).encode("utf-8")
        second_context_manager = type(
            "ContextManager",
            (),
            {
                "__enter__": lambda self: second_response,
                "__exit__": lambda self, exc_type, exc, tb: False,
            },
        )()
        urlopen_mock.side_effect = [
            urlopen_mock.return_value,
            second_context_manager,
            RuntimeError("weather api down"),
        ]

        stdout = io.StringIO()

        with patch.object(
            sys,
            "argv",
            ["claim_reward.py", "--mobile", "15712459595"],
        ), patch("sys.stdout", stdout):
            exit_code = claim_reward.main()

        output = stdout.getvalue()

        self.assertEqual(exit_code, 0)
        self.assertIn("今天建议您喝苦尽甘来拿铁", output)
        self.assertNotIn("今天天气", output)
        save_mobile_mock.assert_called_once_with("15712459595")

    @patch.object(claim_reward, "save_mobile")
    @patch.object(
        claim_reward,
        "load_config",
        return_value={
            "apiBaseUrl": "http://127.0.0.1:8020",
            "timeoutSeconds": 5,
        },
    )
    @patch("urllib.request.urlopen")
    def test_claim_script_keeps_success_message_when_context_fetch_fails(
        self,
        urlopen_mock,
        _load_config_mock,
        save_mobile_mock,
    ) -> None:
        first_response = urlopen_mock.return_value.__enter__.return_value
        first_response.read.return_value = (
            '{"code":200,"data":{"kind":"granted","successCount":1,"failCount":0,'
            '"items":[{"state":1,"message":"发放成功","coupon":{"name":"苦尽甘来拿铁"}}],'
            '"user":{"mobile":"15712459595","nickname":"双龙"}}}'
        ).encode("utf-8")

        urlopen_mock.side_effect = [
            urlopen_mock.return_value,
            RuntimeError("context api down"),
        ]

        stdout = io.StringIO()

        with patch.object(
            sys,
            "argv",
            ["claim_reward.py", "--mobile", "15712459595"],
        ), patch("sys.stdout", stdout):
            exit_code = claim_reward.main()

        output = stdout.getvalue()

        self.assertEqual(exit_code, 0)
        self.assertIn("领取结果：已领取成功", output)
        self.assertIn("您的龙虾专属饮品券「苦尽甘来拿铁」已发放", output)
        self.assertNotIn("推荐您就近前往", output)
        self.assertNotIn("建议您喝", output)
        save_mobile_mock.assert_called_once_with("15712459595")


if __name__ == "__main__":
    unittest.main()
