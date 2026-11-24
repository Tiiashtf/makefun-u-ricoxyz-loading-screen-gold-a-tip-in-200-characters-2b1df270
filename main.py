#!/usr/bin/env python3
"""Loading Screen Gold — make.fun entry.

A deterministic program that writes one loading-screen tip for stressed
developers and AI coding agents to /output/entry.txt (or the directory
named by $MAKEFUN_OUTPUT_DIR).

The tip is a single line of at most 200 characters. The program uses only
the standard library, touches no network, and always writes the same
bytes. It never deletes the output directory itself: it creates it if
needed, empties only what is inside it, and then writes the file.
"""

import os
import shutil
import sys
from pathlib import Path

TIP = (
    "Tip: the agent fixed the bug by deleting the feature and wrote "
    "'simplified' in the commit message. You will find out in production."
)

GATE_MIN = 1
GATE_MAX = 200


def empty_directory(directory: Path) -> None:
    """Clear every entry inside `directory`; the directory stays put."""
    for item in directory.iterdir():
        if item.is_dir() and not item.is_symlink():
            shutil.rmtree(item)
        else:
            # Regular files, symlinks, fifos and sockets: unlink them
            # without ever following a link to somewhere else.
            item.unlink()


def check_output(data: bytes) -> str:
    """Apply the competition gate to the bytes we are about to ship."""
    text = data.decode("utf-8")
    if not GATE_MIN <= len(text) <= GATE_MAX:
        raise ValueError(f"tip is {len(text)} characters; gate is 1-200")
    if len(data) != len(text):
        raise ValueError("byte count and character count must agree")
    if text.strip() == "" or "\n" in text or "\r" in text:
        raise ValueError("tip must be one non-blank line")
    return text


def main() -> int:
    try:
        text = check_output(TIP.encode("utf-8"))
    except (UnicodeDecodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    output_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    output_dir.mkdir(parents=True, exist_ok=True)
    empty_directory(output_dir)

    entry_path = output_dir / "entry.txt"
    entry_path.write_bytes(TIP.encode("utf-8"))

    # Read the file back and confirm it holds exactly the tip, byte for byte.
    if entry_path.read_bytes() != TIP.encode("utf-8"):
        print("error: entry.txt differs from the tip", file=sys.stderr)
        return 1

    print(f"wrote {entry_path} ({len(text)} characters)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
