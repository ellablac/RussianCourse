/**
 * videos.js
 *
 * Karaoke synchronization for a YouTube player.
 * Highlights the current line and progressively fills it left->right with a glow trail.
 */
export class KaraokeSync {
  /**
   * @param {Object} options
   * @param {YT.Player} options.player
   * @param {{t:number, line:number}[]} options.timeline - sorted by t
   * @param {string} options.lineSelector
   * @param {number} options.intervalMs
   */
  constructor({ player, timeline, lineSelector = ".lineRow", intervalMs = 150 }) {
    this.player = player;
    this.timeline = timeline;
    this.lineSelector = lineSelector;
    this.intervalMs = intervalMs;

    this.lineEls = [];
    this.activeLine = -1;
    this.karaokeTimer = null;
  }

  /** Collect DOM line elements (call after lyrics render). */
  init() {
    this.lineEls = Array.from(document.querySelectorAll(this.lineSelector));
    this.activeLine = -1;
  }

  /** Start polling and updating highlight/fill. */
  start() {
    if (this.karaokeTimer) return;

    this.karaokeTimer = window.setInterval(() => {
      if (!this.player || typeof this.player.getCurrentTime !== "function") return;

      // Optional: only update while playing (state 1)
      if (typeof this.player.getPlayerState === "function") {
        const state = this.player.getPlayerState();
        if (state !== 1) return;
      }

      const currentTime = this.player.getCurrentTime();
      const lineIndex = this.getLineForTime(currentTime);
      if (lineIndex < 0) return;

      this.setActiveLine(lineIndex);
      this.updateProgress(currentTime);
    }, this.intervalMs);
  }

  /** Stop polling. */
  stop() {
    if (!this.karaokeTimer) return;
    window.clearInterval(this.karaokeTimer);
    this.karaokeTimer = null;
  }

  /** Binary search: last timeline entry with t <= current time. */
  getLineForTime(timeSeconds) {
    let low = 0;
    let high = this.timeline.length - 1;
    let result = -1;

    while (low <= high) {
      const mid = Math.floor((low + high) / 2);
      if (this.timeline[mid].t <= timeSeconds) {
        result = mid;
        low = mid + 1;
      } else {
        high = mid - 1;
      }
    }

    return result >= 0 ? this.timeline[result].line : -1;
  }

  /** Highlight the current line and reset old line fill. */
  setActiveLine(index) {
    if (index === this.activeLine) return;

    if (this.activeLine >= 0 && this.lineEls[this.activeLine]) {
      const oldEl = this.lineEls[this.activeLine];
      oldEl.classList.remove("active");
      oldEl.style.setProperty("--fill", "0");
    }

    this.activeLine = index;

    if (this.activeLine >= 0 && this.lineEls[this.activeLine]) {
      const el = this.lineEls[this.activeLine];
      el.classList.add("active");
      el.style.setProperty("--fill", "0");
      el.scrollIntoView({ block: "nearest", behavior: "smooth" });
    }
  }

  /** Update progressive fill based on time within the active line's interval. */
  updateProgress(currentTimeSeconds) {
    const lineIndex = this.getLineForTime(currentTimeSeconds);
    if (lineIndex < 0) return;

    const start = this.getStartTimeForLine(lineIndex);
    const end = this.getEndTimeForLine(lineIndex);
    if (start === null || end === null) return;

    const duration = end - start;
    if (duration <= 0) return;

    const raw = (currentTimeSeconds - start) / duration;
    const progress = Math.max(0, Math.min(1, raw));
    const percent = progress * 100;

    const el = this.lineEls[lineIndex];
    if (el) el.style.setProperty("--fill", String(percent));
  }

  /** Find the timeline start time for a given line index. */
  getStartTimeForLine(lineIndex) {
    for (let i = 0; i < this.timeline.length; i++) {
      if (this.timeline[i].line === lineIndex) return this.timeline[i].t;
    }
    return null;
  }

  /** End time is the next timeline time after this line's start; fallback for last line. */
  getEndTimeForLine(lineIndex) {
    const start = this.getStartTimeForLine(lineIndex);
    if (start === null) return null;

    for (let i = 0; i < this.timeline.length; i++) {
      if (this.timeline[i].t > start) return this.timeline[i].t;
    }

    return start + 3; // fallback for last line
  }
}