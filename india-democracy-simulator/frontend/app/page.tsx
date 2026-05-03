"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { useEffect, useState } from "react";

const STATS = [
  { label: "Lok Sabha Seats", value: 543, suffix: "" },
  { label: "States & UTs", value: 36, suffix: "" },
  { label: "Political Parties", value: 42, suffix: "" },
  { label: "Majority Mark", value: 272, suffix: " seats" },
];

const PARTIES = [
  { name: "BJP", seats: 248, color: "#FF9933" },
  { name: "INC", seats: 100, color: "#00BCD4" },
  { name: "SP", seats: 37, color: "#E60000" },
  { name: "TMC", seats: 29, color: "#00A651" },
  { name: "DMK", seats: 22, color: "#CC0000" },
  { name: "Others", seats: 107, color: "#4A4E69" },
];

const ROLES = [
  { id: "party_leader", icon: "👑", name: "Party Leader", desc: "Lead the nation. Every rally, every alliance, every crisis — your call.", difficulty: "Hard" },
  { id: "campaign_manager", icon: "📊", name: "Campaign Manager", desc: "Budget, booth agents, media narrative — the strategist's chair.", difficulty: "Medium" },
  { id: "swing_voter", icon: "🗳️", name: "Swing Voter", desc: "Represent millions of undecided voters. Watch. Judge. Decide.", difficulty: "Easy" },
  { id: "election_commission", icon: "⚖️", name: "Election Officer", desc: "Guard democracy. Handle EVMs, violations, and voter fraud.", difficulty: "Expert" },
];

function AnimatedCounter({ target, duration = 2000 }: { target: number; duration?: number }) {
  const [count, setCount] = useState(0);
  useEffect(() => {
    let start = 0;
    const step = target / (duration / 16);
    const timer = setInterval(() => {
      start += step;
      if (start >= target) {
        setCount(target);
        clearInterval(timer);
      } else {
        setCount(Math.floor(start));
      }
    }, 16);
    return () => clearInterval(timer);
  }, [target, duration]);
  return <>{count}</>;
}

