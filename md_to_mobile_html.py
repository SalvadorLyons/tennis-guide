#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""将当前目录下的 Markdown 文件转换为适合手机阅读的 HTML。

用法：
    在本目录（网球笔记根目录）运行：
        python md_to_mobile_html.py

生成结果：
    在当前目录下创建 docs/ 目录（适合直接用于 GitHub Pages），
    每个 .md 对应一个同名 .html 文件。
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import List
import html as _html

# 尝试使用 Python-Markdown，如果没有安装则回退到简单文本模式
try:  # pragma: no cover - 简单依赖检测
    import markdown as _markdown  # type: ignore
except Exception:  # pragma: no cover - 没装库时的正常路径
    _markdown = None


BASE_DIR = Path(__file__).resolve().parent
SOURCE_DIR = BASE_DIR
OUTPUT_DIR = BASE_DIR / "docs"


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1, maximum-scale=1, viewport-fit=cover\" />
  <title>{title}</title>
  <style>
    :root {{
      color-scheme: light dark;
      --bg: #ffffff;
      --fg: #111111;
      --muted: #666666;
      --accent: #1d9bf0;
      --border: #e0e0e0;
    }}
    @media (prefers-color-scheme: dark) {{
      :root {{
        --bg: #050505;
        --fg: #f5f5f5;
        --muted: #999999;
        --accent: #4aa8ff;
        --border: #333333;
      }}
    }}
    * {{ box-sizing: border-box; }}
    html, body {{
      margin: 0;
      padding: 0;
      background: var(--bg);
      color: var(--fg);
      font-family: -apple-system, BlinkMacSystemFont, system-ui, -system-ui, sans-serif;
      -webkit-text-size-adjust: 100%;
    }}
    body {{
      max-width: 720px;
      margin: 0 auto;
      padding: 12px 16px 40px;
      line-height: 1.7;
      font-size: 17px;
    }}
    header {{
      position: sticky;
      top: 0;
      padding: 8px 0 10px;
      margin: 0 0 8px;
      background: linear-gradient(to bottom, var(--bg) 70%, color-mix(in srgb, var(--bg) 90%, transparent));
      backdrop-filter: blur(8px);
      border-bottom: 1px solid var(--border);
      z-index: 10;
    }}
    h1 {{
      font-size: 22px;
      margin: 0 0 2px;
    }}
    .file-meta {{
      font-size: 12px;
      color: var(--muted);
    }}
    main {{
      margin-top: 8px;
    }}
    h2 {{ font-size: 20px; margin: 20px 0 6px; }}
    h3 {{ font-size: 18px; margin: 16px 0 4px; }}
    h4, h5, h6 {{ font-size: 16px; margin: 12px 0 4px; }}
    p {{ margin: 6px 0 10px; }}
    a {{ color: var(--accent); text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    ul, ol {{ padding-left: 1.4em; margin: 4px 0 10px; }}
    li {{ margin: 2px 0 2px; }}
    .toc {{ list-style: none; padding-left: 0; margin: 8px 0 16px; }}
    .toc li {{ padding: 8px 10px; border-radius: 10px; border: 1px solid var(--border); margin: 6px 0; }}
    .toc a {{ display: block; }}
    .toc .title {{ font-size: 16px; font-weight: 600; }}
    .toc .file-name {{ font-size: 12px; color: var(--muted); }}
    code {{
      font-family: SFMono-Regular, ui-monospace, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
      font-size: 0.9em;
      background: color-mix(in srgb, var(--bg) 85%, #888888);
      padding: 1px 4px;
      border-radius: 4px;
    }}
    pre {{
      background: color-mix(in srgb, var(--bg) 92%, #777777);
      padding: 8px 10px;
      border-radius: 8px;
      overflow-x: auto;
      font-size: 0.9em;
      line-height: 1.5;
    }}
    pre code {{
      background: none;
      padding: 0;
    }}
    blockquote {{
      margin: 6px 0 10px;
      padding: 4px 10px;
      border-left: 3px solid var(--accent);
      color: var(--muted);
      background: color-mix(in srgb, var(--bg) 96%, #777777);
      border-radius: 0 8px 8px 0;
    }}
    hr {{
      border: none;
      border-top: 1px dashed var(--border);
      margin: 16px 0;
    }}
    img {{
      max-width: 100%;
      display: block;
      margin: 8px auto;
      border-radius: 8px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin: 8px 0 12px;
      font-size: 0.9em;
    }}
    th, td {{
      border: 1px solid var(--border);
      padding: 4px 6px;
      text-align: left;
    }}
    th {{
      background: color-mix(in srgb, var(--bg) 92%, #777777);
    }}
  </style>
</head>
<body>
  <header>
    <h1>{title}</h1>
    <div class=\"file-meta\">来自：{source_name}</div>
  </header>
  <main>
  {content}
  </main>
</body>
</html>
"""


def find_markdown_files(directory: Path) -> List[Path]:
    """在目录中查找所有一级 .md 文件（不递归子目录）。"""
    return sorted(p for p in directory.glob("*.md") if p.is_file())


def guess_title(text: str, default: str) -> str:
    """从 Markdown 内容中猜一个标题，优先使用第一行一级标题。"""
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped.lstrip("# ").strip() or default
    return default


def render_markdown(text: str) -> str:
    """将 Markdown 渲染为 HTML。如果没安装 markdown 库，则以预格式文本显示。"""
    if _markdown is not None:
        return _markdown.markdown(
            text,
            extensions=["extra", "tables", "fenced_code"],
            output_format="html5",
        )
    # 回退方案：用 <pre> 包一层，保持换行，配合 CSS 的 pre-wrap
    escaped = _html.escape(text)
    return f"<pre style='white-space: pre-wrap'>{escaped}</pre>"


def convert_one_file(src: Path, dst_dir: Path) -> Path:
    text = src.read_text(encoding="utf-8")
    title = guess_title(text, default=src.stem)
    html_body = render_markdown(text)

    html = HTML_TEMPLATE.format(
        title=_html.escape(title),
        source_name=_html.escape(src.name),
        content=html_body,
    )

    dst_dir.mkdir(parents=True, exist_ok=True)
    out_path = dst_dir / (src.stem + ".html")
    out_path.write_text(html, encoding="utf-8")
    return out_path


def build_index_page(md_files: List[Path], dst_dir: Path) -> Path:
    """生成带目录的首页 index.html，列出所有章节链接。"""
    items = []
    for src in md_files:
        text = src.read_text(encoding="utf-8")
        title = guess_title(text, default=src.stem)
        href = f"{src.stem}.html"
        items.append((src.name, title, href))

    parts: list[str] = []
    parts.append("<section>")
    parts.append("<h2>目录</h2>")
    parts.append("<ul class=\"toc\">")
    for src_name, title, href in items:
        parts.append(
            "<li>"
            f"<a href=\"{_html.escape(href)}\">"
            f"<div class='title'>{_html.escape(title)}</div>"
            f"<div class='file-name'>{_html.escape(src_name)}</div>"
            "</a>"
            "</li>"
        )
    parts.append("</ul>")
    parts.append("</section>")

    content = "\n".join(parts)
    html = HTML_TEMPLATE.format(
        title=_html.escape("网球自学指南"),
        source_name=_html.escape("目录 index"),
        content=content,
    )

    dst_dir.mkdir(parents=True, exist_ok=True)
    out_path = dst_dir / "index.html"
    out_path.write_text(html, encoding="utf-8")
    return out_path


def main(argv: list[str]) -> int:
    if _markdown is None:
        print("[提示] 未检测到 'markdown' 库，将使用简单文本模式。")
        print("       可选：运行 'pip install markdown' 后，重新执行本脚本，效果更好。")

    md_files = find_markdown_files(SOURCE_DIR)
    if not md_files:
        print("未在当前目录找到任何 .md 文件。")
        return 0

    print(f"发现 {len(md_files)} 个 Markdown 文件，开始转换……")

    for path in md_files:
        out = convert_one_file(path, OUTPUT_DIR)
        rel = out.relative_to(BASE_DIR)
        print(f"- {path.name}  ->  {rel}")

    index_path = build_index_page(md_files, OUTPUT_DIR)
    rel_index = index_path.relative_to(BASE_DIR)
    print(f"- 目录首页  ->  {rel_index}")

    print("完成！可以在 'docs' 文件夹中用浏览器或 GitHub Pages 打开这些 HTML 文件（入口为 index.html）。")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main(sys.argv[1:]))
