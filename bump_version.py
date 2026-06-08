# -*- coding: utf-8 -*-
"""
bump_version.py — update the app version in version.py.

Usage:
    python bump_version.py            # bump patch  (4.1 -> 4.1.1 / 4.1.1 -> 4.1.2)
    python bump_version.py patch      # same as above
    python bump_version.py minor      # 4.1 -> 4.2
    python bump_version.py major      # 4.1 -> 5.0
    python bump_version.py 4.5.2      # set an explicit version
"""

import os
import re
import sys

VERSION_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "version.py")


def read_version():
    with open(VERSION_FILE, "r", encoding="utf-8") as f:
        text = f.read()
    m = re.search(r'__version__\s*=\s*"([^"]+)"', text)
    return text, (m.group(1) if m else "0.0")


def bump(current, part):
    nums = [int(x) for x in current.split(".")]
    while len(nums) < 3:
        nums.append(0)
    major, minor, patch = nums[0], nums[1], nums[2]
    if part == "major":
        major, minor, patch = major + 1, 0, 0
    elif part == "minor":
        minor, patch = minor + 1, 0
    else:  # patch
        patch += 1
    return "%d.%d.%d" % (major, minor, patch)


def main():
    arg = sys.argv[1].strip() if len(sys.argv) > 1 else "patch"
    text, current = read_version()

    if re.fullmatch(r"\d+(\.\d+){1,3}", arg):
        new = arg
    elif arg in ("major", "minor", "patch"):
        new = bump(current, arg)
    else:
        print("Unknown argument:", arg)
        print(__doc__)
        sys.exit(1)

    new_text = re.sub(r'(__version__\s*=\s*")[^"]+(")', r"\g<1>%s\g<2>" % new, text)
    with open(VERSION_FILE, "w", encoding="utf-8") as f:
        f.write(new_text)
    print("Version: %s -> %s" % (current, new))
    print("Now rebuild:  python -m PyInstaller build.spec --clean --noconfirm")


if __name__ == "__main__":
    main()
