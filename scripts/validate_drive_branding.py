"""Check the branded OpenCloud theme and its local assets."""
import json
import xml.etree.ElementTree as ET
from pathlib import Path

root = Path(__file__).resolve().parents[1]
base = root / "services/web/assets/themes"
config = json.loads((base / "opencloud/theme.json").read_text())
assert config["common"]["name"] == "GoreeCloud Drive"
assert config["common"]["shareRoles"]
web = config["clients"]["web"]
assert {t["isDark"] for t in web["themes"]} == {True, False}
paths = [config["common"]["logo"]]
paths += [web["defaults"][key] for key in ("logo", "logoMobile", "favicon")]
for theme in web["themes"]:
    roles = theme["designTokens"]["roles"]
    for role in ("primary", "onPrimary", "background", "onBackground"):
        assert roles[role].startswith("#") and len(roles[role]) == 7
    paths.extend(theme[key] for key in ("logo", "logoMobile") if key in theme)
for filename in paths:
    assert filename.startswith("themes/goreecloud/assets/")
    svg = base.parent / filename
    assert svg.is_file(), filename
    tree = ET.parse(svg)
    assert tree.getroot().tag == "{http://www.w3.org/2000/svg}svg"
assert (root / "LICENSE").is_file()
assert "opencloud-eu/opencloud" in (root / "README.md").read_text()
print("GoreeCloud Drive brand and attribution checks passed")
