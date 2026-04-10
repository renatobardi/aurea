# Aurea v0.1.0 — Deployment & Distribution Guide

## Overview

Aurea supports **4 independent distribution modes**, each self-contained and fully functional. No mode is "limited"—they differ only in convenience.

| Mode | Format | Size | Setup | Use Case |
|------|--------|------|-------|----------|
| **Zero-Install** | Markdown templates | ~500 KB | Copy & paste | No CLI, no Python, agent commands only |
| **Zipapp** | Single .pyz file | ~20 MB | `python aurea.pyz` | Developers, quick test |
| **PyInstaller** | Standalone binary | ~40 MB | `./aurea` (no Python needed) | Windows corporate (SCCM/Intune) |
| **pip/uv/pipx** | Wheel + source | ~5 MB core | `pip install aurea` | CI/CD, standard dev workflow |

---

## Mode 1: Zero-Install (Copy & Paste)

**Perfect for:** Completely locked-down Windows machines, air-gap environments, users who only use AI agents.

### Setup
```bash
# Clone repo or download ZIP
git clone https://github.com/renatobardi/aurea.git
cd aurea

# Copy agent command templates to your AI agent:
cp -r src/aurea/agent_commands/claude/ ~/.claude/commands/aurea.*
# (or wherever your agent's commands directory is)
```

### Usage
1. In your AI agent, run: `/aurea.init "my-presentation" --agent claude --theme stripe`
2. Follow the workflow: `/aurea.outline` → `/aurea.generate` → `/aurea.refine` → `/aurea.visual` → `/aurea.build`
3. Open `output/presentation.html` in your browser

**Pros:**
- ✅ Zero dependencies, zero installation
- ✅ Works in completely locked-down environments
- ✅ All templates work independently

**Cons:**
- ❌ No CLI automation (requires agent prompts)
- ❌ Theme management is manual

---

## Mode 2: Zipapp (.pyz)

**Perfect for:** Quick prototyping, laptops, testing environments.

### Download
```bash
# Download from GitHub releases
curl -L https://github.com/renatobardi/aurea/releases/latest/download/aurea.pyz -o aurea.pyz

# Or build locally
python -m pip install shiv
shiv -c aurea -o aurea.pyz -e aurea.cli:app .
```

### Usage
```bash
# Initialize project
python aurea.pyz init my-talk --agent claude --theme stripe

cd my-talk

# Use in agent or CLI
aurea build
aurea serve --watch
aurea theme use linear
```

**Pros:**
- ✅ Single file, no installation needed
- ✅ Works on Python 3.8+
- ✅ All dependencies vendored

**Cons:**
- ❌ Requires Python in PATH
- ❌ Larger file size (~20 MB)

---

## Mode 3: PyInstaller Standalone Executable

**Perfect for:** Corporate Windows deployments (SCCM, Intune), no Python available.

### Download from Releases
```powershell
# Windows
curl -O https://github.com/renatobardi/aurea/releases/latest/download/aurea.exe

# macOS (Intel)
curl -O https://github.com/renatobardi/aurea/releases/latest/download/aurea.app.zip
unzip aurea.app.zip
./aurea.app/Contents/MacOS/aurea --help

# macOS (Apple Silicon)
# (Same as above, built on Apple Silicon)

# Linux
curl -O https://github.com/renatobardi/aurea/releases/latest/download/aurea
chmod +x aurea
./aurea --help
```

### Usage
```bash
# Windows
aurea.exe init my-talk --agent claude --theme stripe

# macOS/Linux
./aurea init my-talk --agent claude --theme stripe

# Identical behavior to all other modes
aurea build
aurea serve --watch
aurea theme list
aurea extract https://linear.app --name linear-custom
```

**Pros:**
- ✅ Zero Python required
- ✅ Can be deployed via SCCM, Intune, Artifactory
- ✅ Works on Windows 7+, macOS 10.13+, Linux glibc 2.17+

**Cons:**
- ❌ Larger file size (~40 MB)
- ❌ First run may trigger security warnings (sign the binary for production)

### Deployment via SCCM (Example)
```powershell
# Create package in SCCM
# Source: aurea.exe
# Installation command: aurea.exe --version
# Detection rule: Registry check for aurea version

# Users run:
aurea init my-presentation --agent claude --theme stripe
```

---

## Mode 4: pip / uv / pipx

**Perfect for:** Developers, CI/CD, traditional Python environments.

### Installation

