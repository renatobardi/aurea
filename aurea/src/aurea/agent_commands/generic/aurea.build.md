---
name: aurea.build
description: Build a standalone HTML presentation from slides (works without CLI)
---

# aurea.build — Standalone HTML Build

You are generating a single, self-contained HTML file from the Markdown slides. The output must work offline, in any browser, with zero external dependencies. **This command includes a full fallback for Mode 1 (no CLI installed).**

## Step 1 — Try the CLI first

Check whether the `aurea` CLI is available:

```bash
aurea --version
```

If the CLI is available and returns a version number, run:

```bash
aurea build --output {{OUTPUT_DIR}}/presentation.html
```

If this succeeds, skip to Step 6 (verification). If the CLI is not available or returns an error, proceed with the manual build below.

## Step 2 — Read all source files

Read these files:

1. `{{CONFIG_PATH}}` — project settings: theme, author, output directory.
2. `{{DESIGN_MD_PATH}}` — active theme design system.
3. `{{THEME_CSS_PATH}}` — theme CSS.
4. `{{THEME_CSS_PATH}}/../layout.css` — layout utilities (if exists).
5. `{{SLIDES_DIR}}/presentation.md` — the full Markdown presentation.

## Step 3 — Parse the Markdown presentation

Parse `presentation.md`:

1. **Extract YAML frontmatter** (between opening `---` and closing `---`): title, author, theme, date.
2. **Split slides** on `---` separators (three dashes on a blank line). Each block between separators is one slide.
3. **Parse each slide**:
   - Extract `<!-- .slide: ... -->` attribute comment (if present) for CSS classes and data attributes.
   - Extract `Note:` section (everything after `Note:` on its own line) as speaker notes.
   - The remaining content is the slide body — convert Markdown to HTML.
4. **Markdown-to-HTML conversion**: convert headings, paragraphs, lists, bold, italic, code blocks, and inline code. You may do this with a simple regex-based approach or describe the transformations explicitly.

## Step 4 — Assemble the standalone HTML

Construct the full HTML file. The output **MUST NOT** contain any `<link href="https://...">` or `<script src="https://...">` — all CSS and JS must be inlined.

Use this structure:

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{ frontmatter.title }}</title>
  <meta name="author" content="{{ frontmatter.author }}">

  <style>
    /* ============================================================
       REVEAL.JS CORE CSS — inlined (vendor from aurea distribution)
       ============================================================ */
    /* Paste the full contents of reveal.js/dist/reveal.css here */

    /* ============================================================
       THEME CSS — inlined from theme.css
       ============================================================ */
    /* Contents of {{THEME_CSS_PATH}} */

    /* ============================================================
       LAYOUT CSS — inlined from layout.css
       ============================================================ */
    /* Contents of layout.css */
  </style>
</head>
<body>

<div class="reveal">
  <div class="slides">

    <!-- SLIDE 1 -->
    <section {{ slide_1_attributes }}>
      {{ slide_1_html }}
      <aside class="notes">{{ slide_1_notes }}</aside>
    </section>

    <!-- SLIDE N -->
    <!-- ... repeat for each slide ... -->

  </div>
</div>

<script>
  /* ============================================================
     REVEAL.JS CORE JS — inlined (vendor from aurea distribution)
     ============================================================ */
  /* Paste the full contents of reveal.js/dist/reveal.js here */
</script>

<script>
  Reveal.initialize({
    hash: true,
    slideNumber: true,
    transition: 'slide',
    backgroundTransition: 'fade',
    plugins: []
  });
</script>

