#!/usr/bin/env bash
# Starts the sensor server (if needed) and opens the panel in a dedicated Chrome app window.
# A KWin rule (class com.google.Chrome, title SensorPanel) pins it borderless over HDMI-A-1 at 3440,0 1280x400.
DIR="$(dirname "$(readlink -f "$0")")"
PORT="${SENSOR_PANEL_PORT:-8765}"
PROFILE="$HOME/.var/app/com.google.Chrome/data/sensor-panel"

if ! curl -s -o /dev/null "http://127.0.0.1:$PORT/api"; then
  nohup python3 "$DIR/server.py" >/dev/null 2>&1 &
  for _ in $(seq 20); do curl -s -o /dev/null "http://127.0.0.1:$PORT/api" && break; sleep 0.25; done
fi

# Each flatpak launch gets a private /tmp, so Chrome's single-instance check can't see an existing panel.
pgrep -f -- "--user-data-dir=$PROFILE" >/dev/null && exit 0

exec flatpak run com.google.Chrome \
  --user-data-dir="$PROFILE" \
  --app="http://127.0.0.1:$PORT/" \
  --no-first-run --noerrdialogs --disable-translate --disable-features=Translate \
  --password-store=basic --hide-crash-restore-bubble \
  --disable-background-timer-throttling --disable-renderer-backgrounding --disable-backgrounding-occluded-windows
