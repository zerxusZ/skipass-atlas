"""Build SkiPass Atlas: merge data/passes/*.json + data/details/*.json into docs/data.js and the exports.

Usage:  python scripts/build.py
"""
import csv
import json
import re
import sys
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape

import gmaps

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
EXPORTS = ROOT / "exports"
DROP_WORDS = r"\b(ski|resort|area|mountain|mtn|mt|the|and|center|centre|club|bowl)\b"
EMOJI = re.compile("[\U0001F000-\U0001FAFF☀-➿️‍]")
SIZE_WEIGHTS = {"trails": 0.5, "vertical_ft": 0.3, "acres": 0.2}
SIZE_TIERS = ((15, "迷你"), (40, "小"), (80, "中"), (125, "大"))


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def key(name):
    """Normalized resort name used to match the same resort across pass lists."""
    n = name.lower().replace("&", " and ").replace("’", "'")
    n = re.sub(r"\(.*?\)", " ", n)
    n = re.sub(DROP_WORDS, " ", n)
    return re.sub(r"[^a-z0-9]", "", n)


def clean(v):
    """Strip emoji and use 限制日 for blackout throughout the text fields."""
    if isinstance(v, str):
        v = EMOJI.sub("", v)
        return re.sub(r"\s*blackout\s*", "限制日", v, flags=re.I).strip()
    if isinstance(v, list):
        return [clean(x) for x in v]
    if isinstance(v, dict):
        return {k: clean(x) for k, x in v.items()}
    return v


