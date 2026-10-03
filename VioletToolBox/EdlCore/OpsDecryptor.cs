using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using System.Xml.Linq;

namespace OplusEdlTool.Services
{
    public class OpsDecryptor
    {
        private static readonly uint[] Key = new uint[] { 0x9ee3b5d1, 0x9d04ea5e, 0xabd51d67, 0xafcbafd2 };
        private static readonly byte[] Mbox5 = new byte[] { 0x60, 0x8a, 0x3f, 0x2d, 0x68, 0x6b, 0xd4, 0x23, 0x51, 0x0c, 0xd0, 0x95, 0xbb, 0x40, 0xe9, 0x76, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0a, 0x00 };
        private static readonly byte[] Mbox6 = new byte[] { 0xAA, 0x69, 0x82, 0x9E, 0x5D, 0xDE, 0xB1, 0x3D, 0x30, 0xBB, 0x81, 0xA3, 0x46, 0x65, 0xa3, 0xe1, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0a, 0x00 };
        private static readonly byte[] Mbox4 = new byte[] { 0xC4, 0x5D, 0x05, 0x71, 0x99, 0xDD, 0xBB, 0xEE, 0x29, 0xA1, 0x6D, 0xC7, 0xAD, 0xBF, 0xA4, 0x3F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0a, 0x00 };
        private byte[] _currentMbox = Mbox5;
        private Action<string>? _log;

        public OpsDecryptor(Action<string>? log = null) { _log = log; }
        private void Log(string msg) => _log?.Invoke(msg);

        public string? Decrypt(string opsFilePath, string? outputDir = null)
        {
            if (!File.Exists(opsFilePath)) { Log($"File not found: {opsFilePath}"); return null; }
            
            string basePath = Path.GetDirectoryName(opsFilePath) ?? ".";
            string extractPath = outputDir ?? Path.Combine(basePath, "extract");
            
            if (Directory.Exists(extractPath)) Directory.Delete(extractPath, true);
            Directory.CreateDirectory(extractPath);

            string? xml = null;
            foreach (var mbox in new[] { Mbox5, Mbox6, Mbox4 })
            {
                _currentMbox = mbox;
                xml = ExtractXml(opsFilePath);
                if (xml != null) { Log($"Found valid key"); break; }
            }
            
            if (xml == null) { Log("Unsupported key!"); return null; }

            File.WriteAllText(Path.Combine(extractPath, "settings.xml"), xml);
            
            var root = XElement.Parse(xml);
            foreach (var child in root.Elements())
            {
                if (child.Name.LocalName == "SAHARA")
                {
                    foreach (var item in child.Elements("File"))
                    {
                        string wfilename = item.Attribute("Path")?.Value ?? "";
                        if (string.IsNullOrEmpty(wfilename)) continue;
                        long start = long.Parse(item.Attribute("FileOffsetInSrc")?.Value ?? "0") * 0x200;
                        long length = long.Parse(item.Attribute("SizeInByteInSrc")?.Value ?? "0");
                        DecryptFile(opsFilePath, extractPath, wfilename, start, length);
                    }
                }
                else if (child.Name.LocalName == "UFS_PROVISION")
                {
                    foreach (var item in child.Elements("File"))
                    {
                        string wfilename = item.Attribute("Path")?.Value ?? "";
                        if (string.IsNullOrEmpty(wfilename)) continue;
                        long start = long.Parse(item.Attribute("FileOffsetInSrc")?.Value ?? "0") * 0x200;
                        long length = long.Parse(item.Attribute("SizeInByteInSrc")?.Value ?? "0");
                        CopyFile(opsFilePath, extractPath, wfilename, start, length);
                    }
                }
                else if (child.Name.LocalName.Contains("Program"))
                {
                    foreach (var item in child.Elements())
                    {
                        ExtractProgramItem(item, opsFilePath, extractPath);
                    }
                }
            }
            
            Log($"Done. Extracted files to {extractPath}");
            return extractPath;
        }

        private void ExtractProgramItem(XElement item, string srcFile, string destPath)
        {
            string wfilename = item.Attribute("filename")?.Value ?? "";
            if (!string.IsNullOrEmpty(wfilename))
            {
                long start = long.Parse(item.Attribute("FileOffsetInSrc")?.Value ?? "0") * 0x200;
                long length = long.Parse(item.Attribute("SizeInByteInSrc")?.Value ?? "0");
                CopyFile(srcFile, destPath, wfilename, start, length);
            }
            foreach (var subitem in item.Elements())
            {
                string subFilename = subitem.Attribute("filename")?.Value ?? "";
                if (!string.IsNullOrEmpty(subFilename))
                {
                    long start = long.Parse(subitem.Attribute("FileOffsetInSrc")?.Value ?? "0") * 0x200;
                    long length = long.Parse(subitem.Attribute("SizeInByteInSrc")?.Value ?? "0");
                    CopyFile(srcFile, destPath, subFilename, start, length);
                }
            }
        }

