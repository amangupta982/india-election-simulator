/* eslint-disable @typescript-eslint/no-explicit-any */
/**
 * Integration tests for game flow and state management
 * Tests the store operations and game state lifecycle
 */
import { useGameStore } from "@/store/gameStore";

beforeEach(() => {
  useGameStore.getState().resetGame();
  useGameStore.getState().clearAuth();
});

describe("Auth State Management", () => {
  test("setAuth stores token and user", () => {
    useGameStore.getState().setAuth("jwt-123", { email: "test@test.com", name: "Test" });
    expect(useGameStore.getState().token).toBe("jwt-123");
    expect(useGameStore.getState().user?.email).toBe("test@test.com");
  });

  test("clearAuth removes token and user", () => {
    useGameStore.getState().setAuth("jwt-123", { email: "test@test.com", name: "Test" });
    useGameStore.getState().clearAuth();
    expect(useGameStore.getState().token).toBeNull();
    expect(useGameStore.getState().user).toBeNull();
  });

  test("token persists across store reads", () => {
    useGameStore.getState().setAuth("persist-test", null);
    expect(useGameStore.getState().token).toBe("persist-test");
  });
});

describe("Game State Management", () => {
  const mockGameState = {
    session_id: "session-1",
    week_number: 1,
    status: "in_progress" as const,
    player_party: "Bharatiya Janata Party",
    role: "campaign_manager",
    difficulty: "normal",
    budget_remaining: 500,
    approval_rating: 50,
    seat_projection_you: 240,
    seat_projection_opp: 220,
    win_probability: 0.45,
    current_event: {
      id: "event-1",
      week_number: 1,
      event_type: "economic",
      headline: "Economic Rally Planned",
      body: "A major economic rally is being planned in UP",
      choices: [
        { text: "Hold grand rally", effect: { seat_delta: 5, budget_delta_crore: -50, approval_delta: 5, state_effects: {} } },
        { text: "Virtual campaign", effect: { seat_delta: 2, budget_delta_crore: -10, approval_delta: 2, state_effects: {} } },
      ],
      affected_states: ["Uttar Pradesh"],
    },
    recent_opponent_moves: [],
    alliance_status: {},
    state_projections: {},
    decisions_made: 0,
    total_weeks: 8,
  };

  test("setGameState stores game state", () => {
    useGameStore.getState().setGameState(mockGameState as any);
    const state = useGameStore.getState().gameState;
    expect(state?.session_id).toBe("session-1");
    expect(state?.player_party).toBe("Bharatiya Janata Party");
    expect(state?.week_number).toBe(1);
  });

  test("setGameState replaces previous state", () => {
    useGameStore.getState().setGameState(mockGameState as any);
    const updated = { ...mockGameState, week_number: 3, approval_rating: 60 };
    useGameStore.getState().setGameState(updated as any);
    expect(useGameStore.getState().gameState?.week_number).toBe(3);
    expect(useGameStore.getState().gameState?.approval_rating).toBe(60);
  });

  test("resetGame clears game state but keeps auth", () => {
    useGameStore.getState().setAuth("jwt-123", { email: "test@test.com", name: "Test" });
    useGameStore.getState().setGameState(mockGameState as any);
    useGameStore.getState().resetGame();
    expect(useGameStore.getState().gameState).toBeNull();
    expect(useGameStore.getState().token).toBe("jwt-123"); // auth preserved
  });
});

describe("Event History Tracking", () => {
  test("addEvent accumulates events", () => {
    const event1 = { id: "e1", week_number: 1, event_type: "economic", headline: "Rally", body: "...", choices: [] };
    const event2 = { id: "e2", week_number: 2, event_type: "scandal", headline: "Scandal", body: "...", choices: [] };
    useGameStore.getState().addEvent(event1 as any);
    useGameStore.getState().addEvent(event2 as any);
    expect(useGameStore.getState().eventsHistory).toHaveLength(2);
    expect(useGameStore.getState().eventsHistory[0].id).toBe("e1");
    expect(useGameStore.getState().eventsHistory[1].id).toBe("e2");
  });

  test("addOpponentMove accumulates moves", () => {
    const move = { id: "m1", week_number: 1, move_type: "rally", headline: "Counter Rally", effects: {} };
    useGameStore.getState().addOpponentMove(move as any);
    expect(useGameStore.getState().opponentMoves).toHaveLength(1);
  });

  test("addSeatSnapshot tracks seat history", () => {
    useGameStore.getState().addSeatSnapshot(1, 240, 220);
    useGameStore.getState().addSeatSnapshot(2, 250, 215);
    const history = useGameStore.getState().seatHistory;
    expect(history).toHaveLength(2);
    expect(history[1].you).toBe(250);
  });

  test("resetGame clears all history", () => {
    useGameStore.getState().addEvent({ id: "e1", week_number: 1, event_type: "test", headline: "Test", body: "", choices: [] } as any);
    useGameStore.getState().addSeatSnapshot(1, 240, 220);
    useGameStore.getState().addCivicsLesson("Test lesson");
    useGameStore.getState().resetGame();
    expect(useGameStore.getState().eventsHistory).toHaveLength(0);
    expect(useGameStore.getState().seatHistory).toHaveLength(0);
    expect(useGameStore.getState().civicsLessons).toHaveLength(0);
  });
});

describe("Civics Lessons", () => {
  test("addCivicsLesson accumulates lessons", () => {
    useGameStore.getState().addCivicsLesson("Lesson about FPTP");
    useGameStore.getState().addCivicsLesson("Lesson about coalitions");
    expect(useGameStore.getState().civicsLessons).toHaveLength(2);
    expect(useGameStore.getState().civicsLessons[0]).toBe("Lesson about FPTP");
  });
});
