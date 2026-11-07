"""Synthetic, read-only source contracts for builder compatibility."""
import unittest
from ops.build_recipe_preflight import ROOT, RECIPES, assess, release_hold_labels


class BuildRecipeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = (ROOT / "go.mod").read_text()
        cls.recipes = {key: (ROOT / path).read_text() for key, path in RECIPES.items()}

    def test_production_builder_is_blocked(self):
        result = assess(self.module, self.recipes["production"], "production")
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("go_builder_older_than_module_requirement", result["findings"])

    def test_pinned_security_trial_never_authorizes_release(self):
        result = assess(self.module, self.recipes["security-trial-pinned"], "security-trial-pinned")
        self.assertEqual(result["status"], "PASS_STATIC")
        self.assertFalse(result["releaseApproved"])

    def test_unknown_builder_and_unsigned_approval_cannot_pass(self):
        recipe = self.recipes["security-trial-pinned"]
        variants = [
            recipe.replace("quay.io/opencloudeu/golang-ci@sha256:", "quay.io/opencloudeu/golang-ci:"),
            recipe.replace('goreecloud.release.approved="false"', 'goreecloud.release.approved="true"'),
            recipe.replace("ENABLE_VIPS=true", "ENABLE_VIPS=false"),
        ]
        for variant in variants:
            with self.subTest(variant=variant[:80]):
                self.assertEqual(assess(self.module, variant, "security-trial-pinned")["status"], "BLOCKED")


    def test_release_hold_must_be_real_unambiguous_label(self):
        recipe = self.recipes["security-trial-pinned"]
        marker = 'goreecloud.release.approved="false"'
        self.assertEqual(release_hold_labels(recipe), ["false"])
        # A comment, RUN or ENV string must not turn a true release label
        # into a static-review pass.
        cases = {
            "comment": recipe.replace(marker, 'goreecloud.release.approved="true"')
                       + "\n# " + marker + "\n",
            "run": recipe.replace(marker, 'goreecloud.release.approved="true"')
                   + "\nRUN echo " + marker + "\n",
            "env": recipe.replace(marker, 'goreecloud.release.approved="true"')
                   + "\nENV " + marker + "\n",
            "duplicate": recipe + '\nLABEL goreecloud.release.approved="true"\n',
            "double_false": recipe + '\nLABEL ' + marker + '\n',
            "embedded_marker_in_other_label": recipe.replace(
                marker, 'org.example.description="other value goreecloud.release.approved=false"'),
            "invalid_label_field": recipe + '\nLABEL not-a-key-value\n',
            "missing": recipe.replace(marker, 'goreecloud.release.approved="true"'),
            "unterminated": recipe + '\nLABEL org.example.foo="bar" \\\n',
        }
        for label, candidate in cases.items():
            with self.subTest(case=label):
                result = assess(self.module, candidate, "security-trial-pinned")
                self.assertEqual(result["status"], "BLOCKED")
                self.assertFalse(result["releaseApproved"])



    def test_release_hold_is_from_final_runtime_stage_only(self):
        recipe = self.recipes["security-trial-pinned"]
        marker = 'goreecloud.release.approved="false"'
        final_from = next(line for line in recipe.splitlines()
                          if line.startswith("FROM alpine@sha256:"))
        self.assertEqual(recipe.count(marker), 1)
        # Dockerfile LABEL in the Go build stage does not appear in the final
        # Alpine image. A build-stage-only hold must never produce PASS_STATIC.
        moved = recipe.replace(marker, 'org.example.runtime.marker="not-a-hold"')
        moved = moved.replace(final_from, f"LABEL {marker}\\n{final_from}", 1)
        self.assertEqual(release_hold_labels(moved), [])
        result = assess(self.module, moved, "security-trial-pinned")
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("security_trial_missing_explicit_release_hold",
                      result["findings"])
        # An unrelated earlier stage with a hold does not invalidate a
        # correctly labeled final image (or double-count it).
        earlier_and_final = recipe.replace(final_from,
                                            f"LABEL {marker}\\n{final_from}", 1)
        self.assertEqual(release_hold_labels(earlier_and_final), ["false"])
        checked = assess(self.module, earlier_and_final,
                         "security-trial-pinned")
        self.assertEqual(checked["status"], "PASS_STATIC")
        self.assertFalse(checked["releaseApproved"])
        # A true final-stage label must not be concealed by an earlier false.
        final_true = earlier_and_final.replace(marker,
                                                'goreecloud.release.approved="true"', 1)
        final_true = final_true.replace(marker,
                                        'goreecloud.release.approved="true"', 1)
        self.assertEqual(release_hold_labels(final_true), ["true"])
        self.assertEqual(assess(self.module, final_true,
                                "security-trial-pinned")["status"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
