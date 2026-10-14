"""
barewingui.shortcuts
~~~~~~~~~~~~~~~~~~~~
Keyboard shortcut strings such as ``"Ctrl+Shift+S"`` or ``"F5"``. Pure Python.
"""

from __future__ import annotations

from dataclasses import dataclass

_MODIFIERS = {
    "ctrl": "ctrl", "control": "ctrl", "strg": "ctrl",
    "shift": "shift", "umschalt": "shift",
    "alt": "alt",
}

_NAMED_KEYS = {
    "enter": 0x0D, "return": 0x0D, "esc": 0x1B, "escape": 0x1B, "space": 0x20,
    "tab": 0x09, "backspace": 0x08, "del": 0x2E, "delete": 0x2E, "entf": 0x2E,
    "ins": 0x2D, "insert": 0x2D, "home": 0x24, "end": 0x23,
    "pgup": 0x21, "pageup": 0x21, "pgdn": 0x22, "pagedown": 0x22,
    "left": 0x25, "up": 0x26, "right": 0x27, "down": 0x28,
}
_CANONICAL = {
    0x0D: "Enter", 0x1B: "Esc", 0x20: "Space", 0x09: "Tab", 0x08: "Backspace",
    0x2E: "Del", 0x2D: "Ins", 0x24: "Home", 0x23: "End", 0x21: "PgUp", 0x22: "PgDn",
    0x25: "Left", 0x26: "Up", 0x27: "Right", 0x28: "Down",
}
_NEEDS_NO_MODIFIER = set(range(0x70, 0x88)) | {0x2E, 0x2D, 0x1B, 0x24, 0x23, 0x21, 0x22}


@dataclass(frozen=True)
class Shortcut:
    """A parsed shortcut: modifier flags plus a Windows virtual-key code."""

    vk: int
    ctrl: bool = False
    shift: bool = False
    alt: bool = False

    @property
    def label(self) -> str:
        """Canonical text, e.g. ``Ctrl+Shift+S`` (shown in menus)."""
        parts = []
        if self.ctrl:
            parts.append("Ctrl")
        if self.shift:
            parts.append("Shift")
        if self.alt:
            parts.append("Alt")
        if 0x70 <= self.vk <= 0x87:
            parts.append(f"F{self.vk - 0x6F}")
        elif self.vk in _CANONICAL:
            parts.append(_CANONICAL[self.vk])
        else:
            parts.append(chr(self.vk))
        return "+".join(parts)

    def __str__(self) -> str:
        return self.label


def parse_shortcut(text: str) -> Shortcut:
    """
    Parse ``"Ctrl+O"``, ``"ctrl+shift+s"``, ``"F5"``, ``"Alt+Left"``, ``"Strg+Entf"``.

    :raises ValueError: for unknown keys, or a plain letter/digit without Ctrl or Alt
        (that would steal normal typing).
    """
    if not isinstance(text, str) or not text.strip():
        raise ValueError("a shortcut must be a non-empty string like 'Ctrl+S'")
    flags = {"ctrl": False, "shift": False, "alt": False}
    key: str | None = None
    for raw in text.split("+"):
        part = raw.strip()
        if not part:
            raise ValueError(f"malformed shortcut {text!r}")
        modifier = _MODIFIERS.get(part.lower())
        if modifier is not None:
            if flags[modifier]:
                raise ValueError(f"modifier {part!r} repeated in shortcut {text!r}")
            flags[modifier] = True
        elif key is not None:
            raise ValueError(f"shortcut {text!r} has more than one key")
        else:
            key = part
    if key is None:
        raise ValueError(f"shortcut {text!r} has no key")

    lowered = key.lower()
    if lowered in _NAMED_KEYS:
        vk = _NAMED_KEYS[lowered]
    elif len(lowered) >= 2 and lowered[0] == "f" and lowered[1:].isdigit() and 1 <= int(lowered[1:]) <= 24:
        vk = 0x6F + int(lowered[1:])
    elif len(key) == 1 and key.isascii() and key.isalnum():
        vk = ord(key.upper())
    else:
        raise ValueError(f"unknown key {key!r} in shortcut {text!r}")

    if vk not in _NEEDS_NO_MODIFIER and not (flags["ctrl"] or flags["alt"]):
        raise ValueError(f"shortcut {text!r} needs Ctrl or Alt (a plain key would block typing)")
    return Shortcut(vk, **flags)
