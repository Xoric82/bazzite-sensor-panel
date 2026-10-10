#!/usr/bin/env bash
# Installs the sensor panel, its KWin window rule, the login screen-focus KWin script and the Game Mode output preference.
set -euo pipefail
SRC="$(cd "$(dirname "$0")" && pwd)"
APP="$HOME/.local/share/sensor-panel"
KWIN_SCRIPT="$HOME/.local/share/kwin/scripts/primary-screen-at-login"

echo "Installing panel to $APP"
mkdir -p "$APP"
install -m755 "$SRC/panel/server.py" "$SRC/panel/launch.sh" "$APP/"
install -m644 "$SRC/panel/panel.html" "$APP/"

echo "Adding app menu + autostart entries"
mkdir -p "$HOME/.local/share/applications" "$HOME/.config/autostart"
cat > "$HOME/.local/share/applications/sensor-panel.desktop" <<DESKTOP
[Desktop Entry]
Type=Application
Name=Sensor Panel
Comment=CPU/GPU/RAM sensor display for the secondary screen
Exec=$APP/launch.sh
Icon=utilities-system-monitor
Categories=System;Monitor;
DESKTOP
cp "$HOME/.local/share/applications/sensor-panel.desktop" "$HOME/.config/autostart/"

echo "Applying KWin window rule"
RULES="$HOME/.config/kwinrulesrc"
[ -f "$RULES" ] && cp "$RULES" "$RULES.bak-sensorpanel"
if ! grep -q '^\[sensorpanel\]' "$RULES" 2>/dev/null; then
  count=$(kreadconfig6 --file kwinrulesrc --group General --key count); count=${count:-0}
  rules=$(kreadconfig6 --file kwinrulesrc --group General --key rules)
  kwriteconfig6 --file kwinrulesrc --group General --key count $((count + 1))
  kwriteconfig6 --file kwinrulesrc --group General --key rules "${rules:+$rules,}sensorpanel"
fi
grep -v '^#' "$SRC/kwin/sensorpanel.kwinrule" | while IFS='=' read -r key value; do
  [ -n "$key" ] && kwriteconfig6 --file kwinrulesrc --group sensorpanel --key "$key" "$value"
done

echo "Installing KWin script primary-screen-at-login"
mkdir -p "$KWIN_SCRIPT"
cp -r "$SRC/kwin/primary-screen-at-login/." "$KWIN_SCRIPT/"
kwriteconfig6 --file kwinrc --group Plugins --key primary-screen-at-loginEnabled true

echo "Setting Game Mode preferred output"
mkdir -p "$HOME/.config/environment.d"
install -m644 "$SRC/gamescope/gamescope-session-plus.conf" "$HOME/.config/environment.d/"

busctl --user call org.kde.KWin /KWin org.kde.KWin reconfigure >/dev/null 2>&1 || true
echo "Done. Start it now with: $APP/launch.sh"
