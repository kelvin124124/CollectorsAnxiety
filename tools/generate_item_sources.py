#!/usr/bin/env python3
"""
Generates CollectorsAnxiety/Resources/ItemSourcesTC.json, the item source (acquisition) data shown to players on
the Traditional Chinese (繁中) server.

Data sources, in order of preference:
  1. FFXIV 繁體中文收藏查詢站 (https://cycleapple.github.io/ffxiv-collection-tc/) - Traditional Chinese source data.
  2. FFXIV Collect (https://ffxivcollect.com/) - English source data, used only for entries the above has no
     sources for (usually content newer than the TC dataset).

Item IDs are resolved against game data via XIVAPI (https://v2.xivapi.com/).

Usage: python3 tools/generate_item_sources.py [path/to/collections_data.json]
Only the Python standard library is required.
"""

import json
import sys
import urllib.parse
import urllib.request
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path

TC_DATA_URL = "https://raw.githubusercontent.com/cycleapple/ffxiv-collection-tc/main/data/collections_data.json"
FFXIV_COLLECT_API = "https://ffxivcollect.com/api"
XIVAPI = "https://v2.xivapi.com/api"

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "CollectorsAnxiety" / "Resources" / "ItemSourcesTC.json"

# Maximum number of sources of a single type kept per entry. Commonly sold items can have dozens of near-identical
# vendors, which isn't useful in a tooltip.
MAX_SOURCES_PER_TYPE = 4

# TC collection name -> output category. Categories keyed by something other than an item ID must match the
# SourceCategory values used by the plugin's unlockables.
TC_COLLECTIONS = {
    "Mounts": "Mount",
    "Minions": "Minion",
    "Emotes": "Emote",
    "Orchestrions": "Orchestrion",
    "Fashion Accessories": "Ornament",
    "Bardings": "Barding",
    "Glasses": "Glasses",
    # Item ID keyed
    "Framer Kits": "Item",
    "Glamour": "Item",
}

# FFXIV Collect endpoints whose IDs match the game's sheet row IDs.
FFXIV_COLLECT_ROW_KEYED = {
    "mounts": "Mount",
    "minions": "Minion",
    "emotes": "Emote",
    "orchestrions": "Orchestrion",
    "fashions": "Ornament",
    "bardings": "Barding",
}

# FFXIV Collect endpoints that are only reliably mappable through their unlock item.
FFXIV_COLLECT_ITEM_KEYED = ["hairstyles", "facewear"]

TYPE_LABELS = {
    "Achievement": "成就",
    "Container": "寶箱",
    "Crafting": "製作",
    "Duty": "任務",
    "Event": "活動",
    "FATE": "危命任務",
    "FirmamentFete": "天穹街振興",
    "Gil": "金幣",
    "Instance": "副本",
    "Misc": "其他",
    "MogStation": "商城",
    "Monster": "怪物",
    "Npc": "NPC",
    "PvP": "PvP",
    "Quest": "任務",
    "Shop": "兌換",
    "Submarine": "潛水艇",
    "Venture": "雇員探險",
}


def fetch_json(url):
    request = urllib.request.Request(url, headers={"User-Agent": "CollectorsAnxiety item source generator"})
    with urllib.request.urlopen(request, timeout=300) as response:
        return json.load(response)


def fetch_sheet(sheet, fields):
    """Fetches every row of a sheet from XIVAPI, returning {row_id: fields}."""
    rows = {}
    after = None
    while True:
        query = {"fields": fields, "limit": 500}
        if after is not None:
            query["after"] = after
        page = fetch_json(f"{XIVAPI}/sheet/{sheet}?{urllib.parse.urlencode(query)}")
        if not page["rows"]:
            return rows
        for row in page["rows"]:
            rows[row["row_id"]] = row["fields"]
        after = page["rows"][-1]["row_id"]


def ref_id(value):
    return value.get("row_id", value.get("value")) if isinstance(value, dict) else value


def format_costs(costs):
    # Item 1 is gil, which the TC data leaves untranslated.
    return "、".join(f"{'金幣' if c.get('ItemId') == 1 else c['ItemName']} ×{c['Amount']:,}"
                    for c in costs if c.get("ItemName"))


