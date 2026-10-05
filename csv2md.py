#!/usr/bin/env python3
"""csv2md — CSV/TSV 转 Markdown 表格。纯标准库，纯本地。"""

import argparse
import csv
import json
import sys

__version__ = "0.1.0"


def escape_cell(text: str) -> str:
    """转义单元格：换行 -> <br>，| -> \\|。"""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\n", "<br>")
    text = text.replace("|", "\\|")
    return text


def truncate(text: str, max_width: int) -> str:
    if max_width is None or max_width <= 0:
        return text
    if len(text) <= max_width:
        return text
    return text[: max_width - 1] + "…"


ALIGN_SEP = {"left": ":---", "center": ":---:", "right": "---:"}


def parse_aligns(spec: str, ncols: int, default: str = "left") -> list:
    """spec 如 'l,c,r' 或 'left,center,right'；不足列数用 default 补齐，多出则截断。"""
    short = {"l": "left", "c": "center", "r": "right"}
    if not spec:
        return [default] * ncols
    parts = [p.strip().lower() for p in spec.split(",")]
    aligns = []
    for p in parts:
        name = short.get(p, p)
        if name not in ALIGN_SEP:
            raise ValueError(f"未知对齐方式：{p}（可用 left/center/right 或 l/c/r）")
        aligns.append(name)
    while len(aligns) < ncols:
        aligns.append(default)
    return aligns[:ncols]


def read_rows(source, delimiter: str) -> list:
    reader = csv.reader(source, delimiter=delimiter)
    rows = [row for row in reader]
    # 去掉全空行
    rows = [r for r in rows if any(c.strip() for c in r)]
    return rows


def to_markdown(rows: list, aligns: list, max_width: int) -> str:
    if not rows:
        raise ValueError("没有数据可转换")
    ncols = max(len(r) for r in rows)
    # 补齐短行
    norm = [r + [""] * (ncols - len(r)) for r in rows]
    cells = [
        [truncate(escape_cell(c), max_width) for c in row]
        for row in norm
    ]
    header, body = cells[0], cells[1:]
    align_row = [ALIGN_SEP[a] for a in aligns[:ncols]]

    def fmt(row):
        return "| " + " | ".join(row) + " |"

    lines = [fmt(header), fmt(align_row)]
    lines.extend(fmt(r) for r in body)
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="csv2md",
        description="CSV/TSV 转 Markdown 表格（GitHub 表格风格）。",
    )
    ap.add_argument("input", nargs="?", help="输入文件（省略则用 --stdin）")
    ap.add_argument("--stdin", action="store_true", help="从标准输入读取")
    ap.add_argument("--tsv", action="store_true", help="按 TSV 解析")
    ap.add_argument("--out", help="写入文件（默认输出到 stdout）")
    ap.add_argument("--no-header", action="store_true",
                    help="首行不是表头（自动生成 列1/列2… 表头）")
    ap.add_argument("--aligns", default="",
                    help="每列对齐，如 l,c,r（可用 left/center/right 或 l/c/r）")
    ap.add_argument("--max-width", type=int, default=None,
                    help="单元格最大宽度，超长截断并加 …")
    ap.add_argument("--json", action="store_true",
                    help="同时输出解析摘要到 stderr（JSON）")
    ap.add_argument("--version", action="version", version=f"csv2md {__version__}")
    args = ap.parse_args(argv)

    if args.stdin or not args.input:
        source = sys.stdin
        close = False
    else:
        try:
            source = open(args.input, newline="", encoding="utf-8-sig")
        except FileNotFoundError:
            print(f"error: 文件不存在：{args.input}", file=sys.stderr)
            return 1
        except OSError as e:
            print(f"error: 无法读取文件：{args.input}（{e}）", file=sys.stderr)
            return 1
        close = True

    try:
        rows = read_rows(source, "\t" if args.tsv else ",")
    except csv.Error as e:
        print(f"error: 解析失败：{e}", file=sys.stderr)
        return 1
    finally:
        if close:
            source.close()

    if not rows:
        print("error: 输入为空，没有可转换的数据", file=sys.stderr)
        return 1

    if args.no_header:
        ncols = max(len(r) for r in rows)
        rows = [[f"列{i + 1}" for i in range(ncols)]] + rows

    try:
        aligns = parse_aligns(args.aligns, max(len(r) for r in rows))
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    md = to_markdown(rows, aligns, args.max_width)

    if args.out:
        try:
            with open(args.out, "w", encoding="utf-8") as f:
                f.write(md)
        except OSError as e:
            print(f"error: 无法写入：{args.out}（{e}）", file=sys.stderr)
            return 1
    else:
        sys.stdout.write(md)

    if args.json:
        summary = {"rows": len(rows), "columns": max(len(r) for r in rows),
                   "aligns": aligns}
        print(json.dumps(summary, ensure_ascii=False), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
