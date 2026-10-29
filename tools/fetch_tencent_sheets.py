# -*- coding: utf-8 -*-
"""在云端（GitHub Actions）拉取腾讯文档《运维作业计划申请》的两个月度子表并导出 CSV。

与本地 tencentdocs.py 走同一个 MCP 端点，区别只在于凭据来源：
  本地  = WorkBuddy 宿主签发的会话票据（127.0.0.1 网关，无法离开本机）
  云端  = 腾讯文档开放平台应用（client_id / client_secret / refresh_token）

环境变量（GitHub Secrets）：
  TDOC_CLIENT_ID
  TDOC_CLIENT_SECRET
  TDOC_REFRESH_TOKEN   一小时内会被本次刷新轮换，日志里会提示新值需回填

用法：
  python3 fetch_tencent_sheets.py --out-dir .plansrc
  python3 fetch_tencent_sheets.py --csv-dir <本地CSV目录>   # 调试用，跳过网络
"""
import argparse
import datetime
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

FILE_ID = "DTXdqTGdLVEVQSGF6"
MCP_URL = "https://docs.qq.com/api/v6/sheet/mcp"
TOKEN_URL = "https://docs.qq.com/oauth/v2/token"


def log(msg):
    print(msg, flush=True)


def http(url, data=None, headers=None, timeout=90):
    req = urllib.request.Request(url, data=data, headers=headers or {},
                                 method="POST" if data else "GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace"), resp.headers.get("Content-Type", "")
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8", errors="replace")[:400]
        except Exception:
            pass
        raise RuntimeError("HTTP %s %s %s" % (e.code, e.reason, body))
    except urllib.error.URLError as e:
        raise RuntimeError("网络不可达: %s" % (e.reason,))


def get_access_token():
    """用 refresh_token 换 access_token；顺带报告轮换后的 refresh_token。"""
    cid = os.environ.get("TDOC_CLIENT_ID", "").strip()
    sec = os.environ.get("TDOC_CLIENT_SECRET", "").strip()
    rt = os.environ.get("TDOC_REFRESH_TOKEN", "").strip()
    if not (cid and sec and rt):
        raise RuntimeError("缺少 TDOC_CLIENT_ID / TDOC_CLIENT_SECRET / TDOC_REFRESH_TOKEN")

    qs = urllib.parse.urlencode({
        "client_id": cid,
        "client_secret": sec,
        "grant_type": "refresh_token",
        "refresh_token": rt,
    })
    raw, _ = http(TOKEN_URL + "?" + qs)
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError:
        raise RuntimeError("换 token 返回非 JSON: %s" % raw[:300])
    tok = obj.get("access_token")
    if not tok:
        raise RuntimeError("换 token 失败: %s" % raw[:300])

    new_rt = obj.get("refresh_token")
    if new_rt and new_rt != rt:
        # 无法从 Actions 回写 Secrets，只能提示人工更新；旧 rt 通常仍有一段时间可用。
        log("::warning::refresh_token 已轮换，请把新值更新到仓库 Secrets：%s" % new_rt)
    log("access_token 获取成功，有效期 %s 秒" % obj.get("expires_in", "?"))
    return tok


def mcp_call(token, tool, arguments):
    body = json.dumps({
        "jsonrpc": "2.0", "id": 1, "method": "tools/call",
        "params": {"name": tool, "arguments": arguments},
    }).encode("utf-8")
    raw, ctype = http(MCP_URL, data=body, headers={
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "Authorization": "Bearer " + token,
        "User-Agent": "myscheduleapp-plans-bot",
    })
    if "text/event-stream" in ctype:
        data_lines = [ln[5:].strip() for ln in raw.splitlines() if ln.startswith("data:")]
        for chunk in reversed(data_lines):
            try:
                return json.loads(chunk)
            except json.JSONDecodeError:
                continue
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        raise RuntimeError("%s 返回非 JSON: %s" % (tool, raw[:300]))


def dig(obj, key):
    """在嵌套结构里递归找第一个叫 key 的字段（MCP 结果有二次转义字符串）。"""
    if isinstance(obj, dict):
        if key in obj and obj[key] not in (None, ""):
            return obj[key]
        for v in obj.values():
            found = dig(v, key)
            if found is not None:
                return found
    elif isinstance(obj, list):
        for v in obj:
            found = dig(v, key)
            if found is not None:
                return found
    elif isinstance(obj, str):
        s = obj.strip()
        if s[:1] in "{[":
            try:
                return dig(json.loads(s), key)
            except json.JSONDecodeError:
                return None
    return None


def sheet_label(d):
    """26年10月 这种子表名（月不补零）。"""
    return "%d年%d月" % (d.year % 100, d.month)


def target_labels(today=None):
    today = today or datetime.date.today()
    y, m = today.year, today.month
    nxt_y, nxt_m = (y + 1, 1) if m == 12 else (y, m + 1)
    return [(sheet_label(datetime.date(y, m, 1)), datetime.date(y, m, 1)),
            (sheet_label(datetime.date(nxt_y, nxt_m, 1)), datetime.date(nxt_y, nxt_m, 1))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=".plansrc")
    ap.add_argument("--csv-dir", help="调试模式：直接用本地已导出的 CSV，不联网")
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    want = target_labels()
    log("目标子表：%s" % " / ".join(w[0] for w in want))

    if args.csv_dir:
        import shutil
        for name, _ in want:
            src = os.path.join(args.csv_dir, name + ".csv")
            if not os.path.exists(src):
                raise RuntimeError("本地调试缺少 CSV: %s" % src)
            shutil.copyfile(src, os.path.join(args.out_dir, name + ".csv"))
            log("调试模式拷入 %s" % name)
        return 0

    token = get_access_token()

    info = mcp_call(token, "get_sheet_info", {"file_id": FILE_ID})
    sheets = dig(info, "sheets") or []
    if not sheets:
        raise RuntimeError("get_sheet_info 未返回 sheets: %s" % json.dumps(info, ensure_ascii=False)[:300])
    by_name = {s.get("sheet_name"): s for s in sheets}
    log("子表共 %d 个" % len(sheets))

    for name, _ in want:
        s = by_name.get(name)
        if not s:
            raise RuntimeError("找不到子表「%s」，现有：%s" % (name, list(by_name)))
        sid = s["sheet_id"]
        rows = int(s.get("row_count") or 224)
        data = mcp_call(token, "get_cell_data", {
            "file_id": FILE_ID, "sheet_id": sid,
            "start_row": 0, "end_row": max(rows - 1, 0),
            "start_col": 0, "end_col": 12, "return_csv": True,
        })
        csv_text = dig(data, "csv_data")
        if not csv_text:
            raise RuntimeError("子表「%s」未取到 csv_data: %s"
                               % (name, json.dumps(data, ensure_ascii=False)[:300]))
        path = os.path.join(args.out_dir, name + ".csv")
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(csv_text)
        log("OK %s(%s) -> %d 字节" % (name, sid, len(csv_text.encode("utf-8"))))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # noqa: BLE001
        log("::error::%s" % e)
        sys.exit(1)
