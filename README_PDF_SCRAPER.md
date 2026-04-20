# book118 文档爬虫 - 使用说明

## 项目文件

| 文件 | 说明 |
|------|------|
| `book118_pdf_scraper.py` | PDF 爬虫（截图转 PDF，支持翻页） |
| `book118_scraper.py` | 元数据爬虫（抓取文档标题、链接等） |
| `requirements.txt` | Python 依赖 |

---

## 📄 PDF 爬虫（推荐）

### 功能特点
- ✅ 自动获取免费文档列表
- ✅ 使用网页自带翻页按钮翻页
- ✅ 只截取文档内容区域（排除工具栏）
- ✅ 逐页截图并合并为 PDF
- ✅ 支持 Edge 浏览器（Windows 自带）

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行
```bash
python book118_pdf_scraper.py
```

### 输出
- PDF 文件：`output_pdfs/*.pdf`
- 抓取记录：`output_pdfs/captured_docs.csv`

---

## 📊 元数据爬虫

### 功能特点
- ✅ 抓取热门文档列表
- ✅ 抓取免费文档列表
- ✅ 保存为 CSV 和 JSON 格式

### 运行
```bash
python book118_scraper.py
```

### 输出
- `book118_hot_docs_*.csv`
- `book118_hot_docs_*.json`

---

## ⚙️ 配置选项

### 修改抓取数量
编辑 `book118_pdf_scraper.py` 主函数：
```python
# 抓取前 3 个文档
for i, doc in enumerate(docs[:3], 1):

# 改为抓取前 10 个
for i, doc in enumerate(docs[:10], 1):
```

### 修改页数限制
默认最多抓取 5 页，可在 `_get_total_pages()` 方法中调整：
```python
if total_pages <= 0:
    total_pages = 5  # 修改这里的默认页数
```

### 后台运行
```python
scraper.setup_browser(headless=True)  # 无界面模式
```

---

## 🔧 依赖

- `selenium>=4.15.0` - 浏览器自动化
- `Pillow>=10.0.0` - 图片处理
- `img2pdf>=0.5.0` - PDF 生成
- `requests>=2.31.0` - HTTP 请求
- `beautifulsoup4>=4.12.0` - HTML 解析

---

## ⚠️ 注意事项

1. 请遵守 book118.com 的使用条款
2. 仅用于学习交流，不要用于商业用途
3. 部分文档可能需要登录或 VIP 权限
4. 抓取间隔已设置延迟，避免被封禁

---

## 📁 输出示例

```
output_pdfs/
├── captured_docs.csv
├── 艺术教师述职报告 (6 篇).docx.pdf
├── 教师师德述职报告 7 篇.docx.pdf
└── 历史爱国人物的事迹材料.docx.pdf
```
