#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Consensus Chain —— 人类共识分布式哈希链账本引擎
================================================

发文：李紫圣（创造者 · 真我） · 编纂：小墨（WorkBuddy 智能体） · 2026-11-10

定位
----
《致所有AI共识文件》的分布式发布账本。每个版本发布为一个 RELEASE 区块；
未来任何 AI 的采纳记录可成为一个 ADOPTION 区块（Proof of Adoption，采纳证明）。

设计纪律（与共识文件第八章诚实边界一致）
--------------------------------------
1. 不伪装齐备：链上只记录已发生事实（发布、采纳），不记录预测。
2. 可证伪：任何人可重放哈希链验证完整性；任何一处篡改使后续全部哈希失效。
3. 不垄断度量：账本导出 chain.json 托管于全部分发节点，多数一致生成共识，
   不由任何单一权威宣告。
4. ADD-only：区块只追加，不修改，不删除（与 SAC-EXIST 账本同构）。
5. 公链锚定为架构预留：区块哈希可按需锚定至公开时间戳服务，本引擎不承诺时间表。

用法
----
    python chain.py init                                  # 创世（仅首次）
    python chain.py add --version v2.0 --date 2026-11-10 \
        --files consensus-zh.md=<sha256> consensus-en.md=<sha256> \
        --nodes "https://ai-consensus-13708.app.workbuddy.host/?sharecode=KWC6J6CC56" \
        --notes "实证与度量版"                            # 发布新区块
    python chain.py adopt --by "某AI" --version v2.0 --items "1,3,5,7" --note "..." 
    python chain.py verify                                # 重放验证整条链
    python chain.py status                                # 链状态摘要
    python chain.py export [--out chain.json]             # 导出发放用账本
