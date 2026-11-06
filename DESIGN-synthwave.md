# Design System: Nightdrive (Synthwave)

The default panel theme, in `panel/themes/synthwave.css`. Sleek and modern first, 80s neon second: a precise instrument cluster set against a night-drive horizon. The 80s lives in the light (neon tubes, the horizon, the grid floor). It does not live in the type or the layout, which stay clean and current.

Treat this as a rulebook. If a change doesn't fit, change this file first, on purpose.

## The scene

- **Sky:** vertical gradient from `--void` at the top through `--night` and `--dusk` to `--horizon` at the horizon line, then straight back to `--void` below it. A soft violet bloom sits on the horizon.
- **Horizon line:** 2px, magenta to pale pink to magenta, fading out at both ends.
- **Grid floor:** violet horizontal lines and blue vertical lines, tilted back with `perspective()` + `rotateX()` and masked so they fade near the horizon and at the bottom. Opacity stays around 0.55. It's backdrop, never content.
- The horizon sits at 64% of the height in landscape and 72% in portrait (`--horizon-y`).
- Panes are 90–94% opaque, so the scene only shows through the gutters and faintly behind the panes. Numbers always sit on a calm, dark surface.

## Palette

| Token | Hex | Use |
|---|---|---|
| `--void` | `#05031a` | Page base, below the horizon |
| `--night` | `#0b0726` | Upper sky, empty album art |
| `--dusk` | `#1a0c46` | Sky near the horizon |
| `--horizon` | `#3a1478` | Horizon band |
| `--neon-blue` | `#3aa0ff` | CPU accent, artist name |
| `--neon-violet` | `#a65cff` | GPU accent, music glow |
| `--neon-magenta` | `#ff4fd8` | RAM accent, horizon, "warm" state |
| `--neon-cyan` | `#2ee6ff` | "OK" temperature state, now-playing line |
| `--neon-red` | `#ff3d6e` | "Hot" state only |
| `--ink` | `#f4f1ff` | Values, song title |
| `--ink-2` | `#aea7dc` | Labels, sub-text, album, times |
| `--ink-3` | `#6d66a8` | Rarely: lowest-priority detail |
| `--rule` | `rgba(166,140,255,.16)` | Pane borders and divider lines |

Ink is tinted lavender. Never use neutral grey on this background. Red appears only when something is actually hot.

The markup and script need `--cpu`, `--gpu`, `--ram`, `--ok`, `--warm` and `--hot`. Keep them mapped to the tokens above.

## Type

Both faces are bundled in `panel/themes/fonts/` (SIL OFL) and served by `server.py` at `/themes/fonts/<name>.woff2`. Never load fonts from a CDN.

- **Oxanium** (variable, 200–800): values, units, song, artist, album, sub-text. Its digits are fixed-width, so numbers don't jitter as they update every second.
  - Values: 700, tracking -0.02em, white with a soft accent glow.
  - Units: 200, in the accent colour. Pairing 700 with 200 is the main hierarchy move.
- **Michroma** (wide): pane titles, metric labels and the now-playing line only. Always uppercase with 0.24–0.32em tracking, and always small. Never use it for numbers or long text.
- Don't introduce Inter, Roboto, Arial or a monospace font for "tech" flavour.

## Light (glow)

- One glow recipe, `--tube`: a tight core (`0 0 .5vmin`, 90%) plus a bloom (`0 0 2.2vmin`, 45%) in the element's own colour (`--c`). Use it for neon lines, dots and bar fills.
- Text glows use `text-shadow` at low strength. Values get a faint white core and an accent bloom.
- Never use large, offset grey drop shadows. Album art is the one exception: it gets coloured offset glows (violet below, blue above), as if lit by the scene.

## Components

- **Pane (`.card`):** radius `0.9vmin`, a 1px `--rule` border, a dark vertical gradient, and an accent wash in the top-left corner. Its top edge is a 1px lit line in the accent that fades at both ends. No corner brackets and no thick coloured side borders.
- **Title:** glowing dot, wide-set name, then a hairline running to the right edge.
- **Gauge (`.bar` / `.fill`):** a 1.1vmin rounded glass track. The fill runs from transparent to the accent, ends in a hot white tip, and glows with `--tube`. When the script sets a state colour (temperature, RAM load), the fill turns that solid colour.
- **Now playing:** a blurred album-art backdrop washed into the night palette, art with scene-lit glows, and a cyan player line with a small animated equaliser. The song title is Oxanium 700 (two lines max), the artist is neon blue, and the album is `--ink-2` at weight 300. The progress tube runs blue to violet to magenta.

## Layout

- **Landscape (1280×400):** three panes side by side. While music plays, music takes 2fr and the sensors become a 1fr column of compact panes with vertical titles.
- **Portrait (800×1200):** three stacked panes, each with its two readings side by side under the title. While music plays, music sits on top (1.25fr) with centred art, and the sensors stack below it as compact panes.
- Use viewport units (`vmin`) for every size. The gutter is `--gap: 1.4vmin`.

## Motion

- The equaliser beside "Now playing" is the only continuous animation.
- The music view arrives with a 0.5s fade and un-blur (expo ease-out).
- Bar widths ease over 0.4s (expo ease-out). The progress bar is linear over 1s, matching the poll rate.
- Respect `prefers-reduced-motion`.
- Nothing moves on the idle sensor view apart from the data itself.

## Don't

- Gradient text, chrome lettering, striped "sunset" suns, or palm trees. That's costume, not sleek.
- Scanlines or noise overlays on top of the numbers.
- Extra colours outside the palette, or pink and red used for anything other than RAM, warm and hot.
- Hover, focus or button states. The window never takes focus.
- Changing the `<title>` from `SensorPanel`.