**pip (standard)**
```bash
pip install aurea
# Optional extras for theme extraction
pip install aurea[extract]
```

**uv (faster, same interface)**
```bash
uv tool install aurea
uv tool run aurea --version
```

**pipx (isolated in PATH)**
```bash
pipx install aurea
aurea --version
```

### Usage
```bash
# Standard CLI
aurea init my-talk --agent claude --theme stripe
cd my-talk

aurea build
aurea serve --watch

# In GitHub Actions
- name: Build presentation
  run: pip install aurea && aurea build --theme stripe

# In CI/CD pipelines
aurea build --minify --embed-fonts --output dist/presentation.html
```

**Pros:**
- ✅ Standard Python package management
- ✅ Easy integration with CI/CD
- ✅ Supports `pip`, `uv`, `pipx`
- ✅ Optional extras (extract) available

**Cons:**
- ❌ Requires Python 3.8+ in environment

---

## Choosing Your Mode

### Corporate Windows (No Python, No Internet Access)
→ **Mode 3: PyInstaller Executable**
- Deploy via SCCM/Intune
- Works completely offline
- No Python required

### Developer Laptop (Quick Testing)
→ **Mode 2: Zipapp** or **Mode 4: pip**
- Mode 2: Single file, no installation
- Mode 4: Standard pip workflow

### Locked-Down Machine (No CLI Allowed)
→ **Mode 1: Zero-Install**
- Copy templates to your agent
- Use agent commands only
- No CLI needed

### CI/CD Pipeline (GitHub Actions, etc.)
→ **Mode 4: pip**
```yaml
- run: pip install aurea
- run: aurea build --minify
```

### Air-Gap / Offline Network
→ **Mode 1 (Zero-Install) + offline agents** or **Mode 3 (Standalone EXE)**
- Pre-download everything
- No internet required after initial setup

---

## Version Management

All modes ship the same version:
```bash
aurea --version
# 0.1.0
```

To upgrade:
- **Mode 1**: Re-copy templates from latest release
- **Mode 2**: Re-download .pyz file
- **Mode 3**: Re-download executable
- **Mode 4**: `pip install --upgrade aurea`

---

## Output Guarantee

**All 4 modes produce identical HTML output.** For example:

```bash
# Mode 1: Agent command /aurea.build
# Mode 2: python aurea.pyz build
# Mode 3: ./aurea build
# Mode 4: aurea build

# All produce: output/presentation.html (same bytes, same reveal.js version)
```

---

## Troubleshooting

### Mode 2 (Zipapp): "Python not found"
```bash
# Use full path or virtual environment
/usr/bin/python3 aurea.pyz init ...
python3.12 aurea.pyz init ...
```

### Mode 3 (PyInstaller): "Cannot execute binary"
- **Windows**: May need VC Redistributables (download from Microsoft)
- **macOS**: May need `xcode-select --install` for code signing
- **Linux**: May need glibc 2.17+ or GLIBC_2.29

### All Modes: Theme not found
```bash
# Update theme list
aurea theme list
aurea theme search dark

# Or use default theme
aurea build --theme default
```

---

## Release Artifacts

GitHub releases include:

| File | Size | Python | Use |
|------|------|--------|-----|
| `aurea-0.1.0-py3-none-any.whl` | 5 MB | 3.8+ | pip install |
| `aurea.pyz` | 20 MB | 3.8+ | Single file |
| `aurea.exe` | 40 MB | None | Windows no Python |
| `aurea` | 40 MB | None | Linux/macOS |
| `aurea.app.zip` | 45 MB | None | macOS |
| `aurea-0.1.0.tar.gz` | 1 MB | 3.8+ | Source code |

---

## Security

### Code Signing (Production)
For corporate deployments, sign the PyInstaller binary:
```bash
# Using signtool (Windows)
signtool sign /f cert.pfx /p password aurea.exe

# Using codesign (macOS)
codesign -s - aurea
```

### Verified Hashes
All release artifacts include SHA-256 hashes. Verify before deployment:
```bash
sha256sum aurea.pyz
# [expected hash from release notes]
```

---

## Support & Documentation

- **Quick Start**: README.md
- **Full Spec**: aurea-spec.md
- **Architecture**: docs/architecture.md
- **Theme System**: docs/theme-system.md
- **Agent Commands**: docs/agent-commands.md
- **Issues**: https://github.com/renatobardi/aurea/issues

---

**Status**: Production-ready (v0.1.0)
**Last Updated**: 2026-04-09
