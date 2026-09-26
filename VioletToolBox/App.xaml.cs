using System.Configuration;
using System.Data;
using System.IO;
using System.Windows;
using System.Text;

namespace WpfApp1
{
    /// <summary>
    /// Interaction logic for App.xaml
    /// </summary>
    public partial class App : System.Windows.Application
    {
        protected override void OnStartup(StartupEventArgs e)
        {
            Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);

            // 全局未处理异常兜底：写崩溃日志，防止静默崩溃/无提示闪退
            DispatcherUnhandledException += (s, args) =>
            {
                LogCrash("UI线程", args.Exception);
                // 刷机场景 UI 线程异常大多可恢复：记录后继续运行，避免窗口直接闪退
                args.Handled = true;
            };
            AppDomain.CurrentDomain.UnhandledException += (s, args) =>
            {
                LogCrash("AppDomain(致命)", args.ExceptionObject as System.Exception);
            };
            TaskScheduler.UnobservedTaskException += (s, args) =>
            {
                LogCrash("后台任务", args.Exception);
                args.SetObserved();
            };

            base.OnStartup(e);
        }

        /// <summary>将异常写入 %LocalAppData%\VioletToolBox\crash.log，供排查定位</summary>
        private static void LogCrash(string source, System.Exception ex)
        {
            try
            {
                if (ex == null) return;
                var dir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "VioletToolBox");
                Directory.CreateDirectory(dir);
                var line = string.Format("[{0:yyyy-MM-dd HH:mm:ss}] [{1}] {2}: {3}\r\n{4}\r\n---\r\n",
                    DateTime.Now, source, ex.GetType().FullName, ex.Message, ex.StackTrace ?? "");
                File.AppendAllText(Path.Combine(dir, "crash.log"), line, Encoding.UTF8);
            }
            catch
            {
                // 日志写入失败不影响程序运行
            }
        }
    }

}
