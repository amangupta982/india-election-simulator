/**
 * Firebase client SDK initialization for the frontend.
 *
 * Provides:
 * - Firebase Auth (Google Sign-In)
 * - Firestore real-time listeners (future: live leaderboard)
 */
import { initializeApp, getApps } from "firebase/app";
import { getAuth, GoogleAuthProvider, signInWithPopup } from "firebase/auth";

const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY || "",
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN || "",
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID || "secure-totality-495209-f6",
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET || "",
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID || "",
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID || "",
  measurementId: process.env.NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID || "",
};

// Initialize Firebase (singleton — prevent re-init in dev hot reload)
const app = getApps().length === 0 ? initializeApp(firebaseConfig) : getApps()[0];
const auth = getAuth(app);
const googleProvider = new GoogleAuthProvider();

/**
 * Sign in with Google via Firebase popup.
 * Returns the Firebase ID token to send to the backend.
 */
export async function signInWithGoogle(): Promise<{
  idToken: string;
  displayName: string;
  email: string;
  photoURL: string | null;
} | null> {
  try {
    const result = await signInWithPopup(auth, googleProvider);
    const idToken = await result.user.getIdToken();
    return {
      idToken,
      displayName: result.user.displayName || "",
      email: result.user.email || "",
      photoURL: result.user.photoURL,
    };
  } catch (error) {
    console.error("Google Sign-In failed:", error);
    return null;
  }
}

export { auth, app };
