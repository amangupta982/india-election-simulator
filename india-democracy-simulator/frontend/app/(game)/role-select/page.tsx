"use client";

import { motion } from "framer-motion";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { useGameStore } from "@/store/gameStore";
import { startGame } from "@/lib/api";

const ROLES = [
  { id: "party_leader", icon: "👑", name: "Party Leader", desc: "You ARE the party. Every decision, every alliance, every rally — it all flows through you. Maximum control, maximum pressure." },
  { id: "campaign_manager", icon: "📊", name: "Campaign Manager", desc: "The strategist behind the scenes. You manage the budget, booth agents, and media narrative. The party leader trusts you completely." },
  { id: "swing_voter", icon: "🗳️", name: "Swing Voter", desc: "You represent millions of undecided voters. Watch both sides campaign and decide who deserves your mandate. A unique perspective." },
  { id: "election_commission", icon: "⚖️", name: "Election Commission", desc: "Ensure free and fair elections. Handle EVM controversies, model code violations, and voter fraud. The guardian of democracy." },
];

const PARTIES = [
  { name: "Bharatiya Janata Party", short: "BJP", color: "#ff9933", seats: 248, icon: "🪷" },
  { name: "Indian National Congress", short: "INC", color: "#00bcd4", seats: 100, icon: "✋" },
  { name: "Samajwadi Party", short: "SP", color: "#e60000", seats: 37, icon: "🚲" },
  { name: "All India Trinamool Congress", short: "TMC", color: "#00a651", seats: 29, icon: "🌸" },
  { name: "Dravida Munnetra Kazhagam", short: "DMK", color: "#cc0000", seats: 22, icon: "☀️" },
];

const DIFFICULTIES = [
  { id: "easy", label: "Rookie Neta", desc: "Forgiving AI, +30% effect bonus" },
  { id: "normal", label: "Seasoned Leader", desc: "Balanced challenge" },
  { id: "hard", label: "Master Strategist", desc: "Aggressive opponent, -30% effect" },
  { id: "expert", label: "Chanakya Mode", desc: "Brutal AI, razor-thin margins" },
];

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
      <div className="flex items-center justify-center gap-2 mb-12">
        {[1, 2, 3].map((s) => (
          <div key={s} className="flex items-center gap-2">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold transition-all ${
              step >= s ? "bg-[#ff9933] text-white" : "bg-white/5 text-[#555577]"
            }`}>
              {s}
            </div>
            {s < 3 && <div className={`w-12 h-0.5 ${step > s ? "bg-[#ff9933]" : "bg-white/10"}`} />}
          </div>
        ))}
      </div>

      {/* Step 1: Role */}
      {step === 1 && (
        <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }}>
          <h1 className="font-[family-name:var(--font-outfit)] text-3xl font-bold text-center mb-2">Choose Your Role</h1>
          <p className="text-center text-[#8888aa] mb-8">How will you experience Indian democracy?</p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {ROLES.map((role) => (
              <motion.button
                key={role.id}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => { setSelectedRole(role.id); setStep(2); }}
                className={`glass-card p-6 text-left transition-all ${
                  selectedRole === role.id ? "border-[#ff9933]/50 shadow-[0_0_30px_rgba(255,153,51,0.15)]" : "hover:border-white/10"
                }`}
              >
                <div className="text-4xl mb-3">{role.icon}</div>
                <h3 className="font-[family-name:var(--font-outfit)] text-xl font-semibold mb-2">{role.name}</h3>
                <p className="text-sm text-[#8888aa]">{role.desc}</p>
              </motion.button>
            ))}
          </div>
        </motion.div>
      )}

      {/* Step 2: Party */}
      {step === 2 && (
        <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }}>
          <h1 className="font-[family-name:var(--font-outfit)] text-3xl font-bold text-center mb-2">Pick Your Party</h1>
          <p className="text-center text-[#8888aa] mb-8">Based on real 2024 election results</p>
          <div className="space-y-3 max-w-2xl mx-auto">
            {PARTIES.map((party) => (
              <motion.button
                key={party.name}
                whileHover={{ scale: 1.01 }}
                whileTap={{ scale: 0.99 }}
                onClick={() => { setSelectedParty(party.name); setStep(3); }}
                className={`glass-card p-5 w-full text-left flex items-center gap-4 transition-all ${
                  selectedParty === party.name ? "border-[#ff9933]/50" : "hover:border-white/10"
                }`}
              >
                <span className="text-3xl">{party.icon}</span>
                <div className="flex-1">
                  <h3 className="font-semibold">{party.name}</h3>
                  <p className="text-sm text-[#8888aa]">{party.short} • Won {party.seats} seats in 2024</p>
                </div>
                <div className="w-24 h-3 bg-white/5 rounded-full overflow-hidden">
                  <div className="h-full rounded-full" style={{ width: `${(party.seats / 543) * 100}%`, background: party.color }} />
                </div>
              </motion.button>
            ))}
          </div>
          <button onClick={() => setStep(1)} className="mt-6 text-sm text-[#8888aa] hover:text-[#ff9933] mx-auto block">← Back to role</button>
        </motion.div>
      )}

      {/* Step 3: Difficulty + Launch */}
      {step === 3 && (
        <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="max-w-2xl mx-auto">
          <h1 className="font-[family-name:var(--font-outfit)] text-3xl font-bold text-center mb-2">Set Difficulty</h1>
          <p className="text-center text-[#8888aa] mb-8">How tough should the opposition be?</p>
          <div className="grid grid-cols-2 gap-3 mb-8">
            {DIFFICULTIES.map((d) => (
              <button
                key={d.id}
                onClick={() => setDifficulty(d.id)}
                className={`glass-card-sm p-4 text-left transition-all ${
                  difficulty === d.id ? "border-[#ff9933]/50 bg-[#ff9933]/5" : "hover:border-white/10"
                }`}
              >
                <h4 className="font-semibold text-sm">{d.label}</h4>
                <p className="text-xs text-[#8888aa] mt-1">{d.desc}</p>
              </button>
            ))}
          </div>

          {/* Summary */}
          <div className="glass-card p-6 mb-6">
            <h3 className="text-sm text-[#8888aa] mb-3">CAMPAIGN BRIEFING</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between"><span className="text-[#8888aa]">Role</span><span>{ROLES.find((r) => r.id === selectedRole)?.name}</span></div>
              <div className="flex justify-between"><span className="text-[#8888aa]">Party</span><span>{PARTIES.find((p) => p.name === selectedParty)?.short}</span></div>
              <div className="flex justify-between"><span className="text-[#8888aa]">Difficulty</span><span>{DIFFICULTIES.find((d) => d.id === difficulty)?.label}</span></div>
              <div className="flex justify-between"><span className="text-[#8888aa]">Campaign Length</span><span>8 weeks</span></div>
              <div className="flex justify-between"><span className="text-[#8888aa]">Starting Budget</span><span>₹500 crore</span></div>
              <div className="flex justify-between"><span className="text-[#8888aa]">Target</span><span className="text-[#ff9933] font-bold">272 / 543 seats</span></div>
            </div>
          </div>

          <button
            onClick={handleStart}
            disabled={loading}
            className="btn-saffron w-full py-4 text-lg rounded-xl disabled:opacity-50"
          >
            {loading ? "Initializing Campaign..." : "🚀 Launch Campaign"}
          </button>
          <button onClick={() => setStep(2)} className="mt-4 text-sm text-[#8888aa] hover:text-[#ff9933] mx-auto block">← Back</button>
        </motion.div>
      )}
    </main>
  );
}
