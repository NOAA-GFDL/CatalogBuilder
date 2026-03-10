import sys
from typing import Literal

BumpLevel = Literal["major", "minor", "none"]

# Checkbox labels must match these substrings in the PR body
CHECKBOX_MAP = {
    "Minor version": "minor",
    "Major version": "major",
}

def determine_bump(body: str) -> BumpLevel:
    checked = []
    for label, level in CHECKBOX_MAP.items():
        # GitHub markdown checked box:
        # - [x] label text
        marker = f"- [x] {label}"
        if marker in body:
            checked.append(level)

    if len(checked) == 0:
        return "none"
    if len(checked) > 1:
        # Raise an error if multiple boxes are checked
        raise SystemExit(
            f"Multiple bump checkboxes selected: {checked}. Please select only one."
        )
    return checked[0]

def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: determine_bump.py '<pr_body>'")

    body = sys.argv[1]
    level = determine_bump(body)
    # Print just the level so the workflow can capture it
    print(level)

if __name__ == "__main__":
    main()
