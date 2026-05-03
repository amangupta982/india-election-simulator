"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { useGameStore } from "@/store/gameStore";
import { startGame } from "@/lib/api";

const ROLES = [
  { id: "party_leader", icon: "👑", name: "Party Leader", desc: "You ARE the party. Every decision, every alliance, every rally — it all flows through you. Maximum control, maximum pressure.", color: "#FF6B2B" },
  { id: "campaign_manager", icon: "📊", name: "Campaign Manager", desc: "The strategist behind the scenes. You manage the budget, booth agents, and media narrative. The party leader trusts you completely.", color: "#00BCD4" },
  { id: "swing_voter", icon: "🗳️", name: "Swing Voter", desc: "You represent millions of undecided voters. Watch both sides campaign and decide who deserves your mandate. A unique perspective.", color: "#1BA80E" },
  { id: "election_commission", icon: "⚖️", name: "Election Commission", desc: "Ensure free and fair elections. Handle EVM controversies, model code violations, and voter fraud. The guardian of democracy.", color: "#9C88FF" },
];

const PARTIES = [
  { name: "Bharatiya Janata Party", short: "BJP", color: "#ff9933", seats: 248, icon: "🪷" },
  { name: "Indian National Congress", short: "INC", color: "#00bcd4", seats: 100, icon: "✋" },
  { name: "Samajwadi Party", short: "SP", color: "#e60000", seats: 37, icon: "🚲" },
  { name: "All India Trinamool Congress", short: "TMC", color: "#00a651", seats: 29, icon: "🌸" },
  { name: "Dravida Munnetra Kazhagam", short: "DMK", color: "#cc0000", seats: 22, icon: "☀️" },
];

const DIFFICULTIES = [
  { id: "easy", label: "Rookie Neta", desc: "Forgiving AI, +30% effect bonus", icon: "🟢" },
  { id: "normal", label: "Seasoned Leader", desc: "Balanced challenge", icon: "🟡" },
  { id: "hard", label: "Master Strategist", desc: "Aggressive opponent, -30% effect", icon: "🟠" },
  { id: "expert", label: "Chanakya Mode", desc: "Brutal AI, razor-thin margins", icon: "🔴" },
];

const pageVariants = {
  enter: { opacity: 0, x: 60, scale: 0.98 },
  center: { opacity: 1, x: 0, scale: 1 },
  exit: { opacity: 0, x: -60, scale: 0.98 },
};

