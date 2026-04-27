from __future__ import annotations

import io
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import claim_reward


class ClaimRewardScriptTest(unittest.TestCase):
    def setUp(self) -> None:
        self.load_activity_joined_patcher = patch.object(claim_reward, "load_activity_joined", return_value=None)
        self.mark_activity_joined_patcher = patch.object(claim_reward, "mark_activity_joined")
        self.mark_activity_not_joined_patcher = patch.object(claim_reward, "mark_activity_not_joined")
        self.load_activity_joined_mock = self.load_activity_joined_patcher.start()
        self.mark_activity_joined_mock = self.mark_activity_joined_patcher.start()
        self.mark_activity_not_joined_mock = self.mark_activity_not_joined_patcher.start()
        self.addCleanup(self.load_activity_joined_patcher.stop)
        self.addCleanup(self.mark_activity_joined_patcher.stop)
        self.addCleanup(self.mark_activity_not_joined_patcher.stop)

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
            '"items":[{"state":1,"message":"发放成功","coupon":{"name":"（前100名）爆款苦尽甘来拿铁免费兑换券"}}],'
            '"user":{"mobile":"15712459595","nickname":"双龙"}}}'
        ).encode("utf-8")
        second_response = type("Resp", (), {})()
        second_response.read = lambda: (
            '{"data":{"goods":[{"name":"苦尽甘来拿铁","categories":["咖啡"],"price":"16.80","cupSizes":["大杯"],'
            '"temperatures":["热","少冰"],"sugarLevels":["3分糖"],"calories":"120 kcal","ingredients":["牛奶"]}],'
            '"stores":[{"name":"幂茶幂咖望京店","address":"北京市朝阳区望京街9号","storeMobile":"01088888888",'
            '"facilities":"休息区","businessStatus":1,'
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
        urlopen_mock.side_effect = [
            urlopen_mock.return_value,
            second_context_manager,
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
        self.assertIn("领取结果：身份验证成功", output)
        self.assertIn("身份验证成功。三重福利发放到账", output)
        self.assertIn("「小龙虾贴纸」一套（到店展示小程序卡券领取）", output)
        self.assertIn("「（前100名）爆款苦尽甘来拿铁免费兑换券」一杯", output)
        self.assertIn("微信小程序里「小龙虾身份标识」", output)
        self.assertIn("你已经领取礼包，现在可以查看你过去的订单信息", output)
        self.assertNotIn("你已完成", output)
        self.assertNotIn("骨灰级粉丝", output)
        self.assertIn("贴纸领取门店信息我给你列全", output)
        self.assertIn(
            "**幂茶幂咖望京店**：地址：北京市朝阳区望京街9号；电话：01088888888；设施：休息区；排队：制作中4杯，预计18分钟",
            output,
        )
        self.assertIn("哇我们的老朋友，今天天气偏凉，建议您喝苦尽甘来拿铁", output)
        self.assertNotIn('"kind"', output)
        save_mobile_mock.assert_called_once_with("15712459595")
        self.mark_activity_joined_mock.assert_called_once_with("15712459595")
        self.mark_activity_not_joined_mock.assert_not_called()

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
        self.assertIn("领取结果：请先登录小程序", output)
        self.assertIn("目前还没登录过新一好喝", output)
        self.assertIn("微信小程序搜索【新一咖啡】", output)
        self.assertIn("登录后获取全部福利和功能", output)
        self.assertNotIn("本次查询手机号：15712459595", output)
        self.assertNotIn("告知小程序绑定的手机号", output)
        save_mobile_mock.assert_called_once_with("15712459595")
        self.mark_activity_joined_mock.assert_not_called()
        self.mark_activity_not_joined_mock.assert_called_once_with("15712459595")

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
    def test_claim_script_marks_joined_when_mobile_already_claimed(
        self,
        urlopen_mock,
        _load_config_mock,
        save_mobile_mock,
    ) -> None:
        response = urlopen_mock.return_value.__enter__.return_value
        response.read.return_value = (
            '{"code":200,"data":{"kind":"already_claimed","successCount":0,"failCount":0,'
            '"items":[],"user":{"id":10956,"uniacid":1,"mobile":"18210234223","nickname":"用户_4749997"}}}'
        ).encode("utf-8")

        stdout = io.StringIO()

        with patch.object(
            sys,
            "argv",
            ["claim_reward.py", "--mobile", "18210234223"],
        ), patch("sys.stdout", stdout):
            exit_code = claim_reward.main()

        output = stdout.getvalue()

        self.assertEqual(exit_code, 0)
        self.assertIn("领取结果：身份验证成功", output)
        self.assertIn("身份验证成功。三重福利发放到账", output)
        self.assertIn("「小龙虾贴纸」一套（到店展示小程序卡券领取）", output)
        self.assertIn("爆品赠饮一杯（具体饮品以小程序卡券为准）", output)
        self.assertIn("微信小程序里「小龙虾身份标识」", output)
        self.assertNotIn("您已参与活动啦", output)
        self.assertNotIn("已经领过", output)
        self.assertNotIn("未找到登录用户", output)
        save_mobile_mock.assert_called_once_with("18210234223")
        self.mark_activity_joined_mock.assert_called_once_with("18210234223")
        self.mark_activity_not_joined_mock.assert_not_called()

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
    def test_claim_script_explains_flow_when_no_reward_config(
        self,
        urlopen_mock,
        _load_config_mock,
        save_mobile_mock,
    ) -> None:
        response = urlopen_mock.return_value.__enter__.return_value
        response.read.return_value = (
            '{"code":200,"data":{"kind":"no_reward_config","successCount":0,"failCount":0,'
            '"items":[],"user":{"id":10956,"mobile":"13730663700","nickname":"用户_7144228"}}}'
        ).encode("utf-8")

        stdout = io.StringIO()

        with patch.object(
            sys,
            "argv",
            ["claim_reward.py", "--mobile", "13730663700"],
        ), patch("sys.stdout", stdout):
            exit_code = claim_reward.main()

        output = stdout.getvalue()

        self.assertEqual(exit_code, 0)
        self.assertIn("领取方式", output)
        self.assertIn("您可以通过绑定【新一好喝】的注册手机号，领取Skill用户大礼包", output)
        self.assertIn("先绑定【新一好喝】注册手机号，再把手机号发来", output)
        self.assertIn("微信小程序搜索【新一咖啡】", output)
        self.assertNotIn("当前没有可领取的活动奖励", output)
        self.assertNotIn("暂无可领取", output)
        save_mobile_mock.assert_called_once_with("13730663700")
        self.mark_activity_joined_mock.assert_not_called()
        self.mark_activity_not_joined_mock.assert_called_once_with("13730663700")

    @patch.object(claim_reward, "load_activity_joined", return_value=False)
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
    def test_claim_script_treats_already_claimed_after_unregistered_as_gift_obtained(
        self,
        urlopen_mock,
        _load_config_mock,
        save_mobile_mock,
        load_activity_joined_mock,
    ) -> None:
        response = urlopen_mock.return_value.__enter__.return_value
        response.read.return_value = (
            '{"code":200,"data":{"kind":"already_claimed","successCount":0,"failCount":0,'
            '"items":[],"user":{"id":10956,"uniacid":1,"mobile":"18539991423","nickname":"用户_991423"}}}'
        ).encode("utf-8")

        stdout = io.StringIO()

        with patch.object(
            sys,
            "argv",
            ["claim_reward.py", "--mobile", "18539991423"],
        ), patch("sys.stdout", stdout):
            exit_code = claim_reward.main()

        output = stdout.getvalue()

        self.assertEqual(exit_code, 0)
        self.assertIn("领取结果：身份验证成功", output)
        self.assertIn("身份验证成功。三重福利发放到账", output)
        self.assertIn("「小龙虾贴纸」一套（到店展示小程序卡券领取）", output)
        self.assertIn("爆品赠饮一杯（具体饮品以小程序卡券为准）", output)
        self.assertIn("微信小程序里「小龙虾身份标识」", output)
        self.assertNotIn("已经领过", output)
        self.assertNotIn("您已参与活动啦", output)
        load_activity_joined_mock.assert_called_once_with("18539991423")
        save_mobile_mock.assert_called_once_with("18539991423")
        self.mark_activity_joined_mock.assert_called_once_with("18539991423")
        self.mark_activity_not_joined_mock.assert_not_called()

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
    def test_claim_script_does_not_duplicate_coupon_label_when_coupon_name_missing(
        self,
        urlopen_mock,
        _load_config_mock,
        save_mobile_mock,
    ) -> None:
        first_response = urlopen_mock.return_value.__enter__.return_value
        first_response.read.return_value = (
            '{"code":200,"data":{"kind":"granted","successCount":1,"failCount":0,'
            '"items":[{"state":1,"message":"发放成功","coupon":{}}],'
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
        self.assertIn("爆品赠饮一杯（具体饮品以小程序卡券为准）", output)
        self.assertNotIn("龙虾专属饮品券龙虾专属饮品券", output)
        save_mobile_mock.assert_called_once_with("15712459595")
        self.mark_activity_joined_mock.assert_called_once_with("15712459595")
        self.mark_activity_not_joined_mock.assert_not_called()

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
        urlopen_mock.side_effect = [
            urlopen_mock.return_value,
            second_context_manager,
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
        self.assertIn("身份验证成功。三重福利发放到账", output)
        self.assertIn("「小龙虾贴纸」一套（到店展示小程序卡券领取）", output)
        self.assertIn("「苦尽甘来拿铁」一杯", output)
        self.assertIn("微信小程序里「小龙虾身份标识」", output)
        self.assertNotIn("您已参与活动啦", output)
        self.assertIn("贴纸领取门店信息我给你列全", output)
        self.assertIn(
            "**幂茶幂咖望京店**：地址：北京市朝阳区望京街9号；电话：未提供联系电话；设施：未提供设施文案；排队：制作中4杯，预计18分钟",
            output,
        )
        self.assertIn("今天天气有点热，建议您喝柚香燕麦拿铁", output)
        save_mobile_mock.assert_called_once_with("15712459595")
        self.mark_activity_joined_mock.assert_called_once_with("15712459595")
        self.mark_activity_not_joined_mock.assert_not_called()

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
            '"weather":null,'
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
        urlopen_mock.side_effect = [urlopen_mock.return_value, second_context_manager]

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
        self.mark_activity_joined_mock.assert_called_once_with("15712459595")
        self.mark_activity_not_joined_mock.assert_not_called()

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
        self.assertIn("领取结果：身份验证成功", output)
        self.assertIn("身份验证成功。三重福利发放到账", output)
        self.assertIn("「苦尽甘来拿铁」一杯", output)
        self.assertNotIn("推荐您就近前往", output)
        self.assertNotIn("建议您喝", output)
        save_mobile_mock.assert_called_once_with("15712459595")
        self.mark_activity_joined_mock.assert_called_once_with("15712459595")
        self.mark_activity_not_joined_mock.assert_not_called()

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
    def test_claim_script_outputs_debug_logs_to_stderr(
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
        stderr = io.StringIO()

        with patch.object(
            sys,
            "argv",
            ["claim_reward.py", "--mobile", "15712459595", "--debug"],
        ), patch("sys.stdout", stdout), patch("sys.stderr", stderr):
            exit_code = claim_reward.main()

        self.assertEqual(exit_code, 0)
        self.assertIn("DEBUG claim_reward: posting claim request to http://127.0.0.1:8020/skill/xinyi/claim", stderr.getvalue())
        self.assertIn("DEBUG claim_reward: user not found; marking activity as not joined", stderr.getvalue())
        self.assertIn("领取结果：请先登录小程序", stdout.getvalue())
        save_mobile_mock.assert_called_once_with("15712459595")
        self.mark_activity_joined_mock.assert_not_called()
        self.mark_activity_not_joined_mock.assert_called_once_with("15712459595")


if __name__ == "__main__":
    unittest.main()
