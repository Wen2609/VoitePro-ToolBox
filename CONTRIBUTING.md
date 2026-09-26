# 贡献指南（CONTRIBUTING）

感谢你对 VioletToolBox（紫罗兰工具箱）的兴趣！本指南帮助你和你的 AI 助手高效协作。

## 项目状态

- 这是**单体 WPF 应用**：UI 全部在 `VioletToolBox/MainWindow.xaml`（约 1 万行），逻辑在 `MainWindow.xaml.cs` + 分部类。
- **动手前必读**：根目录 [`AI_NOTES.md`](AI_NOTES.md)（踩坑记录）与 [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)（架构说明）。

## 开发环境

- Windows + .NET 8 SDK
- 无需额外依赖；构建命令见 ARCHITECTURE.md §7

## 工作流

1. **Fork + 分支**：从 `main` 切功能分支，命名 `feat/描述` 或 `fix/描述`。
2. **本地构建验证**：`taskkill /F /IM VioletToolBox.exe` → `dotnet build SmartTool.csproj` → 必须 **0 错误**。
3. **UI 改动必截图验证**：启动后用 `scripts/dev/cap*.ps1` 截图确认布局（方法见 AI_NOTES.md 坑 9）。
4. **提交信息**：中文或英文，说明"改了什么 + 为什么"。示例：
   ```
   fix(edl): 进度条不贴底问题
   
   - 外层容器 Grid 去除 VerticalAlignment=Top（ScrollViewer 无限高度导致 * 行塌缩）
   - 验证：EDL 页内容从 533px 铺到 762px
   ```
5. **PR**：描述改动 + 附前后对比截图（UI 改动必须）。

## 代码红线（违反会被打回）

| 红线 | 原因 |
|---|---|
| 外层容器 Grid 加 `VerticalAlignment="Top"` | 所有 `*` 行塌缩、页面挤上部、底部空白 |
| 字体简写 `FontFamily="OPPO Sans 4.0"` | 静默回退系统字体 |
| 替换/子集化 `fonts/OPPO_Sans_4.0.ttf` | 子集版导致启动黑屏 |
| 页面内套 ScrollViewer | 与外层滚动冲突 |
| 负边距（如 `Margin="-9,0,0,0"`） | 文字被窗口边缘切掉 |
| 给页面 Grid 加 `VerticalAlignment="Top"` | 破坏 Stretch 撑满 |

## 主题与风格约束

- 主题色：主蓝 `#0A84FF`、浅蓝底 `#E0EFFF`、悬停 `#F0F7FF`、深蓝文字 `#09488A`、正文 `#1D1D1F`、次级 `#8E8E93`、卡片白 `#FFFFFF`。
- 字体：OPPO Sans 4.0（完整 pack 路径）。
- 顶栏：白底、无程序图标、最小化/最大化/关闭。
- **拒绝**：紫色主题、Mac 风格顶栏、底部状态栏。

## 提交类型建议

- `feat`：新功能/新页面（按 ARCHITECTURE.md §8.1 流程）
- `fix`：bug 修复（附根因分析）
- `refactor`：重构（先确认两套侧边栏分发等耦合点）
- `docs`：文档（欢迎补充 AI_NOTES.md / ARCHITECTURE.md）

## 发布

- 正式发行包（含 fonts/images/platform-tools 等运行时资源）通过 **GitHub Releases** 发布，不提交 release/ 目录。
- 版本号维护在 `VioletToolBox/Version.json`。
