"""Native directory picker for local Hermes WebUI sessions."""

from pathlib import Path


class DirectoryPickerUnavailable(RuntimeError):
    """Raised when the host cannot display a native directory picker."""


def pick_directory(initial_directory: str = "") -> str | None:
    """Show the host OS directory dialog and return an absolute path.

    The WebUI backend needs a real host path (not an uploaded browser folder),
    so this is intentionally used only by the loopback-only route.
    """
    try:
        import tkinter as tk
        from tkinter import filedialog
    except (ImportError, RuntimeError) as exc:
        raise DirectoryPickerUnavailable("Native folder selection is unavailable") from exc

    initial_path = Path(initial_directory).expanduser() if initial_directory else Path.home()
    if not initial_path.is_dir():
        initial_path = Path.home()

    root = None
    try:
        root = tk.Tk()
        root.withdraw()
        try:
            root.attributes("-topmost", True)
        except tk.TclError:
            pass
        selected = filedialog.askdirectory(
            parent=root,
            initialdir=str(initial_path),
            mustexist=True,
            title="Choose workspace folder",
        )
    except (tk.TclError, OSError, RuntimeError) as exc:
        raise DirectoryPickerUnavailable("Native folder selection is unavailable on this host") from exc
    finally:
        if root is not None:
            try:
                root.destroy()
            except tk.TclError:
                pass

    if not selected:
        return None
    return str(Path(selected).expanduser().resolve())
