/** 深空星云粒子 + 扫描线动画（Canvas 手写，无外部库）。 */
import { useEffect, useRef } from "react";

interface Star {
  x: number;
  y: number;
  r: number;
  a: number;
  tw: number;
}

interface Nebula {
  x: number;
  y: number;
  r: number;
  color: string;
  vx: number;
  vy: number;
}

/** 全屏背景层：星云径向渐变 + 闪烁星点 + 周期性扫描线。 */
export default function SpaceBackground() {
  const ref = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = ref.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let raf = 0;
    let w = 0;
    let h = 0;
    let stars: Star[] = [];
    let nebulas: Nebula[] = [];

    const resize = () => {
      const dpr = window.devicePixelRatio || 1;
      w = canvas.clientWidth;
      h = canvas.clientHeight;
      canvas.width = Math.max(1, Math.floor(w * dpr));
      canvas.height = Math.max(1, Math.floor(h * dpr));
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.fillStyle = "#0a1120";
      ctx.fillRect(0, 0, w, h);
    };

    const seed = () => {
      const count = Math.min(180, Math.max(60, Math.floor((w * h) / 7000)));
      stars = Array.from({ length: count }, () => ({
        x: Math.random() * w,
        y: Math.random() * h,
        r: Math.random() * 1.3 + 0.3,
        a: Math.random() * 0.7 + 0.3,
        tw: Math.random() * 2 + 1,
      }));
      const R = Math.max(w, h);
      nebulas = [
        { x: w * 0.22, y: h * 0.32, r: R * 0.38, color: "rgba(0,229,255,0.05)", vx: 5, vy: 3 },
        { x: w * 0.82, y: h * 0.72, r: R * 0.42, color: "rgba(167,139,250,0.05)", vx: -4, vy: -2 },
        { x: w * 0.55, y: h * 0.18, r: R * 0.3, color: "rgba(255,59,92,0.04)", vx: 4, vy: 2 },
      ];
    };

    const frame = (t: number) => {
      ctx.clearRect(0, 0, w, h);

      // 星云
      for (const nb of nebulas) {
        nb.x += nb.vx * 0.012;
        nb.y += nb.vy * 0.012;
        if (nb.x < -nb.r) nb.x = w + nb.r;
        if (nb.x > w + nb.r) nb.x = -nb.r;
        if (nb.y < -nb.r) nb.y = h + nb.r;
        if (nb.y > h + nb.r) nb.y = -nb.r;
        const g = ctx.createRadialGradient(nb.x, nb.y, 0, nb.x, nb.y, nb.r);
        g.addColorStop(0, nb.color);
        g.addColorStop(1, "rgba(0,0,0,0)");
        ctx.fillStyle = g;
        ctx.fillRect(0, 0, w, h);
      }

      // 星点闪烁
      for (const s of stars) {
        const alpha = s.a * (0.55 + 0.45 * Math.sin((t / 1000) * s.tw + s.x));
        ctx.globalAlpha = Math.max(0.05, alpha);
        ctx.fillStyle = "#bfe9ff";
        ctx.beginPath();
        ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.globalAlpha = 1;

      // 扫描线
      const scanY = ((t / 1000) * 26) % h;
      const grad = ctx.createLinearGradient(0, scanY - 70, 0, scanY);
      grad.addColorStop(0, "rgba(0,229,255,0)");
      grad.addColorStop(1, "rgba(0,229,255,0.07)");
      ctx.fillStyle = grad;
      ctx.fillRect(0, scanY - 70, w, 70);
      ctx.fillStyle = "rgba(0,229,255,0.16)";
      ctx.fillRect(0, scanY, w, 1);

      raf = requestAnimationFrame(frame);
    };

    resize();
    seed();
    raf = requestAnimationFrame(frame);
    window.addEventListener("resize", () => {
      resize();
      seed();
    });
    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("resize", resize);
    };
  }, []);

  return <canvas ref={ref} className="space-bg" aria-hidden />;
}