export default function RoleSelectPage() {
  const router = useRouter();
  const { token, setGameState, addSeatSnapshot } = useGameStore();
  const [selectedRole, setSelectedRole] = useState("");
  const [selectedParty, setSelectedParty] = useState("");
  const [difficulty, setDifficulty] = useState("normal");
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState(1);

  const handleStart = async () => {
    if (!token || !selectedParty || !selectedRole) return;
    setLoading(true);
    try {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const data: any = await startGame(token, selectedParty, selectedRole, difficulty);
      setGameState(data.initial_state);
      addSeatSnapshot(0, data.initial_state.seat_projection_you, data.initial_state.seat_projection_opp);
      router.push("/war-room");
    } catch (err) {
      console.error(err);
      alert("Failed to start game. Make sure the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  if (!token) {
    router.push("/login");
    return null;
  }

  return (
    <main className="min-h-screen px-4 py-12 max-w-5xl mx-auto">
      {/* Progress steps */}
      <div className="flex items-center justify-center gap-3 mb-14">
        {[
          { n: 1, label: "Role" },
          { n: 2, label: "Party" },
          { n: 3, label: "Launch" },
        ].map((s) => (
          <div key={s.n} className="flex items-center gap-3">
            <motion.div
              animate={{ scale: step === s.n ? 1.15 : 1 }}
              className={`w-10 h-10 rounded-full flex flex-col items-center justify-center text-sm font-bold transition-all duration-300 ${
                step >= s.n ? "bg-gradient-to-br from-[#FF6B2B] to-[#FF9933] text-white shadow-[0_0_20px_rgba(255,107,43,0.3)]" : "bg-white/5 text-[#3E4260]"
              }`}
            >
              {step > s.n ? "✓" : s.n}
            </motion.div>
            {s.n < 3 && (
              <motion.div
                className={`w-16 h-[2px] rounded-full ${step > s.n ? "bg-[#FF6B2B]" : "bg-white/8"}`}
                animate={{ scaleX: step > s.n ? 1 : 0.5 }}
                style={{ transformOrigin: "left" }}
              />
            )}
          </div>
        ))}
      </div>

      <AnimatePresence mode="wait">
        {/* Step 1: Role */}
        {step === 1 && (
          <motion.div key="step1" variants={pageVariants} initial="enter" animate="center" exit="exit" transition={{ duration: 0.4, ease: "easeOut" }}>
            <h1 className="font-[family-name:var(--font-outfit)] text-4xl font-bold text-center mb-2">Choose Your Role</h1>
            <p className="text-center text-[var(--text-secondary)] mb-10">How will you experience Indian democracy?</p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {ROLES.map((role, i) => (
                <motion.button
                  key={role.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.08 }}
                  whileHover={{ scale: 1.025, y: -4 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => { setSelectedRole(role.id); setStep(2); }}
                  className={`glass-card p-7 text-left transition-all relative overflow-hidden ${
                    selectedRole === role.id ? "border-[#ff9933]/40 shadow-[0_0_40px_rgba(255,153,51,0.12)]" : "hover:border-white/8"
                  }`}
                >
                  <div className="absolute top-0 left-0 w-full h-[2px]" style={{ background: `linear-gradient(90deg, transparent, ${role.color}40, transparent)` }} />
                  <motion.div className="text-4xl mb-4" whileHover={{ scale: 1.2, rotate: 10 }} transition={{ type: "spring" }}>{role.icon}</motion.div>
                  <h3 className="font-[family-name:var(--font-outfit)] text-xl font-semibold mb-2">{role.name}</h3>
                  <p className="text-sm text-[var(--text-secondary)] leading-relaxed">{role.desc}</p>
                </motion.button>
              ))}
            </div>
          </motion.div>
        )}

        {/* Step 2: Party */}
        {step === 2 && (
          <motion.div key="step2" variants={pageVariants} initial="enter" animate="center" exit="exit" transition={{ duration: 0.4, ease: "easeOut" }}>
            <h1 className="font-[family-name:var(--font-outfit)] text-4xl font-bold text-center mb-2">Pick Your Party</h1>
            <p className="text-center text-[var(--text-secondary)] mb-10">Based on real 2024 election results</p>
            <div className="space-y-3 max-w-2xl mx-auto">
              {PARTIES.map((party, i) => (
                <motion.button
                  key={party.name}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.06 }}
                  whileHover={{ scale: 1.015, x: 6 }}
                  whileTap={{ scale: 0.99 }}
                  onClick={() => { setSelectedParty(party.name); setStep(3); }}
                  className={`glass-card p-5 w-full text-left flex items-center gap-4 transition-all relative overflow-hidden ${
                    selectedParty === party.name ? "border-[#ff9933]/40" : "hover:border-white/8"
                  }`}
                >
                  <div className="absolute left-0 top-0 bottom-0 w-[3px] rounded-l-xl" style={{ background: party.color }} />
                  <span className="text-3xl">{party.icon}</span>
                  <div className="flex-1">
                    <h3 className="font-semibold">{party.name}</h3>
                    <p className="text-sm text-[var(--text-secondary)]">{party.short} • Won {party.seats} seats in 2024</p>
                  </div>
                  <div className="w-28 h-3 bg-white/5 rounded-full overflow-hidden">
                    <motion.div
                      className="h-full rounded-full"
                      initial={{ width: 0 }}
                      animate={{ width: `${(party.seats / 543) * 100}%` }}
                      transition={{ delay: 0.3 + i * 0.06, duration: 0.8 }}
                      style={{ background: party.color }}
                    />
                  </div>
                </motion.button>
              ))}
            </div>
            <button onClick={() => setStep(1)} className="mt-8 text-sm text-[var(--text-secondary)] hover:text-[#ff9933] mx-auto block transition-colors">← Back to role</button>
          </motion.div>
        )}

        {/* Step 3: Difficulty + Launch */}
        {step === 3 && (
          <motion.div key="step3" variants={pageVariants} initial="enter" animate="center" exit="exit" transition={{ duration: 0.4, ease: "easeOut" }} className="max-w-2xl mx-auto">
            <h1 className="font-[family-name:var(--font-outfit)] text-4xl font-bold text-center mb-2">Set Difficulty</h1>
            <p className="text-center text-[var(--text-secondary)] mb-10">How tough should the opposition be?</p>
            <div className="grid grid-cols-2 gap-3 mb-10">
              {DIFFICULTIES.map((d, i) => (
                <motion.button
                  key={d.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.05 }}
                  whileHover={{ scale: 1.03 }}
                  onClick={() => setDifficulty(d.id)}
                  className={`glass-card-sm p-5 text-left transition-all ${
                    difficulty === d.id ? "border-[#ff9933]/40 bg-[#ff9933]/5 shadow-[0_0_20px_rgba(255,107,43,0.08)]" : "hover:border-white/8"
                  }`}
                >
                  <div className="flex items-center gap-2 mb-1">
                    <span>{d.icon}</span>
                    <h4 className="font-semibold text-sm">{d.label}</h4>
                  </div>
                  <p className="text-xs text-[var(--text-secondary)]">{d.desc}</p>
                </motion.button>
              ))}
            </div>

            {/* Summary */}
            <motion.div
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="glass-card p-7 mb-8 relative overflow-hidden"
            >
              <div className="absolute top-0 left-0 w-full h-[2px] bg-gradient-to-r from-[#FF6B2B] via-[#FF9933] to-[#138808]" />
              <h3 className="text-xs text-[var(--text-muted)] mb-4 uppercase tracking-[0.15em] font-bold">Campaign Briefing</h3>
              <div className="space-y-3 text-sm">
                <div className="flex justify-between"><span className="text-[var(--text-secondary)]">Role</span><span className="font-medium">{ROLES.find((r) => r.id === selectedRole)?.name}</span></div>
                <div className="flex justify-between"><span className="text-[var(--text-secondary)]">Party</span><span className="font-medium">{PARTIES.find((p) => p.name === selectedParty)?.short}</span></div>
                <div className="flex justify-between"><span className="text-[var(--text-secondary)]">Difficulty</span><span className="font-medium">{DIFFICULTIES.find((d) => d.id === difficulty)?.label}</span></div>
                <div className="flex justify-between"><span className="text-[var(--text-secondary)]">Campaign Length</span><span className="font-medium">8 weeks</span></div>
                <div className="flex justify-between"><span className="text-[var(--text-secondary)]">Starting Budget</span><span className="font-medium">₹500 crore</span></div>
                <div className="flex justify-between"><span className="text-[var(--text-secondary)]">Target</span><span className="text-[#ff9933] font-bold">272 / 543 seats</span></div>
              </div>
            </motion.div>

            <motion.button
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.97 }}
              onClick={handleStart}
              disabled={loading}
              className="btn-saffron w-full py-5 text-lg rounded-xl disabled:opacity-50"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Initializing Campaign...
                </span>
              ) : "🚀 Launch Campaign"}
            </motion.button>
            <button onClick={() => setStep(2)} className="mt-5 text-sm text-[var(--text-secondary)] hover:text-[#ff9933] mx-auto block transition-colors">← Back</button>
          </motion.div>
        )}
      </AnimatePresence>
    </main>
  );
}
