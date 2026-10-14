# 数据格式

所有文本用简体中文，不用 emoji，"blackout" 一律写成"限制日"（构建脚本也会自动替换）。

## passes.json

```json
{"Ikon": {"name": "Ikon", "short": "Ikon", "color": "#e0a100", "url": "https://www.ikonpass.com"}}
```

键是 pass 代码，`passes/*.json` 里的 `pass` 字段必须用这个代码。顺序就是网页和导出里的显示顺序。

## regions.json

把每个州/省映射到地区。`default` 是网页打开时默认勾选的地区。新增的州/省没有登记时，构建会报错提示。

## passes/<pass>.json

每个 pass 一份雪场名单：

```json
{"name": "Loon Mountain", "state": "NH", "lat": 44.0364, "lng": -71.6214,
 "pass": "Ikon", "access": "limited", "note": "Ikon 7 天 / Base 5 天", "base_excluded": false}
```

- `access`：`unlimited` 无限 / `limited` 有限 / `bonus` 折扣或赠送天数
- `kind`：可选，越野滑雪点写 `"xc"`
- 同一座雪场在不同 pass 文件里会按名字自动合并（忽略 Ski、Resort、Mountain 等词）。合并后的 id 形如 `loon|NH`

## details/*.json

每个雪场的核实信息，按 id 对应：

```json
{"id": "loon|NH", "name": "Loon Mountain",
 "blackout": "Ikon：无；Ikon Base：12/26-30、1/16-17、2/13-14",
 "days_open": "每天", "hours": "平日 9:00-16:00；周末 8:00-16:00（2025-26 时刻表）",
 "night": {"has": false, "detail": ""},
 "crowd": {"peak": "高 — 原因", "offpeak": "中 — 原因", "tip": "建议"},
 "size": {"vertical_ft": 2190, "acres": 403, "trails": 73, "lifts": 13, "summit_ft": 3050}}
```

也可以不写 `id`，改写 `name` + `state`，脚本会自动匹配。额外的 `extra_blackout` 会追加到该雪场的限制日后面（用于单独调研的 pass，比如 Mountain Collective）。规模分级（`size.label`）由脚本计算，不用手填。

## websites.json

`{"loon|NH": "https://www.loonmtn.com"}`，只放雪场官网。

## popularity.json

雪场名按热门程度排列，用于侧栏 Top 20；不在列表里的按面积排在后面。