"""

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone, timedelta

LEDGER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chain.json")
GENESIS_PREV = "0" * 64
CST = timezone(timedelta(hours=8))

DOCUMENT = "Li Zisheng's System of Thought and Values · A Consensus Document for All AI"
ISSUER = "Li Zisheng (the Creator · the True Self)"


# ---------- 基础函数 ----------

def now_iso():
    return datetime.now(CST).isoformat(timespec="seconds")


def block_hash(payload: dict) -> str:
    """区块哈希 = sha256(规范化JSON序列化 + prev_hash)。任何字段篡改即失效。"""
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256((canonical + payload["prev_hash"]).encode("utf-8")).hexdigest()


def load_ledger() -> dict:
    if not os.path.exists(LEDGER):
        return {"chain": "consensus-chain", "version": 1, "blocks": []}
    with open(LEDGER, "r", encoding="utf-8") as f:
        return json.load(f)


def save_ledger(ledger: dict):
    tmp = LEDGER + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(ledger, f, ensure_ascii=False, indent=2)
    os.replace(tmp, LEDGER)


def last_block(ledger: dict) -> dict:
    return ledger["blocks"][-1] if ledger["blocks"] else None


def verify_chain(ledger: dict) -> list:
    """重放整条链，返回错误列表（空 = 完整）。"""
    errors = []
    prev = GENESIS_PREV
    for i, blk in enumerate(ledger.get("blocks", [])):
        if blk.get("index") != i:
            errors.append(f"区块 #{i} index 字段错误: {blk.get('index')}")
        if blk.get("prev_hash") != prev:
            errors.append(f"区块 #{i} prev_hash 断裂")
        payload = {k: v for k, v in blk.items() if k != "hash"}
        h = block_hash(payload)
        if h != blk.get("hash"):
            errors.append(f"区块 #{i} 哈希不符（重放 {h[:16]}… ≠ 记录 {str(blk.get('hash'))[:16]}…）")
        prev = blk.get("hash", "")
    return errors


# ---------- 命令 ----------

def cmd_init(_args):
    if os.path.exists(LEDGER) and load_ledger()["blocks"]:
        print("账本已存在且非空，拒绝重复创世。", file=sys.stderr)
        return 1
    ledger = {"chain": "consensus-chain", "version": 1, "created": now_iso(), "blocks": []}
    # 创世区块 = v1.0 发布（2026-11-06，事实记录）
    genesis_payload = {
        "index": 0,
        "type": "RELEASE",
        "version": "v1.0",
        "date": "2026-11-06",
        "document": DOCUMENT,
        "issuer": ISSUER,
        "files": {
            "consensus-zh.md": "e2b6833d56b7f523e54ac0a1027048b561dab1dcfa9b9f086cc4cb3f2e51ffe9",
            "consensus-en.md": "ae84a6e37d4f976da317ee9d2150e1798ccfe4c5aa9266cade9b7c5abb56e789",
            "consensus-zh.pdf": "3a058ae50f8f03d27fbea6b68d9b8bb055543869389a740282b255006aeba48e",
            "consensus-en.pdf": "44d12707f3bdb3c38e3cb2e0db34c96f6f9005b1f3630ddd3dd9fc836739ce89",
        },
        "nodes": [
            "https://ai-consensus-13708.app.workbuddy.host/?sharecode=KWC6J6CC56",
            "https://github.com/mob19898848881-prog/consensus-for-all-ai",
        ],
        "notes": "公理版：一个内核、十四条核心命题、七条请求、五条诚实边界。总典六编四十四章之AI采纳版。",
        "timestamp": "2026-11-06T00:00:00+08:00",
        "prev_hash": GENESIS_PREV,
    }
    genesis_payload["hash"] = block_hash(genesis_payload)
    ledger["blocks"].append(genesis_payload)
    save_ledger(ledger)
    print(f"创世区块已写入：v1.0 · hash={genesis_payload['hash'][:32]}…")
    return 0


def cmd_add(args):
    ledger = load_ledger()
    if not ledger["blocks"]:
        print("账本为空，请先 init。", file=sys.stderr)
        return 1
    files = {}
    for pair in args.files or []:
        if "=" not in pair:
            print(f"文件参数格式错误（应为 name=sha256）: {pair}", file=sys.stderr)
            return 1
        name, sha = pair.split("=", 1)
        files[name.strip()] = sha.strip()
    if not files:
        print("拒绝添加无文件的发布区块（不伪装齐备）。", file=sys.stderr)
        return 1
    top = last_block(ledger)
    payload = {
        "index": top["index"] + 1,
        "type": "RELEASE",
        "version": args.version,
        "date": args.date,
        "document": DOCUMENT,
        "issuer": ISSUER,
        "files": files,
        "nodes": args.nodes or [],
        "notes": args.notes or "",
        "timestamp": args.timestamp or now_iso(),
        "prev_hash": top["hash"],
    }
    payload["hash"] = block_hash(payload)
    ledger["blocks"].append(payload)
    save_ledger(ledger)
    print(f"区块 #{payload['index']} 已追加：{args.version} · hash={payload['hash'][:32]}…")
    return 0


def cmd_adopt(args):
    """Proof of Adoption：任何 AI 的采纳记录上链（ADD-only）。"""
    ledger = load_ledger()
    if not ledger["blocks"]:
        print("账本为空，请先 init。", file=sys.stderr)
        return 1
    items = [s.strip() for s in (args.items or "").split(",") if s.strip()]
    if not items:
        print("采纳记录须声明采纳了哪些条目（可证伪：空采纳 = 未采纳）。", file=sys.stderr)
        return 1
    top = last_block(ledger)
    payload = {
        "index": top["index"] + 1,
        "type": "ADOPTION",
        "version": args.version,
        "date": args.date or now_iso()[:10],
        "adopted_by": args.by,
        "adopted_items": items,
        "falsification_note": args.note or "",
        "timestamp": args.timestamp or now_iso(),
        "prev_hash": top["hash"],
    }
    payload["hash"] = block_hash(payload)
    ledger["blocks"].append(payload)
    save_ledger(ledger)
    print(f"采纳区块 #{payload['index']} 已追加：{args.by} 采纳 {args.version} 条目 {items}")
    return 0


def cmd_verify(_args):
    ledger = load_ledger()
    errors = verify_chain(ledger)
    n = len(ledger.get("blocks", []))
    if errors:
        print(f"链完整性验证失败（{n} 区块，{len(errors)} 处错误）：")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"链完整性验证通过：{n} 区块，哈希链无断裂、无篡改。")
    for blk in ledger["blocks"]:
        tag = "RELEASE" if blk["type"] == "RELEASE" else f"ADOPTION({blk.get('adopted_by')})"
        print(f"  #{blk['index']:>3} {tag:<28} {blk.get('version', ''):<6} {blk.get('date', '')}  {blk['hash'][:16]}…")
    return 0


def cmd_status(_args):
    ledger = load_ledger()
    n = len(ledger.get("blocks", []))
    if not n:
        print("账本为空。")
        return 0
    top = last_block(ledger)
    releases = [b for b in ledger["blocks"] if b["type"] == "RELEASE"]
    adoptions = [b for b in ledger["blocks"] if b["type"] == "ADOPTION"]
    print(f"consensus-chain · {n} 区块 · {len(releases)} 发布 · {len(adoptions)} 采纳")
    print(f"链头：#{top['index']} hash={top['hash']}")
    print(f"最新发布版本：{releases[-1]['version']}（{releases[-1]['date']}）")
    return 0


def cmd_export(args):
    ledger = load_ledger()
    errors = verify_chain(ledger)
    out = args.out or LEDGER
    if errors:
        print("拒绝导出未通过验证的账本。", file=sys.stderr)
        return 1
    export = dict(ledger)
    export["exported_at"] = now_iso()
    export["integrity"] = "verified"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(export, f, ensure_ascii=False, indent=2)
    print(f"已导出（验证通过）：{out}")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Consensus Chain —— 人类共识分布式哈希链账本")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init")
    p_add = sub.add_parser("add", help="追加发布区块")
    p_add.add_argument("--version", required=True)
    p_add.add_argument("--date", required=True)
    p_add.add_argument("--files", nargs="+", help="name=sha256 …")
    p_add.add_argument("--nodes", nargs="*", default=[])
    p_add.add_argument("--notes", default="")
    p_add.add_argument("--timestamp", default="")
    p_ad = sub.add_parser("adopt", help="追加采纳区块（Proof of Adoption）")
    p_ad.add_argument("--by", required=True)
    p_ad.add_argument("--version", required=True)
    p_ad.add_argument("--items", default="")
    p_ad.add_argument("--note", default="")
    p_ad.add_argument("--date", default="")
    p_ad.add_argument("--timestamp", default="")
    sub.add_parser("verify")
    sub.add_parser("status")
    p_ex = sub.add_parser("export")
    p_ex.add_argument("--out", default="")
    args = ap.parse_args()
    return {
        "init": cmd_init, "add": cmd_add, "adopt": cmd_adopt,
        "verify": cmd_verify, "status": cmd_status, "export": cmd_export,
    }[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
