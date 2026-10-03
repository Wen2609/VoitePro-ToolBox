namespace OplusEdlTool.Services
{
    public class PartitionEntry
    {
        public string Name { get; set; } = string.Empty;
        public int Lun { get; set; }
        public ulong FirstLBA { get; set; }
        public ulong LastLBA { get; set; }
        public ulong SizeBytes { get; set; }
        public string TypeGuid { get; set; } = string.Empty;
    }
}
