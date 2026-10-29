# -*- coding: utf-8 -*-
"""云端（GitHub Actions）拉取腾讯文档《运维作业计划申请》的月度子表，导出为 CSV。

与本地 tencentdocs.py 的区别只在鉴权：
  本地 = WorkBuddy 宿主签发的会话票据（127.0.0.1 网关，离不开本机）
  云端 = 腾讯文档开放平台 Access Token（三元组请求头：Access-Token / Client-Id / Open-Id）

Client-Id 与 Open-Id 直接从 Access Token（JWT）的 clt / sub 声明里取，所以只需配一个 Secret。

环境变量：
  TDOC_ACCESS_TOKEN   必填。腾讯文档开放平台 access_token
  TDOC_CLIENT_ID      可选。覆盖 JWT 里的 clt
  TDOC_OPEN_ID        可选。覆盖 JWT 里的 sub
  TDOC_FILE_ID        可选。默认运维作业计划表

用法：
  python3 fetch_tencent_sheets.py --out-dir .plansrc
  python3 fetch_tencent_sheets.py --out-dir /tmp/x --csv-dir <本地CSV目录>   # 调试，不联网
"""
import argparse
import base64
import csv
import datetime
import json
import os
import shutil
import sys
import urllib.error
import urllib.parse
import urllib.request

DEFAULT_FILE_ID = "DTXdqTGdLVEVQSGF6"
API_BASE = "https://docs.qq.com/openapi/spreadsheet/v3/files/"
NCOL = 13  # A..M
COL_LETTER = "M"


def log(msg):
    print(msg, flush=True)


def die(msg):
    log("::error::%s" % msg)
    sys.exit(1)


def jwt_claims(token):
    try:
        payload = token.split(".")[1]
        payload += "=" * (-len(payload) % 4)
        return json.loads(base64.urlsafe_b64decode(payload))
    except Exception:  # noqa: BLE001
        return {}


def load_headers():
    token = os.environ.get("TDOC_ACCESS_TOKEN", "").strip()
    if not token:
        die("缺少 TDOC_ACCESS_TOKEN")
    claims = jwt_claims(token)
    client_id = os.environ.get("TDOC_CLIENT_ID", "").strip() or claims.get("clt", "")
    open_id = os.environ.get("TDOC_OPEN_ID", "").strip() or claims.get("sub", "")
    if not client_id or not open_id:
        die("无法从 token 解析 Client-Id / Open-Id，请显式设置 TDOC_CLIENT_ID 与 TDOC_OPEN_ID")

    exp = claims.get("exp")
    if exp:
        left = datetime.datetime.fromtimestamp(float(exp)) - datetime.datetime.now()
        if left.total_seconds() <= 0:
            die("Access Token 已过期（%s），请重新授权后更新 Secret"
                % datetime.datetime.fromtimestamp(float(exp)).strftime("%Y-%m-%d %H:%M"))
        if left.days < 7:
            log("::warning::Access Token 将于 %s 过期（剩 %d 天），请尽快换新"
                % (datetime.datetime.fromtimestamp(float(exp)).strftime("%Y-%m-%d"), left.days))
    return {"Access-Token": token, "Client-Id": client_id, "Open-Id": open_id}


def api_get(headers, path, timeout=90):
    url = API_BASE + path
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            obj = json.loads(resp.read().decode("utf-8", errors="replace"))
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8", errors="replace")[:300]
        except Exception:  # noqa: BLE001
            pass
        die("HTTP %s %s %s" % (e.code, e.reason, body))
    except Exception as e:  # noqa: BLE001
        die("请求失败 %s: %s" % (path, e))
    if obj.get("code"):
        die("接口返回错误 code=%s message=%s" % (obj.get("code"), obj.get("message")))
    return obj


def cell_text(cell):
    """把 cellValue 的三种形态（text / number / time）转成字符串。"""
    cv = (cell or {}).get("cellValue") or {}
    if "text" in cv:
        return (cv.get("text") or "").strip()
    if "number" in cv:
        n = cv["number"]
        try:
            f = float(n)
            return str(int(f)) if f.is_integer() else str(f)
        except (TypeError, ValueError):
            return str(n)
    t = cv.get("time")
    if isinstance(t, dict):
        return "%d年%d月%d日" % (t.get("year", 0), t.get("month", 0), t.get("day", 0))
    return ""


def sheet_label(d):
    """26年10月 这种子表名（月不补零）。"""
    return "%d年%d月" % (d.year % 100, d.month)


def target_labels(today=None):
    today = today or datetime.date.today()
    y, m = today.year, today.month
    nxt_y, nxt_m = (y + 1, 1) if m == 12 else (y, m + 1)
    return [sheet_label(datetime.date(y, m, 1)), sheet_label(datetime.date(nxt_y, nxt_m, 1))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=".plansrc")
    ap.add_argument("--csv-dir", help="调试模式：直接用本地已导出的 CSV，不联网")
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    want = target_labels()
    log("目标子表：%s" % " / ".join(want))

    if args.csv_dir:
        for name in want:
            src = os.path.join(args.csv_dir, name + ".csv")
            if not os.path.exists(src):
                die("本地调试缺少 CSV: %s" % src)
            shutil.copyfile(src, os.path.join(args.out_dir, name + ".csv"))
            log("调试模式拷入 %s" % name)
        return 0

    file_id = os.environ.get("TDOC_FILE_ID", "").strip() or DEFAULT_FILE_ID
    headers = load_headers()

    meta = api_get(headers, urllib.parse.quote(file_id, safe=""))
    props = meta.get("properties") or []
    if not props:
        die("未取到子表列表: %s" % json.dumps(meta, ensure_ascii=False)[:300])
    by_title = {p.get("title"): p for p in props}
    log("子表共 %d 个" % len(props))

    for name in want:
        p = by_title.get(name)
        if not p:
            die("找不到子表「%s」，现有：%s" % (name, list(by_title)))
        sid = p["sheetId"]
        rows_n = int(p.get("rowTotal") or 225)
        rng = "A1:%s%d" % (COL_LETTER, rows_n)
        q = urllib.parse.urlencode({"sheetId": sid})
        obj = api_get(headers, "%s/values/%s?%s"
                      % (urllib.parse.quote(file_id, safe=""), urllib.parse.quote(rng, safe="!:"), q))
        rows = ((obj.get("gridData") or {}).get("rows")) or []
        if not rows:
            die("子表「%s」返回空 gridData" % name)

        path = os.path.join(args.out_dir, name + ".csv")
        with open(path, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f, lineterminator="\n")
            for r in rows:
                vals = [cell_text(c) for c in (r.get("values") or [])]
                vals += [""] * (NCOL - len(vals))
                w.writerow(vals[:NCOL])
        log("OK %s(%s) %d 行 -> %s" % (name, sid, len(rows), path))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as e:  # noqa: BLE001
        log("::error::未预期异常 %s: %s" % (type(e).__name__, e))
        sys.exit(1)
