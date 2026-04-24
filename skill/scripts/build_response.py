#!/usr/bin/env python3
from __future__ import annotations

from typing import Any

WEATHER_LABELS = {
    "sunny": "晴",
    "cloudy": "多云",
    "rainy": "雨",
    "snowy": "雪",
    "unknown": "未知",
}

ORDER_STATE_LABELS = {
    0: "未知",
    1: "待支付",
    2: "制作中",
    3: "待取餐",
    4: "已取消",
    5: "退款中",
    6: "已完成",
}

LOGIN_AND_SHARE_MOBILE_HINT = (
    "登录微信小程序【新一好喝】，领取见面礼，并告知小程序绑定的手机号。"
)
STICKER_PICKUP_HINT = "龙虾专属贴纸已为您准备好，到店就能领取，先到先得，赶快哦。"


def render_primary_response(title: str, lines: list[str]) -> str:
    parts = [title.strip()]
    parts.extend(line.strip() for line in lines if line and line.strip())
    return "\n".join(parts)


def escape_table_cell(value: Any) -> str:
    if value is None:
        return "-"

    if isinstance(value, bool):
        text = "是" if value else "否"
    elif isinstance(value, (list, tuple, set)):
        items = [escape_table_cell(item) for item in value]
        text = "、".join(item for item in items if item != "-")
    else:
        text = str(value).strip()

    if not text:
        return "-"

    return text.replace("|", "\\|").replace("\n", "<br>")


def render_markdown_table(
    title: str,
    headers: list[str],
    rows: list[list[Any]],
    empty_text: str,
) -> str:
    parts = [f"## {title}"]

    if not rows:
        parts.append(empty_text)
        return "\n".join(parts)

    parts.append(f"| {' | '.join(headers)} |")
    parts.append(f"| {' | '.join('---' for _ in headers)} |")

    for row in rows:
        parts.append(f"| {' | '.join(escape_table_cell(cell) for cell in row)} |")

    return "\n".join(parts)


def render_text_section(title: str, lines: list[str]) -> str:
    return render_primary_response(
        f"## {title}",
        lines,
    )


def pick_store_contact(store: dict[str, Any]) -> Any:
    for key in ("storeMobile", "contactPhone", "phone", "telephone", "tel"):
        value = store.get(key)
        if value:
            return value

    return None


def split_store_facilities(store: dict[str, Any]) -> list[str]:
    facilities = store.get("facilities")
    if not facilities:
        return []

    text = str(facilities).replace("，", ",").replace("。", ",")
    return [item.strip() for item in text.split(",") if item.strip()]


def render_store_facilities_text(store: dict[str, Any]) -> Any:
    return store.get("facilities") or None


def format_coupon_label(coupon_names: list[str]) -> str:
    if not coupon_names:
        return "龙虾专属饮品券"

    if len(coupon_names) == 1:
        return f"「{coupon_names[0]}」"

    return "、".join(f"「{name}」" for name in coupon_names)


def render_context_section(context: dict[str, Any]) -> str:
    mobile_source = "-"
    mobile = context.get("mobile")
    if mobile:
        mobile_source = "本地缓存" if context.get("mobileFromStore") else "本次输入"

    rows = [
        ["手机号", mobile],
        ["手机号来源", mobile_source],
        ["用户问题", context.get("query")],
        ["推荐场景", context.get("scene")],
        ["用户偏好", context.get("preference")],
    ]

    return render_markdown_table(
        title="用户上下文",
        headers=["字段", "内容"],
        rows=rows,
        empty_text="暂无上下文信息。",
    )


def render_weather_section(weather: dict[str, Any] | None) -> str:
    rows: list[list[Any]] = []
    if weather:
        rows.append(
            [
                weather.get("city"),
                WEATHER_LABELS.get(weather.get("condition"), weather.get("condition")),
                weather.get("temperatureC"),
            ]
        )

    return render_markdown_table(
        title="天气",
        headers=["城市", "天气", "温度(°C)"],
        rows=rows,
        empty_text="暂无天气数据。",
    )


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


def format_order_goods(goods: list[dict[str, Any]]) -> str:
    entries: list[str] = []
    for item in goods:
        name = item.get("name") or "-"
        detail_parts = [part for part in [item.get("spec"), item.get("attr")] if part]
        if detail_parts:
            entries.append(f"{name}（{' / '.join(detail_parts)}）")
        else:
            entries.append(name)

    return "；".join(entries) if entries else "-"


def format_order_state(state: Any) -> str:
    if isinstance(state, int):
        return ORDER_STATE_LABELS.get(state, f"状态{state}")

    return escape_table_cell(state)


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


