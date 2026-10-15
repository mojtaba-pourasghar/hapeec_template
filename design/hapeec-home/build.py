#!/usr/bin/env python3
"""Render the HAPEEC homepage.

Layout and section order follow the captured Digikala homepage
(`tools/site-capture/captures/www.digikala.com`) section for section; the
palette, wordmark, copy and catalogue are HAPEEC's.

Generating rather than hand-writing the markup keeps one `product_card()` for
every product on the page, so there is a single card implementation to keep
consistent — the same constraint the Blade version carries.

    python3 build.py     # writes index.html next to this file
"""

import html
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = json.load(open(os.path.join(HERE, 'data', 'home.json'), encoding='utf-8'))
BASE = 'https://test.happenengrave.com'
PHOTO = BASE + '/uploads/products/thumbnail/'


def e(s):
    return html.escape(s or '', quote=True)


# ---------------------------------------------------------------------------
# One outline icon family, stroked and never filled, so the header, navigation
# and footer cannot drift into mixed icon styles.
# ---------------------------------------------------------------------------

ICONS = {
    'search':   '<circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/>',
    'camera':   '<path d="M3 8.5A1.5 1.5 0 0 1 4.5 7h2.2a1 1 0 0 0 .83-.45l.94-1.4A1 1 0 0 1 9.3 4.7h5.4a1 1 0 0 1 .83.45l.94 1.4a1 1 0 0 0 .83.45h2.2A1.5 1.5 0 0 1 21 8.5v9A1.5 1.5 0 0 1 19.5 19h-15A1.5 1.5 0 0 1 3 17.5z"/><circle cx="12" cy="12.8" r="3.3"/>',
    'bell':     '<path d="M18 8a6 6 0 1 0-12 0c0 6-2 7-2 7h16s-2-1-2-7"/><path d="M13.7 20a2 2 0 0 1-3.4 0"/>',
    'user':     '<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
    'cart':     '<circle cx="9.5" cy="20" r="1.4"/><circle cx="18" cy="20" r="1.4"/><path d="M2.5 3h2.2l2.5 12.4a1.6 1.6 0 0 0 1.6 1.3h8.9a1.6 1.6 0 0 0 1.6-1.3L21 7H6"/>',
    'menu':     '<path d="M4 7h16"/><path d="M4 12h16"/><path d="M4 17h16"/>',
    'zap':      '<path d="M13 2L4.5 13.5H11l-1 8.5 8.5-11.5H12z"/>',
    'moto':     '<circle cx="5" cy="16.5" r="3.5"/><circle cx="19" cy="16.5" r="3.5"/><path d="M5 16.5h4l4-6h4l2 6"/><path d="M9.5 10.5H15"/>',
    'gear':     '<circle cx="12" cy="12" r="3"/><path d="M19.4 14.5a1.6 1.6 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.6 1.6 0 0 0-2.7 1.1v.3a2 2 0 1 1-4 0v-.2a1.6 1.6 0 0 0-2.8-1.1l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.6 1.6 0 0 0-1.1-2.7h-.3a2 2 0 1 1 0-4h.2a1.6 1.6 0 0 0 1.1-2.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.6 1.6 0 0 0 2.7-1.1v-.3a2 2 0 1 1 4 0v.2a1.6 1.6 0 0 0 2.8 1.1l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.6 1.6 0 0 0 1.1 2.7h.3a2 2 0 1 1 0 4h-.2a1.6 1.6 0 0 0-1.4 1z"/>',
    'flame':    '<path d="M12 2.5s5 4.2 5 8.5a5 5 0 0 1-10 0c0-1.6.8-3 1.7-4 .2 1.3 1 2.2 2 2.2 1.3 0 1.6-1.3 1.3-3-.2-1.4-.5-2.6 0-3.7z"/><path d="M12 22a6.5 6.5 0 0 0 6.5-6.5c0-1.4-.4-2.8-1-4"/>',
    'book':     '<path d="M3 4.5h6a3 3 0 0 1 3 3V20a2.5 2.5 0 0 0-2.5-2.5H3z"/><path d="M21 4.5h-6a3 3 0 0 0-3 3V20a2.5 2.5 0 0 1 2.5-2.5H21z"/>',
    'store':    '<path d="M4 9.5V20h16V9.5"/><path d="M3 4.5h18l1 5a3 3 0 0 1-5.5 1.7A3 3 0 0 1 12 11a3 3 0 0 1-4.5.2A3 3 0 0 1 2 9.5z"/><path d="M9.5 20v-5h5v5"/>',
    'layers':   '<path d="M12 2.8l9 4.7-9 4.7-9-4.7z"/><path d="M3 12.5l9 4.7 9-4.7"/><path d="M3 17l9 4.7 9-4.7"/>',
    'percent':  '<path d="M19 5L5 19"/><circle cx="7.5" cy="7.5" r="3"/><circle cx="16.5" cy="16.5" r="3"/>',
    'truck':    '<path d="M2 7.5h11v9H2z"/><path d="M13 10.5h4l3 3v3h-7z"/><circle cx="6" cy="18.5" r="1.8"/><circle cx="17" cy="18.5" r="1.8"/>',
    'shield':   '<path d="M12 2.8l8 3v5.6c0 4.6-3.2 8.6-8 9.8-4.8-1.2-8-5.2-8-9.8V5.8z"/><path d="M9 12l2.2 2.2L15.5 10"/>',
    'headset':  '<path d="M4 13v-1a8 8 0 0 1 16 0v1"/><path d="M4 13h2.5a1 1 0 0 1 1 1v4a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1z"/><path d="M20 13h-2.5a1 1 0 0 0-1 1v4a1 1 0 0 0 1 1H19a1 1 0 0 0 1-1z"/>',
    'rotate':   '<path d="M3 12a9 9 0 1 0 2.6-6.4"/><path d="M3 4.5V10h5.5"/>',
    'card':     '<rect x="2.5" y="5.5" width="19" height="13" rx="2.5"/><path d="M2.5 10h19"/>',
    'chev_r':   '<path d="M9 5l7 7-7 7"/>',
    'chev_l':   '<path d="M15 5l-7 7 7 7"/>',
    'plus':     '<path d="M12 5v14"/><path d="M5 12h14"/>',
    'close':    '<path d="M18 6L6 18"/><path d="M6 6l12 12"/>',
    'instagram':'<rect x="3.5" y="3.5" width="17" height="17" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17" cy="7" r="1"/>',
    'telegram': '<path d="M21 4.5L2.8 11.3l5.4 1.8L19 6.6l-8.2 8.1.3 5 2.6-3.6 4.2 3z"/>',
    'youtube':  '<rect x="2.5" y="5.5" width="19" height="13" rx="4"/><path d="M10.5 9.5l5 2.5-5 2.5z"/>',
    'linkedin': '<rect x="3.5" y="3.5" width="17" height="17" rx="3"/><path d="M8 11v6"/><circle cx="8" cy="8" r="1"/><path d="M12 17v-3.2a2.3 2.3 0 0 1 4.5 0V17"/><path d="M12 11v6"/>',
    'twitter':  '<path d="M21 5.4a7.4 7.4 0 0 1-2.1.6 3.7 3.7 0 0 0 1.6-2 7.4 7.4 0 0 1-2.3.9 3.7 3.7 0 0 0-6.3 3.4A10.5 10.5 0 0 1 4.3 4.4a3.7 3.7 0 0 0 1.1 5 3.7 3.7 0 0 1-1.7-.5 3.7 3.7 0 0 0 3 3.6 3.7 3.7 0 0 1-1.7.1 3.7 3.7 0 0 0 3.5 2.6A7.4 7.4 0 0 1 3 16.8a10.5 10.5 0 0 0 16.2-9.3z"/>',
}

