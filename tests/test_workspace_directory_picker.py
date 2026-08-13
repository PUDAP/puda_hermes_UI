from pathlib import Path

from api import routes


class _Handler:
    client_address = ("127.0.0.1", 12345)


def test_workspace_picker_returns_selected_path(monkeypatch, tmp_path):
    monkeypatch.setattr("api.directory_picker.pick_directory", lambda initial: str(tmp_path))
    captured = {}
    monkeypatch.setattr(routes, "j", lambda _handler, payload, **_kwargs: captured.update(payload))
    routes._handle_workspace_pick_directory(_Handler(), {"initial_path": str(tmp_path.parent)})
    assert captured == {
        "ok": True,
        "supported": True,
        "canceled": False,
        "path": str(tmp_path),
    }


def test_workspace_picker_does_not_open_dialog_for_remote_client(monkeypatch):
    handler = _Handler()
    handler.client_address = ("203.0.113.10", 12345)
    monkeypatch.setattr(
        "api.directory_picker.pick_directory",
        lambda _initial: (_ for _ in ()).throw(AssertionError("dialog must stay closed")),
    )
    captured = {}
    monkeypatch.setattr(routes, "j", lambda _handler, payload, **_kwargs: captured.update(payload))
    routes._handle_workspace_pick_directory(handler, {})
    assert captured["supported"] is False


def test_workspace_folder_button_uses_directory_picker():
    root = Path(routes.__file__).parent.parent
    html = (root / "static" / "index.html").read_text(encoding="utf-8")
    panels = (root / "static" / "panels.js").read_text(encoding="utf-8")
    assert 'id="btnChooseWorkspace"' in html
    assert 'onclick="chooseWorkspaceDirectory()"' in html
    assert "async function chooseWorkspaceDirectory()" in panels
    assert "'/api/workspaces/pick-directory'" in panels