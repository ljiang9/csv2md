# csv2md

CSV/TSV 转 Markdown 表格。纯 Python 标准库，纯本地运行，无依赖。

## 安装

```bash
git clone https://github.com/ljiang9/csv2md.git
cd csv2md
```

## 用法

```bash
# 基本用法：输出到 stdout
python -m csv2md data.csv

# 写入文件
python -m csv2md data.csv --out table.md

# 从管道读取
cat data.csv | python -m csv2md --stdin

# TSV 输入
python -m csv2md data.tsv --tsv

# 每列对齐（l/c/r 或 left/center/right，不足列数默认左对齐）
python -m csv2md data.csv --aligns c,r

# 首行不是表头
python -m csv2md data.csv --no-header

# 超长单元格截断（加 …）
python -m csv2md data.csv --max-width 30

# 解析摘要（JSON，打到 stderr）
python -m csv2md data.csv --json
```

示例输出：

```markdown
| name | description | notes |
| :---: | ---: | :--- |
| 小红 | 喜欢吃苹果,香蕉和橙子 | 第一行<br>第二行 |
```

## 设计取舍（诚实说明）

- **转义规则**：单元格里的 `|` 转义为 `\|`；单元格内换行转为 `<br>`。
  选 `<br>` 而不是保留换行，是因为 GitHub 表格里裸换行会破坏表格结构。
- **短行补齐**：某行列数少于表头时，用空单元格补齐，保证每行列数一致。
- **`--max-width`** 按字符数截断（不是显示宽度），CJK 字符按 1 个计。
- **BOM**：用 `utf-8-sig` 读取，Excel 导出的 CSV 自带 BOM 也能处理。
- **空行**：全空行会被跳过。

## 已知局限

- 只生成 **GitHub 风格** Markdown 表格（`|` 分隔 + 对齐行），不做 HTML `<table>`。
- 不做类型推断：所有单元格都当字符串处理。
- 极端大的 CSV 会一次性读入内存；日常文档级文件没问题。
