using System.Globalization;
using System.Numerics;
using CollectorsAnxiety.Base;
using CollectorsAnxiety.Data;
using CollectorsAnxiety.Services;
using Dalamud.Interface.Colors;
using Dalamud.Interface.Components;
using Dalamud.Interface.Utility;
using Dalamud.Interface.Utility.Raii;
using Dalamud.Bindings.ImGui;

namespace CollectorsAnxiety.UI.Tabs;

public class SettingsTab : ITab
{
    public string Name => $"Settings###{nameof(SettingsTab)}";

    private readonly PluginConfig _config;
    private readonly ConfigurationLoaderService _configurationLoaderService;
    private readonly ItemSources _itemSources;

    private static readonly string[] ItemSourceModeLabels =
        ["Auto (Traditional Chinese server only)", "Always", "Never"];

    // settings cache
    private bool _hideSpoilers;
    private bool _hiddenItemsInOverview;
    private int _itemSourceMode;

    public SettingsTab(PluginConfig pluginConfig, ConfigurationLoaderService configurationLoaderService,
        ItemSources itemSources)
    {
        _config = pluginConfig;
        _configurationLoaderService = configurationLoaderService;
        _itemSources = itemSources;

        _hideSpoilers = _config.HideSpoilers;
        _hiddenItemsInOverview = _config.CountHiddenItemsInOverview;
        _itemSourceMode = (int)_config.ItemSourceMode;
    }

    public void Draw()
    {
        var childSize = ImGui.GetContentRegionAvail();
        var pbs = ImGuiHelpers.GetButtonSize("placeholder");
        var style = ImGui.GetStyle();

        var paddedY = childSize.Y - pbs.Y - 3 * style.ItemSpacing.Y + 2 * style.FramePadding.Y;

        using (ImRaii.Child("SettingsPane", childSize with {Y = paddedY}))
        {
            ImGui.Text("System Options");
            ImGui.Indent();

            using (ImRaii.PushIndent())
            {
                if (ImGui.Checkbox("Spoiler-Free Mode", ref _hideSpoilers))
                {
                    _config.HideSpoilers = _hideSpoilers;
                    _configurationLoaderService.Save();
                }

                ImGuiComponents.HelpMarker(
                    "When enabled, this feature will mask all non-collected items with a special icon and spoiler text. Uncollected items will still show in counts. Turning this off may reveal items that are not yet available or otherwise spoil certain experiences.");

                if (ImGui.Checkbox("Count Hidden Items in Overview", ref _hiddenItemsInOverview))
                {
                    _config.CountHiddenItemsInOverview = _hiddenItemsInOverview;
                    _configurationLoaderService.Save();
                }

                ImGuiComponents.HelpMarker(
                    "When enabled, the Overview tab will include hidden items in the totals displayed and won\'t invalidate your parses. This option does not affect the progress bars on each individual tab.");

                ImGui.SetNextItemWidth(ImGui.GetFontSize() * 18);
                if (ImGui.Combo("Item Sources (繁中服)", ref _itemSourceMode, ItemSourceModeLabels, ItemSourceModeLabels.Length))
                {
                    _config.ItemSourceMode = (ItemSourceMode)_itemSourceMode;
                    _configurationLoaderService.Save();
                }

                ImGuiComponents.HelpMarker(
                    "Shows where to obtain each entry, in Traditional Chinese, when hovering the map icon next to its name. " +
                    "Data comes from FFXIV 繁體中文收藏查詢站 (cycleapple.github.io/ffxiv-collection-tc), with English FFXIV Collect " +
                    "data for entries it doesn't cover." +
                    (_itemSources.DataTimestamp != null ? $"\n\nData exported: {_itemSources.DataTimestamp}" : "") +
                    $"\nTraditional Chinese server detected: {(_itemSources.IsTraditionalChineseClient() ? "Yes" : "No")}");
            }

            ImGui.Spacing();
            ImGui.Text("Maintenance");

            using (ImRaii.PushIndent())
            {
                if (ImGui.Button("Unhide All Items"))
                {
                    _config.HiddenItems.Clear();
                    _configurationLoaderService.Save();
                }
            }
        }

        // Footer buttons
        if (ImGui.Button("Plugin GitHub"))
        {
            Dalamud.Utility.Util.OpenLink(Constants.GITHUB_URL);
        }
    }
}
