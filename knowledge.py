import json
import re
import os

UNIVERSITIES = [
    {
        "university": "武汉大学",
        "alias": ["武大", "WHU"],
        "province": "湖北",
        "city": "武汉",
        "type": "综合类",
        "level": "985/211/双一流",
        "dormitory": {
            "type": "四人间为主，部分三人间",
            "air_conditioner": "有空调",
            "private_bathroom": "无独立卫浴，公共浴室有隔间和帘子",
            "hot_water": "全天供应，刷卡计费",
            "internet": "校园网全覆盖，每月免费20G",
            "laundry": "每栋楼配公共洗衣机+烘干机",
            "curfew": "23:00门禁",
            "fee": "800-1200元/学年"
        },
        "cafeteria": {
            "count": "16个食堂",
            "features": "梅园食堂（网红餐厅）、枫园食堂（小碗菜）、湖滨食堂（东湖景观）",
            "avg_price": "10-18元/餐",
            "specialties": "热干面、小龙虾、藕汤",
            "hours": "6:30-22:00"
        },
        "campus": {
            "location": "武汉市武昌区珞珈山",
            "area": "5195亩",
            "green_rate": "绿化覆盖率60%+",
            "surrounding": "东湖绿道、广埠屯商圈",
            "transportation": "地铁2号线街道口站/8号线小洪山站",
            "reputation": "最美大学之一，樱花季游客较多"
        },
        "student_review": "宿舍虽没独卫但公共浴室很干净，阿姨每天打扫三遍；文理学部坡多，每天上课像爬山；新生大概率分信息学部，四人间有空调",
        "source": "2025年武大学生调研+学校官网",
        "data_year": "2025"
    },
    {
        "university": "厦门大学",
        "alias": ["厦大", "XMU"],
        "province": "福建",
        "city": "厦门",
        "type": "综合类",
        "level": "985/211/双一流",
        "dormitory": {
            "type": "四人间/二人间（研究生）",
            "air_conditioner": "有空调",
            "private_bathroom": "有独立卫浴、热水器",
            "hot_water": "全天供应",
            "internet": "校园网全覆盖",
            "laundry": "每层有公共洗衣机",
            "curfew": "无门禁，刷卡进出",
            "fee": "800-1500元/学年；思明校区部分海景房"
        },
        "cafeteria": {
            "count": "10+个食堂",
            "features": "芙蓉食堂（手撕鸡拌面）、南光食堂（网红老婆饼）、勤业食堂",
            "avg_price": "12-25元/餐",
            "specialties": "老婆饼、手撕鸡拌面、沙茶面",
            "hours": "6:30-22:30"
        },
        "campus": {
            "location": "厦门市思明区",
            "area": "2600+亩",
            "green_rate": "绿化覆盖率55%+",
            "surrounding": "南普陀寺、白城沙滩",
            "transportation": "公交厦大白城站、靠近环岛路",
            "reputation": "推窗见海，中国最美校园之一"
        },
        "student_review": "住宿条件全国顶尖，海景宿舍名不虚传；食堂好吃不贵，南光老婆饼下午四点就排长队；校园太美导致游客多，上课常被旅游团围观",
        "source": "2025年厦大学生调研+学校官网",
        "data_year": "2025"
    },
    {
        "university": "浙江大学",
        "alias": ["浙大", "ZJU"],
        "province": "浙江",
        "city": "杭州",
        "type": "综合类",
        "level": "985/211/双一流",
        "dormitory": {
            "type": "四人间为主，紫金港校区大部分四人间有独卫",
            "air_conditioner": "有空调",
            "private_bathroom": "大部分有独立卫浴，部分老宿舍为公共浴室",
            "hot_water": "全天供应",
            "internet": "校园网全覆盖，免费",
            "laundry": "每栋楼有公共洗衣机",
            "curfew": "23:30门禁",
            "fee": "1000-1600元/学年"
        },
        "cafeteria": {
            "count": "20+个食堂（7个校区）",
            "features": "紫金港大食堂（亚洲第二）、临湖餐厅（风景好）、麦香餐厅（西餐）",
            "avg_price": "10-20元/餐",
            "specialties": "红烧肉、片儿川、葱包烩",
            "hours": "6:30-22:30"
        },
        "campus": {
            "location": "杭州市西湖区（紫金港）/ 西湖区玉泉",
            "area": "4500+亩（紫金港）",
            "green_rate": "绿化覆盖率50%+",
            "surrounding": "西溪湿地、阿里总部附近",
            "transportation": "地铁5号线浙大紫金港站",
            "reputation": "综合实力顶尖，紫金港校区设施最新"
        },
        "student_review": "紫金港住宿条件很好，独卫+空调是标配；大食堂种类多到吃一个月不重样；校区太大建议买自行车",
        "source": "2025年浙大学生调研+学校官网",
        "data_year": "2025"
    },
    {
        "university": "四川大学",
        "alias": ["川大", "SCU"],
        "province": "四川",
        "city": "成都",
        "type": "综合类",
        "level": "985/211/双一流",
        "dormitory": {
            "type": "四人间/六人间（不同校区差异大）",
            "air_conditioner": "有空调",
            "private_bathroom": "江安校区有独卫，望江校区部分有",
            "hot_water": "定时供应（早晚时段）",
            "internet": "校园网全覆盖",
            "laundry": "公共洗衣机",
            "curfew": "23:00门禁",
            "fee": "800-1200元/学年"
        },
        "cafeteria": {
            "count": "十几个食堂",
            "features": "江安西园一餐（网红）、望江活动中心食堂",
            "avg_price": "8-15元/餐",
            "specialties": "回锅肉、夫妻肺片、担担面",
            "hours": "6:30-22:00"
        },
        "campus": {
            "location": "成都市武侯区/双流区",
            "area": "7000+亩（三个校区）",
            "green_rate": "绿化覆盖率高",
            "surrounding": "望江校区在市中心，江安校区靠近机场",
            "transportation": "地铁1号线/8号线",
            "reputation": "江安校区设施最新，望江校区有历史底蕴"
        },
        "student_review": "江安校区住宿条件最好，四人间有独卫；食堂便宜大碗，8块钱能吃饱；成都美食太多，容易长胖",
        "source": "2025年川大学生调研+学校官网",
        "data_year": "2025"
    },
    {
        "university": "华中科技大学",
        "alias": ["华科", "HUST"],
        "province": "湖北",
        "city": "武汉",
        "type": "理工类",
        "level": "985/211/双一流",
        "dormitory": {
            "type": "四人间为主",
            "air_conditioner": "有空调",
            "private_bathroom": "大部分有独立卫浴",
            "hot_water": "全天供应",
            "internet": "校园网全覆盖",
            "laundry": "公共洗衣机+烘干机",
            "curfew": "23:30门禁",
            "fee": "1000-1400元/学年"
        },
        "cafeteria": {
            "count": "30+个食堂（全国最多之一）",
            "features": "百景园（网红）、西一/西二食堂、韵苑食堂",
            "avg_price": "8-18元/餐",
            "specialties": "热干面、豆皮、藕汤",
            "hours": "6:00-22:30"
        },
        "campus": {
            "location": "武汉市洪山区珞喻路",
            "area": "7000+亩",
            "green_rate": "森林大学，绿化覆盖率70%+",
            "surrounding": "光谷广场、鲁巷商圈",
            "transportation": "地铁2号线华中科技大学站",
            "reputation": "森林大学，校园内有大片梧桐树"
        },
        "student_review": "30多个食堂真的吃不完，百景园性价比超高；校园像森林，空气好但梧桐絮多；理工科氛围浓厚，学习压力大",
        "source": "2025年华科学生调研+学校官网",
        "data_year": "2025"
    }
]