export default function LandingPage() {
  return (
    <main className="relative min-h-screen overflow-hidden">
      {/* Animated background particles */}
      <div className="absolute inset-0 pointer-events-none">
        {Array.from({ length: 30 }).map((_, i) => (
          <div
            key={i}
            className="particle"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 8}s`,
              animationDuration: `${5 + Math.random() * 5}s`,
              background:
                i % 3 === 0
                  ? "rgba(255,107,43,0.5)"
                  : i % 3 === 1
                  ? "rgba(19,136,8,0.5)"
                  : "rgba(0,0,128,0.5)",
              width: `${2 + Math.random() * 3}px`,
              height: `${2 + Math.random() * 3}px`,
            }}
          />
        ))}
      </div>

      {/* Ambient glow orbs */}
      <div className="absolute top-1/4 left-1/4 w-[600px] h-[600px] rounded-full bg-[#FF6B2B]/[0.03] blur-[120px] pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-[500px] h-[500px] rounded-full bg-[#138808]/[0.03] blur-[100px] pointer-events-none" />

      {/* ═══ Hero Section ═══ */}
      <section className="relative flex flex-col items-center justify-center min-h-screen px-6 text-center">
        {/* Ashoka Chakra ring */}
        <motion.div
          initial={{ scale: 0, rotate: -180, opacity: 0 }}
          animate={{ scale: 1, rotate: 0, opacity: 1 }}
          transition={{ duration: 1.4, ease: "easeOut" }}
          className="mb-10"
        >
          <div className="relative w-36 h-36">
            <div className="absolute inset-0 rounded-full border-[3px] border-[#000080]/20 spin-slow" />
            <div className="absolute inset-2 rounded-full border-2 border-[#FF6B2B]/15" />
            <div className="absolute inset-4 rounded-full border border-[#138808]/10" />
            <div className="absolute inset-6 rounded-full bg-gradient-to-br from-[#FF6B2B]/10 via-transparent to-[#138808]/10 flex items-center justify-center backdrop-blur-sm">
              <span className="text-4xl">🏛️</span>
            </div>
          </div>
        </motion.div>

        {/* Title */}
        <motion.h1
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.9 }}
          className="font-[family-name:var(--font-outfit)] text-5xl sm:text-6xl md:text-8xl font-extrabold mb-6 leading-[0.95] tracking-tight"
        >
          <span className="bg-gradient-to-r from-[#FF6B2B] via-white to-[#138808] bg-clip-text text-transparent">
            India Election
          </span>
          <br />
          <span className="text-white/90">Simulator</span>
          <span className="text-[#FF6B2B]">.</span>
        </motion.h1>

        {/* Subtitle */}
        <motion.p
          initial={{ opacity: 0, y: 25 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6, duration: 0.8 }}
          className="text-lg md:text-xl text-[var(--text-secondary)] max-w-2xl mb-10 leading-relaxed"
        >
          543 constituencies. One majority. Can you win it?
          <br />
          <span className="text-[var(--text-muted)]">
            AI-powered civic education game built on real 2024 Lok Sabha data.
          </span>
        </motion.p>

        {/* CTA */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.9, duration: 0.5 }}
        >
          <Link href="/login">
            <button className="btn-saffron text-lg px-12 py-5 rounded-2xl">
              Start Simulation →
            </button>
          </Link>
        </motion.div>

        {/* Stats row */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.2, duration: 0.8 }}
          className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-16 w-full max-w-3xl"
        >
          {STATS.map((stat) => (
            <div key={stat.label} className="glass-card-sm p-5 text-center group hover:border-[#FF6B2B]/20 transition-all">
              <div className="font-[family-name:var(--font-outfit)] text-3xl md:text-4xl font-extrabold text-[#FF6B2B] group-hover:count-pulse">
                <AnimatedCounter target={stat.value} />
                {stat.suffix}
              </div>
              <div className="text-xs text-[var(--text-muted)] mt-2 uppercase tracking-wider font-medium">{stat.label}</div>
            </div>
          ))}
        </motion.div>

        {/* 2024 Actual Results Bar */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.6, duration: 1 }}
          className="mt-14 w-full max-w-2xl"
        >
          <p className="text-[10px] text-[var(--text-muted)] mb-3 text-center uppercase tracking-[0.2em] font-semibold">
            2024 Actual Results
          </p>
          <div className="flex h-10 rounded-2xl overflow-hidden border border-white/5 relative">
            {/* Majority marker */}
            <div
              className="absolute top-0 bottom-0 w-[2px] bg-white/60 z-10 shadow-[0_0_8px_rgba(255,255,255,0.5)]"
              style={{ left: `${(272 / 543) * 100}%` }}
            />
            {PARTIES.map((p) => (
              <motion.div
                key={p.name}
                initial={{ width: 0 }}
                animate={{ width: `${(p.seats / 543) * 100}%` }}
                transition={{ delay: 1.8, duration: 1.2, ease: "easeOut" }}
                className="relative group flex items-center justify-center text-[10px] font-bold cursor-default"
                style={{ background: p.color }}
                title={`${p.name}: ${p.seats} seats`}
              >
                {p.seats > 25 && (
                  <span className="drop-shadow-lg text-white/90">{p.name}</span>
                )}
              </motion.div>
            ))}
          </div>
          <div className="flex justify-between text-[10px] text-[var(--text-muted)] mt-2 px-1">
            <span>0</span>
            <span className="text-[#FF6B2B] font-semibold">↑ 272 Majority</span>
            <span>543</span>
          </div>
        </motion.div>

        {/* Role Preview Cards */}
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 2.0, duration: 0.8 }}
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mt-20 w-full max-w-5xl"
        >
          {ROLES.map((role, i) => (
            <motion.div
              key={role.id}
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 2.2 + i * 0.1 }}
              className="glass-card-glow p-6 text-left cursor-pointer group"
            >
              <div className="flex justify-between items-start mb-4">
                <span className="text-3xl group-hover:scale-110 transition-transform duration-300 inline-block">
                  {role.icon}
                </span>
                <span className={`badge ${
                  role.difficulty === "Easy" ? "badge-booth" :
                  role.difficulty === "Medium" ? "badge-rally" :
                  role.difficulty === "Hard" ? "badge-crisis" :
                  "badge-scam"
                }`}>
                  {role.difficulty}
                </span>
              </div>
              <h3 className="font-[family-name:var(--font-outfit)] text-lg font-bold mb-2 group-hover:text-[#FF6B2B] transition-colors">
                {role.name}
              </h3>
              <p className="text-sm text-[var(--text-secondary)] leading-relaxed">{role.desc}</p>
            </motion.div>
          ))}
        </motion.div>

        {/* Feature highlights */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 2.6, duration: 0.8 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-5 mt-16 w-full max-w-4xl"
        >
          {[
            { icon: "🎯", title: "Real 2024 Data", desc: "563 actual constituencies with real margins, winners, and party data" },
            { icon: "🤖", title: "AI Opponent", desc: "Adversarial AI that counter-strategies your every move in real-time" },
            { icon: "📚", title: "Civics Education", desc: "Every decision teaches real Indian electoral mechanics and history" },
          ].map((f) => (
            <div key={f.title} className="glass-card p-7 hover:border-[#FF6B2B]/15 transition-all duration-300 hover:-translate-y-1 group">
              <div className="text-3xl mb-4 group-hover:scale-110 transition-transform inline-block">{f.icon}</div>
              <h3 className="font-[family-name:var(--font-outfit)] text-lg font-bold mb-2">{f.title}</h3>
              <p className="text-sm text-[var(--text-secondary)] leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </motion.div>

        <div className="mt-20 pb-10 text-xs text-[var(--text-muted)]">
          Built with real 2024 election data • 42 parties • Educational purpose only
        </div>
      </section>
    </main>
  );
}
