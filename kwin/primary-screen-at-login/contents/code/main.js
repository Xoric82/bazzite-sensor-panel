// Keep login on the main monitor: make PRIMARY the active screen when KWin starts, and for the first
// GRACE_MS move any normal window that opens on another screen (e.g. the HDMI sensor panel) over to PRIMARY.
const PRIMARY = "DP-2";
const GRACE_MS = 120000;
// The sensor panel itself. Flatpak Chrome now uses the class com.google.Chrome for every window (it used to be
// chrome-127.0.0.1__-Default), so recognise the panel by its title, or by its URL before the page has set it.
const isPanel = w => w.resourceClass === "chrome-127.0.0.1__-Default" ||
    (w.resourceClass === "com.google.Chrome" && /^(SensorPanel$|127\.0\.0\.1:8765)/.test(String(w.caption)));
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
    if (!inGrace() || !p || !w || !w.normalWindow || isPanel(w)) return;
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

// Chrome only sets the "SensorPanel" title after KWin has already placed the window, so the rule's border/focus
// settings get applied but its position does not. Ask KWin to re-apply rules once the title is there.
function watchPanelTitle(w) {
    if (!w || w.resourceClass !== "com.google.Chrome") return;
    const onCaption = () => {
        if (w.caption !== "SensorPanel") return false;
        w.captionChanged.disconnect(onCaption);
        callDBus("org.kde.KWin", "/KWin", "org.kde.KWin", "reconfigure");
        return true;
    };
    w.captionChanged.connect(onCaption);
    onCaption();
}

focusPrimary();
workspace.screensChanged.connect(() => { if (inGrace()) focusPrimary(); });
workspace.windowAdded.connect(rescue);
workspace.windowAdded.connect(watchPanelTitle);
