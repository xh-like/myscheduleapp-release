# -*- coding: utf-8 -*-
"""把腾讯文档「运维作业计划申请」的月度子表 CSV 转成 App 用的 plans.json。

用法:
    python gen_plans.py <csv目录> <输出json路径> [今天yyyy-MM-dd]

规则:
  - 表内没有“完成状态”列，未完成 = 日期 >= 今天。
  - 子表名形如 26年10月，若单元格年份与子表年份不符（常见 2025 笔误），以子表年份为准。
"""
import csv, json, os, re, sys, datetime

COLS = ["no", "date", "cat", "dept", "time", "content", "site", "area", "note",
        "staff", "risk", "temp", "tag"]

WEEK = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]


def parse_date(text, sheet_year):
    s = (text or "").strip()
    m = re.search(r"(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日", s)
    if m:
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if sheet_year and y != sheet_year:
            y = sheet_year           # 修正年份笔误
    else:
        m = re.search(r"(\d{1,2})\s*[月./-]\s*(\d{1,2})", s)
        if not (m and sheet_year):
            return None
        y, mo, d = sheet_year, int(m.group(1)), int(m.group(2))
    try:
        return datetime.date(y, mo, d)
    except ValueError:
        return None


def main():
    csv_dir = sys.argv[1]
    out_path = sys.argv[2]
    today = datetime.date.fromisoformat(sys.argv[3]) if len(sys.argv) > 3 else datetime.date.today()

    plans = []
    files = sorted(os.listdir(csv_dir))
    for fn in files:
        if not fn.lower().endswith(".csv"):
            continue
        m = re.match(r"(\d{2})年(\d{1,2})月", fn)
        if not m:
            continue
        sheet_year = 2000 + int(m.group(1))
        sheet_month = int(m.group(2))
        with open(os.path.join(csv_dir, fn), encoding="utf-8-sig", newline="") as f:
            rows = list(csv.reader(f))
        for r in rows[1:]:
            if len(r) < 7:
                continue
            r = r + [""] * (len(COLS) - len(r))
            d = parse_date(r[1], sheet_year)
            if not d or d.month != sheet_month:
                continue
            content = r[5].strip()
            if not content:
                continue
            if d < today:                       # 已过期 = 已完成
                continue
            plans.append({
                "id": "%s-%s" % (fn.replace("年", "").replace("月", "").replace(".csv", ""), len(plans) + 1),
                "no": r[0].strip(),
                "date": d.isoformat(),
                "week": WEEK[d.weekday()],
                "time": r[4].strip().replace("：", ":"),
                "content": content,
                "site": r[6].strip(),
                "area": r[7].strip(),
                "dept": r[3].strip(),
                "cat": r[2].strip(),
                "note": r[8].strip(),
                "tag": r[12].strip(),
                "month": "%d-%02d" % (d.year, d.month),
            })

    plans.sort(key=lambda p: (p["date"], p["time"]))
    payload = {
        "updatedAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "source": "腾讯文档·运维作业计划申请",
        "rule": "未完成 = 计划日期 ≥ 今天",
        "today": today.isoformat(),
        "count": len(plans),
        "plans": plans,
    }
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    print("wrote", out_path, "plans:", len(plans), "today:", today)


if __name__ == "__main__":
    main()