        private string? ExtractXml(string filename)
        {
            long filesize = new FileInfo(filename).Length;
            using var fs = new FileStream(filename, FileMode.Open, FileAccess.Read);
            fs.Seek(filesize - 0x200, SeekOrigin.Begin);
            byte[] hdr = new byte[0x200];
            fs.ReadExactly(hdr, 0, 0x200);
            int xmllength = BitConverter.ToInt32(hdr, 0x18);
            int xmlpad = 0x200 - (xmllength % 0x200);
            if (xmlpad == 0x200) xmlpad = 0;
            fs.Seek(filesize - 0x200 - (xmllength + xmlpad), SeekOrigin.Begin);
            byte[] inp = new byte[xmllength + xmlpad];
            fs.ReadExactly(inp, 0, inp.Length);
            byte[] outp = KeyCustomDecrypt(inp);
            string result = Encoding.UTF8.GetString(outp, 0, Math.Min(outp.Length, xmllength));
            return (result.Contains("xml ") || result.Contains("<?xml")) ? result : null;
        }

        private byte[] KeyCustomDecrypt(byte[] inp)
        {
            var outp = new List<byte>();
            uint[] rkey = (uint[])Key.Clone();
            uint[] mbox = GetMboxAsUint();
            int length = inp.Length;
            int ptr = 0;

            while (length > 0xF)
            {
                rkey = KeyUpdate(rkey, mbox);
                for (int i = 0; i < 4 && ptr + i * 4 + 4 <= inp.Length; i++)
                {
                    uint inpVal = BitConverter.ToUInt32(inp, ptr + i * 4);
                    uint tmp = rkey[i] ^ inpVal;
                    outp.AddRange(BitConverter.GetBytes(tmp));
                    rkey[i] = inpVal;
                }
                ptr += 0x10;
                length -= 0x10;
            }
            if (length > 0)
            {
                uint[] sboxMbox = GetSboxMbox();
                rkey = KeyUpdate(rkey, sboxMbox);
                int m = 0;
                while (length > 0 && ptr < inp.Length)
                {
                    byte[] data = new byte[4];
                    int copyLen = Math.Min(4, inp.Length - ptr);
                    Array.Copy(inp, ptr, data, 0, copyLen);
                    uint tmp = BitConverter.ToUInt32(data, 0);
                    outp.AddRange(BitConverter.GetBytes(tmp ^ rkey[m]));
                    rkey[m] = tmp;
                    length -= 4; ptr += 4; m++;
                }
            }
            return outp.ToArray();
        }

        private uint[] GetMboxAsUint()
        {
            uint[] result = new uint[16];
            for (int i = 0; i < 15 && i * 4 < _currentMbox.Length; i++)
                result[i] = BitConverter.ToUInt32(_currentMbox, i * 4);
            result[15] = (uint)(_currentMbox.Length > 60 ? _currentMbox[60] : 0x0a);
            return result;
        }

