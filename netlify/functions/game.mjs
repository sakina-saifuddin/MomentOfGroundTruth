// Audience game: "Can you beat the model?"
//
// Phones vote on /play/, the deck polls the totals. One blob per vote (r{round}/{choice}/{voter}), so
// simultaneous votes never overwrite each other. The true causes and the model's answers live only
// here, and are sent to clients only after the host reveals them.
//
//   GET  ?action=state[&voter=ID]   totals, voter count, reveal flag (+ answers once revealed, + this voter's picks)
//   POST {action:"vote", voter, round, choice}
//   POST {action:"reveal", key, value}   host only
//   POST {action:"reset", key}           host only, wipes all votes
import { getStore } from "@netlify/blobs";
import ANSWERS from "./answers.mjs";

const HOST_KEY = process.env.HOST_KEY || "mog-host";
const N_CAUSES = 8;
const N_ROUNDS = ANSWERS.length;
const STATE_KEY = "meta/state";

const json = (obj, status = 200) =>
  new Response(JSON.stringify(obj), {
    status,
    headers: { "content-type": "application/json", "cache-control": "no-store", "access-control-allow-origin": "*" },
  });

export const makeHandler = (openStore) => async (req) => {
  if (req.method === "OPTIONS") return json({ ok: true });
  const store = openStore();
  const url = new URL(req.url);
  let body = {};
  if (req.method === "POST") {
    try {
      body = await req.json();
    } catch {
      return json({ ok: false, error: "bad json" }, 400);
    }
  }
  const action = body.action || url.searchParams.get("action") || "state";

  const getState = async () => (await store.get(STATE_KEY, { type: "json" })) || { revealed: false, epoch: 0 };
  const listVotes = async () => (await store.list({ prefix: "r" })).blobs.map((b) => b.key);

  if (action === "state") {
    const state = await getState();
    const me = url.searchParams.get("voter");
    const counts = Array.from({ length: N_ROUNDS }, () => Array(N_CAUSES).fill(0));
    const voters = new Set();
    const mine = Array(N_ROUNDS).fill(-1);
    for (const key of await listVotes()) {
      const [r, c, v] = key.split("/");
      const round = Number(r.slice(1));
      const choice = Number(c);
      if (!(round >= 0 && round < N_ROUNDS && choice >= 0 && choice < N_CAUSES)) continue;
      counts[round][choice] += 1;
      voters.add(v);
      if (me && v === me) mine[round] = choice;
    }
    return json({
      ok: true,
      revealed: !!state.revealed,
      epoch: state.epoch || 0,
      voters: voters.size,
      rounds: counts.map((c) => ({ counts: c, total: c.reduce((a, b) => a + b, 0) })),
      mine,
      answers: state.revealed ? ANSWERS : null,
    });
  }

  if (action === "vote") {
    const { voter, round, choice } = body;
    if (typeof voter !== "string" || !/^[A-Za-z0-9-]{6,40}$/.test(voter)) return json({ ok: false, error: "bad voter" }, 400);
    if (!Number.isInteger(round) || round < 0 || round >= N_ROUNDS) return json({ ok: false, error: "bad round" }, 400);
    if (!Number.isInteger(choice) || choice < 0 || choice >= N_CAUSES) return json({ ok: false, error: "bad choice" }, 400);
    const state = await getState();
    if (state.revealed) return json({ ok: false, closed: true });
    // one vote per voter per round: drop any earlier pick, then record this one
    await Promise.all(
      Array.from({ length: N_CAUSES }, (_, c) => (c === choice ? store.set(`r${round}/${c}/${voter}`, "1") : store.delete(`r${round}/${c}/${voter}`))),
    );
    return json({ ok: true, epoch: state.epoch || 0 });
  }

  if (action === "reveal" || action === "reset") {
    if (body.key !== HOST_KEY) return json({ ok: false, error: "wrong host key" }, 403);
    const state = await getState();
    if (action === "reveal") {
      state.revealed = body.value !== false;
      await store.setJSON(STATE_KEY, state);
      return json({ ok: true, revealed: state.revealed });
    }
    const keys = await listVotes();
    for (let i = 0; i < keys.length; i += 25) await Promise.all(keys.slice(i, i + 25).map((k) => store.delete(k)));
    await store.setJSON(STATE_KEY, { revealed: false, epoch: (state.epoch || 0) + 1 });
    return json({ ok: true, cleared: keys.length });
  }

  return json({ ok: false, error: "unknown action" }, 400);
};

export default makeHandler(() => getStore({ name: "game", consistency: "strong" }));
