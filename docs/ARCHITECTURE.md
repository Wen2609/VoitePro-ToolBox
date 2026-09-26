# VioletToolBox 架构文档（ARCHITECTURE.md）

> **面向对象**：AI Agent / 新加入的开发者。本文档描述项目的**完整架构**——目录职责、UI 架构、逻辑架构、关键机制、扩展指南与决策记录。
> **快速避坑**：请配合根目录 [`AI_NOTES.md`](../AI_NOTES.md) 阅读（含全部踩坑记录）。
> 版本：2026-09-26 · 对应 v3.6+ UI 重构后状态

---

## 1. 项目定位

**紫罗兰工具箱（VioletToolBox）**：面向 Android 设备的多功能"搞机/刷机"工具箱，约 110 项功能，覆盖高通 EDL 刷机、Fastboot 刷入、线刷、降级、投屏、备份、模块管理等。

**目标用户**：刷机爱好者 / 维修工程师。**非普通消费者软件**，大量功能依赖 adb/fastboot 与设备底层协议。

---

## 2. 技术栈

| 层 | 选型 | 说明 |
|---|---|---|
| 语言/运行时 | C# / .NET 8.0 (net8.0-windows) | WPF 桌面应用 |
| UI 框架 | WPF + HandyControl 3.5.1 | 侧边栏/窗口/控件基础 |
| 图标 | SharpVectors（SVG 渲染） | `images/*.svg` |
| 二进制工具 | adb/fastboot (platform-tools)、fh_loader、QSaharaServer、magiskboot、aapt | EDL/Fastboot 底层交互 |
| 刷机协议 | SharpEDL、Sahara 协议、ofp/ops 解包 | EDL 9008 模式 |

---

## 3. 目录结构与职责

```
VioletToolBox/                    # ★ 仓库根
├── VioletToolBox.sln             # 解决方案
├── README.md                     # 项目说明（多语言见 docs/）
├── LICENSE                       # 开源许可证
├── CONTRIBUTING.md               # 贡献指南
├── CHANGELOG.md                  # 变更日志
├── .gitignore / .gitattributes   # Git 规则
├── AI_NOTES.md                   # ★ AI 接手必读：坑点清单
├── docs/                         # 文档（README 多语言翻译）
├── scripts/
│   └── dev/                      # 开发调试脚本（截图/DPI 检查等）
├── archive/                      # 历史归档（不进 Git，本地保留）
│   ├── backups/                  #   MainWindow 历史 .bak
│   ├── tools/                    #   临时脚本/C# 探针
│   ├── screenshots/              #   页面截图素材
│   └── buildlogs/                #   编译日志
├── release/                      # 发行包（不进 Git，发布到 GitHub Releases）
│
└── VioletToolBox/                # ★ 工程源码（.NET 项目根）
    ├── SmartTool.csproj          #   工程文件（产物名 VioletToolBox）
    ├── App.xaml / App.xaml.cs    #   应用入口/全局资源
    ├── MainWindow.xaml           #   ★ 全部 UI（约 10300 行，17 个页面 View）
    ├── MainWindow.xaml.cs        #   ★ 主窗口逻辑（约 21300 行）
    ├── MainWindow.<功能>.cs      #   分部类：EdlFlash / Payload / BackupAssistant /
    │                             #   SuperRepair / VioletDownload / HiddenEnvironment /
    │                             #   OnePlusAutoRoot / ColorOSAssistant / FastbootGpt /
    │                             #   EdlSession / EdlDynamicSuper / EdlFeedback /
    │                             #   BroadcastNotice / Localization
    ├── *.cs                      #   独立工具类：DowngradeTool / RomDownload /
    │                             #   oujiaflash / OppoOfpExtractor / OnePlusOpsExtractor /
    │                             #   OfpSegmentedSuperMerger / SuperMaker / FilteredOpenFileDialog
    ├── fonts/OPPO_Sans_4.0.ttf   #   UI 字体（完整版 21.72MB，勿子集化）
    ├── images/*.svg              #   侧边栏/页面图标
    ├── Themes/                   #   HandyControl 主题资源
    ├── platform-tools/           #   adb / fastboot
    ├── fh_loader.exe / QSaharaServer.exe / magiskboot.exe / aapt-arm-pie
    ├── KernelPatch/ LKM_Patch/   #   内核补丁工具
    ├── EdlDynamicSuper/ SuperRepair/ Payload_Dumper_C#/  # 分区/解包子模块
    ├── Protos/ Avb/ avbtool/     #   协议/签名工具
    └── bin/Debug/net8.0-windows/VioletToolBox.exe   # 构建产物
```

