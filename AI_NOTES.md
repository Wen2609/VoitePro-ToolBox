# VioletToolBox 项目 AI 记忆笔记（AI_NOTES）

> 本文件供 **任何后续 AI / 开发者** 快速接手本项目时阅读。
> 记录了：项目概况、构建方式、**所有踩过的坑（根因+修复+防复发）**、UI 设计约束、调试方法。
> 更新时间：2026-09-26。改代码前请先读本文件，尤其是「坑点清单」部分。

---

## 1. 项目概况

| 项 | 值 |
|---|---|
| 产品名 | 紫罗兰工具箱（VioletToolBox） |
| 用途 | 高通 Android 设备刷机/救砖/玩机工具（EDL、Fastboot、线刷、投屏、备份等） |
| 技术栈 | C# / WPF / .NET 8.0-windows / HandyControl 3.5.1 / SharpVectors(SVG) |
| 工程文件 | `SmartTool.csproj`（sln：`VioletToolBox.sln`） |
| UI 结构 | 单个巨型 `MainWindow.xaml`（约 10300 行，17 个页面 View）+ `MainWindow.xaml.cs`（约 21300 行）+ 功能分部类 `MainWindow.*.cs` |
| 窗口尺寸 | 硬编码 `Width=1000, Height=800`（XAML 根 + 构造函数两处） |

### 关键路径
- 工程目录：`VioletToolBox\`（含 `.csproj`）
- 产物 exe：`VioletToolBox\bin\Debug\net8.0-windows\VioletToolBox.exe`
- 字体：`VioletToolBox\fonts\OPPO_Sans_4.0.ttf`（完整版 21.72MB，**勿用子集版**）
- 图标 SVG：`VioletToolBox\images\*.svg`
- 发行包：`release\`；历史备份/脚本/截图：根目录 `_archive_*`（只读归档，勿动）

---

## 2. 构建与启动

```powershell
# 先杀进程（避免 exe 被占用编译失败）
taskkill /F /IM VioletToolBox.exe

# 在工程目录编译
Set-Location "D:\doubao space\VioletToolBox\VioletToolBox"
& "C:\Program Files\dotnet\dotnet.exe" build SmartTool.csproj --configuration Debug -v minimal
# 正常耗时 20~90 秒，输出「0 个错误」为成功

# 启动（必须以工作目录=exe 目录启动，否则找不到 fonts/images）
Start-Process $exe -WorkingDirectory (Split-Path $exe)
# 首次窗口完全渲染需 20~30 秒（HandyControl 异步加载 + 大 XAML 解析）
```

⚠️ **启动后必须等 20~30 秒再截图/交互**，否则可能截到加载遮罩层或空白。

---

## 3. 坑点清单（按重要度排序，每条都真实踩过）

### 🔴 坑 1：外层容器 Grid `VerticalAlignment="Top"` 导致所有页面 `*` 行塌缩
- **现象**：EDL/可视刷写等页面内容挤在上半部分，下半部分大片空白，进度条、底部按钮不贴底；用户原话「进度条不应该在窗口正下方吗」。
- **根因**：主内容 `ScrollViewer`（约 L852）给子元素**无限高度**约束。外层容器 `<Grid VerticalAlignment="Top">` 使 Grid 高度=内容高度，内部所有 `RowDefinition Height="*"` 在无限高度下塌缩为最小高度。
- **修复**：外层容器 Grid 去掉 `VerticalAlignment="Top"`（默认 Stretch），ScrollViewer 视口 > 内容时 Grid 填满视口，`*` 行正常分配。
- **防复发**：⚠️ **不要给外层容器 Grid 加回 VerticalAlignment="Top"**。页面内部若要用 `*` 行撑满高度，保持该页 View 为 Stretch（不要加 Top）。

### 🔴 坑 2：WPF 字体必须用完整 `pack://` 路径，简写字体名无效
- **现象**：界面字体不统一、回退系统默认字体（用户反复抱怨「字体没体现」）。
- **根因**：`FontFamily="OPPO Sans 4.0"` 这种简写，WPF 找不到应用内字体资源时静默回退。
- **修复**：统一替换为完整路径：
  ```
  FontFamily="pack://siteoforigin:,,,/fonts/OPPO_Sans_4.0.ttf#OPPO Sans 4.0"
  ```
