# Design System: Cyberpunk Bazzite (Neon Purple / Dark Cyber)

Use this design system as a strict rulebook for all UI, components, layouts, and styling. Avoid generic AI gradients, standard Bootstrap/Tailwind cards, and default blue/purple glows. The aesthetic must feel like a premium, high-tech gaming OS: dark, hyper-sharp, high-contrast, with precise, vibrant neon accents.

---

## 🎨 1. Color Palette

Strictly adhere to this exact hex color matrix. Do not introduce unauthorized shades.

### ⬛ Backgrounds (Deep Cyber Dark)
*   `--bg-main`: `#0b0914` (Deep obsidian void; primary app background)
*   `--bg-surface`: `#131024` (Slightly lighter dark for cards, containers, panels)
*   `--bg-overlay`: `#1c1833` (For modals, dropdowns, hovered item backgrounds)

### 🔮 Primary Accents (Bazzite / Cyber Neon)
*   `--neon-purple`: `#a855f7` (Vibrant electric purple; primary buttons, active states)
*   `--neon-magenta`: `#ec4899` (Hot pink/magenta; accent highlights, alerts, alternate states)
*   `--neon-cyan`: `#06b6d4` (Data cyan; complementary accent, secondary data points, success/info)

### 📝 Typography & Status
*   `--text-primary`: `#f8fafc` (Ultra-crisp off-white)
*   `--text-secondary`: `#94a3b8` (Muted slate gray for secondary labels)
*   `--text-muted`: `#475569` (Dark slate gray for disabled states or borders)
*   `--ui-danger`: `#f43f5e` (Cyber crimson)

---

## 📐 2. Typography

The type scale must feel digital, technical, and exceptionally clean.

*   **Primary Font (UI & Code):** `JetBrains Mono`, `Fira Code`, or system monospace (`ui-monospace`, `SFMono-Regular`, `Menlo`, `Monaco`, `Consolas`).
*   **Alternative Body Font (If strictly necessary):** `Inter` or `Plus Jakarta Sans`.
*   **Tracking/Letter-spacing:**
    *   Headings: `tracking-wider` (uppercase where appropriate).
    *   Small UI Text: `tracking-widest` (uppercase, `text-xs`).
*   **Scale:** Keep text tight and structured. Use `text-xs` for technical metadata and labels.

---

## 💎 3. Component Aesthetics & Micro-Interactions

Do not use soft, fuzzy drop shadows. Use hard angles, sharp borders, and intentional glow filters.

### 🔲 Borders & Radii
*   **Corner Radius:** Sharp corners or very tight radius only (`rounded-none` or `rounded-sm` max 4px). No heavily rounded pill shapes.
*   **Default Border:** `1px solid #1c1833` (`--bg-overlay`).
*   **Interactive Border:** `1px solid #a855f7` (`--neon-purple`).

### 🌟 Neon Glows & Shadows
*   Never use messy, large blurred shadows. Use precise CSS container glows:
    *   *Purple Glow:* `box-shadow: 0 0 10px rgba(168, 85, 247, 0.4), 0 0 2px rgba(168, 85, 247, 0.2);`
    *   *Cyan Glow:* `box-shadow: 0 0 10px rgba(6, 182, 212, 0.4), 0 0 2px rgba(6, 182, 212, 0.2);`

### 🖱️ Interactive States (Hover/Active)
*   **Buttons:** Standard state is dark (`--bg-overlay`) with a colored neon border. Hover state flashes to a solid neon background with black text.
*   **Transitions:** Fast, snappy response (`transition-all duration-150 ease-out`). Avoid long, cinematic fades.
*   **Focus:** Direct, unfiltered glowing ring or an accent corner bracket.

---

## 🗺️ 4. Layout & Visual Density

*   **Grid System:** Emphasize a rigid grid layout. Use subtle horizontal and vertical border lines to partition sections, mimicking an advanced tactical dashboard or a gaming desktop environment.
*   **Density:** High-density layout. Keep padding intentional (`p-3` to `p-5`). Do not waste massive whitespace.
*   **Decorative Elements:** Use minor cybernetic details to anchor sections (e.g., text brackets `[ DATA ]`, small diagnostic bars, or subtle terminal `$` prefixes).

---

## ⚡ 5. Tailwind Cheat Sheet Implementation

If writing code in Tailwind CSS, map the styles like this:

```html
<!-- Base Container Example -->
<div class="bg-[#0b0914] text-[#f8fafc] font-mono min-h-screen p-6">
  
  <!-- Interactive Card Example -->
  <div class="bg-[#131024] border border-[#1c1833] hover:border-[#a855f7] transition-all duration-150 p-4 rounded-sm shadow-[0_0_10px_rgba(168,85,247,0.15)]">
    <div class="text-xs uppercase tracking-widest text-[#06b6d4] mb-1">// SYSTEM_STATUS</div>
    <h3 class="text-lg font-bold text-[#f8fafc] tracking-wider">CORE_ONLINE</h3>
    <p class="text-sm text-[#94a3b8] mt-2">All bazzite subsystems operational.</p>
    
    <!-- Cyber Button -->
    <button class="mt-4 w-full bg-transparent border border-[#a855f7] text-[#a855f7] hover:bg-[#a855f7] hover:text-[#0b0914] font-bold text-xs uppercase tracking-widest py-2 transition-all duration-150 rounded-none">
      Execute Protocol
    </button>
  </div>

</div>
```
