"use client";

import { useState } from "react";
import { motion } from "framer-motion";

interface GoogleSignInButtonProps {
  onSuccess: (token: string, user: { email: string; display_name: string; avatar_url?: string }) => void;
  onError?: (error: string) => void;
}

/**
 * Google Sign-In button that integrates Firebase Auth with the backend.
 * Sends the Firebase ID token to /api/v1/auth/google for JWT exchange.
 */
export default function GoogleSignInButton({ onSuccess, onError }: GoogleSignInButtonProps) {
  const [loading, setLoading] = useState(false);

  const handleGoogleSignIn = async () => {
    setLoading(true);
    try {
      // Dynamic import to avoid SSR issues
      const { signInWithGoogle } = await import("@/lib/firebase");
      const result = await signInWithGoogle();

      if (!result) {
        onError?.("Google Sign-In was cancelled");
        return;
      }

      // Send Firebase ID token to backend for verification
      const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
      const response = await fetch(`${API_BASE}/auth/google`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id_token: result.idToken }),
      });

      if (!response.ok) {
        const err = await response.json().catch(() => ({ detail: "Authentication failed" }));
        throw new Error(err.detail);
      }

      const data = await response.json();
      onSuccess(data.access_token, {
        email: data.user.email,
        display_name: data.user.display_name,
        avatar_url: data.user.avatar_url,
      });
    } catch (err) {
      const message = err instanceof Error ? err.message : "Sign-in failed";
      onError?.(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.button
      type="button"
      onClick={handleGoogleSignIn}
      disabled={loading}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      aria-label="Sign in with Google"
      className="google-sign-in-btn"
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        gap: "12px",
        width: "100%",
        padding: "14px 24px",
        borderRadius: "12px",
        border: "1px solid rgba(255,255,255,0.15)",
        background: "rgba(255,255,255,0.05)",
        backdropFilter: "blur(12px)",
        color: "#fff",
        fontSize: "15px",
        fontWeight: 500,
        cursor: loading ? "not-allowed" : "pointer",
        opacity: loading ? 0.6 : 1,
        transition: "all 0.2s ease",
        fontFamily: "var(--font-inter)",
      }}
    >
      {/* Google "G" icon */}
      <svg width="20" height="20" viewBox="0 0 48 48" aria-hidden="true">
        <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>
        <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>
        <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>
        <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>
      </svg>
      {loading ? "Signing in..." : "Sign in with Google"}
    </motion.button>
  );
}