def find_university(query):
    query_lower = query.lower()
    for uni in UNIVERSITIES:
        if uni["university"] in query or any(a in query for a in uni["alias"]):
            return uni
    for uni in UNIVERSITIES:
        if uni["province"] in query or uni["city"] in query:
            return uni
    return None


def extract_intent(query):
    dorm_keywords = ["宿舍", "寝室", "住宿", "住", "几人间", "独卫", "空调", "门禁"]
    food_keywords = ["食堂", "吃", "美食", "餐厅", "饭", "伙食", "菜品"]
    env_keywords = ["环境", "校园", "位置", "交通", "面积", "绿化", "周边"]

    dorm = any(k in query for k in dorm_keywords)
    food = any(k in query for k in food_keywords)
    env = any(k in query for k in env_keywords)

    if "对比" in query or "vs" in query.lower():
        return "compare"
    if dorm and not food and not env:
        return "dormitory"
    if food and not dorm and not env:
        return "cafeteria"
    if env and not dorm and not food:
        return "campus"
    return "all"


def format_answer(uni):
    return (
        f"【{uni['university']}】基本信息\n"
        f"📍 所在地：{uni['province']} {uni['city']}\n"
        f"🏫 类型：{uni['type']} | {uni['level']}\n\n"

        f"【宿舍条件】\n"
        f"类型：{uni['dormitory']['type']}\n"
        f"空调：{uni['dormitory']['air_conditioner']}\n"
        f"卫浴：{uni['dormitory']['private_bathroom']}\n"
        f"热水：{uni['dormitory']['hot_water']}\n"
        f"网络：{uni['dormitory']['internet']}\n"
        f"洗衣：{uni['dormitory']['laundry']}\n"
        f"门禁：{uni['dormitory']['curfew']}\n"
        f"费用：{uni['dormitory']['fee']}\n\n"

        f"【食堂情况】\n"
        f"数量：{uni['cafeteria']['count']}\n"
        f"特色：{uni['cafeteria']['features']}\n"
        f"人均：{uni['cafeteria']['avg_price']}\n"
        f"招牌：{uni['cafeteria']['specialties']}\n"
        f"营业：{uni['cafeteria']['hours']}\n\n"

        f"【校园环境】\n"
        f"地址：{uni['campus']['location']}\n"
        f"面积：{uni['campus']['area']}\n"
        f"绿化：{uni['campus']['green_rate']}\n"
        f"周边：{uni['campus']['surrounding']}\n"
        f"交通：{uni['campus']['transportation']}\n"
        f"口碑：{uni['campus']['reputation']}\n\n"

        f"【学长学姐说】\n{uni['student_review']}"
    )


