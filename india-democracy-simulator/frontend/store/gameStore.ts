/* eslint-disable @typescript-eslint/no-explicit-any */
import { create } from "zustand";

export interface EventChoice {
  text: string;
  effect: {
    seat_delta: number;
    budget_delta_crore: number;
    approval_delta: number;
    state_effects: Record<string, number>;
  };
}

export interface GameEvent {
  id: string;
  week_number: number;
  event_type: string;
  headline: string;
  body: string;
  choices: EventChoice[];
  affected_states?: string[];
  civics_lesson?: string;
}

export interface OpponentMove {
  id: string;
  week_number: number;
  move_type: string;
  target_states?: string[];
  headline: string;
  effects: Record<string, any>;
}

export interface GameState {
  session_id: string;
  week_number: number;
  status: string;
  player_party: string;
  role: string;
  difficulty: string;
  budget_remaining: number;
  approval_rating: number;
  seat_projection_you: number;
  seat_projection_opp: number;
  win_probability: number;
  current_event: GameEvent | null;
  recent_opponent_moves: OpponentMove[];
  alliance_status: Record<string, any>;
  state_projections: Record<string, any>;
  decisions_made: number;
  total_weeks: number;
}

interface GameStore {
  // Auth
  token: string | null;
  user: any | null;
  setAuth: (token: string, user: any) => void;
  clearAuth: () => void;

  // Game state
  gameState: GameState | null;
  setGameState: (state: GameState) => void;

  // History
  eventsHistory: GameEvent[];
  opponentMoves: OpponentMove[];
  seatHistory: { week: number; you: number; opp: number }[];
  addEvent: (event: GameEvent) => void;
  addOpponentMove: (move: OpponentMove) => void;
  addSeatSnapshot: (week: number, you: number, opp: number) => void;

  // Civics
  civicsLessons: string[];
  addCivicsLesson: (lesson: string) => void;

  // Reset
  resetGame: () => void;
}

export const useGameStore = create<GameStore>((set) => ({
  token: null,
  user: null,
  setAuth: (token, user) => {
    try { localStorage.setItem("ids_token", token); } catch {}
    set({ token, user });
  },
  clearAuth: () => {
    try { localStorage.removeItem("ids_token"); } catch {}
    set({ token: null, user: null });
  },

  gameState: null,
  setGameState: (state) => set({ gameState: state }),

  eventsHistory: [],
  opponentMoves: [],
  seatHistory: [],
  addEvent: (event) => set((s) => ({ eventsHistory: [...s.eventsHistory, event] })),
  addOpponentMove: (move) => set((s) => ({ opponentMoves: [...s.opponentMoves, move] })),
  addSeatSnapshot: (week, you, opp) =>
    set((s) => ({ seatHistory: [...s.seatHistory, { week, you, opp }] })),

  civicsLessons: [],
  addCivicsLesson: (lesson) =>
    set((s) => ({ civicsLessons: [...s.civicsLessons, lesson] })),

  resetGame: () =>
    set({
      gameState: null,
      eventsHistory: [],
      opponentMoves: [],
      seatHistory: [],
      civicsLessons: [],
    }),
}));