---

## 4. UI 架构

### 4.1 窗口结构（MainWindow.xaml）

```
Window (1000x800, 硬编码)
├── WindowChrome（无边框自定义顶栏）
│   ├── 顶栏：标题 + 最小化/最大化/关闭（无程序图标）
│   ├── SideMenuControl（hc:SideMenu, 列宽 180px）
│   │   ├── 分组头：FlashFeatureGroup / UtilityGroup / ResourceGroup（可折叠，箭头在左）
│   │   ├── 一级项：主页 / 投屏 / 关于…
│   │   └── 子项：基本刷入 / 可视刷写 / EDL刷写 / …
│   └── ScrollViewer（主内容区, Margin="5,20,20,12"）★ 关键
│       └── Grid（★ Stretch，勿加 VerticalAlignment=Top）
│           ├── HomeView / ScreenMirrorView / EdlFlashView / …（17 个页面，Visibility 切换）
│           └── LoadingOverlay（启动遮罩）
```

### 4.2 页面清单（17 个导航项 → View）

| 分组 | 导航项 | View Name | 核心职责 |
|---|---|---|---|
| （顶层） | 主页 | `HomeView` | 设备状态、快捷重启/工具、设备检测 |
| （顶层） | 投屏 | `ScreenMirrorView` | scrcpy 投屏控制 |
| 刷写功能 | 基本刷入 | `BasicFlashView` | Fastboot 刷镜像/解锁 |
| 刷写功能 | 可视刷写 | `FastbootVisualizationView` | 分区可视化读写 |
| 刷写功能 | 欧加线刷 | `OujiaFlashView` | 一加/OPPO/真我线刷 |
| 刷写功能 | EDL刷写 | `EdlFlashView` | 高通 9008 EDL 刷写 |
| 刷写功能 | 降级助手 | `DowngradeAssistantView` | 系统降级 |
| 实用功能 | 模块专区 | `ModuleZoneView` | 模块管理 |
| 实用功能 | 断点续传 | `ResumeTransferView` | 文件传输续传 |
| 实用功能 | 文件传输 | `FileTransferView` | ADB 文件传输 |
| 实用功能 | 脱机修补 | `OfflinePatchView` | 离线修补 |
| 实用功能 | 应用管理 | `AppManagementView` | 应用安装/管理 |
| 实用功能 | 安卓通用 | `AndroidGeneralView` | 通用 ADB 功能 |
| 刷机资源 | Payload | `PayloadView` | Payload 解包 |
| 刷机资源 | 备份助手 | `BackupAssistantView` | 数据备份 |
| 刷机资源 | 隐藏环境 | `HiddenEnvironmentView` | 隐藏功能 |
| 刷机资源 | 系统专区 | `SystemZoneView` | 系统级操作 |
| （顶层） | 关于 | `AboutView` | 版本/反馈 |

### 4.3 关键布局约束（曾踩坑，见 AI_NOTES.md 坑 1/4/5/6）
1. 主内容 ScrollViewer 子 Grid **必须 Stretch**——否则所有 `*` 行塌缩、进度条不贴底。
2. GroupBox 自定义模板（`EdlCardGroupBoxStyle`）内容 `Padding="10,32,10,10"`——Header 浮顶需 32px 空间。
3. 禁负边距（文字被切）；页面内禁套 ScrollViewer（滚动交给外层）。

---

## 5. 逻辑架构

### 5.1 分层

```
UI 层（MainWindow.xaml + 事件处理器）
   │  事件/属性绑定
逻辑层（MainWindow.xaml.cs + 分部类）
   │  （adb/fastboot 命令组装、状态机）
工具层（*.cs 工具类 + 外部二进制）
   │  （OFP 解包、Payload 解析、EDL 协议、下载）
设备层（platform-tools / SharpEDL / 串口 / USB）
```

### 5.2 核心模块职责

