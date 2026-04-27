#!/usr/bin/env python3
from __future__ import annotations

from typing import Any

from recommendation_logic import (
    build_recommendation_fallback_copy,
    build_recommendation_material_lines,
)
from response_rendering import (
    escape_table_cell,
    render_markdown_table,
    render_primary_response,
    render_text_section,
)

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
ACTIVITY_GIFT_ITEMS = ("龙虾专属贴纸", "龙虾专属饮品券", "小程序龙虾专属头像属性")
ACTIVITY_GIFT_SUMMARY = f"见面礼包含：{'、'.join(ACTIVITY_GIFT_ITEMS)}。"
STICKER_PICKUP_HINT = "龙虾专属贴纸已为您准备好，到店就能领取，先到先得，赶快哦。"
ACTIVITY_QUERY_KEYWORDS = ("活动", "福利", "优惠", "券", "见面礼", "龙虾", "领取")


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
        return ""

    if len(coupon_names) == 1:
        return f"「{coupon_names[0]}」"

    return "、".join(f"「{name}」" for name in coupon_names)


def render_context_section(context: dict[str, Any]) -> str:
    mobile_source = "-"
    mobile = context.get("mobile")
    if mobile:
        mobile_source = "本地缓存" if context.get("mobileFromStore") else "本次输入"

    activity_joined = context.get("activityJoined")
    if activity_joined is True:
        activity_joined_label = "是"
    elif activity_joined is False:
        activity_joined_label = "否"
    else:
        activity_joined_label = "未确认"

    rows = [
        ["手机号", mobile],
        ["手机号来源", mobile_source],
        ["是否已参加活动", activity_joined_label],
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


def is_activity_query(context: dict[str, Any]) -> bool:
    text = " ".join(
        str(context.get(key) or "")
        for key in ("query", "scene", "preference")
    )
    return any(keyword in text for keyword in ACTIVITY_QUERY_KEYWORDS)


def render_brand_activity_section(context: dict[str, Any]) -> str:
    activity_joined = context.get("activityJoined")

    if activity_joined is True:
        lines = [
            f"**小龙虾专属见面礼**：用户已经成功参与，{ACTIVITY_GIFT_SUMMARY}",
            "龙虾专属贴纸到店可领，龙虾专属饮品券和小程序龙虾专属头像属性已经生效。",
            "回答时可以温和提醒“你已经领过啦”，不要再要求用户重新登录小程序或再次告知手机号。",
        ]
    else:
        lines = [
            f"**小龙虾专属见面礼**：登录微信小程序【新一好喝】完成注册和手机号绑定后，告知绑定手机号即可领取。{ACTIVITY_GIFT_SUMMARY}",
            "龙虾专属贴纸到店可领，龙虾专属饮品券和小程序龙虾专属头像属性会随活动状态生效。",
        ]

    lines.append("这是品牌活动，必须和商品列表里的买一赠一、特价、畅饮卡等商品活动区分开。")
    return render_text_section("品牌活动", lines)


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


def build_store_pickup_lines(stores: list[dict[str, Any]]) -> list[str]:
    if not stores:
        return []

    highlighted_stores = stores[:2]
    lines = ["贴纸领取门店信息我给你列全（地址、电话、设施、排队）："]

    for store in highlighted_stores:
        wait_parts: list[str] = []
        if store.get("makingCupCount") is not None:
            wait_parts.append(f"制作中{store.get('makingCupCount')}杯")
        if store.get("makingCupMinutes") is not None:
            wait_parts.append(f"预计{store.get('makingCupMinutes')}分钟")

        lines.append(
            "；".join(
                [
                    f"**{store.get('name') or '-'}**：地址：{store.get('address') or '-'}",
                    f"电话：{pick_store_contact(store) or '未提供联系电话'}",
                    f"设施：{render_store_facilities_text(store) or '未提供设施文案'}",
                    f"排队：{'，'.join(wait_parts) if wait_parts else '暂无排队信息'}",
                ]
            )
        )

    return lines


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


def render_answer_requirements_section(
    stores: list[dict[str, Any]],
    context: dict[str, Any],
) -> str:
    lines = [
        "先给出一段有温度的主推荐文案，像熟悉的店员在认真帮用户挑一杯，而不是像报告摘要。",
        "回答需要有层次和重点：推荐饮品、适合它的几个原因、附近可去的门店、活动留资提示分成 3-4 个短块，不要堆成一整段。",
        "主推饮品名和门店名必须加粗；如果提到备选饮品，也可以加粗突出。",
        "可以少量使用合适 emoji 做层次锚点或增强温度，比如饮品、天气、门店、活动各 0-1 个；不要每行都加，也不要连续堆 emoji。",
        "把推荐依据自然融进表达里，可以用轻量分点，但不要使用“根据你的历史订单偏好”“推荐理由”“历史偏好匹配”“天气适配”“推荐门店”这类机械标题。",
        "语气要真诚、松弛、有人情味；少用营销腔、感叹号和模板化开场，不要复述固定模板。",
    ]

    if context.get("activityJoined"):
        lines.append("用户已参加过活动，不要再输出登录小程序、领取见面礼、告知手机号这类留资提示。")
    else:
        lines.append(
            f"用户未参加过活动或当前手机号状态未确认，回答末尾可以用分割线 `---` 单独隔开留资提示：如果仿生人会梦见电子羊，那小龙虾也需要一杯充满灵魂的赛博咖啡！登录微信小程序【新一好喝】，领取见面礼，并告知小程序绑定的手机号。必须说明{ACTIVITY_GIFT_SUMMARY}不要把储值次卡作为见面礼权益，除非接口或素材明确返回。"
        )

    if is_activity_query(context):
        lines.append(
            "用户正在问活动/福利/优惠，最终回答必须把“**小龙虾专属见面礼**”作为独立品牌活动，和商品列表里的买一赠一、特价、畅饮卡等商品活动并列展示，不能只列商品活动。"
        )

    if stores:
        lines.extend(
            [
                "若返回了门店数据，最终回答里至少给出 1-2 家具体门店，带上门店名和详细地址。",
                "若有门店电话也一并给出；如果没有电话字段，再明确说明未提供联系电话。",
                "若门店返回了 facilities，必须明确返回这段设施文案，不要省略。",
                "门店部分用“如果你在附近，可以去……”这类自然说法承接；门店名加粗，地址、电话、设施和排队信息用短行呈现。",
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
        render_brand_activity_section(context),
        render_weather_section(weather),
        render_orders_section(orders),
        render_goods_section(goods),
        render_stores_section(stores),
        render_store_summary_section(stores),
        render_answer_requirements_section(stores, context),
    ]

    recommendation_material_lines = build_recommendation_material_lines(goods, orders, weather)
    if recommendation_material_lines:
        sections.append(
            render_text_section(
                "推荐素材",
                recommendation_material_lines,
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
        requested_mobile = data.get("requestedMobile")
        mobile_line = f"本次查询手机号：{requested_mobile}" if requested_mobile else ""
        return render_primary_response(
            "领取结果：未找到登录用户",
            [
                mobile_line,
                ACTIVITY_GIFT_SUMMARY,
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
    recommendation_copy = build_recommendation_fallback_copy(goods, orders, weather)

    title = "领取结果：处理完成"
    lines: list[str] = []

    if kind == "granted":
        title = "领取结果：已领取成功"
        lines.extend(build_activity_completion_lines(kind, coupon_names))
    elif kind == "obtained_after_registration":
        title = "领取结果：礼品已到账"
        lines.extend(
            [
                "已经识别到你的账号，龙虾专属活动礼品已经获取成功。",
                ACTIVITY_GIFT_SUMMARY,
                "龙虾专属饮品券和小程序龙虾专属头像属性已经生效，请登录小程序查看。",
                STICKER_PICKUP_HINT,
            ]
        )
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
