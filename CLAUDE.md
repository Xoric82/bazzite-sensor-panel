# Bazzite Sensor Panel

See README.md for what the project does and how it is installed.

## Design

All visual changes to the panel follow [DESIGN.md](DESIGN.md) (Cyberpunk Bazzite: neon purple / dark cyber). Treat it as the rulebook: use only its palette, monospace type, sharp corners (max 4px radius), tight neon glows instead of soft shadows, and a dense grid layout.

How it applies here:

- Styling lives in `panel/themes/`. The design goes in `cyber.css`, the default. `classic.css` is the original look kept for restoring: don't edit it. Both stylesheets style the same markup in `panel.html`, so markup changes must work in both. A theme must define the variables the markup and script use: `--cpu`, `--gpu` and `--ram` (each card sets `--accent` from one of them) and `--ok`, `--warm` and `--hot` (bar states; the script also sets each bar's current colour as `--fill`).
- The panel is plain HTML/CSS with no build step and no Tailwind. Use DESIGN.md's colors as CSS custom properties on `:root` with the same names (`--bg-main`, `--neon-purple`, and so on). Treat the Tailwind section as a reference for the look, not as code to paste.
- The panel is a display, not an app: the window never takes focus, so hover, focus and button states don't apply.
- It runs on a 1280×400 screen viewed from a distance, and the layout also has to work in portrait. Keep sizes in viewport units and keep the numbers readable over decorative detail.
- Fonts must already be installed or bundled locally. The panel runs from `127.0.0.1`, and fetching fonts from a CDN at startup isn't reliable. Fira Code ships with Bazzite; JetBrains Mono isn't installed, so use the stack `"JetBrains Mono", "Fira Code", ui-monospace, monospace`.
- Keep the page `<title>` as `SensorPanel`: the KWin rule and login script find the window by that title.
