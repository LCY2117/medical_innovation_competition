/** Web Audio：CPR 节拍器滴答声与提示音（需用户手势后创建 AudioContext）。 */

let ctx: AudioContext | null = null;

/** 创建/恢复 AudioContext（浏览器要求用户手势后才能发声）。 */
export function ensureAudio(): AudioContext | null {
  try {
    const AC =
      window.AudioContext ||
      (window as unknown as { webkitAudioContext?: typeof AudioContext }).webkitAudioContext;
    if (!AC) return null;
    if (!ctx) ctx = new AC();
    if (ctx.state === "suspended") void ctx.resume();
    return ctx;
  } catch {
    return null;
  }
}

/** 播放一次节拍音。kind: press=按压（高频短促） breath=吹气（低频柔和）。 */
export function playBeat(kind: "press" | "breath"): void {
  const c = ensureAudio();
  if (!c) return;
  try {
    const osc = c.createOscillator();
    const gain = c.createGain();
    const now = c.currentTime;
    osc.type = "sine";
    osc.frequency.value = kind === "press" ? 940 : 520;
    gain.gain.setValueAtTime(0.0001, now);
    gain.gain.linearRampToValueAtTime(kind === "press" ? 0.4 : 0.3, now + 0.005);
    gain.gain.exponentialRampToValueAtTime(0.0001, now + (kind === "press" ? 0.12 : 0.35));
    osc.connect(gain);
    gain.connect(c.destination);
    osc.start(now);
    osc.stop(now + (kind === "press" ? 0.14 : 0.4));
  } catch {
    /* 忽略音频异常，节拍器仍以视觉脉冲运行 */
  }
}

/** 播放一次短提示音（动作成功反馈）。 */
export function playConfirm(): void {
  const c = ensureAudio();
  if (!c) return;
  try {
    const osc = c.createOscillator();
    const gain = c.createGain();
    const now = c.currentTime;
    osc.type = "triangle";
    osc.frequency.value = 1320;
    gain.gain.setValueAtTime(0.0001, now);
    gain.gain.linearRampToValueAtTime(0.25, now + 0.01);
    gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.25);
    osc.connect(gain);
    gain.connect(c.destination);
    osc.start(now);
    osc.stop(now + 0.28);
  } catch {
    /* ignore */
  }
}
