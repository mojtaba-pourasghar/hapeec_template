#!/usr/bin/env node
/* Command-line capture, no UI needed:
     node cli.js https://example.com --max 60 --mobile-only --png
     node cli.js https://example.com --login      (sign in by hand; the session is detected, saved and the capture runs signed in)
     node cli.js https://example.com --auth       (re-use the saved session)
     node cli.js https://example.com --fresh      (forget earlier captures of this site and start over)
     node cli.js https://example.com/p/1 https://example.com/cart --only   (just these pages, nothing else)
     node cli.js https://example.com --seed https://example.com/profile/orders --seed ... */
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { capture, recordLogin } from './server/crawler.js';

const here = path.dirname(fileURLToPath(import.meta.url));
const args = process.argv.slice(2);
const seeds = args.flatMap((a, i) => (a === '--seed' && args[i + 1] ? [args[i + 1]] : []));
const urls = args.filter((a, i) => /^https?:\/\//.test(a) && args[i - 1] !== '--seed' && args[i - 1] !== '--login-url');
const url = urls[0];
const flag = (name) => args.includes(name);
const value = (name, fallback) => {
  const i = args.indexOf(name);
  return i !== -1 && args[i + 1] ? Number(args[i + 1]) : fallback;
};

if (!url) {
  console.log('Usage: node cli.js <https://site> [--max 40] [--visits 150] [--per-pattern 3] [--depth 4] [--slice 2000]\n' +
    '                    [--desktop-only | --mobile-only] [--png] [--keep-query] [--no-dedupe] [--all] [--only]\n' +
    '                    [--seed <url> ...] [--login [--login-url <url>]] [--login-only] [--auth] [--fresh] [--headed]');
  process.exit(1);
}

const outDir = path.resolve(process.env.CAPTURE_DIR || path.join(here, 'captures'));

const loginUrlIndex = args.indexOf('--login-url');
const loginUrl = loginUrlIndex !== -1 ? args[loginUrlIndex + 1] : url;

// --login: open the site, sign in by hand; the session is detected and saved
// automatically, then the capture continues signed in (--login-only stops there).
if (flag('--login') || flag('--login-only')) {
  const r = await recordLogin(loginUrl, outDir, (e) => e.message && console.log(e.message));
  if (flag('--login-only') || !r.saved) process.exit(r.saved ? 0 : 1);
}

const viewports = flag('--desktop-only') ? ['desktop'] : flag('--mobile-only') ? ['mobile'] : ['desktop', 'mobile'];
await capture({
  url,
  outDir,
  maxPages: value('--max', 40),
  maxVisits: value('--visits', 150),
  perPattern: value('--per-pattern', 3),
  dedupe: !flag('--no-dedupe'),
  focus: !flag('--all'),
  seeds,
  maxDepth: value('--depth', 4),
  sliceHeight: value('--slice', 2000),
  delay: value('--delay', 800),
  viewports,
  keepQuery: flag('--keep-query'),
  format: flag('--png') ? 'png' : 'jpeg',
  useAuth: flag('--auth') || flag('--login'),
  fresh: flag('--fresh'),
  only: flag('--only') ? urls : undefined,
  headed: flag('--headed')
}, (e) => {
  if (e.type === 'start') console.log(`saving to ${e.outDir}${e.auth ? ' (signed in, ' + e.seeds + ' panel pages)' : ''}` +
    (e.resumed ? `\nresuming: ${e.previous.length} pages already captured, ${e.queued} links queued` : ''));
  if (e.type === 'fill') console.log(`[${e.index}] adding missing ${e.viewports.join(', ')}: ${e.url}`);
  if (e.type === 'page') console.log(`[${e.index}] ${e.url}  (${e.kind}, ${e.pattern})`);
  if (e.type === 'shot') console.log(`    ${e.viewport}: ${e.files.length} file(s), ${e.height}px tall`);
  if (e.type === 'skip') console.log(`    - skipped ${e.url} (${e.reason === 'focus' ? 'enough ' + e.kind + ' pages' : 'same layout as #' + e.sameAs})`);
  if (e.type === 'visited') console.log(`    + ${e.url}`);
  if (e.type === 'log') console.log(e.message);
  if (e.type === 'error' && e.index == null) console.log(`  ! ${e.url}: ${e.message}`);
  if (e.type === 'error') console.log(`    ! ${e.viewport}: ${e.message}`);
  if (e.type === 'done') console.log(`done: ${e.pages} new pages, ${e.skipped} duplicates skipped, ${e.filled} missing views added, ${e.failed} failed; ` +
    `${e.total} pages in total, ${e.pending} links left for next run -> ${e.outDir}` +
    (e.missing && e.missing.length ? `\nnot found: ${e.missing.join(', ')}` : ''));
});
