# VoitePro Tool Box

**紫罗兰工具箱（VioletToolBox）重构版** —— 面向安卓设备的刷机/线刷工具箱。

基于 [Smart-Paocai/VioletToolBox](https://github.com/Smart-Paocai/VioletToolBox) 源码的深度 UI 重构与性能优化版本：全新的 iOS 风格蓝主题、Noto Sans SC 子集字体（OFL 商用免费）、分组折叠侧边栏、按需懒加载页面，启动与运行时流畅度大幅提升。

> 📌 **AI/开发者提示**：接手本项目的 AI 或开发者，请先阅读：
> - **[AI_NOTES.md](AI_NOTES.md)** — 踩坑记录（字体/布局/滚动/分组机制/调试方法）
> - **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** — 架构说明与扩展指南
> - **[CONTRIBUTING.md](CONTRIBUTING.md)** — 贡献指南
> - **[CHANGELOG.md](CHANGELOG.md)** — 变更日志

## 功能一览

- **刷写功能**
  - **基本刷入**：分区镜像刷入（boot/init_boot）、Bootloader 解锁回锁、小米官方线刷、扩展功能（双清/擦除谷歌锁/修复ADB/强开USB安全/一加DDR/基带调试端口/文件传输/OCDT分析）
  - **可视刷写**：Fastboot 分区可视化读写，ADB/FB 模式读取分区表，读写擦备份 GPT，XML 刷写脚本生成，Slot A 模式
  - **欧加线刷**：一加/真我/OPPO 线刷，全量包模式（强力线刷/AB通刷/仅FBD/修复FastbootD/ARB熔断检测/修复Super真死/Payload解包）与售后包模式
  - **EDL 刷写**：高通 9008 紧急下载模式（精简版保留入口，模块待后续版本）
  - **降级助手**：ColorOS 固件下载与 OTA 降级
- **实用功能**
  - **模块专区**：Magisk 与隐藏环境（隐藏 ROOT、快捷安装 Momo/密钥认证/Hunter 等检测项、模块拖放安装）
  - **断点续传**：多线程下载 OTA 全量包
  - **文件传输**：ADB 批量传/收文件、批量安装 APK
  - **脱机修补**：boot 镜像离线修补、一加全自动 ROOT、制作 GKI 镜像、联想 AVB 签名
  - **应用管理**：冻结/解冻、提取 APK、清除数据、卸载
  - **安卓通用**：合并 OPLUS Super、解包 OFP/OPS、TWRP 分区操作、OCDT 生成
  - **Payload**：全量包 ZIP 信息可视化与按需提取
- **刷机资源**
  - **备份助手**：图片/视频/通讯录在线备份
  - **Rom 专区**：OPPO/OPLUS/realme/魅族/联想/小米/Redmi OTA 卡刷包、线刷包与 Boot 镜像
  - **下载专区**：断点续传下载
- **关于**：软件信息

## 技术栈

- **框架**：WPF（.NET 8.0-windows）
- **主题**：iOS 风格蓝主题（主色 `#0A84FF`、浅蓝底 `#E0EFFF`、悬停 `#F0F7FF`）
- **字体**：Noto Sans SC（SIL OFL 开源商用，按程序字符集子集化后 0.8MB，内置 `fonts/NotoSansSC-Sub.otf`）
- **图标**：SVG 图标（`SvgViewbox`）
- **性能**：16 个页面按需懒加载（DataTemplate + ContentControl PageHost）、控件缓存、WMI 异步枚举、硬件加速（移除透明窗口）、启动约 2s

## 构建

```bash
dotnet restore VioletToolBox/SmartTool.csproj
dotnet build VioletToolBox/SmartTool.csproj -c Debug
```

运行产物：`VioletToolBox/bin/Debug/net8.0-windows/VioletToolBox.exe`

## 项目结构

```
VioletToolBox/
├── VioletToolBox/          # 主工程（SmartTool.csproj）
│   ├── MainWindow.xaml     # 主界面 + 16 个页面模板
│   ├── MainWindow.xaml.cs  # 逻辑代码
│   ├── fonts/              # Noto Sans SC 子集字体
│   └── images/             # SVG 图标
├── docs/                   # 架构/贡献文档
├── scripts/                # 开发辅助脚本
├── AI_NOTES.md             # AI 协作开发约定
└── CHANGELOG.md            # 变更记录
```

## 许可证

本项目基于 [Smart-Paocai/VioletToolBox](https://github.com/Smart-Paocai/VioletToolBox) 派生，采用 **GNU General Public License v3.0（GPL-3.0）**，详见 [LICENSE](LICENSE)。

## 免责声明

刷机有风险，使用前请备份重要数据；本工具仅供学习与开发研究使用。