        private static readonly byte[] Sbox = Convert.FromHexString("c66363a5c66363a5f87c7c84f87c7c84ee777799ee777799f67b7b8df67b7b8dfff2f20dfff2f20dd66b6bbdd66b6bbdde6f6fb1de6f6fb191c5c55491c5c55460303050603030500201010302010103ce6767a9ce6767a9562b2b7d562b2b7de7fefe19e7fefe19b5d7d762b5d7d7624dababe64dababe6ec76769aec76769a8fcaca458fcaca451f82829d1f82829d89c9c94089c9c940fa7d7d87fa7d7d87effafa15effafa15b25959ebb25959eb8e4747c98e4747c9fbf0f00bfbf0f00b41adadec41adadecb3d4d467b3d4d4675fa2a2fd5fa2a2fd45afafea45afafea239c9cbf239c9cbf53a4a4f753a4a4f7e4727296e47272969bc0c05b9bc0c05b75b7b7c275b7b7c2e1fdfd1ce1fdfd1c3d9393ae3d9393ae4c26266a4c26266a6c36365a6c36365a7e3f3f417e3f3f41f5f7f702f5f7f70283cccc4f83cccc4f6834345c6834345c51a5a5f451a5a5f4d1e5e534d1e5e534f9f1f108f9f1f108e2717193e2717193abd8d873abd8d87362313153623131532a15153f2a15153f0804040c0804040c95c7c75295c7c75246232365462323659dc3c35e9dc3c35e3018182830181828379696a1379696a10a05050f0a05050f2f9a9ab52f9a9ab50e0707090e07070924121236241212361b80809b1b80809bdfe2e23ddfe2e23dcdebeb26cdebeb264e2727694e2727697fb2b2cd7fb2b2cdea75759fea75759f1209091b1209091b1d83839e1d83839e582c2c74582c2c74341a1a2e341a1a2e361b1b2d361b1b2ddc6e6eb2dc6e6eb2b45a5aeeb45a5aee5ba0a0fb5ba0a0fba45252f6a45252f6763b3b4d763b3b4db7d6d661b7d6d6617db3b3ce7db3b3ce5229297b5229297bdde3e33edde3e33e5e2f2f715e2f2f711384849713848497a65353f5a65353f5b9d1d168b9d1d1680000000000000000c1eded2cc1eded2c4020206040202060e3fcfc1fe3fcfc1f79b1b1c879b1b1c8b65b5bedb65b5bedd46a6abed46a6abe8dcbcb468dcbcb4667bebed967bebed97239394b7239394b944a4ade944a4ade984c4cd4984c4cd4b05858e8b05858e885cfcf4a85cfcf4abbd0d06bbbd0d06bc5efef2ac5efef2a4faaaae54faaaae5edfbfb16edfbfb16864343c5864343c59a4d4dd79a4d4dd766333355663333551185859411858594");

        private uint[] GetSboxMbox()
        {
            uint[] result = new uint[16];
            for (int i = 0; i < 15 && i * 4 < Sbox.Length; i++)
                result[i] = BitConverter.ToUInt32(Sbox, i * 4);
            result[15] = 0x0a;
            return result;
        }

        private static uint GsBox(int offset)
        {
            if (offset < 0 || offset + 4 > Sbox.Length) return 0;
            return BitConverter.ToUInt32(Sbox, offset);
        }

