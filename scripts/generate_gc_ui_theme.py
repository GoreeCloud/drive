#!/usr/bin/env python3
"""Generate an opt-in OpenCloud-compatible theme from verified GC UI Foundations tokens.

Input is the *verified* Apache-2.0 GC UI Foundations v1 token contract.
This does not copy GC UI's own product logo or claim a complete Drive UI migration.
"""
import argparse
import json
from pathlib import Path

# Explicit semantic mapping: GC UI -> OpenCloud web-client design-token roles.
ROLE_MAPPING = {
    "primary": "primary",
    "onPrimary": "onPrimary",
    "primaryContainer": "primaryContainer",
    "onPrimaryContainer": "onPrimaryContainer",
    "secondary": "secondary",
    "onSecondary": "onSecondary",
    "secondaryContainer": "secondaryContainer",
    "onSecondaryContainer": "onSecondaryContainer",
    "tertiary": "tertiary",
    "onTertiary": "onTertiary",
    "tertiaryContainer": "tertiaryContainer",
    "onTertiaryContainer": "onTertiaryContainer",
    "error": "danger",
    "onError": "onDanger",
    "errorContainer": "dangerContainer",
    "onErrorContainer": "onDangerContainer",
    "background": "canvas",
    "onBackground": "onCanvas",
    "surface": "surface",
    "onSurface": "onSurface",
    "surfaceVariant": "surfaceTonal",
    "onSurfaceVariant": "onSurfaceMuted",
    "outline": "outline",
    "outlineVariant": "divider",
    "scrim": "scrim",
    "inverseSurface": "inverseSurface",
    "inverseOnSurface": "inverseOnSurface",
    "surfaceDim": "surfaceInset",
    "surfaceBright": "surfaceRaised",
    "surfaceContainerLowest": "surfaceInset",
    "surfaceContainerLow": "surface",
    "surfaceContainer": "surfaceTonal",
    "surfaceContainerHigh": "surfaceRaised",
    "surfaceContainerHighest": "surfaceRaised",
}
FIXED_MAPPING = {
    "primary": ("primaryContainer", "onPrimaryContainer"),
    "secondary": ("secondaryContainer", "onSecondaryContainer"),
    "tertiary": ("tertiaryContainer", "onTertiaryContainer"),
}


def semantic_color(theme, name):
    entry = theme[name]
    value = entry["$value"]
    if entry["$type"] != "color" or not isinstance(value, str) or len(value) != 7 or not value.startswith("#"):
        raise ValueError(f"invalid GC UI color token: {name}")
    if not all(c in "0123456789abcdefABCDEF" for c in value[1:]):
        raise ValueError(f"invalid GC UI hex color token: {name}")
    return value.upper()


def client_roles(colors, mode):
    source = colors[mode]
    roles = {target: semantic_color(source, origin) for target, origin in ROLE_MAPPING.items()}

    # GC UI's source palette has no stand-alone shadow token. Using its scrim
    # protects contrast semantics without inventing a palette-wide default.
    roles["shadow"] = semantic_color(source, "scrim")
    opposite = "dark" if mode == "light" else "light"
    roles["inversePrimary"] = semantic_color(colors[opposite], "primary")

    # Fixed colors are intentionally mode-independent, matching their role in
    # the OpenCloud theme contract and GC UI's light-container semantics.
    for name, (fixed, on_fixed) in FIXED_MAPPING.items():
        cap = name[0].upper() + name[1:]
        roles[name + "Fixed"] = semantic_color(colors["light"], fixed)
        roles["on" + cap + "Fixed"] = semantic_color(colors["light"], on_fixed)

    return roles


def generate(gc_ui_tokens, upstream_theme):
    colors = gc_ui_tokens["color"]
    upstream_web = upstream_theme["clients"]["web"]

    # Retain upstream application role labels and existing icon/logo paths
    # during this opt-in preview. Neither is represented as first-party artwork.
    # Logo migration requires approved Drive-specific visual assets.
    preview = {
        "common": {
            "name": "GoreeCloud Drive — UI Foundations Preview",
            "slogan": "Private cloud storage and collaboration",
            "logo": upstream_theme["common"]["logo"],
            "shareRoles": upstream_theme["common"]["shareRoles"],
        },
        "clients": {
            "android": {},
            "desktop": {},
            "ios": {},
            "web": {
                "defaults": upstream_web["defaults"],
                "themes": [
                    {
                        "isDark": mode == "dark",
                        "label": "GoreeCloud UI · Iris (" + mode + ")",
                        "designTokens": {"roles": client_roles(colors, mode)},
                    }
                    for mode in ("light", "dark")
                ],
            },
        },
    }
    # Preserve the existing alternate dark-logo affordances for compatibility.
    for source_theme, result_theme in zip(upstream_web["themes"], preview["clients"]["web"]["themes"]):
        for field in ("logo", "logoMobile"):
            if field in source_theme:
                result_theme[field] = source_theme[field]
    return preview


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tokens", required=True, type=Path, help="Verified gc-ui Foundations gc.v1.tokens.json")
    parser.add_argument("--upstream-theme", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    gc_ui_tokens = json.loads(args.tokens.read_text(encoding="utf-8"))
    upstream_theme = json.loads(args.upstream_theme.read_text(encoding="utf-8"))
    generated = generate(gc_ui_tokens, upstream_theme)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(generated, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
