# SkiPass Atlas

**一张地图看清：手上的雪票能去哪些雪场，去之前要知道什么。**

买了 Ikon、Epic、Indy 或者其他雪票，想找个周末去滑雪？在地图上点开任意一座雪场，就能看到这张票在那里怎么用、哪天不能用、几点开门、有没有夜场、会不会很挤。

目前覆盖 **美国东海岸 2026-27 雪季**（缅因到田纳西，100 多个雪场），以后会扩展到全北美。

## 打开地图

| 版本 | 适合 | 链接 |
|---|---|---|
| **Google 地图版** | 手机上直接看、导航过去，不用装任何东西 | [打开 Google 地图](https://www.google.com/maps/d/viewer?mid=1v73g1b2VCTcrjQ8O72NQ3vNLTQ4SbUE) |
| **网页版** | 按雪票、州、规模、夜场筛选，看热门 Top 20 | `docs/index.html`（开启 GitHub Pages 后可在线打开） |

## 每座雪场能看到什么

- **哪些雪票能用**：无限次、有限天数，还是 Bonus（赠送天数或折扣）
- **限制日**：哪些日子这张票不能用（通常是圣诞新年、MLK 周末、总统日周末），以及要不要提前预约
- **开放时间**：每周开哪几天、几点到几点
- **夜场**：有没有，哪几晚，开到几点
- **繁忙程度**：旺季和平日分别有多挤，附错峰建议
- **规模**：迷你、小型、中型、大型、超大型，以及雪道数量
- **雪场官网**

## 收录的雪票

Ikon、Epic、Indy、Snow Pass、Mountain Collective、SKI3（纽约州 Whiteface / Gore / Belleayre）、Boyne New England、White Mountain Super Pass。

还没收录的其他通票（Freedom Pass、各州儿童护照等）整理在 [research/other-passes.md](research/other-passes.md)。

## 怎么看

- 一座雪场在多张雪票上时，网页版的圆点会分成几种颜色；Google 地图版会在旁边放几个点，每个点对应一张票。
- **限制日**就是英文里的 blackout dates。便宜的版本（Ikon Base、Epic Local、Indy Base）限制日通常更多。
- **规模**综合了雪道数、落差和面积。超大型是 Killington、Sugarloaf、Sunday River 这一级；中型大概是 Hunter 这一级。

## 注意

信息整理自各雪票和雪场官网及公开报道（2026 年 10 月）。很多雪场还没公布 2026-27 雪季的营业时间，暂时用的是上一季的时刻表；繁忙程度是估算。**出发前请以雪场官网为准。**

发现信息有误或想补充雪场，欢迎开 Issue。

---

## 维护与贡献

数据都在 `data/` 文件夹，格式说明见 [data/README.md](data/README.md)。改完后运行一次构建，就会更新网页版和 Google 地图导入文件：

```bash
python scripts/build.py
```

- 本地预览网页版：`python -m http.server 8000 --directory docs`，然后打开 http://localhost:8000
- 发布网页版：仓库 Settings → Pages，Branch 选 `main`，Folder 选 `/docs`
- 更新 Google 地图版：按 [exports/gmaps/README.md](exports/gmaps/README.md) 重新导入对应图层

**相关项目**：[OpenSkiMap](https://openskimap.org) / [skimap.org](https://skimap.org) 有全球雪场和雪道的开源地理数据（不含雪票信息）；各雪票官网也有自家雪场地图，但只显示自家雪场。
