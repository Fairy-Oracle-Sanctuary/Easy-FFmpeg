<p align="center">
  <img src="app/resource/images/logo.png" alt="logo" width="200"/>
</p>

<h1 align="center">
  Easy FFmpeg
</h1>

<p align="center">
  <a href="https://easypeg.ora-san.org/">软件官网</a> · <a href="https://github.com/Fairy-Oracle-Sanctuary/Easy-FFmpeg">GitHub 仓库</a> · <a href="https://github.com/Fairy-Oracle-Sanctuary/Easy-FFmpeg/releases">下载发布版</a>
</p>

<p align="center">
  <i>基于 FFmpeg 的批量视频处理工具，操作简单易用</i>
</p>

<p align="center">
  提供可视化任务队列、高级编码参数配置，以及音频提取、视频剪切、GIF 制作、视频拼接、字幕处理、音量归一化、变速等 12 种常用工具，内置 FFmpeg 路径自动检测、右键菜单集成与系统托盘。
</p>

<p align="center">
  <a style="text-decoration:none">
    <img src="https://img.shields.io/badge/LICENSE-GPL%20v3-green" alt="LICENSE"/>
  </a>

  <a style="text-decoration:none">
    <img src="https://img.shields.io/badge/Python-3.9+-yellow" alt="Python 3.9+"/>
  </a>

  <a style="text-decoration:none">
    <img src="https://img.shields.io/badge/Version-1.0.0-purple" alt="Version 1.0.0"/>
  </a>

  <a style="text-decoration:none">
    <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-orange" alt="Platform Windows | macOS | Linux"/>
  </a>

  <a style="text-decoration:none">
    <img src="https://img.shields.io/badge/UI-PySide6%20%2B%20QFluentWidgets_Pro-cyan" alt="UI PySide6 + QFluentWidgets_Pro"/>
  </a>
</p>

<p align="center">
 <a href="README.md">English</a> | <a href="README.zh.md">简体中文</a>
</p>

<p align="center">
  <a href="#功能特性">功能特性</a> •
  <a href="#快速开始">快速开始</a> •
  <a href="#使用说明">使用说明</a> •
  <a href="#配置说明">配置说明</a> •
  <a href="#常见问题">常见问题</a>
</p>

---

## 功能特性

### 🎬 任务队列与批量处理
- 可视化任务卡片，实时显示进度、速度、码率与预估大小
- 任务持久化存储（SQLite），仅已完成任务入库，运行中任务留存内存
- 支持批量添加、重试、取消、删除（可选同时删除输出文件）
- 重试任务可选「使用当前设置」或「使用原任务参数」
- Two-Pass 编码支持，自动切换阶段文案
- 失败任务角标警告，主页信息卡片一键跳转
- 拖放文件到路径输入框即可添加，支持递归扫描文件夹
- Windows 资源管理器右键菜单直接发送媒体文件

### 🎛️ 高级编码参数
- 编码器选择（软件编码 / 硬件加速：CUDA、VideoToolbox、QSV 等）
- 质量控制（CRF / 目标码率）与编码速度（preset）
- 分辨率（自定义宽高 / 常用预设）与帧率
- 音频编码器、音频码率、移除音轨
- 图片质量与编码参数
- 进阶设置：起始时间、时长、去隔行、画面旋转、tune
- 参数块可勾选启用，未勾选不加入 FFmpeg 命令
- 支持自定义 FFmpeg 命令模板（`{{input_file}}` / `{{output_file}}` 占位符）

### 🧰 更多工具（12 种）
- **音频提取**：从视频提取音轨，转为 MP3/AAC/WAV/Opus/Vorbis/FLAC
- **视频截图**：按时间点截取单帧画面
- **GIF 制作**：视频片段转 GIF 动图
- **视频剪切**：按时间段裁剪视频
- **音视频格式转换**：容器与编码互转
- **图片格式转换**：图片格式互转与质量压缩
- **视频拼接**：合并多个视频，自动用 `scale2ref` + `setsar` 统一分辨率与 SAR
- **媒体信息**：异步探测编码 / 码率 / 时长等详情，结构化中文展示
- **MS Store 徽标**：一键生成上架微软商店的 5 个徽标（720×1080、1080×1080、300×300、150×150、71×71），保持原比例居中透明补齐
- **字幕处理**：提取字幕 / 嵌入硬字幕（烧录）/ 嵌入软字幕 / 格式转换（SRT/ASS/VTT 互转）
- **音量归一化**：基于 EBU R128 标准的响度与动态范围归一化
- **速度调整**：音视频同步变速 / 仅视频 / 仅音频，`atempo` 链支持 0.25×–8×+