| 模块 | 文件 | 职责 |
|---|---|---|
| EDL 刷写 | `MainWindow.EdlFlash.cs` / `EdlSession.cs` / `EdlDynamicSuper.cs` / `EdlFeedback.cs` | 9008 模式分区读写、进度反馈 |
| 线刷 | `oujiaflash.cs` | 欧加设备线刷（一加/OPPO/真我） |
| Payload | `MainWindow.Payload.cs` / `Payload_Dumper_C#/` | payload.bin 解包 |
| 备份 | `MainWindow.BackupAssistant.cs` | 应用数据备份 |
| 下载 | `VioletDownload.cs` / `Aria2DownloadService.cs` / `RomDownload.cs` | 固件下载 |
| 解包 | `OppoOfpExtractor.cs` / `OnePlusOpsExtractor.cs` / `OfpSegmentedSuperMerger.cs` | OFP/OPS 解包合并 |
| 隐藏环境 | `MainWindow.HiddenEnvironment.cs` | 隐藏功能入口 |
| 本地化 | `MainWindow.Localization.cs` | 多语言 |
| 提示 | `MainWindow.BroadcastNotice.cs` | 公告/弹窗 |

### 5.3 页面切换机制（两套并存，改动需同步）
1. `DirectItem_PreviewMouseLeftButtonUp`：侧边栏一级项点击 → 清其他选中 → 切 View。
2. `SideMenu_SelectionChanged`：switch 分发 → 切 View。
3. 分组折叠：`GroupHeader_Click` → `ToggleGroup(name)` 手动切换子项 `Visibility`（`_groupItems` 字典定义归属，`_groupExpanded` 记录状态）。

---

## 6. 关键机制详解

### 6.1 侧边栏分组（HandyControl SideMenu 特殊用法）
- 分组头与子项是 **SideMenu 平级节点**，非嵌套。
- 子项 `Visibility` 由代码手动控制（默认折叠）。
- 分组头是 `DockPanel`：箭头（RotateTransform 0↔180）+ 文字，箭头在**左侧**。
- 新增分组：`MainWindow.xaml.cs` 的 `_groupItems` 字典加映射 + XAML 加分组头/子项。

### 6.2 字体体系
- 全部 UI 字体：`pack://siteoforigin:,,,/fonts/OPPO_Sans_4.0.ttf#OPPO Sans 4.0`（完整 pack 路径，简写无效）。
- 日志/代码框保留等宽栈：`Cascadia Mono,OPPO Sans,Consolas`。
- 字体文件必须是完整版（子集版会导致启动黑屏）。

### 6.3 主题色（用户最终确认）
| Token | 值 | 用途 |
|---|---|---|
| 主蓝 | `#FF0A84FF` | 选中/主按钮/进度 |
| 浅蓝底 | `#FFE0EFFF` | 选中项底色/标签 |
| 悬停 | `#FFF0F7FF` | 悬停底色 |
| 深蓝文字 | `#FF09488A` | 强调文字 |
| 正文 | `#FF1D1D1F` | 主要文字 |
| 次级 | `#FF8E8E93` | 次要文字/占位 |
| 卡片 | `#FFFFFFFF` | 卡片背景 |

### 6.4 窗口
- 无边框（WindowChrome），自定义顶栏：白底、无图标、最小化/最大化/关闭。
- `Border_MouseLeftButtonDown` 拖动（`IsOnButton` 判断避免吞按钮）。
- 尺寸 1000x800 硬编码（XAML + 构造函数双处）。
- 关闭**不清理**运行痕迹。

### 6.5 启动时序
1. XAML 解析（大文件，约 1~2 秒）→ 窗口显示。
2. `Loaded` → `Dispatcher.BeginInvoke`：150ms 后设置分组 Role/折叠、选中主页 → 80ms 后隐藏 LoadingOverlay。
3. 完整可交互约需 20~30 秒（HandyControl 异步 + 大 XAML）。

---

## 7. 构建与运行

```powershell
# 依赖：.NET 8 SDK（C:\Program Files\dotnet\dotnet.exe）
taskkill /F /IM VioletToolBox.exe 2>$null   # 先杀进程
Set-Location VioletToolBox\VioletToolBox
dotnet build SmartTool.csproj --configuration Debug -v minimal
# 期望输出：0 个错误；耗时 20~90 秒（首次）或 3 秒（增量）

# 运行（工作目录必须是 exe 所在目录，否则找不到 fonts/images）
Start-Process .\bin\Debug\net8.0-windows\VioletToolBox.exe -WorkingDirectory .\bin\Debug\net8.0-windows
```

---

## 8. 扩展指南

