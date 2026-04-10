# Quickstart: Aurea CLI and Presentation Toolkit

**Feature**: 001-aurea-cli-toolkit  
**Date**: 2026-04-08  
**Purpose**: Validate the implementation end-to-end before shipping. Follow these steps in order.

---

## Prerequisites

- Python 3.8+ available (check: `python3 --version`)
- Git available (for `aurea init` git setup)
- A terminal (PowerShell on Windows, bash/zsh on macOS/Linux)

---

## Step 1: Install (pip mode)

```bash
# From repo root
pip install -e ".[dev,extract]"

# Verify
aurea --version
# Expected: aurea 0.1.0

aurea --help
# Expected: shows init, build, serve, theme, extract subcommands
```

---

## Step 2: Initialize a Project

```bash
# Create a new project with defaults
aurea init my-demo

# Expected stdout: (nothing — silent on success)
# Expected stderr:
#   Using defaults: --agent claude --theme default
#   + my-demo/.aurea/config.json
#   + my-demo/.aurea/themes/default/DESIGN.md
#   + my-demo/.aurea/themes/default/theme.css
#   + my-demo/.aurea/themes/default/layout.css
#   + my-demo/.aurea/themes/default/meta.json
#   + my-demo/.aurea/themes/registry.json
#   + my-demo/.claude/commands/aurea.theme.md
#   + my-demo/.claude/commands/aurea.outline.md
#   + my-demo/.claude/commands/aurea.generate.md
#   + my-demo/.claude/commands/aurea.refine.md
#   + my-demo/.claude/commands/aurea.visual.md
#   + my-demo/.claude/commands/aurea.extract.md
#   + my-demo/.claude/commands/aurea.build.md
#   + my-demo/slides/.gitkeep
#   + my-demo/output/.gitkeep
#   + my-demo/README.md

cd my-demo

# Verify structure
cat .aurea/config.json
# Expected: {"agent": "claude", "theme": "default", "themes_dir": ".aurea/themes", ...}
```

---

## Step 3: Browse Themes

```bash
# List all available themes
aurea theme list
# Expected: table with 36+ rows, columns: ID | Name | Category | Mood | Colors

# Search for a dark theme
aurea theme search "dark minimal"
# Expected: 3-10 results ordered by relevance, takes <500ms

# View theme details
aurea theme info midnight
# Expected: Full metadata with color swatches, typography, mood description

# Apply a theme
aurea theme use midnight
# Expected stderr: Theme 'midnight' applied. Config updated.

cat .aurea/config.json
# Expected: active_theme is now "midnight"
```

---

## Step 4: Build a Presentation

Create a sample `slides/presentation.md`:

```bash
cat > slides/presentation.md << 'EOF'
---
title: "Microservices for CTOs"
author: "Jane Dev"
theme: "midnight"
---

# The Microservices Journey

From monolith to distributed systems

Note: Welcome everyone. This talk is about the architectural shift.

---

## Why Microservices?

- Independent deployability
- Technology flexibility  
- Team autonomy
- Scalability per service

Note: Each point corresponds to a real business driver.

---

## The Cost

Operational complexity increases **significantly**

Network calls replace function calls

Note: Don't skip this slide — set realistic expectations.

---

## When to Start

Deploy your monolith first.

Migrate when **team friction** exceeds **migration cost**

Note: Conway's Law applies here.

---

# Questions?

github.com/yourteam/architecture

EOF
```

```bash
# Build the presentation
aurea build

# Expected stdout: output/presentation.html
# Expected stderr: Built 5 slides in 0.XX s (XXX KB)

# Verify output
ls -lh output/presentation.html
# Expected: file exists, size ~200-500 KB

# Verify standalone (no external resources)
grep -c "https://" output/presentation.html
# Expected: 0 (zero external URLs)
```

---

## Step 5: Preview Locally

```bash
# Serve the presentation
aurea serve
# Expected stdout: Serving at http://127.0.0.1:8000 — press Ctrl+C to stop

# Open in browser: http://127.0.0.1:8000
# Expected: reveal.js presentation with midnight theme, 5 slides
# Press → to advance slides, S for speaker notes
```

