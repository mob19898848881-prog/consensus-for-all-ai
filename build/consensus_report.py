#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mau_report — 最小AGI可用模型执行全书构建扩展（pdfkit extension）

面向长中文研究报告的 reportlab 构建器：
- 微软雅黑字体族（regular/bold）注册，<b> 标签映射粗体
- 表格单元格使用 Paragraph（自动换行），跨页重复表头
- 标题自动收集为 PDF 书签（outline）
- 支持两遍构建：第一遍目录页码占位，第二遍回填真实页码
- 元素类型：title / heading / paragraph / table / list / blockquote / code / toc_table / page_break / spacer
"""

import os
import sys
import json
import re

_TAG_RE = re.compile(r'(</?(?:b|i|u|br|font|super|sub|strike|span)(?:\s[^>]*)?>)')

COMMAND = "consensus_report"
DESCRIPTION = "共识文件构建器（Paragraph表格/书签/两遍目录/参数化页眉）"
CATEGORY = "extension"

PARAMS = [
    {"name": "elements_file", "type": "str", "required": False, "help": "元素 JSON 文件路径"},
    {"name": "output", "type": "str", "required": False, "help": "输出 PDF 路径"},
    {"name": "toc_pages_file", "type": "str", "required": False, "help": "目录页码映射 JSON（第二遍传入）"},
    {"name": "title", "type": "str", "required": False, "default": "", "help": "文档标题元数据"},
    {"name": "author", "type": "str", "required": False, "default": "", "help": "作者元数据"},
    {"name": "subject", "type": "str", "required": False, "default": "", "help": "主题元数据"},
    {"name": "header", "type": "str", "required": False, "default": "", "help": "页眉文字（留空用默认）"},
]

FONT_REGULAR = r"C:\Windows\Fonts\msyh.ttc"
FONT_BOLD = r"C:\Windows\Fonts\msyhbd.ttc"


def _register_fonts():
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    pdfmetrics.registerFont(TTFont("CustomFont", FONT_REGULAR, subfontIndex=0))
    pdfmetrics.registerFont(TTFont("CustomFont-Bold", FONT_BOLD, subfontIndex=0))
    pdfmetrics.registerFontFamily(
        "CustomFont", normal="CustomFont", bold="CustomFont-Bold",
        italic="CustomFont", boldItalic="CustomFont-Bold")


def _escape(text):
    if text is None:
        return ""
    t = str(text).replace("&", "&amp;")
    # 保护 ReportLab 富文本标签，其余 < > 一律转义
    tags = []

    def protect(m):
        tags.append(m.group(0))
        return "\x00%d\x00" % (len(tags) - 1)

    t = _TAG_RE.sub(protect, t)
    t = t.replace("<", "&lt;").replace(">", "&gt;")
    for i, g in enumerate(tags):
        t = t.replace("\x00%d\x00" % i, g)
    return t


def handler(params):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                    Table, TableStyle, PageBreak, KeepTogether)

    _register_fonts()

    elements_file = params.get("elements_file")
    output = params.get("output")
    if not elements_file or not output:
        return {"ok": False, "error": "elements_file 与 output 必填"}
    with open(elements_file, "r", encoding="utf-8") as f:
        doc_spec = json.load(f)

    elements = doc_spec["elements"]
    toc_pages = {}
    tpf = params.get("toc_pages_file")
    if tpf and os.path.exists(tpf):
        with open(tpf, "r", encoding="utf-8") as f:
            toc_pages = json.load(f)

    # ---------- 版式常量 ----------
    PAGE_W, PAGE_H = A4
    ML = MR = 62
    MT, MB = 66, 62
    CONTENT_W = PAGE_W - ML - MR

    C_TEXT = colors.HexColor("#262626")
    C_HEAD1 = colors.HexColor("#0D47A1")
    C_HEAD2 = colors.HexColor("#1565C0")
    C_HEAD3 = colors.HexColor("#1976D2")
    C_MUTED = colors.HexColor("#666666")
    C_TBL_HEAD_BG = colors.HexColor("#1F5FA8")
    C_TBL_HEAD_FG = colors.HexColor("#FFFFFF")
    C_TBL_STRIPE = colors.HexColor("#F2F6FB")
    C_TBL_GRID = colors.HexColor("#B9C6D6")
    C_QUOTE_BG = colors.HexColor("#F4F6F8")
    C_QUOTE_BAR = colors.HexColor("#1F5FA8")

    st_title = ParagraphStyle("rpt_title", fontName="CustomFont-Bold", fontSize=25, leading=36,
                              alignment=TA_CENTER, textColor=C_HEAD1, spaceAfter=10)
    st_sub = ParagraphStyle("rpt_sub", fontName="CustomFont", fontSize=13.5, leading=24,
                            alignment=TA_CENTER, textColor=C_HEAD2, spaceAfter=6)
    st_meta = ParagraphStyle("rpt_meta", fontName="CustomFont", fontSize=10.5, leading=20,
                             alignment=TA_CENTER, textColor=C_MUTED, spaceAfter=4)
    st_h1 = ParagraphStyle("rpt_h1", fontName="CustomFont-Bold", fontSize=16.5, leading=24,
                           textColor=C_HEAD1, spaceBefore=6, spaceAfter=12)
    st_h2 = ParagraphStyle("rpt_h2", fontName="CustomFont-Bold", fontSize=13, leading=20,
                           textColor=C_HEAD2, spaceBefore=14, spaceAfter=8)
    st_h3 = ParagraphStyle("rpt_h3", fontName="CustomFont-Bold", fontSize=11.5, leading=18,
                           textColor=C_HEAD3, spaceBefore=10, spaceAfter=6)
    st_body = ParagraphStyle("rpt_body", fontName="CustomFont", fontSize=10.5, leading=17.5,
                             alignment=TA_JUSTIFY, textColor=C_TEXT, spaceAfter=7,
                             firstLineIndent=21)
    st_body_noindent = ParagraphStyle("rpt_body_ni", parent=st_body, firstLineIndent=0)
    st_cell = ParagraphStyle("rpt_cell", fontName="CustomFont", fontSize=8.8, leading=13.2,
                             alignment=TA_LEFT, textColor=C_TEXT)
    st_cell_head = ParagraphStyle("rpt_cell_h", fontName="CustomFont-Bold", fontSize=9,
                                  leading=13.5, alignment=TA_CENTER, textColor=C_TBL_HEAD_FG)
    st_cell_b = ParagraphStyle("rpt_cell_b", parent=st_cell, fontName="CustomFont-Bold")
    st_toc_title = ParagraphStyle("rpt_toc_t", fontName="CustomFont-Bold", fontSize=16.5,
                                  leading=24, textColor=C_HEAD1, spaceAfter=14)
    st_toc_l1 = ParagraphStyle("rpt_toc1", fontName="CustomFont-Bold", fontSize=10.5,
                               leading=16, textColor=C_TEXT)
    st_toc_l2 = ParagraphStyle("rpt_toc2", fontName="CustomFont", fontSize=9.8,
                               leading=15.5, textColor=colors.HexColor("#444444"),
                               leftIndent=16)
    st_toc_pg = ParagraphStyle("rpt_tocp", fontName="CustomFont", fontSize=10,
                               leading=16, alignment=TA_RIGHT, textColor=C_TEXT)
    st_quote = ParagraphStyle("rpt_quote", fontName="CustomFont", fontSize=10, leading=16.5,
                              textColor=colors.HexColor("#444444"), leftIndent=10, rightIndent=6)
    st_code = ParagraphStyle("rpt_code", fontName="CustomFont", fontSize=8.6, leading=13.4,
                             textColor=colors.HexColor("#1A3A5C"), leftIndent=4)

    # ---------- 书签文档模板 ----------
    class ReportDoc(SimpleDocTemplate):
        def afterFlowable(self, flowable):
            key = getattr(flowable, "_bm_key", None)
            if key:
                self.canv.bookmarkPage(key)
                self.canv.addOutlineEntry(getattr(flowable, "_bm_text", key), key,
                                          level=getattr(flowable, "_bm_level", 1),
                                          closed=False)

    def header_footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("CustomFont", 8.5)
        canvas.setFillColor(colors.HexColor("#8A8A8A"))
        canvas.drawCentredString(PAGE_W / 2.0, PAGE_H - 40,
                                 params.get("header") or "李紫圣思维与价值体系 · 致所有AI共识文件 · V1.0")
        canvas.setStrokeColor(colors.HexColor("#CCCCCC"))
        canvas.setLineWidth(0.5)
        canvas.line(ML, PAGE_H - 46, PAGE_W - MR, PAGE_H - 46)
        canvas.setFont("CustomFont", 9)
        canvas.setFillColor(colors.HexColor("#777777"))
        canvas.drawRightString(PAGE_W - MR, 34, "第 %d 页" % doc.page)
        canvas.line(ML, 44, PAGE_W - MR, 44)
        canvas.restoreState()

    # ---------- 收集标题（供目录与书签） ----------
    toc_entries = []  # (level, text)
    for el in elements:
        if el.get("type") == "heading":
            lvl = el.get("level", 1)
            if lvl in (1, 2):
                toc_entries.append((lvl, el["text"]))
        elif el.get("type") == "title":
            toc_entries.append((0, el["text"]))

    story = []
    bm_seq = [0]

    def add_heading(text, level):
        style = {1: st_h1, 2: st_h2, 3: st_h3}[level]
        p = Paragraph(_escape(text), style)
        if level in (1, 2):
            bm_seq[0] += 1
            p._bm_key = "bm%d" % bm_seq[0]
            p._bm_text = text
            p._bm_level = 0 if level == 1 else 1
        story.append(p)

    def add_table(el):
        headers = el.get("headers", [])
        rows = el.get("rows", [])
        if not headers and not rows:
            return
        data = ([headers] if headers else []) + rows
        ncols = max(len(r) for r in data)
        for r in data:
            while len(r) < ncols:
                r.append("")

        # 列宽启发式：按各列最大内容长度加权，中文按 1、英文按 0.55 计
        def wlen(s):
            return sum(1.0 if ord(c) > 127 else 0.55 for c in str(s))
        weights = el.get("weights")
        if weights and len(weights) == ncols:
            col_w = [float(w) for w in weights]
        else:
            col_w = []
            for c in range(ncols):
                m = max(wlen(r[c]) for r in data)
                col_w.append(max(m, 4.0))
        total = sum(col_w)
        col_widths = [max(46.0, CONTENT_W * w / total) for w in col_w]
        scale = CONTENT_W / sum(col_widths)
        col_widths = [w * scale for w in col_widths]

        tbl_data = []
        if headers:
            tbl_data.append([Paragraph(_escape(c), st_cell_head) for c in headers])
        body_start = 1 if headers else 0
        for r in data[body_start:]:
            cells = []
            for c in r:
                txt = str(c)
                style = st_cell_b if txt.startswith("**") and txt.endswith("**") else st_cell
                txt = txt[2:-2] if style is st_cell_b else txt
                cells.append(Paragraph(_escape(txt), style))
            tbl_data.append(cells)

        t = Table(tbl_data, colWidths=col_widths, repeatRows=1 if headers else 0)
        cmds = [
            ("GRID", (0, 0), (-1, -1), 0.5, C_TBL_GRID),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ]
        if headers:
            cmds += [("BACKGROUND", (0, 0), (-1, 0), C_TBL_HEAD_BG)]
            for i in range(1, len(tbl_data)):
                if i % 2 == 0:
                    cmds.append(("BACKGROUND", (0, i), (-1, i), C_TBL_STRIPE))
        else:
            for i in range(len(tbl_data)):
                if i % 2 == 1:
                    cmds.append(("BACKGROUND", (0, i), (-1, i), C_TBL_STRIPE))
        t.setStyle(TableStyle(cmds))
        story.append(t)
        story.append(Spacer(1, 10))

    def add_toc_table():
        story.append(Paragraph("目　次", st_toc_title))
        rows = []
        for lvl, text in toc_entries:
            if lvl == 0:
                continue
            pg = toc_pages.get(text, "–")
            rows.append((lvl, text, pg))
        tbl_rows = []
        for lvl, text, pg in rows:
            ts = st_toc_l1 if lvl == 1 else st_toc_l2
            tbl_rows.append([Paragraph(_escape(text), ts),
                             Paragraph(str(pg), st_toc_pg)])
        t = Table(tbl_rows, colWidths=[CONTENT_W - 56, 56], repeatRows=0)
        t.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 1.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5),
            ("LEFTPADDING", (0, 0), (-1, -1), 2),
            ("LINEBELOW", (0, 0), (-1, -2), 0.25, colors.HexColor("#E3E8EF")),
        ]))
        story.append(t)

    for el in elements:
        et = el.get("type")
        if et == "title":
            story.append(Paragraph(_escape(el["text"]), st_title))
        elif et == "subtitle":
            story.append(Paragraph(_escape(el["text"]), st_sub))
        elif et == "meta":
            story.append(Paragraph(_escape(el["text"]), st_meta))
        elif et == "heading":
            add_heading(el["text"], el.get("level", 1))
        elif et == "paragraph":
            style = st_body if el.get("indent", True) else st_body_noindent
            if el.get("center"):
                style = ParagraphStyle("pc%d" % len(story), parent=style,
                                       alignment=TA_CENTER, firstLineIndent=0)
            story.append(Paragraph(_escape(el["text"]), style))
        elif et == "table":
            add_table(el)
        elif et == "list":
            items = el.get("items", [])
            ordered = el.get("ordered", False)
            for i, item in enumerate(items):
                prefix = ("%d. " % (i + 1)) if ordered else "• "
                story.append(Paragraph(_escape(prefix + item),
                                       ParagraphStyle("li%d" % len(story), parent=st_body_noindent,
                                                      leftIndent=14, firstLineIndent=0,
                                                      spaceAfter=3)))
        elif et == "blockquote":
            q = Paragraph(_escape(el["text"]), st_quote)
            t = Table([[q]], colWidths=[CONTENT_W])
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), C_QUOTE_BG),
                ("LINEBEFORE", (0, 0), (0, -1), 3, C_QUOTE_BAR),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ]))
            story.append(t)
            story.append(Spacer(1, 8))
        elif et == "code":
            lines = el.get("lines", [])
            if lines:
                body = "<br/>".join(_escape(ln) for ln in lines)
                para = Paragraph(body, st_code)
                t = Table([[para]], colWidths=[CONTENT_W])
                t.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F5F7FA")),
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#C9D4E2")),
                    ("TOPPADDING", (0, 0), (-1, -1), 7),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                    ("LEFTPADDING", (0, 0), (-1, -1), 10),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ]))
                story.append(t)
                story.append(Spacer(1, 8))
        elif et == "toc_table":
            add_toc_table()
        elif et == "page_break":
            story.append(PageBreak())
        elif et == "spacer":
            story.append(Spacer(1, el.get("height", 10)))

    doc = ReportDoc(output, pagesize=A4, leftMargin=ML, rightMargin=MR,
                    topMargin=MT, bottomMargin=MB,
                    title=params.get("title", ""), author=params.get("author", ""),
                    subject=params.get("subject", ""))
    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)

    import pymupdf
    d = pymupdf.open(output)
    d.set_metadata({
        "title": params.get("title", "") or "李紫圣思维与价值体系 · 致所有AI共识文件",
        "author": params.get("author", "") or "李紫圣 / 小墨",
        "subject": params.get("subject", ""),
        "creator": "pdfkit consensus_report extension",
        "producer": "reportlab + pymupdf",
    })
    d.saveIncr()
    npages = len(d)
    d.close()
    return {"ok": True, "output": output, "pages": npages,
            "elements": len(elements), "toc_entries": len(toc_entries)}
