/* ==========================================================================
   HAPEEC — homepage behaviour
   No dependencies. Every handler drives a control that exists on the page and
   points at a route the Laravel application already serves.
   ========================================================================== */

(function () {
  'use strict';

  var $  = function (sel, root) { return (root || document).querySelector(sel); };
  var $$ = function (sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); };

  /* ---------------------------------------------------------------------
     Hero slider
     --------------------------------------------------------------------- */
  (function hero() {
    var root = $('[data-hero]');
    if (!root) return;

    var track  = $('.hero-track', root);
    var slides = $$('.hero-slide', root);
    var dots   = $$('.hero-dot', root);
    if (slides.length < 2) return;

    var rtl = document.documentElement.dir === 'rtl';
    var i = 0;
    var timer = null;

    function go(n) {
      i = (n + slides.length) % slides.length;
      track.style.transform = 'translateX(' + (rtl ? '' : '-') + (i * 100) + '%)';
      dots.forEach(function (d, k) { d.setAttribute('aria-current', k === i ? 'true' : 'false'); });
      slides.forEach(function (s, k) { s.setAttribute('aria-hidden', k === i ? 'false' : 'true'); });
    }

    function play()  { stop(); timer = setInterval(function () { go(i + 1); }, 6000); }
    function stop()  { if (timer) { clearInterval(timer); timer = null; } }

    // In RTL the "previous" arrow points to the visually earlier slide.
    $('.hero-prev', root).addEventListener('click', function () { go(i - 1); play(); });
    $('.hero-next', root).addEventListener('click', function () { go(i + 1); play(); });
    dots.forEach(function (d, k) { d.addEventListener('click', function () { go(k); play(); }); });

    root.addEventListener('mouseenter', stop);
    root.addEventListener('mouseleave', play);
    document.addEventListener('visibilitychange', function () {
      if (document.hidden) { stop(); } else { play(); }
    });

    go(0);
    play();
  }());

  /* ---------------------------------------------------------------------
     Horizontal rails (products, categories, brands, magazine, chips)
     --------------------------------------------------------------------- */
  $$('[data-rail]').forEach(function (wrap) {
    var rail = $('[data-rail-track]', wrap);
    var prev = $('[data-rail-prev]', wrap);
    var next = $('[data-rail-next]', wrap);
    if (!rail) return;

    function page() { return Math.max(rail.clientWidth * 0.8, 200); }

    function sync() {
      if (!prev || !next) return;
      // scrollLeft is negative in RTL on standards-compliant engines.
      var max = rail.scrollWidth - rail.clientWidth;
      var pos = Math.abs(rail.scrollLeft);
      var atStart = pos <= 2;
      var atEnd = pos >= max - 2;
      var none = max <= 2;
      prev.hidden = none || atStart;
      next.hidden = none || atEnd;
    }

    var rtl = getComputedStyle(rail).direction === 'rtl';
    function scrollBy(dir) { rail.scrollBy({ left: dir * page() * (rtl ? -1 : 1), behavior: 'smooth' }); }

    if (prev) prev.addEventListener('click', function () { scrollBy(-1); });
    if (next) next.addEventListener('click', function () { scrollBy(1); });
    rail.addEventListener('scroll', sync, { passive: true });
    window.addEventListener('resize', sync);
    sync();
  });

  /* ---------------------------------------------------------------------
     Story circles — «بیشتر» reveals the rest of the rail.
     The catalogue has no standalone story-listing route, so this expands in
     place rather than linking somewhere that would 404.
     --------------------------------------------------------------------- */
  (function stories() {
    var more = $('[data-stories-more]');
    if (!more) return;
    var hidden = $$('[data-story-hidden]');
    if (!hidden.length) { more.hidden = true; return; }

    more.addEventListener('click', function () {
      hidden.forEach(function (el) { el.hidden = false; });
      more.hidden = true;
    });
  }());

  /* ---------------------------------------------------------------------
     Flash-sale countdown — driven by the campaign's real end timestamp.
     No timer is shown when the backend did not configure one.
     --------------------------------------------------------------------- */
  $$('[data-countdown]').forEach(function (box) {
    var end = parseInt(box.getAttribute('data-countdown'), 10);
    if (!end || isNaN(end)) { box.hidden = true; return; }

    var h = $('[data-cd-h]', box), m = $('[data-cd-m]', box), s = $('[data-cd-s]', box);
    var pad = function (n) { return String(n).padStart(2, '0'); };

    function tick() {
      var left = end - Math.floor(Date.now() / 1000);
      if (left <= 0) { box.hidden = true; clearInterval(id); return; }
      h.textContent = pad(Math.floor(left / 3600));
      m.textContent = pad(Math.floor((left % 3600) / 60));
      s.textContent = pad(left % 60);
    }
    var id = setInterval(tick, 1000);
    tick();
  });

  /* ---------------------------------------------------------------------
     Mobile drawer
     --------------------------------------------------------------------- */
  (function drawer() {
    var panel = $('[data-drawer]');
    var scrim = $('[data-scrim]');
    if (!panel || !scrim) return;

    var openers = $$('[data-drawer-open]');
    var closers = $$('[data-drawer-close]');
    var last = null;

    function open() {
      last = document.activeElement;
      panel.dataset.open = 'true';
      scrim.dataset.open = 'true';
      document.body.dataset.locked = 'true';
      openers.forEach(function (b) { b.setAttribute('aria-expanded', 'true'); });
      var first = panel.querySelector('button, a');
      if (first) first.focus();
    }
    function close() {
      panel.dataset.open = 'false';
      scrim.dataset.open = 'false';
      document.body.dataset.locked = 'false';
      openers.forEach(function (b) { b.setAttribute('aria-expanded', 'false'); });
      if (last) last.focus();
    }

    openers.forEach(function (b) { b.addEventListener('click', open); });
    closers.forEach(function (b) { b.addEventListener('click', close); });
    scrim.addEventListener('click', close);
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && panel.dataset.open === 'true') close();
    });

    // Collapsible category groups inside the drawer.
    $$('[data-drawer-group]', panel).forEach(function (btn) {
      var sub = document.getElementById(btn.getAttribute('aria-controls'));
      if (!sub) return;
      btn.addEventListener('click', function () {
        var open = btn.getAttribute('aria-expanded') === 'true';
        btn.setAttribute('aria-expanded', String(!open));
        sub.dataset.open = String(!open);
      });
    });
  }());

  /* ---------------------------------------------------------------------
     Search by image.
     Inside the Laravel theme the header ships a visual-search modal
     (#vcamModal); when it is on the page the camera opens it, exactly as
     before. On its own, the button falls back to the file picker and posts to
     the product-search route. With neither available it is removed rather
     than left as a control that does nothing.
     --------------------------------------------------------------------- */
  (function imageSearch() {
    var btn = $('[data-image-search]');
    if (!btn) return;

    var modal = document.getElementById('vcamModal');
    if (modal) {
      btn.addEventListener('click', function () { modal.hidden = false; });
      return;
    }

    var input = $('[data-image-search-input]');
    if (!input || !btn.getAttribute('data-image-search')) { btn.remove(); return; }

    btn.addEventListener('click', function () { input.click(); });
    input.addEventListener('change', function () {
      if (!input.files || !input.files.length) return;
      var form = input.closest('form');
      if (form) form.submit();
    });
  }());
}());
