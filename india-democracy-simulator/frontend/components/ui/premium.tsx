"use client";

import { useEffect, useMemo, useState } from "react";
import { motion, useSpring, useTransform } from "framer-motion";

/* ═══════════════════════════════════════════════════════════════════════════
   ANIMATED NUMBER TICKER
   Numbers never snap — they roll like a stock ticker
   ═══════════════════════════════════════════════════════════════════════════ */
export function AnimatedNumber({
  value,
  prefix = "",
  suffix = "",
  className = "",
  duration = 0.8,
}: {
  value: number;
  prefix?: string;
  suffix?: string;
  className?: string;
  duration?: number;
}) {
  const spring = useSpring(0, { duration: duration * 1000, bounce: 0 });
  const display = useTransform(spring, (v) => Math.round(v));
  const [rendered, setRendered] = useState(0);

  useEffect(() => {
    spring.set(value);
  }, [spring, value]);

  useEffect(() => {
    const unsub = display.on("change", (v) => setRendered(v));
    return unsub;
  }, [display]);

  return (
    <span className={`${className} ticker-flash`} key={value}>
      {prefix}{rendered.toLocaleString()}{suffix}
    </span>
  );
}

/* ═══════════════════════════════════════════════════════════════════════════
   GAUGE CHART (Semi-circular arc)
   For approval rating, win probability, etc.
   ═══════════════════════════════════════════════════════════════════════════ */
export function GaugeChart({
  value,
  max = 100,
  size = 120,
  strokeWidth = 8,
  color = "#FF6B2B",
  label,
  suffix = "%",
}: {
  value: number;
  max?: number;
  size?: number;
  strokeWidth?: number;
  color?: string;
  label?: string;
  suffix?: string;
}) {
  const radius = (size - strokeWidth) / 2;
  const circumference = Math.PI * radius; // half circle
  const pct = Math.min(value / max, 1);
  const offset = circumference * (1 - pct);

  return (
    <div className="flex flex-col items-center">
      <svg width={size} height={size / 2 + 10} viewBox={`0 0 ${size} ${size / 2 + 10}`}>
        {/* Background arc */}
        <path
          d={`M ${strokeWidth / 2} ${size / 2} A ${radius} ${radius} 0 0 1 ${size - strokeWidth / 2} ${size / 2}`}
          className="gauge-bg"
          strokeWidth={strokeWidth}
        />
        {/* Value arc */}
        <motion.path
          d={`M ${strokeWidth / 2} ${size / 2} A ${radius} ${radius} 0 0 1 ${size - strokeWidth / 2} ${size / 2}`}
          className="gauge-ring"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1.5, ease: "easeOut" }}
        />
      </svg>
      <div className="text-center -mt-4">
        <div className="font-[family-name:var(--font-space)] text-2xl font-bold" style={{ color }}>
          <AnimatedNumber value={Math.round(value)} suffix={suffix} />
        </div>
        {label && (
          <div className="text-[10px] text-[var(--text-muted)] uppercase tracking-wider font-semibold mt-0.5">
            {label}
          </div>
        )}
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════════════
   PARLIAMENT HEMICYCLE (543 dots in a semicircle)
   ═══════════════════════════════════════════════════════════════════════════ */
export function ParliamentChart({
  playerSeats,
  oppSeats,
  playerColor = "#FF6B2B",
  oppColor = "#00BCD4",
  size = 320,
}: {
  playerSeats: number;
  oppSeats: number;
  playerColor?: string;
  oppColor?: string;
  size?: number;
}) {
  const total = 543;

  // Use useMemo to compute dot positions (pure computation, no refs needed)
  const dots = useMemo(() => {
    const result: { x: number; y: number }[] = [];
    const rows = 12;
    const cx = size / 2;
    const cy = size / 2 + 10;
    let placed = 0;
    for (let row = 0; row < rows && placed < total; row++) {
      const r = 40 + row * ((size / 2 - 50) / rows);
      const seatsInRow = Math.min(
        Math.floor(Math.PI * r / 8),
        total - placed
      );
      for (let s = 0; s < seatsInRow && placed < total; s++) {
        const angle = Math.PI - (s / (seatsInRow - 1 || 1)) * Math.PI;
        const x = cx + r * Math.cos(angle);
        const y = cy - r * Math.sin(angle);
        result.push({ x, y });
        placed++;
      }
    }
    return result;
  }, [size]);

  // Derive colors from props (no mutation needed)
  const getColor = (idx: number) => {
    if (idx < playerSeats) return playerColor;
    if (idx < playerSeats + oppSeats) return oppColor;
    return "#1E2240";
  };

  return (
    <div className="relative" style={{ width: size, height: size / 2 + 30 }}>
      <svg width={size} height={size / 2 + 30} viewBox={`0 0 ${size} ${size / 2 + 30}`}>
        {dots.map((dot, i) => (
          <motion.circle
            key={i}
            cx={dot.x}
            cy={dot.y}
            r={2.5}
            fill={getColor(i)}
            initial={{ opacity: 0, scale: 0 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: i * 0.002, duration: 0.3 }}
          />
        ))}
        {/* Majority line */}
        <line
          x1={size / 2} y1={size / 2 + 15}
          x2={size / 2} y2={10}
          stroke="rgba(255,255,255,0.15)"
          strokeWidth={1}
          strokeDasharray="4 3"
        />
      </svg>
      {/* Majority label */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 text-[9px] text-[var(--text-muted)] font-semibold uppercase tracking-wider">
        272 Majority
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════════════
   TYPEWRITER TEXT
   Reveals text character by character like an intelligence briefing
   ═══════════════════════════════════════════════════════════════════════════ */
export function TypewriterText({
  text,
  speed = 20,
  className = "",
  onComplete,
}: {
  text: string;
  speed?: number;
  className?: string;
  onComplete?: () => void;
}) {
  const [charIndex, setCharIndex] = useState(0);

  useEffect(() => {
    // Reset and start interval when text changes
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setCharIndex(0);
    let i = 0;
    const interval = setInterval(() => {
      i++;
      if (i >= text.length) {
        clearInterval(interval);
        onComplete?.();
      }
      setCharIndex((prev) => Math.min(prev + 1, text.length));
    }, speed);
    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [text, speed]);

  const displayed = text.slice(0, charIndex);
  const done = charIndex >= text.length;

  return (
    <span className={className}>
      {displayed}
      {!done && <span className="typewriter-cursor" />}
    </span>
  );
}

/* ═══════════════════════════════════════════════════════════════════════════
   SKELETON LOADER (Shimmer card placeholder)
   ═══════════════════════════════════════════════════════════════════════════ */
export function SkeletonCard({ className = "" }: { className?: string }) {
  return (
    <div className={`glass-card-sm p-6 ${className}`}>
      <div className="skeleton h-3 w-1/3 mb-4" />
      <div className="skeleton h-8 w-2/3 mb-3" />
      <div className="skeleton h-3 w-full mb-2" />
      <div className="skeleton h-3 w-4/5" />
    </div>
  );
}
