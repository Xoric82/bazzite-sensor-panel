#!/usr/bin/env python3
"""Tiny sensor server: serves panel.html, its theme stylesheets and a JSON endpoint read from sysfs/procfs."""
import glob, json, os, re, signal, subprocess, threading, time, urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
PORT = int(os.environ.get("SENSOR_PANEL_PORT", "8765"))


def read(path, default=None):
    try:
        with open(path) as f:
            return f.read().strip()
    except OSError:
        return default


def hwmon_by_name(name):
    return [h for h in glob.glob("/sys/class/hwmon/hwmon*") if read(f"{h}/name") == name]


def find_cpu_hwmon():
    found = hwmon_by_name("k10temp") or hwmon_by_name("coretemp")
    return found[0] if found else None


def find_dgpu_hwmon():
    # Pick the amdgpu with the most VRAM, so the discrete card wins over the iGPU.
    best, best_vram = None, -1
    for h in hwmon_by_name("amdgpu"):
        vram = int(read(f"{h}/device/mem_info_vram_total", "0"))
        if vram > best_vram:
            best, best_vram = h, vram
    return best


def labelled(hwmon, kind, label):
    for lp in glob.glob(f"{hwmon}/{kind}*_label"):
        if read(lp) == label:
            return read(lp.replace("_label", "_input"))
    return None


CPU_HW, GPU_HW = find_cpu_hwmon(), find_dgpu_hwmon()
CPU_MAX_MHZ = max(
    (int(read(p, "0")) for p in glob.glob("/sys/devices/system/cpu/cpu*/cpufreq/cpuinfo_max_freq")),
    default=0,
) / 1000


def sample():
    freqs = [int(read(p, "0")) / 1000 for p in glob.glob("/sys/devices/system/cpu/cpu*/cpufreq/scaling_cur_freq")]
    cpu_temp = None
    if CPU_HW:
        t = labelled(CPU_HW, "temp", "Tctl") or read(f"{CPU_HW}/temp1_input")
        cpu_temp = int(t) / 1000 if t else None

    gpu = {"freq": None, "freq_max": None, "temp": None, "hotspot": None, "load": None}
    if GPU_HW:
        f = labelled(GPU_HW, "freq", "sclk")
        gpu["freq"] = int(f) / 1e6 if f else None
        sclk = read(f"{GPU_HW}/device/pp_dpm_sclk", "")
        mhz = [int(l.split()[1].rstrip("Mhz")) for l in sclk.splitlines() if len(l.split()) > 1]
        gpu["freq_max"] = max(mhz) if mhz else None
        e, j = labelled(GPU_HW, "temp", "edge"), labelled(GPU_HW, "temp", "junction")
        gpu["temp"] = int(e) / 1000 if e else None
        gpu["hotspot"] = int(j) / 1000 if j else None
        b = read(f"{GPU_HW}/device/gpu_busy_percent")
        gpu["load"] = int(b) if b else None

    mem = {}
    for line in read("/proc/meminfo", "").splitlines():
        k, v = line.split(":", 1)
        mem[k] = int(v.split()[0])  # kB
    total, avail = mem.get("MemTotal", 0), mem.get("MemAvailable", 0)

    return {
        "cpu": {
            "freq": sum(freqs) / len(freqs) if freqs else None,
            "freq_peak": max(freqs) if freqs else None,
            "freq_max": CPU_MAX_MHZ or None,
            "temp": cpu_temp,
        },
        "gpu": gpu,
        "ram": {"used": (total - avail) / 1048576, "total": total / 1048576},
        "music": now_playing,
    }


# ---- Now playing (MPRIS over D-Bus, via busctl) -----------------------------------------------

MPRIS_PREFIX = "org.mpris.MediaPlayer2."
MPRIS_PATH, MPRIS_PLAYER = "/org/mpris/MediaPlayer2", "org.mpris.MediaPlayer2.Player"
# Prefer these players when several are playing at once (matched against the bus name).
PREFERRED = ("audiotube", "youtube", "music", "chromium", "chrome", "firefox", "plasma-browser-integration")
ART_DIRS = ("/tmp/", "/run/user/", os.path.expanduser("~/.var/app/"), os.path.expanduser("~/.cache/"))

now_playing = {"playing": False}
art_file = None  # local path of the current album art, when the player gave us a file:// URL


def busctl(*args):
    try:
        out = subprocess.run(["busctl", "--user", "--json=short", *args],
                             capture_output=True, text=True, timeout=2)
        return out.stdout if out.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def mpris_players():
    out = busctl("list", "--no-pager", "--acquired")
    names = [b["name"] for b in json.loads(out)] if out else []
    return [n for n in names if n.startswith(MPRIS_PREFIX)]


def unwrap(v):
    return v.get("data") if isinstance(v, dict) else v


def read_player(name):
    out = busctl("get-property", name, MPRIS_PATH, MPRIS_PLAYER, "PlaybackStatus", "Metadata", "Position")
    if not out:
        return None
    lines = out.strip().splitlines()
    if len(lines) < 2:
        return None
    status = unwrap(json.loads(lines[0]))
    meta = {k: unwrap(v) for k, v in (unwrap(json.loads(lines[1])) or {}).items()}
    position = unwrap(json.loads(lines[2])) if len(lines) > 2 else None
    artist = meta.get("xesam:artist") or []
    return {
        "player": name[len(MPRIS_PREFIX):],
        "status": status,
        "title": meta.get("xesam:title") or "",
        "artist": ", ".join(artist) if isinstance(artist, list) else str(artist),
        "album": meta.get("xesam:album") or "",
        "art_url": meta.get("mpris:artUrl") or "",
        "length": (meta.get("mpris:length") or 0) / 1e6,
        "position": (position or 0) / 1e6,
    }


