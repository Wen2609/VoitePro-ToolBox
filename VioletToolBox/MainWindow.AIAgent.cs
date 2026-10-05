using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Threading;

namespace WpfApp1
{
    /// <summary>AI 对话消息（支持流式更新）</summary>
    public sealed class AgentChatMessage : INotifyPropertyChanged
    {
        private string _text = "";

        public string Role { get; set; } = "assistant";

        public string Text
        {
            get => _text;
            set
            {
                if (_text != value)
                {
                    _text = value;
                    PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(nameof(Text)));
                }
            }
        }

        public event PropertyChangedEventHandler? PropertyChanged;
    }

    public partial class MainWindow
    {
        // ==================== 配置 ====================
        private sealed class AiAgentConfig
        {
            public string BaseUrl { get; set; } = "https://api.deepseek.com/v1";
            public string ApiKey { get; set; } = "";
            public string Model { get; set; } = "deepseek-chat";
            public bool RequireConfirm { get; set; } = true;
        }

        private static readonly string AiConfigDir =
            Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData), "VioletToolBox");
        private static readonly string AiConfigFile = Path.Combine(AiConfigDir, "ai_agent_config.json");
        private static readonly HttpClient AiHttp = new() { Timeout = TimeSpan.FromSeconds(150) };
        private static readonly JsonElement AiToolsJsonElement = JsonDocument.Parse(AiToolsJson).RootElement.Clone();

        private AiAgentConfig _aiConfig = new();
        private ObservableCollection<AgentChatMessage>? _aiMessages;
        private bool _aiReady;
        private bool _agentBusy;
        private CancellationTokenSource? _agentCts;
        private TaskCompletionSource<bool>? _pendingConfirmTcs;

        // ==================== 常量 ====================
        private const string AiSystemPrompt =
            "你是集成在「紫罗兰工具箱」（Windows 安卓刷机工具）中的 AI 助手 Agent，帮助用户完成安卓设备刷机、救砖、解锁、备份等操作。\n\n" +
            "你可以：\n" +
            "1. 教程问答：回答解锁 BL、线刷、救砖、分区、EDL、ADB/Fastboot 命令等刷机知识（必要时调用 get_tutorial 查询内置知识库，不要凭空编造）；\n" +
            "2. 日志诊断：用户粘贴设备输出或报错后，逐条分析原因并给出可执行的排查与修复步骤；\n" +
            "3. 命令自动生成：根据需求生成正确的 ADB/Fastboot 命令，并解释每条命令的作用与风险；\n" +
            "4. 自动执行操作：通过 get_device_status 读取设备状态，用 run_adb_command / run_fastboot_command 执行命令，用 navigate_to_page 切换工具箱页面。\n\n" +
            "执行规则：\n" +
            "- 全程使用简体中文，回答简洁、专业，命令用代码块展示。\n" +
            "- 执行任何命令前，先用一句话向用户说明目的与影响。\n" +
            "- 读取类命令（devices、getvar、shell getprop、dumpsys 等）可以直接执行；写入、擦除、格式化、刷入分区等高风险命令，系统会自动弹出确认框请求用户批准——你无需让用户再打字确认，只需清楚说明要执行什么。\n" +
            "- 命令执行失败时，阅读输出并给出针对性修复建议，必要时提出替代方案。\n" +
            "- 涉及可能清空数据的操作（解锁 BL、回锁、format、erase userdata 等）必须提醒用户数据会丢失。\n" +
            "- 不知道的事情不要编造；先用 get_tutorial，仍不确定就建议用户查阅官方文档。\n\n" +
            "工具箱已有页面：主页（设备状态）、投屏、基本刷入、可视刷写、欧加线刷、EDL刷写、降级助手、模块专区、文件传输、脱机修补、应用管理、安卓通用、Payload、Rom专区、备份助手、断点续传、下载专区、关于。";

        private const string AiToolsJson =
            "[{\"type\":\"function\",\"function\":{\"name\":\"get_device_status\"," +
            "\"description\":\"读取当前连接的安卓设备状态：连接模式（系统/Fastboot/未连接）、设备序列号、机型、系统版本、BL解锁状态，并列出 adb/fastboot 可见设备。\"," +
            "\"parameters\":{\"type\":\"object\",\"properties\":{},\"required\":[]}}}," +
            "{\"type\":\"function\",\"function\":{\"name\":\"run_adb_command\"," +
            "\"description\":\"在已连接的设备上执行一条 ADB 命令（自动附加 -s 设备序列号）。读取类命令（devices、shell getprop 等）可放心使用；flash/erase/format/wipe 等高风险命令执行前会自动弹出确认框由用户批准。\"," +
            "\"parameters\":{\"type\":\"object\",\"properties\":{\"command\":{\"type\":\"string\",\"description\":\"要执行的 adb 命令参数，如：shell getprop ro.build.version.release\"},\"reason\":{\"type\":\"string\",\"description\":\"执行目的说明，简短即可\"}},\"required\":[\"command\"]}}}," +
            "{\"type\":\"function\",\"function\":{\"name\":\"run_fastboot_command\"," +
            "\"description\":\"在 fastboot 模式下对设备执行一条 Fastboot 命令（自动附加 -s 序列号）。读取类命令（devices、getvar all 等）可直接执行；flash/erase/format/wipe 等高风险命令执行前会自动弹出确认框。\"," +
            "\"parameters\":{\"type\":\"object\",\"properties\":{\"command\":{\"type\":\"string\",\"description\":\"要执行的 fastboot 命令参数，如：getvar all\"},\"reason\":{\"type\":\"string\",\"description\":\"执行目的说明\"}},\"required\":[\"command\"]}}}," +
            "{\"type\":\"function\",\"function\":{\"name\":\"get_tutorial\"," +
            "\"description\":\"查询内置刷机知识库，返回对应主题的教程与命令。可用主题：unlock（解锁BL）、flash（线刷/刷机）、rescue（救砖/EDL）、partition（分区）、adb（ADB常用命令）、fastboot（Fastboot常用命令）、backup（备份分区）、relock（回锁）、xiaomi（小米）、oplus（欧加）、format（双清）、edl（9008）。\"," +
            "\"parameters\":{\"type\":\"object\",\"properties\":{\"topic\":{\"type\":\"string\",\"description\":\"知识库主题关键词\"}},\"required\":[\"topic\"]}}}," +
            "{\"type\":\"function\",\"function\":{\"name\":\"navigate_to_page\"," +
            "\"description\":\"切换到工具箱的指定功能页面。可用值：主页、投屏、基本刷入、可视刷写、欧加线刷、EDL刷写、降级助手、模块专区、文件传输、脱机修补、应用管理、安卓通用、Payload、Rom专区、备份助手、断点续传、下载专区、关于。\"," +
            "\"parameters\":{\"type\":\"object\",\"properties\":{\"page\":{\"type\":\"string\",\"description\":\"目标页面名称\"}},\"required\":[\"page\"]}}}]";

        private const string AiWelcomeText =
            "我是紫罗兰 AI 助手 —— 可执行操作的刷机 Agent。\n\n" +
            "我能帮你：\n" +
            "· 查看设备状态（连接模式 / 机型 / 序列号 / BL 解锁）\n" +
            "· 生成并执行 ADB / Fastboot 命令（高风险命令会先弹确认框，经你批准后才执行）\n" +
            "· 诊断设备日志与报错，给出修复步骤\n" +
            "· 解答解锁 BL、线刷、救砖、分区等教程问题\n\n" +
            "开始使用：请先点击右上角「设置」，配置 OpenAI 兼容接口（如 DeepSeek / 通义 / 豆包）。API Key 仅保存在本机。\n" +
            "也可以先点下方「查看设备状态」或「刷机教程」体验离线能力。";

        // ==================== 知识库 ====================
        private static readonly Dictionary<string, string> AiKnowledgeBase = new()
        {
            ["unlock"] =
                "【解锁 Bootloader（BL）】\n" +
                "风险：解锁会清空全部数据，且部分机型解锁后失去保修/部分功能（如银行应用、DRM）。\n" +
                "小米/红米：官方申请解锁资格（绑定账号→下载解锁工具→等待 7 天/168 小时），Fastboot 模式下执行 fastboot flashing unlock（部分旧机型 fastboot oem unlock）。\n" +
                "一加/欧加：fastboot oem unlock（或 fastboot flashing unlock），部分海外机型需官方解锁申请；OPPO/真我国行通常不支持官方解锁。\n" +
                "解锁前务必备份：fastboot 下可直接执行 fastboot flash boot boot.img 前先回读分区（工具内「回读分区/备份字库」）。\n" +
                "解锁后设备会显示已解锁警告，属正常现象。",
            ["flash"] =
                "【线刷 / 刷机】\n" +
                "常规流程：1) 解锁 BL；2) 下载对应机型官方 ROM（小米线刷包、欧加售后包、高通 fastboot 包）；3) 解压；4) 进 Fastboot 模式（关机→音量- + 电源，或 adb reboot bootloader）；5) 刷入。\n" +
                "小米官方线刷包内 scripts 目录：flash_all_except_storage.bat（保留用户数据）、flash_all.bat（全清）、flash_all_lock.bat（全清并回锁）。\n" +
                "通用命令：\n" +
                "fastboot flash boot boot.img\n" +
                "fastboot flash vendor_boot vendor_boot.img\n" +
                "fastboot flash super super.img（动态分区机型）\n" +
                "fastboot -w（格式化 userdata）\n" +
                "fastboot reboot\n" +
                "注意：ROM 必须匹配机型与版本，刷错包可能变砖。",
            ["rescue"] =
                "【救砖】\n" +
                "判断：白砖（能进 fastboot/rec）相对好救；黑砖（无任何反应）通常是硬件/EDL 层问题。\n" +
                "能进 Fastboot：重刷官方完整包（见 flash 主题），或用工具「可视刷写」回读/刷入分区。\n" +
                "能进 Recovery：三清后刷官方卡刷包（小米：电源+音量上；其他品牌按机型）。\n" +
                "黑砖（高通机型）：进入 EDL 9008 模式（音量上下+电源、或短接测试点、或 adb reboot edl），用全量 QPST/firehose 包恢复——本工具「EDL刷写」页可完成。\n" +
                "救砖前先确认驱动：设备管理器应能看到 9008/Qualcomm HS-USB 设备。",
            ["partition"] =
                "【分区说明】\n" +
                "常见分区：boot（内核）、vendor_boot、recovery、system/vendor（动态分区并入 super）、super（逻辑分区容器）、vbmeta（防回滚校验）、userdata（用户数据）、misc（启动标志）、frp、modem（基带）。\n" +
                "危险操作：erase userdata / format 会清数据；erase frp 可能触发账户锁；误擦 modem/boot 可能导致不开机。\n" +
                "刷写前建议先回读备份 boot、super、vbmeta、modem 等分区（工具「可视刷写」→ 回读分区 / 备份字库）。\n" +
                "动态分区机型不要单独刷 system/vendor 镜像，应从 super 或整包刷入。",
            ["adb"] =
                "【ADB 常用命令】\n" +
                "adb devices -l（列出设备与型号）\n" +
                "adb shell getprop ro.build.version.release（系统版本）\n" +
                "adb shell getprop ro.product.model（机型）\n" +
                "adb push 本地文件 /data/local/tmp/（推文件）\n" +
                "adb pull /sdcard/文件 .（拉文件）\n" +
                "adb install -r app.apk（覆盖安装）\n" +
                "adb reboot bootloader（进 Fastboot）\n" +
                "adb reboot recovery（进 Recovery）\n" +
                "adb reboot edl（高通进 9008）\n" +
                "adb logcat（实时日志）\n" +
                "adb shell dumpsys battery（电池信息）\n" +
                "需要 root 的命令在 shell 前加 su -c。",
            ["fastboot"] =
                "【Fastboot 常用命令】\n" +
                "fastboot devices（列出设备）\n" +
                "fastboot getvar all（读取全部变量：型号/版本/AB槽/解锁状态）\n" +
                "fastboot getvar current-slot（当前槽位）\n" +
                "fastboot flash 分区 镜像（刷入分区，如 fastboot flash boot boot.img）\n" +
                "fastboot erase 分区（擦除分区）\n" +
                "fastboot -w（清空 userdata+cache）\n" +
                "fastboot reboot（重启）\n" +
                "fastboot reboot bootloader（重启到 fastboot）\n" +
                "fastboot flashing unlock / fastboot oem unlock（解锁 BL，视机型）\n" +
                "fastboot flashing lock / fastboot oem lock（回锁）\n" +
                "fastboot set_active a|b（切换槽位）\n" +
                "提示：多设备时需加 -s 序列号。",
            ["backup"] =
                "【备份分区】\n" +
                "刷机/解锁前建议备份关键分区：boot、super（或 system/vendor）、vbmeta、modem、persist。\n" +
                "工具内路径：「可视刷写」→ 回读分区 / 备份字库 / 备份 GPT；备份产物为 img 镜像，保存在本地可随时回刷。\n" +
                "带 root 的设备也可 adb shell \"su -c 'dd if=/dev/block/by-name/boot of=/sdcard/boot.img'\" 备份。\n" +
                "备份文件请存放两份（本机+网盘），刷机前务必验证镜像大小非 0。",
            ["relock"] =
                "【回锁 Bootloader】\n" +
                "小米/红米：fastboot flashing lock（全清）；fastboot oem lock（旧机型）。\n" +
                "一加：fastboot oem lock。\n" +
                "注意：回锁通常再次清空数据，且部分机型（如小米）回锁后需重新申请解锁资格；确认不需要再折腾再回锁。\n" +
                "回锁后建议恢复官方 ROM 并升级到最新版本，再执行锁命令。",
            ["xiaomi"] =
                "【小米/红米】\n" +
                "解锁：官方申请（账号绑定 7 天），fastboot flashing unlock。\n" +
                "线刷：官方线刷包（tgz/zip），解压后运行 flash_all*.bat；保留数据选 flash_all_except_storage.bat。\n" +
                "工具「基本刷入」页支持常规镜像刷入与小米官方线刷；「可视刷写」支持分区级读写。\n" +
                "常见救法：进 Rec（音量+电源）三清后线刷；无法进 Rec 用 fastboot 重刷 boot/recovery。",
            ["oplus"] =
                "【欧加（OPPO/一加/真我）】\n" +
                "解锁：一加多为 fastboot oem unlock（部分机型官方申请）；OPPO/真我国行通常不支持解锁。\n" +
                "线刷：ColorOS 售后线刷包，工具「欧加线刷」页支持全流程（含回锁、清数据选项）。\n" +
                "降级：ColorOS 大版本降级可用工具「降级助手」页完成，注意降级会清数据。\n" +
                "ADB 切换基带调试端口等高级操作见「模块专区」。",
            ["format"] =
                "【双清 / 格式化】\n" +
                "含义：清除用户数据（userdata/cache），恢复出厂状态，不动系统分区。\n" +
                "Fastboot：fastboot -w 或 fastboot erase userdata。\n" +
                "Recovery：进入 Rec 后选 wipe data/factory reset（各品牌菜单不同）。\n" +
                "注意：仅双清不会回退系统版本；部分机型（A/B 槽）还需确认当前槽位。双清前把重要数据备份到电脑。",
            ["edl"] =
                "【EDL / 9008 模式】\n" +
                "EDL（Emergency Download）是高通芯片的底层下载模式，用于救黑砖与刷全量包。\n" +
                "进入方式：1) adb reboot edl；2) 关机后音量上下+电源同时按住；3) 短接主板上测试点（需拆机）。\n" +
                "驱动：设备管理器出现 Qualcomm HS-USB QDLoader 9008（或 900E），无驱动先装高通驱动。\n" +
                "使用：工具「EDL刷写」页通过 firehose loader 与全量包刷写；EDL 下务必使用匹配机型的 loader，错误操作可能烧坏分区表。\n" +
                "EDL 也是备份 QCN 基带校准数据的时机。"
        };

        private static readonly Dictionary<string, string> AiPageAliases = new()
        {
            ["主页"] = "HomeView", ["首页"] = "HomeView", ["设备状态"] = "HomeView",
            ["投屏"] = "ScreenMirrorView",
            ["基本刷入"] = "BasicFlashView", ["基本刷机"] = "BasicFlashView",
            ["可视刷写"] = "FastbootVisualizationView", ["分区"] = "FastbootVisualizationView",
            ["欧加线刷"] = "OujiaFlashView",
            ["EDL刷写"] = "EdlFlashView", ["EDL"] = "EdlFlashView",
            ["降级助手"] = "ColorOSAssistantView",
            ["模块专区"] = "HiddenEnvironmentView",
            ["文件传输"] = "SystemZoneView",
            ["脱机修补"] = "AutorootView",
            ["应用管理"] = "AppManagementView",
            ["安卓通用"] = "AndroidGeneralView",
            ["Payload"] = "PayloadView",
            ["Rom专区"] = "RomDownloadview", ["ROM专区"] = "RomDownloadview",
            ["备份助手"] = "BackupAssistantView",
            ["断点续传"] = "VioletDownloadView",
            ["下载专区"] = "VioletDownloadView",
            ["关于"] = "AboutToolView", ["关于工具"] = "AboutToolView"
        };

        // 主题中文/别名 → 知识库键 映射（GetTutorial 用）
        private static readonly Dictionary<string, string[]> AiTopicAliases = new()
        {
            ["unlock"] = new[] { "解锁", "解bl", "解 bootloader", "bl锁", "bootloader 解锁", "unlock" },
            ["flash"] = new[] { "线刷", "刷机", "刷入", "卡刷", "刷包", "flash" },
            ["rescue"] = new[] { "救砖", "变砖", "砖", "黑砖", "白砖", "9008", "rescue" },
            ["partition"] = new[] { "分区", "boot", "vbmeta", "super", "userdata", "partition" },
            ["adb"] = new[] { "adb命令", "adb 命令", "推文件", "拉文件", "adb" },
            ["fastboot"] = new[] { "fastboot", "fastboot命令", "fb" },
            ["backup"] = new[] { "备份", "备份分区", "回读", "备份字库", "backup" },
            ["relock"] = new[] { "回锁", "上锁", "重新锁定", "relock" },
            ["xiaomi"] = new[] { "小米", "红米", "miui", "hyperos", "xiaomi" },
            ["oplus"] = new[] { "欧加", "oppo", "一加", "oneplus", "真我", "realme", "coloros", "oplus" },
            ["format"] = new[] { "双清", "格式化", "清除数据", "wipe", "format" },
            ["edl"] = new[] { "edl", "9008", "工程模式", "深刷" }
        };

        // ==================== UI 辅助 ====================
        private T? AiCtl<T>(string name) where T : class => FindControlInPages(name) as T;

        private void RunOnUi(Action action)
        {
            if (Dispatcher.CheckAccess()) action();
            else Dispatcher.Invoke(action);
        }

        private void AddAiMessage(AgentChatMessage message)
        {
            RunOnUi(() =>
            {
                if (_aiMessages == null) return;
                // 限制消息条数，防止超长对话导致内存与渲染膨胀（虚拟化之外的硬上限）
                while (_aiMessages.Count >= 300) _aiMessages.RemoveAt(0);
                _aiMessages.Add(message);
                try
                {
                    var sv = AiCtl<ScrollViewer>("AIAgentScrollViewer");
                    sv?.ScrollToEnd();
                    // 新消息入场动画：淡入 + 6px 上滑（与全局 150-200ms 动效语言一致）
                    var ic = AiCtl<ItemsControl>("AIAgentMessagesBox");
                    if (ic != null)
                    {
                        Dispatcher.BeginInvoke(new Action(() =>
                        {
                            try
                            {
                                var idx = ic.Items.Count - 1;
                                if (idx >= 0 && ic.ItemContainerGenerator != null)
                                {
                                    var c = ic.ItemContainerGenerator.ContainerFromIndex(idx) as System.Windows.FrameworkElement;
                                    AnimateMessageEntry(c);
                                }
                            }
                            catch { }
                        }), System.Windows.Threading.DispatcherPriority.Loaded);
                    }
                }
                catch { }
            });
        }

        private static void AnimateMessageEntry(System.Windows.FrameworkElement? container)
        {
            if (container == null) return;
            container.Opacity = 0;
            var tt = new System.Windows.Media.TranslateTransform(0, 6);
            container.RenderTransform = tt;
            var fade = new System.Windows.Media.Animation.DoubleAnimation(0, 1, TimeSpan.FromMilliseconds(200));
            fade.EasingFunction = new System.Windows.Media.Animation.CubicEase { EasingMode = System.Windows.Media.Animation.EasingMode.EaseOut };
            var slide = new System.Windows.Media.Animation.DoubleAnimation(6, 0, TimeSpan.FromMilliseconds(200));
            slide.EasingFunction = new System.Windows.Media.Animation.CubicEase { EasingMode = System.Windows.Media.Animation.EasingMode.EaseOut };
            container.BeginAnimation(System.Windows.UIElement.OpacityProperty, fade);
            tt.BeginAnimation(System.Windows.Media.TranslateTransform.YProperty, slide);
        }

        private void AddAiSystem(string text) => AddAiMessage(new AgentChatMessage { Role = "system", Text = text });

        private static readonly System.Windows.Media.Animation.DoubleAnimation[] AiDotPulseAnims = BuildAiDotPulseAnims();

        private static readonly string[] TypingDotNames = { "AiDot1", "AiDot2", "AiDot3" };

        private static System.Windows.Media.Animation.DoubleAnimation[] BuildAiDotPulseAnims()
        {
            var arr = new System.Windows.Media.Animation.DoubleAnimation[3];
            for (var i = 0; i < 3; i++)
            {
                arr[i] = new System.Windows.Media.Animation.DoubleAnimation(0.25, 1.0, TimeSpan.FromMilliseconds(560))
                {
                    AutoReverse = true,
                    RepeatBehavior = System.Windows.Media.Animation.RepeatBehavior.Forever,
                    BeginTime = TimeSpan.FromMilliseconds(i * 187) // 三点错相位呼吸，如原生打字动画
                };
            }
            return arr;
        }

        private void ShowAiTyping(bool show, string status)
        {
            RunOnUi(() =>
            {
                var panel = AiCtl<Border>("AIAgentTypingPanel");
                var st = AiCtl<TextBlock>("AIAgentStatusText");
                if (panel == null || st == null) return;
                panel.Visibility = show ? Visibility.Visible : Visibility.Collapsed;
                st.Text = status;
                for (var i = 0; i < TypingDotNames.Length; i++)
                {
                    var dot = AiCtl<TextBlock>(TypingDotNames[i]);
                    if (dot == null) continue;
                    if (show)
                    {
                        dot.BeginAnimation(UIElement.OpacityProperty, AiDotPulseAnims[i]);
                    }
                    else
                    {
                        dot.BeginAnimation(UIElement.OpacityProperty, null);
                        dot.Opacity = 1;
                    }
                }
            });
        }

        private void SetAiBusyUi(bool busy)
        {
            RunOnUi(() =>
            {
                var send = AiCtl<System.Windows.Controls.Button>("AIAgentSendButton");
                if (send != null) send.IsEnabled = !busy;
                var stop = AiCtl<System.Windows.Controls.Button>("AIAgentStopButton");
                if (stop != null) stop.Visibility = busy ? Visibility.Visible : Visibility.Collapsed;
            });
        }

        private string SafeConnectionType()
        {
            try { return GetRawLocalizedText(AiCtl<TextBlock>("BottomConnectionTypeText")) ?? "--"; }
            catch { return "--"; }
        }

        private void RefreshAiDeviceBadge()
        {
            RunOnUi(() =>
            {
                var badge = AiCtl<TextBlock>("AIAgentDeviceText");
                var dot = AiCtl<System.Windows.Shapes.Ellipse>("AIAgentDeviceDot");
                if (badge == null) return;
                string conn = SafeConnectionType();
                string serial = "";
                try { serial = GetSelectedDeviceSerial(); } catch { }
                string serialSuffix = string.IsNullOrWhiteSpace(serial) ? "" : $" · {serial}";
                if (conn == "系统")
                {
                    badge.Text = "设备: 已连接（系统）" + serialSuffix;
                    if (dot != null) dot.Fill = new System.Windows.Media.SolidColorBrush(System.Windows.Media.Color.FromRgb(52, 199, 89));
                }
                else if (conn == "Fastboot")
                {
                    badge.Text = "设备: Fastboot" + serialSuffix;
                    if (dot != null) dot.Fill = new System.Windows.Media.SolidColorBrush(System.Windows.Media.Color.FromRgb(255, 149, 0));
                }
                else
                {
                    badge.Text = "设备: 未连接";
                    if (dot != null) dot.Fill = new System.Windows.Media.SolidColorBrush(System.Windows.Media.Color.FromRgb(142, 142, 147));
                }
            });
        }

        private void RefreshAiFooter()
        {
            RunOnUi(() =>
            {
                var footer = AiCtl<TextBlock>("AIAgentFooterText");
                if (footer == null) return;
                bool hasKey = !string.IsNullOrWhiteSpace(_aiConfig.ApiKey);
                footer.Text = $"模型: {_aiConfig.Model} ｜ API: {(hasKey ? "已配置" : "未配置")} ｜ 命令执行确认: {(_aiConfig.RequireConfirm ? "开" : "关")}";
            });
        }

        // ==================== 页面初始化 ====================
        /// <summary>注册 AI 页控件名→AIAgentView 直通映射，避免 FindControlInPages 触发全页面模板扫描</summary>
        private void RegisterAiControlNameMappings()
        {
            if (_nameViewMap.ContainsKey("AIAgentView")) return;
            var names = new[]
            {
                "AIAgentView", "AIAgentMessagesBox", "AIAgentInputBox", "AIAgentSendButton", "AIAgentStopButton",
                "AIAgentScrollViewer", "AIAgentTypingPanel", "AIAgentStatusText", "AiDot1", "AiDot2", "AiDot3",
                "AIAgentConfirmPanel", "AIAgentConfirmText", "AIAgentConfirmAllowButton", "AIAgentConfirmDenyButton",
                "AIAgentDeviceText", "AIAgentDeviceDot", "AIAgentDeviceBadge", "AIAgentFooterText",
                "AIAgentConfigOverlay", "AIAgentConfigBaseUrlBox", "AIAgentConfigKeyBox", "AIAgentConfigModelBox",
                "AIAgentConfigConfirmCheck", "AIAgentConfigStatusText"
            };
            foreach (var n in names)
            {
                if (!_nameViewMap.ContainsKey(n)) _nameViewMap[n] = "AIAgentView";
            }
        }

        private void EnsureAIAgentPageReady()
        {
            try
            {
                RegisterAiControlNameMappings();
                if (FindControlInPages("AIAgentView") as FrameworkElement == null) return;
                if (_aiReady) return;
                _aiConfig = LoadOrCreateConfig();
                var box = AiCtl<ItemsControl>("AIAgentMessagesBox");
                if (box != null)
                {
                    _aiMessages = new ObservableCollection<AgentChatMessage>();
                    box.ItemsSource = _aiMessages;
                }
                if (_aiMessages != null && _aiMessages.Count == 0)
                {
                    _aiMessages.Add(new AgentChatMessage { Role = "assistant", Text = AiWelcomeText });
                }
                RefreshAiDeviceBadge();
                RefreshAiFooter();
                _aiReady = true;
            }
            catch (Exception ex)
            {
                LogAiError("EnsureAIAgentPageReady", ex);
            }
        }

        private void RefreshAIAgentPageState()
        {
            try
            {
                EnsureAIAgentPageReady();
                RefreshAiDeviceBadge();
                RefreshAiFooter();
            }
            catch (Exception ex)
            {
                LogAiError("RefreshAIAgentPageState", ex);
            }
        }

        // ==================== 配置读写 ====================
        private static AiAgentConfig LoadOrCreateConfig()
        {
            try
            {
                if (File.Exists(AiConfigFile))
                {
                    var cfg = JsonSerializer.Deserialize<AiAgentConfig>(File.ReadAllText(AiConfigFile));
                    if (cfg != null) return cfg;
                }
            }
            catch { }
            return new AiAgentConfig();
        }

        private static void SaveConfig(AiAgentConfig cfg)
        {
            try
            {
                Directory.CreateDirectory(AiConfigDir);
                File.WriteAllText(AiConfigFile, JsonSerializer.Serialize(cfg, new JsonSerializerOptions { WriteIndented = true }));
            }
            catch { }
        }

        private void LogAiError(string tag, Exception ex)
        {
            try { File.AppendAllText(Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "page_error.log"), $"{DateTime.Now:HH:mm:ss} {tag}: {ex}\r\n"); } catch { }
        }

        // ==================== UI 事件 ====================
        private void AIAgentSendButton_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                EnsureAIAgentPageReady();
                var box = AiCtl<System.Windows.Controls.TextBox>("AIAgentInputBox");
                string text = box?.Text?.Trim() ?? "";
                if (text.Length == 0 || _agentBusy) return;
                _ = Task.Run(() => SendToAgentAsync(text));
            }
            catch (Exception ex)
            {
                LogAiError("Send", ex);
            }
        }

        private void AIAgentInputBox_TextChanged(object sender, System.Windows.Controls.TextChangedEventArgs e)
        {
            try
            {
                var tb = sender as System.Windows.Controls.TextBox;
                if (tb == null) return;
                var ph = AiCtl<TextBlock>("AIAgentInputPlaceholder");
                if (ph == null) return;
                ph.Visibility = string.IsNullOrEmpty(tb.Text) ? Visibility.Visible : Visibility.Collapsed;
            }
            catch { }
        }

        private void AIAgentInputBox_KeyDown(object sender, System.Windows.Input.KeyEventArgs e)
        {
            // 输入法（中文候选词确认等）处理的回车键值为 Key.ImeProcessed，不应触发发送
            if (e.Key == Key.Enter && e.Key != Key.ImeProcessed && (Keyboard.Modifiers & ModifierKeys.Shift) == 0)
            {
                e.Handled = true;
                AIAgentSendButton_Click(sender, new RoutedEventArgs());
            }
        }

        private void AIAgentStopButton_Click(object sender, RoutedEventArgs e)
        {
            if (!_agentBusy) return;
            try { _agentCts?.Cancel(); } catch { }
            FinishConfirm(false);
            AddAiSystem("正在停止…");
        }

        private void AIAgentClearButton_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                EnsureAIAgentPageReady();
                try { _agentCts?.Cancel(); } catch { }
                try { _agentCts?.Dispose(); } catch { }
                _agentCts = null;
                _agentBusy = false;
                SetAiBusyUi(false);
                ShowAiTyping(false, "");
                FinishConfirm(false);
                RunOnUi(() =>
                {
                    _aiMessages?.Clear();
                    _aiMessages?.Add(new AgentChatMessage { Role = "assistant", Text = AiWelcomeText });
                });
            }
            catch (Exception ex)
            {
                LogAiError("Clear", ex);
            }
        }

        private void AIAgentConfigButton_Click(object sender, RoutedEventArgs e)
        {
            EnsureAIAgentPageReady();
            var cfg = LoadOrCreateConfig();
            _aiConfig = cfg;
            RunOnUi(() =>
            {
                var baseUrl = AiCtl<System.Windows.Controls.TextBox>("AIAgentConfigBaseUrlBox");
                var key = AiCtl<PasswordBox>("AIAgentConfigKeyBox");
                var model = AiCtl<System.Windows.Controls.TextBox>("AIAgentConfigModelBox");
                var confirm = AiCtl<System.Windows.Controls.CheckBox>("AIAgentConfigConfirmCheck");
                var status = AiCtl<TextBlock>("AIAgentConfigStatusText");
                if (baseUrl != null) baseUrl.Text = cfg.BaseUrl;
                if (key != null) key.Password = cfg.ApiKey;
                if (model != null) model.Text = cfg.Model;
                if (confirm != null) confirm.IsChecked = cfg.RequireConfirm;
                if (status != null) status.Text = "";
                var overlay = AiCtl<Grid>("AIAgentConfigOverlay");
                if (overlay != null)
                {
                    overlay.Visibility = Visibility.Visible;
                    overlay.BeginAnimation(UIElement.OpacityProperty, null);
                    overlay.Opacity = 0.0;
                    var anim = new System.Windows.Media.Animation.DoubleAnimation(0.0, 1.0, TimeSpan.FromMilliseconds(160));
                    overlay.BeginAnimation(UIElement.OpacityProperty, anim);
                }
            });
        }

        private void AIAgentConfigCloseButton_Click(object sender, RoutedEventArgs e)
        {
            RunOnUi(() =>
            {
                var overlay = AiCtl<Grid>("AIAgentConfigOverlay");
                if (overlay != null) overlay.Visibility = Visibility.Collapsed;
            });
        }

        private void AIAgentConfigSaveButton_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                var cfg = ReadConfigFields();
                SaveConfig(cfg);
                _aiConfig = cfg;
                RunOnUi(() =>
                {
                    var status = AiCtl<TextBlock>("AIAgentConfigStatusText");
                    if (status != null) status.Text = "已保存 ✓（配置保存在本机，不会上传）";
                    var overlay = AiCtl<Grid>("AIAgentConfigOverlay");
                    if (overlay != null) overlay.Visibility = Visibility.Collapsed;
                });
                RefreshAiFooter();
                RefreshAiDeviceBadge();
            }
            catch (Exception ex)
            {
                LogAiError("ConfigSave", ex);
            }
        }

        private void AIAgentConfigResetButton_Click(object sender, RoutedEventArgs e)
        {
            RunOnUi(() =>
            {
                var baseUrl = AiCtl<System.Windows.Controls.TextBox>("AIAgentConfigBaseUrlBox");
                var key = AiCtl<PasswordBox>("AIAgentConfigKeyBox");
                var model = AiCtl<System.Windows.Controls.TextBox>("AIAgentConfigModelBox");
                var confirm = AiCtl<System.Windows.Controls.CheckBox>("AIAgentConfigConfirmCheck");
                var status = AiCtl<TextBlock>("AIAgentConfigStatusText");
                if (baseUrl != null) baseUrl.Text = "https://api.deepseek.com/v1";
                if (key != null) key.Password = "";
                if (model != null) model.Text = "deepseek-chat";
                if (confirm != null) confirm.IsChecked = true;
                if (status != null) status.Text = "已恢复默认（尚未保存）";
            });
        }

        private async void AIAgentConfigTestButton_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                var cfg = ReadConfigFields();
                RunOnUi(() =>
                {
                    var status = AiCtl<TextBlock>("AIAgentConfigStatusText");
                    if (status != null) status.Text = "正在测试连接…";
                });
                string result = await Task.Run(() => TestConnectionAsync(cfg));
                RunOnUi(() =>
                {
                    var status = AiCtl<TextBlock>("AIAgentConfigStatusText");
                    if (status != null) status.Text = result;
                });
            }
            catch (Exception ex)
            {
                LogAiError("ConfigTest", ex);
            }
        }

        private AiAgentConfig ReadConfigFields()
        {
            string baseUrl = "", apiKey = "", model = "deepseek-chat";
            bool requireConfirm = true;
            RunOnUi(() =>
            {
                baseUrl = AiCtl<System.Windows.Controls.TextBox>("AIAgentConfigBaseUrlBox")?.Text?.Trim() ?? "";
                apiKey = AiCtl<PasswordBox>("AIAgentConfigKeyBox")?.Password?.Trim() ?? "";
                model = AiCtl<System.Windows.Controls.TextBox>("AIAgentConfigModelBox")?.Text?.Trim() ?? "deepseek-chat";
                requireConfirm = AiCtl<System.Windows.Controls.CheckBox>("AIAgentConfigConfirmCheck")?.IsChecked != false;
            });
            return new AiAgentConfig
            {
                BaseUrl = string.IsNullOrWhiteSpace(baseUrl) ? "https://api.deepseek.com/v1" : baseUrl,
                ApiKey = apiKey,
                Model = string.IsNullOrWhiteSpace(model) ? "deepseek-chat" : model,
                RequireConfirm = requireConfirm
            };
        }

        private void FinishConfirm(bool allow)
        {
            RunOnUi(() =>
            {
                var panel = AiCtl<Border>("AIAgentConfirmPanel");
                if (panel != null) panel.Visibility = Visibility.Collapsed;
            });
            _pendingConfirmTcs?.TrySetResult(allow);
        }

        private void AIAgentConfirmAllowButton_Click(object sender, RoutedEventArgs e) => FinishConfirm(true);

        private void AIAgentConfirmDenyButton_Click(object sender, RoutedEventArgs e) => FinishConfirm(false);

        private void AIAgentQuickDeviceButton_Click(object sender, RoutedEventArgs e)
        {
            if (_agentBusy) return;
            _agentBusy = true;
            _agentCts = new CancellationTokenSource();
            var ct = _agentCts.Token;
            AddAiMessage(new AgentChatMessage { Role = "user", Text = "查看设备状态" });
            SetAiBusyUi(true);
            ShowAiTyping(true, "正在读取设备状态…");
            _ = Task.Run(async () =>
            {
                try
                {
                    var result = await GetDeviceStatusAsync(ct);
                    AddAiMessage(new AgentChatMessage { Role = "tool", Text = $"⚙ get_device_status\n{Truncate(result, 2000)}" });
                }
                catch (Exception ex)
                {
                    AddAiSystem($"⚠ {ex.Message}");
                }
                finally
                {
                    _agentBusy = false;
                    SetAiBusyUi(false);
                    ShowAiTyping(false, "");
                    try { _agentCts?.Dispose(); } catch { }
                    _agentCts = null;
                }
            });
        }

        private void AIAgentQuickCommandButton_Click(object sender, RoutedEventArgs e)
        {
            EnsureAIAgentPageReady();
            RunOnUi(() =>
            {
                var box = AiCtl<System.Windows.Controls.TextBox>("AIAgentInputBox");
                if (box != null) box.Text = "请帮我生成常用的解锁 BL、线刷与救砖命令，并逐一解释每条命令的作用与风险。";
            });
            AIAgentSendButton_Click(sender, e);
        }

        private void AIAgentQuickDiagnoseButton_Click(object sender, RoutedEventArgs e)
        {
            EnsureAIAgentPageReady();
            RunOnUi(() =>
            {
                var box = AiCtl<System.Windows.Controls.TextBox>("AIAgentInputBox");
                if (box != null) box.Text = "我想诊断一条设备报错。请先简要说明常见刷机错误类型（卡米、变砖、驱动失败、分区损坏、解锁失败等）的诊断思路与检查步骤，我随后把具体输出粘贴给你。";
            });
            AIAgentSendButton_Click(sender, e);
        }

        private void AIAgentQuickTutorialButton_Click(object sender, RoutedEventArgs e)
        {
            EnsureAIAgentPageReady();
            if (string.IsNullOrWhiteSpace(_aiConfig.ApiKey))
            {
                AddAiMessage(new AgentChatMessage { Role = "user", Text = "刷机教程" });
                AddAiMessage(new AgentChatMessage { Role = "assistant", Text = GetTutorialOverview() });
                return;
            }
            RunOnUi(() =>
            {
                var box = AiCtl<System.Windows.Controls.TextBox>("AIAgentInputBox");
                if (box != null) box.Text = "请给我一份刷机入门教程：解锁 BL、线刷、救砖、常用 ADB / Fastboot 命令，分步骤说明并标注风险。";
            });
            AIAgentSendButton_Click(sender, e);
        }

        // ==================== 核心：发送与 Agent 循环 ====================
        private async Task SendToAgentAsync(string userText)
        {
            try
            {
                EnsureAIAgentPageReady();
                var cfg = LoadOrCreateConfig();
                _aiConfig = cfg;
                if (_agentBusy) return;
                _agentBusy = true;
                _agentCts = new CancellationTokenSource();
                var ct = _agentCts.Token;

                RunOnUi(() =>
                {
                    var box = AiCtl<System.Windows.Controls.TextBox>("AIAgentInputBox");
                    if (box != null) box.Text = "";
                });
                SetAiBusyUi(true);
                AddAiMessage(new AgentChatMessage { Role = "user", Text = userText });

                if (string.IsNullOrWhiteSpace(cfg.ApiKey))
                {
                    AddAiSystem("尚未配置 API Key。点击右上角「设置」，填写 OpenAI 兼容接口的地址与 Key（如 DeepSeek / 通义 / 豆包），再重试。离线可先使用「查看设备状态」与「刷机教程」。");
                    _agentBusy = false;
                    SetAiBusyUi(false);
                    try { _agentCts?.Dispose(); } catch { }
                    _agentCts = null;
                    return;
                }
                ShowAiTyping(true, "正在思考…");

                var apiMsgs = BuildApiHistory(cfg);
                try
                {
                    for (int round = 0; round < 6; round++)
                    {
                        ct.ThrowIfCancellationRequested();
                        var bubble = new AgentChatMessage { Role = "assistant", Text = "" };
                        var toolCalls = new List<ToolCallAcc>();
                        await ChatOnceAsync(apiMsgs, cfg, bubble, toolCalls, ct);

                        bool hasText = bubble.Text.Length > 0;
                        if (!hasText)
                        {
                            // 仅工具调用轮次：移除空气泡
                            RunOnUi(() => _aiMessages?.Remove(bubble));
                        }

                        if (toolCalls.Count == 0)
                        {
                            apiMsgs.Add(AsstMsg(hasText ? bubble.Text : null, null));
                            break;
                        }

                        apiMsgs.Add(AsstMsg(hasText ? bubble.Text : null, toolCalls));
                        foreach (var tc in toolCalls)
                        {
                            // 跳过流式增量错位产生的空占位（仅当 index 空洞时出现）
                            if (string.IsNullOrWhiteSpace(tc.Name)) continue;
                            ct.ThrowIfCancellationRequested();
                            ShowAiTyping(true, $"正在执行工具 {tc.Name} …");
                            string result;
                            try
                            {
                                result = await ExecuteAgentToolAsync(tc.Name, tc.Args.ToString(), ct);
                            }
                            catch (OperationCanceledException)
                            {
                                throw;
                            }
                            catch (Exception ex)
                            {
                                result = $"Error: {ex.Message}";
                            }
                            AddAiMessage(new AgentChatMessage { Role = "tool", Text = $"⚙ {tc.Name}\n{Truncate(result, 2000)}" });
                            apiMsgs.Add(new Dictionary<string, object?>
                            {
                                ["role"] = "tool",
                                ["tool_call_id"] = tc.Id,
                                ["content"] = result
                            });
                        }
                        ShowAiTyping(true, "正在思考…");
                    }
                }
                catch (OperationCanceledException)
                {
                    AddAiSystem("已停止。");
                }
                catch (Exception ex)
                {
                    AddAiSystem($"⚠ {ex.Message}");
                }
                finally
                {
                    _agentBusy = false;
                    SetAiBusyUi(false);
                    ShowAiTyping(false, "");
                    try { _agentCts?.Dispose(); } catch { }
                    _agentCts = null;
                    RunOnUi(() =>
                    {
                        var box = AiCtl<System.Windows.Controls.TextBox>("AIAgentInputBox");
                        box?.Focus();
                    });
                }
            }
            catch (Exception ex)
            {
                LogAiError("SendToAgentAsync", ex);
            }
        }

        private List<Dictionary<string, object?>> BuildApiHistory(AiAgentConfig cfg)
        {
            var list = new List<Dictionary<string, object?>> { new() { ["role"] = "system", ["content"] = AiSystemPrompt } };
            List<AgentChatMessage>? snapshot = null;
            RunOnUi(() => snapshot = _aiMessages?.ToList());
            if (snapshot != null)
            {
                var keep = snapshot.Where(m => m.Role is "user" or "assistant" && m.Text.Length > 0).TakeLast(12);
                foreach (var m in keep)
                {
                    list.Add(new Dictionary<string, object?> { ["role"] = m.Role, ["content"] = m.Text });
                }
            }
            return list;
        }

        private static Dictionary<string, object?> AsstMsg(string? content, List<ToolCallAcc>? toolCalls)
        {
            var d = new Dictionary<string, object?> { ["role"] = "assistant", ["content"] = content };
            if (toolCalls != null && toolCalls.Count > 0)
            {
                d["tool_calls"] = toolCalls.Select(t => (object?)new Dictionary<string, object?>
                {
                    ["id"] = t.Id,
                    ["type"] = "function",
                    ["function"] = new Dictionary<string, object?> { ["name"] = t.Name, ["arguments"] = t.Args.ToString() }
                }).ToList();
            }
            return d;
        }

        private static string ChatUrl(AiAgentConfig cfg)
        {
            string baseUrl = (cfg.BaseUrl ?? "").Trim().TrimEnd('/');
            if (baseUrl.Length == 0) baseUrl = "https://api.deepseek.com/v1";
            return baseUrl.EndsWith("/chat/completions", StringComparison.OrdinalIgnoreCase)
                ? baseUrl
                : baseUrl + "/chat/completions";
        }

        private async Task ChatOnceAsync(
            List<Dictionary<string, object?>> msgs,
            AiAgentConfig cfg,
            AgentChatMessage bubble,
            List<ToolCallAcc> toolCalls,
            CancellationToken ct)
        {
            try
            {
                await StreamOnceAsync(msgs, cfg, bubble, toolCalls, ct);
            }
            catch (Exception) when (bubble.Text.Length == 0 && toolCalls.Count == 0)
            {
                await NonStreamOnceAsync(msgs, cfg, bubble, toolCalls, ct);
            }
        }

        private async Task StreamOnceAsync(
            List<Dictionary<string, object?>> msgs,
            AiAgentConfig cfg,
            AgentChatMessage bubble,
            List<ToolCallAcc> toolCalls,
            CancellationToken ct)
        {
            var payload = new Dictionary<string, object?>
            {
                ["model"] = cfg.Model,
                ["messages"] = msgs,
                ["tools"] = AiToolsJsonElement,
                ["tool_choice"] = "auto",
                ["stream"] = true,
                ["temperature"] = 0.4,
                ["max_tokens"] = 2048
            };
            string json = JsonSerializer.Serialize(payload);
            using var req = new HttpRequestMessage(HttpMethod.Post, ChatUrl(cfg));
            req.Headers.Authorization = new AuthenticationHeaderValue("Bearer", cfg.ApiKey);
            req.Headers.Accept.Add(new MediaTypeWithQualityHeaderValue("text/event-stream"));
            req.Content = new StringContent(json, Encoding.UTF8, "application/json");

            using var resp = await AiHttp.SendAsync(req, HttpCompletionOption.ResponseHeadersRead, ct);
            if (!resp.IsSuccessStatusCode)
            {
                string errBody = await resp.Content.ReadAsStringAsync(ct);
                throw new Exception($"API 错误 HTTP {(int)resp.StatusCode}: {Truncate(errBody, 300)}");
            }
            using var stream = await resp.Content.ReadAsStreamAsync(ct);
            using var reader = new StreamReader(stream, Encoding.UTF8);
            bool sawAny = false;
            // 流式节流：chunk 先在局部缓冲，约 40ms 合并一次刷新 UI，避免逐 token 重排掉帧
            var pendingText = new StringBuilder();
            long lastUiFlushMs = Environment.TickCount64;
            void FlushStreamText(bool force)
            {
                long now = Environment.TickCount64;
                if (!force && now - lastUiFlushMs < 40) return;
                lastUiFlushMs = now;
                string flush = pendingText.ToString();
                pendingText.Clear();
                if (flush.Length == 0) return;
                RunOnUi(() =>
                {
                    if (_aiMessages != null && !_aiMessages.Contains(bubble)) _aiMessages.Add(bubble);
                    bubble.Text += flush;
                    try
                    {
                        var sv = AiCtl<ScrollViewer>("AIAgentScrollViewer");
                        sv?.ScrollToEnd();
                    }
                    catch { }
                });
            }
            while (true)
            {
                ct.ThrowIfCancellationRequested();
                string? line = await reader.ReadLineAsync(ct);
                if (line == null) break;
                if (!line.StartsWith("data:", StringComparison.Ordinal)) continue;
                string data = line.Substring(5).Trim();
                if (data == "[DONE]") break;
                sawAny = true;
                try
                {
                    using var doc = JsonDocument.Parse(data);
                    var root = doc.RootElement;
                    if (root.TryGetProperty("error", out var er))
                    {
                        throw new Exception("API 错误: " + Truncate(er.GetString() ?? "未知错误", 300));
                    }
                    if (!root.TryGetProperty("choices", out var choices) || choices.GetArrayLength() == 0) continue;
                    var delta = choices[0].GetProperty("delta");
                    if (delta.TryGetProperty("content", out var cp) && cp.ValueKind == JsonValueKind.String)
                    {
                        string s = cp.GetString() ?? "";
                        if (s.Length > 0)
                        {
                            pendingText.Append(s);
                            FlushStreamText(false);
                        }
                    }
                    if (delta.TryGetProperty("tool_calls", out var tcs))
                    {
                        foreach (var tc in tcs.EnumerateArray())
                        {
                            int idx = tc.TryGetProperty("index", out var ip) ? ip.GetInt32() : toolCalls.Count;
                            while (toolCalls.Count <= idx) toolCalls.Add(new ToolCallAcc { Index = toolCalls.Count });
                            var acc = toolCalls[idx];
                            if (tc.TryGetProperty("id", out var idp) && idp.ValueKind == JsonValueKind.String) acc.Id += idp.GetString();
                            if (tc.TryGetProperty("function", out var fn))
                            {
                                if (fn.TryGetProperty("name", out var np) && np.ValueKind == JsonValueKind.String) acc.Name += np.GetString();
                                if (fn.TryGetProperty("arguments", out var ap) && ap.ValueKind == JsonValueKind.String) acc.Args.Append(ap.GetString());
                            }
                        }
                    }
                }
                catch (JsonException)
                {
                    // 忽略无法解析的 SSE 行
                }
            }
            // 流结束：强制刷新剩余文本
            FlushStreamText(true);
            if (!sawAny) throw new Exception("API 未返回有效数据（流为空），请检查接口地址与模型名");
        }

        private async Task NonStreamOnceAsync(
            List<Dictionary<string, object?>> msgs,
            AiAgentConfig cfg,
            AgentChatMessage bubble,
            List<ToolCallAcc> toolCalls,
            CancellationToken ct)
        {
            var payload = new Dictionary<string, object?>
            {
                ["model"] = cfg.Model,
                ["messages"] = msgs,
                ["tools"] = AiToolsJsonElement,
                ["tool_choice"] = "auto",
                ["stream"] = false,
                ["temperature"] = 0.4,
                ["max_tokens"] = 2048
            };
            string json = JsonSerializer.Serialize(payload);
            using var req = new HttpRequestMessage(HttpMethod.Post, ChatUrl(cfg));
            req.Headers.Authorization = new AuthenticationHeaderValue("Bearer", cfg.ApiKey);
            req.Content = new StringContent(json, Encoding.UTF8, "application/json");

            using var resp = await AiHttp.SendAsync(req, HttpCompletionOption.ResponseContentRead, ct);
            string body = await resp.Content.ReadAsStringAsync(ct);
            if (!resp.IsSuccessStatusCode)
            {
                throw new Exception($"API 错误 HTTP {(int)resp.StatusCode}: {Truncate(body, 300)}");
            }
            using var doc = JsonDocument.Parse(body);
            var root = doc.RootElement;
            if (root.TryGetProperty("error", out var er))
            {
                throw new Exception("API 错误: " + Truncate(er.GetString() ?? "未知错误", 300));
            }
            if (!root.TryGetProperty("choices", out var choices) || choices.GetArrayLength() == 0)
            {
                throw new Exception("API 未返回有效结果");
            }
            var msg = choices[0].GetProperty("message");
            if (msg.TryGetProperty("content", out var cp) && cp.ValueKind == JsonValueKind.String)
            {
                string s = cp.GetString() ?? "";
                if (s.Length > 0)
                {
                    string full = s;
                    RunOnUi(() =>
                    {
                        if (_aiMessages != null && !_aiMessages.Contains(bubble)) _aiMessages.Add(bubble);
                        bubble.Text = full;
                        try
                        {
                            var sv = AiCtl<ScrollViewer>("AIAgentScrollViewer");
                            sv?.ScrollToEnd();
                        }
                        catch { }
                    });
                }
            }
            if (msg.TryGetProperty("tool_calls", out var tcs))
            {
                foreach (var tc in tcs.EnumerateArray())
                {
                    int idx = tc.TryGetProperty("index", out var ip) ? ip.GetInt32() : toolCalls.Count;
                    while (toolCalls.Count <= idx) toolCalls.Add(new ToolCallAcc { Index = toolCalls.Count });
                    var acc = toolCalls[idx];
                    if (tc.TryGetProperty("id", out var idp)) acc.Id += idp.GetString();
                    if (tc.TryGetProperty("function", out var fn))
                    {
                        if (fn.TryGetProperty("name", out var np)) acc.Name += np.GetString();
                        if (fn.TryGetProperty("arguments", out var ap)) acc.Args.Append(ap.GetString());
                    }
                }
            }
        }

        // ==================== 工具执行 ====================
        private async Task<string> ExecuteAgentToolAsync(string name, string argsJson, CancellationToken ct)
        {
            switch (name)
            {
                case "get_device_status":
                    return await GetDeviceStatusAsync(ct);

                case "get_tutorial":
                {
                    string topic = ParseArg(argsJson, "topic");
                    return GetTutorial(topic);
                }

                case "run_adb_command":
                {
                    string cmd = ParseArg(argsJson, "command");
                    if (string.IsNullOrWhiteSpace(cmd)) return "错误: 缺少 command 参数";
                    if (_aiConfig.RequireConfirm)
                    {
                        bool ok = await RequestCommandConfirmationAsync("adb", cmd, ct);
                        if (!ok) return "用户已拒绝执行该命令（User declined）";
                    }
                    ShowAiTyping(true, "正在执行 adb …");
                    return await ExecuteToolWithOutputAsync("adb.exe", cmd, ct);
                }

                case "run_fastboot_command":
                {
                    string cmd = ParseArg(argsJson, "command");
                    if (string.IsNullOrWhiteSpace(cmd)) return "错误: 缺少 command 参数";
                    if (_aiConfig.RequireConfirm)
                    {
                        bool ok = await RequestCommandConfirmationAsync("fastboot", cmd, ct);
                        if (!ok) return "用户已拒绝执行该命令（User declined）";
                    }
                    ShowAiTyping(true, "正在执行 fastboot …");
                    return await ExecuteToolWithOutputAsync("fastboot.exe", cmd, ct);
                }

                case "navigate_to_page":
                {
                    string page = ParseArg(argsJson, "page");
                    string? view = page != null && AiPageAliases.TryGetValue(page, out var v) ? v : null;
                    if (view == null) return $"未知页面: {page}";
                    RunOnUi(() =>
                    {
                        try { ShowPage(view); } catch { }
                    });
                    return $"已切换到页面「{page}」";
                }

                default:
                    return $"未知工具: {name}";
            }
        }

        private static string ParseArg(string argsJson, string key)
        {
            try
            {
                if (string.IsNullOrWhiteSpace(argsJson)) return "";
                using var doc = JsonDocument.Parse(argsJson);
                if (doc.RootElement.TryGetProperty(key, out var v) && v.ValueKind == JsonValueKind.String)
                {
                    return v.GetString() ?? "";
                }
            }
            catch { }
            return "";
        }

        private Task<bool> RequestCommandConfirmationAsync(string tool, string command, CancellationToken ct)
        {
            var tcs = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
            _pendingConfirmTcs = tcs;
            CancellationTokenRegistration reg = default;
            try
            {
                // 注意：必须在方法返回 tcs.Task 之前保持注册有效，否则取消回调被注销，停止按钮将无法解除确认等待。
                reg = ct.Register(() => tcs.TrySetResult(false));
                RunOnUi(() =>
                {
                    var txt = AiCtl<TextBlock>("AIAgentConfirmText");
                    if (txt != null) txt.Text = $"[{tool}] {command}";
                    var panel = AiCtl<Border>("AIAgentConfirmPanel");
                    if (panel != null)
                    {
                        // 弹出动画：轻微放大 + 淡入，避免突兀出现
                        panel.Visibility = Visibility.Visible;
                        panel.RenderTransformOrigin = new System.Windows.Point(0.5, 0.5);
                        panel.BeginAnimation(UIElement.RenderTransformProperty, null);
                        panel.RenderTransform = new System.Windows.Media.ScaleTransform(0.96, 0.96);
                        panel.BeginAnimation(UIElement.OpacityProperty, null);
                        panel.Opacity = 0.0;
                        var sb = new System.Windows.Media.Animation.Storyboard();
                        var oa = new System.Windows.Media.Animation.DoubleAnimation(0.0, 1.0, TimeSpan.FromMilliseconds(160))
                        {
                            EasingFunction = new System.Windows.Media.Animation.CubicEase { EasingMode = System.Windows.Media.Animation.EasingMode.EaseOut }
                        };
                        System.Windows.Media.Animation.Storyboard.SetTarget(oa, panel);
                        System.Windows.Media.Animation.Storyboard.SetTargetProperty(oa, new System.Windows.PropertyPath(UIElement.OpacityProperty));
                        sb.Children.Add(oa);
                        var sa = new System.Windows.Media.Animation.DoubleAnimation(0.96, 1.0, TimeSpan.FromMilliseconds(180))
                        {
                            EasingFunction = new System.Windows.Media.Animation.CubicEase { EasingMode = System.Windows.Media.Animation.EasingMode.EaseOut }
                        };
                        System.Windows.Media.Animation.Storyboard.SetTarget(sa, panel);
                        System.Windows.Media.Animation.Storyboard.SetTargetProperty(sa, new System.Windows.PropertyPath("(UIElement.RenderTransform).(ScaleTransform.ScaleX)"));
                        sb.Children.Add(sa);
                        var sa2 = new System.Windows.Media.Animation.DoubleAnimation(0.96, 1.0, TimeSpan.FromMilliseconds(180))
                        {
                            EasingFunction = new System.Windows.Media.Animation.CubicEase { EasingMode = System.Windows.Media.Animation.EasingMode.EaseOut }
                        };
                        System.Windows.Media.Animation.Storyboard.SetTarget(sa2, panel);
                        System.Windows.Media.Animation.Storyboard.SetTargetProperty(sa2, new System.Windows.PropertyPath("(UIElement.RenderTransform).(ScaleTransform.ScaleY)"));
                        sb.Children.Add(sa2);
                        sb.Completed += (_, _) => { try { panel.RenderTransform = null; } catch { } };
                        sb.Begin(panel);
                    }
                    AiCtl<System.Windows.Controls.Button>("AIAgentConfirmAllowButton")?.Focus();
                    AddAiMessage(new AgentChatMessage { Role = "system", Text = $"⏸ 等待确认执行命令（尚未执行）\n[{tool}] {command}" });
                });
            }
            catch
            {
                tcs.TrySetResult(false);
            }
            // 等待用户操作或取消；无论何种方式结束，都需要注销回调并清理引用。
            tcs.Task.ContinueWith(_ =>
            {
                reg.Dispose();
                if (ReferenceEquals(_pendingConfirmTcs, tcs)) _pendingConfirmTcs = null;
            }, TaskScheduler.Default);
            return tcs.Task;
        }

        private async Task<string> ExecuteToolWithOutputAsync(string toolName, string arguments, CancellationToken ct)
        {
            Process? process = null;
            try
            {
                ct.ThrowIfCancellationRequested();
                string toolPath = GetToolPath(toolName);
                string serial = GetSelectedDeviceSerial();
                string finalArgs = string.IsNullOrWhiteSpace(serial) ? arguments : $"-s {serial} {arguments}";
                var psi = new ProcessStartInfo
                {
                    FileName = toolPath,
                    Arguments = finalArgs,
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    CreateNoWindow = true,
                    WorkingDirectory = File.Exists(toolPath)
                        ? (Path.GetDirectoryName(toolPath) ?? AppDomain.CurrentDomain.BaseDirectory)
                        : AppDomain.CurrentDomain.BaseDirectory
                };
                process = Process.Start(psi);
                if (process == null) return "Error: 进程启动失败";

                Task<string> outTask;
                Task<string> errTask;
                using (var outReader = new StreamReader(process.StandardOutput.BaseStream, new UTF8Encoding(false), true))
                using (var errReader = new StreamReader(process.StandardError.BaseStream, new UTF8Encoding(false), true))
                {
                    outTask = outReader.ReadToEndAsync();
                    errTask = errReader.ReadToEndAsync();
                    await process.WaitForExitAsync(ct);
                    await Task.WhenAll(outTask, errTask);
                }
                string output = await outTask;
                string error = await errTask;
                return string.Join(
                    Environment.NewLine,
                    new[] { output.Trim(), error.Trim() }.Where(t => !string.IsNullOrWhiteSpace(t)));
            }
            catch (OperationCanceledException)
            {
                try
                {
                    if (process != null && !process.HasExited) process.Kill(entireProcessTree: true);
                }
                catch { }
                throw;
            }
            catch (Exception ex)
            {
                return $"Error: {ex.Message}";
            }
            finally
            {
                process?.Dispose();
            }
        }

        private async Task<string> GetDeviceStatusAsync(CancellationToken ct)
        {
            var sb = new StringBuilder();
            string conn = SafeConnectionType();
            string serial = "";
            try { serial = GetSelectedDeviceSerial(); } catch { }
            sb.AppendLine($"连接模式: {conn}");
            sb.AppendLine($"选中设备: {(string.IsNullOrWhiteSpace(serial) ? "无" : serial)}");
            if (!string.IsNullOrWhiteSpace(lastDeviceModel)) sb.AppendLine($"机型: {lastDeviceModel}");
            if (!string.IsNullOrWhiteSpace(lastAndroidVersion)) sb.AppendLine($"系统版本: {lastAndroidVersion}");
            if (!string.IsNullOrWhiteSpace(lastUnlockStatus)) sb.AppendLine($"BL解锁状态: {lastUnlockStatus}");
            try
            {
                var dev = await ExecuteToolWithOutputAsync("adb.exe", "devices -l", ct);
                sb.AppendLine("— adb devices —");
                sb.AppendLine(dev);
            }
            catch (OperationCanceledException) { throw; }
            catch { }
            if (conn == "Fastboot")
            {
                try
                {
                    var fd = await ExecuteToolWithOutputAsync("fastboot.exe", "devices", ct);
                    sb.AppendLine("— fastboot devices —");
                    sb.AppendLine(fd);
                }
                catch (OperationCanceledException) { throw; }
                catch { }
            }
            return sb.ToString();
        }

        private static string GetTutorial(string topic)
        {
            string key = (topic ?? "").Trim().ToLowerInvariant();
            if (key.Length == 0) return GetTutorialOverview();
            // 中文/别名 → 主题键 映射，避免“解锁BL”“线刷”等常见说法匹配不到英文 key
            foreach (var alias in AiTopicAliases)
            {
                foreach (var name in alias.Value)
                {
                    if (key == name || key.Contains(name) || name.Contains(key))
                    {
                        return $"【{alias.Key}】\n{AiKnowledgeBase[alias.Key]}";
                    }
                }
            }
            foreach (var kv in AiKnowledgeBase)
            {
                if (key == kv.Key || key.Contains(kv.Key) || kv.Key.Contains(key))
                {
                    return $"【{kv.Key}】\n{kv.Value}";
                }
            }
            return $"知识库未收录「{topic}」。可用主题：unlock、flash、rescue、partition、adb、fastboot、backup、relock、xiaomi、oplus、format、edl。";
        }

        private static string GetTutorialOverview()
        {
            var sb = new StringBuilder();
            sb.AppendLine("【刷机入门 · 内置知识库概览】");
            sb.AppendLine();
            sb.AppendLine("1. 解锁 BL（unlock）：官方申请解锁资格（小米需绑定账号等待 7 天），fastboot flashing unlock 解锁，解锁会清空数据。");
            sb.AppendLine("2. 线刷（flash）：下载对应机型官方 ROM → 进 Fastboot → fastboot flash boot/system/super … → fastboot -w → fastboot reboot。");
            sb.AppendLine("3. 救砖（rescue）：白砖重刷官方包；黑砖（高通）进 EDL 9008 用全量包恢复（工具「EDL刷写」页）。");
            sb.AppendLine("4. 分区（partition）：boot / vbmeta / super / userdata 等，刷机前先回读备份关键分区。");
            sb.AppendLine("5. 常用命令：");
            sb.AppendLine("   · adb devices / adb shell getprop / adb reboot bootloader");
            sb.AppendLine("   · fastboot devices / fastboot getvar all / fastboot flash <分区> <img>");
            sb.AppendLine("6. 备份（backup）：boot、super、vbmeta、modem 等分区建议先备份（工具「可视刷写」→ 回读分区）。");
            sb.AppendLine("7. 双清（format）：fastboot -w 或 Recovery 双清，仅清除数据不换系统版本。");
            sb.AppendLine();
            sb.AppendLine("在对话中输入主题关键词（如「解锁BL」「救砖」「ADB命令」），我可以给出更详细的步骤与风险提示。");
            return sb.ToString();
        }

        private async Task<string> TestConnectionAsync(AiAgentConfig cfg)
        {
            try
            {
                if (string.IsNullOrWhiteSpace(cfg.ApiKey))
                {
                    return "连接失败：请先填写 API Key 再测试（Key 仅保存在本机）。";
                }
                var msgs = new List<Dictionary<string, object?>> { new() { ["role"] = "user", ["content"] = "ping" } };
                var payload = new Dictionary<string, object?>
                {
                    ["model"] = cfg.Model,
                    ["messages"] = msgs,
                    ["max_tokens"] = 1,
                    ["stream"] = false
                };
                string json = JsonSerializer.Serialize(payload);
                using var req = new HttpRequestMessage(HttpMethod.Post, ChatUrl(cfg));
                req.Headers.Authorization = new AuthenticationHeaderValue("Bearer", cfg.ApiKey);
                req.Content = new StringContent(json, Encoding.UTF8, "application/json");
                using var resp = await AiHttp.SendAsync(req, HttpCompletionOption.ResponseContentRead);
                string body = await resp.Content.ReadAsStringAsync();
                if (!resp.IsSuccessStatusCode)
                {
                    return $"连接失败: HTTP {(int)resp.StatusCode} {Truncate(body, 200)}";
                }
                using var doc = JsonDocument.Parse(body);
                if (doc.RootElement.TryGetProperty("error", out var er))
                {
                    return "连接失败: " + Truncate(er.GetString() ?? "未知错误", 200);
                }
                return $"连接成功 ✓ 模型 {cfg.Model} 可用";
            }
            catch (Exception ex)
            {
                return "连接失败: " + ex.Message;
            }
        }

        private static string Truncate(string text, int max)
        {
            if (string.IsNullOrEmpty(text)) return text;
            if (max <= 0) return "";
            if (text.Length <= max) return text;
            return text.Substring(0, max) + "…(截断)";
        }
    }

    internal sealed class ToolCallAcc
    {
        public int Index { get; set; }
        public string Id { get; set; } = "";
        public string Name { get; set; } = "";
        public StringBuilder Args { get; } = new();
    }
}
