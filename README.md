# 东南大学教务处讲座更新提醒器

## 能做什么

- 自动监控 3 个公开栏目：
  - [课外研学讲座](https://jwc.seu.edu.cn/kwyxjz/list.htm)
  - [文化素质讲座](https://jwc.seu.edu.cn/whszjz/list.htm)
  - [学业辅导讲座](https://jwc.seu.edu.cn/xyfdjz/list.htm)
- 发现**新增公告**或**标题/列表日期变化**，通过 Server酱 Turbo 推送一条微信消息，包含标题和原文网址。
- 自动记录已处理通知，避免重复发送。首次运行只登记已有历史通知，不打扰你。
- 使用 GitHub Actions 定时运行，你的 Windows 电脑可以关机。

## 具体使用步骤（只需配置一次）

### 1. 开通微信推送

1. 打开 <https://sct.ftqq.com>，使用微信扫码登录。
2. 在“通道配置”中根据网站提示启用一个可用的微信通道。
3. 在“SendKey”界面复制 **以 SCT 开头** 的密钥，**不要发给别人，也不要粘贴到公开仓库文件里**。
4. 免费额度以 Server酱官网实时说明为准，目前免费会员每天 5 条（多条讲座合并成 1 条提醒）。

### 2. 在 GitHub 创建仓库并上传文件

1. 登录 <https://github.com>，点击右上角“+” → “New repository”，仓库可设为 **Private**。
2. 在电脑上把本项目 zip 解压成文件夹；注意 `.github` 是隐藏目录，上传时必须保留路径 `.github/workflows/lecture-watch.yml`。
3. GitHub 网页里可以点击“Add file” → “Upload files”上传各文件，也可直接用 git 命令上传整个项目（推荐）。
4. **确保**仓库包含 `monitor.py`、`requirements.txt` 和 `.github/workflows/lecture-watch.yml`；首次尚无 `data/seen.json` 是正常的。

> `.github` 中的工作流文件，上传到 GitHub 后才会触发自动任务。网页批量上传有时不方便保留隐藏目录，请核对文件树。

### 3. 配置 Secret（重要）

进入仓库的 **Settings → Secrets and variables → Actions → New repository secret**。

- **Name**：`SERVERCHAN_SENDKEY`
- **Secret**：你在 Server酱拿到的以 SCT 开头的密钥。

点击 Add secret。密钥不会提交到仓库文件中。

### 4. 开启并测试 Actions

1. 打开仓库的 **Actions** 标签页。如显示需要开启，按提示启用工作流。
2. 找到“东南大学讲座更新提醒”，点击 **Run workflow** 手动执行，勾选 `send_test` 后运行。
3. 若运行成功，你的微信将收到**一条测试消息**。第一次运行也会建立历史通知基线。
4. 后面默认约每 15 分钟检查一次，只在发现新增或变更时发提醒。

**如果最后一步无法将记录推回仓库**：在 Settings → Actions → General → Workflow permissions 中，允许工作流的 `Read and write permissions`，或检查仓库/组织权限策略。工作流自身已声明 `contents: write`。

## 设计限制与注意事项

- GitHub 定时任务**不是实时**推送，有时会排队延迟或少量计划执行被跳过。
- 目前只监控列表中的**新公告和标题/日期变化**，**不能监控正文内容中不改标题的细微修改**。因为部分文章仅向校内 IP 开放，不尝试绕过校园网权限。
- 免费 Server酱 Turbo 当前有每日条数限制；一天多条新增会被合并成一条推送。如果用完配额，程序会保留未完成状态，在下次检测时重试。
- 首次运行需要正常连接并解析学校网站。如果 GitHub 云端访问学校列表被限制，部署会失败，这种情况下可改成校园网电脑上的 Windows 定时任务。
- 学校如修改网站布局，可能需要更新 `monitor.py` 中的链接识别规则。
- 如果空白的“文化素质讲座”栏目有新文章，工具也会监控到符合学校文章 URL 格式的链接。

## Windows 本地运行（可选）

安装 Python 后，在文件夹内执行：

```powershell
pip install -r requirements.txt
$env:SERVERCHAN_SENDKEY='你自己的SCT密钥'
python monitor.py
```

之后可以用 Windows 任务计划程序每 15 分钟执行一次，但这需要电脑开机并能够访问校园网站。不要把密钥写进公开代码或脚本。

## 项目文件

- `monitor.py`：网页解析、去重、微信推送逻辑
- `.github/workflows/lecture-watch.yml`：每 15 分钟云端执行、保存记录
- `data/seen.json`：第一次运行后自动生成，存放处理过的文章 URL、标题和日期
- `requirements.txt`：Python 依赖
