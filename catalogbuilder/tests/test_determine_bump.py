"""Tests for .github/scripts/determine_bump.py"""

import os
import importlib.util

import pytest

# Load the script as a module without requiring a package structure
_script_path = os.path.join(
    os.path.dirname(__file__), "..", "..", ".github", "scripts", "determine_bump.py"
)
_spec = importlib.util.spec_from_file_location("determine_bump", _script_path)
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)
determine_bump = _module.determine_bump


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _body(minor=False, major=False, no_bump=False):
    """Build a PR body with the requested checkboxes ticked."""
    lines = [
        f"- {'[x]' if minor else '[ ]'} **Minor version**",
        f"- {'[x]' if major else '[ ]'} **Major version**",
        f"- {'[x]' if no_bump else '[ ]'} **No version bump**",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Happy-path tests
# ---------------------------------------------------------------------------

def test_minor_checkbox_returns_minor():
    assert determine_bump(_body(minor=True)) == "minor"


def test_major_checkbox_returns_major():
    assert determine_bump(_body(major=True)) == "major"


def test_no_bump_checkbox_returns_none():
    assert determine_bump(_body(no_bump=True)) == "none"


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------

def test_no_checkbox_raises_system_exit():
    with pytest.raises(SystemExit):
        determine_bump(_body())


def test_multiple_checkboxes_raises_system_exit():
    with pytest.raises(SystemExit):
        determine_bump(_body(minor=True, major=True))


def test_all_checkboxes_raises_system_exit():
    with pytest.raises(SystemExit):
        determine_bump(_body(minor=True, major=True, no_bump=True))


# ---------------------------------------------------------------------------
# Case-insensitivity
# ---------------------------------------------------------------------------

def test_matching_is_case_insensitive():
    # Vary the case of the checkbox marker text; the parser uppercases both
    # sides before comparing, so different capitalisation must still match.
    body_upper = "- [X] **MINOR VERSION**"
    assert determine_bump(body_upper) == "minor"

    body_lower = "- [x] **minor version**"
    assert determine_bump(body_lower) == "minor"