### 8.1 新增一个页面（示例：加"XX工具"）
1. **XAML**：`MainWindow.xaml` 中新增 `<Grid x:Name="XxView" Visibility="Collapsed">`（复制现有页面结构，注意布局约束：Stretch、Padding 32、无负边距、无内层 ScrollViewer）。
2. **侧边栏**：在目标分组下加 `<hc:SideMenuItem Header="XX工具" PreviewMouseLeftButtonUp="DirectItem_PreviewMouseLeftButtonUp">`（一级项）或加入 `_groupItems`（子项）。
3. **代码**：`MainWindow.xaml.cs` 的 `DirectItem_PreviewMouseLeftButtonUp` / `SideMenu_SelectionChanged` 的 switch 加 case，切换 Visibility。
4. **逻辑**：新功能逻辑放 `MainWindow.<功能>.cs` 分部类。
5. **图标**：SVG 放 `images/`，`<svg:SvgViewbox Source="images/xx.svg"/>`。
6. **验证**：编译 → 启动 → BitBlt 截图（方法见 AI_NOTES.md 坑 9）。

### 8.2 修改 UI 的禁止项（红线）
- ❌ 外层容器 Grid 加 `VerticalAlignment="Top"`
- ❌ 字体简写（必须完整 pack 路径）
- ❌ 替换/子集化字体文件
- ❌ 负边距、页面内 ScrollViewer
- ❌ 给页面加 VerticalAlignment=Top（破坏 Stretch 撑满）

### 8.3 调试工具
- `scripts/dev/cap*.ps1`：窗口截图（BitBlt）。
- `scripts/dev/check_dpi.ps1`：DPI 检查。
- 验证点击：PostMessage 模拟（见 AI_NOTES.md 坑 9）。

---

## 9. 决策记录（ADR 摘要）

| # | 决策 | 原因 | 备注 |
|---|---|---|---|
| 1 | 单文件 MainWindow.xaml（10300 行） | 继承原项目结构，避免大重构风险 | 未来可拆分 UserControl |
| 2 | 页面 Visibility 切换而非 ContentControl | 原项目结构，改动最小 | 启动慢的根因之一，未来可懒加载 |
| 3 | 窗口尺寸硬编码 1000x800 | SystemParameters.WorkArea 在某些会话返回极小值 → 58x30 窗口 | 勿恢复适配逻辑 |
| 4 | 字体完整版 21.72MB 随包分发 | 子集版导致启动黑屏 | 勿优化体积 |
| 5 | 主题色 iOS 蓝 #0A84FF | 用户明确选择（拒绝紫色/黑白） | 见 §6.3 |
| 6 | 关闭不清理运行痕迹 | 用户要求 | — |
| 7 | 侧边栏分组折叠默认收起 | 17 项全展开超窗口高度 | 行高 40px 可压缩 |

---

## 10. 开源状态与合规

- **许可证**：`LICENSE`（GPL-3.0，见文件头）。
- **第三方依赖**：HandyControl (MIT)、SharpVectors (BSD)、Newtonsoft.Json (MIT)、Google.Protobuf (BSD)、BouncyCastle (MIT)、ZstdSharp (MIT)、SharpCompress (MIT)。二进制工具（adb/fastboot、magiskboot、aapt）各自许可，随包分发需保留原许可声明。
- **含第三方工具二进制**：KernelPatch/LKM_Patch 的 .ko 与 ksud.exe 已随仓库分发（开源项目，许可证见各子目录）。
- **release/** 与 **archive/** 不进 Git 仓库（已加入 .gitignore）；正式发行包发布到 GitHub Releases。

---

## 11. 已知问题 / 技术债

1. MainWindow.xaml 单文件过大 → 加载慢（20~30 秒可交互）。
2. 两套侧边栏分发（DirectItem + SelectionChanged）逻辑重复。
3. 事件处理器命名混乱（`CheckBox_Checked_3` 等），重构需先确认引用。
4. 部分页面按钮高度不统一（如基本刷入"执行指令"60px）。
5. 首页设备信息卡片等区域在无设备时显示占位符，无空态视觉设计。
6. 多语言仅 README 层，应用内 Localization 分部类是否完整未审计。

---

## 12. 快速上手（给新 AI 的 5 分钟路线）

1. 读 `AI_NOTES.md`（坑点）→ 本文档 §4/§5（架构）。
2. 打开 `MainWindow.xaml` 用 Ctrl+F 定位页面 View（如 `EdlFlashView`）。
3. 改 UI → 按 §7 编译 → 按 AI_NOTES.md 坑 9 截图验证。
4. 改侧边栏/页面切换 → 同步 `DirectItem_PreviewMouseLeftButtonUp` 与 `SideMenu_SelectionChanged`。
5. 提交 PR：遵循 CONTRIBUTING.md。
