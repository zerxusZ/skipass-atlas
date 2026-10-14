"""Google My Maps edition: one row per (resort, pass) with only Name / Latitude / Longitude / Pass / Details.

Called from build.py. Writes all.csv plus one CSV per pass, so each pass can be imported as its own
toggleable My Maps layer. Rows for the same resort are fanned out in a small circle so the duplicate
pins don't sit exactly on top of each other.
"""
import csv
import math

ACCESS = {"unlimited": "无限", "limited": "有限", "bonus": "Bonus"}
SIZES = {"超大": "超大型", "大": "大型", "中": "中型", "小": "小型", "迷你": "迷你"}
FAN_RADIUS = 0.004  # degrees, roughly 300-400 m
COLUMNS = ["Name", "Latitude", "Longitude", "Pass", "Details"]


def num(v, unit=""):
    return "不明" if v is None else f"{v:,}{unit}"


def details(r, p, meta):
    names = {code: x["name"] for code, x in meta["passes"].items()}
    i = r.get("info") or {}
    lines = [f"{names[p['pass']]}（{ACCESS[p['access']]}）：{p['note']}"]
    others = [f"{names[q['pass']]}（{ACCESS[q['access']]}）" for q in r["passes"] if q is not p]
    if others:
        lines.append("同样可用：" + "、".join(others))
    kind = "越野滑雪" if r["kind"] == "xc" else "高山雪场"
    lines.append(f"{r['state']} · {meta['regions'][r['region']]} · {kind}")
    if i:
        s = i.get("size") or {}
        lines.append(f"规模：{SIZES.get(s.get('label'), '不明')}｜{num(s.get('trails'))} 条雪道｜落差 {num(s.get('vertical_ft'), ' ft')}"
                     f"｜{num(s.get('acres'))} 英亩｜{num(s.get('lifts'))} 条缆车")
        lines.append("开放时间：" + "；".join(x for x in (i.get("days_open"), i.get("hours")) if x))
        n = i.get("night")
        lines.append("夜场：" + ("不明" if not n else ("有，" + n.get("detail", "")) if n.get("has") else "无"))
        lines.append("限制日：" + (i.get("blackout") or "不明").replace("\n", "；"))
        c = i.get("crowd") or {}
        if c:
            lines.append(f"繁忙程度：旺季 {c.get('peak', '不明')}；淡季 {c.get('offpeak', '不明')}")
            if c.get("tip"):
                lines.append("建议：" + c["tip"])
        if i.get("website"):
            lines.append("官网：" + i["website"])
    return "\n".join(lines)


def export(resorts, meta, out_dir):
    rows = []
    for r in resorts:
        n = len(r["passes"])
        for k, p in enumerate(r["passes"]):
            lat, lng = r["lat"], r["lng"]
            if n > 1:
                angle = 2 * math.pi * k / n
                lat += FAN_RADIUS * math.cos(angle)
                lng += FAN_RADIUS * math.sin(angle) / math.cos(math.radians(r["lat"]))
            name = meta["passes"][p["pass"]]["name"]
            rows.append({"Name": f"{r['name']}｜{name}", "Latitude": round(lat, 5), "Longitude": round(lng, 5),
                         "Pass": name, "Details": details(r, p, meta)})

    out_dir.mkdir(parents=True, exist_ok=True)

    def write(path, subset):
        with open(path, "w", newline="", encoding="utf-8-sig") as fh:
            w = csv.DictWriter(fh, fieldnames=COLUMNS)
            w.writeheader()
            w.writerows(subset)

    write(out_dir / "all.csv", rows)
    for code, p in meta["passes"].items():
        write(out_dir / f"{code}.csv", [x for x in rows if x["Pass"] == p["name"]])