def format_answer_by_intent(uni, intent):
    if intent == "dormitory":
        d = uni["dormitory"]
        return (
            f"【{uni['university']} - 宿舍条件】\n"
            f"类型：{d['type']}\n空调：{d['air_conditioner']}\n"
            f"卫浴：{d['private_bathroom']}\n热水：{d['hot_water']}\n"
            f"网络：{d['internet']}\n洗衣：{d['laundry']}\n"
            f"门禁：{d['curfew']}\n费用：{d['fee']}\n\n"
            f"学长说：{uni['student_review']}"
        )
    elif intent == "cafeteria":
        c = uni["cafeteria"]
        return (
            f"【{uni['university']} - 食堂情况】\n"
            f"数量：{c['count']}\n特色窗口：{c['features']}\n"
            f"人均价格：{c['avg_price']}\n招牌美食：{c['specialties']}\n"
            f"营业时间：{c['hours']}"
        )
    elif intent == "campus":
        c = uni["campus"]
        return (
            f"【{uni['university']} - 校园环境】\n"
            f"地址：{c['location']}\n面积：{c['area']}\n"
            f"绿化：{c['green_rate']}\n周边配套：{c['surrounding']}\n"
            f"交通：{c['transportation']}\n综合评价：{c['reputation']}"
        )
    else:
        return format_answer(uni)


