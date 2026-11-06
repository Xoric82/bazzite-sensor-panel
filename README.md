# Bazzite Sensor Panel

A full-screen hardware monitor for a small secondary display (a 1280×400 HDMI "sensor panel") on Bazzite / KDE Plasma 6 (Wayland).

It shows:

- **CPU**: average clock speed (with peak core) and Tctl temperature (`k10temp`)
- **GPU**: shader clock speed (with load %) and edge temperature (with junction hotspot). It picks the discrete amdgpu card over the iGPU automatically.
- **RAM**: used / total and percentage
- **Now playing**: album art, title, artist, album and progress for anything publishing MPRIS (YouTube Music in Chrome/Firefox, AudioTube, etc.). It appears automatically while music plays.

The layout adapts to landscape or portrait. When music plays, the sensors shrink into a compact column.

## How it works

| Piece | Path in repo | Installed to |
|---|---|---|
| Sensor + MPRIS server (Python stdlib only, `127.0.0.1:8765`) | `panel/server.py` | `~/.local/share/sensor-panel/` |
| Panel page (polls `/api` every second) | `panel/panel.html` | `~/.local/share/sensor-panel/` |
| Theme stylesheets (`synthwave`, `cyber`, `classic`) and bundled fonts | `panel/themes/` | `~/.local/share/sensor-panel/themes/` |
| Launcher (starts server, opens a dedicated Chrome app window) | `panel/launch.sh` | `~/.local/share/sensor-panel/` |
| KWin window rule (pins the window over the panel, never takes focus) | `kwin/sensorpanel.kwinrule` | `~/.config/kwinrulesrc` |
| KWin script: make the main monitor active at login and move stray windows off the panel for 2 min | `kwin/primary-screen-at-login/` | `~/.local/share/kwin/scripts/` |
| Game Mode: prefer DP outputs so gamescope never switches to the panel | `gamescope/gamescope-session-plus.conf` | `~/.config/environment.d/` |

`install.sh` also adds a **Sensor Panel** entry to the app menu and to autostart.

Notes:

- **Album art from Flatpak browsers:** these report art as `file:///tmp/...` inside their sandbox. The server resolves it via `/run/user/<uid>/.flatpak/<app>/tmp/`.
- **Window matching:** Flatpak Chrome gives every window the class `com.google.Chrome`, so the KWin rule and script recognise the panel by its title `SensorPanel` (the `<title>` in `panel.html`). Keep the two in sync.
- **Watchdog:** if the panel page stops polling for 60 s (e.g. Chrome's renderer died) while the panel window is still open, the server restarts it.
- **Health check:** `curl -s http://127.0.0.1:8765/health` reports how long ago the panel last polled.
- **Game Mode:** gamescope only drives one output, so the panel is blank there. It works in Desktop Mode.

## Requirements

- Bazzite (or another KDE Plasma 6 Wayland desktop) with `python3`, `curl`, `busctl`, `kwriteconfig6`
- Google Chrome Flatpak (`com.google.Chrome`)
- AMD CPU/GPU sensors (`k10temp`, `amdgpu`); `coretemp` is used as a CPU fallback

## Install

```bash
./install.sh
~/.local/share/sensor-panel/launch.sh
```

## Themes

The panel ships with three looks, which share the same markup and script:

- **`synthwave`** (default): "Nightdrive", a sleek neon purple and blue dashboard on an 80s horizon grid. See [DESIGN-synthwave.md](DESIGN-synthwave.md). Its fonts (Oxanium, Michroma; SIL OFL) are bundled in `panel/themes/fonts/`.
- **`cyber`**: the "Cyberpunk Bazzite" design in [DESIGN.md](DESIGN.md).
- **`classic`**: the original blue/red/purple cards. `panel/themes/classic.css` is the original stylesheet, unchanged.

To switch, write the theme name to `~/.config/sensor-panel/theme`, close the panel window, and start it again:

```bash
mkdir -p ~/.config/sensor-panel && echo cyber > ~/.config/sensor-panel/theme
~/.local/share/sensor-panel/launch.sh
```

Delete that file (or write `synthwave`) to go back to the default. `SENSOR_PANEL_THEME=classic` works too for a one-off launch. The git tag `classic-design` marks the last commit before themes existed.

## Adapting to your setup

These values are specific to the original machine (3440×1440 main monitor on `DP-2`, panel on `HDMI-A-1` rotated to 1280×400 and placed to its right):

- `kwin/sensorpanel.kwinrule`: `position` / `size` must match the panel's place in System Settings → Display & Monitor
- `kwin/primary-screen-at-login/contents/code/main.js`: `PRIMARY` connector name
- `gamescope/gamescope-session-plus.conf`: output preference order

Find connector names with:

```bash
for p in /sys/class/drm/card*-*; do echo "$(basename $p) $(cat $p/status)"; done
```

## Uninstall

```bash
rm -rf ~/.local/share/sensor-panel ~/.local/share/kwin/scripts/primary-screen-at-login
rm ~/.local/share/applications/sensor-panel.desktop ~/.config/autostart/sensor-panel.desktop ~/.config/environment.d/gamescope-session-plus.conf
```

Then remove the "Sensor Panel on secondary display" rule in System Settings → Window Management → Window Rules.
