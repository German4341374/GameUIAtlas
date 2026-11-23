"""Check the offline gallery without contacting Figma or GitHub."""
from pathlib import Path
import re
import struct
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
studies = sorted((ROOT / "studies").iterdir())
assert len(studies) == 4
all_nodes = set()
for folder in studies:
    for sub in ("art", "icons"):
        assert len(list((folder / sub).glob("*.svg"))) == 4, (folder, sub)
    assert (folder / "detail.svg").is_file()
    for path in folder.rglob("*.svg"):
        xml = ElementTree.parse(path).getroot()
        assert xml.tag == "{http://www.w3.org/2000/svg}svg" and xml.get("viewBox"), path
    raw = (folder / "overview.png").read_bytes()
    assert raw[:8] == b"\x89PNG\r\n\x1a\n", folder
    width, height = struct.unpack(">II", raw[16:24])
    assert min(width, height) >= 800, folder
    nodes = re.findall(r"\?node-id=(\d+-\d+)", (folder / "README.md").read_text(encoding="utf-8"))
    assert len(nodes) == 5 and len(set(nodes)) == 5, folder
    all_nodes.update(nodes)
assert len(all_nodes) == 20
for doc in ROOT.rglob("README.md"):
    for target in re.findall(r"\]\(([^)]+)\)", doc.read_text(encoding="utf-8")):
        if not target.startswith(("https://", "#")):
            assert (doc.parent / target).exists(), (doc, target)
print("OK: 4 boards, 16 Figma frame links, 36 SVG files, 4 PNG previews and all relative README links.")