        private static uint[] KeyUpdate(uint[] iv1, uint[] asbox)
        {
            uint d = iv1[0] ^ asbox[0], a = iv1[1] ^ asbox[1], b = iv1[2] ^ asbox[2], c = iv1[3] ^ asbox[3];
            uint e = GsBox((int)(((b >> 16) & 0xff) * 8 + 2)) ^ GsBox((int)(((a >> 8) & 0xff) * 8 + 3)) ^ GsBox((int)((c >> 24) * 8 + 1)) ^ GsBox((int)((d & 0xff) * 8)) ^ asbox[4];
            uint h = GsBox((int)(((c >> 16) & 0xff) * 8 + 2)) ^ GsBox((int)(((b >> 8) & 0xff) * 8 + 3)) ^ GsBox((int)((d >> 24) * 8 + 1)) ^ GsBox((int)((a & 0xff) * 8)) ^ asbox[5];
            uint i = GsBox((int)(((d >> 16) & 0xff) * 8 + 2)) ^ GsBox((int)(((c >> 8) & 0xff) * 8 + 3)) ^ GsBox((int)((a >> 24) * 8 + 1)) ^ GsBox((int)((b & 0xff) * 8)) ^ asbox[6];
            a = GsBox((int)(((d >> 8) & 0xff) * 8 + 3)) ^ GsBox((int)(((a >> 16) & 0xff) * 8 + 2)) ^ GsBox((int)((b >> 24) * 8 + 1)) ^ GsBox((int)((c & 0xff) * 8)) ^ asbox[7];
            int g = 8;
            for (int f = 0; f < (asbox.Length > 15 ? asbox[15] : 10) - 2; f++)
            {
                uint td = e >> 24, m = h >> 16, s = h >> 24, z = e >> 16, l = i >> 24, t = e >> 8;
                e = GsBox((int)(((i >> 16) & 0xff) * 8 + 2)) ^ GsBox((int)(((h >> 8) & 0xff) * 8 + 3)) ^ GsBox((int)((a >> 24) * 8 + 1)) ^ GsBox((int)((e & 0xff) * 8)) ^ (g < asbox.Length ? asbox[g] : 0);
                h = GsBox((int)(((a >> 16) & 0xff) * 8 + 2)) ^ GsBox((int)(((i >> 8) & 0xff) * 8 + 3)) ^ GsBox((int)(td * 8 + 1)) ^ GsBox((int)((h & 0xff) * 8)) ^ (g + 1 < asbox.Length ? asbox[g + 1] : 0);
                i = GsBox((int)((z & 0xff) * 8 + 2)) ^ GsBox((int)(((a >> 8) & 0xff) * 8 + 3)) ^ GsBox((int)(s * 8 + 1)) ^ GsBox((int)((i & 0xff) * 8)) ^ (g + 2 < asbox.Length ? asbox[g + 2] : 0);
                a = GsBox((int)((t & 0xff) * 8 + 3)) ^ GsBox((int)((m & 0xff) * 8 + 2)) ^ GsBox((int)(l * 8 + 1)) ^ GsBox((int)((a & 0xff) * 8)) ^ (g + 3 < asbox.Length ? asbox[g + 3] : 0);
                g += 4;
            }
            return new uint[] {
                (GsBox((int)(((i >> 16) & 0xff) * 8)) & 0xff0000) ^ (GsBox((int)(((h >> 8) & 0xff) * 8 + 1)) & 0xff00) ^ (GsBox((int)((a >> 24) * 8 + 3)) & 0xff000000) ^ (GsBox((int)((e & 0xff) * 8 + 2)) & 0xFF) ^ (g < asbox.Length ? asbox[g] : 0),
                (GsBox((int)(((a >> 16) & 0xff) * 8)) & 0xff0000) ^ (GsBox((int)(((i >> 8) & 0xff) * 8 + 1)) & 0xff00) ^ (GsBox((int)((e >> 24) * 8 + 3)) & 0xff000000) ^ (GsBox((int)((h & 0xff) * 8 + 2)) & 0xFF) ^ (g + 3 < asbox.Length ? asbox[g + 3] : 0),
                (GsBox((int)(((e >> 16) & 0xff) * 8)) & 0xff0000) ^ (GsBox((int)(((a >> 8) & 0xff) * 8 + 1)) & 0xff00) ^ (GsBox((int)((h >> 24) * 8 + 3)) & 0xff000000) ^ (GsBox((int)((i & 0xff) * 8 + 2)) & 0xFF) ^ (g + 2 < asbox.Length ? asbox[g + 2] : 0),
                (GsBox((int)(((h >> 16) & 0xff) * 8)) & 0xff0000) ^ (GsBox((int)(((e >> 8) & 0xff) * 8 + 1)) & 0xff00) ^ (GsBox((int)((i >> 24) * 8 + 3)) & 0xff000000) ^ (GsBox((int)((a & 0xff) * 8 + 2)) & 0xFF) ^ (g + 1 < asbox.Length ? asbox[g + 1] : 0)
            };
        }

        private void CopyFile(string srcFile, string destPath, string wfilename, long start, long length)
        {
            Log($"Extracting {wfilename}");
            string destFile = Path.Combine(destPath, wfilename);
            Directory.CreateDirectory(Path.GetDirectoryName(destFile) ?? destPath);
            using var rf = new FileStream(srcFile, FileMode.Open, FileAccess.Read);
            using var wf = new FileStream(destFile, FileMode.Create, FileAccess.Write);
            rf.Seek(start, SeekOrigin.Begin);
            byte[] buffer = new byte[0x100000];
            long remaining = length;
            while (remaining > 0)
            {
                int toRead = (int)Math.Min(buffer.Length, remaining);
                int read = rf.Read(buffer, 0, toRead);
                if (read == 0) break;
                wf.Write(buffer, 0, read);
                remaining -= read;
            }
        }

        private void DecryptFile(string srcFile, string destPath, string wfilename, long start, long length)
        {
            Log($"Decrypting {wfilename}");
            string destFile = Path.Combine(destPath, wfilename);
            Directory.CreateDirectory(Path.GetDirectoryName(destFile) ?? destPath);
            using var rf = new FileStream(srcFile, FileMode.Open, FileAccess.Read);
            rf.Seek(start, SeekOrigin.Begin);
            byte[] data = new byte[length + (4 - length % 4) % 4];
            rf.ReadExactly(data, 0, (int)length);
            byte[] outp = KeyCustomDecrypt(data);
            using var wf = new FileStream(destFile, FileMode.Create, FileAccess.Write);
            wf.Write(outp, 0, (int)Math.Min(outp.Length, length));
        }
    }
}
