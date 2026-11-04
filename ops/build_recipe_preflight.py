#!/usr/bin/env python3
"""Offline static check of Drive Go builder compatibility; never builds or deploys."""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECIPES = {
    "production": "Dockerfile",
    "security-trial": "ops/deploy/Dockerfile.security-trial",
    "security-trial-pinned": "ops/deploy/Dockerfile.security-trial-pinned",
}
# Manifest of the official Go 1.26 amd64 builder verified in the isolated
# November 2026 security trial; this is not a fresh image attestation.
REVIEWED_BUILDER = "sha256:620c7a90212b46c4aa90e64ce6ed5cbb8934ccabc056d6bfd6bb2683f3f1d1e4"


def release_hold_labels(recipe: str) -> list[str]:
    """Return explicit hold-label values from Dockerfile LABEL instructions.

    Comments, RUN/ENV/ARG text and shell output must never masquerade as a
    hold label. Join Dockerfile continuations before inspecting LABEL fields.
    This is a narrow source contract, not a full Dockerfile interpreter.
    """
    values = []
    parts = []
    for raw in recipe.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        continued = line.endswith("\\")
        parts.append(line[:-1].strip() if continued else line)
        if continued:
            continue
        logical = " ".join(parts)
        parts.clear()
        match = re.match(r"^LABEL\s+(.+)$", logical, re.IGNORECASE)
        if not match:
            continue
        # Multiple markers are ambiguous; a later LABEL can override earlier
        # values and leave the image falsely marked as a non-release artifact.
        for value in re.findall(
            r"""(?:^|\s)goreecloud\.release\.approved\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s]+))""",
            match.group(1),
        ):
            values.append(next((part for part in value if part), ""))
    if parts:
        raise ValueError("Unterminated Dockerfile instruction")
    return values

def assess(go_mod: str, recipe: str, target: str) -> dict:
    result = {"target": target, "status": "BLOCKED", "releaseApproved": False, "findings": []}
    version = re.search(r"^go\s+(\d+)\.(\d+)(?:\.\d+)?\s*$", go_mod, re.MULTILINE)
    stage = re.search(r"^FROM\s+(\S+)\s+AS\s+build\s*$", recipe, re.MULTILINE | re.IGNORECASE)
    if not version or not stage:
        result["findings"].append("missing_go_directive_or_build_stage")
        return result
    required = tuple(map(int, version.groups()))
    image = stage.group(1)
    result["sourceGo"] = ".".join(map(str, required))
    result["builderImage"] = image
    tagged = re.fullmatch(r"quay\.io/opencloudeu/golang-ci:(\d+)\.(\d+)", image)
    if tagged:
        available = tuple(map(int, tagged.groups()))
    elif image == "quay.io/opencloudeu/golang-ci@" + REVIEWED_BUILDER:
        available = (1, 26)
        result["findings"].append("builder_version_from_prior_review_only_not_fresh_attestation")
    else:
        result["findings"].append("unknown_or_unreviewed_go_builder")
        return result
    result["builderGo"] = ".".join(map(str, available))
    if available < required:
        result["findings"].append("go_builder_older_than_module_requirement")
        return result
    if target not in RECIPES:
        result["findings"].append("unknown_recipe_target")
        return result
    if target != "production":
        if image != "quay.io/opencloudeu/golang-ci@" + REVIEWED_BUILDER:
            result["findings"].append("security_trial_builder_not_reviewed_digest")
            return result
        try:
            holds = release_hold_labels(recipe)
        except ValueError:
            result["findings"].append("security_trial_invalid_release_hold_instruction")
            return result
        if holds != ["false"]:
            result["findings"].append("security_trial_missing_explicit_release_hold")
            return result
        if not re.search(r"^RUN make go-generate build ENABLE_VIPS=true EDITION=dev\s*$", recipe, re.MULTILINE):
            result["findings"].append("security_trial_build_flags_changed")
            return result
        if target == "security-trial-pinned":
            stages = re.findall(r"^FROM\s+(\S+)", recipe, re.MULTILINE)
            if len(stages) != 3 or not all(re.search(r"@sha256:[0-9a-f]{64}$", stage) for stage in stages):
                result["findings"].append("trial_base_images_not_all_digest_pinned")
                return result
    result["status"] = "PASS_STATIC"
    result["findings"].append("static_only_runtime_dependency_security_and_recovery_unverified")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True, choices=tuple(RECIPES))
    args = parser.parse_args()
    try:
        go_mod = (ROOT / "go.mod").read_text(encoding="utf-8")
        recipe = (ROOT / RECIPES[args.target]).read_text(encoding="utf-8")
        result = assess(go_mod, recipe, args.target)
    except OSError:
        result = {"target": args.target, "status": "BLOCKED", "releaseApproved": False,
                  "findings": ["recipe_or_go_mod_unavailable"]}
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "PASS_STATIC" else 2


if __name__ == "__main__":
    raise SystemExit(main())
