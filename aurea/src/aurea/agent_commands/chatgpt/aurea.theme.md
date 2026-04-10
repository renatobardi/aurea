---
name: aurea.theme
description: Browse and select a presentation theme from the Aurea registry
---

# aurea.theme — Theme Selection

You are helping the user browse and select a presentation theme for their Aurea project.

## Step 1 — Read the theme registry

Read the file at `{{REGISTRY_PATH}}`. This is a JSON index of all available themes. Each entry contains:
- `id` — unique identifier
- `name` — display name
- `mood` — emotional tone (e.g., "professional", "playful", "minimal")
- `colors` — primary, secondary, accent, background, text
- `tags` — searchable keywords
- `description` — one-sentence summary

## Step 2 — Parse user criteria

The user's input is: `$ARGUMENTS`

Extract search intent from the input. Look for:
- **Mood descriptors**: words like "dark", "minimal", "bold", "warm", "corporate", "creative", "technical"
- **Color preferences**: specific hues or palettes mentioned
- **Brand/company inspiration**: "like Stripe", "like Apple", "like Linear"
- **Industry context**: "fintech", "startup", "medical", "education"
- **Tone**: "formal", "playful", "serious", "energetic"

If no criteria provided, ask: "What mood or visual style are you going for? (e.g., minimal, bold, corporate, creative)"

## Step 3 — Filter and rank themes

Score each theme in the registry against the extracted criteria:
- Exact tag match: +3 points
- Mood match: +2 points
- Color tone match (warm/cool/neutral): +1 point
- Description keyword match: +1 point

Select the **top 5 themes** by score.

## Step 4 — Present the options

Display the top 5 themes in a clear table or list. For each theme show:

```
Theme: <name> (<id>)
Mood: <mood>
Colors: ■ #RRGGBB (primary) · ■ #RRGGBB (accent) · ■ #RRGGBB (background)
Tags: <tag1>, <tag2>, <tag3>
Description: <one-sentence description>
```

After listing all 5, ask: "Which theme would you like to use? Enter the theme name or ID, or say 'show more' to see additional options."

## Step 5 — Apply the selected theme

Once the user confirms a theme ID:

1. Read `{{CONFIG_PATH}}` to find the current `themes_dir` value.
2. Locate the theme directory at `{{REGISTRY_PATH}}/../<theme-id>/`.
3. Copy the following files to the project's themes directory:
   - `DESIGN.md` → `{{CONFIG_PATH}}/../.aurea/themes/<theme-id>/DESIGN.md`
   - `theme.css` → `{{CONFIG_PATH}}/../.aurea/themes/<theme-id>/theme.css`
   - `layout.css` → `{{CONFIG_PATH}}/../.aurea/themes/<theme-id>/layout.css` (if exists)
   - `meta.json` → `{{CONFIG_PATH}}/../.aurea/themes/<theme-id>/meta.json`
4. Update `{{CONFIG_PATH}}` — set `"active_theme": "<theme-id>"`.
5. Confirm: "Theme **<name>** is now active. Run `aurea.generate` or `aurea.build` to use it."

## Principles

- Never apply a theme without explicit user confirmation.
- If the registry is missing or malformed, report the error clearly and suggest running `aurea theme list` from the CLI.
- Respect the user's creative vision — if they describe a very specific look, explain which theme comes closest and why.
