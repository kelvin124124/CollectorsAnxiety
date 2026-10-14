# Collector's Anxiety [DEVELOPMENT PREVIEW]

[![Download count](https://img.shields.io/endpoint?url=https://vz32sgcoal.execute-api.us-east-1.amazonaws.com/CollectorsAnxiety)](https://github.com/KazWolfe/XIVDeck)

Collector's Anxiety is a Dalamud plugin that helps [Final Fantasy XIV][ffxiv] completionists 
track their in-game hoard.

> ⚠️ **Hic Svnt Leones!**
>
> This plugin, alongside all of Dalamud, is against the Terms of Service for Final Fantasy XIV.
> While this plugin has gone to great lengths to ensure that it is as safe as possible and adheres
> to the spirit of the game, there is still a small risk. Please ensure you're only using official
> builds and releases of all relevant tools.
>
> By using this plugin (and Dalamud itself), you understand that you are risking receiving a
> ban for client modifications. For more information, please see [Dalamud's FAQ][dalamudfaq-tos].

## Plugin Components

Collector's Anxiety is a fully self-contained plugin, meaning that it only exists within the game.

To open the Collector's Anxiety window, either use the `/panxiety` command or use the built-in "open 
settings" button provided by Dalamud in the plugin installer. The Collector's Anxiety window is 
tab-based, with all tracked items appearing as individual tabs.

The **Overview** tab of Collector's Anxiety shows a quick, well, overview of all tracked categories.
This view also will apply parse coloring to each category name, to give players a quick sense of their
progress as well as to encourage just a little bit of toxicity, as a treat. Collection data is not
uploaded to any server, and collection parses are relative to total items collected.

### Item Sources (Traditional Chinese Server)

On the Traditional Chinese (繁中) server, a map icon appears next to each entry. Hover over it to see where the entry
comes from. The data comes from [FFXIV 繁體中文收藏查詢站][collection-tc]. For entries that site doesn't cover, the
English data from [FFXIV Collect][ffxivcollect] is shown instead. Players on other servers can turn this on from the
Settings tab. To refresh the bundled data, run `python3 tools/generate_item_sources.py`.

### Installing the Plugin

To install Collector's Anxiety, simply add it through the Dalamud Plugin Installer. Note that, at
this time, this plugin is only available for users with
[Dalamud Testing plugins enabled][dalamudfaq-test]. Upon full release of Collector's Anxiety, it will
be made available to all users.


[ffxiv]: https://www.finalfantasyxiv.com
[collection-tc]: https://cycleapple.github.io/ffxiv-collection-tc/
[ffxivcollect]: https://ffxivcollect.com/
[pointcrow]: https://www.youtube.com/watch?v=NSNFwHUXVqc
[dalamudfaq-test]: https://goatcorp.github.io/faq/dalamud_troubleshooting.html#q-how-do-i-enable-plugin-test-builds
[dalamudfaq-tos]: https://goatcorp.github.io/faq/xl_troubleshooting#q-are-xivlauncher-dalamud-and-dalamud-plugins-safe-to-use