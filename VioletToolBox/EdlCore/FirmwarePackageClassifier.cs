using System;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using System.Xml;
using System.Xml.Linq;

namespace OplusEdlTool.Services
{
    public enum RomPackageKind
    {
        Unknown,
        OfficialSfp,
        ThirdParty
    }

    public sealed record RomPackageInfo(RomPackageKind Kind, string Reason)
    {
        public static readonly RomPackageInfo Unknown = new(RomPackageKind.Unknown, "not classified");

        public bool IsThirdParty => Kind == RomPackageKind.ThirdParty;
    }

    public static class FirmwarePackageClassifier
    {
        private const string VersionInfoName = "version_info.txt";
        private const string ChecksumManifestName = "all_files_checksum.txt";
        private const string ProjectConfigName = "Projectconfig.xml";
        private const string ImagesFolderName = "IMAGES";
        private const long MaximumTextFileBytes = 16L * 1024 * 1024;
        private const int MaximumXmlCharacters = 32 * 1024 * 1024;

        public static RomPackageInfo ClassifyRomFolder(string romRootPath)
        {
            if (string.IsNullOrWhiteSpace(romRootPath))
            {
                return new RomPackageInfo(RomPackageKind.ThirdParty, "路径为空");
            }

            string root;
            try
            {
                root = Path.TrimEndingDirectorySeparator(Path.GetFullPath(romRootPath));
            }
            catch (Exception ex) when (ex is ArgumentException or NotSupportedException or PathTooLongException)
            {
                return new RomPackageInfo(RomPackageKind.ThirdParty, "路径无效");
            }

            if (Path.GetFileName(root).Equals(ImagesFolderName, StringComparison.OrdinalIgnoreCase))
            {
                string? parent = Path.GetDirectoryName(root);
                if (!string.IsNullOrEmpty(parent))
                {
                    root = parent;
                }
            }

            bool hasVersionInfo = File.Exists(Path.Combine(root, VersionInfoName));
            bool hasChecksumManifest = File.Exists(Path.Combine(root, ChecksumManifestName));
            bool manifestHasProjectConfig = hasChecksumManifest &&
                ManifestContainsProjectConfig(Path.Combine(root, ChecksumManifestName));

            if (hasVersionInfo && hasChecksumManifest && manifestHasProjectConfig)
            {
                return new RomPackageInfo(
                    RomPackageKind.OfficialSfp,
                    $"{VersionInfoName} + {ChecksumManifestName} 校验通过, {ProjectConfigName}{DescribeProjectIds(ReadPackageProjectIds(root))}");
            }

            if (hasVersionInfo || hasChecksumManifest)
            {
                return new RomPackageInfo(
                    RomPackageKind.ThirdParty,
                    "SFP 标记文件不完整或清单未包含 Projectconfig.xml");
            }

            return new RomPackageInfo(
                RomPackageKind.ThirdParty,
                $"未找到 {VersionInfoName} / {ChecksumManifestName}");
        }

        private static string DescribeProjectIds(string[] projectIds) =>
            projectIds.Length == 0 ? string.Empty : $", 项目号: {string.Join(", ", projectIds)}";

        private static string[] ReadPackageProjectIds(string root)
        {
            string direct = Path.Combine(root, ProjectConfigName);
            if (File.Exists(direct))
            {
                return ReadProjectIds(direct);
            }

            string inImages = Path.Combine(root, ImagesFolderName, ProjectConfigName);
            return File.Exists(inImages) ? ReadProjectIds(inImages) : Array.Empty<string>();
        }

        private static string[] ReadProjectIds(string projectConfigPath)
        {
            XDocument? document = TryLoadXml(projectConfigPath);
            return document == null ? Array.Empty<string>() : ExtractProjectIds(document);
        }

        private static string[] ExtractProjectIds(XDocument document)
        {
            return document.Descendants()
                .Where(element => NameEquals(element, "program"))
                .Select(element => element.Attributes()
                    .FirstOrDefault(attribute => NameEquals(attribute, "project"))?.Value?.Trim())
                .Where(value => !string.IsNullOrEmpty(value))
                .Select(value => value!)
                .Where(value => uint.TryParse(value, NumberStyles.None, CultureInfo.InvariantCulture, out uint project) && project != 0)
                .Distinct(StringComparer.Ordinal)
                .OrderBy(value => value, StringComparer.Ordinal)
                .ToArray();
        }

        private static bool ManifestContainsProjectConfig(string manifestPath)
        {
            try
            {
                var info = new FileInfo(manifestPath);
                if (!info.Exists || info.Length <= 0 || info.Length > MaximumTextFileBytes)
                {
                    return false;
                }

                using var reader = new StreamReader(manifestPath, Encoding.UTF8, detectEncodingFromByteOrderMarks: true);
                string? line;
                while ((line = reader.ReadLine()) != null)
                {
                    if (line.Contains(ProjectConfigName, StringComparison.OrdinalIgnoreCase))
                    {
                        return true;
                    }
                }

                return false;
            }
            catch (Exception ex) when (ex is IOException or UnauthorizedAccessException)
            {
                return false;
            }
        }

        private static XDocument? TryLoadXml(string path)
        {
            try
            {
                var settings = new XmlReaderSettings
                {
                    DtdProcessing = DtdProcessing.Prohibit,
                    XmlResolver = null,
                    MaxCharactersInDocument = MaximumXmlCharacters
                };
                using var stream = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.Read);
                using var reader = XmlReader.Create(stream, settings);
                return XDocument.Load(reader, LoadOptions.None);
            }
            catch (Exception ex) when (ex is XmlException or IOException or UnauthorizedAccessException or InvalidOperationException)
            {
                return null;
            }
        }

        private static bool NameEquals(XElement element, string name) =>
            element.Name.LocalName.Equals(name, StringComparison.OrdinalIgnoreCase);

        private static bool NameEquals(XAttribute attribute, string name) =>
            attribute.Name.LocalName.Equals(name, StringComparison.OrdinalIgnoreCase);
    }
}
