"""Guard the OpenCloud IdP keyboard-focus accessibility backport."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
CSS = (ROOT / "services" / "idp" / "src" / "app.css").read_text(encoding="utf-8")


def declarations(selector):
    escaped = re.escape(selector)
    match = re.search(r"(?m)^\s*" + escaped + r"\s*\{([^}]*)\}", CSS)
    if not match:
        raise AssertionError(f"Missing CSS selector {selector!r}")
    return dict(
        (key.strip().lower(), value.strip().lower())
        for key, value in re.findall(r"([\w-]+)\s*:\s*([^;]+);", match.group(1))
    )


class IdpKeyboardFocusTests(unittest.TestCase):
    def test_every_keyboard_focused_control_has_visible_outline(self):
        body = declarations("body :focus-visible")
        self.assertEqual(body.get("outline"), "2px solid #20434f")
        self.assertEqual(body.get("outline-offset"), "2px")

    def test_logo_link_focus_visible_on_changing_background(self):
        logo = declarations(".oc-logo-container:focus-visible")
        self.assertEqual(logo.get("outline-color"), "#fff")
        self.assertEqual(logo.get("box-shadow"), "0 0 0 6px #20434f")

    def test_existing_form_input_focus_retained(self):
        input_focus = declarations(".oc-input:focus")
        self.assertEqual(input_focus.get("outline"), "2px solid #e2baff")
        self.assertEqual(input_focus.get("outline-offset"), "0")

    def test_existing_disabled_ripple_requires_fallback(self):
        ripple = declarations(".MuiTouchRipple-root")
        self.assertEqual(ripple.get("display"), "none !important")
        button = declarations(".oc-button")
        self.assertEqual(button.get("box-shadow"), "none !important")


if __name__ == "__main__":
    unittest.main()
