# Bazzite Sensor Panel

See README.md for what the project does and how it is installed.

## Design

The default theme is **synthwave** ("Nightdrive"): all visual changes to the default panel follow [DESIGN-synthwave.md](DESIGN-synthwave.md). Treat it as the rulebook: its palette and tokens, Oxanium + Michroma (bundled), the single `--tube` glow recipe, one continuous animation, and no costume (gradient text, chrome, suns, scanlines).

How it applies here:

- Styling lives in `panel/themes/`. `synthwave.css` is the default. `cyber.css` follows [DESIGN.md](DESIGN.md) (Cyberpunk Bazzite) and `classic.css` is the original look: don't restyle those two when working on synthwave. All three style the same markup in `panel.html`, so markup changes must work in all of them. A theme must define the variables the markup and script use: `--cpu`, `--gpu` and `--ram` (each card sets `--accent` from one of them) and `--ok`, `--warm` and `--hot` (bar states; the script also sets each bar's current colour as `--fill`).
- The panel is plain HTML/CSS with no build step, no Tailwind and no component library. Use CSS custom properties on `:root`.
- The panel is a display, not an app: the window never takes focus, so hover, focus and button states don't apply.
- It must work at 1280×400 landscape and 800×1200 portrait, viewed from a distance. Keep sizes in viewport units (`vmin`) and keep the numbers readable over decorative detail. Check both orientations, with and without music, with a long song title and with missing album art.
- Fonts must be bundled locally in `panel/themes/fonts/` (served at `/themes/fonts/<name>.woff2`). Never use a CDN.
- Keep the page `<title>` as `SensorPanel`: the KWin rule and login script find the window by that title.
