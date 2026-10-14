using System.Collections.Generic;
using Lumina.Excel;
using Lumina.Excel.Sheets;

namespace CollectorsAnxiety.Data;

public interface IUnlockable
{
    public uint Id { get; }
}

public abstract class Unlockable<T> : IUnlockable where T : struct, IExcelRow<T>
{
    internal readonly T LuminaEntry;

    protected Unlockable(T excelRow)
    {
        LuminaEntry = excelRow;
        Id = LuminaEntry.RowId;
    }

    public virtual uint Id { get; }

    public virtual Item? UnlockItem => null;

    /// <summary>
    /// The category this entry's item sources are keyed under, or null if sources are only looked up by unlock item.
    /// </summary>
    public virtual string? SourceCategory => null;

    /// <summary>
    /// The IDs to look up item sources by within <see cref="SourceCategory"/>.
    /// </summary>
    public virtual IEnumerable<uint> SourceIds => [Id];

    public abstract string Name { get; }
    public abstract uint? IconId { get; }

    public virtual uint SortKey => Id;

    public abstract bool IsUnlocked();

    public abstract bool IsValid();
}
