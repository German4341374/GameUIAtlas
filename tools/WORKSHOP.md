# Prop workshop

Each study has one self-contained glTF 2.0 binary (`model/prop.glb`). Open it using **File → Import → glTF 2.0** in Blender. Select parts in the outliner to inspect the geometry: the censer's chain links, the courier's load restraints, the press screw or the receiver's tuning scale. Models use material colors and geometry rather than external texture files. They are static props, not rigged simulations.

`model/studio.png` is a Cycles render of that asset with a floor, camera and three area lights. The studio rig is deliberately left out of the GLB. The corresponding `detail.svg` embeds the render but keeps headings, captions and layout elements separate. Drag the SVG into a design canvas; replace missing fonts if needed. The cloud Figma boards document the earlier vector iteration.

## Rebuild

In a Python 3.11 environment install `bpy==4.5.3`. From the repository root:

```sh
python tools/props.py          # or one study: python tools/props.py apex
python tools/plates.py         # assemble portable layouts, no third-party dependency
python tools/check.py
python tools/import_check.py   # re-import the binaries with Blender
```

To update GitHub's raster previews, make Playwright 1.62.1 and Chromium available to Node, then run `node tools/preview.cjs`. Optionally set `CHROMIUM_PATH` to an existing headless Chromium executable. The prebuilt assets do not require Python, Blender or Node to download.