- **范围**：XAML 中所有 `FontFamily="OPPO Sans 4.0"`（35+ 处）和 `<Setter Property="FontFamily" Value="Microsoft YaHei UI"/>`（16 处，EDL 等页面 GroupBox 样式）都已替换。
- **例外**：日志/代码框保留 `Cascadia Mono,pack://...OPPO Sans...,Consolas` 字体栈是**合理**的（等宽日志），不要替换成纯 OPPO Sans。

### 🔴 坑 3：OPPO Sans 字体子集化会导致窗口初始化异常
- **现象**：程序启动后黑屏/窗口无内容/崩溃。
- **根因**：之前用过 4.38MB 的子集化字体文件，字体不完整引发 WPF 初始化异常。
- **修复**：用完整版 `fonts\OPPO_Sans_4.0.ttf`（21.72MB）。备份在 `fonts\OPPO_Sans_4.0_full.ttf.bak`（归档目录也有）。
- **防复发**：**不要**为省体积替换成子集字体。若必须子集化，先完整验证启动。

### 🟠 坑 4：GroupBox 自定义模板 Header 浮顶会遮挡内容
- **现象**：EDL 页「文件选择」卡片顶部输入框被 Header 遮住/切掉。
- **根因**：`PayloadGroupBoxStyle` 模板的 Header 用 `Margin="10,-8,0,0"` 浮在卡片顶部，若内容 `Padding` 只给 `10`，Header 与内容重叠。
- **修复**：卡片样式 `Padding` 改为 `10,32,10,10`（顶部 32px 留给 Header）。EDL 页 `EdlCardGroupBoxStyle` 已改。
- **防复发**：新建 GroupBox 卡片时，顶部 Padding 必须 ≥32px，或用完整高度行（`Height="Auto"`）。

### 🟠 坑 5：负边距导致左侧文字被窗口边缘切掉
- **现象**：EDL 页「端引导/UFI」等文字左半边被切。
- **根因**：`Margin="-9,0,0,0"`（以及 -20/-31 等）把元素拉出容器左边界。
- **修复**：全部归零（`-9→0` 等，涉及 EDL、下载页、文件列表页多处）。
- **防复发**：不要再用负左边距做「视觉对齐」，用正 Margin 或 Grid 列宽控制。

### 🟠 坑 6：ScrollViewer 双层嵌套导致滚动/测量异常
- **现象**：部分页面无法下滑、内容测量错误、底部空白。
- **处理**：主页内层 ScrollViewer 标签已删除；其他页面内层 ScrollViewer 从 Auto 改 Disabled；外层主内容 ScrollViewer（约 L852）`VerticalScrollBarVisibility="Visible"` 强制显示。
- **防复发**：页面内不要再套 ScrollViewer；滚动交给外层统一处理。

### 🟠 坑 7：HandyControl SideMenu 分组是「兄弟节点 + 手动 Visibility」，不是嵌套结构
- **现象**：早期误以为分组子项要嵌进分组节点，导致「分组无法展开」误判（实际是自动化测试坐标错误，功能一直正常）。
- **实际机制**：
  - 分组标题（`FlashFeatureGroup` / `UtilityGroup` / `ResourceGroup`）与子项在 `hc:SideMenu` 中**平级**。
  - 展开/折叠由 `GroupHeader_Click` → `ToggleGroup(name)` 手动切换子项 `Visibility`（字典 `_groupItems` 定义归属，`_groupExpanded` 记录状态）。
  - 分组标题 Header 是 `DockPanel`（箭头图标 + 文字），箭头 `RotateTransform` 0/180 随状态旋转。箭头在**分组名左侧**（用户要求）。
  - 启动时（Loaded 后 Dispatcher.BeginInvoke）设 `Role=Header` 并默认全折叠。
