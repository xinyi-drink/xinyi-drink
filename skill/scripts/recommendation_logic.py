#!/usr/bin/env python3
from __future__ import annotations

from typing import Any


def describe_weather_feel(weather: dict[str, Any] | None) -> str | None:
    temperature = weather.get("temperatureC") if weather else None
    if not isinstance(temperature, (int, float)):
        return None

    if temperature <= 10:
        return "有点冷"
    if temperature <= 18:
        return "偏凉"
    if temperature <= 26:
        return "挺舒服"
    return "有点热"


def choose_recommendation_good(
    goods: list[dict[str, Any]],
    orders: dict[str, Any] | None,
    weather: dict[str, Any] | None,
) -> dict[str, Any] | None:
    if not goods:
        return None

    order_goods_names = [
        order_good.get("name")
        for order in (orders or {}).get("orders", [])
        for order_good in order.get("goods", [])
        if order_good.get("name")
    ]

    for ordered_name in order_goods_names:
        for good in goods:
            good_name = good.get("name")
            if not good_name:
                continue
            if good_name == ordered_name or good_name in ordered_name or ordered_name in good_name:
                return good

    feel = describe_weather_feel(weather)
    if feel in {"有点冷", "偏凉"}:
        for good in goods:
            temperatures = good.get("temperatures") or []
            if any("热" in str(item) for item in temperatures):
                return good

    if feel == "有点热":
        for good in goods:
            temperatures = good.get("temperatures") or []
            if any("冰" in str(item) for item in temperatures):
                return good

    return goods[0]


def build_recommendation_reason_signals(
    recommended_good: dict[str, Any],
    orders: dict[str, Any] | None,
    weather: dict[str, Any] | None,
) -> list[str]:
    signals: list[str] = []
    recommended_name = recommended_good.get("name")
    order_goods_names = [
        order_good.get("name")
        for order in (orders or {}).get("orders", [])
        for order_good in order.get("goods", [])
        if order_good.get("name")
    ]

    if recommended_name and order_goods_names:
        matched_history = [
            name
            for name in order_goods_names
            if name == recommended_name or recommended_name in name or name in recommended_name
        ]
        if matched_history:
            signals.append(f"历史订单里出现过：{'、'.join(matched_history[:3])}")
        else:
            signals.append(f"用户有历史订单，可参考近期喝过：{'、'.join(order_goods_names[:3])}")

    weather_feel = describe_weather_feel(weather)
    if weather_feel:
        signals.append(f"当前天气体感：{weather_feel}")

    temperatures = recommended_good.get("temperatures") or []
    if temperatures:
        signals.append(f"可选温度：{'、'.join(str(item) for item in temperatures)}")

    sugar_levels = recommended_good.get("sugarLevels") or []
    if sugar_levels:
        signals.append(f"可选糖度：{'、'.join(str(item) for item in sugar_levels)}")

    calories = recommended_good.get("calories")
    if calories:
        signals.append(f"热量信息：{calories}")

    ingredients = recommended_good.get("ingredients") or []
    if ingredients:
        signals.append(f"主要配料：{'、'.join(str(item) for item in ingredients)}")

    categories = recommended_good.get("categories") or []
    if categories:
        signals.append(f"商品分类：{'、'.join(str(item) for item in categories)}")

    return signals


def build_recommendation_fallback_copy(
    goods: list[dict[str, Any]],
    orders: dict[str, Any] | None,
    weather: dict[str, Any] | None,
) -> str | None:
    recommended_good = choose_recommendation_good(goods, orders, weather)
    if not recommended_good:
        return None

    recommended_name = recommended_good.get("name")
    if not recommended_name:
        return None

    weather_feel = describe_weather_feel(weather)
    has_history = bool((orders or {}).get("orders"))

    if weather_feel:
        if has_history:
            return f"哇我们的老朋友，今天天气{weather_feel}，建议您喝{recommended_name}。"
        return f"今天天气{weather_feel}，建议您喝{recommended_name}。"

    if has_history:
        return f"哇我们的老朋友，今天建议您喝{recommended_name}。"
    return f"今天建议您喝{recommended_name}。"


def build_recommendation_material_lines(
    goods: list[dict[str, Any]],
    orders: dict[str, Any] | None,
    weather: dict[str, Any] | None,
) -> list[str]:
    recommended_good = choose_recommendation_good(goods, orders, weather)
    if not recommended_good:
        return []

    recommended_name = recommended_good.get("name")
    if not recommended_name:
        return []

    lines = [
        f"推荐候选饮品：{recommended_name}",
        f"推荐素材字段：candidateName={recommended_name}",
        "主推荐文案由大模型根据下方素材自行生成，不要照搬固定模板。",
        "推荐理由请显式展开 2-4 条，只使用已提供的历史订单、天气、商品属性和门店信息，不要编造未返回的数据。",
    ]
    reason_signals = build_recommendation_reason_signals(
        recommended_good,
        orders,
        weather,
    )
    if reason_signals:
        lines.append(f"推荐素材字段：reasonSignals={' | '.join(reason_signals)}")
        lines.append(f"可用推荐依据：{'；'.join(reason_signals)}。")

    return lines
