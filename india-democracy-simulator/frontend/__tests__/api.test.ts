/**
 * Tests for API client functions — mocked fetch.
 */

// Mock fetch globally
const mockFetch = jest.fn();
global.fetch = mockFetch;

// Must import after setting up mock
import * as api from "@/lib/api";

beforeEach(() => {
  mockFetch.mockReset();
});

function mockOk(data: unknown) {
  mockFetch.mockResolvedValueOnce({
    ok: true,
    json: async () => data,
  });
}

function mockError(status: number, detail: string) {
  mockFetch.mockResolvedValueOnce({
    ok: false,
    status,
    statusText: "Error",
    json: async () => ({ detail }),
  });
}

describe("registerUser", () => {
  test("sends correct payload", async () => {
    mockOk({ access_token: "tok", user: { email: "a@b.com" } });
    await api.registerUser("a@b.com", "Test", "pass123");

    expect(mockFetch).toHaveBeenCalledTimes(1);
    const [url, opts] = mockFetch.mock.calls[0];
    expect(url).toContain("/auth/register");
    expect(opts.method).toBe("POST");
    const body = JSON.parse(opts.body);
    expect(body.email).toBe("a@b.com");
    expect(body.display_name).toBe("Test");
  });
});

describe("loginUser", () => {
  test("sends email and password", async () => {
    mockOk({ access_token: "tok", user: { email: "a@b.com" } });
    await api.loginUser("a@b.com", "pass");

    const [url, opts] = mockFetch.mock.calls[0];
    expect(url).toContain("/auth/login");
    expect(JSON.parse(opts.body).password).toBe("pass");
  });

  test("throws on error response", async () => {
    mockError(401, "Invalid credentials");
    await expect(api.loginUser("a@b.com", "wrong")).rejects.toThrow("Invalid credentials");
  });
});

describe("startGame", () => {
  test("sends auth header and game config", async () => {
    mockOk({ session_id: "s1", initial_state: {} });
    await api.startGame("my-token", "BJP", "party_leader", "normal");

    const [url, opts] = mockFetch.mock.calls[0];
    expect(url).toContain("/game/start");
    expect(opts.headers["Authorization"]).toBe("Bearer my-token");
    const body = JSON.parse(opts.body);
    expect(body.player_party).toBe("BJP");
    expect(body.role).toBe("party_leader");
  });
});

describe("submitDecision", () => {
  test("sends event_id and choice_index", async () => {
    mockOk({ new_state: {}, effects_applied: {} });
    await api.submitDecision("tok", "sess-1", "evt-1", 2);

    const [url, opts] = mockFetch.mock.calls[0];
    expect(url).toContain("/game/sess-1/decision");
    const body = JSON.parse(opts.body);
    expect(body.event_id).toBe("evt-1");
    expect(body.choice_index).toBe(2);
  });
});

describe("getConstituencies", () => {
  test("no params returns all", async () => {
    mockOk({ total: 10, constituencies: [] });
    await api.getConstituencies();

    const [url] = mockFetch.mock.calls[0];
    expect(url).toContain("/constituencies");
    expect(url).not.toContain("state=");
  });

  test("state param is encoded", async () => {
    mockOk({ total: 3, constituencies: [] });
    await api.getConstituencies("Uttar Pradesh");

    const [url] = mockFetch.mock.calls[0];
    expect(url).toContain("state=Uttar%20Pradesh");
  });
});

describe("getLeaderboard", () => {
  test("passes party and role filters", async () => {
    mockOk({ entries: [], total: 0 });
    await api.getLeaderboard("BJP", "party_leader");

    const [url] = mockFetch.mock.calls[0];
    expect(url).toContain("party=BJP");
    expect(url).toContain("role=party_leader");
  });
});