- **防复发**：**不要**把子项改成 SideMenuItem 嵌套结构（会破坏现有 ToggleGroup 逻辑）；新增分组只需在 `_groupItems` 加一条映射。

### 🟠 坑 8：窗口尺寸硬编码，勿启用系统工作区适配
- **现象**：早期用 `SystemParameters.WorkArea` 适配屏幕，某些会话返回极小值导致窗口 58x30。
- **修复**：XAML 根 + 构造函数双处硬编码 `1000x800`。
- **防复发**：**不要**重新启用 WorkArea 适配逻辑。

### 🟡 坑 9：截图调试方法论（本机环境特殊性）
- 目标窗口：`EnumWindows` 遍历找标题含「紫罗兰」的 hwnd（`GetProcess` 的 MainWindowHandle 是 58x30 的辅助窗口，不可用）。
- 截图：`BitBlt` 从屏幕 DC 抓取（`PrintWindow` 对 `AllowsTransparency=True` 的 WPF 窗口截到全黑）。
- **OCR 坐标是千分比（0~1000）不是像素**！换算：`y_px = y_permil × 窗口高 / 1000`。这是多次点击「无效/错位」的根因。
- 窗口被其他窗口遮挡时截到别人的界面；本机 **360tray 会抢前台锁**，`SetForegroundWindow` 可能失败。
- 可靠交互方式：`PostMessage(hwnd, WM_LBUTTONDOWN/UP, MK_LBUTTON, (y<<16)|x)` 直接给目标窗口发消息，绕开前台锁与 360 拦截。
- 侧边栏滚轮：`PostMessage(WM_MOUSEWHEEL)` 不一定触发 WPF 滚轮（真实鼠标滚轮正常）。

### 🟡 坑 10：UI 设计硬约束（用户明确要求/拒绝）
- ✅ **主题色**：iOS 蓝 `#FF0A84FF`；浅蓝 `#FFE0EFFF`；悬停 `#FFF0F7FF`；深蓝文字 `#FF09488A`；正文黑 `#1D1D1F`；次要灰 `#FF8E8E93`。
- ✅ **字体**：OPPO Sans 4.0（完整 pack 路径）。
- ✅ 顶栏：白色、无程序图标（用户要求去掉）、含最小化/最大化/关闭三按钮；`Border_MouseLeftButtonDown` 拖动窗口（有 `IsOnButton` 判断避免拖拽吞按钮点击）。
- ✅ 窗口按钮顺序：最小化「—」、最大化「□」、关闭「×」，悬停蓝底。
- ✅ 关闭程序**不清理**工具运行痕迹（用户要求）。
- ❌ **拒绝**：紫色主题、Mac 风格顶栏、底部状态栏（底栏）、黑白纯色主题（早期版本，已弃用）。
- ✅ 侧边栏：蓝色圆角分组箭头（左侧）、选中项圆角蓝底无左侧竖条、分组可折叠。
- ⚠️ 侧边栏行高约 40px（`Margin="6,2"` + `Padding="10,8"` + 图标 40x20），全分组展开后内容超出 800px 窗口需滚动——如需优化可压缩行高至 34px，但需重测点击热区。

### 🟡 坑 11：启动时窗口渲染慢 + 加载遮罩
- 窗口加载时有 `LoadingOverlay` 遮罩，`Dispatcher.BeginInvoke` 延迟隐藏（150ms 后设 Role/折叠分组/选主页，再 80ms 隐藏遮罩）。
- 改启动逻辑时注意不要破坏遮罩隐藏时序。

### 🟡 坑 12：SideMenu 点击事件
- 一级项：`PreviewMouseLeftButtonUp="DirectItem_PreviewMouseLeftButtonUp"`（先清其他选中再切页面，解决「点两次才生效」）。
- 分组头：`PreviewMouseLeftButtonDown="GroupHeader_Click"`。
- `SideMenu_SelectionChanged` 也有 switch 分发（两套分发并存，改页面切换时两处都要同步）。

---

## 4. 整理后的文件结构

