# Google My Maps 导入说明

每个雪场按 pass 拆成多行：一座山在几个 pass 上，就有几个点，每个点只写一个 pass 的权益。
同一座山的几个点围成一个约 300 m 的小圈，方便分别点开。

只有 5 列：`Name`、`Latitude`、`Longitude`、`Pass`、`Details`。规模、开放时间、夜场、限制日、繁忙程度、官网都合并在 `Details` 里。

## 推荐做法：每个 pass 一个图层（可以单独开关）

1. 打开 https://www.google.com/mymaps → **Create a new map**，改个地图名
2. 默认图层点 **Import**，上传 `Ikon.csv`
   - 位置列勾选 `Latitude`、`Longitude`
   - 标题列选 `Name`
3. 点 **Add layer**，再导入 `Epic.csv`；依次导入 `Indy.csv`、`Snow.csv`、`MC.csv`、`SKI3.csv`、`Boyne.csv`、`WMSP.csv`（共 8 个图层，My Maps 上限是 10 个）
4. 每个图层点 **Uniform style** 旁的油漆桶，选一种颜色（建议和网页版一致：Ikon 黄、Epic 蓝、Indy 玫红、Snow 绿、MC 紫、SKI3 黑、Boyne 赭色、White Mountain 青色）
5. 右上角 **Share** → 打开 "Anyone with the link can view"，复制链接即可分享

## 省事做法：一个图层

导入 `all.csv`，在图层里选 **Style by data column → Pass**，每个 pass 自动一种颜色。缺点是没法单独开关某个 pass。

## 更新数据

```bash
python scripts/build.py
```

然后在 My Maps 里删掉旧图层，重新导入。
