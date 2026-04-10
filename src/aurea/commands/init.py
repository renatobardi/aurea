# IMPORTANT: Do NOT use `from __future__ import annotations` in this file.
# Typer commands use typing_extensions.Annotated at runtime — combining with
# the future import causes TypeError on Python 3.8 (Art. I exception).
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, FrozenSet, Optional, Tuple

from aurea._log import _log
from aurea.exceptions import AureaError

# Required DESIGN.md sections (from FR-020)
REQUIRED_SECTIONS: FrozenSet[str] = frozenset(
    {
        "visual theme",
        "color palette",
        "typography",
        "components",
        "layout",
        "depth",
        "do's",
        "responsive",
        "agent prompt",
    }
)

# ---------------------------------------------------------------------------
# Agent configuration
# ---------------------------------------------------------------------------

# Maps agent id → (commands_dir, file_format, arg_placeholder)
AGENT_CONFIG: Dict[str, Tuple[str, str, str]] = {
    "claude": (".claude/commands", ".md", "$ARGUMENTS"),
    "gemini": (".gemini/commands", ".toml", "{{args}}"),
    "copilot": (".github/copilot-instructions", ".agent.md", "$ARGUMENTS"),
    "windsurf": (".windsurf/commands", ".md", "$ARGUMENTS"),
    "devin": (".devin/commands", ".md", "$ARGUMENTS"),
    "chatgpt": (".chatgpt/commands", ".md", "$ARGUMENTS"),
    "cursor": (".cursor/commands", ".md", "$ARGUMENTS"),
    "generic": ("commands", ".md", "$ARGUMENTS"),
}

# Names of the 7 standard templates (without extension)
TEMPLATE_NAMES = [
    "aurea.theme",
    "aurea.outline",
    "aurea.generate",
    "aurea.refine",
    "aurea.visual",
    "aurea.extract",
    "aurea.build",
]

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class ProjectConfig:
    agent: str
    theme: str
    themes_dir: str
    slides_dir: str
    output_dir: str
    version: str


def write_config(path: Path, config: ProjectConfig) -> None:
    """Serialize ProjectConfig to JSON at *path*."""
    data = {
        "agent": config.agent,
        "theme": config.theme,
        "themes_dir": config.themes_dir,
        "slides_dir": config.slides_dir,
        "output_dir": config.output_dir,
        "version": config.version,
    }
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# Placeholder substitution
# ---------------------------------------------------------------------------

_PLACEHOLDER_KEYS = [
    "{{DESIGN_MD_PATH}}",
    "{{THEME_CSS_PATH}}",
    "{{CONFIG_PATH}}",
    "{{REGISTRY_PATH}}",
    "{{SLIDES_DIR}}",
    "{{OUTPUT_DIR}}",
]


def substitute_placeholders(
    template_text: str,
    design_md_path: str,
    theme_css_path: str,
    config_path: str,
    registry_path: str,
    slides_dir: str,
    output_dir: str,
) -> str:
    """Replace all 7 known placeholder tokens in *template_text*."""
    return (
        template_text.replace("{{DESIGN_MD_PATH}}", design_md_path)
        .replace("{{THEME_CSS_PATH}}", theme_css_path)
        .replace("{{CONFIG_PATH}}", config_path)
        .replace("{{REGISTRY_PATH}}", registry_path)
        .replace("{{SLIDES_DIR}}", slides_dir)
        .replace("{{OUTPUT_DIR}}", output_dir)
    )


# ---------------------------------------------------------------------------
# Theme resolution
# ---------------------------------------------------------------------------


def _global_themes_dir() -> Path:
    """Return the path to the bundled themes directory."""
    return Path(__file__).parent.parent / "themes"


def _resolve_theme_dir(theme_id: str) -> Path:
    """Return the path to the global theme directory for *theme_id*."""
    theme_dir = _global_themes_dir() / theme_id
    if not theme_dir.is_dir():
        raise AureaError(
            f"Error: theme '{theme_id}' not found. Run 'aurea theme search {theme_id}' "
            "to find similar themes."
        )
    return theme_dir