def size_scores(sizes):
    """Weighted size score in trail-equivalent units: vertical and acres are scaled by the ratio of the
    dataset medians to trails, then blended 50/30/20; weights renormalize when a metric is missing."""
    def median(xs):
        xs = sorted(xs)
        return xs[len(xs) // 2] if xs else None
    med = {k: median([s[k] for s in sizes if s.get(k)]) for k in SIZE_WEIGHTS}
    scale = {k: med["trails"] / med[k] for k in SIZE_WEIGHTS}
    scores = []
    for s in sizes:
        parts = {k: s[k] * scale[k] for k in SIZE_WEIGHTS if s.get(k)}
        w = sum(SIZE_WEIGHTS[k] for k in parts)
        scores.append(round(sum(SIZE_WEIGHTS[k] * v for k, v in parts.items()) / w, 1) if w else None)
    return scores


def size_label(score):
    """<=15 迷你, 16-40 小, 41-80 中, 81-125 大, 126+ 超大 (on the weighted score)."""
    if score is None:
        return None
    for limit, label in SIZE_TIERS:
        if score <= limit:
            return label
    return "超大"


def kml_color(hex_color):
    r, g, b = hex_color[1:3], hex_color[3:5], hex_color[5:7]
    return f"ff{b}{g}{r}"


def main():
    passes = load(DATA / "passes.json")
    regions_cfg = load(DATA / "regions.json")
    state_region = {st: code for code, reg in regions_cfg["regions"].items() for st in reg["states"]}
    pass_order = list(passes)

    merged = {}
    for f in sorted((DATA / "passes").glob("*.json")):
        for r in load(f):
            st = r["state"].upper()
            if st not in state_region:
                sys.exit(f"{f.name}: unknown state/province {st!r} for {r['name']} — add it to data/regions.json")
            if r["pass"] not in passes:
                sys.exit(f"{f.name}: unknown pass {r['pass']!r} — add it to data/passes.json")
            k = key(r["name"]) + "|" + st
            m = merged.setdefault(k, {"id": k, "name": r["name"], "state": st, "lat": r["lat"], "lng": r["lng"],
                                      "region": state_region[st], "kind": "xc", "passes": []})
            if r.get("kind") != "xc":
                m["kind"] = "alpine"
            if any(p["pass"] == r["pass"] for p in m["passes"]):
                print(f"duplicate within pass: {r['pass']} {r['name']}", file=sys.stderr)
                continue
            m["passes"].append({"pass": r["pass"], "access": r["access"],
                                "note": clean(r.get("note", "")), "base_excluded": bool(r.get("base_excluded"))})
    resorts = sorted(merged.values(), key=lambda r: (list(regions_cfg["regions"]).index(r["region"]), r["state"], r["name"]))

    # Details: entries carry an "id" (name|ST); entries with only name/state are matched by name and may add an
    # "extra_blackout" line for a pass whose research was done separately (e.g. Mountain Collective).
    info = {}
    for f in sorted((DATA / "details").glob("*.json")):
        for d in load(f):
            k = d.get("id") or key(d["name"]) + "|" + d["state"].upper()
            extra = d.get("extra_blackout", "")
            body = {kk: v for kk, v in d.items()
                    if kk not in ("id", "name", "state", "confidence", "sources", "extra_blackout")}
            cur = info.setdefault(k, {})
            for kk, v in body.items():
                cur.setdefault(kk, v)
            if extra:
                cur["blackout"] = (cur.get("blackout", "") + "\n" + extra).strip()
    websites = load(DATA / "websites.json")

    for r in resorts:
        r["passes"].sort(key=lambda p: pass_order.index(p["pass"]))
        if r["id"] in info:
            r["info"] = clean(info[r["id"]])
            r["info"]["size"] = r["info"].get("size") or {}
            if websites.get(r["id"]):
                r["info"]["website"] = websites[r["id"]]
    sized = [r for r in resorts if "info" in r]
    for r, score in zip(sized, size_scores([r["info"]["size"] for r in sized])):
        r["info"]["size"]["score"] = score
        r["info"]["size"]["label"] = size_label(score)

    popular_list = load(DATA / "popularity.json")
    popular = {name: i for i, name in enumerate(popular_list)}
    ranked = sorted((r for r in resorts if r["kind"] == "alpine"),
                    key=lambda r: (popular.get(r["name"], len(popular)),
                                   -((r.get("info") or {}).get("size", {}).get("acres") or 0)))
    for i, r in enumerate(ranked):
        r["rank"] = i + 1
    unknown = set(popular_list) - {r["name"] for r in resorts}
    if unknown:
        print(f"popularity.json names not found: {sorted(unknown)}", file=sys.stderr)
    default = set(regions_cfg["default"])
    missing = [r["name"] for r in resorts if r["region"] in default and r["kind"] == "alpine" and "info" not in r]
    if missing:
        print(f"{len(missing)} alpine resorts in default regions without details: {', '.join(missing)}", file=sys.stderr)

    used_regions = [c for c in regions_cfg["regions"] if any(r["region"] == c for r in resorts)]
    meta = {"updated": date.today().isoformat(), "passes": passes,
            "regions": {c: regions_cfg["regions"][c]["label"] for c in used_regions},
            "defaultRegions": [c for c in regions_cfg["default"] if c in used_regions]}
    (ROOT / "docs" / "data.js").write_text(
        f"window.META = {json.dumps(meta, ensure_ascii=False, indent=1)};\n"
        f"window.RESORTS = {json.dumps(resorts, ensure_ascii=False, indent=1)};\n", encoding="utf-8")

    write_exports(resorts, meta, pass_order)
    gmaps.export(resorts, meta, EXPORTS / "gmaps")

    counts = {p: sum(any(q["pass"] == p for q in r["passes"]) for r in resorts) for p in pass_order}
    print(f"{len(resorts)} resorts ({len(sized)} with details); per pass: {counts}")


def write_exports(resorts, meta, pass_order):
    EXPORTS.mkdir(exist_ok=True)

    # Checklist of every resort and whether its details have been researched.
    with open(EXPORTS / "resort-list.csv", "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "Name", "State", "Region", "Kind", "Passes", "Verified"])
        for r in resorts:
            w.writerow([r["id"], r["name"], r["state"], r["region"], r["kind"],
                        " + ".join(f"{p['pass']}:{p['access']}" for p in r["passes"]), "yes" if "info" in r else ""])

    def summary(r):
        return "; ".join(f"{p['pass']} {p['access']}" + (f" ({p['note']})" if p["note"] else "") for p in r["passes"])

    def details(r):
        i = r.get("info") or {}
        s, n, c = i.get("size") or {}, i.get("night") or {}, i.get("crowd") or {}
        return {"Size": s.get("label") or "", "Website": i.get("website") or "",
                "Vertical_ft": s.get("vertical_ft") or "", "Acres": s.get("acres") or "",
                "Trails": s.get("trails") or "", "Lifts": s.get("lifts") or "",
                "Hours": " ".join(x for x in (i.get("days_open"), i.get("hours")) if x),
                "Night": ("有：" + (n.get("detail") or "")) if n.get("has") else ("无" if i else ""),
                "Blackout": i.get("blackout") or "", "Crowd_peak": c.get("peak") or "",
                "Crowd_offpeak": c.get("offpeak") or "", "Tip": c.get("tip") or ""}
    detail_cols = list(details({}).keys())

    # Full table, one row per resort.
    with open(EXPORTS / "resorts.csv", "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(["Name", "State", "Latitude", "Longitude", "Region", "Kind", "Passes", "Details"]
                   + pass_order + detail_cols)
        for r in resorts:
            by = {p["pass"]: p["access"] for p in r["passes"]}
            w.writerow([r["name"], r["state"], r["lat"], r["lng"], r["region"], r["kind"],
                        " + ".join(p["pass"] for p in r["passes"]), summary(r)]
                       + [by.get(p, "") for p in pass_order] + list(details(r).values()))

    # KML, one folder per region; resorts on several passes get a grey pin.
    colors = {code: kml_color(p["color"]) for code, p in meta["passes"].items()} | {"Multi": "ff7f7f7f"}
    styles = "".join(f'<Style id="{n}"><IconStyle><color>{c}</color><Icon><href>'
                     'http://maps.google.com/mapfiles/kml/paddle/wht-blank.png</href></Icon></IconStyle></Style>'
                     for n, c in colors.items())
    labels = {"Size": "规模", "Website": "官网", "Vertical_ft": "落差(ft)", "Acres": "英亩", "Trails": "雪道",
              "Lifts": "缆车", "Hours": "开放时间", "Night": "夜场", "Blackout": "限制日", "Crowd_peak": "旺季拥挤",
              "Crowd_offpeak": "淡季拥挤", "Tip": "建议"}

    def kml_desc(r):
        lines = [r["state"] + " — " + summary(r)]
        lines += [f"{labels[k]}：{v}" for k, v in details(r).items() if v != ""]
        return "\n".join(lines)

    folders = []
    for code, label in meta["regions"].items():
        marks = []
        for r in (x for x in resorts if x["region"] == code):
            style = r["passes"][0]["pass"] if len(r["passes"]) == 1 else "Multi"
            marks.append(f"<Placemark><name>{escape(r['name'])}</name><styleUrl>#{style}</styleUrl>"
                         f"<description>{escape(kml_desc(r))}</description>"
                         f"<Point><coordinates>{r['lng']},{r['lat']},0</coordinates></Point></Placemark>")
        folders.append(f"<Folder><name>{escape(label)}</name>{''.join(marks)}</Folder>")
    (EXPORTS / "resorts.kml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?><kml xmlns="http://www.opengis.net/kml/2.2"><Document>'
        f"<name>SkiPass Atlas</name>{styles}{''.join(folders)}</Document></kml>", encoding="utf-8")


if __name__ == "__main__":
    main()
