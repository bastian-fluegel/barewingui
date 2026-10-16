# Contributing

Thanks for trying BareWinGUI. The most useful thing right now is feedback from real Windows machines: open an issue (bug report or feedback form) with your Windows version, display scaling and a small script.

Code changes:

```bash
python -m unittest discover -s tests   # logic tests run everywhere, window tests on Windows
```

- Keep it dependency free (standard library only).
- Native controls only: BareWinGUI draws nothing itself.
- Add a test for every fix; window tests belong in `tests/` with the Windows-only skip.
- Please open an issue before a larger change.
