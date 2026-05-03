"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { useGameStore } from "@/store/gameStore";
import { getPostMortem } from "@/lib/api";
import SeatTallyBar from "@/components/seat-tally";

export default function ResultsPage() {
  const router = useRouter();
  const { token, gameState, seatHistory } = useGameStore();
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [postMortem, setPostMortem] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [revealStep, setRevealStep] = useState(0);

  useEffect(() => {
    if (!token || !gameState) {
      router.push("/");
      return;
    }
    const fetchResults = async () => {
      try {
        const data = await getPostMortem(token, gameState.session_id);
        setPostMortem(data);
        // Dramatic reveal sequence
        setTimeout(() => setRevealStep(1), 500);
        setTimeout(() => setRevealStep(2), 1500);
        setTimeout(() => setRevealStep(3), 2500);
      } catch (err) {
        console.error(err);
        setLoading(false);
      }
    };
    fetchResults();
  }, [token, gameState, router]);

  if (!postMortem && loading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center">
        <motion.div
          animate={{ scale: [1, 1.15, 1] }}
          transition={{ repeat: Infinity, duration: 1.5 }}
          className="text-5xl mb-8"
        >
          🗳️
        </motion.div>
        <div className="font-[family-name:var(--font-outfit)] text-2xl font-bold mb-4">Counting votes...</div>
        <div className="w-72 h-2.5 bg-white/5 rounded-full overflow-hidden">
          <motion.div
            initial={{ width: "5%" }}
            animate={{ width: "95%" }}
            transition={{ duration: 3, ease: "easeInOut" }}
            className="h-full bg-gradient-to-r from-[#FF6B2B] to-[#FF9933] rounded-full"
          />
        </div>
        <p className="text-xs text-[var(--text-muted)] mt-4">Tallying 543 constituencies...</p>
      </div>
    );
  }

  if (!postMortem) return null;

  const won = postMortem.won_majority;

  return (
    <main className="min-h-screen pt-12 pb-24 px-4 max-w-4xl mx-auto relative">
      {/* Background glow based on win/loss */}
      <div className={`absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] rounded-full blur-[200px] pointer-events-none ${
        won ? "bg-[#138808]/[0.06]" : "bg-[#C0392B]/[0.06]"
      }`} />

      {/* ═══ Verdict ═══ */}
      <motion.div
        initial={{ opacity: 0, y: 40, scale: 0.9 }}
        animate={revealStep >= 1 ? { opacity: 1, y: 0, scale: 1 } : {}}
        transition={{ duration: 0.8, ease: "easeOut" }}
        className="text-center mb-14 relative"
      >
        <motion.div
          initial={{ scale: 0, rotate: -90 }}
          animate={revealStep >= 1 ? { scale: 1, rotate: 0 } : {}}
          transition={{ delay: 0.2, duration: 0.6, type: "spring" }}
          className="text-7xl mb-6 inline-block"
        >
          {won ? "🏆" : "📉"}
        </motion.div>
        <h1 className="font-[family-name:var(--font-outfit)] text-6xl md:text-7xl font-extrabold mb-4">
          <span className={won ? "text-[#1BA80E]" : "text-[#E74C3C]"}>
            {won ? "Victory!" : "Defeat."}
          </span>
        </h1>
        <p className="text-xl text-[var(--text-secondary)]">
          {postMortem.player_party} secured{" "}
          <span className={`font-bold ${won ? "text-[#1BA80E]" : "text-[#E74C3C]"}`}>
            {postMortem.final_seats_you}
          </span>{" "}
          seats
          {won ? " — crossing the 272 majority mark!" : ` — needed ${272 - postMortem.final_seats_you} more for majority.`}
        </p>
      </motion.div>

      {/* ═══ Seat Tally ═══ */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={revealStep >= 2 ? { opacity: 1, y: 0 } : {}}
        className="mb-16"
      >
        <SeatTallyBar />
      </motion.div>

      {/* ═══ Key Numbers ═══ */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={revealStep >= 2 ? { opacity: 1, y: 0 } : {}}
        transition={{ delay: 0.2 }}
        className="grid grid-cols-3 gap-4 mb-16"
      >
        <div className="glass-card-sm p-6 text-center">
          <div className="text-[10px] text-[var(--text-muted)] uppercase tracking-wider font-semibold mb-2">Your Seats</div>
          <div className="font-[family-name:var(--font-outfit)] text-4xl font-extrabold text-[#FF6B2B]">
            {postMortem.final_seats_you}
          </div>
        </div>
        <div className="glass-card-sm p-6 text-center">
          <div className="text-[10px] text-[var(--text-muted)] uppercase tracking-wider font-semibold mb-2">Opposition</div>
          <div className="font-[family-name:var(--font-outfit)] text-4xl font-extrabold text-[#00BCD4]">
            {postMortem.final_seats_opp}
          </div>
        </div>
        <div className="glass-card-sm p-6 text-center">
          <div className="text-[10px] text-[var(--text-muted)] uppercase tracking-wider font-semibold mb-2">Margin</div>
          <div className={`font-[family-name:var(--font-outfit)] text-4xl font-extrabold ${won ? "text-[#1BA80E]" : "text-[#E74C3C]"}`}>
            {won ? "+" : ""}{postMortem.final_seats_you - 272}
          </div>
        </div>
      </motion.div>

      {/* ═══ Post-Mortem Sections ═══ */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={revealStep >= 3 ? { opacity: 1 } : {}}
      >
        <h2 className="text-[10px] text-[var(--text-muted)] uppercase tracking-[0.2em] font-bold mb-6">
          📰 Election Post-Mortem
        </h2>
        <div className="space-y-6">
          {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
          {postMortem.sections.map((section: any, idx: number) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: idx * 0.15 }}
              className="glass-card p-8 relative overflow-hidden group"
            >
              {/* Left accent */}
              <div className={`absolute left-0 top-0 bottom-0 w-1 rounded-l-xl ${
                won ? "bg-gradient-to-b from-[#1BA80E] to-[#138808]/30" : "bg-gradient-to-b from-[#E74C3C] to-[#C0392B]/30"
              }`} />
              
              <h3 className="font-[family-name:var(--font-outfit)] text-[10px] font-bold tracking-[0.15em] text-[var(--text-muted)] uppercase mb-4 pl-4">
                {section.title}
              </h3>
              
              <div className="text-base leading-relaxed text-white/85 mb-6 pl-4">
                {section.content}
              </div>

              {section.civics_principles && section.civics_principles.length > 0 && (
                <div className="bg-[var(--bg-base)] rounded-xl p-5 border border-white/5 ml-4">
                  <div className="text-[10px] text-[#FF6B2B] font-bold mb-2 uppercase tracking-wider flex items-center gap-1.5">
                    📚 Civics Insight
                  </div>
                  <ul className="space-y-1.5">
                    {section.civics_principles.map((principle: string, i: number) => (
                      <li key={i} className="text-sm text-[var(--text-secondary)] flex items-start gap-2">
                        <span className="text-[#FF6B2B] mt-1 text-[8px]">●</span>
                        {principle}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* ═══ Actions ═══ */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={revealStep >= 3 ? { opacity: 1, y: 0 } : {}}
        transition={{ delay: 0.5 }}
        className="mt-16 flex justify-center gap-4"
      >
        <button
          onClick={() => router.push("/role-select")}
          className="btn-saffron text-base"
        >
          Play Again →
        </button>
        <button
          onClick={() => router.push("/leaderboard")}
          className="btn-ghost"
        >
          View Leaderboard
        </button>
      </motion.div>
    </main>
  );
}
