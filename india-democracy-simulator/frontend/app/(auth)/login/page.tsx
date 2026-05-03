"use client";

import { motion } from "framer-motion";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { useGameStore } from "@/store/gameStore";
import { loginUser, registerUser } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const setAuth = useGameStore((s) => s.setAuth);
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      let data: any;
      if (isRegister) {
        data = await registerUser(email, displayName, password);
      } else {
        data = await loginUser(email, password);
      }
      setAuth(data.access_token, data.user);
      router.push("/role-select");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen flex items-center justify-center px-4 relative">
      {/* Ambient orbs */}
      <div className="absolute top-1/3 left-1/3 w-[400px] h-[400px] rounded-full bg-[#FF6B2B]/[0.03] blur-[100px] pointer-events-none" />
      <div className="absolute bottom-1/3 right-1/3 w-[300px] h-[300px] rounded-full bg-[#138808]/[0.02] blur-[80px] pointer-events-none" />

      <motion.div
        initial={{ opacity: 0, y: 30, scale: 0.97 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.7, ease: "easeOut" }}
        className="glass-card-glow p-10 w-full max-w-md relative overflow-hidden"
      >
        {/* Top accent line */}
        <div className="absolute top-0 left-0 w-full h-[3px] bg-gradient-to-r from-[#FF6B2B] via-[#FF9933] to-[#138808]" />

        <div className="text-center mb-10">
          <motion.div
            initial={{ scale: 0, rotate: -180 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={{ delay: 0.2, duration: 0.8, ease: "easeOut" }}
            className="inline-block"
          >
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-[#FF6B2B]/20 to-[#FF6B2B]/5 flex items-center justify-center border border-[#FF6B2B]/20 mb-4 mx-auto">
              <span className="text-3xl">🏛️</span>
            </div>
          </motion.div>
          <h1 className="font-[family-name:var(--font-outfit)] text-2xl font-extrabold">
            {isRegister ? "Join the Campaign" : "Welcome Back"}
          </h1>
          <p className="text-sm text-[var(--text-secondary)] mt-2">
            {isRegister ? "Create your political identity" : "Your war room awaits, Neta ji"}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          {isRegister && (
            <div>
              <label className="block text-xs text-[var(--text-muted)] mb-2 uppercase tracking-wider font-semibold">Display Name</label>
              <input
                type="text"
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                className="input-field"
                placeholder="Your political name"
                required
              />
            </div>
          )}

          <div>
            <label className="block text-xs text-[var(--text-muted)] mb-2 uppercase tracking-wider font-semibold">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="input-field"
              placeholder="neta@india.gov"
              required
            />
          </div>

          <div>
            <label className="block text-xs text-[var(--text-muted)] mb-2 uppercase tracking-wider font-semibold">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="input-field"
              placeholder="••••••••"
              required
            />
          </div>

          {error && (
            <motion.div
              initial={{ opacity: 0, y: -5 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-[#E74C3C] text-sm bg-[#E74C3C]/8 px-4 py-3 rounded-xl border border-[#E74C3C]/20"
            >
              {error}
            </motion.div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="btn-saffron w-full py-4 text-base rounded-xl disabled:opacity-50 mt-2"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Loading...
              </span>
            ) : isRegister ? "Create Account" : "Enter War Room →"}
          </button>
        </form>

        <div className="mt-8 text-center">
          <button
            onClick={() => { setIsRegister(!isRegister); setError(""); }}
            className="text-sm text-[var(--text-secondary)] hover:text-[#FF6B2B] transition-colors"
          >
            {isRegister ? "Already have an account? Login" : "New here? Create account"}
          </button>
        </div>
      </motion.div>
    </main>
  );
}
