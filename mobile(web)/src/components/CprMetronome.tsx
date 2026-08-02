import React, { useEffect, useRef, useState } from 'react';

const BPM = 110;
const COMPRESSIONS = 30;
const BREATHES = 2;
// 每个按压周期间隔（秒）：60 / BPM
const BEAT_INTERVAL = 60 / BPM;

interface CprMetronomeProps {
  active: boolean;
  onBeat?: (count: number, phase: 'compress' | 'breathe') => void;
}

export function CprMetronome({ active, onBeat }: CprMetronomeProps) {
  const [count, setCount] = useState(0);
  const [phase, setPhase] = useState<'compress' | 'breathe'>('compress');
  const audioRef = useRef<AudioContext | null>(null);

  useEffect(() => {
    if (!active) {
      setCount(0);
      setPhase('compress');
      return;
    }
    if (!audioRef.current) {
      try {
        const Ctx = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
        audioRef.current = new Ctx();
      } catch {
        audioRef.current = null;
      }
    }
    const ctx = audioRef.current;
    let nextBeat = performance.now() + 400;
    let timer: number | null = null;

    const playBeep = () => {
      if (!ctx) return;
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'square';
      osc.frequency.value = 880;
      gain.gain.setValueAtTime(0.0001, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.35, ctx.currentTime + 0.005);
      gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.09);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + 0.1);
    };

    const loop = () => {
      setCount((c) => {
        const next = c + 1;
        if (next <= COMPRESSIONS) {
          setPhase('compress');
          playBeep();
          onBeat?.(next, 'compress');
          nextBeat += BEAT_INTERVAL * 1000;
          timer = window.setTimeout(loop, BEAT_INTERVAL * 1000);
        } else if (next <= COMPRESSIONS + BREATHES) {
          setPhase('breathe');
          onBeat?.(next, 'breathe');
          // 呼吸期停顿 1.6 秒
          nextBeat += 1600;
          timer = window.setTimeout(loop, 1600);
        } else {
          setCount(0);
          timer = window.setTimeout(loop, 400);
        }
        return next;
      });
    };

    timer = window.setTimeout(loop, 400);
    return () => {
      if (timer) window.clearTimeout(timer);
    };
  }, [active, onBeat]);

  const inCompress = phase === 'compress';
  const cycleCount = ((count - 1) % (COMPRESSIONS + BREATHES)) + 1;

  return (
    <div className={`cpr-metronome ${active ? 'active' : ''} ${inCompress ? 'compress' : 'breathe'}`}>
      <div className="cpr-metronome-head">
        <span className="cpr-pulse-dot" />
        <strong>{inCompress ? '胸外按压' : '人工呼吸'}</strong>
        <span>{BPM} BPM · 30:2</span>
      </div>
      <div className="cpr-metronome-beat">
        <div className="cpr-beat-ring">
          <span className="cpr-beat-count">{inCompress ? cycleCount : cycleCount - COMPRESSIONS}</span>
        </div>
        <div className="cpr-beat-label">{inCompress ? `第 ${cycleCount} 次按压` : `呼吸 ${cycleCount - COMPRESSIONS}/2`}</div>
      </div>
      <div className="cpr-phase-track">
        <div className={`cpr-phase-seg ${count <= COMPRESSIONS ? 'filled' : ''}`}>按压 ×{COMPRESSIONS}</div>
        <div className={`cpr-phase-seg breathe ${count > COMPRESSIONS ? 'filled' : ''}`}>呼吸 ×{BREATHES}</div>
      </div>
    </div>
  );
}
