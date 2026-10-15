import { useEffect, useMemo, useRef, useState } from 'react';

const DEFAULTS = {
  url: '',
  maxPages: 40,
  perPattern: 3,
  dedupe: true,
  focus: true,
  only: '',
  fresh: false,
  headed: false,
  seeds: '',
  loginUrl: '',
  maxDepth: 4,
  desktop: true,
  mobile: true,
  keepQuery: false,
  sliceHeight: 2000,
  delay: 800,
  format: 'jpeg',
  useAuth: false
};

const fa = (n) => Number(n).toLocaleString('fa-IR');

const KIND_LABEL = {
  home: 'صفحه اصلی', search: 'جستجو', listing: 'دسته و فیلتر', product: 'محصول', cart: 'سبد خرید',
  checkout: 'پروسه خرید', auth: 'ورود و ثبت‌نام', panel: 'پنل کاربر', blog: 'بلاگ', post: 'مطلب بلاگ',
  contact: 'تماس با ما', terms: 'قوانین و مقررات', about: 'درباره ما', faq: 'سوالات متداول', landing: 'لندینگ', other: 'سایر'
};

export default function App() {
  const [form, setForm] = useState(() => {
    try { return { ...DEFAULTS, ...JSON.parse(localStorage.getItem('site-capture-form') || '{}') }; } catch { return DEFAULTS; }
  });
  const [events, setEvents] = useState([]);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState('');
  const [serverDown, setServerDown] = useState(false);
  const [starting, setStarting] = useState(false);
  const [outRoot, setOutRoot] = useState('');
  const logEnd = useRef(null);
  const [saved, setSaved] = useState(null); // manifest.json of earlier runs for this site
  const [reload, setReload] = useState(0);   // bump to re-read manifest.json
  const [deleted, setDeleted] = useState(() => new Set()); // indexes removed in this session
  const [confirming, setConfirming] = useState(null);      // index awaiting a second click

  // Live progress: poll the local server (works behind any proxy, no SSE buffering)
  useEffect(() => {
    let after = 0;
    let job = null;
    let alive = true;
    let failures = 0;
    fetch('/api/status').then((r) => r.json()).then((s) => setOutRoot(s.outRoot)).catch(() => {});
    const tick = async () => {
      try {
        const r = await fetch(`/api/history?after=${after}`, { cache: 'no-store' });
        if (!r.ok) throw new Error(String(r.status));
        const h = await r.json();
        if (!alive) return;
        failures = 0;
        setServerDown(false);
        if (h.job !== job) {
          // A new job started (or first load): fetch its whole history next tick
          const reset = job !== null || after > 0;
          job = h.job;
          if (reset) { after = 0; setEvents([]); return; }
        }
        if (h.events.length) {
          after += h.events.length;
          setEvents((list) => [...list, ...h.events]);
        }
        setRunning(h.running);
      } catch {
        failures += 1;
        if (failures >= 2) setServerDown(true);
      } finally {
        if (alive) setTimeout(tick, 1000);
      }
    };
    tick();
    return () => { alive = false; };
  }, []);

  useEffect(() => {
    try { localStorage.setItem('site-capture-form', JSON.stringify(form)); } catch { /* private mode */ }
  }, [form]);

  useEffect(() => { logEnd.current?.scrollIntoView({ block: 'nearest' }); }, [events]);

  const formHostEarly = (() => { try { return new URL(form.url).hostname; } catch { return ''; } })();
  useEffect(() => {
    if (!formHostEarly) { setSaved(null); return; }
    let cancelled = false;
    fetch(`/captures/${formHostEarly}/manifest.json`, { cache: 'no-store' })
      .then((r) => (r.ok ? r.json() : null))
      .then((m) => { if (!cancelled) setSaved(m); })
      .catch(() => { if (!cancelled) setSaved(null); });
    return () => { cancelled = true; };
  }, [formHostEarly, running, reload]);

  const pages = useMemo(() => {
    const map = new Map();
    // Earlier runs first (from disk, or from the start event of a resumed run)
    const startEv = [...events].reverse().find((e) => e.type === 'start');
    const previous = startEv ? startEv.previous || [] : (saved ? saved.pages.map((p) => ({
      index: p.index, url: p.url, pattern: p.pattern, kind: p.kind,
      shots: Object.fromEntries(Object.entries(p.shots || {}).map(([vp, sh]) => [vp, { files: sh.files.map((f) => `pages/${p.slug}/${f}`) }]))
    })) : []);
    for (const p of previous) map.set(p.index, { ...p, old: true, shots: { ...p.shots }, errors: [] });
    for (const e of events) {
      if (e.type === 'page') map.set(e.index, { ...e, shots: {}, errors: [] });
      if (e.type === 'fill' && map.has(e.index)) map.get(e.index).filling = e.viewports;
      if (e.type === 'shot' && map.has(e.index)) map.get(e.index).shots[e.viewport] = e;
      if (e.type === 'error' && map.has(e.index)) map.get(e.index).errors.push(e);
      if (e.type === 'removed') map.delete(e.index);   // replaced by a new capture of the same address
    }
    for (const i of deleted) map.delete(i);
    return [...map.values()];
  }, [events, saved, deleted]);

  const start = [...events].reverse().find((e) => e.type === 'start');
  const skipped = events.filter((e) => e.type === 'skip');
  const visited = events.filter((e) => e.type === 'visited');
  const logs = events.filter((e) => ['log', 'login-open', 'login-detected', 'login-saved'].includes(e.type));
  const generalErrors = events.filter((e) => e.type === 'error' && (e.index == null || !pages.some((p) => p.index === e.index)));
  const visiting = running ? [...events].reverse().find((e) => e.type === 'visit') : null;

  async function removePage(index) {
    if (confirming !== index) { setConfirming(index); return; }
    setConfirming(null);
    try {
      await post('/api/delete', { host, index });
      setDeleted((d) => new Set(d).add(index));
      setReload((n) => n + 1);
    } catch (err) { setError(err.message); }
  }
  const loginBusy = events.some((e) => e.type === 'login-open') && !events.some((e) => e.type === 'login-saved');
  const done = events.find((e) => e.type === 'done');
  const fatal = events.find((e) => e.type === 'fatal');
  const formHost = formHostEarly;
  // Image paths come from the folder the server actually wrote to, not the form field
  const host = start ? start.outDir.split(/[\\/]/).pop() : formHost;

  const set = (key) => (e) => {
    const v = e.target.type === 'checkbox' ? e.target.checked : e.target.value;
    setForm((f) => ({ ...f, [key]: v }));
  };

  async function post(path, body) {
    setError('');
    const r = await fetch(path, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body || {}) });
    const data = await r.json().catch(() => ({}));
    if (!r.ok) throw new Error(data.error || 'خطا در ارتباط با سرور');
    return data;
  }

  async function onSubmit(e) {
    e.preventDefault();
    try {
      new URL(form.url);
    } catch { setError('آدرس کامل سایت را وارد کنید، مثلاً https://www.example.com'); return; }
    await startCapture({ only: '' });
  }

  // Single-page mode: photograph exactly these addresses, nothing else
  const onlyList = form.only.split(/\s+/).filter(Boolean);
  async function onOnly() {
    const bad = onlyList.find((x) => { try { return !/^https?:$/.test(new URL(x).protocol); } catch { return true; } });
    if (!onlyList.length || bad) { setError(bad ? `آدرس کامل نیست: ${bad}` : 'آدرس صفحه را وارد کنید.'); return; }
    const hosts = new Set(onlyList.map((x) => new URL(x).origin));
    if (hosts.size > 1) { setError('همه آدرس‌ها باید از یک سایت باشند؛ هر سایت را جدا بدهید.'); return; }
    await startCapture({ only: form.only, fresh: false });
  }

  async function startCapture(extra) {
    if (!form.desktop && !form.mobile) { setError('حداقل یکی از دسکتاپ یا موبایل را انتخاب کنید.'); return; }
    setStarting(true);
    try {
      await post('/api/capture', {
        ...form,
        ...extra,
        useAuth: false,
        viewports: [form.desktop && 'desktop', form.mobile && 'mobile'].filter(Boolean)
      });
      setRunning(true);
    } catch (err) {
      setError(/Failed to fetch|NetworkError/i.test(err.message) ? 'سرور ابزار در دسترس نیست. پنجره ترمینال npm run dev را ببینید.' : err.message);
    } finally { setStarting(false); }
  }

  return (
    <div className="app">
      <header className="top">
        <h1>عکس‌برداری از صفحات سایت</h1>
        <p>آدرس سایت را بدهید؛ ابزار صفحه‌ها را پیدا می‌کند و از هر نوع صفحه، نسخه دسکتاپ و موبایل را تمام‌صفحه ذخیره می‌کند.</p>
      </header>

      <main className="layout">
        <form className="card form" onSubmit={onSubmit} noValidate>
          <label className="field">
            <span>آدرس سایت</span>
            <input dir="ltr" type="url" placeholder="https://www.example.com" value={form.url} onChange={set('url')} required />
          </label>

          <div className="row">
            <label className="field"><span>حداکثر صفحه</span>
              <input type="number" min="1" max="500" value={form.maxPages} onChange={set('maxPages')} /></label>
            <label className="field"><span>از هر الگوی آدرس</span>
              <input type="number" min="1" max="50" value={form.perPattern} onChange={set('perPattern')} />
              <small>چند صفحه با آدرس مشابه باز شود</small></label>
          </div>

          <label className="check">
            <input type="checkbox" checked={form.focus} onChange={set('focus')} />
            <span>فقط صفحه‌های مهم: جستجو و فیلتر، محصول، سبد و پروسه خرید، پنل، بلاگ، قوانین و تماس (از لندینگ‌ها یکی کافی است)</span>
          </label>

          <label className="check">
            <input type="checkbox" checked={form.dedupe} onChange={set('dedupe')} />
            <span>از هر قالب فقط یک نمونه (اگر یک دسته‌بندی گرفته شد، بقیه دسته‌ها رد می‌شوند)</span>
          </label>

          <fieldset className="checks">
            <legend>نمایش</legend>
            <label><input type="checkbox" checked={form.desktop} onChange={set('desktop')} /> دسکتاپ (۱۴۴۰)</label>
            <label><input type="checkbox" checked={form.mobile} onChange={set('mobile')} /> موبایل (۳۹۰)</label>
          </fieldset>

          <details>
            <summary>تنظیمات بیشتر</summary>
            <div className="row">
              <label className="field"><span>عمق لینک‌ها</span>
                <input type="number" min="0" max="10" value={form.maxDepth} onChange={set('maxDepth')} /></label>
              <label className="field"><span>ارتفاع هر تکه (px)</span>
                <input type="number" min="600" max="6000" step="100" value={form.sliceHeight} onChange={set('sliceHeight')} /></label>
            </div>
            <div className="row">
              <label className="field"><span>مکث بین صفحه‌ها (ms)</span>
                <input type="number" min="0" max="10000" step="100" value={form.delay} onChange={set('delay')} /></label>
              <label className="field"><span>فرمت</span>
                <select value={form.format} onChange={set('format')}>
                  <option value="jpeg">JPG (حجم کم)</option>
                  <option value="png">PNG (کیفیت کامل)</option>
                </select></label>
            </div>
            <label className="check"><input type="checkbox" checked={form.keepQuery} onChange={set('keepQuery')} /> آدرس‌های با پارامتر (?page=2) جدا حساب شوند</label>
            <label className="check"><input type="checkbox" checked={form.headed} onChange={set('headed')} /> نمایش مرورگر هنگام عکس‌برداری (برای سایت‌هایی که مرورگر پنهان را مسدود می‌کنند)</label>
            <label className="field"><span>آدرس‌های اضافه (هر خط یک آدرس)</span>
              <textarea dir="ltr" rows="3" value={form.seeds} onChange={set('seeds')} placeholder="https://www.example.com/profile/orders" />
              <small>صفحه‌هایی که لینکشان در سایت پیدا نمی‌شود</small></label>
          </details>


          {saved && saved.pages && saved.pages.length > 0 && (
            <div className="memory">
              <p>از این سایت قبلاً <strong>{fa(saved.pages.length)}</strong> صفحه گرفته شده
                {saved.pending && saved.pending.length ? <> و <strong>{fa(saved.pending.length)}</strong> لینک برای ادامه مانده</> : null}.
                با «شروع» فقط صفحه‌های جدید گرفته می‌شود.</p>
              <label className="check"><input type="checkbox" checked={form.fresh} onChange={set('fresh')} /> از اول (عکس‌های قبلی این سایت پاک شود)</label>
            </div>
          )}

          {serverDown && <p className="error" role="alert">سرور ابزار جواب نمی‌دهد. پنجره ترمینال را ببینید؛ اگر بسته شده دوباره npm run dev را بزنید.</p>}
          {error && <p className="error" role="alert">{error}</p>}

          <div className="actions">
            <button className="btn" type="submit" disabled={running || starting}>{starting ? 'در حال ارسال…' : running ? 'در حال عکس‌برداری…' : 'شروع'}</button>
            {running && <button className="btn ghost" type="button" onClick={() => post('/api/stop')}>توقف</button>}
          </div>
          <fieldset className="panel-box">
            <legend>فقط یک صفحه مشخص</legend>
            <p className="muted">آدرس صفحه را بدهید تا فقط از همان (دسکتاپ و موبایل) عکس گرفته شود؛ بدون گشتن در سایت. چند آدرس هم می‌شود، هر خط یکی. اگر قبلاً گرفته شده، عکس جدید جایش را می‌گیرد.</p>
            <textarea dir="ltr" rows="2" value={form.only} onChange={set('only')} placeholder="https://www.example.com/product/123" aria-label="آدرس صفحه" />
            <button type="button" className="btn ghost" disabled={running || starting || !onlyList.length} onClick={onOnly}>
              {onlyList.length > 1 ? `فقط همین ${fa(onlyList.length)} صفحه` : 'فقط همین صفحه'}
            </button>
          </fieldset>

          {outRoot && <p className="muted">پوشه خروجی: <code dir="ltr">{outRoot}</code></p>}
        </form>

        <section className="card results" aria-live="polite">
          <div className="results__head">
            <h2>نتیجه</h2>
            <span className="muted">{fa(pages.length)} صفحه</span>
          </div>
          {fatal && <p className="error">{fatal.message}</p>}
          {done && done.only && <p className="ok">تمام شد: {fa(done.pages)} صفحه گرفته شد{done.failed ? `، ${fa(done.failed)} صفحه باز نشد` : ''}. عکس‌ها در <code dir="ltr">{done.outDir}</code> است.</p>}
          {done && !done.only && <p className="ok">تمام شد: {fa(done.pages)} صفحه جدید، {fa(done.filled)} نمای جاافتاده تکمیل شد، {fa(done.skipped)} صفحه تکراری رد شد{done.failed ? `، ${fa(done.failed)} صفحه باز نشد` : ''}. در مجموع {fa(done.total)} صفحه در <code dir="ltr">{done.outDir}</code> است. این پوشه را کامیت و پوش کنید.</p>}
          {done && done.missing && done.missing.length > 0 && (
            <p className="muted">پیدا نشد: {done.missing.map((k) => KIND_LABEL[k] || k).join('، ')}. اگر آدرسشان را می‌دانید، در «تنظیمات بیشتر» به «آدرس‌های اضافه» بدهید.</p>
          )}
          {visiting && <p className="muted" dir="auto">در حال باز کردن: <span dir="ltr">{visiting.url}</span></p>}
          {logs.length > 0 && <p className="muted">{logs[logs.length - 1].message}</p>}
          {generalErrors.length > 0 && (
            <ul className="errors" role="alert">
              {generalErrors.slice(-5).map((e, i) => <li key={i}><span dir="ltr">{e.url}</span>: {e.message}</li>)}
            </ul>
          )}
          {skipped.length > 0 && (
            <details className="skipped">
              <summary>{fa(skipped.length)} صفحه رد شد (قالب تکراری یا نوع صفحه‌ای که کافی بود)</summary>
              <ul>{skipped.map((e) => <li key={e.url}><span dir="ltr">{e.url}</span> <span className="muted">{e.reason === 'focus' ? `${KIND_LABEL[e.kind] || e.kind} کافی بود` : `= #${e.sameAs}`}</span></li>)}</ul>
            </details>
          )}
          {!pages.length && !running && <p className="muted">هنوز چیزی گرفته نشده است.</p>}
          {running && !pages.length && <p className="muted">در حال باز کردن سایت…</p>}
          <ul className="pages">
            {pages.map((p) => (
              <li key={p.index} className="page">
                <div className="page__meta">
                  <span className="num">{fa(p.index)}</span>
                  {p.old && <span className="tag">قبلی</span>}
                  {p.filling && <span className="tag">تکمیل {p.filling.join('، ')}</span>}
                  {(p.old || done) && !running && (
                    <button type="button" className={'del' + (confirming === p.index ? ' del--confirm' : '')}
                      onClick={() => removePage(p.index)} onBlur={() => setConfirming(null)}
                      aria-label={`حذف صفحه ${p.index} و فولدر عکس‌هایش`}>
                      {confirming === p.index ? 'مطمئنید؟ دوباره بزنید' : 'حذف'}
                    </button>
                  )}
                  <a dir="ltr" href={p.url} target="_blank" rel="noreferrer">{p.url}</a>
                  {p.kind && <span className="tag kind">{KIND_LABEL[p.kind] || p.kind}</span>}
                  <span className="tag" dir="ltr">{p.pattern}</span>
                </div>
                <div className="thumbs">
                  {['desktop', 'mobile'].map((vp) => p.shots[vp] && (
                    <a key={vp} className={'thumb ' + vp} href={`/captures/${host}/${p.shots[vp].files[0]}`} target="_blank" rel="noreferrer">
                      <img src={`/captures/${host}/${p.shots[vp].files[0]}`} alt={`${vp} ${p.url}`} loading="lazy" />
                      <span>{vp === 'desktop' ? 'دسکتاپ' : 'موبایل'} · {fa(p.shots[vp].files.length)} فایل</span>
                    </a>
                  ))}
                </div>
                {p.errors.map((er, i) => <p key={i} className="error small">{er.viewport}: {er.message}</p>)}
              </li>
            ))}
          </ul>
          <div ref={logEnd} />
        </section>
      </main>
    </div>
  );
}