SOCIAL = {'fa-instagram': 'instagram', 'fa-telegram': 'telegram', 'fa-youtube': 'youtube',
          'fa-linkedin-in': 'linkedin', 'fa-twitter': 'twitter'}


def icon(name, cls='icon'):
    body = ICONS.get(name)
    if not body:
        return ''
    return ('<svg class="%s" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" '
            'aria-hidden="true" focusable="false">%s</svg>' % (cls, body))


TOMAN = (
    '<svg width="0" height="0" aria-hidden="true" focusable="false" style="position:absolute">'
    '<symbol id="toman" viewBox="0 0 14 14"><path fill-rule="evenodd" d="M3.057 1.742L3.821 1l.78.75-.776.741-.768-.749zm3.23 2.48c0 .622-.16 1.111-.478 1.467-.201.221-.462.39-.783.505a3.251 3.251 0 01-1.083.163h-.555c-.421 0-.801-.074-1.139-.223a2.045 2.045 0 01-.9-.738A2.238 2.238 0 011 4.148c0-.059.001-.117.004-.176.03-.55.204-1.158.525-1.827l1.095.484c-.257.532-.397 1-.419 1.403-.002.04-.004.08-.004.12 0 .252.055.458.166.618a.887.887 0 00.5.354c.085.028.178.048.278.06.079.01.16.014.243.014h.555c.458 0 .769-.081.933-.244.14-.139.21-.383.21-.731V2.02h1.2v2.202zm5.433 3.184l-.72-.7.709-.706.735.707-.724.7zm-2.856.308c.542 0 .973.19 1.293.569.297.346.445.777.445 1.293v.364h.18v-.004h.41c.221 0 .377-.028.467-.084.093-.055.14-.14.14-.258v-.069c.004-.243.017-1.044 0-1.115L13 8.05v1.574a1.4 1.4 0 01-.287.863c-.306.405-.804.607-1.495.607h-.627c-.061.733-.434 1.257-1.117 1.573-.267.122-.58.21-.937.265a5.845 5.845 0 01-.914.067v-1.159c.612 0 1.072-.082 1.38-.247.25-.132.376-.298.376-.499h-.515c-.436 0-.807-.113-1.113-.339-.367-.273-.55-.667-.55-1.18 0-.488.122-.901.367-1.24.296-.415.728-.622 1.296-.622zm.533 2.226v-.364c0-.217-.048-.389-.143-.516a.464.464 0 00-.39-.187.478.478 0 00-.396.187.705.705 0 00-.136.449.65.65 0 00.003.067c.008.125.066.22.177.283.093.054.21.08.352.08h.533zM9.5 6.707l.72.7.724-.7L10.209 6l-.709.707zm-6.694 4.888h.03c.433-.01.745-.106.937-.29.024.012.065.035.12.068l.074.039.081.042c.135.073.261.133.379.18.345.146.67.22.977.22a1.216 1.216 0 00.87-.34c.3-.285.449-.714.449-1.286a2.19 2.19 0 00-.335-1.145c-.299-.457-.732-.685-1.3-.685-.502 0-.916.192-1.242.575-.113.132-.21.284-.294.456-.032.062-.06.125-.084.191a.504.504 0 00-.03.078 1.67 1.67 0 00-.022.06c-.103.309-.171.485-.205.53-.072.09-.214.14-.427.147-.123-.005-.209-.03-.256-.076-.057-.054-.085-.153-.085-.297V7l-1.201-.5v3.562c0 .261.048.496.143.703.071.158.168.296.29.413.123.118.266.211.43.28.198.084.42.13.665.136v.001h.036zm2.752-1.014a.778.778 0 00.044-.353.868.868 0 00-.165-.47c-.1-.134-.217-.201-.35-.201-.18 0-.33.103-.447.31-.042.071-.08.158-.114.262a2.434 2.434 0 00-.04.12l-.015.053-.015.046c.142.118.323.216.544.293.18.062.325.092.433.092.044 0 .086-.05.125-.152z" clip-rule="evenodd"/></symbol></svg>'
)


