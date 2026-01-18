# 双色球号码查重工具

一个自动抓取中国福利彩票双色球开奖数据，并提供号码重复检查功能的 Web 应用。支持 GitHub Actions 定时自动更新数据，可选择部署在 **GitHub Pages** 或 **Cloudflare Pages** 上，完全免费运行。

> 🔗 **在线演示**：https://perry0077.github.io/doubleball/

## 功能特性

- **号码查重**：输入 6 个红球号码 + 1 个蓝球号码，检查是否与历史开奖号码重复
- **历史数据**：包含从 2003 年至今的全部双色球开奖记录（约 2000+ 期）
- **自动更新**：通过 GitHub Actions 在每期开奖后自动抓取最新数据
- **免费部署**：使用 Cloudflare Pages 免费托管，无需服务器
- **响应式设计**：支持手机和电脑访问

## 项目结构

```
双色球/
├── html/
│   └── index.html              # 前端页面（包含历史数据）
├── .github/
│   └── workflows/
│       ├── update-data.yml     # GitHub Actions 定时抓取数据
│       └── deploy-pages.yml    # GitHub Pages 自动部署
├── extract_doubleball.py       # 数据抓取核心模块
├── update_html.py              # 更新 HTML 文件的脚本（支持增量更新）
├── scrape_doubleball.py        # 简单抓取示例
├── check_duplicate.py          # 本地查重脚本
├── .gitignore                  # Git 忽略配置
└── README.md                   # 本文件
```

## 工作原理

### 数据来源

数据来自中国福利彩票官方网站 (cwl.gov.cn) 的公开 API 接口：

```
https://www.cwl.gov.cn/cwl_admin/front/cwlkj/search/kjxx/findDrawNotice
```

### 自动更新流程

本项目支持两种部署方式，均可实现全自动更新：

#### GitHub Pages 部署流程

```
GitHub Actions (定时触发：周二/四/日 22:30)
    ↓
运行 update_html.py 增量抓取最新数据
    ↓
更新 HTML 文件中的 historyData
    ↓
自动提交到 GitHub 仓库
    ↓
触发 deploy-pages.yml 自动部署到 GitHub Pages
```

#### Cloudflare Pages 部署流程

```
GitHub Actions (定时触发：周二/四/日 22:30)
    ↓
运行 update_html.py 增量抓取最新数据
    ↓
更新 HTML 文件中的 historyData
    ↓
自动提交到 GitHub 仓库
    ↓
Cloudflare Pages 检测到更新，自动部署
```

### 更新时间

双色球开奖时间为每周二、四、日晚 21:15。GitHub Actions 配置在开奖后约 1 小时自动运行：

- 北京时间：周日、周二、周四 22:30
- UTC 时间：14:30 (cron: `30 14 * * 0,2,4`)

## 本地使用

### 环境要求

- Python 3.9+
- requests 库

### 安装依赖

```bash
# 创建虚拟环境（可选）
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install requests
```

### 抓取数据

```bash
# 抓取全部历史数据并保存为 CSV
python extract_doubleball.py

# 更新 HTML 文件中的数据
python update_html.py
```

### 本地预览

直接用浏览器打开 `html/index.html` 即可使用查重功能。

## 部署指南

### 第一步：Fork 或克隆仓库

```bash
# 方式一：直接 Fork 本仓库（推荐）
# 访问 https://github.com/Perry0077/doubleball 点击 Fork

# 方式二：克隆后推送到自己的仓库
git clone https://github.com/Perry0077/doubleball.git
cd doubleball
git remote set-url origin https://github.com/你的用户名/doubleball.git
git push -u origin main
```

### 第二步：选择部署方式

---

## 方式一：GitHub Pages 部署（推荐）

GitHub Pages 是 GitHub 官方提供的静态网站托管服务，配置简单，与 GitHub Actions 无缝集成。

### 1. 启用 GitHub Pages

1. 打开仓库 **Settings** → **Pages**
2. 在 **Build and deployment** 部分：
   - **Source** 选择 **GitHub Actions**
3. 点击保存

### 2. 手动触发首次部署

1. 进入仓库 **Actions** 页面
2. 点击左侧 **"部署到 GitHub Pages"**
3. 点击 **"Run workflow"** → **"Run workflow"**
4. 等待部署完成（约 30 秒）

### 3. 访问网站

部署成功后，访问：
```
https://你的用户名.github.io/doubleball/
```

### 4. 添加网站链接到仓库（可选）

1. 在仓库首页点击右侧 **About** 旁边的 ⚙️ 齿轮
2. 在 **Website** 填入你的 GitHub Pages 地址
3. 保存

### 5. 验证自动更新

后续每次开奖后，GitHub Actions 会自动：
1. 抓取最新数据 → 2. 更新 HTML → 3. 提交代码 → 4. 自动部署

