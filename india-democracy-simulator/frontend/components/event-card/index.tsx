"use client";

import { motion } from "framer-motion";
import { GameEvent } from "@/store/gameStore";

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

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95, y: 10 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      className="glass-card-glow p-8 relative overflow-hidden"
    >
      {/* Top gradient accent */}
      <div className="absolute top-0 left-0 w-full h-[3px] bg-gradient-to-r from-[#FF6B2B] via-[#FF9933] to-[#FF6B2B]" />
      
      {/* Ambient glow */}
      <div className="absolute -top-20 -right-20 w-40 h-40 rounded-full bg-[#FF6B2B]/[0.04] blur-[60px] pointer-events-none" />

      {/* Header */}
      <div className="flex justify-between items-start mb-5">
        <div className="flex items-center gap-3">
          <span className="text-2xl">{icon}</span>
          <span className={badgeClass}>
            {event.event_type.replace("_", " ")}
          </span>
        </div>
        {event.affected_states && event.affected_states.length > 0 && (
          <span className="text-xs text-[var(--text-muted)] bg-white/[0.03] px-3 py-1.5 rounded-lg border border-white/5">
            📍 {event.affected_states.join(", ")}
          </span>
        )}
      </div>

      {/* Headline */}
      <h2 className="font-[family-name:var(--font-outfit)] text-2xl md:text-[26px] font-bold mb-4 leading-snug text-white">
        {event.headline}
      </h2>
      
      {/* Body */}
      <p className="text-[var(--text-secondary)] mb-8 leading-relaxed text-[15px]">
        {event.body}
      </p>

      {/* Choices */}
      <div className="space-y-3">
        {event.choices.map((choice, idx) => (
          <motion.button
            key={idx}
            whileHover={!disabled ? { scale: 1.01, x: 4 } : {}}
            whileTap={!disabled ? { scale: 0.99 } : {}}
            onClick={() => onChoiceSelect(idx)}
            disabled={disabled}
            className={`choice-btn ${disabled ? "opacity-40 cursor-not-allowed" : ""}`}
          >
            <div className="flex items-start gap-3">
              <span className="w-7 h-7 rounded-lg bg-[#FF6B2B]/10 text-[#FF6B2B] flex items-center justify-center text-sm font-bold flex-shrink-0 mt-0.5">
                {idx + 1}
              </span>
              <div className="flex-1">
                <span className="font-semibold text-[15px] leading-snug">{choice.text}</span>
                {/* Effect preview on hover */}
                <div className="flex gap-3 mt-2 text-[11px]">
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
                </div>
              </div>
            </div>
          </motion.button>
        ))}
      </div>

      {/* Civics lesson teaser */}
      {event.civics_lesson && (
        <div className="mt-6 pt-5 border-t border-white/5">
          <p className="text-[11px] text-[var(--text-muted)] uppercase tracking-wider font-semibold mb-1">📚 Civics Insight</p>
          <p className="text-xs text-[var(--text-secondary)] leading-relaxed">{event.civics_lesson}</p>
        </div>
      )}
    </motion.div>
  );
}
