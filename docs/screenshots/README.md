# 页面实测截图

2026-09-29，本轮截图来自内置浏览器通过真实本地 HTTP `http://127.0.0.1:8765/` 打开生成的 `index.html`，不是设计示意图。桌面按1440×1000、手机按390×844视口验收；截图按浏览器实际输出尺寸保存。

- `desktop.png`：米白/墨绿入口、72/32/2统计、固定左栏、搜索及语言位置；已移除重复审核徽标。
- `search.png`：普通感冒查询和相关卡片。
- `detail.png`：危险信号、长文目录和正文。
- `source-info.png`：详情末尾展开的来源与编辑信息。
- `mobile.png`、`mobile-detail.png`：手机查阅和普通感冒就医阈值列表。
- `comparison.png`：中英切换后的双病症比较与完整单元格展开。
- `arabic.png`：阿语界面RTL、固定物理布局与明确英文正文回退。

截图与23项真实HTTP浏览器测试互补；测试还覆盖全文CSV、离线文件、隐私和XSS。审核事实集中展示，章节保留直接来源链接。

## 研报地图补充：2026-09-30

以下新增截图同样来自真实本地HTTP。此前截图记录原有病症功能，本组记录补充后的地图：

- `cancer-map.png`：癌症目录、34＋2口径、独立计数与无重复分组标签的卡片。
- `cancer-reading.png`：白血病中文正文、就地术语解释、治疗路径与章节来源。
- `lifecycle-mobile.png`：390×844视口中的功能储备正文、目录和分条知识。
- `lifecycle-arabic.png`：同一正文切换阿语界面，英文回退正文与目录维持LTR。

本轮28项HTTP/离线浏览器检查通过，最终地图相关定向复查通过。截图保存后已重置临时视口。

## 正式站点：2026-09-30

`public-healthcare.png` 来自内置浏览器实际访问 `https://www.zengyuwei.cn/healthcare/`，展示线上栏目与72/32/2统计。公网下载的完整页面SHA-256与本地构建一致。

`public-home-entry.png` 来自正式个人主页，展示新增医学入口及保留的原有项目。

## PostgreSQL在线版本（2026-09-30）

新增postgres-desktop-zh.png和postgres-mobile-ar-detail.png来自真实PostgreSQL、Uvicorn HTTP与Chromium。35项浏览器检查通过；本版本不承诺离线正文，旧离线截图和记录仅说明历史版本。