def convert_tc_source(source):
    source_type = source.get("Type", "")
    label = TYPE_LABELS.get(source_type, source_type)
    name = (source.get("Name") or "").strip()
    detail = (source.get("Description") or "").strip() or None

    if source_type in ("Shop", "Gil") and source.get("NpcName"):
        # Rebuild shop text from structured data; the precomputed name mixes in English.
        text = source["NpcName"]
        territory = (source.get("Location") or {}).get("Territory")
        if territory:
            text += f"（{territory}）"
        costs = format_costs(source.get("Costs") or [])
        if costs:
            text += f"：{costs}"
    elif source_type == "Crafting":
        text = "可由製作職業製作"
    else:
        text = name

    if not text:
        return None

    converted = OrderedDict(Type=label, Text=text)
    if detail and detail != text:
        converted["Detail"] = detail
    return converted


def convert_collect_source(source):
    text = (source.get("text") or "").strip()
    if not text:
        return None
    return OrderedDict(Type=source.get("type") or "", Text=text, English=True)


def limit_sources(sources):
    """De-duplicates sources and caps how many of each type are kept."""
    seen = set()
    by_type = OrderedDict()
    for source in sources:
        if source is None:
            continue
        key = (source["Type"], source["Text"], source.get("Detail"))
        if key in seen:
            continue
        seen.add(key)
        by_type.setdefault(source["Type"], []).append(source)

    result = []
    for source_type, group in by_type.items():
        result.extend(group[:MAX_SOURCES_PER_TYPE])
        if len(group) > MAX_SOURCES_PER_TYPE:
            result.append(OrderedDict(Type=source_type, Text=f"……以及其他 {len(group) - MAX_SOURCES_PER_TYPE} 個來源",
                                      English=group[0].get("English", False)))
    for source in result:
        if not source.get("English"):
            source.pop("English", None)
    return result


def main():
    if len(sys.argv) > 1:
        print(f"Loading TC data from {sys.argv[1]}")
        with open(sys.argv[1], encoding="utf-8") as f:
            tc_data = json.load(f)
    else:
        print(f"Downloading TC data from {TC_DATA_URL}")
        tc_data = fetch_json(TC_DATA_URL)

    print("Fetching armoire items from XIVAPI")
    armoire_items = {ref_id(fields["Item"]) for fields in fetch_sheet("Cabinet", "Item").values()}
    armoire_items.discard(0)

    output = OrderedDict((category, {}) for category in dict.fromkeys(TC_COLLECTIONS.values()))

    for collection in tc_data["Collections"]:
        category = TC_COLLECTIONS.get(collection["CollectionName"])
        if category is None:
            continue

        for item in collection["Items"]:
            # Glamour covers every equippable item; only the armoire-storable ones are tracked by the plugin.
            if collection["CollectionName"] == "Glamour" and item["Id"] not in armoire_items:
                continue
            sources = limit_sources(convert_tc_source(s) for s in item["Sources"])
            if sources:
                output[category].setdefault(str(item["Id"]), []).extend(sources)

    tc_counts = {category: len(entries) for category, entries in output.items()}

    def add_fallback(category, key, collect_sources):
        key = str(key)
        if key in output[category]:
            return
        sources = limit_sources(convert_collect_source(s) for s in collect_sources or [])
        if sources:
            output[category][key] = sources

    for endpoint, category in FFXIV_COLLECT_ROW_KEYED.items():
        print(f"Fetching {endpoint} from FFXIV Collect")
        for entry in fetch_json(f"{FFXIV_COLLECT_API}/{endpoint}")["results"]:
            add_fallback(category, entry["id"], entry.get("sources"))

    for endpoint in FFXIV_COLLECT_ITEM_KEYED:
        print(f"Fetching {endpoint} from FFXIV Collect")
        for entry in fetch_json(f"{FFXIV_COLLECT_API}/{endpoint}")["results"]:
            if entry.get("item_id"):
                add_fallback("Item", entry["item_id"], entry.get("sources"))

    for category in output:
        output[category] = OrderedDict(sorted(output[category].items(), key=lambda kv: int(kv[0])))
        print(f"  {category}: {tc_counts[category]} TC, {len(output[category]) - tc_counts[category]} English fallback")

    document = OrderedDict(
        GeneratedAt=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        TcDataExportedAt=tc_data.get("ExportedAt"),
        Sources=output,
    )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8", newline="\n") as f:
        json.dump(document, f, ensure_ascii=False, separators=(",", ":"))
        f.write("\n")
    print(f"Wrote {OUTPUT_PATH} ({OUTPUT_PATH.stat().st_size // 1024} KiB)")


if __name__ == "__main__":
    main()
