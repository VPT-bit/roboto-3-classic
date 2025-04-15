# ... (giữ nguyên đoạn đầu)

# === Áp dụng vào UFOs ===
sources_dir = "sources"

for ufo_folder in os.listdir(sources_dir):
    if not ufo_folder.endswith(".ufo"):
        continue
    ufo_path = os.path.join(sources_dir, ufo_folder)
    print(f"\nPatching {ufo_path}...")

    # fontinfo.plist
    fontinfo_path = os.path.join(ufo_path, "fontinfo.plist")
    if not os.path.exists(fontinfo_path):
        print("  - Skipped (no fontinfo.plist)")
        continue

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
