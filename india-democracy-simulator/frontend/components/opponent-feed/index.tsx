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

export function OpponentFeed({ moves }: { moves: OpponentMove[] }) {
  const displayMoves = [...moves].reverse().slice(0, 5);

  return (
    <div className="glass-card-sm h-full flex flex-col overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-white/5 bg-[#0D1225]/80 rounded-t-[14px] flex-shrink-0">
        <h3 className="font-[family-name:var(--font-outfit)] text-xs font-bold flex items-center gap-2 text-[#E74C3C] uppercase tracking-wider">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75" />
            <span className="relative inline-flex rounded-full h-2 w-2 bg-red-500" />
          </span>
          Opposition Intel
        </h3>
      </div>
      
      {/* Feed */}
      <div className="flex-1 overflow-y-auto p-3 space-y-3">
        {displayMoves.length === 0 ? (
          <div className="flex-1 flex items-center justify-center h-full">
            <p className="text-xs text-[var(--text-muted)] text-center italic py-10">
              Waiting for opposition intel...
            </p>
          </div>
        ) : (
          <AnimatePresence>
            {displayMoves.map((move, i) => {
              const icon = MOVE_ICONS[move.move_type] || "⚡";
              return (
                <motion.div
                  key={`${move.id}-${i}`}
                  initial={{ opacity: 0, x: 20, scale: 0.95 }}
                  animate={{ opacity: 1, x: 0, scale: 1 }}
                  transition={{ delay: i * 0.05 }}
                  className="bg-[#0D1225] border border-red-500/10 rounded-xl p-3.5 relative overflow-hidden group hover:border-red-500/25 transition-all"
                >
                  {/* Left accent bar */}
                  <div className="absolute left-0 top-0 bottom-0 w-[3px] bg-gradient-to-b from-red-500/60 to-red-800/30 rounded-l-xl" />
                  
                  {/* Meta */}
                  <div className="text-[10px] text-[var(--text-muted)] mb-2 flex justify-between items-center pl-2">
                    <span className="flex items-center gap-1.5">
                      <span>{icon}</span>
                      <span className="uppercase font-semibold tracking-wider">
                        {move.move_type.replace(/_/g, " ")}
                      </span>
                    </span>
                    <span className="text-[var(--text-muted)] font-mono">W{move.week_number}</span>
                  </div>
                  
                  {/* Headline */}
                  <p className="text-sm font-medium text-white/85 leading-snug pl-2">
                    {move.headline}
                  </p>
                  
                  {/* Target states */}
                  {move.target_states && move.target_states.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-2 pl-2">
                      {move.target_states.map((state) => (
                        <span key={state} className="text-[9px] text-red-400/70 bg-red-400/5 px-1.5 py-0.5 rounded">
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
