# 变更日志（CHANGELOG）

本项目遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 与 [Semantic Versioning](https://semver.org/lang/zh-CN/)。

## [未发布] - UI 重构与打磨（基于 v3.6 源码）

### 新增
- 顶栏：白底无边框自定义窗口，增加**最大化**按钮（最小化/最大化/关闭）。
- 侧边栏：分组**折叠/展开**功能（FlashFeatureGroup / UtilityGroup / ResourceGroup），分组箭头位于**名称左侧**，默认全部折叠。
- 侧边栏选中项：圆角蓝色胶囊高亮（无左侧竖条指示条）。
- 首页快捷操作区（快捷重启 / 快捷工具 / 设备检测开关）。
- 全部 17 个页面完成 UI 重做与布局修复。

### 变更
- **主题色**：由原紫/黑白色改为 **iOS 蓝** 主题（主蓝 `#0A84FF`、浅蓝底 `#E0EFFF`、悬停 `#F0F7FF`、深蓝文字 `#09488A`）。
- **字体**：全应用统一为 **OPPO Sans 4.0**（完整 pack://siteoforigin 路径加载），日志区保留 Cascadia Mono 等宽栈。
- 侧边栏宽度 160px → 180px。
- 窗口尺寸固定 1000x800（移除失效的系统工作区适配逻辑）。
- 移除程序图标于顶栏；关闭程序**不清理**工具运行痕迹。
- 外层内容容器 Grid 去除 `VerticalAlignment="Top"`——修复所有页面 `*` 行塌缩、进度条不贴底问题。
- EDL 页文件选择卡片行高 180px → Auto（自适应，防止输入行溢出）。
- GroupBox 卡片 Padding 顶部统一 32px（防止 Header 遮挡内容）。
- 清除多处负边距（`-9`/`-20` 等，防止文字被窗口边缘裁切）。

### 修复
- 部分页面按钮/字体被遮挡、偏移错位。
- 部分页面无法下滑（内外层 ScrollViewer 冲突）。
- EDL 页「云端引导/存储器/串口」输入行溢出。
- 页面切换需点两次才生效（改为 PreviewMouseLeftButtonUp 先行清选）。
- 移除侧边栏点击调试日志与 click_log.txt 输出。

### 开发体验
- 新增 `AI_NOTES.md`（坑点记忆，供 AI/开发者快速避坑）。
- 新增 `docs/ARCHITECTURE.md`（架构说明与扩展指南）。
- 新增 `CONTRIBUTING.md`（贡献指南）。
- 目录规范化：脚本入 `scripts/dev/`，历史备份/截图/日志入 `archive/`（不进 Git）。

## [3.6] - 2026-09-12（上游发行版基线）

- 上游项目原始版本（GitHub: Smart-Paocai/VioletToolBox）。
- 本仓库自该版本源码 + 发行包合并后开始 UI 重构。
