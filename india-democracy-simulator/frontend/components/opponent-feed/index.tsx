"use client";

import { motion, AnimatePresence } from "framer-motion";
import { OpponentMove } from "@/store/gameStore";

const MOVE_ICONS: Record<string, string> = {
  counter_rally: "📢",
  attack_ad: "💢",
  poach_alliance: "🤝",
  oppo_research: "🔍",
  pm_event: "🎤",
  booth_agent_deploy: "🗳️",
};

const MOVE_COLORS: Record<string, string> = {
  counter_rally: "#E74C3C",
  attack_ad: "#FF4757",
  poach_alliance: "#FFA502",
  oppo_research: "#9C88FF",
  pm_event: "#E74C3C",
  booth_agent_deploy: "#FF6B2B",
};

export function OpponentFeed({ moves }: { moves: OpponentMove[] }) {
  const displayMoves = [...moves].reverse().slice(0, 5);

  return (
    <div className="glass-card-sm h-full flex flex-col overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-white/5 bg-[#080C18]/80 rounded-t-[16px] flex-shrink-0">
        <h3 className="font-[family-name:var(--font-outfit)] text-xs font-bold flex items-center gap-2 text-[#E74C3C] uppercase tracking-wider">
          <span className="relative flex h-2.5 w-2.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75" />
            <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-red-500" />
          </span>
          Opposition Intel Feed
        </h3>
      </div>

      {/* Feed */}
      <div className="flex-1 overflow-y-auto p-3 space-y-3">
        {displayMoves.length === 0 ? (
          <div className="flex-1 flex flex-col items-center justify-center h-full py-10">
            <motion.div
              animate={{ opacity: [0.3, 0.7, 0.3] }}
              transition={{ repeat: Infinity, duration: 2 }}
              className="text-3xl mb-3"
            >
              🛰️
            </motion.div>
            <p className="text-xs text-[var(--text-muted)] text-center italic">
              Scanning for opposition intel...
            </p>
            <div className="mt-3 flex gap-1">
              {[0, 1, 2].map(i => (
                <motion.div
                  key={i}
                  className="w-1.5 h-1.5 rounded-full bg-red-500/40"
                  animate={{ opacity: [0.2, 1, 0.2] }}
                  transition={{ repeat: Infinity, duration: 1.2, delay: i * 0.3 }}
                />
              ))}
            </div>
          </div>
        ) : (
          <AnimatePresence>
            {displayMoves.map((move, i) => {
              const icon = MOVE_ICONS[move.move_type] || "⚡";
              const color = MOVE_COLORS[move.move_type] || "#E74C3C";
              return (
                <motion.div
                  key={`${move.id}-${i}`}
                  initial={{ opacity: 0, x: 30, scale: 0.9 }}
                  animate={{ opacity: 1, x: 0, scale: 1 }}
                  exit={{ opacity: 0, x: -20 }}
                  transition={{ delay: i * 0.06, type: "spring", stiffness: 200, damping: 20 }}
                  className="bg-[#080C18] border border-red-500/8 rounded-xl p-4 relative overflow-hidden group hover:border-red-500/20 transition-all duration-300"
                >
                  {/* Left accent bar */}
                  <div
                    className="absolute left-0 top-0 bottom-0 w-[3px] rounded-l-xl"
                    style={{ background: `linear-gradient(to bottom, ${color}90, ${color}30)` }}
                  />

                  {/* Hover shimmer */}
                  <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/[0.01] to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

                  {/* Meta */}
                  <div className="text-[10px] text-[var(--text-muted)] mb-2 flex justify-between items-center pl-2">
                    <span className="flex items-center gap-1.5">
                      <span>{icon}</span>
                      <span className="uppercase font-semibold tracking-wider" style={{ color: `${color}CC` }}>
                        {move.move_type.replace(/_/g, " ")}
                      </span>
                    </span>
                    <span className="text-[var(--text-muted)] font-mono text-[9px] bg-white/[0.03] px-1.5 py-0.5 rounded">W{move.week_number}</span>
                  </div>

                  {/* Headline */}
                  <p className="text-sm font-medium text-white/85 leading-snug pl-2">
                    {move.headline}
                  </p>

                  {/* Target states */}
                  {move.target_states && move.target_states.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 mt-2.5 pl-2">
                      {move.target_states.map((state) => (
                        <span key={state} className="text-[9px] px-2 py-0.5 rounded-md border" style={{ color: `${color}99`, background: `${color}08`, borderColor: `${color}15` }}>
                          {state}
                        </span>
                      ))}
                    </div>
                  )}
                </motion.div>
              );
            })}
          </AnimatePresence>
        )}
      </div>
    </div>
  );
}
