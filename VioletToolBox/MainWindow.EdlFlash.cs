// EDL Flash page logic — merged from OplusEdlTool (Avalonia) into VioletToolBox (WPF)
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using System.Threading;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using TextBox = System.Windows.Controls.TextBox;
using ListBox = System.Windows.Controls.ListBox;
using CheckBox = System.Windows.Controls.CheckBox;
using ProgressBar = System.Windows.Controls.ProgressBar;
using OpenFileDialog = Microsoft.Win32.OpenFileDialog;
using MessageBox = System.Windows.MessageBox;
using System.Windows.Input;
using System.Windows.Threading;
using System.Xml.Linq;
using Microsoft.Win32;
using OplusEdlTool.Services;

namespace WpfApp1
{
    public class EdlPartitionRow : INotifyPropertyChanged
    {
        private bool _isSelected;
        private string _name = string.Empty;
        private int _lun;
        private ulong _firstLBA;
        private ulong _lastLBA;
        private string _sizeFormatted = string.Empty;
        private ulong _sizeBytes;
        private string _typeGuid = string.Empty;
        private string _filePath = string.Empty;

        public bool IsSelected
        {
            get => _isSelected;
            set { _isSelected = value; OnPropertyChanged(nameof(IsSelected)); }
        }
        public string Name
        {
            get => _name;
            set { _name = value; OnPropertyChanged(nameof(Name)); }
        }
        public int Lun
        {
            get => _lun;
            set { _lun = value; OnPropertyChanged(nameof(Lun)); }
        }
        public ulong FirstLBA
        {
            get => _firstLBA;
            set { _firstLBA = value; OnPropertyChanged(nameof(FirstLBA)); }
        }
        public ulong LastLBA
        {
            get => _lastLBA;
            set { _lastLBA = value; OnPropertyChanged(nameof(LastLBA)); }
        }
        public string SizeFormatted
        {
            get => _sizeFormatted;
            set { _sizeFormatted = value; OnPropertyChanged(nameof(SizeFormatted)); }
        }
        public ulong SizeBytes
        {
            get => _sizeBytes;
            set { _sizeBytes = value; OnPropertyChanged(nameof(SizeBytes)); }
        }
        public string TypeGuid
        {
            get => _typeGuid;
            set { _typeGuid = value; OnPropertyChanged(nameof(TypeGuid)); }
        }
        public string FilePath
        {
            get => _filePath;
            set { _filePath = value; OnPropertyChanged(nameof(FilePath)); }
        }

        public string NumSectors { get; set; } = string.Empty;
        public string SectorSize { get; set; } = "4096";

        public PartitionEntry ToEntry() => new PartitionEntry
        {
            Name = Name,
            Lun = Lun,
            FirstLBA = FirstLBA,
            LastLBA = LastLBA,
            SizeBytes = SizeBytes,
            TypeGuid = TypeGuid
        };

