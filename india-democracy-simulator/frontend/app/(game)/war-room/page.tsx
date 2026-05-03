"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { useGameStore } from "@/store/gameStore";
import { submitDecision } from "@/lib/api";
import SeatTallyBar from "@/components/seat-tally";
import { EventCard } from "@/components/event-card";
import { OpponentFeed } from "@/components/opponent-feed";

function StatCard({ label, value, color, icon, subtitle }: {
  label: string; value: string; color: string; icon: string; subtitle?: string;
}) {
  return (
    <div className="glass-card-sm px-5 py-4 flex items-center gap-3 group hover:border-white/10 transition-all min-w-0">
      <div className="w-10 h-10 rounded-xl flex items-center justify-center text-lg flex-shrink-0"
        style={{ background: `${color}15`, border: `1px solid ${color}25` }}>
        {icon}
      </div>
      <div className="min-w-0">
        <div className="text-[10px] text-[var(--text-muted)] uppercase tracking-wider font-semibold">{label}</div>
        <div className="font-[family-name:var(--font-outfit)] text-xl font-extrabold" style={{ color }}>
          {value}
        </div>
        {subtitle && <div className="text-[10px] text-[var(--text-muted)]">{subtitle}</div>}
      </div>
    </div>
  );
}

function WeekProgress({ current, total }: { current: number; total: number }) {
  return (
    <div className="flex items-center gap-1.5">
      {Array.from({ length: total }).map((_, i) => (
        <div
          key={i}
          className={`week-dot ${i + 1 < current ? "completed" : i + 1 === current ? "active" : ""}`}
        />
      ))}
    </div>
  );
}