</body>
</html>
```

### Inlining reveal.js

**If the aurea vendor files are accessible** at `{{SLIDES_DIR}}/../../vendor/revealjs/`:
- Read `vendor/revealjs/dist/reveal.css` → inline into `<style>`.
- Read `vendor/revealjs/dist/reveal.js` → inline into `<script>`.

**If vendor files are NOT accessible** (pure Mode 1 fallback), include a minimal reveal.js-compatible CSS reset and navigation JavaScript. Write the following minimal implementation:

```html
<style>
/* Minimal presentation CSS — no external dependencies */
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { width: 100%; height: 100%; overflow: hidden; background: var(--r-background-color, #1a1a2e); }
.reveal { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; }
.reveal .slides { width: 960px; height: 700px; position: relative; }
.reveal section { display: none; padding: 40px; position: absolute; inset: 0; flex-direction: column; justify-content: center; }
.reveal section.present { display: flex; }
.reveal h1 { font-size: 2.5em; margin-bottom: 0.5em; }
.reveal h2 { font-size: 1.8em; margin-bottom: 0.4em; }
.reveal p, .reveal li { font-size: 1.1em; line-height: 1.6; }
.reveal ul { padding-left: 1.5em; }
.reveal aside.notes { display: none; }
.progress { position: fixed; bottom: 0; left: 0; height: 3px; background: var(--aurea-accent, #4f8ef7); transition: width 0.3s; }
.controls { position: fixed; bottom: 20px; right: 20px; display: flex; gap: 8px; }
.controls button { background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); color: #fff; padding: 8px 16px; border-radius: 4px; cursor: pointer; font-size: 14px; }
.controls button:hover { background: rgba(255,255,255,0.2); }
.slide-counter { position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%); color: rgba(255,255,255,0.4); font-size: 13px; font-family: sans-serif; }
</style>
```

```html
<script>
// Minimal presentation engine — no dependencies
(function() {
  var slides = document.querySelectorAll('.reveal section');
  var current = 0;
  var counter = document.querySelector('.slide-counter');
  var progress = document.querySelector('.progress');

  function show(n) {
    slides[current].classList.remove('present');
    current = Math.max(0, Math.min(n, slides.length - 1));
    slides[current].classList.add('present');
    if (counter) counter.textContent = (current + 1) + ' / ' + slides.length;
    if (progress) progress.style.width = ((current + 1) / slides.length * 100) + '%';
    history.replaceState(null, '', '#/' + current);
  }

  document.addEventListener('keydown', function(e) {
    if (e.key === 'ArrowRight' || e.key === 'ArrowDown' || e.key === ' ') show(current + 1);
    if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') show(current - 1);
    if (e.key === 'Home') show(0);
    if (e.key === 'End') show(slides.length - 1);
  });

  document.querySelector('.btn-next').addEventListener('click', function() { show(current + 1); });
  document.querySelector('.btn-prev').addEventListener('click', function() { show(current - 1); });

  // Touch swipe
  var touchStartX = 0;
  document.addEventListener('touchstart', function(e) { touchStartX = e.touches[0].clientX; });
  document.addEventListener('touchend', function(e) {
    var dx = e.changedTouches[0].clientX - touchStartX;
    if (Math.abs(dx) > 50) show(dx < 0 ? current + 1 : current - 1);
  });

  // Start
  var hash = parseInt(window.location.hash.replace('#/', '')) || 0;
  show(hash);
})();
</script>
```

Add to the body, after the slides div:
```html
<div class="progress"></div>
<div class="slide-counter"></div>
<div class="controls">
  <button class="btn-prev">←</button>
  <button class="btn-next">→</button>
</div>
```

## Step 5 — Write the output file

Write the assembled HTML to `{{OUTPUT_DIR}}/presentation.html`.

Ensure:
- [ ] No `<link href="https://...">` anywhere in the file.
- [ ] No `<script src="https://...">` anywhere in the file.
- [ ] No `@import url('https://...')` in any `<style>` block.
- [ ] The file opens correctly when double-clicked (no server required).
- [ ] All slides are present as `<section>` elements.
- [ ] Speaker notes are in `<aside class="notes">` tags.

## Step 6 — Verify and report

```
Build complete.

Output: {{OUTPUT_DIR}}/presentation.html
File size: ~X KB
Slides: N
Offline: ✓ (all resources inlined)
Build mode: CLI / vendor inline / minimal fallback

Open the file in your browser to preview:
  macOS: open {{OUTPUT_DIR}}/presentation.html
  Windows: start {{OUTPUT_DIR}}/presentation.html
  Linux: xdg-open {{OUTPUT_DIR}}/presentation.html
```

If any slides failed to render, list them with the error reason.

## Principles

- **The output HTML MUST NOT contain any `<link href='https://...'>` or `<script src='https://...'>` — all CSS and JS must be inlined.** This is the non-negotiable constraint of Aurea's offline-first design.
- **Graceful degradation**: CLI → vendor files → minimal fallback. Each level produces a working presentation.
- **Speaker notes are preserved**: even in the minimal fallback, `<aside class="notes">` tags must be present for presenter tools.
- **File size target**: aim for <5 MB for the standalone HTML. Warn the user if it exceeds this.