你可以在 **Actions** 页面查看运行记录。

---

## 方式二：Cloudflare Pages 部署

Cloudflare Pages 提供全球 CDN 加速，国内访问速度更快。

### 1. 连接 Cloudflare Pages

1. 登录 [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. 进入 **Pages** 页面
3. 点击 **Create a project** → **Connect to Git**
4. 授权并选择你的 GitHub 仓库

### 2. 配置构建设置

| 配置项 | 值 |
|--------|-----|
| Build command | 留空 |
| Build output directory | `html` |

点击 **Save and Deploy**

### 3. 访问网站

部署成功后，Cloudflare 会分配一个域名：
```
https://你的项目名.pages.dev/
```

### 4. 验证自动更新

每次 GitHub Actions 推送更新后，Cloudflare Pages 会自动检测并重新部署。

---

### 第三步：验证定时更新

1. 进入 GitHub 仓库的 **Actions** 页面
2. 找到 **更新双色球数据** workflow
3. 点击 **Run workflow** 手动触发一次
4. 等待运行完成，检查是否成功提交更新
5. 确认 Cloudflare Pages 是否自动重新部署

## 免费额度说明

| 服务 | 免费额度 | 实际使用 |
|------|----------|----------|
| GitHub Actions | 2000 分钟/月 | 每次约 1 分钟，每月约 12 分钟 |
| GitHub Pages | 100GB 带宽/月 | 静态页面，几乎可忽略 |
| Cloudflare Pages | 500 次构建/月 | 每月约 12 次 |

两种部署方式都完全在免费额度内运行，无需任何费用。

## 两种部署方式对比

| 特性 | GitHub Pages | Cloudflare Pages |
|------|--------------|------------------|
| 配置难度 | ⭐ 简单 | ⭐⭐ 中等 |
| 国内访问 | 一般 | 较快（有 CDN） |
| 自定义域名 | 支持 | 支持 |
| HTTPS | 自动 | 自动 |
| 与 GitHub 集成 | 原生集成 | 需授权连接 |

## 核心代码说明

### extract_doubleball.py

数据抓取模块，提供以下函数：

- `fetch_page(page_no)` - 获取指定页码的开奖数据
- `fetch_latest_page()` - 只获取第一页（最新 30 条数据）
- `fetch_all_data()` - 遍历所有页面获取完整历史数据
- `extract_fields(records)` - 提取期号、日期、红球、蓝球字段
- `save_to_csv(data)` - 保存数据到 CSV 文件

### update_html.py

HTML 更新脚本，支持增量更新：

```bash
# 增量更新（默认，只抓取第一页新数据）
python update_html.py

# 全量刷新（抓取所有历史数据）
python update_html.py --full
```

工作流程：
1. 读取 HTML 中现有的 `historyData`
2. 判断是否需要全量抓取（首次运行或使用 --full 参数）
3. 增量模式：只抓取第一页，根据期号去重合并
4. 更新 `historyData` 和 `dataInfo`（更新时间、最新期号等）
5. 写回 HTML 文件

### update-data.yml

GitHub Actions 数据更新工作流：

- 定时触发：每周日、二、四 UTC 14:30（北京时间 22:30）
- 支持手动触发：workflow_dispatch
- 自动提交：仅在数据有变化时提交

### deploy-pages.yml

GitHub Pages 自动部署工作流：

- 触发条件：`html/` 目录有文件变化时自动触发
- 支持手动触发：workflow_dispatch
- 部署目标：GitHub Pages

## 数据格式

每条开奖记录包含以下字段：

```json
{
  "code": "2025006",           // 期号
  "date": "2025-01-16",        // 开奖日期
  "red": "03,05,08,13,21,23",  // 红球号码（逗号分隔）
  "blue": "16"                  // 蓝球号码
}
```

## 常见问题

### Q: 数据更新失败怎么办？

A: 检查 GitHub Actions 运行日志，常见原因：
- 官方 API 接口变更
- 网络连接问题
- Cookie 过期（一般不影响）

### Q: 如何手动更新数据？

A:
1. 本地运行：`python update_html.py`
2. 或在 GitHub Actions 页面点击 "Run workflow"

### Q: 可以修改更新频率吗？

A: 修改 `.github/workflows/update-data.yml` 中的 cron 表达式：
```yaml
schedule:
  - cron: '30 14 * * 0,2,4'  # 分 时 日 月 周
```

## 许可证

本项目仅供学习交流使用。双色球开奖数据版权归中国福利彩票发行管理中心所有。

## 致谢

- 数据来源：[中国福利彩票官网](https://www.cwl.gov.cn/)
- 托管服务：[Cloudflare Pages](https://pages.cloudflare.com/)
- 自动化：[GitHub Actions](https://github.com/features/actions)