export default function WarRoomPage() {
  const router = useRouter();
  const { token, gameState, setGameState, addEvent, addOpponentMove, addSeatSnapshot, addCivicsLesson } = useGameStore();
  const [loading, setLoading] = useState(false);
  const [showEffects, setShowEffects] = useState<string | null>(null);

  useEffect(() => {
    if (!token) { router.push("/login"); return; }
    if (!gameState) { router.push("/role-select"); return; }
  }, [token, gameState, router]);

  const handleDecision = async (choiceIndex: number) => {
    if (!token || !gameState || !gameState.current_event) return;
    setLoading(true);
    try {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const result: any = await submitDecision(
        token, gameState.session_id, gameState.current_event.id, choiceIndex
      );

      const seatDelta = result.effects_applied.seat_delta;
      if (seatDelta !== 0) {
        setShowEffects(seatDelta > 0 ? `+${seatDelta} Seats` : `${seatDelta} Seats`);
        setTimeout(() => setShowEffects(null), 3000);
      }

      if (gameState.current_event) addEvent(gameState.current_event);
      if (result.opponent_move) addOpponentMove(result.opponent_move);
      if (result.civics_lesson) addCivicsLesson(result.civics_lesson);
      addSeatSnapshot(result.new_state.week_number, result.new_state.seat_projection_you, result.new_state.seat_projection_opp);
      setGameState(result.new_state);

      if (result.new_state.status === "completed" || (result.new_state.week_number >= 8 && !result.new_state.current_event)) {
        setTimeout(() => router.push("/results"), 2000);
      }
    } catch (err) {
      console.error(err);
      alert("Failed to submit decision");
    } finally {
      setLoading(false);
    }
  };

  if (!gameState) return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="w-10 h-10 border-3 border-[#FF6B2B]/30 border-t-[#FF6B2B] rounded-full animate-spin" />
    </div>
  );

  const approvalColor = gameState.approval_rating > 55 ? "#1BA80E" : gameState.approval_rating > 35 ? "#FF9933" : "#E74C3C";
  const winColor = gameState.win_probability > 0.55 ? "#1BA80E" : gameState.win_probability > 0.35 ? "#FF9933" : "#E74C3C";

  return (
    <main className="min-h-screen flex flex-col max-w-[1440px] mx-auto">
      {/* ═══ Top Nav Bar ═══ */}
      <header className="px-6 py-4 border-b border-white/5 flex justify-between items-center flex-shrink-0 bg-[var(--bg-base)]/80 backdrop-blur-xl sticky top-0 z-30">
        <div className="flex items-center gap-4">
          <div>
            <h1 className="font-[family-name:var(--font-outfit)] text-xl font-bold text-white flex items-center gap-2">
              <span className="text-[#FF6B2B]">⚡</span> War Room
            </h1>
            <div className="flex items-center gap-3 mt-0.5">
              <span className="text-[10px] text-[var(--text-muted)] uppercase tracking-wider">
                {gameState.player_party} • {gameState.role.replace(/_/g, " ")}
              </span>
            </div>
          </div>
        </div>

        <WeekProgress current={gameState.week_number} total={8} />

        <div className="text-right">
          <span className="text-[10px] text-[var(--text-muted)] uppercase tracking-wider">Week</span>
          <div className="font-[family-name:var(--font-outfit)] text-2xl font-extrabold text-white">
            {gameState.week_number}<span className="text-[var(--text-muted)] text-lg">/8</span>
          </div>
        </div>
      </header>

      {/* ═══ Stats Row ═══ */}
      <div className="px-6 py-4 grid grid-cols-2 md:grid-cols-4 gap-3 flex-shrink-0">
        <StatCard label="Campaign Budget" value={`₹${gameState.budget_remaining}Cr`} color="#00BCD4" icon="💰" />
        <StatCard label="Approval Rating" value={`${Math.round(gameState.approval_rating)}%`} color={approvalColor} icon="📊" />
        <StatCard label="Win Probability" value={`${Math.round(gameState.win_probability * 100)}%`} color={winColor} icon="🎯" />
        <StatCard label="Decisions Made" value={`${gameState.decisions_made}`} color="#9C88FF" icon="📝" subtitle={`of ${gameState.total_weeks} weeks`} />
      </div>

      {/* ═══ Seat Tally ═══ */}
      <div className="px-6 pb-4 flex-shrink-0">
        <SeatTallyBar />
      </div>

      {/* ═══ Main Content Grid ═══ */}
      <div className="flex-1 px-6 pb-6 grid grid-cols-1 lg:grid-cols-[1fr_360px] gap-6 min-h-0">
        {/* Event Area */}
        <div className="flex flex-col relative min-h-0">
          <AnimatePresence mode="wait">
            {gameState.current_event ? (
              <motion.div
                key={gameState.current_event.id}
                initial={{ opacity: 0, x: -40 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 40 }}
                transition={{ duration: 0.5, ease: "easeOut" }}
                className="flex-1 flex items-start justify-center overflow-y-auto pt-2"
              >
                <div className="w-full max-w-2xl">
                  <EventCard
                    event={gameState.current_event}
                    onChoiceSelect={handleDecision}
                    disabled={loading}
                  />
                </div>
              </motion.div>
            ) : (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex-1 flex items-center justify-center"
              >
                <div className="text-center">
                  <motion.div
                    animate={{ scale: [1, 1.1, 1] }}
                    transition={{ repeat: Infinity, duration: 2 }}
                    className="text-6xl mb-6"
                  >
                    🗳️
                  </motion.div>
                  <h2 className="font-[family-name:var(--font-outfit)] text-3xl font-bold mb-3">
                    Election Day
                  </h2>
                  <p className="text-[var(--text-secondary)] mb-8">The nation is voting...</p>
                  <div className="w-14 h-14 border-[3px] border-[#FF6B2B]/20 border-t-[#FF6B2B] rounded-full animate-spin mx-auto" />
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Floating effects */}
          <AnimatePresence>
            {showEffects && (
              <motion.div
                initial={{ opacity: 0, y: 0, scale: 0.5 }}
                animate={{ opacity: 1, y: -120, scale: 1.2 }}
                exit={{ opacity: 0, y: -180 }}
                transition={{ duration: 0.6, ease: "easeOut" }}
                className={`absolute top-1/2 left-1/2 -translate-x-1/2 font-[family-name:var(--font-outfit)] text-3xl font-extrabold drop-shadow-lg pointer-events-none z-20 ${
                  showEffects.startsWith("+") ? "text-[#1BA80E]" : "text-[#E74C3C]"
                }`}
              >
                {showEffects}
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Right Sidebar */}
        <div className="flex flex-col gap-4 min-h-0">
          <div className="flex-1 min-h-0 overflow-hidden">
            <OpponentFeed moves={gameState.recent_opponent_moves} />
          </div>
        </div>
      </div>
    </main>
  );
}
