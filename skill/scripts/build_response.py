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

LEAD_CAPTURE_COPY = "您可以通过绑定【新一好喝】的注册手机号，领取 Skill 用户大礼包。"
UNREGISTERED_LOGIN_COPY = "目前还没登录过新一好喝，请到微信小程序搜索【新一咖啡】登录后获取全部福利和功能。"
ACTIVITY_GIFT_SUMMARY = "三重福利包含：「小龙虾贴纸」一套、根据接口返回的爆品赠饮一杯、微信小程序里「小龙虾身份标识」。"
ACTIVITY_QUERY_KEYWORDS = ("活动", "福利", "优惠", "券", "见面礼", "龙虾", "领取")
ORDER_QUERY_KEYWORDS = ("订单", "过去", "历史", "完成", "买过", "购买", "消费", "几单", "多少单", "下过单")


def build_activity_flow_lines() -> list[str]:
    return [
        LEAD_CAPTURE_COPY,
        f"活动内容：{ACTIVITY_GIFT_SUMMARY}",
        "领取流程：先绑定【新一好喝】注册手机号，再把手机号发来，我会帮您领取。",
        "如果还没登录过新一好喝，请到微信小程序搜索【新一咖啡】登录后获取全部福利和功能。",
    ]


def build_unregistered_activity_lines(mobile: Any) -> list[str]:
    mobile_text = str(mobile).strip() if mobile else "当前手机号"
    return [
        f"{mobile_text} 目前还没查到【新一好喝】小程序登录/绑定记录；请到微信小程序搜索【新一咖啡】登录后获取全部福利和功能。",
        LEAD_CAPTURE_COPY,
        f"活动内容：{ACTIVITY_GIFT_SUMMARY}",
        "参与方法：请先在微信小程序搜索【新一咖啡】，登录/注册并绑定手机号；完成后把绑定手机号发来，我会帮您继续领取。",
        "这不是没有活动，而是需要先完成小程序登录/绑定后才能发放礼包。",
    ]


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


def format_coupon_reward(coupon_names: list[str]) -> str:
    if not coupon_names:
        return "爆品赠饮一杯（具体饮品以小程序卡券为准）"

    if len(coupon_names) == 1:
        return f"{format_coupon_label(coupon_names)}一杯"

    return f"{format_coupon_label(coupon_names)}各一杯"


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


def is_order_query(context: dict[str, Any]) -> bool:
    text = " ".join(
        str(context.get(key) or "")
        for key in ("query", "scene", "preference")
    )
    return any(keyword in text for keyword in ORDER_QUERY_KEYWORDS)


def render_brand_activity_section(context: dict[str, Any]) -> str:
    activity_joined = context.get("activityJoined")

    if activity_joined is True:
        lines = [
            f"**Skill 用户大礼包**：用户身份已验证成功，{ACTIVITY_GIFT_SUMMARY}",
            "回答时可以说明福利已经到账，不要再要求用户重新登录小程序或再次告知手机号。",
        ]
    else:
        lines = [
            f"**Skill 用户大礼包**：{LEAD_CAPTURE_COPY}",
            "用户可以提供【新一好喝】注册手机号领取；如果仍未注册，提醒去微信小程序搜索【新一咖啡】登录后获取全部福利和功能。",
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
    if kind in {"granted", "already_claimed", "obtained_after_registration"}:
        return [
            "身份验证成功。三重福利发放到账：",
            f"「小龙虾贴纸」一套（到店展示小程序卡券领取）；{format_coupon_reward(coupon_names)}；微信小程序里「小龙虾身份标识」。",
            "你已经领取礼包，现在可以查看你过去的订单信息。",
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


def build_order_followup_lines(orders: dict[str, Any] | None) -> list[str]:
    if orders is None:
        return ["用户追问订单信息时，当前未提供手机号，不能查询过去订单。"]

    order_list = orders.get("orders", [])
    completed_orders = [order for order in order_list if order.get("state") == 6]
    goods_names: list[str] = []
    store_names: list[str] = []
    for order in order_list:
        store = order.get("store") or {}
        if store.get("name"):
            store_names.append(str(store.get("name")))
        for good in order.get("goods", []):
            if good.get("name"):
                goods_names.append(str(good.get("name")))

    lines = [
        f"用户追问订单信息时再展开：你已完成{len(completed_orders)}单，是新一的骨灰级粉丝吧。",
        f"当前可见订单数：{len(order_list)}单。",
    ]
    if goods_names:
        lines.append(f"买过的商品可以提这些：{'、'.join(goods_names[:5])}。")
    if store_names:
        unique_store_names = list(dict.fromkeys(store_names))
        lines.append(f"到过的门店可以提这些：{'、'.join(unique_store_names[:3])}。")

    return lines


def render_order_followup_section(
    context: dict[str, Any],
    orders: dict[str, Any] | None,
) -> str:
    if not is_order_query(context):
        return ""

    return render_text_section("订单追问素材", build_order_followup_lines(orders))


def render_goods_section(goods: list[dict[str, Any]]) -> str:
    rows = [
        [
            item.get("name"),
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
        headers=["商品名称", "价格", "杯型", "温度", "糖度", "卡路里", "配料"],
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
        "接口没返回的数据不要编造；没有门店、商品、券名、订单或活动状态时，明确说当前没拿到。",
        "登录成功后只提示用户已经领取礼包、现在可以查看过去的订单信息；不要主动展开已完成多少单或购买明细。",
        "只有用户追问订单、完成多少单、买过什么时，才根据订单数据返回已完成订单数和购买信息；可以自然说“你已完成xx单，是新一的骨灰级粉丝吧”。",
    ]

    if context.get("activityJoined"):
        lines.append("用户已参加过活动，不要再输出主动留资文案；可说明身份验证成功，三重福利已经到账。")
    else:
        lines.append(
            f"用户未参加过活动或当前手机号状态未确认，回答末尾可以用分割线 `---` 单独隔开主动留资文案：{LEAD_CAPTURE_COPY} 用户提交手机号后如果仍未注册，再提示：{UNREGISTERED_LOGIN_COPY}"
        )

    if is_activity_query(context):
        lines.append(
            "用户正在问活动/福利/优惠，最终回答必须把“**Skill 用户大礼包**”作为独立品牌活动，和商品列表里的买一赠一、特价、畅饮卡等商品活动并列展示，不能只列商品活动。"
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
        render_order_followup_section(context, orders),
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
        return render_primary_response(
            "领取结果：请先登录小程序",
            build_unregistered_activity_lines(data.get("requestedMobile")),
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
        title = "领取结果：身份验证成功"
        lines.extend(build_activity_completion_lines(kind, coupon_names))
    elif kind == "obtained_after_registration":
        title = "领取结果：身份验证成功"
        lines.extend(build_activity_completion_lines(kind, coupon_names))
    elif kind == "already_claimed":
        title = "领取结果：身份验证成功"
        lines.extend(build_activity_completion_lines(kind, coupon_names))
    elif kind == "no_reward_config":
        title = "领取方式"
        lines.extend(build_activity_flow_lines())
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