def _validate_design_md(design_md_path: Path, theme_id: str) -> None:
    """Raise AureaError if DESIGN.md is missing or lacks any of the 9 required sections."""
    if not design_md_path.exists():
        raise AureaError(
            f"Error: theme '{theme_id}' DESIGN.md missing or invalid (needs 9 sections)"
        )
    text = design_md_path.read_text(encoding="utf-8").lower()
    missing = [s for s in REQUIRED_SECTIONS if s not in text]
    if missing:
        raise AureaError(
            "Error: theme '{t}' DESIGN.md is missing sections: {m}".format(
                t=theme_id, m=", ".join(sorted(missing))
            )
        )


def _global_registry() -> Optional[Path]:
    """Return global registry.json path if it exists."""
    p = _global_themes_dir() / "registry.json"
    return p if p.exists() else None


# ---------------------------------------------------------------------------
# Command file copying
# ---------------------------------------------------------------------------


def copy_agent_commands(
    agent_id: str,
    project_root: Path,
    design_md_path: str,
    theme_css_path: str,
    config_path: str,
    registry_path: str,
    slides_dir: str,
    output_dir: str,
    commands_dir_override: Optional[str] = None,
) -> None:
    """Copy pre-built agent command templates into the project.

    If *commands_dir_override* is not None (from --commands-dir), it is used
    as the write target. Otherwise the default from AGENT_CONFIG is used.

    Templates are already in their native formats (authoring-time conversion
    was done in the source tree — there is no runtime format conversion here).
    """
    if agent_id not in AGENT_CONFIG:
        raise AureaError(
            "Error: unknown agent '{a}'. Valid agents: {valid}".format(
                a=agent_id,
                valid=", ".join(sorted(AGENT_CONFIG.keys())),
            )
        )

    default_dir, file_format, _arg_placeholder = AGENT_CONFIG[agent_id]
    target_dir_str = commands_dir_override if commands_dir_override is not None else default_dir
    target_dir = project_root / target_dir_str
    target_dir.mkdir(parents=True, exist_ok=True)

    # Source: pre-built templates for this agent
    src_commands_dir = Path(__file__).parent.parent / "agent_commands" / agent_id

    for name in TEMPLATE_NAMES:
        # Determine source filename
        if agent_id == "copilot":
            src_filename = f"{name}.agent.md"
        elif agent_id == "gemini":
            src_filename = f"{name}.toml"
        else:
            src_filename = f"{name}.md"

        src_file = src_commands_dir / src_filename
        if not src_file.exists():
            _log.warning("Template not found, skipping: %s", src_file)
            continue

        content = src_file.read_text(encoding="utf-8")
        content = substitute_placeholders(
            content,
            design_md_path=design_md_path,
            theme_css_path=theme_css_path,
            config_path=config_path,
            registry_path=registry_path,
            slides_dir=slides_dir,
            output_dir=output_dir,
        )

        # Determine output filename
        if agent_id == "copilot":
            out_filename = f"{name}.agent.md"
        elif agent_id == "gemini":
            out_filename = f"{name}.toml"
        else:
            out_filename = f"{name}.md"

        out_file = target_dir / out_filename
        out_file.write_text(content, encoding="utf-8")
        _log.info("  + %s", out_file.relative_to(project_root))


# ---------------------------------------------------------------------------
# Main scaffold function
# ---------------------------------------------------------------------------


