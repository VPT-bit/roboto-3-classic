import os
import plistlib
from fontTools.ttLib import TTFont
from defcon import Font

def extract_kerning_from_gpos(ttfont):
    kerning = {}
    if "GPOS" not in ttfont:
        return kerning
    gpos = ttfont["GPOS"].table
    if not hasattr(gpos, "LookupList"):
        return kerning

    glyph_order = ttfont.getGlyphOrder()
    glyph_to_name = {i: n for i, n in enumerate(glyph_order)}
    name_to_glyph = {n: i for i, n in enumerate(glyph_order)}

    for lookup in gpos.LookupList.Lookup:
        if lookup.LookupType != 2:
            continue
        for subtable in lookup.SubTable:
            if subtable.Format != 1:
                continue
            for left in subtable.PairSet:
                left_glyph = subtable.Coverage.glyphs[subtable.PairSet.index(left)]
                for pairValueRecord in left.PairValueRecord:
                    right_glyph = pairValueRecord.SecondGlyph
                    value = pairValueRecord.Value1.XAdvance or 0
                    if value != 0:
                        kerning.setdefault(left_glyph, {})[right_glyph] = value
    return kerning

# === Đọc thông tin từ RobotoFallback-VF ===
fallback_font = TTFont("RobotoFallback-VF(4).ttf")
fallback_os2 = fallback_font["OS/2"]
xAvgCharWidth = fallback_os2.xAvgCharWidth
usWidthClass = fallback_os2.usWidthClass
space_width = fallback_font["hmtx"].metrics.get("space", (508, 0))[0]
kerning_data = extract_kerning_from_gpos(fallback_font)

print(f"xAvgCharWidth={xAvgCharWidth}, widthClass={usWidthClass}, space_width={space_width}")
print(f"Extracted {sum(len(v) for v in kerning_data.values())} kerning pairs")

# === Áp dụng vào UFOs ===
sources_dir = "sources"

for ufo_folder in os.listdir(sources_dir):
    if not ufo_folder.endswith(".ufo"):
        continue
    ufo_path = os.path.join(sources_dir, ufo_folder)
    print(f"\nPatching {ufo_path}...")

    # fontinfo.plist
    fontinfo_path = os.path.join(ufo_path, "fontinfo.plist")
    with open(fontinfo_path, "rb") as f:
        fontinfo = plistlib.load(f)

    fontinfo["xAvgCharWidth"] = xAvgCharWidth
    fontinfo["widthClass"] = usWidthClass

    with open(fontinfo_path, "wb") as f:
        plistlib.dump(fontinfo, f)
    print("  - Updated fontinfo.plist")

    # space.glif
    font = Font(ufo_path)
    if "space" in font:
        glyph = font["space"]
        glyph.width = space_width
        glyph.changed()
        font.save()
        print("  - Updated space.glif")

    # kerning.plist
    kerning_out = {}
    for left, rights in kerning_data.items():
        for right, value in rights.items():
            kerning_out.setdefault(left, {})[right] = value

    kerning_path = os.path.join(ufo_path, "kerning.plist")
    with open(kerning_path, "wb") as f:
        plistlib.dump(kerning_out, f)
    print(f"  - Written kerning.plist with {sum(len(v) for v in kerning_out.values())} pairs")

print("\n===> All UFOs patched successfully.")
