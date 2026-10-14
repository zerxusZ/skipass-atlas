# SkiPass Atlas

北美滑雪通票地图：在一张地图上看清楚每座雪场能用哪些 pass、怎么用，以及规模、开放时间、夜场、限制日和繁忙程度。

*An interactive map of North American ski resorts by multi-resort pass (Ikon, Epic, Indy, Mountain Collective and regional passes), with per-resort details. Currently covers the US East Coast for the 2026-27 season.*

## 覆盖范围

- **地区**：美国东北、中大西洋、东南（已逐个核实 103 个高山雪场），加拿大东部部分雪场；以后计划扩展到全北美。
- **通票**：Ikon、Epic、Indy、Snow Pass、Mountain Collective、SKI3、Boyne New England、White Mountain Super Pass，包括 bonus 山和越野滑雪（XC）合作点。
- **每个雪场的信息**：pass 权益（无限 / 有限 / Bonus）、规模（迷你到超大型）、雪道/落差/面积/缆车、每周开放时间、夜场、各 pass 限制日、旺季/淡季繁忙程度、雪场官网。

## 使用

网页版在 `docs/`，是纯静态页面（Leaflet + OpenStreetMap，不需要 API key）。

```bash
python -m http.server 8000 --directory docs
```

然后打开 http://localhost:8000 。也可以开启 GitHub Pages（Settings → Pages → Branch: `main`，Folder: `/docs`）直接发布。

Google My Maps 版本在 `exports/gmaps/`，导入步骤见 [exports/gmaps/README.md](exports/gmaps/README.md)。

## 目录结构

```
data/
  passes.json        通票登记表：名称、简称、颜色、官网
  regions.json       州/省 → 地区，以及默认显示的地区
  popularity.json    热门排序（侧栏 Top 20 用）
  websites.json      雪场官网
  passes/*.json      每个 pass 一份雪场名单
  details/*.json     每个雪场的核实信息
docs/                网页版（index.html + 生成的 data.js）
exports/             生成的 CSV / KML / Google My Maps 文件
research/            调研笔记（例如尚未收录的其他通票）
scripts/             build.py（构建全部输出）、gmaps.py（My Maps 导出）
```

## 更新数据

改完 `data/` 里的文件后运行（需要 Python 3.9+，无第三方依赖）：

```bash
python scripts/build.py
```

它会生成 `docs/data.js` 和 `exports/` 下的全部文件。数据格式见 [data/README.md](data/README.md)。

**规模分级**：综合分 = 雪道数 50% + 落差 30% + 面积 20%（落差和面积先按全体中位数换算成"等效雪道数"）。≤15 迷你，16–40 小型，41–80 中型，81–125 大型，126+ 超大型。

## 相关项目

- [OpenSkiMap](https://openskimap.org) / [skimap.org](https://skimap.org)：全球雪场与雪道的开源地理数据，没有 pass 信息，可以作为以后扩展的底图和坐标来源。
- Reddit 上有人做过 Ikon / Epic / Indy / Mountain Collective 的 Google My Maps 图层，但只有位置，没有核实过，也不含详细信息。
- 各 pass 官网都有自己的雪场地图，但只显示自家雪场。

## 免责声明

数据整理自各 pass 和雪场官网及公开报道（2026 年 10 月）。很多雪场还没公布 2026-27 雪季的营业时间，用的是 2025-26 时刻表；繁忙程度是估算。出发前请以官网为准。
