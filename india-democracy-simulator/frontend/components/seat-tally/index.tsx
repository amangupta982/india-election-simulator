"use client";

import { useGameStore } from "@/store/gameStore";
import { motion } from "framer-motion";

export default function SeatTallyBar() {
  const gameState = useGameStore((s) => s.gameState);

  if (!gameState) return null;

  const { player_party, seat_projection_you, seat_projection_opp } = gameState;
  const others = Math.max(0, 543 - seat_projection_you - seat_projection_opp);
  const playerPct = (seat_projection_you / 543) * 100;
  const othersPct = (others / 543) * 100;
  const oppPct = (seat_projection_opp / 543) * 100;
  const majorityPct = (272 / 543) * 100;

  const isWinning = seat_projection_you >= 272;

  return (
    <div className="w-full glass-card-sm p-5">
      {/* Labels */}
      <div className="flex justify-between items-end mb-3">
        <div className="flex flex-col">
          <span className="text-[10px] text-[var(--text-muted)] uppercase tracking-wider font-semibold mb-1">You</span>
          <div className="flex items-baseline gap-2">
            <motion.span
              key={seat_projection_you}
              initial={{ scale: 1.3, color: "#FF6B2B" }}
              animate={{ scale: 1, color: "#FF6B2B" }}
              className="font-[family-name:var(--font-outfit)] text-3xl font-extrabold"
            >
              {seat_projection_you}
            </motion.span>
            <span className="text-xs text-[var(--text-muted)]">{player_party?.split(" ").map(w => w[0]).join("")}</span>
          </div>
        </div>

        <div className="flex flex-col items-center">
          <span className={`text-[10px] font-bold uppercase tracking-wider ${isWinning ? "text-[#1BA80E]" : "text-[var(--text-muted)]"}`}>
            {isWinning ? "✓ Majority" : "Majority 272"}
          </span>
          <div className="w-[1px] h-5 bg-white/20 mt-1" />
        </div>

        <div className="flex flex-col items-end">
          <span className="text-[10px] text-[var(--text-muted)] uppercase tracking-wider font-semibold mb-1">Opposition</span>
          <motion.span
            key={seat_projection_opp}
            initial={{ scale: 1.3 }}
            animate={{ scale: 1 }}
            className="font-[family-name:var(--font-outfit)] text-3xl font-extrabold text-[#00BCD4]"
          >
            {seat_projection_opp}
          </motion.span>
        </div>
      </div>

      {/* Bar */}
      <div className="w-full h-10 bg-white/[0.03] rounded-2xl overflow-hidden flex relative border border-white/5">
        {/* Majority marker */}
        <div
          className="absolute top-0 bottom-0 w-[2px] bg-white/50 z-10"
          style={{ left: `${majorityPct}%` }}
        >
          <div className="absolute -top-1 left-1/2 -translate-x-1/2 w-1.5 h-1.5 rounded-full bg-white shadow-[0_0_6px_rgba(255,255,255,0.8)]" />
        </div>

        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${playerPct}%` }}
          transition={{ duration: 1, ease: "easeOut" }}
          className="h-full seat-bar-fill rounded-l-2xl relative overflow-hidden"
          style={{ background: "linear-gradient(90deg, #FF6B2B, #FF9933)" }}
        >
          <div className="absolute inset-0 bg-gradient-to-b from-white/10 to-transparent" />
        </motion.div>

        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${othersPct}%` }}
          transition={{ duration: 1, delay: 0.2, ease: "easeOut" }}
          className="h-full seat-bar-fill"
          style={{ background: "#2A2E45" }}
        />

        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${oppPct}%` }}
          transition={{ duration: 1, delay: 0.4, ease: "easeOut" }}
          className="h-full seat-bar-fill rounded-r-2xl relative overflow-hidden"
          style={{ background: "linear-gradient(90deg, #00BCD4, #0097A7)" }}
        >
          <div className="absolute inset-0 bg-gradient-to-b from-white/10 to-transparent" />
        </motion.div>
      </div>

      {/* Bottom scale */}
      <div className="flex justify-between text-[10px] text-[var(--text-muted)] mt-2 px-1 font-mono">
        <span>0</span>
        <span>136</span>
        <span className="text-[#FF6B2B]">272</span>
        <span>408</span>
        <span>543</span>
      </div>
    </div>
  );
}