def money(num):
    return ('<span class="ltr">%s</span>'
            '<svg class="toman" viewBox="0 0 14 14" aria-hidden="true"><use href="#toman"/></svg>'
            '<span class="sr-only">تومان</span>' % e(num))


# ---------------------------------------------------------------------------
# The single product card. Every product on the page renders through this.
# ---------------------------------------------------------------------------

def product_card(p, eager=False):
    if not p.get('href') or not p.get('title'):
        return ''

    # A struck-through price and a discount badge appear only where the
    # catalogue actually carries a discount.
    discounted = bool(p.get('discount')) and bool(p.get('old')) and p['old'] != p.get('price')

    img = ('<img src="%s" alt="" %s decoding="async" width="300" height="300">'
           % (e(p['img']), 'loading="eager"' if eager else 'loading="lazy"')) if p.get('img') else ''

    row = ''
    if discounted:
        row = ('<div class="pprice-row"><span class="pdisc ltr">%s</span>'
               '<span class="pold">%s</span></div>' % (e(p['discount']), money(p['old'])))

    now = '<div class="pnow">%s</div>' % money(p['price']) if p.get('price') else ''

    return (
        '<article class="pcard">'
        '<div class="pimg">%s</div>'
        '<h3 class="pname"><a class="pcard-link" href="%s">%s</a></h3>'
        '<div class="pprice">%s%s</div>'
        '</article>'
    ) % (img, e(p['href']), e(p['title']), row, now)


