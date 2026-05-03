/**
 * Tests for Zustand game store — state management logic.
 */
import { useGameStore } from "@/store/gameStore";

// Reset store before each test
beforeEach(() => {
  useGameStore.setState({
    token: null,
    user: null,
    gameState: null,
    eventsHistory: [],
    opponentMoves: [],
    seatHistory: [],
    civicsLessons: [],
  });
});

describe("Auth State", () => {
  test("setAuth stores token and user", () => {
    const store = useGameStore.getState();
    store.setAuth("test-token-123", { email: "test@example.com", display_name: "Test" });

    const updated = useGameStore.getState();
    expect(updated.token).toBe("test-token-123");
    expect(updated.user.email).toBe("test@example.com");
  });

  test("clearAuth removes token and user", () => {
    const store = useGameStore.getState();
    store.setAuth("token", { email: "a@b.com" });
    store.clearAuth();

    const updated = useGameStore.getState();
    expect(updated.token).toBeNull();
    expect(updated.user).toBeNull();
  });
});

describe("Game State", () => {
  test("setGameState updates game state", () => {
    const mockState = {
      session_id: "sess-123",
      week_number: 3,
      status: "in_progress",
      player_party: "Bharatiya Janata Party",
      role: "party_leader",
      difficulty: "normal",
      budget_remaining: 450,
      approval_rating: 52,
      seat_projection_you: 260,
      seat_projection_opp: 283,
      win_probability: 0.35,
      current_event: null,
      recent_opponent_moves: [],
      alliance_status: {},
      state_projections: {},
      decisions_made: 2,
      total_weeks: 8,
    };

    useGameStore.getState().setGameState(mockState);
    const updated = useGameStore.getState();
    expect(updated.gameState?.session_id).toBe("sess-123");
    expect(updated.gameState?.budget_remaining).toBe(450);
    expect(updated.gameState?.week_number).toBe(3);
  });
});

describe("Event History", () => {
  test("addEvent appends to events history", () => {
    const event = {
      id: "evt-1",
      week_number: 1,
      event_type: "rally",
      headline: "Test Rally",
      body: "Test body",
      choices: [],
    };

    useGameStore.getState().addEvent(event);
    useGameStore.getState().addEvent({ ...event, id: "evt-2", week_number: 2 });

    const updated = useGameStore.getState();
    expect(updated.eventsHistory).toHaveLength(2);
    expect(updated.eventsHistory[0].id).toBe("evt-1");
    expect(updated.eventsHistory[1].id).toBe("evt-2");
  });

  test("addOpponentMove appends to opponent moves", () => {
    const move = {
      id: "opp-1",
      week_number: 1,
      move_type: "counter_rally",
      headline: "Opposition counter-rally",
      effects: { approval_delta: -2 },
    };

    useGameStore.getState().addOpponentMove(move);
    expect(useGameStore.getState().opponentMoves).toHaveLength(1);
  });

  test("addSeatSnapshot tracks seat history", () => {
    const store = useGameStore.getState();
    store.addSeatSnapshot(1, 240, 303);
    store.addSeatSnapshot(2, 255, 288);
    store.addSeatSnapshot(3, 270, 273);

    const updated = useGameStore.getState();
    expect(updated.seatHistory).toHaveLength(3);
    expect(updated.seatHistory[2]).toEqual({ week: 3, you: 270, opp: 273 });
  });
});

describe("Civics Lessons", () => {
  test("addCivicsLesson appends lessons", () => {
    const store = useGameStore.getState();
    store.addCivicsLesson("FPTP means each constituency is a separate battle.");
    store.addCivicsLesson("272 seats needed for majority in Lok Sabha.");

    const updated = useGameStore.getState();
    expect(updated.civicsLessons).toHaveLength(2);
    expect(updated.civicsLessons[0]).toContain("FPTP");
  });
});

describe("Reset", () => {
  test("resetGame clears all game data but keeps auth", () => {
    const store = useGameStore.getState();
    store.setAuth("token", { email: "test@test.com" });
    store.addEvent({
      id: "evt-1", week_number: 1, event_type: "rally",
      headline: "Test", body: "Test", choices: [],
    });
    store.addSeatSnapshot(1, 200, 343);
    store.addCivicsLesson("Test lesson");

    store.resetGame();

    const updated = useGameStore.getState();
    expect(updated.gameState).toBeNull();
    expect(updated.eventsHistory).toHaveLength(0);
    expect(updated.seatHistory).toHaveLength(0);
    expect(updated.civicsLessons).toHaveLength(0);
    // Auth should NOT be cleared
    expect(updated.token).toBe("token");
  });
});
