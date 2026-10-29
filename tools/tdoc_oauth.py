#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
腾讯文档开放平台 —— OAuth 令牌工具（授权码换取 / 刷新）。

背景：access_token 有效期 30 天；refresh_token 有效期 1 年，但**每刷新一次旧的
refresh_token 立即失效**，必须把新返回的 refresh_token 保存下来，否则下次没法再用。

用法
----
1) 用授权码换第一对令牌（code 5~10 分钟内有效，且只能用一次）：

   python3 tools/tdoc_oauth.py exchange \
       --client-id  <Client ID> \
       --client-secret <Client Secret> \
       --code <回调地址里的 code> \
       --redirect-uri <与应用里配置的完全一致的地址>

2) 之后每次刷新（读上一轮保存的 refresh_token，成功后自动覆盖保存新的一对）：

   python3 tools/tdoc_oauth.py refresh \
       --client-id <Client ID> --client-secret <Client Secret>

令牌默认存到 ./tdoc_token.json（含明文密钥，已在 .gitignore 中忽略，切勿提交）。
加 --show 才会把完整令牌打印到终端。
"""

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

TOKEN_URL = "https://docs.qq.com/oauth/v2/token"
DEFAULT_STORE = "tdoc_token.json"


def mask(s: str, keep: int = 6) -> str:
    if not s:
        return "(空)"
    if len(s) <= keep * 2:
        return s[:2] + "*" * (len(s) - 2)
    return f"{s[:keep]}…{s[-4:]}（共 {len(s)} 字符）"


def http_get_json(url: str):
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    op = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with op.open(req, timeout=45) as r:
            body = r.read().decode("utf-8", "replace")
            return r.status, body
    except urllib.error.HTTPError as e:  # noqa: F821  (urllib.error 由 urllib.request 带入作用域)
        return e.code, e.read().decode("utf-8", "replace")
    except Exception as e:  # 网络层
        return 0, f"__ERR__ {type(e).__name__}: {e}"


def call_token(params: dict):
    url = TOKEN_URL + "?" + urllib.parse.urlencode(params)
    status, body = http_get_json(url)

    if body.startswith("__ERR__"):
        print("FAIL 网络请求失败：" + body[7:].strip())
        return None

    if status != 200:
        hint = ""
        if status == 401:
            hint = "（code 已过期或已被使用过，重新打开授权链接再扫一次即可）"
        print(f"FAIL HTTP {status}{hint}")
        print("     " + body[:300].replace("\n", " "))
        return None

    try:
        data = json.loads(body)
    except Exception:
        print("FAIL 回包不是合法 JSON：" + body[:200])
        return None

    if not data.get("access_token"):
        print("FAIL 回包缺少 access_token：" + body[:300])
        return None

    return data


def load_store(path: str) -> dict:
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_store(path: str, data: dict):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)
    try:
        os.chmod(path, 0o600)
    except Exception:
        pass


def report(tag: str, data: dict, store_path: str, show: bool):
    at = data.get("access_token", "")
    rt = data.get("refresh_token", "")
    exp_in = int(data.get("expires_in") or 0)
    uid = data.get("user_id", "")

    now = int(time.time())
    record = {
        "client_id": data.get("client_id", ""),
        "access_token": at,
        "refresh_token": rt,
        "expires_in": exp_in,
        "expires_at": now + exp_in if exp_in else 0,
        "expires_at_text": time.strftime("%Y-%m-%d %H:%M", time.localtime(now + exp_in)) if exp_in else "",
        "refresh_expires_at_text": time.strftime("%Y-%m-%d", time.localtime(now + 365 * 86400)),
        "open_id": uid,
        "scope": data.get("scope", ""),
        "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    save_store(store_path, record)

    print(f"OK {tag}")
    print(f"     access_token  {mask(at)}")
    print(f"     refresh_token {mask(rt)}")
    if exp_in:
        print(f"     有效期        {exp_in // 86400} 天，到期 {record['expires_at_text']}")
    if uid:
        print(f"     Open-Id       {uid}")
    print(f"     已保存到      {store_path}")

    if show:
        print("\n--- 完整令牌（不要发到公开场合）---")
        print("access_token  =", at)
        print("refresh_token =", rt)
        print("open_id       =", uid)

    if not rt:
        print("\nWARN 回包里没有 refresh_token；说明该应用未开通「长期访问」，需在开放平台重新授权。")

    print("\n下一步：把 access_token / refresh_token 分别填进仓库 Secrets："
          "\n      TDOC_ACCESS_TOKEN / TDOC_REFRESH_TOKEN（另需 TDOC_CLIENT_ID、TDOC_CLIENT_SECRET 若要自动续期）")


def cmd_exchange(a):
    if a.store:
        old = load_store(a.store)
        if old.get("refresh_token") and not a.force:
            print(f"提示：{a.store} 已有令牌（更新于 {old.get('updated_at','?')}）。")
            print("      覆盖会使旧的 refresh_token 失效。确认要重新授权请加 --force。")
            return 2

    data = call_token({
        "client_id": a.client_id,
        "client_secret": a.client_secret,
        "redirect_uri": a.redirect_uri,
        "grant_type": "authorization_code",
        "code": a.code.strip(),
    })
    if not data:
        return 1
    data.setdefault("client_id", a.client_id)
    report("授权码换取成功", data, a.store, a.show)
    return 0


def cmd_refresh(a):
    old = load_store(a.store)
    rt = a.refresh_token or old.get("refresh_token", "")
    if not rt:
        print(f"FAIL 没有可用的 refresh_token（{a.store} 不存在或为空，且未通过 --refresh-token 指定）")
        return 1

    data = call_token({
        "client_id": a.client_id,
        "client_secret": a.client_secret,
        "grant_type": "refresh_token",
        "refresh_token": rt,
    })
    if not data:
        print("     refresh_token 可能已过期（有效期 1 年）或被上一次刷新作废，需要重新走授权链接。")
        return 1

    # 关键：刷新会轮换 refresh_token，旧值立刻失效，必须落盘新的。
    data.setdefault("client_id", a.client_id)
    if not data.get("refresh_token"):
        data["refresh_token"] = rt  # 少数情况下不返回，沿用旧值
    report("刷新成功", data, a.store, a.show)
    return 0


def main():
    p = argparse.ArgumentParser(description="腾讯文档 OAuth 令牌工具")
    sub = p.add_subparsers(dest="cmd", required=True)

    e = sub.add_parser("exchange", help="用授权码换取 access_token / refresh_token")
    e.add_argument("--client-id", required=True)
    e.add_argument("--client-secret", required=True)
    e.add_argument("--code", required=True)
    e.add_argument("--redirect-uri", required=True)
    e.add_argument("--store", default=DEFAULT_STORE)
    e.add_argument("--force", action="store_true", help="已有令牌时仍强制覆盖")
    e.add_argument("--show", action="store_true", help="打印完整令牌")
    e.set_defaults(func=cmd_exchange)

    r = sub.add_parser("refresh", help="用 refresh_token 换新的一对令牌")
    r.add_argument("--client-id", required=True)
    r.add_argument("--client-secret", required=True)
    r.add_argument("--refresh-token", default="", help="不填则读 --store 里保存的")
    r.add_argument("--store", default=DEFAULT_STORE)
    r.add_argument("--show", action="store_true")
    r.set_defaults(func=cmd_refresh)

    a = p.parse_args()
    sys.exit(a.func(a))


if __name__ == "__main__":
    main()