### 🖼️ 界面与交互特性
- 现代化 Fluent 设计（PySide6 + QFluentWidgets）
- Windows 11 云母（Mica）效果
- 标题栏快捷主题切换（深色 / 浅色），自动持久化
- 系统托盘集成，关闭最小化到托盘
- 检测到新版本时在更新按钮上以 InfoBadge 显示版本号
- 内置更新检查：非商店版可直接下载安装包到本地，商店版跳转浏览器
- 多语言支持（基于 FluentTranslator 的 i18n 框架）
- 日志自动清理（可配置保留天数）

---

## 系统要求

- **操作系统**：Windows 10/11（推荐）、macOS、Linux
- **Python**：3.9+（源码运行）
- **FFmpeg**：需单独安装，应用内可自动检测路径或手动指定
- **硬件**：支持硬件加速的 GPU（可选，用于编码加速）

---

## 快速开始

### 1. 克隆仓库

```bash
git clone --recursive https://github.com/Fairy-Oracle-Sanctuary/Easy-FFmpeg.git
cd Easy-FFmpeg
```

### 2. 创建虚拟环境（推荐使用 uv）

```bash
uv venv
# Windows
.venv\Scripts\activate
# Unix/macOS
source .venv/bin/activate
```

### 3. 安装依赖

```bash
# 通用依赖
uv pip install -r requirements.txt

# Windows 额外依赖（pywin32）
uv pip install -r requirements-win.txt

# macOS 额外依赖（PyObjC）
uv pip install -r requirements-mac.txt
```

### 4. 准备 FFmpeg

确保 `ffmpeg` 可在系统 PATH 中访问，或在应用「设置」页面手动指定 FFmpeg 可执行文件路径。应用启动时会自动检测。

### 5. 运行应用

```bash
python Easy-FFmpeg.py
```

