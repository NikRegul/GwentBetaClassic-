"""Extract the exact original Beta global settings for the isolated AI host."""
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/vendor/audio-python"))
import UnityPy

source = ROOT / "Gwent 0.9.24.3.432/Gwent_Data/resources.assets"
output = ROOT / "BetaGwent/drafts/day-iteration-20261023/beta-original-js/Settings.xml"
matches = []
for obj in UnityPy.load(str(source)).objects:
    if obj.type.name != "TextAsset":
        continue
    asset = obj.read()
    if asset.m_Name != "Settings":
        continue
    raw = asset.m_Script
    if isinstance(raw, str):
        raw = raw.encode("utf-8", errors="surrogateescape")
    matches.append((obj.path_id, raw))
if len(matches) != 1:
    raise RuntimeError(f"Expected one original Settings asset, got {len(matches)}")
path_id, raw = matches[0]
output.parent.mkdir(parents=True, exist_ok=True)
if output.exists() and output.read_bytes() != raw:
    raise RuntimeError("Refusing to overwrite different settings")
output.write_bytes(raw)
metadata = {
    "source": str(source.relative_to(ROOT)),
    "sourceSha256": hashlib.sha256(source.read_bytes()).hexdigest(),
    "type": "TextAsset", "name": "Settings", "pathId": path_id,
    "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
    "output": str(output.relative_to(ROOT)),
}
output.with_suffix(".provenance.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
print(json.dumps(metadata))
