"use client";

import { motion } from "framer-motion";
import Image from "next/image";
import Link from "next/link";
import { useEffect, useState } from "react";

/* ═══════════════════════════════════════════════════════════════════
   DATA
   ═══════════════════════════════════════════════════════════════════ */

const PARTIES = [
  { name: "BJP", seats: 272, pct: "50.1%", trend: "+12", color: "#FF9933", icon: "🪷" },
  { name: "INC", seats: 136, pct: "28.3%", trend: "+8", color: "#00BCD4", icon: "✋" },
  { name: "SP", seats: 37, pct: "6.8%", trend: "+3", color: "#E60000", icon: "🚲" },
  { name: "TMC", seats: 29, pct: "5.2%", trend: "+2", color: "#00A651", icon: "🌸" },
  { name: "OTHERS", seats: 69, pct: "9.6%", trend: "+9", color: "#9C88FF", icon: "🏛️" },
];

const STATS = [
  { label: "LOK SABHA SEATS", value: 543, sub: "All Constituencies", icon: "👥", color: "#FF6B2B" },
  { label: "STATES & UTs", value: 36, sub: "Pan India Coverage", icon: "🗺️", color: "#00BCD4" },
  { label: "POLITICAL PARTIES", value: 42, sub: "Real 2024 Data", icon: "🏛️", color: "#9C88FF" },
  { label: "SEATS TO WIN", value: 272, sub: "Majority Mark", icon: "🏆", color: "#FFD700" },
];

const CLIMATE_CARDS = [
  { title: "SWING STATES", sub: "UP, Maharashtra, Bihar, Karnataka", tag: "High Impact", tagColor: "#FF6B2B", icon: "📊" },
  { title: "VOTER SENTIMENT", sub: "Youth vote ↑ 12%\nUrban shift detected", tag: "Dynamic", tagColor: "#00BCD4", icon: "👥" },
  { title: "MEDIA INFLUENCE", sub: "High\nSocial media surge", tag: "Trending", tagColor: "#9C88FF", icon: "📱" },
  { title: "ECONOMIC FACTOR", sub: "Inflation impact\nCost of living key", tag: "Critical", tagColor: "#E74C3C", icon: "₹" },
];

/* ═══════════════════════════════════════════════════════════════════
   ANIMATED COUNTER
   ═══════════════════════════════════════════════════════════════════ */

function AnimatedCounter({ target, duration = 2000 }: { target: number; duration?: number }) {
  const [count, setCount] = useState(0);
  useEffect(() => {
    let start = 0;
    const step = target / (duration / 16);
    const timer = setInterval(() => {
      start += step;
      if (start >= target) { setCount(target); clearInterval(timer); }
      else setCount(Math.floor(start));
    }, 16);
    return () => clearInterval(timer);
  }, [target, duration]);
  return <span aria-live="polite" aria-atomic="true">{count}</span>;
}

/* ═══════════════════════════════════════════════════════════════════
   PARTICLE FIELD
   ═══════════════════════════════════════════════════════════════════ */

