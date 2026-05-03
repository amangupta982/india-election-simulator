const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

async function apiFetch<T>(
  path: string,
  options: RequestInit = {},
  token?: string | null
): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "API Error");
  }
  return res.json();
}

// Auth
export const registerUser = (email: string, display_name: string, password: string) =>
  apiFetch("/auth/register", {
    method: "POST",
    body: JSON.stringify({ email, display_name, password }),
  });

export const loginUser = (email: string, password: string) =>
  apiFetch("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });

// Game
export const startGame = (
  token: string,
  player_party: string,
  role: string,
  difficulty: string = "normal"
) =>
  apiFetch("/game/start", {
    method: "POST",
    body: JSON.stringify({ player_party, role, difficulty }),
  }, token);

export const submitDecision = (
  token: string,
  sessionId: string,
  eventId: string,
  choiceIndex: number
) =>
  apiFetch(`/game/${sessionId}/decision`, {
    method: "POST",
    body: JSON.stringify({ event_id: eventId, choice_index: choiceIndex }),
  }, token);

export const getGameState = (token: string, sessionId: string) =>
  apiFetch(`/game/${sessionId}/state`, {}, token);

export const getPostMortem = (token: string, sessionId: string) =>
  apiFetch(`/game/${sessionId}/post-mortem`, {}, token);

// Constituencies
export const getConstituencies = (state?: string) =>
  apiFetch(`/constituencies${state ? `?state=${encodeURIComponent(state)}` : ""}`);

export const getSwingConstituencies = () =>
  apiFetch("/constituencies/swing");

// Leaderboard
export const getLeaderboard = (party?: string, role?: string) => {
  const params = new URLSearchParams();
  if (party) params.set("party", party);
  if (role) params.set("role", role);
  return apiFetch(`/leaderboard?${params.toString()}`);
};

// Feedback
export const submitFeedback = (
  token: string,
  sessionId: string,
  eventId: string,
  rating: number,
  feedbackText?: string
) =>
  apiFetch("/feedback/event", {
    method: "POST",
    body: JSON.stringify({
      session_id: sessionId,
      event_id: eventId,
      rating,
      feedback_text: feedbackText,
    }),
  }, token);