def rail(items, eager_first=False):
    cards = ''.join(product_card(p, eager=(eager_first and i < 6))
                    for i, p in enumerate(items))
    return (
        '<div class="rail-wrap" data-rail>'
        '<button class="rail-nav rail-prev" data-rail-prev aria-label="قبلی" hidden>%s</button>'
        '<button class="rail-nav rail-next" data-rail-next aria-label="بعدی">%s</button>'
        '<div class="rail" data-rail-track>%s</div>'
        '</div>'
    ) % (icon('chev_r', 'icon-sm'), icon('chev_l', 'icon-sm'), cards)


def section(title, body, sub=None, more=None, sec_id=None):
    sub_html = '<p>%s</p>' % e(sub) if sub else ''
    more_html = ('<a class="chip-all" href="%s">مشاهده همه%s</a>'
                 % (e(more), icon('chev_l', 'icon-xs'))) if more else ''
    return (
        '<section class="sec"%s><div class="cont">'
        '<div class="sec-hd"><div><h2>%s</h2>%s</div>%s</div>%s'
        '</div></section>'
    ) % (' id="%s"' % e(sec_id) if sec_id else '', e(title), sub_html, more_html, body)


# ---------------------------------------------------------------------------
# Page
# ---------------------------------------------------------------------------

def build():
    d = DATA
    out = []
    w = out.append

    # Real HAPEEC photography behind the category circles and banner tiles:
    # a helmet tile shows a helmet, a glove tile shows gloves. No pictograms.
    CAT_PHOTO = {
        'موتور سیکلت': 'product01.jpg', 'موتور شهری': 'product03.jpg',
        'اسکوتر': 'product06.jpg', 'موتور کراس و آفرود': 'product05.jpg',
        'موتور برقی': 'product07.jpg', 'کلاه کاسکت و عینک': 'product11.jpg',
        'دستکش موتورسیکلت': 'product13.jpg', 'لاستیک موتورسیکلت': 'product15.jpg',
        'روغن موتور سیکلت': 'product17.jpg', 'شمع موتورسیکلت': 'product23.jpg',
        'چراغ و لامپ موتور': 'product25.jpg', 'قفل و دزدگیر موتور': 'product29.jpg',
        'لوازم یدکی': 'product33.jpg', 'لوازم مصرفی': 'product35.jpg',
    }

    w('<!DOCTYPE html>')
    w('<html lang="fa" dir="rtl">')
    w('<head>')
    w('<meta charset="utf-8">')
    w('<meta name="viewport" content="width=device-width, initial-scale=1">')
    w('<title>هپیک | HAPEEC — پلتفرم موتورسیکلت</title>')
    w('<meta name="description" content="%s">' % e(d['footer']['desc']))
    w('<link rel="stylesheet" href="assets/css/tokens.css">')
    w('<link rel="stylesheet" href="assets/css/home.css">')
    w('</head>')
    w('<body>')
    w(TOMAN)
    w('<a class="skip-link" href="#main">رفتن به محتوای اصلی</a>')

    # ---- announcement strip, edge to edge --------------------------------
    ann = d['announcement']
    if ann.get('img'):
        w('<a class="ann" href="%s"><img src="%s" alt="%s" fetchpriority="high"></a>'
          % (e(ann.get('href') or BASE + '/fa/flash-sale'), e(ann['img']), e(ann['alt'])))

    # ---- header row 1 ----------------------------------------------------
    w('<header class="hdr">')
    w('<div class="cont hdr-row">')
    w('<button class="hdr-menu" data-drawer-open aria-expanded="false" aria-controls="drawer" '
      'aria-label="منو">%s</button>' % icon('menu'))
    w('<a class="logo" href="%s/fa" aria-label="هپیک — صفحه اصلی">'
      '<img src="assets/img/hapeec-wordmark.png" alt="HAPEEC" width="433" height="73"></a>' % BASE)

    w('<div class="search-wrap">')
    w('<form class="search" action="%s/fa/products" method="get" role="search">' % BASE)
    w('<button class="search-btn" type="submit" aria-label="جستجو">%s</button>' % icon('search', 'icon-sm'))
    w('<input type="search" name="q" placeholder="جستجو" aria-label="جستجو در محصولات" autocomplete="off">')
    w('</form>')
    w('<form action="%s/fa/products" method="post" enctype="multipart/form-data" hidden>'
      '<input type="file" name="image" accept="image/*" data-image-search-input hidden></form>' % BASE)
    w('<button class="cam" type="button" data-image-search="%s/fa/products" '
      'aria-label="جستجو با عکس" title="جستجو با عکس">%s</button>' % (BASE, icon('camera', 'icon-sm')))
    w('</div>')

    w('<div class="acts">')
    w('<a class="act" href="%s/fa/notifications" aria-label="اعلان‌ها"><span class="act-ico">%s</span></a>'
      % (BASE, icon('bell', 'icon-sm')))
    w('<a class="act act-login" href="%s/fa/login">%s<span class="act-txt">ورود | ثبت‌نام</span></a>'
      % (BASE, icon('user', 'icon-sm')))
    w('<span class="act-sep" aria-hidden="true"></span>')
    w('<a class="act" href="%s/fa/cart" aria-label="سبد خرید">'
      '<span class="act-ico">%s<span class="act-badge" hidden>0</span></span></a>'
      % (BASE, icon('cart', 'icon-sm')))
    w('</div>')
    w('</div>')
    w('</header>')

    # ---- header row 2: navigation. Its two ends set the content guard ----
    NAV = [
        ('شگفت‌انگیزها', 'zap', BASE + '/fa/flash-sale'),
        ('موتورسیکلت', 'moto', BASE + '/fa/products?type=motorcycle'),
        ('لوازم یدکی', 'gear', BASE + '/fa/products?type=parts'),
        ('پرفروش‌ترین‌ها', 'flame', BASE + '/fa/products?sort=bestselling'),
        ('مجله', 'book', BASE + '/fa/blogs'),
    ]
    w('<nav class="nav" aria-label="میان‌برها"><div class="cont nav-row">')
    w('<button class="nav-link" data-drawer-open aria-expanded="false" aria-controls="drawer">'
      '%s<span>دسته‌بندی کالاها</span></button>' % icon('menu', 'icon-sm'))
    w('<span class="nav-sep" aria-hidden="true"></span>')
    w('<ul class="nav-list">')
    for label, ico, href in NAV:
        w('<li><a class="nav-link" href="%s">%s<span>%s</span></a></li>'
          % (e(href), icon(ico, 'icon-sm'), e(label)))
    w('</ul>')
    if d.get('sell_cta'):
        w('<span class="nav-sep nav-sep-end" aria-hidden="true"></span>')
        w('<a class="nav-link nav-sell" href="%s">%s<span>%s</span></a>'
          % (e(d['sell_cta']['href']), icon('store', 'icon-sm'), e(d['sell_cta']['text'])))
    w('</div></nav>')

    w('<main id="main">')

    # ---- hero, edge to edge ----------------------------------------------
    if d['hero']:
        w('<section class="hero" data-hero aria-label="بنر اصلی"><div class="hero-track">')
        for i, s in enumerate(d['hero']):
            w('<div class="hero-slide" aria-hidden="%s"><img src="%s" alt="%s" %s decoding="async"></div>'
              % ('false' if i == 0 else 'true', e(s['img']), e(s['alt']),
                 'fetchpriority="high"' if i == 0 else 'loading="lazy"'))
        w('</div>')
        w('<button class="hero-nav hero-prev" aria-label="اسلاید قبلی">%s</button>' % icon('chev_r', 'icon-sm'))
        w('<button class="hero-nav hero-next" aria-label="اسلاید بعدی">%s</button>' % icon('chev_l', 'icon-sm'))
        w('<div class="hero-dots">')
        for i in range(len(d['hero'])):
            w('<button class="hero-dot" aria-current="%s" aria-label="اسلاید %d"></button>'
              % ('true' if i == 0 else 'false', i + 1))
        w('</div></section>')

    # ---- story circles: 8 fixed + «بیشتر» --------------------------------
    stories, VISIBLE = d['stories'], 8
    w('<section class="sec stories" aria-label="هایلایت‌ها"><div class="cont"><div class="story-rail">')
    for i, s in enumerate(stories):
        w('<button type="button" class="story" data-story-id="%s" data-slides="%s"%s>'
          '<span class="story-ring"><span class="story-img">'
          '<img src="%s" alt="" loading="lazy" width="84" height="84"></span></span>'
          '<span class="story-label">%s</span></button>'
          % (e(s['id']), e(json.dumps(s['slides'], ensure_ascii=False)),
             ' hidden data-story-hidden' if i >= VISIBLE else '', e(s['img']), e(s['label'])))
    if len(stories) > VISIBLE:
        w('<button class="story story-more" data-stories-more aria-label="نمایش هایلایت‌های بیشتر">'
          '<span class="story-ring"><span class="story-img">%s</span></span>'
          '<span class="story-label">بیشتر</span></button>' % icon('plus', 'icon-sm'))
    w('</div></div></section>')

    # ---- campaign block: Digikala's شگفت‌انگیز bar, in HAPEEC orange ------
    fs = d['flash']
    unit = '<span class="timer-unit ltr" data-cd-%s>--</span>'
    timer = ('<div class="timer" data-countdown="%s" role="timer" aria-label="زمان باقی‌مانده">'
             '%s<span class="timer-sep">:</span>%s<span class="timer-sep">:</span>%s</div>'
             % (e(str(fs['end'])), unit % 's', unit % 'm', unit % 'h')) if fs.get('end') else ''

    w('<section class="sec" id="flash-sale"><div class="cont"><div class="campaign">')
    w('<div class="campaign-side">')
    w('<span class="campaign-mark">%s</span>' % icon('percent', 'campaign-mark'))
    w('<h2>شگفت‌انگیز</h2>')
    w(timer)
    w('<a class="btn-ghost" href="%s">مشاهده همه%s</a>' % (e(fs['cta_href']), icon('chev_l', 'icon-xs')))
    w('</div>')
    w('<div class="campaign-rail" data-rail-track>')
    for i, p in enumerate(d['grids']['flashGrid']):
        w(product_card(p, eager=i < 6))
    w('</div>')
    w('</div></div></section>')

    # ---- four banner tiles, no captions -----------------------------------
    TILES = [
        ('موتورسیکلت', 'product01.jpg', '/fa/products?categories=1'),
        ('کلاه کاسکت و عینک', 'product11.jpg', '/fa/products?categories=9'),
        ('دستکش موتورسیکلت', 'product13.jpg', '/fa/products?categories=10'),
        ('روغن و لوازم مصرفی', 'product17.jpg', '/fa/products?categories=5'),
    ]
    w('<section class="sec" aria-label="بنرهای تبلیغاتی"><div class="cont"><div class="banners-4">')
    for alt, img, href in TILES:
        w('<a class="banner" href="%s" aria-label="%s"><img src="%s%s" alt="%s" loading="lazy"></a>'
          % (e(BASE + href), e(alt), PHOTO, img, e(alt)))
    w('</div></div></section>')

    # ---- categories: real photography, Digikala's circle grid -------------
    cats = [c for c in d['categories'] if c['name'] in CAT_PHOTO][:10]
    w(section('دسته‌بندی‌ها',
              '<div class="cats">' + ''.join(
                  '<a class="cat" href="%s"><span class="cat-img">'
                  '<img src="%s%s" alt="" loading="lazy"></span><h3>%s</h3></a>'
                  % (e(c['href']), PHOTO, CAT_PHOTO[c['name']], e(c['name'])) for c in cats
              ) + '</div>',
              more=BASE + '/fa/products'))

    # ---- motorcycles ------------------------------------------------------
    w(section('خرید موتورسیکلت', rail(d['grids']['motorGrid']['items']),
              sub='نو و کارکرده، با ضمانت اصالت و ارسال سراسری',
              more=BASE + '/fa/products?type=motorcycle', sec_id='motorcycles'))

    # ---- compatibility chips ---------------------------------------------
    w(section('خرید بر اساس موتور شما',
              '<div class="chips">' + ''.join(
                  '<a class="chip" href="%s">%s<span>%s</span>%s</a>'
                  % (e(m['href']), icon('layers' if not m['cc'] else 'moto', 'icon-xs'), e(m['name']),
                     '<span class="chip-cc ltr">%s</span>' % e(m['cc']) if m['cc'] else '')
                  for m in d['moto']) + '</div>',
              sub='موتور خود را انتخاب کنید تا قطعات سازگار را اول ببینید'))

    # ---- two wide banners -------------------------------------------------
    WIDE = [(b['href'], b['img'], b['alt']) for b in d['mid_banners'][:1]]
    WIDE.append((BASE + '/fa/products?type=parts', PHOTO + 'product33.jpg', 'قطعات و لوازم یدکی'))
    w('<section class="sec" aria-label="بنرهای کمپین"><div class="cont"><div class="banners-2">')
    for href, img, alt in WIDE:
        w('<a class="banner" href="%s"><img src="%s" alt="%s" loading="lazy"></a>'
          % (e(href), e(img), e(alt)))
    w('</div></div></section>')

    # ---- parts ------------------------------------------------------------
    w(section('قطعات و لوازم جانبی', rail(d['grids']['partGrid']['items']),
              sub='لاستیک، روغن، کلاه کاسکت و قطعات مصرفی',
              more=BASE + '/fa/products?type=parts', sec_id='parts'))

    # ---- weekly offers ----------------------------------------------------
    w(section('پیشنهادات این هفته', rail(d['grids']['prodGrid']['items']),
              more=BASE + '/fa/products'))

    # ---- bestsellers: Digikala's numbered compact grid --------------------
    best = (d['grids']['partGrid']['items'] + d['grids']['motorGrid']['items'])[:12]
    w(section('پرفروش‌ترین‌ها',
              '<div class="best">' + ''.join(
                  '<a class="best-item" href="%s"><span class="best-rank ltr">%d</span>'
                  '<span class="best-title">%s</span>'
                  '<span class="best-thumb"><img src="%s" alt="" loading="lazy"></span></a>'
                  % (e(p['href']), i + 1, e(p['title']), e(p['img']))
                  for i, p in enumerate(best) if p.get('href')) + '</div>',
              more=BASE + '/fa/products?sort=bestselling'))

    # ---- brands: marks only --------------------------------------------
    w(section('محبوب‌ترین برندها',
              '<div class="brands-wrap" data-rail>'
              '<button class="rail-nav rail-prev" data-rail-prev aria-label="قبلی" hidden>%s</button>'
              '<div class="brands" data-rail-track>%s</div>'
              '<button class="rail-nav rail-next" data-rail-next aria-label="بعدی">%s</button></div>'
              % (icon('chev_r', 'icon-sm'),
                 ''.join('<a class="brand" href="%s" aria-label="%s">%s</a>'
                         % (e(b['href']), e(b['name']),
                            '<img src="%s" alt="%s" loading="lazy">' % (e(b['logo']), e(b['name']))
                            if b.get('logo') else
                            '<span class="brand-name ltr">%s</span>' % e(b['name']))
                         for b in d['brands']),
                 icon('chev_l', 'icon-sm'))))

    # ---- magazine ---------------------------------------------------------
    w(section('مجله موتور',
              '<div class="posts">' + ''.join(
                  '<article class="post"><a href="%s">'
                  '<img src="%s" alt="" loading="lazy" width="320" height="200">'
                  '<h3>%s</h3></a><time>%s</time></article>'
                  % (e(p['href']), e(p['img']), e(p['title']), e(p['date']))
                  for p in d['blog'][:8]) + '</div>',
              more=BASE + '/fa/blogs'))

    w('</main>')

    # ---- footer -----------------------------------------------------------
    f = d['footer']
    SERVICES = [('truck', 'ارسال سراسری'), ('rotate', 'ضمانت ۷ روزه بازگشت'),
                ('shield', 'ضمانت اصالت کالا'), ('card', 'پرداخت امن'),
                ('headset', 'پشتیبانی ۲۴/۷')]
    w('<footer class="ft"><div class="cont">')
    w('<div class="ft-services">')
    for ico, label in SERVICES:
        w('<div class="ft-service">%s<span>%s</span></div>' % (icon(ico), e(label)))
    w('</div>')

    w('<div class="ft-top">')
    w('<div><div class="ft-logo">'
      '<img src="assets/img/hapeec-wordmark-lockup.png" alt="HAPEEC — Motorcycle Platform" '
      'width="434" height="121"></div>')
    w('<p class="ft-desc">%s</p>' % e(f['desc']))
    w('<div class="ft-socials">')
    for s in f['socials']:
        w('<a class="fsoc" href="%s" aria-label="%s">%s</a>'
          % (e(s['href']), e(s['title']), icon(SOCIAL.get(s['icon'], 'store'), 'icon-sm')))
    w('</div></div>')
    half = (len(f['links']) + 1) // 2
    for col, links in (('اطلاعات', f['links'][:half]), ('خدمات', f['links'][half:])):
        w('<div class="ft-col"><h3>%s</h3><nav class="ft-links">' % e(col))
        for l in links:
            w('<a href="%s">%s</a>' % (e(l['href']), e(l['text'])))
        w('</nav></div>')
    w('</div>')
    w('<div class="ft-bot"><span>%s</span></div>' % e(f['copy']))
    w('</div></footer>')

    # ---- mobile drawer ----------------------------------------------------
    w('<div class="scrim" data-scrim data-open="false"></div>')
    w('<nav class="drawer" id="drawer" data-drawer data-open="false" aria-label="منوی موبایل">')
    w('<div class="drawer-head">'
      '<img src="assets/img/hapeec-wordmark.png" alt="HAPEEC" width="433" height="73">'
      '<button data-drawer-close aria-label="بستن منو">%s</button></div>' % icon('close', 'icon-sm'))
    w('<div class="drawer-body">')
    w('<div class="drawer-label">دسته‌بندی</div>')
    for i, g in enumerate(d['mega']):
        sid = 'drw-%d' % i
        w('<button class="drawer-link" data-drawer-group aria-expanded="false" aria-controls="%s">'
          '%s<span>%s</span><span class="drawer-chev">%s</span></button>'
          % (sid, icon('layers', 'icon-sm'), e(g['title']), icon('chev_l', 'icon-xs')))
        w('<div class="drawer-sub" id="%s" data-open="false">' % sid)
        w('<a href="%s">مشاهده همه %s</a>' % (e(g['href']), e(g['title'])))
        for l in g['links']:
            w('<a href="%s">%s</a>' % (e(l['href']), e(l['text'])))
        w('</div>')
    w('<div class="drawer-label">میان‌برها</div>')
    for label, ico, href in NAV:
        w('<a class="drawer-link" href="%s">%s<span>%s</span></a>' % (e(href), icon(ico, 'icon-sm'), e(label)))
    w('<div class="drawer-label">اطلاعات</div>')
    for l in f['links']:
        w('<a class="drawer-link" href="%s">%s</a>' % (e(l['href']), e(l['text'])))
    w('</div></nav>')

    w('<script src="assets/js/home.js" defer></script>')
    w('</body></html>')
    return '\n'.join(out)


if __name__ == '__main__':
    path = os.path.join(HERE, 'index.html')
    with open(path, 'w', encoding='utf-8') as fh:
        fh.write(build())
    print('wrote', path, os.path.getsize(path), 'bytes')