> 普通用户可直接从 [Releases](https://github.com/Fairy-Oracle-Sanctuary/Easy-FFmpeg/releases) 下载对应平台的安装包，无需配置 Python 环境。

---

## 使用说明

### 主页
- **信息卡片**：显示版本、更新时间、日志占用，提供 FFmpeg 官网、GitHub、清空日志、重置设置等快捷入口
- **更新按钮**：检测到新版本时显示版本号徽标，点击检查更新

### 任务页
- 拖放或右键发送媒体文件即可添加任务
- 任务卡片支持开始 / 取消 / 重试 / 删除（删除时可选择是否一并删除输出文件）
- 顶部角标显示任务数量，存在失败任务时变红警告

### 高级页
- 勾选需要启用的参数块，按需配置编码器、质量、分辨率、音频等
- 启用「自定义参数」可直接编写 FFmpeg 命令模板

### 更多页
- 从入口网格选择所需工具，进入功能页填写参数后执行
- 工具任务复用主任务队列，统一显示进度与状态

### 设置页
- 配置个性化（主题、主题色、界面缩放、语言）、FFmpeg 路径、编码默认参数、日志清理等
- 部分设置项需重启应用后生效

### 主题切换
点击标题栏最小化按钮左侧的主题切换按钮，可在深色 / 浅色模式间快速切换，设置自动保存。

---

## 配置说明

主要配置项可在「设置」页面修改，配置文件存储在用户目录下（Windows：`%APPDATA%\EasyFFmpeg\config.json`）。

### 个性化
- 应用主题（深色 / 浅色 / 跟随系统）
- 主题色
- 界面缩放
- Mica 效果（Windows 11）
- 语言

### FFmpeg
- FFmpeg 可执行文件路径（自动检测）
- 自定义视频 / 音频 / 图片参数模板
- 启用的参数块
- 并发编码数
- 重试任务是否使用当前设置
- 软件编码器 / 硬件加速开关与编码器选择
- 质量模式（CRF / 码率）、CRF、视频码率、Two-Pass
- 编码速度、分辨率、自定义宽高、帧率
- 音频编码器、音频码率、移除音轨
- 图片质量、tune、起始时间、时长、去隔行、画面旋转

### 主窗口
- 关闭时直接退出（而非最小化到托盘）
- 启动时自动检查更新

### 主页
- 添加文件时递归扫描子文件夹

### 日志
- 自动清理过期日志
- 日志保留天数

---

## 常见问题

### Q: 提示找不到 FFmpeg
A: 请确保 `ffmpeg` 已安装并在系统 PATH 中，或在「设置 → FFmpeg」页面手动指定 `ffmpeg.exe`（Windows）/ `ffmpeg`（macOS/Linux）的完整路径。应用支持自动检测。

### Q: 视频拼接报错「Input link parameters do not match」
A: 输入视频分辨率或 SAR 不一致时，应用已内置 `scale2ref` + `setsar` 滤镜自动统一。若仍失败，请检查输入文件是否损坏，或先用「音视频格式转换」统一参数。

### Q: 嵌入硬字幕失败（路径含空格 / 盘符）
A: 应用已对字幕路径中的 `\`、`:`、`'` 进行转义并用单引号包裹。若仍失败，请尽量避免路径中包含特殊字符，或检查字幕文件格式是否被 `subtitles` 滤镜支持。

### Q: MS Store 徽标只生成了一个任务
A: 该功能已支持同一输入生成 5 个不同尺寸的任务（`allow_duplicate`）。如仍异常，请确认输入为图片文件。

### Q: 更新检查无响应或下载失败
A: 非商店版通过 GitHub Release 下载安装包，请确认网络可访问 GitHub。商店版会跳转浏览器打开 Release 页面。

### Q: macOS 首次打开提示无法验证开发者
A: 应用未签名，首次打开请右键 → 打开，或在终端执行 `xattr -dr com.apple.quarantine /Applications/Easy-FFmpeg.app`。

---

## 技术栈

- **UI 框架**：PySide6 + QFluentWidgets（Fluent 设计）
- **视频处理**：FFmpeg
- **任务存储**：SQLite
- **配置存储**：JSON
- **打包**：Nuitka
- **安装包**：Inno Setup（Windows）
- **包管理**：uv（推荐）

---

## 贡献指南

1. Fork 本仓库
2. 创建特性分支（`git checkout -b feature/AmazingFeature`）
3. 提交更改（`git commit -m 'Add AmazingFeature'`）
4. 推送到分支（`git push origin feature/AmazingFeature`）
5. 开启 Pull Request

---

## 许可证

本项目采用 [GPL v3](LICENSE) 许可证。

---

## 致谢

- UI 组件基于 [PySide6-Fluent-Widgets-Pro](https://github.com/Fairy-Oracle-Sanctuary/PySide6-Fluent-Widgets-Pro)（Fork 自 [PyQt-Fluent-Widgets](https://github.com/zhiyiYo/PyQt-Fluent-Widgets) 并在此基础上修改）
- 视频处理基于 [FFmpeg](https://ffmpeg.org/)

---

<a href="https://github.com/Fairy-Oracle-Sanctuary/Easy-FFmpeg/graphs/contributors"> <img src="https://contrib.rocks/image?repo=Fairy-Oracle-Sanctuary/Easy-FFmpeg" /> </a>

## Star History

<a href="https://www.star-history.com/?repos=Fairy-Oracle-Sanctuary%2FEasy-FFmpeg&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=Fairy-Oracle-Sanctuary/Easy-FFmpeg&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=Fairy-Oracle-Sanctuary/Easy-FFmpeg&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/chart?repos=Fairy-Oracle-Sanctuary/Easy-FFmpeg&type=date&legend=top-left" />
 </picture>
</a>
