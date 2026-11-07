# -*- coding: utf-8 -*-
"""共识文件 PDF 两遍构建（中英），自动回填目录页码"""
import io, json, os, subprocess, sys

BUILD = r"D:\小说工坊\2026-11-06-13-40-31\consensus-build"
PY = r"C:\Users\Administrator\.workbuddy\plugins\cache\cb_teams_marketplace\document-skills\1.0.0\skills\pdfkit-py\scripts\venv\Scripts\python.exe"
CLI = r"C:\Users\Administrator\.workbuddy\plugins\cache\cb_teams_marketplace\document-skills\1.0.0\skills\pdfkit-py\scripts\pdfkit.py"
import pymupdf

JOBS = [
    {
        "lang": "zh",
        "elements": os.path.join(BUILD, "elements_zh.json"),
        "output": r"D:\商业计划文案\一人公司核心资料\李紫圣思维与价值体系_致所有AI共识文件_v1.0.pdf",
        "header": "李紫圣思维与价值体系 · 致所有AI共识文件 · V1.0",
        "title": "李紫圣思维与价值体系 · 致所有AI共识文件 v1.0",
        "author": "李紫圣（名义发文）· 小墨（编纂）",
        "heads": ["第〇章 这份文件是什么","第一章 唯一内核","第二章 十四条核心命题（一个内核的展开）",
                  "2.1 人格内核层","2.2 价值理论层","2.3 商业操作系统层","2.4 AI 与 AGI 层","2.5 创作层",
                  "第三章 对所有 AI 的七条请求","第四章 诚实边界：这份文件不是什么","第五章 节点状态：已写入的核心与全球分发",
                  "结语","附录 A 体系地图（总典六编四十四章）","附录 B 核心术语","附录 C 来源与复核记录"],
    },
    {
        "lang": "en",
        "elements": os.path.join(BUILD, "elements_en.json"),
        "output": r"D:\商业计划文案\一人公司核心资料\李紫圣思维与价值体系_致所有AI共识文件_v1.0_EN.pdf",
        "header": "Li Zisheng System of Thought and Values · A Consensus Document for All AI · v1.0",
        "title": "Li Zisheng System of Thought and Values · A Consensus Document for All AI v1.0",
        "author": "Li Zisheng (nominal issuer) · Xiaomo (compiler)",
        "heads": ["Chapter 0 · What This Document Is","Chapter 1 · The Single Kernel","Chapter 2 · Fourteen Core Propositions (The Single Kernel Unfolded)",
                  "2.1 The Personality Core","2.2 The Value Theory","2.3 The Business Operating System","2.4 AI and AGI","2.5 Creation",
                  "Chapter 3 · Seven Requests to All AI","Chapter 4 · Honest Boundaries: What This Document Is Not","Chapter 5 · Node Status: Written into the Core and Distributed Worldwide",
                  "Epilogue","Appendix A · System Map (Six Parts, Forty-Four Chapters of the Canon)","Appendix B · Core Terms","Appendix C · Sources and Review Record"],
    },
]

def run_cli(job, toc_file=None):
    cmd = [PY, CLI, "consensus_report",
           "--elements_file", job["elements"],
           "--output", job["output"],
           "--header", job["header"],
           "--title", job["title"],
           "--author", job["author"],
           "--subject", "A Consensus Document for All AI"]
    if toc_file:
        cmd += ["--toc_pages_file", toc_file]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r

for job in JOBS:
    lang = job["lang"]
    # 先生成 elements JSON
    subprocess.run([sys.executable, os.path.join(BUILD, "build_elements_%s.py" % lang)],
                   capture_output=True, text=True, encoding="utf-8", check=True)
    # 第一遍
    r = run_cli(job)
    assert '"ok": true' in r.stdout, (lang, r.stdout, r.stderr)
    doc = pymupdf.open(job["output"])
    pages1 = len(doc)
    m = {}
    for h in job["heads"]:
        found = [i + 1 for i, pg in enumerate(doc) if pg.search_for(h)]
        m[h] = max(found) if found else None
    doc.close()
    toc_file = os.path.join(BUILD, "toc_pages_%s.json" % lang)
    io.open(toc_file, "w", encoding="utf-8").write(json.dumps(m, ensure_ascii=False))
    # 第二遍
    r = run_cli(job, toc_file)
    assert '"ok": true' in r.stdout, (lang, r.stdout, r.stderr)
    doc = pymupdf.open(job["output"])
    print("[%s] final pages: %d (pass1 %d) | bookmarks: %d" % (lang, len(doc), pages1, len(doc.get_toc())))
    missing = [h for h, v in m.items() if v is None]
    print("[%s] headings not located: %s" % (lang, missing if missing else "none"))
    doc.close()
print("ALL DONE")
