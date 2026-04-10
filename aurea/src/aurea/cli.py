# Entry point for the Aurea CLI.
# IMPORTANT: Do NOT use `from __future__ import annotations` in this file.
# Combining it with typing_extensions.Annotated at runtime causes TypeError on
# Python 3.8 (known CPython bug — Art. I exception).
from typing import Optional

import typer
from typing_extensions import Annotated

from aurea import __version__
from aurea.exceptions import AureaError

app = typer.Typer(
    name="aurea",
    help="Generate high-quality standalone HTML presentations via AI agents.",
    no_args_is_help=True,
)

# Theme sub-group (registered as `aurea theme <subcommand>`)
theme_app = typer.Typer(help="Browse and manage presentation themes.")
app.add_typer(theme_app, name="theme")


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"aurea {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        Optional[bool],
        typer.Option(
            "--version",
            callback=_version_callback,
            is_eager=True,
            help="Print version and exit.",
        ),
    ] = None,
) -> None:
    """Aurea — AI-guided presentation toolkit."""


# ---------------------------------------------------------------------------
# init
# ---------------------------------------------------------------------------
@app.command("init")
def init_command(
    project_name: Annotated[
        Optional[str],
        typer.Argument(help="Directory name for the new project."),
    ] = None,
    agent: Annotated[
        str, typer.Option("--agent", help="Target AI agent id.")
    ] = "claude",
    theme: Annotated[
        str, typer.Option("--theme", help="Initial theme id.")
    ] = "default",
    here: Annotated[
        bool, typer.Option("--here", help="Initialize in current directory.")
    ] = False,
    force: Annotated[
        bool, typer.Option("--force", help="Overwrite if project directory exists.")
    ] = False,
    no_git: Annotated[
        bool, typer.Option("--no-git", help="Skip git init.")
    ] = False,
    commands_dir: Annotated[
        Optional[str],
        typer.Option("--commands-dir", help="Override commands directory path."),
    ] = None,
    lang: Annotated[
        str, typer.Option("--lang", help="Language for generated templates.")
    ] = "en",
) -> None:
    """Initialize a new Aurea presentation project."""
    from aurea.commands.init import scaffold_project

    scaffold_project(
        project_name=project_name,
        agent=agent,
        theme=theme,
        here=here,
        force=force,
        no_git=no_git,
        commands_dir=commands_dir,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# build
# ---------------------------------------------------------------------------
@app.command("build")
def build_command(
    input_file: Annotated[
        Optional[str],
        typer.Option("--input", help="Source Markdown file."),
    ] = None,
    output_file: Annotated[
        Optional[str],
        typer.Option("--output", help="Output HTML file."),
    ] = None,
    theme_override: Annotated[
        Optional[str],
        typer.Option("--theme", help="Override active theme."),
    ] = None,
    minify: Annotated[
        bool, typer.Option("--minify", help="Minify HTML output.")
    ] = False,
    watch: Annotated[
        bool, typer.Option("--watch", help="Watch for changes and rebuild.")
    ] = False,
    embed_fonts: Annotated[
        bool, typer.Option("--embed-fonts", help="Inline web fonts as base64.")
    ] = False,
) -> None:
    """Compile slides/presentation.md into a standalone HTML presentation."""
    from aurea.commands.build import run_build

    run_build(
        input_file=input_file,
        output_file=output_file,
        theme_override=theme_override,
        minify=minify,
        watch=watch,
        embed_fonts=embed_fonts,
    )


# ---------------------------------------------------------------------------
# serve
# ---------------------------------------------------------------------------
@app.command("serve")
def serve_command(
    port: Annotated[
        int, typer.Option("--port", help="Preferred port (tries sequential if occupied).")
    ] = 8000,
    host: Annotated[
        str, typer.Option("--host", help="Bind address.")
    ] = "127.0.0.1",
    watch: Annotated[
        bool, typer.Option("--watch", help="Rebuild on file changes and reload.")
    ] = False,
    input_file: Annotated[
        Optional[str],
        typer.Option("--input", help="HTML file to serve."),
    ] = None,
) -> None:
    """Start a local HTTP server to preview the presentation."""
    from aurea.commands.serve import run_serve

    run_serve(port=port, host=host, watch=watch, input_file=input_file)


# ---------------------------------------------------------------------------
# extract (lazy import — depends on [extract] optional group)
# ---------------------------------------------------------------------------
@app.command("extract")
def extract_command(
    url: Annotated[str, typer.Argument(help="Public URL to scrape.")],
    name: Annotated[
        Optional[str],
        typer.Option("--name", help="Output theme id/directory name."),
    ] = None,
    depth: Annotated[
        int, typer.Option("--depth", help="Crawl depth.")
    ] = 1,
    raw: Annotated[
        bool, typer.Option("--raw", help="Skip semantic token interpretation.")
    ] = False,
    use: Annotated[
        bool, typer.Option("--use", help="Apply extracted theme after extraction.")
    ] = False,
    timeout: Annotated[
        int, typer.Option("--timeout", help="HTTP request timeout in seconds.")
    ] = 30,
    user_agent: Annotated[
        str, typer.Option("--user-agent", help="HTTP User-Agent header.")
    ] = "Aurea/1.0",
    delay: Annotated[
        float, typer.Option("--delay", help="Delay between page requests.")
    ] = 1.0,
) -> None:
    """Extract a design system from a URL and save it as a reusable theme."""
    try:
        from aurea.commands.extract import run_extract
    except ImportError:
        raise AureaError(
            "Extract dependencies missing. Run: pip install aurea[extract]"
        )

    run_extract(
        url=url,
        name=name,
        depth=depth,
        raw=raw,
        use=use,
        timeout=timeout,
        user_agent=user_agent,
        delay=delay,
    )


# ---------------------------------------------------------------------------
# theme sub-commands
# ---------------------------------------------------------------------------
@theme_app.command("list")
def theme_list_command(
    format_: Annotated[
        str, typer.Option("--format", help="Output format: table or json.")
    ] = "table",
) -> None:
    """List all available themes."""
    from aurea.commands.theme import cmd_list

    cmd_list(format_=format_)


@theme_app.command("search")
def theme_search_command(
    query: Annotated[str, typer.Argument(help="Search query.")],
    category: Annotated[
        Optional[str], typer.Option("--category", help="Filter by category.")
    ] = None,
    tag: Annotated[
        Optional[str], typer.Option("--tag", help="Filter by tag.")
    ] = None,
    format_: Annotated[
        str, typer.Option("--format", help="Output format: table or json.")
    ] = "table",
) -> None:
    """Search themes by keyword."""
    from aurea.commands.theme import cmd_search

    cmd_search(query=query, category=category, tag=tag, format_=format_)


@theme_app.command("info")
def theme_info_command(
    theme_id: Annotated[str, typer.Argument(help="Theme id.")],
) -> None:
    """Show full metadata for a theme."""
    from aurea.commands.theme import cmd_info

    cmd_info(theme_id=theme_id)


@theme_app.command("show")
def theme_show_command(
    theme_id: Annotated[str, typer.Argument(help="Theme id.")],
) -> None:
    """Print the DESIGN.md of a theme."""
    from aurea.commands.theme import cmd_show

    cmd_show(theme_id=theme_id)


@theme_app.command("use")
def theme_use_command(
    theme_id: Annotated[str, typer.Argument(help="Theme id to apply.")],
) -> None:
    """Apply a theme to the current project."""
    from aurea.commands.theme import cmd_use

    cmd_use(theme_id=theme_id)


@theme_app.command("create")
def theme_create_command(
    theme_name: Annotated[str, typer.Argument(help="New theme id.")],
    output: Annotated[
        Optional[str],
        typer.Option("--output", help="Directory to create the theme scaffold in."),
    ] = None,
) -> None:
    """Scaffold a new custom theme."""
    from aurea.commands.theme import cmd_create

    cmd_create(theme_name=theme_name, output=output)


if __name__ == "__main__":
    app()