```
D:\doubao space\VioletToolBox\
├── VioletToolBox.sln
├── README.md                  # 原项目说明
├── LICENSE
├── page_manifest.json         # 页面清单（旧）
├── 紫罗兰工具箱-深度分析报告.html
├── docs\                      # README 多语言翻译（en/ja/ko/vi/zh-TW/hi）
├── release\                   # 发行包（321 文件，84MB）
├── VioletToolBox\             # ★ 工程目录
│   ├── SmartTool.csproj
│   ├── App.xaml / App.xaml.cs
│   ├── MainWindow.xaml        # ★ 全部 UI（17 页面）
│   ├── MainWindow.xaml.cs     # ★ 主逻辑
│   ├── MainWindow.<功能>.cs   # 分部类：EdlFlash / Payload / BackupAssistant / SuperRepair / VioletDownload / HiddenEnvironment / OnePlusAutoRoot / ColorOSAssistant / FastbootGpt / EdlSession / EdlDynamicSuper / EdlFeedback / BroadcastNotice / Localization
│   ├── *.cs                   # 独立工具类：DowngradeTool / RomDownload / oujiaflash / OppoOfpExtractor / OnePlusOpsExtractor / OfpSegmentedSuperMerger / SuperMaker / FilteredOpenFileDialog / RelayCommand / SaharaProgrammerManifest / Aria2DownloadService / HorizontalBattery
│   ├── fonts\OPPO_Sans_4.0.ttf  # 完整字体 21.72MB
│   ├── images\*.svg           # 侧边栏/页面图标
│   ├── Themes\                # HandyControl 主题
│   ├── platform-tools\        # adb/fastboot
│   ├── fh_loader.exe / QSaharaServer.exe / magiskboot.exe / aapt-arm-pie  # EDL/刷机工具
│   ├── *.dll                  # HandyControl / SharpVectors / Newtonsoft / Protobuf 等依赖
│   └── bin\Debug\net8.0-windows\VioletToolBox.exe  # 构建产物
├── _archive_backups\          # MainWindow 历史 .bak（9 个，含原始版）
├── _archive_tools\            # 临时 ps1/cs 脚本 + wpftmp 残留（25 个）
├── _archive_screenshots\      # 页面截图/素材备份（187 个）
└── _archive_buildlogs\        # 编译日志（41 个）
```

⚠️ 归档目录（`_archive_*`）只读保留、勿清理勿移动；工程代码改动只动 `VioletToolBox\`。

---

## 5. 遗留问题 / 未来优化建议

1. **MainWindow.xaml 单文件过大**（10300 行）：未来可拆分为每页一个 UserControl/ResourceDictionary。分部类 cs 已拆，xaml 未拆。
2. **页面 View 全部平铺在同一个 Grid 里**用 Visibility 切换——加载慢的根因之一。可改为 `ContentControl` + 懒加载。
3. **两套侧边栏点击分发**（DirectItem + SelectionChanged switch）存在重复，后续重构可合并，但改动风险高（页面切换逻辑耦合）。
4. **命名/事件处理混乱**：如 `CheckBox_Checked_3`、多个 TextChanged 处理器，重构时先确认引用关系。
5. 部分页面（基本刷入「执行指令」按钮 60px 高）存在按钮高度不统一，如再打磨可按 32/36px 统一。
6. **验证截图脚本**（归档在 `_archive_tools\`）：`cap*.ps1` / `scan*.ps1` / BitBlt 方法可复用。

---

## 6. 一句话总结（给新接手的 AI）

> 这是一个 WPF 单体应用，UI 全在 `MainWindow.xaml`。改 UI 时：字体必须用完整 pack 路径、别动外层容器 Grid 的 Stretch、GroupBox Padding 顶部留 32px、别用负边距、别给页面套 ScrollViewer。构建 = taskkill + dotnet build；验证 = BitBlt 截图 + PostMessage 点击（OCR 坐标是千分比，换算后使用）。用户偏好：蓝色 #0A84FF、OPPO Sans、侧边栏分组折叠、不要紫色不要 Mac 风。
