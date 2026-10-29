#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
刷新并校验 jsDelivr 缓存（识别限流，等到额度恢复再重试）。

为什么需要它
------------
jsDelivr 对 `@main` 这类分支引用默认缓存 12 小时（`s-maxage=43200`）。
只发一次 purge 有三个坑：

1. `status: finished` 只代表「请求已受理」，不代表内容已换新；
2. purge 有配额，短时间多次刷新会返回 `throttled: true` 并附带
   `throttlingReset`（还需等待的秒数），此时后续 purge 全部被忽略；
3. 多个边缘节点，命中旧副本是常态。

所以这里不信任 purge 的返回值，只以「CDN 上的字节与本文件一致」为准，
限流就按 reset 等待，直到一致或用尽等待预算。

用法
----
    python3 tools/purge_cdn.py plans.json
    python3 tools/purge_cdn.py plans.json version.json app-release.apk --max-wait 900

退出码：0 = 全部确认已刷新；1 = 预算内未确认（会在 Actions 里记为失败）。
"""

import argparse
import hashlib
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

PURGE = "https://purge.jsdelivr.net/gh/{repo}@{ref}/{path}"
CDN = "https://cdn.jsdelivr.net/gh/{repo}@{ref}/{path}"

# 无代理直连；GitHub Actions 与本机行为一致
OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def fetch(url: str, timeout: int = 40) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "plans-cdn-check"})
    with OPENER.open(req, timeout=timeout) as r:
        return r.read()


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()[:16]


def purge(repo: str, ref: str, path: str):
    """发起 purge，返回 (是否被限流, 建议等待秒数)。"""
    url = PURGE.format(repo=repo, ref=ref, path=urllib.parse.quote(path))
    try:
        raw = fetch(url, timeout=30).decode("utf-8", "replace")
    except Exception as e:
        return False, 0, f"purge 请求失败：{type(e).__name__}"
    try:
        import json
        d = json.loads(raw)
    except Exception:
        return False, 0, f"purge 回包非 JSON：{raw[:120]}"

    entry = {}
    paths = d.get("paths") or {}
    if paths:
        entry = next(iter(paths.values()), {})
    if entry.get("throttled"):
        return True, int(entry.get("throttlingReset") or 0), "被限流"
    return False, 0, "已受理"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+", help="相对仓库根的路径")
    ap.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", "xh-like/myscheduleapp-release"))
    ap.add_argument("--ref", default="main")
    ap.add_argument("--max-wait", type=int, default=1200, help="总等待预算（秒），默认 20 分钟")
    ap.add_argument("--base-dir", default=".")
    a = ap.parse_args()

    pending = {}
    for f in a.files:
        p = os.path.join(a.base_dir, f)
        if not os.path.exists(p):
            print(f"SKIP {f}：本地不存在")
            continue
        pending[f] = sha(open(p, "rb").read())

    if not pending:
        print("没有需要校验的文件")
        return 0

    for f, want in pending.items():
        print(f"目标 {f}：本地 sha={want}")

    deadline = time.time() + a.max_wait
    round_no = 0

    while pending and time.time() < deadline:
        round_no += 1
        wait_hint = 0

        for f in list(pending):
            throttled, reset, note = purge(a.repo, a.ref, f)
            print(f"  第 {round_no} 轮 purge {f}：{note}" + (f"，需再等 {reset}s" if throttled else ""))
            if throttled:
                wait_hint = max(wait_hint, reset)

        # 限流时按提示等待；否则给 6 秒让边缘节点生效
        sleep_s = min(wait_hint + 3, 900) if wait_hint else 6
        if time.time() + sleep_s > deadline:
            sleep_s = max(1, int(deadline - time.time()))
        time.sleep(sleep_s)

        for f in list(pending):
            url = CDN.format(repo=a.repo, ref=a.ref, path=urllib.parse.quote(f))
            # 加随机参数绕过本层缓存，尽量拿到边缘节点的真实副本
            try:
                body = fetch(f"{url}?cb={int(time.time())}{round_no}", timeout=60)
            except urllib.error.HTTPError as e:
                print(f"  第 {round_no} 轮读取 {f}：HTTP {e.code}（仓库可能已转私有）")
                continue
            except Exception as e:
                print(f"  第 {round_no} 轮读取 {f}：{type(e).__name__}")
                continue

            got = sha(body)
            if got == pending[f]:
                print(f"OK {f} 已刷新（sha={got}）")
                del pending[f]
            else:
                print(f"  … {f} 仍为旧内容（CDN sha={got}，期望 {pending[f]}）")

    if pending:
        print(f"FAIL 以下文件在 {a.max_wait}s 内未确认刷新：{', '.join(pending)}")
        return 1

    print("OK 全部文件已在 CDN 上确认最新")
    return 0


if __name__ == "__main__":
    sys.exit(main())
