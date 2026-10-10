// Keep login on the main monitor: make PRIMARY the active screen when KWin starts, and for the first
// GRACE_MS move any normal window that opens on another screen (e.g. the HDMI sensor panel) over to PRIMARY.
const PRIMARY = "DP-2";
const GRACE_MS = 120000;
const IGNORE_CLASSES = ["chrome-127.0.0.1__-Default"];  // the sensor panel itself
const started = Date.now();

const inGrace = () => Date.now() - started < GRACE_MS;
const primary = () => workspace.screens.find(o => o.name === PRIMARY);

function focusPrimary() {
    if (!primary()) return;
    for (let i = 0; i < workspace.screens.length && workspace.activeScreen.name !== PRIMARY; i++)
        workspace.slotSwitchToNextScreen();
}

function rescue(w) {
    const p = primary();
    if (!inGrace() || !p || !w || !w.normalWindow || IGNORE_CLASSES.includes(String(w.resourceClass))) return;
    if (w.output && w.output.name !== PRIMARY) {
        workspace.sendClientToScreen(w, p);
        if (!w.fullScreen) {
            // Re-center: the panel's aspect ratio is so different that relative placement can land off-screen.
            const a = p.geometry, g = w.frameGeometry;
            const width = Math.min(g.width, a.width), height = Math.min(g.height, a.height);
            w.frameGeometry = { x: a.x + (a.width - width) / 2, y: a.y + (a.height - height) / 2, width, height };
        }
    }
    focusPrimary();
}

focusPrimary();
workspace.screensChanged.connect(() => { if (inGrace()) focusPrimary(); });
workspace.windowAdded.connect(rescue);