def scaffold_project(
    project_name: Optional[str],
    agent: str,
    theme: str,
    here: bool,
    force: bool,
    no_git: bool,
    commands_dir: Optional[str],
    lang: str,
) -> None:
    """Create a complete Aurea project directory structure."""
    from aurea import __version__

    # --- validate agent ---
    if agent not in AGENT_CONFIG:
        _log.error(
            "Error: unknown agent '%s'. Valid agents: %s",
            agent,
            ", ".join(sorted(AGENT_CONFIG.keys())),
        )
        sys.exit(1)

    # --- resolve project root ---
    if here:
        project_root = Path.cwd()
    elif project_name:
        project_root = Path.cwd() / project_name
    else:
        project_root = Path.cwd()

    # --- check for existing directory ---
    if project_root.exists() and not here and project_name:
        if not force:
            _log.error(
                "Error: directory '%s' already exists. Use --force to overwrite.",
                project_name,
            )
            sys.exit(1)
        # With --force: existing slides/ is preserved
    elif not project_root.exists():
        project_root.mkdir(parents=True)

    # --- apply defaults notice ---
    # Print when either agent OR theme is using a default value
    # This warns users about defaults even if only one was explicitly set
    if agent == "claude" or theme == "default":
        msg = "  Using defaults:"
        if agent == "claude":
            msg += " --agent claude"
        if theme == "default":
            msg += " --theme default"
        print(msg, file=sys.stderr)

    # --- validate and resolve theme ---
    try:
        global_theme_dir = _resolve_theme_dir(theme)
        _validate_design_md(global_theme_dir / "DESIGN.md", theme)
    except AureaError as exc:
        _log.error("%s", exc)
        sys.exit(1)

    # --- language note (v1: English only) ---
    if lang != "en":
        print(
            f"  Language '{lang}' not available, using 'en'",
            file=sys.stderr,
        )
        lang = "en"

    # --- create directory structure ---
    aurea_dir = project_root / ".aurea"
    local_themes_dir = aurea_dir / "themes"
    local_theme_dir = local_themes_dir / theme
    slides_dir = project_root / "slides"
    output_dir = project_root / "output"

    local_theme_dir.mkdir(parents=True, exist_ok=True)
    slides_dir.mkdir(exist_ok=True)
    output_dir.mkdir(exist_ok=True)

    # --- .gitkeep files ---
    gitkeep_slides = slides_dir / ".gitkeep"
    if not gitkeep_slides.exists():
        gitkeep_slides.write_text("")
    gitkeep_output = output_dir / ".gitkeep"
    if not gitkeep_output.exists():
        gitkeep_output.write_text("")

    # --- copy theme files ---
    theme_files = ["DESIGN.md", "theme.css", "layout.css", "meta.json"]
    for fname in theme_files:
        src = global_theme_dir / fname
        dst = local_theme_dir / fname
        if src.exists():
            shutil.copy2(src, dst)
            _log.info(
                "  + %s",
                dst.relative_to(project_root),
            )

    # --- write local registry.json (minimal — only the selected theme) ---
    # The global registry is always read by load_registry(); the local registry
    # exists only to track locally-installed/extracted themes so they shadow global.
    local_registry_path = local_themes_dir / "registry.json"
    _meta_src = local_theme_dir / "meta.json"
    if _meta_src.exists():
        meta = json.loads(_meta_src.read_text(encoding="utf-8"))
        meta["path"] = theme
        registry_data: Dict[str, Any] = {
            "version": "1.0.0",
            "sources": [],
            "themes": [meta],
        }
        local_registry_path.write_text(json.dumps(registry_data, indent=2), encoding="utf-8")

    _log.info("  + %s", local_registry_path.relative_to(project_root))

    # --- write config.json ---
    config = ProjectConfig(
        agent=agent,
        theme=theme,
        themes_dir=".aurea/themes",
        slides_dir="slides",
        output_dir="output",
        version=__version__,
    )
    config_path = aurea_dir / "config.json"
    write_config(config_path, config)
    _log.info("  + %s", config_path.relative_to(project_root))

    # --- copy agent commands ---
    rel_design_md = f".aurea/themes/{theme}/DESIGN.md"
    rel_theme_css = f".aurea/themes/{theme}/theme.css"
    rel_config = ".aurea/config.json"
    rel_registry = ".aurea/themes/registry.json"
    rel_slides = "slides"
    rel_output = "output"

    try:
        copy_agent_commands(
            agent_id=agent,
            project_root=project_root,
            design_md_path=rel_design_md,
            theme_css_path=rel_theme_css,
            config_path=rel_config,
            registry_path=rel_registry,
            slides_dir=rel_slides,
            output_dir=rel_output,
            commands_dir_override=commands_dir,
        )
    except AureaError as exc:
        _log.error("%s", exc)
        sys.exit(1)

    # --- write README.md ---
    try:
        from aurea._tpl import render_template

        readme_content = render_template(
            "slide_readme.md.j2",
            project_name=project_name or project_root.name,
            agent=agent,
            theme=theme,
        )
        readme_path = project_root / "README.md"
        if not readme_path.exists() or force:
            readme_path.write_text(readme_content, encoding="utf-8")
            _log.info("  + README.md")
    except Exception as exc:
        _log.warning("Could not render README.md: %s", exc)

    # --- git init ---
    if not no_git:
        try:
            git_dir = project_root / ".git"
            if not git_dir.exists():
                subprocess.run(
                    ["git", "init", str(project_root)],
                    check=True,
                    capture_output=True,
                )
        except (subprocess.CalledProcessError, FileNotFoundError):
            _log.warning("git init skipped (git not available or failed)")
