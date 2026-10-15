/* Local API for the React UI: start a capture job, stream progress (SSE), stop it,
   record a login, and serve captured images for previews. */
import express from 'express';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { capture, recordLogin, deletePage } from './crawler.js';

const here = path.dirname(fileURLToPath(import.meta.url));
const OUT_ROOT = path.resolve(process.env.CAPTURE_DIR || path.join(here, '..', 'captures'));
const PORT = Number(process.env.PORT || 3001);

const app = express();
app.use(express.json());
app.use('/captures', express.static(OUT_ROOT));

let job = null;            // only one capture runs at a time
const clients = new Set(); // open SSE connections
const history = [];        // events of the current job, replayed to late subscribers
let jobId = 0;             // bumped whenever history is reset

function broadcast(event) {
  history.push(event);
  const line = `data: ${JSON.stringify(event)}\n\n`;
  for (const res of clients) res.write(line);
}

app.get('/api/status', (req, res) => {
  res.json({ running: !!job, outRoot: OUT_ROOT });
});

/* Polling fallback: events after a given position (SSE can be buffered by proxies) */
app.get('/api/history', (req, res) => {
  const after = Math.max(0, Number(req.query.after) || 0);
  res.set('Cache-Control', 'no-store');
  res.json({ job: jobId, running: !!job, events: history.slice(after) });
});

app.get('/api/events', (req, res) => {
  res.set({ 'Content-Type': 'text/event-stream', 'Cache-Control': 'no-cache', Connection: 'keep-alive' });
  res.flushHeaders();
  for (const e of history) res.write(`data: ${JSON.stringify(e)}\n\n`);
  clients.add(res);
  req.on('close', () => clients.delete(res));
});

function captureOptions(b) {
  // Single-page mode: the addresses to photograph, one per line (same site as the first)
  const only = String(b.only || '').split(/\s+/).filter((x) => /^https?:\/\//.test(x)).slice(0, 100);
  return {
    url: new URL(only[0] || b.url).href,
    only: only.length ? only : undefined,
    outDir: OUT_ROOT,
    maxPages: clamp(b.maxPages, 1, 500, 40),
    maxVisits: clamp(b.maxVisits, 1, 2000, 150),
    perPattern: clamp(b.perPattern, 1, 50, 3),
    dedupe: b.dedupe !== false,
    focus: b.focus !== false,
    fresh: !!b.fresh,
    seeds: String(b.seeds || '').split(/\s+/).filter((x) => /^https?:\/\//.test(x)).slice(0, 100),
    maxDepth: clamp(b.maxDepth, 0, 10, 4),
    viewports: (b.viewports || ['desktop', 'mobile']).filter((v) => v === 'desktop' || v === 'mobile'),
    keepQuery: !!b.keepQuery,
    sliceHeight: clamp(b.sliceHeight, 600, 6000, 2000),
    delay: clamp(b.delay, 0, 10000, 800),
    format: b.format === 'png' ? 'png' : 'jpeg',
    useAuth: !!b.useAuth,
    headed: !!b.headed
  };
}

function startCapture(options) {
  const controller = new AbortController();
  job = { controller };
  return capture({ ...options, signal: controller.signal }, broadcast)
    .catch((err) => broadcast({ type: 'fatal', message: String(err.message || err) }))
    .finally(() => { job = null; });
}

app.post('/api/capture', (req, res) => {
  // A login window left open must never block a capture: drop it
  if (job && job.login) { job.controller.abort(); job = null; }
  if (job) return res.status(409).json({ error: 'یک عکس‌برداری در حال اجراست. اول «توقف» را بزنید.' });
  let options;
  try { options = captureOptions(req.body || {}); } catch { return res.status(400).json({ error: 'آدرس سایت معتبر نیست.' }); }
  history.length = 0;
  jobId += 1;
  broadcast({ type: 'log', message: 'در حال راه‌اندازی مرورگر…' });
  startCapture({ ...options, useAuth: false });
  res.json({ ok: true });
});

/* Opens the site for a manual sign-in; when the session is detected (or the window
   is closed) the capture starts automatically, signed in, with the given options. */
app.post('/api/login', (req, res) => {
  if (job) return res.status(409).json({ error: 'یک کار در حال اجراست.' });
  let options;
  try { options = captureOptions({ ...(req.body || {}), useAuth: true }); } catch { return res.status(400).json({ error: 'آدرس معتبر نیست.' }); }
  history.length = 0;
  jobId += 1;
  const loginUrl = req.body.loginUrl && /^https?:\/\//.test(req.body.loginUrl) ? req.body.loginUrl : options.url;
  const controller = new AbortController();
  job = { controller, login: true };
  recordLogin(loginUrl, OUT_ROOT, broadcast, null, { signal: controller.signal })
    .then((r) => {
      if (controller.signal.aborted) return;
      job = null;
      if (req.body.autoCapture === false) return;
      if (!r.saved) { broadcast({ type: 'fatal', message: 'جلسه ورود ذخیره نشد.' }); return; }
      return startCapture(options);
    })
    .catch((err) => { if (controller.signal.aborted) return; job = null; broadcast({ type: 'fatal', message: String(err.message || err) }); });
  res.json({ ok: true });
});

/* Delete one captured page (folder + manifest entry). A missing folder is ignored. */
app.post('/api/delete', async (req, res) => {
  const { host, index } = req.body || {};
  if (job) return res.status(409).json({ error: 'تا پایان کار در حال اجرا صبر کنید.' });
  try {
    res.json(await deletePage(OUT_ROOT, String(host || ''), index));
  } catch (err) {
    res.status(400).json({ error: String(err.message || err) });
  }
});

app.post('/api/stop', (req, res) => {
  if (job) job.controller.abort();
  if (job && job.login) job = null;
  res.json({ ok: true });
});

if (process.argv.includes('--serve-ui')) {
  const dist = path.join(here, '..', 'dist');
  app.use(express.static(dist));
  app.get('*', (req, res) => res.sendFile(path.join(dist, 'index.html')));
}

function clamp(v, min, max, fallback) {
  const n = Number(v);
  return Number.isFinite(n) ? Math.min(max, Math.max(min, Math.round(n))) : fallback;
}

app.listen(PORT, '127.0.0.1', () => {
  console.log(`site-capture server: http://localhost:${PORT}`);
  console.log(`captures folder:     ${OUT_ROOT}`);
});