function ParticleField() {
  const [particles] = useState(() => {
    const colors = [
      "rgba(255,107,43,0.4)", "rgba(19,136,8,0.4)",
      "rgba(0,188,212,0.3)", "rgba(156,136,255,0.3)",
    ];
    return Array.from({ length: 60 }, (_, i) => ({
      left: `${Math.random() * 100}%`,
      top: `${Math.random() * 100}%`,
      delay: `${Math.random() * 10}s`,
      dur: `${6 + Math.random() * 8}s`,
      bg: colors[i % 4],
      size: `${1.5 + Math.random() * 2.5}px`,
    }));
  });

  return (
    <div className="absolute inset-0 pointer-events-none overflow-hidden" aria-hidden="true">
      {particles.map((p, i) => (
        <div
          key={i}
          className="particle"
          style={{
            left: p.left, top: p.top,
            animationDelay: p.delay, animationDuration: p.dur,
            background: p.bg, width: p.size, height: p.size,
          }}
        />
      ))}
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════
   INDIA MAP — Real constituency map image with glow effects
   ═══════════════════════════════════════════════════════════════════ */

function IndiaMap() {
  return (
    <div className="india-map-container">
      {/* Ambient glow behind the map */}
      <div className="map-ambient-glow" />
      {/* Real India map image */}
      <Image
        src="/india-map-glow.png"
        alt="India Election Map with constituency boundaries and heatmap coloring"
        width={680}
        height={680}
        priority
        className="india-map-image"
      />
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════
   LIVE RESULTS PANEL
   ═══════════════════════════════════════════════════════════════════ */

function LiveResultsPanel() {
  const total = PARTIES.reduce((a, p) => a + p.seats, 0);
  return (
    <motion.div
      initial={{ opacity: 0, x: 40 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: 0.6, duration: 0.8 }}
      className="live-results-panel"
    >
      {/* Header */}
      <div className="panel-header">
        <div className="live-dot-wrapper">
          <span className="live-dot" />
          <span className="panel-title">LIVE RESULTS</span>
        </div>
        <span className="panel-subtitle">543 / 543 Constituencies</span>
      </div>

      {/* Party rows */}
      <div className="party-list">
        {PARTIES.map((party, i) => (
          <motion.div
            key={party.name}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.8 + i * 0.1 }}
            className="party-row"
          >
            <div className="party-icon" style={{ background: `${party.color}20`, borderColor: `${party.color}40` }}>
              <span>{party.icon}</span>
            </div>
            <div className="party-name" style={{ color: party.color }}>{party.name}</div>
            <div className="party-seats">
              <span className="seats-value"><AnimatedCounter target={party.seats} /></span>
            </div>
            <div className="party-meta">
              <span className="trend-up">↑ {party.trend}</span>
              <span className="party-pct">{party.pct}</span>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Seat distribution bar */}
      <div className="seat-bar-container">
        <div className="seat-bar">
          {PARTIES.map((party) => (
            <motion.div
              key={party.name}
              initial={{ width: 0 }}
              animate={{ width: `${(party.seats / total) * 100}%` }}
              transition={{ delay: 1.4, duration: 1, ease: "easeOut" }}
              className="seat-bar-segment"
              style={{ background: party.color }}
            />
          ))}
        </div>
        <div className="majority-label">
          <span>🏆</span> 272 to Win
        </div>
      </div>
    </motion.div>
  );
}

/* ═══════════════════════════════════════════════════════════════════
   MAIN LANDING PAGE
   ═══════════════════════════════════════════════════════════════════ */

export default function LandingPage() {

  return (
    <main className="landing-page" aria-label="India Election Simulator - Home">
      <ParticleField />

      {/* ═══ TOP NAVBAR ═══ */}
      <motion.nav
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="top-navbar"
        aria-label="Main navigation"
      >
        <div className="nav-left">
          <div className="nav-logo">
            <span className="logo-icon">🏛️</span>
            <span className="logo-text">
              India <span className="logo-accent">Election Simulator</span>
            </span>
          </div>
        </div>
        <div className="nav-right">
          <div className="nav-tag live-tag">
            <span className="live-dot-sm" />
            Live Simulation
          </div>
          <div className="nav-tag year-tag">2024 Lok Sabha</div>
        </div>
      </motion.nav>

      {/* ═══ HERO: 3-column layout ═══ */}
      <section className="hero-section" aria-label="Hero - Election simulator overview">
        {/* LEFT — Headline */}
        <motion.div
          initial={{ opacity: 0, x: -50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2, duration: 0.8 }}
          className="hero-left"
        >
          <div className="tagline">
            <span className="tagline-icon">✦</span>
            THE POWER IS IN YOUR STRATEGY
          </div>

          <h1 className="hero-title">
            <span className="title-gradient">India Election</span>
            <br />
            <span className="title-white">Simulator</span>
            <motion.span
              className="title-dot"
              animate={{ opacity: [1, 0.3, 1] }}
              transition={{ repeat: Infinity, duration: 2 }}
            >.</motion.span>
          </h1>

          <p className="hero-sub">
            AI-powered civic education game built on real
            <br />
            2024 Lok Sabha data. Make decisions. See impacts.
            <br />
            Change the outcome.
          </p>

          <div className="hero-cta">
            <motion.div whileHover={{ scale: 1.04 }} whileTap={{ scale: 0.97 }}>
              <Link href="/login" className="btn-primary-glow" aria-label="Start election simulation">
                Start Simulation <span className="btn-arrow" aria-hidden="true">→</span>
              </Link>
            </motion.div>
            <motion.div whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.97 }}>
              <button className="btn-outline-demo" aria-label="Watch demo video">
                <span className="play-icon" aria-hidden="true">▶</span> Watch Demo
              </button>
            </motion.div>
          </div>
        </motion.div>

        {/* CENTER — India Map */}
        <motion.div
          initial={{ opacity: 0, scale: 0.85 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.4, duration: 1, ease: "easeOut" }}
          className="hero-center"
        >
          <IndiaMap />
        </motion.div>

        {/* RIGHT — Live Results */}
        <div className="hero-right">
          <LiveResultsPanel />
        </div>
      </section>

      {/* ═══ POLITICAL CLIMATE STRIP ═══ */}
      <motion.section
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1.0, duration: 0.7 }}
        className="climate-strip"
        aria-label="Political climate indicators"
        role="region"
      >
        {/* Label card */}
        <div className="climate-label-card">
          <div className="climate-label-top">TODAY&apos;S</div>
          <div className="climate-label-main">POLITICAL<br />CLIMATE</div>
          <div className="climate-label-live">
            <span className="live-dot-sm" /> Live Insights
          </div>
        </div>

        {/* Climate info cards */}
        {CLIMATE_CARDS.map((card, i) => (
          <motion.div
            key={card.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.2 + i * 0.1 }}
            whileHover={{ scale: 1.03, y: -3 }}
            className="climate-card"
            tabIndex={0}
            role="article"
            aria-label={`${card.title}: ${card.tag}`}
          >
            <div className="climate-card-icon" style={{ color: card.tagColor }}>{card.icon}</div>
            <div className="climate-card-content">
              <h4 className="climate-card-title">{card.title}</h4>
              <p className="climate-card-sub">{card.sub}</p>
            </div>
            <div className="climate-card-tag" style={{ color: card.tagColor, borderColor: `${card.tagColor}30`, background: `${card.tagColor}10` }}>
              {card.tag}
            </div>
          </motion.div>
        ))}
      </motion.section>

      {/* ═══ BOTTOM STATS ═══ */}
      <motion.section
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1.4, duration: 0.7 }}
        className="bottom-stats"
        aria-label="Key election statistics"
        role="region"
      >
        {STATS.map((stat, i) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.6 + i * 0.1 }}
            whileHover={{ scale: 1.04, y: -4 }}
            className="stat-card"
          >
            <div className="stat-card-icon" style={{ color: stat.color }}>
              {stat.icon}
            </div>
            <div className="stat-card-body">
              <div className="stat-card-value" style={{ color: stat.color }}>
                <AnimatedCounter target={stat.value} />
              </div>
              <div className="stat-card-label">{stat.label}</div>
              <div className="stat-card-sub">{stat.sub}</div>
            </div>
          </motion.div>
        ))}
      </motion.section>

      {/* Footer accent */}
      <footer className="landing-footer" role="contentinfo">
        Built with real 2024 election data • 42 parties • Educational purpose only
      </footer>
    </main>
  );
}
