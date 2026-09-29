# 使用、GitHub 发布与更新

## 当前在线站点

入口为 **https://www.zengyuwei.cn/healthcare/**，个人主页 **https://www.zengyuwei.cn/home/** 已登记“开放医学指南”。源码仓库为 https://github.com/StarlightDamian/knowledge-healthcare 。

2026-09-30 挂载到现有主页静态服务；复用既有域名和隧道。医学页面自包含于 `healthcare/index.html`，服务从 `~/.local/share/home-page/releases/current` 读取。`/healthcare` 自动跳转至 `/healthcare/`。医学和健身路径返回 `Cache-Control: public, no-cache, no-transform`，保留原始页面并阻止托管层注入统计脚本。

服务器主页源码在 `/mnt/raid1/03_software_engineering/05_github/home-assistant/home-page`。本次线上候选从当前发布目录复制，仅添加医学页面和主页入口；原5个项目保留，线上现为6个。源码中另外10个尚未发布的项目没有随本次上线。普通主页发布或回滚会继承当前 `fitness/`、`healthcare/` 目录；显式提供某应用目录时完整采用候选版本。

### 更新与回滚

1. 修改内容或界面，完成下文检查并构建 `index.html`。
2. 在服务器复制当前 release 为独立候选，仅替换候选的 `healthcare/index.html`；使用候选回环 HTTP 验证内容和响应头。不要直接覆盖 `current` 内的文件，也不要发布包含无关改动的主页 `dist/`。
3. 从主页源码目录运行 `python3 src/scripts/publish-static.py <候选目录> "$HOME/.local/share/home-page/releases"`，然后 `systemctl --user restart home-page.service`。等待服务就绪，核对公网状态和医学页面SHA-256。
4. 要回退医学页面，在新候选中明确放入上一版 `healthcare/`，再按同一流程发布。普通主页回滚保留当前医学页面，不能用它代替医学版本回退。

本次版本和验证见 [上线记录](../reports/deployment-20260930.md)。GitHub 推送触发 CI，不会自动更新此服务器。

## 本地直接使用

`index.html` 已构建，包含全部数据与资源。可直接打开文件，或在仓库根目录运行 `python -m http.server 8000 --bind 127.0.0.1`，访问 `http://127.0.0.1:8000`。本地 HTTP 和断网后的 file:// 阅读均已通过 Windows Chromium 检查。

## 最简单的 GitHub Pages 发布

创建或选择仓库，将解压目录内的文件放在仓库根目录，而不是又套一层 `open-medical-guide/`。保留隐藏的 `.github/`。先检查将公开的内容，不上传真实患者资料。

Settings → Pages → Build and deployment → Source 选择 Deploy from a branch；选择自己的主分支和 `/(root)`，保存。GitHub 完成发布后会显示网站地址。提交的是已经构建的 `index.html`，此路线不需要云端 Python/Node 构建。

## Actions 构建发布（可选）

Settings → Pages 将 Source 设为 GitHub Actions，然后在 Actions 手动运行 **Deploy educational preview**。工作流先校验、测试并构建，然后只上传 `_site/index.html` 与 `.nojekyll`，不把审核资料或整个仓库误上传为站点。默认不因医学正文更新而自动向公网部署：由维护者明确触发。

`.github/workflows/ci.yml` 对 push / pull request 自动测试；它不赋予临床审核状态。`pages.yml` 发布教育预览，页面集中说明真实内容与来源状态。使用可选 Pages 路线时，需要仓库管理员一次性配置 Pages 和权限。

官方流程参考：https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages 。GitHub Actions 标签和托管规则可能更新；部署前检查官方说明。工作流使用官方 action 版本标签，**尚未全部固定到不可变提交 SHA**，正式供应链加固需要补充。

## 内容更新

编辑 JSON → `python -m src.guide validate` → Node/Python 测试 → `python -m src.guide build` → 本地检查 → 提交源码及生成的 `index.html`。不要以自动通过 CI 替代医学审核。来源变动运行 `impact` 命令，医学已审条目要重新签审。

## 临床门禁与封包

```bash
python -m src.guide validate --mode clinical   # 当前应失败
python -m src.guide package --out release.zip
python -m src.guide verify
```

临床模式失败不会阻止你分发明确的教育预览，但严禁改名为“临床已验证”规避状态。`verify` 校验当前文件是否与清单一致；修改源码或再生成报告后必须重新打包生成清单。它不提供发布者身份认证或数字签名。

## 生产化尚未完成的项目

独立临床/地区验证、正式审稿制度、真实凭证和受保护分支、完整医学本地化、外部临床基准、指南变化/撤稿监控、可访问性外部审计、行动依赖 SHA 固定、地区用途合规评估、上线监测与纠错响应均需另行完成。
