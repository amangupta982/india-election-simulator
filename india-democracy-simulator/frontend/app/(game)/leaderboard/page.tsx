"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { getLeaderboard } from "@/lib/api";
import Link from "next/link";

export default function LeaderboardPage() {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [entries, setEntries] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    getLeaderboard().then((data: any) => {
      setEntries(data.entries || []);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  const getRankDisplay = (idx: number) => {
    if (idx === 0) return { icon: "🥇", class: "table-row-gold" };
    if (idx === 1) return { icon: "🥈", class: "table-row-silver" };
    if (idx === 2) return { icon: "🥉", class: "table-row-bronze" };
    return { icon: `#${idx + 1}`, class: "" };
  };

  return (
    <main className="min-h-screen pt-12 px-4 max-w-5xl mx-auto pb-20 relative">
      {/* Background glow */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[300px] rounded-full bg-[#FF6B2B]/[0.03] blur-[150px] pointer-events-none" />

      {/* Header */}
      <div className="text-center mb-12">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <span className="text-5xl mb-4 inline-block">🏆</span>
          <h1 className="font-[family-name:var(--font-outfit)] text-5xl font-extrabold mb-3">
            Hall of <span className="text-[#FF6B2B]">Fame</span>
          </h1>
          <p className="text-[var(--text-secondary)] text-lg">India&apos;s finest election strategists</p>
        </motion.div>
      </div>

      {/* Table */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="glass-card overflow-hidden"
      >
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-white/5">
              <th className="p-5 text-[10px] text-[var(--text-muted)] font-bold uppercase tracking-wider">Rank</th>
              <th className="p-5 text-[10px] text-[var(--text-muted)] font-bold uppercase tracking-wider">Strategist</th>
              <th className="p-5 text-[10px] text-[var(--text-muted)] font-bold uppercase tracking-wider">Party</th>
              <th className="p-5 text-[10px] text-[var(--text-muted)] font-bold uppercase tracking-wider hidden md:table-cell">Role</th>
              <th className="p-5 text-[10px] text-[var(--text-muted)] font-bold uppercase tracking-wider">Margin</th>
              <th className="p-5 text-[10px] text-[var(--text-muted)] font-bold uppercase tracking-wider text-right">Score</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={6} className="p-12 text-center">
                  <div className="w-8 h-8 border-2 border-[#FF6B2B]/30 border-t-[#FF6B2B] rounded-full animate-spin mx-auto mb-3" />
                  <span className="text-[var(--text-muted)] text-sm">Loading rankings...</span>
                </td>
              </tr>
            ) : entries.length === 0 ? (
              <tr>
                <td colSpan={6} className="p-16 text-center">
                  <div className="text-4xl mb-4">🗳️</div>
                  <h3 className="font-[family-name:var(--font-outfit)] text-lg font-bold mb-2">No campaigns completed yet</h3>
                  <p className="text-[var(--text-secondary)] text-sm mb-6">Be the first to make history!</p>
                  <Link href="/role-select">
                    <button className="btn-saffron">Start Campaign →</button>
                  </Link>
                </td>
              </tr>
            ) : (
              entries.map((entry, idx) => {
                const rank = getRankDisplay(idx);
                return (
                  <motion.tr
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: idx * 0.08 }}
                    key={idx}
                    className={`border-b border-white/[0.03] hover:bg-white/[0.02] transition-colors ${rank.class}`}
                  >
                    <td className="p-5">
                      <span className="text-lg">{rank.icon}</span>
                    </td>
                    <td className="p-5">
                      <span className="font-bold text-white">{entry.display_name}</span>
                    </td>
                    <td className="p-5">
                      <span className="px-2.5 py-1 bg-white/5 rounded-lg text-xs font-medium border border-white/5">
                        {entry.player_party}
                      </span>
                    </td>
                    <td className="p-5 text-[var(--text-secondary)] capitalize hidden md:table-cell">
                      {entry.role.replace(/_/g, " ")}
                    </td>
                    <td className="p-5">
                      <span className={`font-mono font-bold ${entry.seat_margin > 0 ? "text-[#1BA80E]" : "text-[#E74C3C]"}`}>
                        {entry.seat_margin > 0 ? `+${entry.seat_margin}` : entry.seat_margin}
                      </span>
                    </td>
                    <td className="p-5 text-right">
                      <span className="font-mono font-extrabold text-[#FF6B2B] text-lg">
                        {Math.round(entry.score).toLocaleString()}
                      </span>
                    </td>
                  </motion.tr>
                );
              })
            )}
          </tbody>
        </table>
      </motion.div>

      <div className="mt-8 text-center">
        <Link href="/">
          <button className="btn-ghost">← Back to Home</button>
        </Link>
      </div>
    </main>
  );
}
