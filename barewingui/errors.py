"""
barewingui.errors
~~~~~~~~~~~~~~~~~
Exception types raised by BareWinGUI.
"""

from __future__ import annotations


class BareWinGUIError(Exception):
    """Base class for all BareWinGUI errors."""


class PlatformError(BareWinGUIError, RuntimeError):
    """Raised when a Windows-only feature is used on another platform."""


class LayoutError(BareWinGUIError, ValueError):
    """Raised for invalid layout configuration (bad option values, misuse of containers)."""
