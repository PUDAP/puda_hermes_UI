from pathlib import Path

WORKSPACE_JS = Path("static/workspace.js").read_text(encoding="utf-8")
SESSIONS_JS = Path("static/sessions.js").read_text(encoding="utf-8")
MESSAGES_JS = Path("static/messages.js").read_text(encoding="utf-8")
INDEX_HTML = Path("static/index.html").read_text(encoding="utf-8")
STYLE_CSS = Path("static/style.css").read_text(encoding="utf-8")
CHANGELOG = Path("CHANGELOG.md").read_text(encoding="utf-8")


def test_workspace_artifacts_tab_collects_session_files_and_previews_them():
    assert 'id="workspaceArtifactsTab"' in INDEX_HTML
    assert 'id="workspaceArtifacts"' in INDEX_HTML
    assert "function collectSessionArtifacts()" in WORKSPACE_JS
    assert "function _artifactCandidatesFromToolCall(tc)" in WORKSPACE_JS
    assert "ARTIFACT_IGNORE_RE" in WORKSPACE_JS
    assert "node_modules" in WORKSPACE_JS and "__pycache__" in WORKSPACE_JS
    assert "function renderSessionArtifacts()" in WORKSPACE_JS
    assert "function scheduleRenderSessionArtifacts()" in WORKSPACE_JS
    assert "function openArtifactPath(path)" in WORKSPACE_JS
    assert "openFile(rel);" in WORKSPACE_JS
    assert "Prose mentions" in WORKSPACE_JS
    assert "/(?:created|wrote|updated|edited|saved|modified)" not in WORKSPACE_JS
    assert "panel.dataset.activeTab = _workspacePanelActiveTab" in WORKSPACE_JS
    assert "renderSessionArtifacts();" in SESSIONS_JS
    assert "typeof scheduleRenderSessionArtifacts==='function'" in MESSAGES_JS
    assert "S.toolCalls=d.session.tool_calls.map" in MESSAGES_JS
    assert ".workspace-artifact-item" in STYLE_CSS


def test_pdf_chat_artifacts_use_workspace_relative_path_handling():
    """Absolute artifact paths must not be sent directly to preview APIs."""
    fn_start = WORKSPACE_JS.index("function openWorkspaceArtifact(path)")
    fn_end = WORKSPACE_JS.index("async function openFile(path", fn_start)
    body = WORKSPACE_JS[fn_start:fn_end]

    assert "openArtifactPath(path)" in body
    assert "openFile(path)" not in body


def test_local_images_and_pdfs_open_in_workspace_beside_chat():
    ui_js = Path("static/ui.js").read_text(encoding="utf-8")

    assert 'class="workspace-preview-card image-workspace-card"' in ui_js
    assert 'class="workspace-preview-card pdf-workspace-card"' in ui_js
    assert "openWorkspaceArtifact(this.dataset.path)" in ui_js
    assert "querySelectorAll('.workspace-preview-open[data-path]')" in ui_js


def test_workspace_panel_width_is_pointer_resizable():
    boot_js = Path("static/boot.js").read_text(encoding="utf-8")

    assert 'id="rightpanelResize"' in INDEX_HTML
    assert 'aria-label="Resize workspace panel"' in INDEX_HTML
    assert "initResize('rightpanelResize'" in boot_js
    assert "handle.addEventListener('pointerdown'" in boot_js
    assert "document.addEventListener('pointermove'" in boot_js
    assert "localStorage.setItem(storageKey" in boot_js
    assert "touch-action:none" in STYLE_CSS


def test_desktop_theme_does_not_override_resized_workspace_width():
    preview_rule = STYLE_CSS.split('html[data-workspace-preview="open"] .rightpanel', 1)[1].split("}", 1)[0]
    assert "!important" not in preview_rule
    assert "min-width:620px" not in preview_rule

    biomni_rule = STYLE_CSS.rsplit(".rightpanel{", 1)[1].split("}", 1)[0]
    assert "width:min(27vw,520px)!important" not in biomni_rule
    assert "min-width:360px" not in biomni_rule


def test_workspace_artifacts_structured_args_are_mutation_gated():
    """Read-only tool args with path fields must not appear as changed files."""
    fn_start = WORKSPACE_JS.index("function _artifactCandidatesFromToolCall(tc)")
    fn_end = WORKSPACE_JS.index("function collectSessionArtifacts()", fn_start)
    body = WORKSPACE_JS[fn_start:fn_end]

    args_gate = body.index("args && typeof args === 'object'")
    mutation_gate = body.rfind("ARTIFACT_MUTATION_TOOLS.has(name)", 0, args_gate)

    assert mutation_gate >= 0, (
        "structured path/file_path/source/destination extraction must be gated "
        "on ARTIFACT_MUTATION_TOOLS so read_file/list_dir paths do not appear "
        "as created or edited artifacts"
    )


def test_changelog_mentions_workspace_artifacts_tab():
    unreleased = CHANGELOG.split("## [v0.51.103]", 1)[0]
    assert "Artifacts tab" in unreleased
