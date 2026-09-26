/* peak-glow.js: brighten elements to the live peak level of an <audio> element.
 * Drop into Flask's static/ and add <script src="/static/peak-glow.js"></script>.
 * Tag any element with the selector below (default: class="peak-glow").
 * Override any setting before this script loads:
 *   <script>window.PeakGlowConfig = { target: "both", releaseMs: 300 };</script>
 */
(function () {
  "use strict";

  const C = Object.assign({
    selector: ".peak-glow",       // any CSS selector: ".peak-glow", "#meter", ...
    audioId: "live-stream-audio", // id of the <audio> element to listen to
    target: "background",         // "background" | "border" | "both"
    floorDb: -60,                 // peak at or below this dB = level 0 (dBFS 0 = 127)
    attackMs: 10,                 // rise time constant: smaller = snappier
    releaseMs: 150,               // fall time constant: larger = smoother decay
    maxLighten: 60,               // % mixed toward white at level 127
    respectReducedMotion: true,   // do nothing if the OS asks for reduced motion
  }, (typeof window !== "undefined" && window.PeakGlowConfig) || {});

  // Sample peak (0..1) -> 0..127, linear in dB between floorDb and 0 dBFS.
  function toLevel(peak) {
    if (peak <= 0) return 0;
    const db = 20 * Math.log10(peak);
    return Math.round(127 * Math.min(1, Math.max(0, (db - C.floorDb) / -C.floorDb)));
  }

  if (typeof document === "undefined") { module.exports = { toLevel, C }; return; } // node self-check

  const audio = document.getElementById(C.audioId);
  if (!audio) return;
  window.PeakGlow = {
    config: C,
    prepare,
  };
  let ctx, analyser, buf, raf = 0, level = 0, last = 0, items = [];

  function apply(v) {
    const p = (v / 127) * C.maxLighten;
    const glowBg = C.target !== "border";
    const glowBd = C.target !== "background";
    for (const it of items) { // the un-targeted property is written back to its base colour
      it.el.style.backgroundColor = glowBg ? `color-mix(in srgb, ${it.bg}, white ${p}%)` : it.bg;
      it.el.style.borderColor = glowBd ? `color-mix(in srgb, ${it.bd}, white ${p}%)` : it.bd;
      it.el.style.setProperty("--peak", v);
    }
  }

  function frame(t) {
    analyser.getFloatTimeDomainData(buf);
    let peak = 0;
    for (const s of buf) peak = Math.max(peak, Math.abs(s));
    const target = toLevel(peak);
    const tau = target > level ? C.attackMs : C.releaseMs;
    level += (target - level) * (1 - Math.exp(-(t - last) / tau));
    last = t;
    apply(Math.round(level));
    raf = requestAnimationFrame(frame);
  }

  function prepare() {
    if (
      C.respectReducedMotion &&
      matchMedia("(prefers-reduced-motion: reduce)").matches
    ) {
      return;
    }
  
    if (!ctx) {
      ctx = new AudioContext();
      analyser = ctx.createAnalyser();
      analyser.fftSize = 1024;
      buf = new Float32Array(analyser.fftSize);
  
      ctx.createMediaElementSource(audio).connect(analyser);
      analyser.connect(ctx.destination);
    }
  
    ctx.resume();
  }

  function start() {
    prepare();
  
    if (!ctx || raf) return;

    for (const el of document.querySelectorAll(C.selector)) {
    el.style.removeProperty("background-color");
    el.style.removeProperty("border-color");
    el.style.removeProperty("--peak");
    }
    // Re-read base colours on every start so theme changes are picked up.
    items = [...document.querySelectorAll(C.selector)].map((el) => {
      const cs = getComputedStyle(el);
  
      const it = {
        el,
        bg: cs.backgroundColor,
        bd: cs.borderColor,
        css: el.style.cssText,
      };
  
      el.style.transition = "none";
      return it;
    });
  
    last = performance.now();
    raf = requestAnimationFrame(frame);
  }

  function stop() {
    cancelAnimationFrame(raf);
    raf = 0;
    level = 0;
    for (const it of items) it.el.style.cssText = it.css; // back to the original look
    items = [];
  }

  audio.addEventListener("play", start);
  for (const e of ["pause", "ended", "error"]) audio.addEventListener(e, stop);
  if (!audio.paused) start();
})();