def rank(p):
    name = p["player"].lower()
    pref = next((i for i, k in enumerate(PREFERRED) if k in name), len(PREFERRED))
    return (p["status"] != "Playing", pref)


def resolve_art(url):
    """Return (url for the page, local file path or None)."""
    global art_file
    if url.startswith("file://"):
        path = urllib.parse.unquote(urllib.parse.urlparse(url).path)
        if not os.path.isfile(path) and path.startswith("/tmp/"):
            # Flatpak apps (e.g. Chrome) have a private /tmp, exposed on the host under /run/user/<uid>/.flatpak/<app>/tmp
            found = glob.glob(f"/run/user/{os.getuid()}/.flatpak/*/tmp/{path[len('/tmp/'):]}")
            path = found[0] if found else path
        path = os.path.realpath(path)
        if path.startswith(ART_DIRS) and os.path.isfile(path):
            return f"/art?v={abs(hash((path, os.path.getmtime(path))))}", path
        return "", None
    if url.startswith(("http://", "https://")):
        return url, None
    return "", None


def poll_music():
    global now_playing, art_file
    while True:
        try:
            players = [p for p in map(read_player, mpris_players()) if p and p["title"]]
            best = min(players, key=rank) if players else None
            if best:
                art, art_file = resolve_art(best.pop("art_url"))
                best.update(art=art, playing=best["status"] == "Playing", t=time.time())
                now_playing = best
            else:
                now_playing, art_file = {"playing": False}, None
        except Exception:
            now_playing = {"playing": False}
        time.sleep(1)


# ---- Watchdog: restart the panel window if its page stops polling (e.g. Chrome's renderer died) ----

PROFILE = os.path.expanduser("~/.var/app/com.google.Chrome/data/sensor-panel")
STALL_SECS = 60
last_poll = 0.0  # time of the last /api request from the panel page


def panel_pids():
    out = subprocess.run(["pgrep", "-f", "--", f"--user-data-dir={PROFILE}"], capture_output=True, text=True)
    return [int(p) for p in out.stdout.split()]


def restart_panel():
    pids = panel_pids()
    for sig in (signal.SIGTERM, signal.SIGKILL):
        for pid in pids:
            try:
                os.kill(pid, sig)
            except ProcessLookupError:
                pass
        for _ in range(20):
            if not panel_pids():
                break
            time.sleep(0.25)
        pids = panel_pids()
        if not pids:
            break
    subprocess.Popen([os.path.join(HERE, "launch.sh")], start_new_session=True,
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def watchdog():
    global last_poll
    while True:
        time.sleep(10)
        # Only act if the panel has polled before (so we know it's meant to be running) and is still open.
        if last_poll and time.time() - last_poll > STALL_SECS and panel_pids():
            restart_panel()
            last_poll = time.time()  # give the new window time to load before checking again


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        global last_poll
        if self.path.startswith("/api"):
            if self.headers.get("X-Sensor-Panel"):
                last_poll = time.time()
            body, ctype = json.dumps(sample()).encode(), "application/json"
        elif self.path.startswith("/health"):
            age = round(time.time() - last_poll, 1) if last_poll else None
            body, ctype = json.dumps({"panel_last_poll_secs_ago": age, "panel_pids": panel_pids()}).encode(), "application/json"
        elif self.path.startswith("/art"):
            path = art_file
            if not path or not os.path.isfile(path):
                self.send_error(404)
                return
            with open(path, "rb") as f:
                body = f.read()
            ctype = ("image/png" if body[:4] == b"\x89PNG" else
                     "image/webp" if body[:4] == b"RIFF" and body[8:12] == b"WEBP" else
                     "image/gif" if body[:3] == b"GIF" else "image/jpeg")
        elif urllib.parse.urlsplit(self.path).path in ("/", "/index.html"):
            with open(os.path.join(HERE, "panel.html"), "rb") as f:
                body, ctype = f.read(), "text/html; charset=utf-8"
        elif m := re.fullmatch(r"/themes/([a-z0-9-]+)\.css", urllib.parse.urlsplit(self.path).path):
            path = os.path.join(HERE, "themes", m[1] + ".css")
            if not os.path.isfile(path):
                self.send_error(404)
                return
            with open(path, "rb") as f:
                body, ctype = f.read(), "text/css; charset=utf-8"
        elif m := re.fullmatch(r"/themes/fonts/([A-Za-z0-9-]+)\.woff2", urllib.parse.urlsplit(self.path).path):
            # Fonts bundled with the themes: the panel can't rely on a CDN at startup.
            path = os.path.join(HERE, "themes", "fonts", m[1] + ".woff2")
            if not os.path.isfile(path):
                self.send_error(404)
                return
            with open(path, "rb") as f:
                body, ctype = f.read(), "font/woff2"
        else:
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    threading.Thread(target=poll_music, daemon=True).start()
    threading.Thread(target=watchdog, daemon=True).start()
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