def handle_compare(query):
    pairs = re.split(r"和|与|vs|跟", query)
    names = [p.strip() for p in pairs if p.strip()]
    found = []
    for name in names:
        for u in UNIVERSITIES:
            if u["university"] in name or any(a in name for a in u["alias"]):
                found.append(u)
                break

    if len(found) < 2:
        return "需要两所不同的院校才能对比，请指定两个学校名称，例如'对比武大和厦大的宿舍'"

    result = f"【对比：{found[0]['university']} vs {found[1]['university']}】\n\n"

    result += "┌──────────────┬──────────────┬──────────────┐\n"
    result += f"│              │ {found[0]['university']:<10} │ {found[1]['university']:<10} │\n"
    result += "├──────────────┼──────────────┼──────────────┤\n"

    dorms = []
    for u in found:
        d = u['dormitory']
        dorms.append(f"{d['type']} | {d['air_conditioner']} | {'有独卫' if '有' in d['private_bathroom'] else '公共浴室'}")

    result += f"│ 宿舍          │ {dorms[0]:<12} │ {dorms[1]:<12} │\n"
    result += "├──────────────┼──────────────┼──────────────┤\n"

    prices = []
    for u in found:
        prices.append(u['cafeteria']['avg_price'])

    result += f"│ 食堂均价      │ {prices[0]:<12} │ {prices[1]:<12} │\n"
    result += "└──────────────┴──────────────┴──────────────┘\n\n"

    result += f"📌 {found[0]['university']}学长说：{found[0]['student_review']}\n"
    result += f"📌 {found[1]['university']}学长说：{found[1]['student_review']}"

    return result


def handle_recommend(query):
    levels = {"985": [], "211": [], "双一流": []}
    for u in UNIVERSITIES:
        for k in levels:
            if k in u["level"]:
                levels[k].append(u["university"])

    dorm_keywords = ["宿舍好", "住宿好", "条件好", "独卫", "好宿舍"]
    if any(k in query for k in dorm_keywords):
        good_dorm = [
            "厦门大学", "浙江大学", "华中科技大学",
            "深圳大学", "南方科技大学"
        ]
        result = "以下院校宿舍条件普遍较好（独立卫浴+空调+四人间）：\n"
        for u in UNIVERSITIES:
            if u["university"] in good_dorm:
                d = u["dormitory"]
                result += (
                    f"  ✅ {u['university']}（{u['level']}）\n"
                    f"     {d['type']} | {d['private_bathroom']} | {d['air_conditioner']}\n"
                )
        return result

    food_keywords = ["食堂好", "好吃", "美食多", "吃得好"]
    if any(k in query for k in food_keywords):
        good_food = ["华中科技大学", "浙江大学", "厦门大学", "四川大学"]
        result = "以下院校食堂备受好评：\n"
        for u in UNIVERSITIES:
            if u["university"] in good_food:
                c = u["cafeteria"]
                result += (
                    f"  🍜 {u['university']}（{u['level']}）\n"
                    f"     食堂数量：{c['count']} | 人均：{c['avg_price']}\n"
                    f"     招牌：{c['specialties']}\n"
                )
        return result

    result = "以下不同层次院校供参考：\n"
    for level, unis in levels.items():
        if unis:
            result += f"\n【{level}】{', '.join(unis[:5])}"
    return result


def query_knowledge(query, list_only=False):
    if list_only:
        return [u["university"] for u in UNIVERSITIES]

    if not query:
        return {
            "answer": "你好！我是高考择校助手。我可以帮你查询院校的宿舍、食堂、校园环境等信息。"
                       "试试问我：'武汉大学宿舍怎么样'、'哪个学校食堂好吃'、'对比武大和厦大'",
            "source_hint": "",
            "data_year": "2025"
        }

    if "推荐" in query or "哪个" in query or "哪些" in query:
        text = handle_recommend(query)
        return {
            "answer": text,
            "source_hint": "多所院校数据综合",
            "data_year": "2025"
        }

    if "对比" in query and ("和" in query or "与" in query or "vs" in query.lower()):
        text = handle_compare(query)
        if text.startswith("需要"):
            return {"answer": text, "source_hint": "", "data_year": "2025"}
        return {
            "answer": text,
            "source_hint": "相关院校数据综合",
            "data_year": "2025"
        }

    uni = find_university(query)
    if not uni:
        return {
            "answer": f"关于「{query}」的信息暂未收录。我们目前收录了以下院校：\n"
                       + "\n".join(f"  {u['university']}" for u in UNIVERSITIES)
                       + "\n\n更多院校正在持续更新中，欢迎反馈需求！",
            "source_hint": "",
            "data_year": "2025"
        }

    intent = extract_intent(query)
    text = format_answer_by_intent(uni, intent)

    return {
        "answer": text,
        "source_hint": uni["source"],
        "data_year": uni["data_year"]
    }
