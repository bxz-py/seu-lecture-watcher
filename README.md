# 东南大学教务处讲座更新提醒器

![运行状态](https://github.com/bxz-py/seu-lecture-watcher/actions/workflows/lecture-watch.yml/badge.svg)
![Python 3.11](https://img.shields.io/badge/Python-3.11-blue)
![GitHub Actions](https://img.shields.io/badge/Automation-GitHub%20Actions-2088FF)

**不用每天刷新教务处网页。** 这是一个基于 Python、GitHub Actions 和 [Server酱 Turbo](https://sct.ftqq.com/) 的讲座更新提醒工具：定期检查东南大学教务处的公开讲座列表，发现新通知后通过微信推送标题与原文链接。

- 不需要自己购买服务器，部署完成后电脑可以关机。
- 默认计划每 **15 分钟**检查一次（GitHub 排队时可能延迟，不保证实时）。
- 只提醒**新增公告**以及**标题或列表日期变化**；同一次检查中发现多条更新时合并推送。
- 首次运行建立历史通知记录，不会把页面里已有的公告全部当成新消息发给你。
- **非东南大学官方项目**；只读取公开网页，不登录教务系统，不绕过校园网络限制。

> **首次使用？** 推荐直接跳到 [方法一：Fork 一份自己的提醒器](#方法一fork-一份自己的提醒器推荐)。手机也可以完成配置。

## 目录

- [监控范围](#监控范围)
- [消息效果示例](#消息效果示例)
- [方法一：Fork 一份自己的提醒器（推荐）](#方法一fork-一份自己的提醒器推荐)
- [方法二：手动创建仓库并上传](#方法二手动创建仓库并上传)
- [检查是否运行成功](#检查是否运行成功)
- [Windows 本地运行](#windows-本地运行可选)
- [常见问题 FAQ](#常见问题-faq)
- [项目文件及实现原理](#项目文件及实现原理)
- [安全、限制与项目说明](#安全限制与项目说明)

## 监控范围

| 栏目 | 官网地址 |
| --- | --- |
| 课外研学讲座 | [查看通知](https://jwc.seu.edu.cn/kwyxjz/list.htm) |
| 文化素质讲座 | [查看通知](https://jwc.seu.edu.cn/whszjz/list.htm) |
| 学业辅导讲座 | [查看通知](https://jwc.seu.edu.cn/xyfdjz/list.htm) |

程序仅监控上述**列表页面可识别的文章链接**，不会读取你的个人教务信息，也不会自动报名讲座。

## 消息效果示例

以下是**格式示意，并非真实收到的截图**。发现一条新增通知时，微信消息大致如下：

> **东南大学教务处讲座更新（1条）**
>
> 共发现 1 条新增或变更的讲座通知：
>
> **[课外研学讲座·新增]** 第 X 周课外研学讲座预告（YYYY-MM-DD）
>
> 官网文章链接
>
> 注：部分文章正文仅允许通过校园网络或学校官方 VPN 查看。

没有新通知时，程序静默运行，不会每 15 分钟发一条“暂无更新”。

实际微信提醒由 Server酱接收通道展示，排版可能略有差异。若要给项目添加真实效果截图，请先遮住微信昵称、头像、SendKey 等个人信息，再上传截图。

## 方法一：Fork 一份自己的提醒器（推荐）

适合大多数同学，**无须自己写代码**。整个过程可以在手机 GitHub 网页上完成。

### 1. Fork 项目到自己的 GitHub

1. 登录 [GitHub](https://github.com/)。
2. 打开本项目主页：[bxz-py/seu-lecture-watcher](https://github.com/bxz-py/seu-lecture-watcher)。
3. 点击右上方 **Fork → Create a new fork**。
4. 按页面提示创建仓库，保留默认的 `main` 分支。

创建后，你将拥有自己的项目副本，例如 `你的用户名/seu-lecture-watcher`。**后面所有设置都应在你自己的仓库完成**，不要修改原仓库。

### 2. 启用 Fork 仓库的 GitHub Actions

打开**自己的**仓库 → **Actions**。

- 如看到 **I understand my workflows, go ahead and enable them**，点击启用。
- 找到 **东南大学讲座更新提醒** 工作流；如看到 **Enable workflow**，点击启用。

**重要：公开仓库被 Fork 后，定时工作流默认是禁用的。** 必须检查并启用自己的工作流，不能因为原仓库显示绿色对勾，就以为自己的仓库已经开始监控。

### 3. 配置 Server酱微信通知

1. 访问 [Server酱 Turbo](https://sct.ftqq.com/)，登录后按官网指引配置一个可用的微信消息通道。
2. 在 Server酱页面找到 **SendKey**，复制以 `SCT` 开头的密钥。
3. 回到**自己的 GitHub 仓库**，打开 **Settings → Secrets and variables → Actions**。
4. 点击 **New repository secret**，填写：

   | 字段 | 内容 |
   | --- | --- |
   | **Name** | `SERVERCHAN_SENDKEY` |
   | **Secret** | 你自己的 Server酱 SendKey（以 `SCT` 开头） |

5. 点击 **Add secret** 保存。

**请不要把 SendKey 放进 README、Python 文件、Issue、提交记录、截图或公开聊天。** GitHub Secrets 的内容不会直接展示在仓库代码中。

### 4. 清除 Fork 时带来的旧通知记录

如果 Fork 下来的仓库已经包含 `data/seen.json`，建议**在第一次运行前删除这个文件**：

1. 打开自己仓库中的 `data/seen.json`。
2. 在文件页面菜单中选择 **Delete file**（可能藏在 `…` 菜单中）。
3. 确认 **Commit changes**，保存到 `main` 分支。

为什么要删除？`seen.json` 是原仓库的历史通知记录。删掉它后，你的第一次运行会重新建立属于自己的基线，不会误用原仓库记录。程序会自动重新生成该文件。

> 手机网页找不到删除按钮时，可以在浏览器菜单里切换到“桌面版网站”。

### 5. 手动运行一次，验证微信推送

1. 打开自己的仓库 → **Actions**。
2. 选择 **东南大学讲座更新提醒**。
3. 点击 **Run workflow**，分支选择 `main`。
4. 勾选 `send_test`（发送测试通知），再点击绿色 **Run workflow**。
5. 打开本次运行记录，确认最终出现**绿色对勾**，并查看微信是否收到测试消息。

只要抓取学校列表、测试推送和保存通知记录都成功，后面就能按计划自动检查。**不需要每次手动点击 Run workflow。**

## 方法二：手动创建仓库并上传

如果不想 Fork，也可以自己新建仓库部署：

1. 在 GitHub 创建一个新仓库（`Public` 或 `Private` 均可），默认分支使用 `main`。
2. 上传以下文件，并保持目录结构：

```text
seu-lecture-watcher/
├── .github/
│   └── workflows/
│       └── lecture-watch.yml
├── monitor.py
├── requirements.txt
├── test_monitor.py
└── README.md
```

3. 再按[方法一的第 2～5 步](#2-启用-fork-仓库的-github-actions)配置 Actions、Server酱和测试运行。

**手机端小技巧：** GitHub 移动网页可能不支持直接上传文件夹。普通文件可以逐个上传；工作流可用 **Add file → Create new file**，在文件名处直接输入 `.github/workflows/lecture-watch.yml`，GitHub 会自动建立对应目录，然后粘贴原项目的文件内容。

## 检查是否运行成功

在自己仓库的 **Actions → 东南大学讲座更新提醒** 中查看运行记录：

| 看到的状态 | 意思 | 建议 |
| --- | --- | --- |
| ✅ 绿色对勾 | 本次工作流完成 | 如果勾选了 `send_test`，也检查是否收到微信 |
| 🟡 排队 / 正在运行 | GitHub 正在安排或执行 | 查看运行详情 |
| ❌ 红色叉号 | 某一步执行失败 | 点开失败的步骤，阅读日志定位原因 |
| 没有运行记录 | 可能尚未启动，或工作流未启用 | 检查 Actions，并手动触发一次 |

**计划任务说明：** `lecture-watch.yml` 目前在 UTC 时间每小时的第 7、22、37、52 分钟安排检查，相当于计划**每约 15 分钟**执行一次。GitHub 可能延迟、跳过个别计划运行，因此它不是秒级实时监控。

项目主页顶部的运行状态徽章显示的是**原仓库**的状态；Fork 用户请以**自己仓库** Actions 页面为准。

## Windows 本地运行（可选）

如果不使用 GitHub Actions，可以在 Windows 电脑上安装 Python 3.11，然后在项目目录打开 PowerShell：

```powershell
python -m pip install -r requirements.txt
python -m unittest -q
$env:SERVERCHAN_SENDKEY='替换为你自己的SCT密钥'
python monitor.py
```

若想进行一次测试推送，可在同一个 PowerShell 窗口临时设置：

```powershell
$env:SEND_TEST='true'
python monitor.py
Remove-Item Env:\SEND_TEST
```

本地运行会把历史记录写入 `data/seen.json`。如需定时检查，可以自行配置 Windows 任务计划程序；这要求**电脑开机并能访问学校官网**。

安全提醒：上面的密钥只应在自己的终端临时使用，不要把真实值提交到 GitHub，也不要在共享电脑上保留包含密钥的命令历史。

## 常见问题 FAQ

<details>
<summary><strong>Q1：为什么显示绿色对勾，却没有收到新的讲座消息？</strong></summary>

如果没有新的公告或标题/日期变化，程序本来就不会发提醒。想确认推送是否正常，可以在 **Run workflow** 时勾选 `send_test`。如果测试运行绿色对勾，但微信没收到消息，请检查 Server酱微信通道是否启用、消息是否进入其他接收入口，并核对 Server酱后台记录。
</details>

<details>
<summary><strong>Q2：为什么 Fork 后没有自动运行？</strong></summary>

GitHub 默认禁用公开仓库 Fork 副本的定时工作流。去自己仓库的 **Actions** 启用工作流；确认 `lecture-watch.yml` 位于默认分支 `main`。此后仍可能有调度延迟。相关说明：[GitHub 工作流启用与停用](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/disable-and-enable-workflows)。
</details>

<details>
<summary><strong>Q3：出现“缺少 SERVERCHAN_SENDKEY”或微信推送失败怎么办？</strong></summary>

检查自己的仓库 **Settings → Secrets and variables → Actions** 中是否存在名称完全一致的 `SERVERCHAN_SENDKEY`，密钥是否以 `SCT` 开头，Server酱推送通道是否配置好，以及当前套餐是否达到推送额度上限。**不要将真实密钥贴到 Issue 或日志截图里。**
</details>

<details>
<summary><strong>Q4：最后“保存通知记录”失败、显示 git push rejected 怎么办？</strong></summary>

这通常是仓库远端分支发生更新，导致推送冲突。检查工作流中 `actions/checkout@v4` 是否使用最新的 `main` 分支，再手动重新运行一次。还要检查 **Settings → Actions → General → Workflow permissions** 里的写入权限是否允许工作流保存 `data/seen.json`。本项目工作流已经声明了 `contents: write`。
</details>

<details>
<summary><strong>Q5：第一次运行为什么没有把历史讲座全部推过来？</strong></summary>

这是预期行为。第一次运行建立 `data/seen.json` 基线，不将已有的历史文章当成“新增”。后续检测到新链接或列表标题/日期变化时才发送消息。
</details>

<details>
<summary><strong>Q6：如果学校在原通知正文里修改了讲座信息，会提醒吗？</strong></summary>

不一定。当前版本只比较**公告链接、列表标题和列表日期**，没有持续比对正文内容。如果正文改了但列表标题、日期没变，程序不会发现。部分文章正文还可能仅允许校园网或学校官方 VPN 访问。
</details>

<details>
<summary><strong>Q7：为什么突然很久没有自动运行？</strong></summary>

先检查 Actions 是否仍处于启用状态。GitHub 可能因仓库长期没有活动而自动禁用公开仓库的计划工作流（通常是 60 天无活动），需要仓库所有者重新启用。也可能是 GitHub 调度延迟或网络故障。可参考 [GitHub Actions 排错文档](https://docs.github.com/en/actions/how-tos/troubleshoot-workflows)。
</details>

<details>
<summary><strong>Q8：手机可以完成部署吗？</strong></summary>

可以。Fork、设置 Secret、启用 Actions、手动测试都可以在 GitHub 网页上操作。手机上看不到按钮时，切换到“桌面版网站”。**无需安装 Python 到手机**。
</details>

## 项目文件及实现原理

```text
教务处公开讲座列表
        ↓
Python（requests + BeautifulSoup）抓取并解析
        ↓
对照 data/seen.json 中已处理的链接、标题和日期
        ↓
有新增或变化？ ── 否 → 不推送
        │
        是
        ↓
Server酱 Turbo → 微信消息
        ↓
推送成功后保存最新去重记录
```

| 文件 | 作用 |
| --- | --- |
| `monitor.py` | 抓取公开讲座列表、解析文章信息、检查更新、发送消息 |
| `requirements.txt` | Python 依赖（`requests`、`beautifulsoup4`） |
| `test_monitor.py` | 解析与去重相关的测试 |
| `.github/workflows/lecture-watch.yml` | GitHub Actions 定时执行和记录提交 |
| `data/seen.json` | 运行后生成/更新的通知记录（只含公开公告标题、日期及链接） |
| `README.md` | 使用说明 |

## 安全、限制与项目说明

- **只抓取公开网页。** 不要求东南大学统一身份认证账号，不登录个人教务系统，不尝试访问受限资源。
- **密钥必须保密。** SendKey 只保存在个人仓库 GitHub Actions Secrets 中，不写入源代码。即使仓库是 Public，Secrets 也不会直接作为文件公开。
- **仓库公开会暴露代码和提交历史。** 请勿上传个人账号、密码、学号、隐私截图或带密钥的配置文件。
- **免费配额和 GitHub Actions 规则可能调整。** 以 [Server酱官网](https://sct.ftqq.com/) 以及 GitHub 官方文档为准。
- **只适用于当前网站结构。** 网站修改 HTML 或链接规则、云端无法访问学校网站时，程序可能需要维护。
- **不是官方信息发布渠道。** 是否开讲、时间地点以及报名要求，请以学校官网原文为准。
- 本项目目前未添加 `LICENSE` 文件；代码虽可公开查看，二次分发及其他使用仍需遵守适用的版权规则。

如发现解析错误、部署问题或有改进建议，欢迎通过 [Issues](https://github.com/bxz-py/seu-lecture-watcher/issues) 反馈。未来可考虑增加**关键词过滤、更多通知渠道和正文变更检测**；这些功能**当前尚未实现**。