        public event PropertyChangedEventHandler? PropertyChanged;
        protected void OnPropertyChanged(string propertyName)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        }
    }

    public class EdlXmlFileItem : INotifyPropertyChanged
    {
        private bool _isSelected;
        public string Name { get; set; } = string.Empty;
        public string FullPath { get; set; } = string.Empty;
        public bool IsSelected
        {
            get => _isSelected;
            set
            {
                _isSelected = value;
                PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(nameof(IsSelected)));
            }
        }
        public event PropertyChangedEventHandler? PropertyChanged;
    }

    public partial class MainWindow
    {
        private EdlService? _edl;
        private RawProgramXmlProcessor? _edlXmlProcessor;
        private ObservableCollection<EdlPartitionRow> _edlRows = new();
        private ObservableCollection<EdlXmlFileItem> _edlXmlFileItems = new();
        private DispatcherTimer? _edlPortTimer;
        private CancellationTokenSource? _edlCts;
        private string? _edlPort;
        private string? _edlRomImagesPath;
        private string[]? _edlRawProgramFiles;
        private RomPackageInfo _edlRomPackage = RomPackageInfo.Unknown;
        private string? _edlLogFilePath;
        private readonly object _edlLogLock = new object();
        private bool _edlInitialized;

        private T E<T>(string name) where T : class
            => this.FindControlInPages(name) as T;

        private void EnsureEdl()
        {
            if (_edlInitialized) return;
            _edlInitialized = true;
            try { _edl = new EdlService(AppendEdlLog, UpdateEdlProgress); }
            catch (Exception ex)
            {
                try { System.IO.File.AppendAllText(System.IO.Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "edl_debug.txt"), $"[EdlService ctor] {ex}\n"); } catch { }
            }
            try { _edlXmlProcessor = new RawProgramXmlProcessor(AppendEdlLog); }
            catch (Exception ex)
            {
                try { System.IO.File.AppendAllText(System.IO.Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "edl_debug.txt"), $"[XmlProcessor ctor] {ex}\n"); } catch { }
            }
            var logDir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "VioletToolBox");
            try { Directory.CreateDirectory(logDir); } catch { }
            _edlLogFilePath = Path.Combine(logDir, "edl_log.txt");
            try { File.WriteAllText(_edlLogFilePath, $"========== EDL Log Started at {DateTime.Now:yyyy-MM-dd HH:mm:ss} ==========\n"); } catch { }

            if (_edlPortTimer == null)
            {
                _edlPortTimer = new DispatcherTimer { Interval = TimeSpan.FromSeconds(1) };
                _edlPortTimer.Tick += (s, e) => RefreshEdlPortStatus();
                _edlPortTimer.Start();
            }
            RefreshEdlPortStatus();
        }

        // ---------- Logging & Progress ----------
        public void AppendEdlLog(string s)
        {
            var ts = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss");
            var logLine = $"{ts} {s}\n";
            if (!string.IsNullOrEmpty(_edlLogFilePath))
            {
                lock (_edlLogLock)
                {
                    try { File.AppendAllText(_edlLogFilePath, logLine); } catch { }
                }
            }
            var logBox = E<TextBox>("EdlLogTextBox");
            this.Dispatcher.BeginInvoke(new Action(() =>
            {
                if (logBox == null) return;
                var lines = (logBox.Text ?? "").Split('\n');
                if (lines.Length > 500)
                    logBox.Text = string.Join("\n", lines.Skip(lines.Length - 500)) + logLine;
                else
                    logBox.Text += logLine;
                logBox.CaretIndex = logBox.Text?.Length ?? 0;
                logBox.ScrollToEnd();
            }));
        }

        public void UpdateEdlProgress(int percent)
        {
            if (percent < 0) percent = 0;
            if (percent > 100) percent = 100;
            this.Dispatcher.BeginInvoke(new Action(() =>
            {
                var bar = E<ProgressBar>("EdlProgressBar");
                if (bar != null) bar.Value = percent;
            }));
        }

        // ---------- Port Detection ----------
        private void RefreshEdlPortStatus()
        {
            try
            {
                var port = DetectEdl9008Port();
                var status = E<TextBlock>("EdlPortStatusText");
                if (status == null) return;
                if (!string.IsNullOrEmpty(port))
                {
                    status.Text = port;
                    status.Foreground = System.Windows.Media.Brushes.Green;
                }
                else
                {
                    status.Text = "未检测到";
                    status.Foreground = System.Windows.Media.Brushes.Red;
                }
            }
            catch { }
        }

        private string? DetectEdl9008Port()
        {
            try
            {
                var toolsDir = FindEdlToolsDir();
                if (toolsDir == null) return null;
                var lsusb = Path.Combine(toolsDir, "lsusb.exe");
                if (!File.Exists(lsusb)) return null;
                var psi = new System.Diagnostics.ProcessStartInfo
                {
                    FileName = lsusb,
                    WorkingDirectory = toolsDir,
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                    CreateNoWindow = true
                };
                using var p = System.Diagnostics.Process.Start(psi);
                if (p == null) return null;
                var output = p.StandardOutput.ReadToEnd();
                p.WaitForExit(2000);
                var m = Regex.Match(output, @"Qualcomm HS-USB QDLoader 9008 \(COM(?<n>\d+)\)");
                if (m.Success) return "COM" + m.Groups["n"].Value;
            }
            catch { }
            return null;
        }

        private string? FindEdlToolsDir()
        {
            var dir = AppContext.BaseDirectory;
            for (int i = 0; i < 8; i++)
            {
                var candidate = Path.Combine(dir, "Tools");
                var full = Path.GetFullPath(candidate);
                if (Directory.Exists(full) && File.Exists(Path.Combine(full, "fh_loader.exe")))
                    return full;
                // fallback: base dir itself contains fh_loader.exe
                if (File.Exists(Path.Combine(dir, "fh_loader.exe")))
                    return dir;
                var parent = Directory.GetParent(dir);
                if (parent == null) break;
                dir = parent.FullName;
            }
            return null;
        }

        // ---------- File pickers ----------
        private string? PickFile(string title, string filter)
        {
            var dlg = new OpenFileDialog { Title = title, Filter = filter, CheckFileExists = true };
            return dlg.ShowDialog(this) == true ? dlg.FileName : null;
        }

        private string? PickFolder(string title)
        {
            var dlg = new System.Windows.Forms.FolderBrowserDialog { Description = title, UseDescriptionForTitle = true };
            return dlg.ShowDialog() == System.Windows.Forms.DialogResult.OK ? dlg.SelectedPath : null;
        }

        // ---------- Event handlers ----------
        private void EdlDevPrgBrowse_Click(object sender, RoutedEventArgs e)
        {
            var f = PickFile("选择设备编程器", "设备编程器 (*.mbn)|*.mbn|所有文件 (*.*)|*.*");
            if (f != null) { var t = E<TextBox>("EdlDevPrgTextBox"); if (t != null) t.Text = f; }
        }

        private void EdlDigestBrowse_Click(object sender, RoutedEventArgs e)
        {
            var f = PickFile("选择摘要文件", "摘要文件 (*.bin)|*.bin|所有文件 (*.*)|*.*");
            if (f != null) { var t = E<TextBox>("EdlDigestTextBox"); if (t != null) t.Text = f; }
        }

        private void EdlSigBrowse_Click(object sender, RoutedEventArgs e)
        {
            var f = PickFile("选择签名文件", "签名文件 (*.bin)|*.bin|所有文件 (*.*)|*.*");
            if (f != null) { var t = E<TextBox>("EdlSigTextBox"); if (t != null) t.Text = f; }
        }

        private async void EdlRomBrowse_Click(object sender, RoutedEventArgs e)
        {
            EnsureEdl();
            var result = System.Windows.MessageBox.Show("选择 ROM 源：\n\n是 = 文件夹（解压后的 ROM）\n否 = 文件（OFP/OPS 加密包）\n取消 = 退出",
                "选择 ROM 来源", MessageBoxButton.YesNoCancel, MessageBoxImage.Question);
            if (result == MessageBoxResult.Cancel) return;
            if (result == MessageBoxResult.Yes)
                await SelectEdlRomFolder();
            else
                await SelectEdlOfpOpsFile();
        }

        private async Task SelectEdlRomFolder()
        {
            var folder = PickFolder("选择 ROM 文件夹");
            if (string.IsNullOrEmpty(folder)) return;

            _edlRomPackage = RomPackageInfo.Unknown;
            var imagesPath = FindEdlImagesFolder(folder);
            if (imagesPath == null)
            {
                AppendEdlLog("未找到 IMAGES 文件夹或 rawprogram*.xml");
                System.Windows.MessageBox.Show("未找到 IMAGES 文件夹或 rawprogram*.xml", "错误", MessageBoxButton.OK, MessageBoxImage.Error);
                return;
            }
            if (!await ValidateAndLoadEdlRawProgram(imagesPath, folder)) return;
            _edlRomPackage = FirmwarePackageClassifier.ClassifyRomFolder(folder);
            LogEdlRomPackage();
        }

        private async Task SelectEdlOfpOpsFile()
        {
            var f = PickFile("选择 OFP 或 OPS 加密 ROM 文件", "ROM 文件 (*.ofp;*.ops)|*.ofp;*.ops|所有文件 (*.*)|*.*");
            if (string.IsNullOrEmpty(f)) return;

            _edlRomPackage = RomPackageInfo.Unknown;
            var ext = Path.GetExtension(f).ToLower();
            AppendEdlLog($"已选择文件: {Path.GetFileName(f)}");
            AppendEdlLog("开始解压，请稍候...");

            string? extractPath = null;
            try
            {
                if (ext == ".ops")
                {
                    var decryptor = new OpsDecryptor(AppendEdlLog);
                    extractPath = await Task.Run(() => decryptor.Decrypt(f));
                }
                else if (ext == ".ofp")
                {
                    var decryptor = new OfpDecryptor(AppendEdlLog);
                    extractPath = await Task.Run(() => decryptor.Decrypt(f));
                }
                else
                {
                    AppendEdlLog("不支持的文件格式");
                    return;
                }
            }
            catch (Exception ex)
            {
                AppendEdlLog($"解压错误: {ex.Message}");
                return;
            }

            if (string.IsNullOrEmpty(extractPath))
            {
                AppendEdlLog("解压失败");
                return;
            }

            AppendEdlLog($"解压完成: {extractPath}");
            await MergeEdlSuperImages(extractPath);
            var imagesPath = FindEdlImagesFolder(extractPath) ?? extractPath;
            if (!await ValidateAndLoadEdlRawProgram(imagesPath, extractPath))
            {
                _edlRomPackage = RomPackageInfo.Unknown;
                return;
            }
            LogEdlRomPackage();
        }

        private async Task MergeEdlSuperImages(string extractPath)
        {
            try
            {
                var superFiles = Directory.GetFiles(extractPath, "super.*.img")
                    .Where(f => Regex.IsMatch(Path.GetFileName(f), @"^super\.\d+\.[a-fA-F0-9]+\.img$"))
                    .OrderBy(f =>
                    {
                        var m = Regex.Match(Path.GetFileName(f), @"^super\.(\d+)\.");
                        return m.Success ? int.Parse(m.Groups[1].Value) : int.MaxValue;
                    })
                    .ToList();

                if (superFiles.Count == 0)
                {
                    AppendEdlLog("未找到 super 分段镜像");
                    return;
                }

                AppendEdlLog($"找到 {superFiles.Count} 个 super 分段镜像");
                var renamedFiles = new List<string>();
                for (int i = 0; i < superFiles.Count; i++)
                {
                    var newName = Path.Combine(extractPath, $"super{i}.img");
                    if (File.Exists(newName) && newName != superFiles[i])
                        File.Delete(newName);
                    if (superFiles[i] != newName)
                    {
                        File.Move(superFiles[i], newName);
                        AppendEdlLog($"重命名 {Path.GetFileName(superFiles[i])} -> super{i}.img");
                    }
                    renamedFiles.Add(newName);
                }

                var toolsDir = FindEdlToolsDir();
                if (toolsDir == null) { AppendEdlLog("未找到工具目录，跳过 super 合并"); return; }
                var simg2imgPath = Path.Combine(toolsDir, "simg2img.exe");
                if (!File.Exists(simg2imgPath)) { AppendEdlLog("simg2img.exe 不存在，跳过 super 合并"); return; }

                var superOutputPath = Path.Combine(extractPath, "super.img");
                if (File.Exists(superOutputPath)) { AppendEdlLog("super.img 已存在，跳过合并"); return; }

                var args = string.Join(" ", renamedFiles.Select(f => $"\"{f}\"")) + $" \"{superOutputPath}\"";
                AppendEdlLog("使用 simg2img 合并 super 镜像...");

                var result = await Task.Run(() =>
                {
                    var psi = new System.Diagnostics.ProcessStartInfo
                    {
                        FileName = simg2imgPath,
                        Arguments = args,
                        WorkingDirectory = extractPath,
                        UseShellExecute = false,
                        RedirectStandardOutput = true,
                        RedirectStandardError = true,
                        CreateNoWindow = true
                    };
                    using var process = System.Diagnostics.Process.Start(psi);
                    if (process == null) return (false, "无法启动 simg2img");
                    var output = process.StandardOutput.ReadToEnd();
                    var error = process.StandardError.ReadToEnd();
                    process.WaitForExit();
                    return process.ExitCode == 0 ? (true, output) : (false, error);
                });

                if (result.Item1)
                {
                    AppendEdlLog("super 镜像合并成功");
                    foreach (var file in renamedFiles)
                        if (File.Exists(file)) File.Delete(file);
                }
                else
                {
                    AppendEdlLog($"合并 super 镜像失败: {result.Item2}");
                }
            }
            catch (Exception ex)
            {
                AppendEdlLog($"合并 super 镜像错误: {ex.Message}");
            }
        }

        private string? FindEdlImagesFolder(string basePath)
        {
            var imagesPath = Path.Combine(basePath, "IMAGES");
            if (Directory.Exists(imagesPath)) return imagesPath;
            if (Path.GetFileName(basePath).Equals("IMAGES", StringComparison.OrdinalIgnoreCase))
                return basePath;
            if (Directory.GetFiles(basePath, "rawprogram*.xml").Length > 0)
                return basePath;
            return null;
        }

        private async Task<bool> ValidateAndLoadEdlRawProgram(string imagesPath, string displayPath)
        {
            var xmlFiles = new List<string>();
            for (int i = 0; i <= 5; i++)
            {
                var xmlFile = Path.Combine(imagesPath, $"rawprogram{i}.xml");
                if (File.Exists(xmlFile)) xmlFiles.Add(xmlFile);
            }
            if (xmlFiles.Count == 0)
            {
                xmlFiles = Directory.GetFiles(imagesPath, "rawprogram*.xml")
                    .OrderBy(f =>
                    {
                        var fileName = Path.GetFileNameWithoutExtension(f);
                        var m = Regex.Match(fileName, @"\d+");
                        return m.Success ? int.Parse(m.Value) : int.MaxValue;
                    })
                    .ToList();
            }

            if (xmlFiles.Count == 0)
            {
                AppendEdlLog("未找到 rawprogram*.xml");
                System.Windows.MessageBox.Show("未找到 rawprogram*.xml", "错误", MessageBoxButton.OK, MessageBoxImage.Error);
                return false;
            }

            _edlRomImagesPath = imagesPath;
            _edlRawProgramFiles = xmlFiles.ToArray();
            var romPath = E<TextBox>("EdlRomPathTextBox");
            if (romPath != null) romPath.Text = displayPath;

            _edlXmlFileItems.Clear();
            foreach (var xmlFile in xmlFiles)
            {
                _edlXmlFileItems.Add(new EdlXmlFileItem
                {
                    Name = Path.GetFileName(xmlFile),
                    FullPath = xmlFile,
                    IsSelected = false
                });
            }
            var xmlList = E<ListBox>("EdlXmlList");
            if (xmlList != null)
            {
                xmlList.ItemsSource = null;
                xmlList.ItemsSource = _edlXmlFileItems;
                xmlList.DisplayMemberPath = "Name";
                xmlList.ItemTemplate = BuildEdlXmlItemTemplate();
            }

            _edlRows.Clear();
            var grid = E<DataGrid>("EdlPartitionGrid");
            if (grid != null) grid.ItemsSource = null;
            AppendEdlLog($"找到 {xmlFiles.Count} 个 XML 文件");
            _ = CheckAndMergeEdlSuperPartitionAsync(displayPath, imagesPath);
            return true;
        }

        private DataTemplate? BuildEdlXmlItemTemplate()
        {
            var factory = new FrameworkElementFactory(typeof(CheckBox));
            factory.SetBinding(CheckBox.IsCheckedProperty, new System.Windows.Data.Binding("IsSelected")
            {
                Mode = System.Windows.Data.BindingMode.TwoWay,
                UpdateSourceTrigger = System.Windows.Data.UpdateSourceTrigger.PropertyChanged
            });
            factory.SetValue(CheckBox.ContentProperty, new System.Windows.Data.Binding("Name"));
            factory.SetValue(CheckBox.MarginProperty, new Thickness(6, 2, 0, 2));
            factory.SetValue(CheckBox.VerticalAlignmentProperty, VerticalAlignment.Center);
            var dt = new DataTemplate(typeof(EdlXmlFileItem)) { VisualTree = factory };
            return dt;
        }

        private async Task CheckAndMergeEdlSuperPartitionAsync(string romBaseDir, string imagesPath)
        {
            try
            {
                var superImgPath = Path.Combine(imagesPath, "super.img");
                if (File.Exists(superImgPath)) { AppendEdlLog("super.img 已存在"); return; }

                var superMergeService = new SuperMergeService(AppendEdlLog, UpdateEdlProgress);
                var jsonPath = superMergeService.FindSuperDefJson(romBaseDir);
                if (string.IsNullOrEmpty(jsonPath)) return;

                var config = superMergeService.ParseSuperDefJson(jsonPath);
                if (config == null) { AppendEdlLog("解析 super_def.json 失败"); return; }

                var partitionsWithPath = config.Partitions.Where(p => !string.IsNullOrEmpty(p.Path)).ToList();
                if (partitionsWithPath.Count == 0) { AppendEdlLog("super_def.json 中没有需要合并的分区"); return; }

                var result = System.Windows.MessageBox.Show(
                    $"检测到 {partitionsWithPath.Count} 个分区需要合并到 super.img，是否合并？",
                    "合并 Super 分区", MessageBoxButton.YesNo, MessageBoxImage.Question);
                if (result != MessageBoxResult.Yes) { AppendEdlLog("用户取消 super 合并"); return; }

                AppendEdlLog("开始合并 Super 分区...");
                var success = await superMergeService.MergeSuperAsync(imagesPath, config, romBaseDir);
                if (success)
                {
                    AppendEdlLog("Super 分区合并完成！");
                    if (_edlRawProgramFiles != null && _edlRawProgramFiles.Length > 0 && _edlRows.Count > 0)
                        LoadEdlPartitionsFromXml();
                    else
                        AppendEdlLog("请选择 XML 文件并点击『加载』查看更新后的分区列表。");
                }
                else
                {
                    AppendEdlLog("Super 分区合并失败");
                }
            }
            catch (Exception ex)
            {
                AppendEdlLog($"检查 super 分区错误: {ex.Message}");
            }
        }

        private void LoadEdlPartitionsFromXml()
        {
            if (_edlRawProgramFiles == null || _edlRawProgramFiles.Length == 0) return;
            if (string.IsNullOrEmpty(_edlRomImagesPath))
                _edlRomImagesPath = Path.GetDirectoryName(_edlRawProgramFiles[0]);

            _edlRows.Clear();
            int totalPartitions = 0;

            foreach (var file in _edlRawProgramFiles)
            {
                var xmlDir = Path.GetDirectoryName(file) ?? _edlRomImagesPath ?? "";
                try
                {
                    var xmlDoc = XDocument.Load(file);
                    var programs = xmlDoc.Descendants("program");
                    foreach (var program in programs)
                    {
                        var fileName = program.Attribute("filename")?.Value ?? "";
                        var label = program.Attribute("label")?.Value ?? "";
                        var sizeKB = program.Attribute("size_in_KB")?.Value ?? "0";
                        var startSector = program.Attribute("start_sector")?.Value ?? "0";
                        var numPartitionSectors = program.Attribute("num_partition_sectors")?.Value ?? "0";
                        var physicalPartitionNumber = program.Attribute("physical_partition_number")?.Value ?? "0";
                        double sizeInKB = double.TryParse(sizeKB, out var parsedSize) ? parsedSize : 0;
                        string sizeFormatted;
                        if (sizeInKB >= 1048576)
                            sizeFormatted = $"{sizeInKB / 1048576:F2} GB";
                        else if (sizeInKB >= 1024)
                            sizeFormatted = $"{sizeInKB / 1024:F2} MB";
                        else
                            sizeFormatted = $"{sizeInKB:F2} KB";

                        var searchPath = !string.IsNullOrEmpty(_edlRomImagesPath) ? _edlRomImagesPath : xmlDir;
                        var filePath = string.IsNullOrEmpty(fileName) ? "" : Path.Combine(searchPath, fileName);
                        var fileExists = !string.IsNullOrEmpty(filePath) && File.Exists(filePath);
                        string displayFileName = fileName;
                        if (!fileExists && !string.IsNullOrEmpty(fileName) &&
                            Regex.IsMatch(fileName, @"^super\.\d+\.[a-fA-F0-9]+\.img$"))
                        {
                            var superImgPath = Path.Combine(searchPath, "super.img");
                            if (File.Exists(superImgPath))
                            {
                                filePath = superImgPath;
                                fileExists = true;
                                displayFileName = "super.img";
                            }
                        }

                        if (!string.IsNullOrEmpty(fileName))
                        {
                            ulong firstLba = ulong.TryParse(startSector, out var start) ? start : 0;
                            ulong numSectors = ulong.TryParse(numPartitionSectors, out var sectors) ? sectors : 0;
                            ulong lastLba = numSectors > 0 ? firstLba + numSectors - 1 : 0;
                            ulong sizeBytes = (ulong)(sizeInKB * 1024);
                            string actualSizeFormatted = sizeFormatted;
                            if (sizeInKB == 0 && fileExists && File.Exists(filePath))
                            {
                                try
                                {
                                    var fileInfo = new FileInfo(filePath);
                                    sizeBytes = (ulong)fileInfo.Length;
                                    double fileSizeKB = sizeBytes / 1024.0;
                                    if (fileSizeKB >= 1048576) actualSizeFormatted = $"{fileSizeKB / 1048576:F2} GB";
                                    else if (fileSizeKB >= 1024) actualSizeFormatted = $"{fileSizeKB / 1024:F2} MB";
                                    else actualSizeFormatted = $"{fileSizeKB:F2} KB";
                                    if (numSectors == 0)
                                    {
                                        numSectors = sizeBytes / 4096;
                                        lastLba = numSectors > 0 ? firstLba + numSectors - 1 : 0;
                                    }
                                }
                                catch { }
                            }

                            _edlRows.Add(new EdlPartitionRow
                            {
                                IsSelected = fileExists,
                                Name = string.IsNullOrEmpty(label) ? fileName : label,
                                Lun = int.TryParse(physicalPartitionNumber, out var lun) ? lun : 0,
                                FirstLBA = firstLba,
                                LastLBA = lastLba,
                                SizeFormatted = actualSizeFormatted,
                                SizeBytes = sizeBytes,
                                FilePath = fileExists ? filePath : $"[NOT FOUND] {filePath}",
                                NumSectors = numSectors > 0 ? numSectors.ToString() : numPartitionSectors,
                                SectorSize = "4096"
                            });
                            totalPartitions++;
                        }
                    }
                    AppendEdlLog($"解析: {Path.GetFileName(file)}");
                }
                catch (Exception ex)
                {
                    AppendEdlLog($"解析 {Path.GetFileName(file)} 错误: {ex.Message}");
                }
            }

            var grid = E<DataGrid>("EdlPartitionGrid");
            if (grid != null)
            {
                grid.ItemsSource = null;
                grid.ItemsSource = _edlRows.ToList();
            }
            var existingFiles = _edlRows.Count(r => !r.FilePath.StartsWith("[NOT FOUND]"));
            var info = E<TextBlock>("EdlRomInfoText");
            if (info != null)
                info.Text = $"共 {totalPartitions} 个分区，{existingFiles} 个文件可用 | {GetEdlRomPackageKindName(_edlRomPackage.Kind)}";
            AppendEdlLog($"已加载 {totalPartitions} 个分区（来自 {_edlRawProgramFiles.Length} 个 XML 文件）");
        }

        private static string GetEdlRomPackageKindName(RomPackageKind kind) => kind switch
        {
            RomPackageKind.OfficialSfp => "官方包",
            RomPackageKind.ThirdParty => "第三方包",
            _ => "未知"
        };

        private void LogEdlRomPackage()
        {
            AppendEdlLog($"ROM 包类型: {GetEdlRomPackageKindName(_edlRomPackage.Kind)}");
        }

        private void EdlXmlAll_Click(object sender, RoutedEventArgs e)
        {
            foreach (var item in _edlXmlFileItems) item.IsSelected = true;
        }

        private void EdlXmlNone_Click(object sender, RoutedEventArgs e)
        {
            foreach (var item in _edlXmlFileItems) item.IsSelected = false;
        }

        private void EdlLoad_Click(object sender, RoutedEventArgs e)
        {
            EnsureEdl();
            var selectedXmls = _edlXmlFileItems.Where(x => x.IsSelected).ToList();
            if (selectedXmls.Count == 0)
            {
                AppendEdlLog("请先选择 XML 文件");
                System.Windows.MessageBox.Show("请先勾选要加载的 rawprogram XML 文件", "提示", MessageBoxButton.OK, MessageBoxImage.Information);
                return;
            }
            _edlRawProgramFiles = selectedXmls.Select(x => x.FullPath).ToArray();
            AppendEdlLog($"加载 {selectedXmls.Count} 个 XML 文件: {string.Join(", ", selectedXmls.Select(x => x.Name))}");
            LoadEdlPartitionsFromXml();
        }

        private void EdlSearch_TextChanged(object sender, TextChangedEventArgs e)
        {
            var box = E<TextBox>("EdlSearchBox");
            var grid = E<DataGrid>("EdlPartitionGrid");
            if (box == null || grid == null) return;
            var searchText = box.Text?.Trim().ToLower() ?? "";
            var filtered = string.IsNullOrEmpty(searchText)
                ? _edlRows.ToList()
                : _edlRows.Where(r => r.Name.ToLower().Contains(searchText)).ToList();
            grid.ItemsSource = null;
            grid.ItemsSource = filtered;
        }

        private void EdlPartitionGrid_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (sender is DataGrid dg && dg.SelectedItem != null)
                dg.SelectedItem = null;
        }

        private void EdlPartitionGrid_MouseDoubleClick(object sender, MouseButtonEventArgs e)
        {
            var grid = E<DataGrid>("EdlPartitionGrid");
            if (grid == null || grid.SelectedItem is not EdlPartitionRow row) return;
            var f = PickFile($"为分区 {row.Name} 选择文件", "镜像文件 (*.img;*.bin;*.mbn)|*.img;*.bin;*.mbn|所有文件 (*.*)|*.*");
            if (string.IsNullOrEmpty(f)) return;
            row.FilePath = f;
            row.IsSelected = true;
            try
            {
                var fi = new FileInfo(f);
                row.SizeBytes = (ulong)fi.Length;
                row.SizeFormatted = FormatEdlSize((ulong)fi.Length);
                var sectorSize = (_edl?.StorageType == "emmc") ? 512 : 4096;
                var numSectors = (ulong)fi.Length / (ulong)sectorSize;
                row.NumSectors = numSectors.ToString();
                if (row.FirstLBA > 0) row.LastLBA = row.FirstLBA + numSectors - 1;
                AppendEdlLog($"为 {row.Name} 选择文件: {Path.GetFileName(f)} ({FormatEdlSize((ulong)fi.Length)})");
            }
            catch (Exception ex)
            {
                AppendEdlLog($"警告: 读取文件信息失败: {ex.Message}");
            }
            var dg2 = E<DataGrid>("EdlPartitionGrid");
            if (dg2 != null) dg2.Items.Refresh();
        }

        private static string FormatEdlSize(ulong bytes)
        {
            const double KB = 1024, MB = KB * 1024, GB = MB * 1024;
            if (bytes >= GB) return Math.Round(bytes / GB, 2) + " GB";
            if (bytes >= MB) return Math.Round(bytes / MB, 2) + " MB";
            if (bytes >= KB) return Math.Round(bytes / KB, 2) + " KB";
            return bytes + " B";
        }

        // ---------- Enter Firehose ----------
        private async void EdlEnterFirehose_Click(object sender, RoutedEventArgs e)
        {
            EnsureEdl();
            var devPrg = E<TextBox>("EdlDevPrgTextBox")?.Text ?? "";
            if (string.IsNullOrWhiteSpace(devPrg))
            {
                AppendEdlLog("请先选择设备编程器文件");
                return;
            }
            _edlCts?.Cancel();
            _edlCts = new CancellationTokenSource();
            var token = _edlCts.Token;
            SetEdlButtonEnabled("EdlEnterFirehoseButton", false);
            try
            {
                AppendEdlLog("等待 EDL 端口 (9008)...");
                var port = await _edl!.WaitForEdlPortAsync(token);
                if (token.IsCancellationRequested) { AppendEdlLog("进入 Firehose 已取消。"); return; }
                AppendEdlLog("设备已连接: " + port);

                AppendEdlLog("发送设备编程器...");
                var ok = await _edl.SendProgrammerAsync(port, devPrg);
                if (token.IsCancellationRequested) { AppendEdlLog("进入 Firehose 已取消。"); return; }
                if (!ok) { AppendEdlLog("发送编程器失败"); return; }

                var digest = E<TextBox>("EdlDigestTextBox")?.Text ?? "";
                if (!string.IsNullOrWhiteSpace(digest))
                {
                    AppendEdlLog("发送摘要...");
                    ok = await _edl.SendDigestsAsync(port, digest);
                    if (token.IsCancellationRequested) { AppendEdlLog("进入 Firehose 已取消。"); return; }
                    if (!ok) { AppendEdlLog("发送摘要失败"); return; }
                }

                AppendEdlLog("发送校验命令...");
                ok = await _edl.SendVerifyAsync(port);
                if (token.IsCancellationRequested) { AppendEdlLog("进入 Firehose 已取消。"); return; }
                if (!ok) { AppendEdlLog("校验失败"); return; }

                var sig = E<TextBox>("EdlSigTextBox")?.Text ?? "";
                if (!string.IsNullOrWhiteSpace(sig))
                {
                    AppendEdlLog("发送签名...");
                    ok = await _edl.SendDigestsAsync(port, sig);
                    if (token.IsCancellationRequested) { AppendEdlLog("进入 Firehose 已取消。"); return; }
                    if (!ok) { AppendEdlLog("发送签名失败"); return; }
                }

                AppendEdlLog("发送 sha256init 命令...");
                ok = await _edl.SendSha256InitAsync(port);
                if (token.IsCancellationRequested) { AppendEdlLog("进入 Firehose 已取消。"); return; }
                if (!ok) { AppendEdlLog("sha256init 失败"); return; }

                AppendEdlLog("配置中...");
                ok = await _edl.ConfigureAsync(port);
                if (token.IsCancellationRequested) { AppendEdlLog("进入 Firehose 已取消。"); return; }
                if (!ok) { AppendEdlLog("配置失败"); return; }

                _edlPort = port;
                AppendEdlLog("Firehose 模式进入成功！");
            }
            catch (OperationCanceledException)
            {
                AppendEdlLog("进入 Firehose 已取消。");
            }
            catch (Exception ex)
            {
                AppendEdlLog("错误: " + ex.Message);
            }
            finally
            {
                _edlCts = null;
                SetEdlButtonEnabled("EdlEnterFirehoseButton", true);
            }
        }

        private void SetEdlButtonEnabled(string name, bool enabled)
        {
            this.Dispatcher.BeginInvoke(new Action(() =>
            {
                var b = E<System.Windows.Controls.Button>(name);
                if (b != null) b.IsEnabled = enabled;
            }));
        }

        // ---------- Read Partitions ----------
        private async void EdlReadPartitions_Click(object sender, RoutedEventArgs e)
        {
            EnsureEdl();
            SetEdlButtonEnabled("EdlReadPartitionsButton", false);
            try
            {
                AppendEdlLog("等待 EDL 端口 (9008)...");
                var port = await _edl!.WaitForEdlPortAsync();
                AppendEdlLog("设备已连接: " + port);
                AppendEdlLog("配置中...");
                var ok = await _edl.ConfigureAsync(port);
                if (!ok) { AppendEdlLog("配置失败"); return; }
                AppendEdlLog("测试读写模式...");
                var mode = await _edl.TestRwModeAsync(port);
                AppendEdlLog("读写模式: " + mode.Item1 + (string.IsNullOrEmpty(mode.Item2) ? "" : (" " + mode.Item2)));
                _edlPort = port;

                AppendEdlLog("读取分区表...");
                var parts = await _edl.ReadPartitionTableAsync(port, mode.Item1);
                if (parts == null || parts.Count == 0) { AppendEdlLog("未找到分区"); return; }

                var newRows = new ObservableCollection<EdlPartitionRow>();
                foreach (var p in parts)
                {
                    newRows.Add(new EdlPartitionRow
                    {
                        Name = p.Name,
                        Lun = p.Lun,
                        FirstLBA = p.FirstLBA,
                        LastLBA = p.LastLBA,
                        SizeBytes = p.SizeBytes,
                        SizeFormatted = FormatEdlSize(p.SizeBytes),
                        TypeGuid = p.TypeGuid
                    });
                }
                _edlRows.Clear();
                foreach (var r in newRows) _edlRows.Add(r);
                var grid = E<DataGrid>("EdlPartitionGrid");
                if (grid != null)
                {
                    grid.ItemsSource = null;
                    grid.ItemsSource = _edlRows.ToList();
                }
                AppendEdlLog($"找到 {parts.Count} 个分区");
            }
            catch (Exception ex)
            {
                AppendEdlLog("错误: " + ex.Message);
            }
            finally
            {
                SetEdlButtonEnabled("EdlReadPartitionsButton", true);
            }
        }

        // ---------- Read Selected (backup) ----------
        private async void EdlReadSelected_Click(object sender, RoutedEventArgs e)
        {
            EnsureEdl();
            var result = System.Windows.MessageBox.Show("选择备份方式：\n\n是 = 自动备份选定的分区\n否 = 按自定义 XML 备份\n取消 = 退出",
                "备份方式", MessageBoxButton.YesNoCancel, MessageBoxImage.Question);
            if (result == MessageBoxResult.Cancel) return;
            if (result == MessageBoxResult.Yes)
                await ReadEdlSelectedPartitionsAuto();
            else
                await ReadEdlByCustomXml();
        }

        private async Task ReadEdlSelectedPartitionsAuto()
        {
            var selected = _edlRows.Where(r => r.IsSelected).ToList();
            if (selected.Count == 0) { AppendEdlLog("未选择任何分区"); return; }

            var folder = PickFolder("选择备份输出文件夹");
            if (string.IsNullOrEmpty(folder)) return;
            var destBase = folder;

            var superPartitions = selected.Where(r => EdlService.IsSuperPartition(r.Name)).ToList();
            var otherPartitions = selected.Where(r => !EdlService.IsSuperPartition(r.Name)).OrderBy(r => r.SizeBytes).ToList();

            _edlCts = new CancellationTokenSource();
            SetEdlButtonEnabled("EdlReadSelectedButton", false);
            try
            {
                AppendEdlLog("等待 EDL 端口...");
                var port = await _edl!.WaitForEdlPortAsync(_edlCts.Token);
                AppendEdlLog("设备已连接: " + port);
                AppendEdlLog("配置中...");
                var ok = await _edl.ConfigureAsync(port);
                if (!ok) { AppendEdlLog("配置失败"); return; }
                AppendEdlLog("测试读写模式...");
                var mode = await _edl.TestRwModeAsync(port);
                AppendEdlLog("读写模式: " + mode.rwmode);

                if (otherPartitions.Count > 0)
                {
                    AppendEdlLog($"先备份 {otherPartitions.Count} 个普通分区...");
                    foreach (var r in otherPartitions)
                    {
                        if (_edlCts.Token.IsCancellationRequested) { AppendEdlLog("任务已取消"); break; }
                        AppendEdlLog($"读取分区: {r.Name} ({FormatEdlSize(r.SizeBytes)})...");
                        var outPath = await _edl.BackupPartitionAsync(port, mode.rwmode, r.ToEntry());
                        if (outPath == null) { AppendEdlLog("失败: " + r.Name); continue; }
                        var dest = Path.Combine(destBase, r.Name + ".img");
                        try { File.Copy(outPath, dest, true); AppendEdlLog("已保存: " + dest); }
                        catch { AppendEdlLog("复制失败: " + r.Name); }
                    }
                }

                if (superPartitions.Count > 0 && !_edlCts.Token.IsCancellationRequested)
                {
                    AppendEdlLog("正在备份 super 分区（可能需要较长时间）...");
                    foreach (var r in superPartitions)
                    {
                        if (_edlCts.Token.IsCancellationRequested) { AppendEdlLog("任务已取消"); break; }
                        AppendEdlLog($"读取 super 分区 ({FormatEdlSize(r.SizeBytes)})...");
                        var outPath = await _edl.BackupSuperPartitionAsync(port, mode.rwmode, destBase);
                        if (outPath == null) { AppendEdlLog("失败: " + r.Name); continue; }
                        var dest = Path.Combine(destBase, "super.img");
                        if (outPath != dest)
                        {
                            try
                            {
                                if (File.Exists(dest)) File.Delete(dest);
                                File.Move(outPath, dest);
                                AppendEdlLog("已保存: " + dest);
                            }
                            catch { AppendEdlLog("重命名失败，文件位于: " + outPath); }
                        }
                        else
                        {
                            AppendEdlLog("已保存: " + dest);
                        }
                    }
                }

                AppendEdlLog("备份选定分区完成");
                if (E<CheckBox>("EdlExportXmlCheckBox")?.IsChecked == true)
                    ExportEdlPartitionsToXml(selected, destBase);
            }
            catch (OperationCanceledException)
            {
                AppendEdlLog("任务已取消");
            }
            catch (Exception ex)
            {
                AppendEdlLog("错误: " + ex.Message);
            }
            finally
            {
                _edlCts = null;
                SetEdlButtonEnabled("EdlReadSelectedButton", true);
            }
        }

        private async Task ReadEdlByCustomXml()
        {
            var dlg = new OpenFileDialog { Title = "选择用于读取分区的 XML 文件", Filter = "XML 文件 (*.xml)|*.xml|所有文件 (*.*)|*.*", Multiselect = true };
            if (dlg.ShowDialog(this) != true || dlg.FileNames.Length == 0) return;
            var xmlFiles = dlg.FileNames.ToList();

            _edlCts = new CancellationTokenSource();
            SetEdlButtonEnabled("EdlReadSelectedButton", false);
            try
            {
                AppendEdlLog("等待 EDL 端口...");
                var port = await _edl!.WaitForEdlPortAsync(_edlCts.Token);
                AppendEdlLog("设备已连接: " + port);
                AppendEdlLog("配置中...");
                var ok = await _edl.ConfigureAsync(port);
                if (!ok) { AppendEdlLog("配置失败"); return; }
                AppendEdlLog("测试读写模式...");
                var mode = await _edl.TestRwModeAsync(port);
                AppendEdlLog("读写模式: " + mode.rwmode + (string.IsNullOrEmpty(mode.gptmainMode) ? "" : (" " + mode.gptmainMode)));

                AppendEdlLog($"按自定义 XML 读取 ({xmlFiles.Count} 个文件)...");
                var outDir = await _edl.ReadByXmlAsync(port, xmlFiles, mode.rwmode);
                if (outDir == null)
                    AppendEdlLog("按 XML 读取失败");
                else
                    AppendEdlLog($"按 XML 读取完成。输出: {outDir}");
            }
            catch (OperationCanceledException)
            {
                AppendEdlLog("任务已取消");
            }
            catch (Exception ex)
            {
                AppendEdlLog("错误: " + ex.Message);
            }
            finally
            {
                _edlCts = null;
                SetEdlButtonEnabled("EdlReadSelectedButton", true);
            }
        }

        private void ExportEdlPartitionsToXml(List<EdlPartitionRow> partitions, string outputDir)
        {
            try
            {
                var groupedByLun = partitions.GroupBy(r => r.Lun).OrderBy(g => g.Key);
                foreach (var lunGroup in groupedByLun)
                {
                    var lun = lunGroup.Key;
                    var xmlPath = Path.Combine(outputDir, $"rawprogram_{lun}_backup.xml");
                    var doc = new XDocument(
                        new XDeclaration("1.0", "utf-8", null),
                        new XElement("data")
                    );
                    var dataElement = doc.Element("data")!;
                    dataElement.Add(new XComment(" Generated by VioletToolBox EDL "));
                    dataElement.Add(new XComment($" Export time: {DateTime.Now:yyyy-MM-dd HH:mm:ss} "));
                    dataElement.Add(new XComment($" LUN {lun} - {lunGroup.Count()} partitions "));

                    foreach (var partition in lunGroup.OrderBy(p => p.FirstLBA))
                    {
                        var sectorSize = 4096;
                        if (!string.IsNullOrEmpty(partition.SectorSize) && int.TryParse(partition.SectorSize, out var parsedSize))
                            sectorSize = parsedSize;

                        var numSectors = partition.LastLBA - partition.FirstLBA + 1;
                        if (!string.IsNullOrEmpty(partition.NumSectors) && ulong.TryParse(partition.NumSectors, out var parsedNumSectors))
                            numSectors = parsedNumSectors;

                        var startByteHex = $"0x{partition.FirstLBA * (ulong)sectorSize:x}";
                        var sizeInKB = (numSectors * (ulong)sectorSize) / 1024.0;
                        var fileName = partition.Name + ".img";

                        dataElement.Add(new XElement("program",
                            new XAttribute("SECTOR_SIZE_IN_BYTES", sectorSize.ToString()),
                            new XAttribute("file_sector_offset", "0"),
                            new XAttribute("filename", fileName),
                            new XAttribute("label", partition.Name),
                            new XAttribute("num_partition_sectors", numSectors.ToString()),
                            new XAttribute("partofsingleimage", "false"),
                            new XAttribute("physical_partition_number", lun.ToString()),
                            new XAttribute("readbackverify", "false"),
                            new XAttribute("size_in_KB", sizeInKB.ToString("F1")),
                            new XAttribute("sparse", "false"),
                            new XAttribute("start_byte_hex", startByteHex),
                            new XAttribute("start_sector", partition.FirstLBA.ToString())
                        ));
                    }
                    doc.Save(xmlPath);
                    AppendEdlLog($"已导出 XML: {xmlPath}");
                }
            }
            catch (Exception ex)
            {
                AppendEdlLog($"导出 XML 失败: {ex.Message}");
            }
        }

        // ---------- Write Selected / Start Flash / Erase / Stop ----------
        private static readonly string[] EdlGptMainPartitionNames = new[] {
            "PrimaryGPT", "gpt_main0", "gpt_main1", "gpt_main2", "gpt_main3", "gpt_main4", "gpt_main5"
        };
        private static readonly string[] EdlGptBackupPartitionNames = new[] {
            "BackupGPT", "gpt_backup0", "gpt_backup1", "gpt_backup2", "gpt_backup3", "gpt_backup4", "gpt_backup5"
        };
        private static readonly string[] EdlGptPartitionNames =
            EdlGptMainPartitionNames.Concat(EdlGptBackupPartitionNames).ToArray();

        private List<EdlPartitionRow> FilterEdlGptPartitions(List<EdlPartitionRow> gptPartitions)
        {
            var result = new List<EdlPartitionRow>();
            var processedLuns = new HashSet<int>();
            foreach (var p in gptPartitions.Where(p => EdlGptMainPartitionNames.Contains(p.Name, StringComparer.OrdinalIgnoreCase)))
            {
                result.Add(p);
                processedLuns.Add(p.Lun);
                AppendEdlLog($"[GPT] 将刷写 {p.Name} (LUN{p.Lun})");
            }
            foreach (var p in gptPartitions.Where(p => EdlGptBackupPartitionNames.Contains(p.Name, StringComparer.OrdinalIgnoreCase)))
            {
                if (!processedLuns.Contains(p.Lun))
                {
                    result.Add(p);
                    AppendEdlLog($"[GPT] 将刷写 {p.Name} (LUN{p.Lun}) - 未找到 gpt_main");
                }
                else
                {
                    AppendEdlLog($"[GPT] 跳过 {p.Name} (LUN{p.Lun}) - gpt_main 已存在");
                }
            }
            return result;
        }

        private List<EdlPartitionRow> GetEdlSelectedValid()
        {
            return _edlRows.Where(r => r.IsSelected && !string.IsNullOrEmpty(r.FilePath) && !r.FilePath.StartsWith("[NOT FOUND]")).ToList();
        }

        private bool ConfirmEdlFlash(List<EdlPartitionRow> allSelected, out List<EdlPartitionRow> gptParts, out List<EdlPartitionRow> normalParts)
        {
            gptParts = new List<EdlPartitionRow>();
            normalParts = new List<EdlPartitionRow>();
            if (allSelected.Count == 0)
            {
                AppendEdlLog("没有有效分区（文件缺失）");
                System.Windows.MessageBox.Show("没有可刷写的有效分区\n\n提示：双击分区行可选择刷写文件。", "提示", MessageBoxButton.OK, MessageBoxImage.Information);
                return false;
            }
            var gptRaw = allSelected.Where(r => EdlGptPartitionNames.Contains(r.Name, StringComparer.OrdinalIgnoreCase)).ToList();
            normalParts = allSelected.Where(r => !EdlGptPartitionNames.Contains(r.Name, StringComparer.OrdinalIgnoreCase)).ToList();
            gptParts = FilterEdlGptPartitions(gptRaw);

            if (normalParts.Count > 0)
                AppendEdlLog($"[信息] 普通分区 (spoof 刷写): {string.Join(", ", normalParts.Take(5).Select(r => r.Name))}{(normalParts.Count > 5 ? $" 等 {normalParts.Count - 5} 个" : "")}");

            var totalCount = gptParts.Count + normalParts.Count;
            if (totalCount == 0) { AppendEdlLog("没有有效分区"); return false; }

            var confirmMsg = $"确认刷写 {totalCount} 个分区？\n\n" +
                string.Join(", ", gptParts.Concat(normalParts).Take(10).Select(r => r.Name)) +
                (totalCount > 10 ? $" 等 {totalCount - 10} 个" : "");
            var result = System.Windows.MessageBox.Show(confirmMsg, "确认刷写", MessageBoxButton.YesNo, MessageBoxImage.Question);
            if (result != MessageBoxResult.Yes) return false;

            var persist = normalParts.FirstOrDefault(r => r.Name.Equals("persist", StringComparison.OrdinalIgnoreCase));
            if (persist != null)
            {
                var pResult = System.Windows.MessageBox.Show("警告：刷写 persist 分区可能导致设备异常！\n\n是否继续刷写 persist？", "persist 分区警告", MessageBoxButton.YesNo, MessageBoxImage.Warning);
                if (pResult != MessageBoxResult.Yes)
                {
                    normalParts = normalParts.Where(r => !r.Name.Equals("persist", StringComparison.OrdinalIgnoreCase)).ToList();
                    AppendEdlLog("已跳过 persist 分区");
                }
            }
            var ocdt = normalParts.FirstOrDefault(r =>
                r.Name.Equals("ocdt", StringComparison.OrdinalIgnoreCase) &&
                !string.IsNullOrEmpty(r.FilePath) &&
                !r.FilePath.StartsWith("[NOT FOUND]"));
            if (ocdt != null)
            {
                var oResult = System.Windows.MessageBox.Show("警告：刷写 OCDT 分区可能影响设备型号信息！\n\n是否继续？", "OCDT 分区警告", MessageBoxButton.YesNo, MessageBoxImage.Warning);
                if (oResult != MessageBoxResult.Yes)
                {
                    normalParts = normalParts.Where(r => !r.Name.Equals("ocdt", StringComparison.OrdinalIgnoreCase)).ToList();
                    AppendEdlLog("已跳过 OCDT 分区");
                }
            }
            return true;
        }

        private async void EdlWriteSelected_Click(object sender, RoutedEventArgs e)
        {
            EnsureEdl();
            var allSelected = GetEdlSelectedValid();
            if (!ConfirmEdlFlash(allSelected, out var gptPartitions, out var normalPartitions)) return;

            _edlCts = new CancellationTokenSource();
            SetEdlButtonEnabled("EdlWriteSelectedButton", false);
            try
            {
                AppendEdlLog("等待 EDL 端口...");
                var port = await _edl!.WaitForEdlPortAsync(_edlCts.Token);
                AppendEdlLog("设备已连接: " + port);
                AppendEdlLog("配置中...");
                var ok = await _edl.ConfigureAsync(port);
                if (!ok) { AppendEdlLog("配置失败"); return; }
                var protectLun5 = E<CheckBox>("EdlProtectLun5CheckBox")?.IsChecked == true;
                if (protectLun5)
                {
                    var lun5Count = allSelected.Count(p => p.Lun == 5);
                    if (lun5Count > 0) AppendEdlLog($"[保护 LUN5] 跳过 {lun5Count} 个 LUN5 分区");
                }
                var sectorSize = _edl.StorageType == "emmc" ? 512 : 4096;

                if (gptPartitions.Count > 0)
                {
                    AppendEdlLog("第 1 步: 刷写 GPT 分区 (normal 模式)...");
                    var rwMode = await _edl.TestRwModeAsync(port);
                    foreach (var partition in gptPartitions)
                    {
                        if (_edlCts.Token.IsCancellationRequested) { AppendEdlLog("任务已取消"); return; }
                        if (protectLun5 && partition.Lun == 5) { AppendEdlLog($"[保护 LUN5] 跳过: {partition.Name}"); continue; }
                        AppendEdlLog($"[GPT] 刷写 {partition.Name} (LUN{partition.Lun})...");
                        ok = await _edl.FlashPartitionNormalAsync(port, rwMode.rwmode, partition.ToEntry(), partition.FilePath);
                        if (!ok) { AppendEdlLog($"[GPT] 刷写 {partition.Name} 失败"); return; }
                        AppendEdlLog($"[GPT] {partition.Name} 刷写成功");
                    }
                }
                if (normalPartitions.Count > 0)
                {
                    AppendEdlLog("第 2 步: 刷写普通分区 (spoof 模式)...");
                    var flashTasks = new List<EdlService.FlashPartitionInfo>();
                    foreach (var partition in normalPartitions)
                    {
                        if (protectLun5 && partition.Lun == 5) { AppendEdlLog($"[保护 LUN5] 跳过: {partition.Name}"); continue; }
                        flashTasks.Add(new EdlService.FlashPartitionInfo
                        {
                            Name = partition.Name,
                            FilePath = partition.FilePath,
                            Lun = partition.Lun.ToString(),
                            StartSector = partition.FirstLBA,
                            NumSectors = partition.LastLBA - partition.FirstLBA + 1,
                            SectorSize = sectorSize
                        });
                    }
                    if (flashTasks.Count > 0)
                    {
                        ok = await _edl.FlashPartitionsWithSpoofAsync(port, flashTasks, _edlCts.Token);
                        if (!ok) { AppendEdlLog("刷写失败"); return; }
                    }
                }
                AppendEdlLog("刷写完成");
                await ApplyEdlPatchXmls(port, allSelected, protectLun5, sectorSize);
                await EdlAutoRebootIfEnabled(port);
                AppendEdlLog("所有操作完成");
            }
            catch (OperationCanceledException)
            {
                AppendEdlLog("任务已取消");
            }
            catch (Exception ex)
            {
                AppendEdlLog("错误: " + ex.Message);
            }
            finally
            {
                _edlCts = null;
                SetEdlButtonEnabled("EdlWriteSelectedButton", true);
            }
        }

        private async void EdlStartFlash_Click(object sender, RoutedEventArgs e)
        {
            EnsureEdl();
            var devPrg = E<TextBox>("EdlDevPrgTextBox")?.Text ?? "";
            var digest = E<TextBox>("EdlDigestTextBox")?.Text ?? "";
            var sig = E<TextBox>("EdlSigTextBox")?.Text ?? "";
            if (string.IsNullOrWhiteSpace(devPrg) || string.IsNullOrWhiteSpace(digest) || string.IsNullOrWhiteSpace(sig))
            {
                AppendEdlLog("请先加载 DevPrg、Digest 和 Sig 文件");
                System.Windows.MessageBox.Show("请先加载 DevPrg、Digest 和 Sig 文件", "错误", MessageBoxButton.OK, MessageBoxImage.Error);
                return;
            }
            if (_edlRawProgramFiles == null || _edlRawProgramFiles.Length == 0 || string.IsNullOrEmpty(_edlRomImagesPath))
            {
                AppendEdlLog("未加载 ROM 包");
                return;
            }

            var allSelected = GetEdlSelectedValid();
            if (!ConfirmEdlFlash(allSelected, out var gptPartitions, out var normalPartitions)) return;

            _edlCts = new CancellationTokenSource();
            SetEdlButtonEnabled("EdlStartFlashButton", false);
            SetEdlButtonEnabled("EdlWriteSelectedButton", false);
            SetEdlButtonEnabled("EdlEnterFirehoseButton", false);
            try
            {
                var token = _edlCts.Token;
                AppendEdlLog("等待 EDL 端口...");
                var port = await _edl!.WaitForEdlPortAsync(token);
                AppendEdlLog("设备已连接: " + port);
                AppendEdlLog("检查设备是否处于 Firehose 模式...");
                var isInFirehose = await _edl.ConfigureAsync(port);

                if (!isInFirehose)
                {
                    AppendEdlLog("设备未进入 Firehose 模式，正在发送编程器文件...");
                    AppendEdlLog("发送编程器...");
                    var ok = await _edl.SendProgrammerAsync(port, devPrg);
                    if (token.IsCancellationRequested) { AppendEdlLog("任务已取消"); return; }
                    if (!ok) { AppendEdlLog("发送编程器失败"); return; }
                    AppendEdlLog("发送摘要...");
                    ok = await _edl.SendDigestsAsync(port, digest);
                    if (token.IsCancellationRequested) { AppendEdlLog("任务已取消"); return; }
                    if (!ok) { AppendEdlLog("发送摘要失败"); return; }
                    AppendEdlLog("发送校验命令...");
                    ok = await _edl.SendVerifyAsync(port);
                    if (token.IsCancellationRequested) { AppendEdlLog("任务已取消"); return; }
                    if (!ok) { AppendEdlLog("校验失败"); return; }
                    AppendEdlLog("发送签名...");
                    ok = await _edl.SendDigestsAsync(port, sig);
                    if (token.IsCancellationRequested) { AppendEdlLog("任务已取消"); return; }
                    if (!ok) { AppendEdlLog("发送签名失败"); return; }
                    AppendEdlLog("发送 sha256init 命令...");
                    ok = await _edl.SendSha256InitAsync(port);
                    if (token.IsCancellationRequested) { AppendEdlLog("任务已取消"); return; }
                    if (!ok) { AppendEdlLog("sha256init 失败"); return; }
                    AppendEdlLog("配置中...");
                    ok = await _edl.ConfigureAsync(port);
                    if (token.IsCancellationRequested) { AppendEdlLog("任务已取消"); return; }
                    if (!ok) { AppendEdlLog("配置失败"); return; }
                    AppendEdlLog("Firehose 模式进入成功！");
                    await Task.Delay(200, token);
                }
                else
                {
                    AppendEdlLog("设备已处于 Firehose 模式");
                }

                _edlPort = port;
                AppendEdlLog("开始刷写流程...");
                var protectLun5 = E<CheckBox>("EdlProtectLun5CheckBox")?.IsChecked == true;
                if (protectLun5)
                {
                    var lun5Count = allSelected.Count(p => p.Lun == 5);
                    if (lun5Count > 0) AppendEdlLog($"[保护 LUN5] 跳过 {lun5Count} 个 LUN5 分区");
                }
                var sectorSize = _edl.StorageType == "emmc" ? 512 : 4096;
                bool flashOk;

                if (gptPartitions.Count > 0)
                {
                    AppendEdlLog("第 1 步: 刷写 GPT 分区 (normal 模式)...");
                    var rwMode = await _edl.TestRwModeAsync(port);
                    foreach (var partition in gptPartitions)
                    {
                        if (token.IsCancellationRequested) { AppendEdlLog("任务已取消"); return; }
                        if (protectLun5 && partition.Lun == 5) { AppendEdlLog($"[保护 LUN5] 跳过: {partition.Name}"); continue; }
                        AppendEdlLog($"[GPT] 刷写 {partition.Name} (LUN{partition.Lun})...");
                        flashOk = await _edl.FlashPartitionNormalAsync(port, rwMode.rwmode, partition.ToEntry(), partition.FilePath);
                        if (!flashOk) { AppendEdlLog($"[GPT] 刷写 {partition.Name} 失败"); return; }
                        AppendEdlLog($"[GPT] {partition.Name} 刷写成功");
                    }
                }

                if (normalPartitions.Count > 0)
                {
                    AppendEdlLog("第 2 步: 刷写普通分区 (spoof 模式)...");
                    var flashTasks = new List<EdlService.FlashPartitionInfo>();
                    foreach (var partition in normalPartitions)
                    {
                        if (protectLun5 && partition.Lun == 5) { AppendEdlLog($"[保护 LUN5] 跳过: {partition.Name}"); continue; }
                        flashTasks.Add(new EdlService.FlashPartitionInfo
                        {
                            Name = partition.Name,
                            FilePath = partition.FilePath,
                            Lun = partition.Lun.ToString(),
                            StartSector = partition.FirstLBA,
                            NumSectors = partition.LastLBA - partition.FirstLBA + 1,
                            SectorSize = sectorSize
                        });
                    }
                    if (flashTasks.Count > 0)
                    {
                        flashOk = await _edl.FlashPartitionsWithSpoofAsync(port, flashTasks, token);
                        if (!flashOk) { AppendEdlLog("刷写失败"); return; }
                    }
                }

                AppendEdlLog("刷写完成");
                await ApplyEdlPatchXmls(port, allSelected, protectLun5, sectorSize);
                await EdlAutoRebootIfEnabled(port);
                AppendEdlLog("所有操作完成");
            }
            catch (OperationCanceledException)
            {
                AppendEdlLog("任务已取消");
            }
            catch (Exception ex)
            {
                AppendEdlLog("错误: " + ex.Message);
            }
            finally
            {
                _edlCts = null;
                SetEdlButtonEnabled("EdlStartFlashButton", true);
                SetEdlButtonEnabled("EdlWriteSelectedButton", true);
                SetEdlButtonEnabled("EdlEnterFirehoseButton", true);
            }
        }

        private async Task ApplyEdlPatchXmls(string port, List<EdlPartitionRow> allSelected, bool protectLun5, int sectorSize)
        {
            if (_edlRawProgramFiles == null || _edlRawProgramFiles.Length == 0) return;
            var skipPatch = E<CheckBox>("EdlSkipPatchCheckBox")?.IsChecked == true;
            AppendEdlLog(skipPatch ? "[跳过 Patch XML] 已跳过 patch XML 文件" : "应用 patch 文件...");
            var patchMode = await _edl!.TestRwModeAsync(port);
            var patchRwMode = patchMode.rwmode;
            var patchXmlFiles = _edlRawProgramFiles.AsEnumerable();
            if (skipPatch)
            {
                patchXmlFiles = Enumerable.Empty<string>();
            }
            else if (protectLun5)
            {
                patchXmlFiles = _edlRawProgramFiles.Where(f =>
                    !Path.GetFileName(f).Equals("rawprogram5.xml", StringComparison.OrdinalIgnoreCase));
                AppendEdlLog("[保护 LUN5] 跳过 patch5.xml");
            }
            var patchCount = await _edl.WritePatchXmlsAsync(port, patchXmlFiles, _edlRomImagesPath, patchRwMode);
            if (patchCount > 0)
                AppendEdlLog($"已应用 {patchCount} 个 patch 文件");
            else if (skipPatch)
                AppendEdlLog("[跳过 Patch XML] 用户设置跳过");
            else
                AppendEdlLog("未应用任何 patch 文件（文件可能不存在）");

            if (_edlRomPackage.IsThirdParty)
            {
                AppendEdlLog("第三方包：跳过 bootable storage drive 设置");
            }
            else
            {
                await _edl.SendSetBootableStorageDriveAsync(port);
            }
        }

        private async Task EdlAutoRebootIfEnabled(string port)
        {
            if (E<CheckBox>("EdlAutoRebootCheckBox")?.IsChecked == true)
            {
                AppendEdlLog("自动重启已开启，正在重启设备...");
                var rebootOk = await _edl!.RebootToEdlAsync(port);
                AppendEdlLog(rebootOk ? "设备重启命令发送成功！" : "警告：发送重启命令失败");
            }
        }

        private async void EdlEraseSelected_Click(object sender, RoutedEventArgs e)
        {
            EnsureEdl();
            var selected = _edlRows.Where(r => r.IsSelected).ToList();
            if (selected.Count == 0) { AppendEdlLog("未选择任何分区"); return; }

            var confirm = System.Windows.MessageBox.Show($"确认擦除 {selected.Count} 个选定分区？\n\n此操作不可恢复！",
                "确认擦除", MessageBoxButton.YesNo, MessageBoxImage.Warning);
            if (confirm != MessageBoxResult.Yes) return;

            _edlCts = new CancellationTokenSource();
            SetEdlButtonEnabled("EdlEraseSelectedButton", false);
            try
            {
                AppendEdlLog("等待 EDL 端口...");
                var port = await _edl!.WaitForEdlPortAsync(_edlCts.Token);
                AppendEdlLog("设备已连接: " + port);
                AppendEdlLog("配置中...");
                var ok = await _edl.ConfigureAsync(port);
                if (!ok) { AppendEdlLog("配置失败"); return; }
                AppendEdlLog("测试读写模式...");
                var mode = await _edl.TestRwModeAsync(port);
                AppendEdlLog("读写模式: " + mode.rwmode);

                foreach (var r in selected)
                {
                    if (_edlCts.Token.IsCancellationRequested) { AppendEdlLog("任务已取消"); break; }
                    AppendEdlLog($"擦除分区: {r.Name} (LUN{r.Lun})...");
                    ok = await _edl.ErasePartitionAsync(port, mode.rwmode, r.ToEntry());
                    AppendEdlLog(ok ? $"{r.Name} 擦除成功" : $"{r.Name} 擦除失败");
                }
                AppendEdlLog("擦除完成");
            }
            catch (OperationCanceledException)
            {
                AppendEdlLog("任务已取消");
            }
            catch (Exception ex)
            {
                AppendEdlLog("错误: " + ex.Message);
            }
            finally
            {
                _edlCts = null;
                SetEdlButtonEnabled("EdlEraseSelectedButton", true);
            }
        }

        private void EdlStop_Click(object sender, RoutedEventArgs e)
        {
            if (_edlCts != null)
            {
                _edlCts.Cancel();
                AppendEdlLog("正在停止当前操作...");
            }
        }

        private void EdlClearLog_Click(object sender, RoutedEventArgs e)
        {
            var logBox = E<TextBox>("EdlLogTextBox");
            if (logBox != null) logBox.Text = string.Empty;
        }
    }
}
