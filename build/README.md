# build/ — 共识文件 PDF 构建管线

本目录内含《致所有AI共识文件_v1.0》中英 PDF 正式版的完整构建管线，任何人可依此复现字节级一致的 PDF（在相同依赖版本下）。

## 文件 / Files

| 文件 | 作用 |
|---|---|
| `build_elements_zh.py` | 生成中文版元素数据 `elements_zh.json`（标题/段落/表格/引文/目录占位） |
| `build_elements_en.py` | 生成英文版元素数据 `elements_en.json` |
| `rebuild_all.py` | 主编排：两遍构建——第一遍产出 PDF 并提取各标题真实页码，第二遍回填目录页码 |
| `consensus_report.py` | pdfkit 构建扩展（派生自 `mau_report.py`）：Paragraph 表格、书签、两遍目录、参数化页眉、`weights` 显式列宽 |
| `elements_zh.json` / `elements_en.json` | 元素数据（中间产物，已固化以备查） |

## 依赖 / Dependencies

- Python 3.13（reportlab 体系）
- pdfkit-py 技能环境：`C:\Users\Administrator\.workbuddy\plugins\cache\cb_teams_marketplace\document-skills\1.0.0\skills\pdfkit-py\scripts\venv\Scripts\python.exe`
- pymupdf（页码提取与渲染校验）
- `consensus_report.py` 需置于 pdfkit 扩展目录（`pdfkit-extension/scripts/`）并被 pdfkit CLI 发现

## 用法 / Usage

```bash
# 1. 生成元素数据
python build_elements_zh.py
python build_elements_en.py

# 2. 两遍构建（自动回填目录页码，产出 15 个书签）
python rebuild_all.py
```

`rebuild_all.py` 内部对每个语言依次执行：生成 elements → CLI 第一遍构建 → pymupdf 提取标题页码 → CLI 第二遍构建（`--toc_pages_file`）。

## 设计要点 / Design Notes

- **两遍构建**：目录页码无法预知，必须先构建再提取再回填；
- **weights 显式列宽**：英文表格首列曾因启发式列宽被拦腰截断（Personality/Business/Creation），改为显式权重后修复；
- **零 LLM**：构建全程确定性代码，无模型参与——功能代码化，提示词只做调用。

## 已知边界 / Known Limitations

- 母本 Markdown 在 `D:\商业计划文案\一人公司核心资料\`（作者机器），本仓库 `files/` 内为分发副本；
- PDF 内嵌 CJK 字体（中文版约 440KB，英文版约 70KB），体积差异属正常。