```bash
# Test watch mode
aurea serve --watch
# (in another terminal) echo "test" >> slides/presentation.md
# Expected: rebuild triggered, browser reloads
```

---

## Step 6: Test Watch + Rebuild

```bash
# Build with watch
aurea build --watch &

# Modify a slide
echo "" >> slides/presentation.md
echo "---" >> slides/presentation.md
echo "## New Slide" >> slides/presentation.md
echo "Added at runtime" >> slides/presentation.md

# Expected stderr: Rebuilt in 0.XXs (watching...)
kill %1  # stop watch process
```

---

## Step 7: Extract a Theme (P3 — optional)

```bash
# Extract from a public URL
aurea extract https://linear.app --name linear-custom

# Expected stdout:
#   Extracted theme 'linear-custom' → .aurea/themes/linear-custom/
#   Colors extracted: 8, Fonts detected: 2, Mood: minimal, modern

# Verify extracted files
ls .aurea/themes/linear-custom/
# Expected: DESIGN.md  layout.css  meta.json  theme.css

# Use extracted theme
aurea theme use linear-custom
aurea build
# Expected: output/presentation.html with linear visual style
```

---

## Step 8: Test --force and Edge Cases

```bash
# Test init in existing directory (without --force)
cd ..
aurea init my-demo
# Expected exit 1: Error: directory 'my-demo' already exists. Use --force to overwrite.

# Test with --force (should NOT overwrite slides/)
touch my-demo/slides/important.md
aurea init my-demo --force
ls my-demo/slides/important.md
# Expected: file still exists (slides/ preserved)

# Test unknown theme
cd my-demo
aurea theme use nonexistent-theme
# Expected exit 1: Error: theme 'nonexistent-theme' not found. Try 'aurea theme search nonexistent-theme'

# Test port conflict (if you have another server on 8000)
aurea serve --port 8000
# Expected stderr: Port 8000 in use, trying 8001...
# Expected stdout: Serving at http://127.0.0.1:8001 — press Ctrl+C to stop
```

---

## Step 9: Different Agent Formats

```bash
cd ..

# Test Gemini format
aurea init gemini-demo --agent gemini --theme default
ls gemini-demo/.gemini/commands/
# Expected: aurea.outline.toml  aurea.generate.toml  ... (7 .toml files)
grep "{{args}}" gemini-demo/.gemini/commands/aurea.outline.toml
# Expected: at least one match (Gemini placeholder)

# Test language fallback
aurea init lang-demo --agent claude --lang pt-br
# Expected stderr: Language 'pt-br' not available, using 'en'
# (or if pt-br templates exist: no warning, Portuguese templates)
```

---

## Step 10: Theme Create

```bash
cd my-demo

aurea theme create my-brand
ls .aurea/themes/my-brand/
# Expected: DESIGN.md  layout.css  meta.json  theme.css

head -5 .aurea/themes/my-brand/DESIGN.md
# Expected: 9-section scaffold with guide comments

aurea theme use my-brand
aurea build
# Expected: builds successfully with blank/default theme
```

---

## Validation Checklist

After completing all steps:

- [ ] `aurea init` creates complete project structure in <2 seconds
- [ ] `aurea theme list` shows 36+ themes
- [ ] `aurea theme search "dark"` returns results in <500ms
- [ ] `aurea build` produces HTML with zero external resource references
- [ ] HTML opens correctly offline in Chrome and Firefox
- [ ] `aurea serve` starts in <1 second
- [ ] `--watch` mode triggers rebuild on file changes
- [ ] Gemini init produces `.toml` files in `.gemini/commands/`
- [ ] `--force` preserves `slides/` directory content
- [ ] Error messages are clear and actionable

---

## Four-Mode Validation (before release)

```bash
# Mode 2: zipapp
python aurea.pyz --version
python aurea.pyz init pyz-test --agent claude

# Mode 3: PyInstaller exe (Windows)
.\aurea.exe --version
.\aurea.exe init exe-test --agent claude

# Mode 4: pip (done above)
# Mode 1 (zero-install): manually copy .claude/commands/ from any project
#   to a clean directory and verify /aurea.outline works in Claude Code
```
