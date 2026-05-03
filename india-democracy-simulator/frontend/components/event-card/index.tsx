"use client";

import { motion } from "framer-motion";
import { useState } from "react";
import { GameEvent } from "@/store/gameStore";
import { TypewriterText } from "@/components/ui/premium";

const EVENT_ICONS: Record<string, string> = {
  crisis: "🔥",
  rally: "📢",
  alliance: "🤝",
  scam: "💣",
  media: "📺",
  booth: "🗳️",
  caste_coalition: "👥",
  regional_defense: "🛡️",
  opposition_research: "🔍",
};

const EVENT_COLORS: Record<string, string> = {
  crisis: "#E74C3C",
  rally: "#FF6B2B",
  alliance: "#00BCD4",
  scam: "#E74C3C",
  media: "#9C88FF",
  booth: "#1BA80E",
  caste_coalition: "#FF9933",
  regional_defense: "#4DA6FF",
  opposition_research: "#9C88FF",
};

export function EventCard({
  event,
  onChoiceSelect,
  disabled,
}: {
  event: GameEvent;
  onChoiceSelect: (index: number) => void;
  disabled: boolean;
}) {
  const icon = EVENT_ICONS[event.event_type] || "📋";
  const badgeClass = `badge badge-${event.event_type}`;
  const accentColor = EVENT_COLORS[event.event_type] || "#FF6B2B";
  const [bodyRevealed, setBodyRevealed] = useState(false);
  const [hoveredChoice, setHoveredChoice] = useState<number | null>(null);

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.96, y: 20 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      transition={{ duration: 0.5, ease: "easeOut" }}
      className="glass-card-glow p-8 relative overflow-hidden"
    >
      {/* Top gradient accent */}
      <motion.div
        className="absolute top-0 left-0 w-full h-[3px]"
        style={{ background: `linear-gradient(90deg, ${accentColor}, ${accentColor}88, ${accentColor})` }}
        initial={{ scaleX: 0 }}
        animate={{ scaleX: 1 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
      />

      {/* Scanning line effect */}
      <div className="absolute inset-0 pointer-events-none scan-line opacity-30" />

      {/* Ambient glow */}
      <div
        className="absolute -top-20 -right-20 w-48 h-48 rounded-full blur-[80px] pointer-events-none"
        style={{ background: `${accentColor}08` }}
      />

      {/* Header */}
      <div className="flex justify-between items-start mb-5">
        <div className="flex items-center gap-3">
          <motion.span
            className="text-2xl"
            initial={{ scale: 0, rotate: -45 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
          >
            {icon}
          </motion.span>
          <span className={badgeClass}>
            {event.event_type.replace("_", " ")}
          </span>
        </div>
        {event.affected_states && event.affected_states.length > 0 && (
          <motion.span
            initial={{ opacity: 0, x: 10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
            className="text-xs text-[var(--text-muted)] bg-white/[0.03] px-3 py-1.5 rounded-lg border border-white/5"
          >
            📍 {event.affected_states.join(", ")}
          </motion.span>
        )}
      </div>

      {/* Headline */}
      <h2 className="font-[family-name:var(--font-outfit)] text-2xl md:text-[26px] font-bold mb-4 leading-snug text-white">
        <TypewriterText text={event.headline} speed={25} onComplete={() => setBodyRevealed(true)} />
      </h2>

      {/* Body — fades in after headline typewriter completes */}
      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: bodyRevealed ? 1 : 0 }}
        transition={{ duration: 0.6 }}
        className="text-[var(--text-secondary)] mb-8 leading-relaxed text-[15px]"
      >
        {event.body}
      </motion.p>

      {/* Choices */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: bodyRevealed ? 1 : 0.3, y: bodyRevealed ? 0 : 10 }}
        transition={{ duration: 0.5, delay: 0.2 }}
        className="space-y-3"
      >
        {event.choices.map((choice, idx) => (
          <motion.button
            key={idx}
            whileHover={!disabled ? { scale: 1.015, x: 6 } : {}}
            whileTap={!disabled ? { scale: 0.98 } : {}}
            onClick={() => onChoiceSelect(idx)}
            onMouseEnter={() => setHoveredChoice(idx)}
            onMouseLeave={() => setHoveredChoice(null)}
            disabled={disabled}
            className={`choice-btn ${disabled ? "opacity-40 cursor-not-allowed" : ""}`}
          >
            <div className="flex items-start gap-3">
              <span className="w-8 h-8 rounded-xl flex items-center justify-center text-sm font-bold flex-shrink-0 mt-0.5 transition-all duration-300"
                style={{
                  background: hoveredChoice === idx ? `${accentColor}25` : `${accentColor}10`,
                  border: `1px solid ${hoveredChoice === idx ? `${accentColor}50` : `${accentColor}20`}`,
                  color: accentColor,
                }}
              >
                {idx + 1}
              </span>
              <div className="flex-1">
                <span className="font-semibold text-[15px] leading-snug">{choice.text}</span>
                {/* Effect preview */}
                <motion.div
                  className="flex gap-3 mt-2 text-[11px]"
                  initial={{ opacity: 0.5 }}
                  animate={{ opacity: hoveredChoice === idx ? 1 : 0.5 }}
                >
                  {choice.effect.budget_delta_crore !== 0 && (
                    <span className={choice.effect.budget_delta_crore < 0 ? "text-[#E74C3C]" : "text-[#1BA80E]"}>
                      ₹{choice.effect.budget_delta_crore > 0 ? "+" : ""}{choice.effect.budget_delta_crore}Cr
                    </span>
                  )}
                  {choice.effect.approval_delta !== 0 && (
                    <span className={choice.effect.approval_delta < 0 ? "text-[#E74C3C]" : "text-[#1BA80E]"}>
                      {choice.effect.approval_delta > 0 ? "+" : ""}{choice.effect.approval_delta}% approval
                    </span>
                  )}
                  {choice.effect.seat_delta !== 0 && (
                    <span className={choice.effect.seat_delta < 0 ? "text-[#E74C3C]" : "text-[#1BA80E]"}>
                      {choice.effect.seat_delta > 0 ? "+" : ""}{choice.effect.seat_delta} seats
                    </span>
                  )}
                </motion.div>
              </div>
            </div>
          </motion.button>
        ))}
      </motion.div>

      {/* Civics lesson teaser */}
      {event.civics_lesson && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: bodyRevealed ? 1 : 0 }}
          transition={{ delay: 0.5 }}
          className="mt-6 pt-5 border-t border-white/5"
        >
          <p className="text-[11px] text-[var(--text-muted)] uppercase tracking-wider font-semibold mb-1">📚 Civics Insight</p>
          <p className="text-xs text-[var(--text-secondary)] leading-relaxed">{event.civics_lesson}</p>
        </motion.div>
      )}
    </motion.div>
  );
}