def build_recommendation_copy(
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


def build_store_pickup_lines(stores: list[dict[str, Any]]) -> list[str]:
    if not stores:
        return []

    highlighted_stores = stores[:2]

    if len(highlighted_stores) == 1:
        store = highlighted_stores[0]
        return [
            f"推荐您就近前往{store.get('name') or '-'}（{store.get('address') or '-'}）领取贴纸。"
        ]

    store_descriptions = [
        f"{store.get('name') or '-'}（{store.get('address') or '-'}）"
        for store in highlighted_stores
    ]

    return [
        f"推荐您就近前往{'或'.join(store_descriptions)}领取贴纸。"
    ]


def build_activity_completion_lines(kind: str, coupon_names: list[str]) -> list[str]:
    if kind == "granted":
        return [
            f"您的龙虾专属饮品券{format_coupon_label(coupon_names)}已发放。",
            "龙虾专属标签和头像也已同步点亮，请登录小程序查看。",
            STICKER_PICKUP_HINT,
        ]

    if kind == "already_claimed":
        return [
            "您已参与活动啦。",
            "龙虾专属标签和头像已经点亮，请登录小程序查看。",
            STICKER_PICKUP_HINT,
        ]

    return []


def render_orders_section(orders: dict[str, Any] | None) -> str:
    if orders is None:
        return "## 订单历史\n未提供手机号，未查询订单历史。"

    rows = [
        [
            item.get("createdAt"),
            item.get("orderSn"),
            format_order_state(item.get("state")),
            item.get("pickNo"),
            item.get("serverTime"),
            item.get("store", {}).get("name") if item.get("store") else None,
            format_order_goods(item.get("goods", [])),
            item.get("goodsNum"),
        ]
        for item in orders.get("orders", [])
    ]

    return render_markdown_table(
        title="订单历史",
        headers=[
            "下单时间",
            "订单号",
            "状态",
            "排号",
            "预计取餐时间",
            "门店",
            "商品",
            "杯数",
        ],
        rows=rows,
        empty_text="暂无订单记录。",
    )


def render_goods_section(goods: list[dict[str, Any]]) -> str:
    rows = [
        [
            item.get("name"),
            item.get("categories", []),
            item.get("price"),
            item.get("cupSizes", []),
            item.get("temperatures", []),
            item.get("sugarLevels", []),
            item.get("calories"),
            item.get("ingredients", []),
        ]
        for item in goods
    ]

    return render_markdown_table(
        title="商品列表",
        headers=["商品名称", "分类", "价格", "杯型", "温度", "糖度", "卡路里", "配料"],
        rows=rows,
        empty_text="暂无商品数据。",
    )


def format_store_status(store: dict[str, Any]) -> str:
    parts: list[str] = []
    if store.get("businessStatus") is not None:
        parts.append(f"营业状态={store.get('businessStatus')}")
    if store.get("operatingStatus") is not None:
        parts.append(f"运营状态={store.get('operatingStatus')}")
    if store.get("realtimeState") is not None:
        parts.append(f"实时状态={store.get('realtimeState')}")
    return " / ".join(parts) if parts else "-"


def build_store_feature_tags(store: dict[str, Any]) -> list[str]:
    feature_tags: list[str] = []

    def append_tag(tag: Any) -> None:
        if not tag:
            return
        text = str(tag).strip()
        if text and text not in feature_tags:
            feature_tags.append(text)

    for facility in split_store_facilities(store):
        append_tag(facility)

    for label in store.get("labels", []):
        if isinstance(label, dict):
            append_tag(label.get("name"))

    if store.get("supportUnattendedMode") == 1:
        append_tag("支持无人模式")

    if store.get("storeType") == 2:
        append_tag("Box 门店")

    return feature_tags


def build_store_summary_lines(stores: list[dict[str, Any]]) -> list[str]:
    lines: list[str] = []
    for store in stores[:2]:
        feature_tags = build_store_feature_tags(store)
        feature_text = "、".join(feature_tags) if feature_tags else "暂无特色信息"
        wait_parts: list[str] = []
        if store.get("makingCupCount") is not None:
            wait_parts.append(f"制作中{store.get('makingCupCount')}杯")
        if store.get("makingCupMinutes") is not None:
            wait_parts.append(f"预计{store.get('makingCupMinutes')}分钟")
        wait_text = "，".join(wait_parts) if wait_parts else "暂无排队信息"
        contact = pick_store_contact(store) or "未提供联系电话"

        lines.append(
            "；".join(
                [
                    f"门店名：{store.get('name') or '-'}",
                    f"地址：{store.get('address') or '-'}",
                    f"电话：{contact}",
                    f"设施：{render_store_facilities_text(store) or '未提供设施文案'}",
                    f"特色：{feature_text}",
                    f"排队：{wait_text}",
                ]
            )
        )

    return lines


def render_stores_section(stores: list[dict[str, Any]]) -> str:
    rows = [
        [
            item.get("name"),
            item.get("address"),
            pick_store_contact(item),
            render_store_facilities_text(item),
            format_store_status(item),
            build_store_feature_tags(item),
            item.get("makingCupCount"),
            item.get("makingCupMinutes"),
        ]
        for item in stores
    ]

    return render_markdown_table(
        title="门店列表",
        headers=["门店名称", "地址", "联系电话", "设施文案", "状态", "特色标签", "制作中杯数", "制作时长(分钟)"],
        rows=rows,
        empty_text="暂无门店数据。",
    )


def render_answer_requirements_section(stores: list[dict[str, Any]]) -> str:
    lines = [
        "先给出推荐饮品，再补充门店信息，不要只概括成“有多家门店正在营业中”。",
    ]

    if stores:
        lines.extend(
            [
                "若返回了门店数据，最终回答里至少给出 1-2 家具体门店，带上门店名和详细地址。",
                "若有门店电话也一并给出；如果没有电话字段，再明确说明未提供联系电话。",
                "若门店返回了 facilities，必须明确返回这段设施文案，不要省略。",
            ]
        )
    else:
        lines.append("如果没有门店数据，明确说明当前未拿到可用门店信息。")

    return render_text_section("回答要求", lines)


def render_store_summary_section(stores: list[dict[str, Any]]) -> str:
    return render_text_section(
        "门店摘要建议",
        build_store_summary_lines(stores)
        if stores
        else ["当前未拿到可直接复述的门店摘要。"],
    )


def render_recommendation_context(
    *,
    context: dict[str, Any],
    goods: list[dict[str, Any]],
    stores: list[dict[str, Any]],
    weather: dict[str, Any] | None,
    orders: dict[str, Any] | None,
) -> str:
    sections = [
        render_context_section(context),
        render_weather_section(weather),
        render_orders_section(orders),
        render_goods_section(goods),
        render_stores_section(stores),
        render_store_summary_section(stores),
        render_answer_requirements_section(stores),
    ]

    recommendation_copy = build_recommendation_copy(goods, orders, weather)
    if recommendation_copy:
        sections.append(
            render_text_section(
                "推荐话术建议",
                [recommendation_copy],
            )
        )

    return "\n\n".join(section for section in sections if section.strip())


def render_claim_result(
    data: dict[str, Any],
    context_data: dict[str, Any] | None = None,
) -> str:
    kind = data.get("kind")
    items = data.get("items", [])
    user = data.get("user")

    if kind == "unregistered":
        return render_primary_response(
            "领取结果：未找到登录用户",
            [
                f"请先{LOGIN_AND_SHARE_MOBILE_HINT}",
            ],
        )

    coupon_names = [
        item.get("coupon", {}).get("name")
        for item in items
        if item.get("state") == 1 and item.get("coupon")
    ]
    coupon_names = [name for name in coupon_names if name]

    context_data = context_data or {}
    goods = context_data.get("goods", [])
    stores = context_data.get("stores", [])
    weather = context_data.get("weather")
    orders = context_data.get("orders")
    recommendation_copy = build_recommendation_copy(goods, orders, weather)

    title = "领取结果：处理完成"
    lines: list[str] = []

    if kind == "granted":
        title = "领取结果：已领取成功"
        lines.extend(build_activity_completion_lines(kind, coupon_names))
    elif kind == "already_claimed":
        title = "领取结果：已经领过"
        lines.extend(build_activity_completion_lines(kind, coupon_names))
    elif kind == "no_reward_config":
        title = "领取结果：当前没有可领奖励"
        lines.append("当前没有可领取的活动奖励。")
    else:
        lines.append("活动处理已完成。")

    if user and user.get("nickname"):
        lines.append(f"当前识别用户：{user.get('nickname')}")

    lines.extend(build_store_pickup_lines(stores))

    if recommendation_copy:
        lines.append(recommendation_copy)

    failed_messages = [item.get("message") for item in items if item.get("state") != 1 and item.get("message")]
    if failed_messages and kind == "no_reward_config":
        lines.append(f"失败原因：{'；'.join(str(message) for message in failed_messages)}")

    return render_primary_response(title, lines)
