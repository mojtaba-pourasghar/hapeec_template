#!/usr/bin/env python3
"""Render the HAPEEC homepage from the content extracted off the live site.

The point of generating rather than hand-writing the markup is that every
product on the page goes through one `product_card()` template, so there is a
single card implementation to keep consistent — the same constraint the Blade
version carries (see README.md).

    python3 build.py        # writes index.html next to this file
"""

import html
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = json.load(open(os.path.join(HERE, 'data', 'home.json'), encoding='utf-8'))

BASE = 'https://test.happenengrave.com'


def e(s):
    return html.escape(s or '', quote=True)


# ---------------------------------------------------------------------------
# Outline icon set. One family, stroked, never filled — so the header, the
# navigation and the footer cannot drift into mixed icon styles.
# ---------------------------------------------------------------------------

ICONS = {
    'search':    '<circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/>',
    'camera':    '<path d="M3 8.5A1.5 1.5 0 0 1 4.5 7h2.2a1 1 0 0 0 .83-.45l.94-1.4A1 1 0 0 1 9.3 4.7h5.4a1 1 0 0 1 .83.45l.94 1.4a1 1 0 0 0 .83.45h2.2A1.5 1.5 0 0 1 21 8.5v9A1.5 1.5 0 0 1 19.5 19h-15A1.5 1.5 0 0 1 3 17.5z"/><circle cx="12" cy="12.8" r="3.3"/>',
    'bell':      '<path d="M18 8a6 6 0 1 0-12 0c0 6-2 7-2 7h16s-2-1-2-7"/><path d="M13.7 20a2 2 0 0 1-3.4 0"/>',
    'user':      '<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
    'cart':      '<circle cx="9.5" cy="20" r="1.4"/><circle cx="18" cy="20" r="1.4"/><path d="M2.5 3h2.2l2.5 12.4a1.6 1.6 0 0 0 1.6 1.3h8.9a1.6 1.6 0 0 0 1.6-1.3L21 7H6"/>',
    'menu':      '<path d="M4 7h16"/><path d="M4 12h16"/><path d="M4 17h16"/>',
    'zap':       '<path d="M13 2L4.5 13.5H11l-1 8.5 8.5-11.5H12z"/>',
    'flame':     '<path d="M12 2.5s5 4.2 5 8.5a5 5 0 0 1-10 0c0-1.6.8-3 1.7-4 .2 1.3 1 2.2 2 2.2 1.3 0 1.6-1.3 1.3-3-.2-1.4-.5-2.6 0-3.7z"/><path d="M12 22a6.5 6.5 0 0 0 6.5-6.5c0-1.4-.4-2.8-1-4"/>',
    'book':      '<path d="M3 4.5h6a3 3 0 0 1 3 3V20a2.5 2.5 0 0 0-2.5-2.5H3z"/><path d="M21 4.5h-6a3 3 0 0 0-3 3V20a2.5 2.5 0 0 1 2.5-2.5H21z"/>',
    'store':     '<path d="M4 9.5V20h16V9.5"/><path d="M3 4.5h18l1 5a3 3 0 0 1-5.5 1.7A3 3 0 0 1 12 11a3 3 0 0 1-4.5.2A3 3 0 0 1 2 9.5z"/><path d="M9.5 20v-5h5v5"/>',
    'tag':       '<path d="M20.5 13.3l-7.2 7.2a1.6 1.6 0 0 1-2.3 0l-7.5-7.5V3.5h9.5l7.5 7.5a1.6 1.6 0 0 1 0 2.3z"/><circle cx="8" cy="8" r="1.4"/>',
    'chev_r':    '<path d="M9 5l7 7-7 7"/>',
    'chev_l':    '<path d="M15 5l-7 7 7 7"/>',
    'arrow_l':   '<path d="M19 12H5"/><path d="M11 18l-6-6 6-6"/>',
    'plus':      '<path d="M12 5v14"/><path d="M5 12h14"/>',
    'lock':      '<rect x="4" y="10.5" width="16" height="10" rx="2"/><path d="M8 10.5V7a4 4 0 0 1 8 0v3.5"/>',
    'award':     '<circle cx="12" cy="9" r="5.5"/><path d="M8.6 13.6L7.5 21l4.5-2.4L16.5 21l-1.1-7.4"/>',
    'rotate':    '<path d="M3 12a9 9 0 1 0 2.6-6.4"/><path d="M3 4.5V10h5.5"/>',
    'headset':   '<path d="M4 13v-1a8 8 0 0 1 16 0v1"/><path d="M4 13h2.5a1 1 0 0 1 1 1v4a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1z"/><path d="M20 13h-2.5a1 1 0 0 0-1 1v4a1 1 0 0 0 1 1H19a1 1 0 0 0 1-1z"/>',
    'layers':    '<path d="M12 2.8l9 4.7-9 4.7-9-4.7z"/><path d="M3 12.5l9 4.7 9-4.7"/><path d="M3 17l9 4.7 9-4.7"/>',
    'moto':      '<circle cx="5" cy="16.5" r="3.5"/><circle cx="19" cy="16.5" r="3.5"/><path d="M5 16.5h4l4-6h4l2 6"/><path d="M9.5 10.5H15"/>',
    'gear':      '<circle cx="12" cy="12" r="3"/><path d="M19.4 14.5a1.6 1.6 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.6 1.6 0 0 0-2.7 1.1v.3a2 2 0 1 1-4 0v-.2a1.6 1.6 0 0 0-2.8-1.1l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.6 1.6 0 0 0-1.1-2.7h-.3a2 2 0 1 1 0-4h.2a1.6 1.6 0 0 0 1.1-2.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.6 1.6 0 0 0 2.7-1.1v-.3a2 2 0 1 1 4 0v.2a1.6 1.6 0 0 0 2.8 1.1l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.6 1.6 0 0 0 1.1 2.7h.3a2 2 0 1 1 0 4h-.2a1.6 1.6 0 0 0-1.4 1z"/>',
    'close':     '<path d="M18 6L6 18"/><path d="M6 6l12 12"/>',
    'instagram': '<rect x="3.5" y="3.5" width="17" height="17" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17" cy="7" r="1"/>',
    'telegram':  '<path d="M21 4.5L2.8 11.3l5.4 1.8L19 6.6l-8.2 8.1.3 5 2.6-3.6 4.2 3z"/>',
    'youtube':   '<rect x="2.5" y="5.5" width="19" height="13" rx="4"/><path d="M10.5 9.5l5 2.5-5 2.5z"/>',
    'linkedin':  '<rect x="3.5" y="3.5" width="17" height="17" rx="3"/><path d="M8 11v6"/><circle cx="8" cy="8" r="1"/><path d="M12 17v-3.2a2.3 2.3 0 0 1 4.5 0V17"/><path d="M12 11v6"/>',
    'twitter':   '<path d="M21 5.4a7.4 7.4 0 0 1-2.1.6 3.7 3.7 0 0 0 1.6-2 7.4 7.4 0 0 1-2.3.9 3.7 3.7 0 0 0-6.3 3.4A10.5 10.5 0 0 1 4.3 4.4a3.7 3.7 0 0 0 1.1 5 3.7 3.7 0 0 1-1.7-.5 3.7 3.7 0 0 0 3 3.6 3.7 3.7 0 0 1-1.7.1 3.7 3.7 0 0 0 3.5 2.6A7.4 7.4 0 0 1 3 16.8a10.5 10.5 0 0 0 16.2-9.3z"/>',
}

# Font Awesome class -> outline icon, so the live markup's icon choices survive.
FA_MAP = {
    'fa-bolt': 'zap', 'fa-motorcycle': 'moto', 'fa-gears': 'gear',
    'fa-fire': 'flame', 'fa-newspaper': 'book',
}

SOCIAL_MAP = {
    'fa-instagram': 'instagram', 'fa-telegram': 'telegram', 'fa-youtube': 'youtube',
    'fa-linkedin-in': 'linkedin', 'fa-twitter': 'twitter',
}


def icon(name, cls='icon'):
    body = ICONS.get(name)
    if not body:
        return ''
    return ('<svg class="%s" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" '
            'aria-hidden="true" focusable="false">%s</svg>' % (cls, body))


TOMAN_SYMBOL = (
    '<svg width="0" height="0" aria-hidden="true" focusable="false" style="position:absolute">'
    '<symbol id="toman" viewBox="0 0 14 14"><path fill-rule="evenodd" d="M3.057 1.742L3.821 1l.78.75-.776.741-.768-.749zm3.23 2.48c0 .622-.16 1.111-.478 1.467-.201.221-.462.39-.783.505a3.251 3.251 0 01-1.083.163h-.555c-.421 0-.801-.074-1.139-.223a2.045 2.045 0 01-.9-.738A2.238 2.238 0 011 4.148c0-.059.001-.117.004-.176.03-.55.204-1.158.525-1.827l1.095.484c-.257.532-.397 1-.419 1.403-.002.04-.004.08-.004.12 0 .252.055.458.166.618a.887.887 0 00.5.354c.085.028.178.048.278.06.079.01.16.014.243.014h.555c.458 0 .769-.081.933-.244.14-.139.21-.383.21-.731V2.02h1.2v2.202zm5.433 3.184l-.72-.7.709-.706.735.707-.724.7zm-2.856.308c.542 0 .973.19 1.293.569.297.346.445.777.445 1.293v.364h.18v-.004h.41c.221 0 .377-.028.467-.084.093-.055.14-.14.14-.258v-.069c.004-.243.017-1.044 0-1.115L13 8.05v1.574a1.4 1.4 0 01-.287.863c-.306.405-.804.607-1.495.607h-.627c-.061.733-.434 1.257-1.117 1.573-.267.122-.58.21-.937.265a5.845 5.845 0 01-.914.067v-1.159c.612 0 1.072-.082 1.38-.247.25-.132.376-.298.376-.499h-.515c-.436 0-.807-.113-1.113-.339-.367-.273-.55-.667-.55-1.18 0-.488.122-.901.367-1.24.296-.415.728-.622 1.296-.622zm.533 2.226v-.364c0-.217-.048-.389-.143-.516a.464.464 0 00-.39-.187.478.478 0 00-.396.187.705.705 0 00-.136.449.65.65 0 00.003.067c.008.125.066.22.177.283.093.054.21.08.352.08h.533zM9.5 6.707l.72.7.724-.7L10.209 6l-.709.707zm-6.694 4.888h.03c.433-.01.745-.106.937-.29.024.012.065.035.12.068l.074.039.081.042c.135.073.261.133.379.18.345.146.67.22.977.22a1.216 1.216 0 00.87-.34c.3-.285.449-.714.449-1.286a2.19 2.19 0 00-.335-1.145c-.299-.457-.732-.685-1.3-.685-.502 0-.916.192-1.242.575-.113.132-.21.284-.294.456-.032.062-.06.125-.084.191a.504.504 0 00-.03.078 1.67 1.67 0 00-.022.06c-.103.309-.171.485-.205.53-.072.09-.214.14-.427.147-.123-.005-.209-.03-.256-.076-.057-.054-.085-.153-.085-.297V7l-1.201-.5v3.562c0 .261.048.496.143.703.071.158.168.296.29.413.123.118.266.211.43.28.198.084.42.13.665.136v.001h.036zm2.752-1.014a.778.778 0 00.044-.353.868.868 0 00-.165-.47c-.1-.134-.217-.201-.35-.201-.18 0-.33.103-.447.31-.042.071-.08.158-.114.262a2.434 2.434 0 00-.04.12l-.015.053-.015.046c.142.118.323.216.544.293.18.062.325.092.433.092.044 0 .086-.05.125-.152z" clip-rule="evenodd"/></symbol></svg>'
)


def price(num):
    """Price + the toman glyph, kept LTR inside RTL copy."""
    return ('<span class="ltr"><span class="price-num">%s</span>'
            '<svg class="toman" viewBox="0 0 14 14" aria-hidden="true" focusable="false">'
            '<use href="#toman"/></svg></span>'
            '<span class="sr-only">تومان</span>' % e(num))


# ---------------------------------------------------------------------------
# The single product card. Every product row on the page renders through this.
# ---------------------------------------------------------------------------

def product_card(p, eager=False):
    if not p.get('href') or not p.get('title'):
        return ''

    # A struck-through original price and a discount badge are shown only when
    # the catalogue actually carries a discount for this product.
    has_discount = bool(p.get('discount')) and bool(p.get('old')) and p['old'] != p.get('price')

    img = ('<img src="%s" alt="" %s decoding="async" width="300" height="300">'
           % (e(p['img']), 'loading="eager"' if eager else 'loading="lazy"')) if p.get('img') else ''

    disc = '<span class="pdisc ltr">%s</span>' % e(p['discount']) if has_discount else ''
    old = '<span class="pold">%s</span>' % price(p['old']) if has_discount else ''
    now = '<span class="pnow">%s</span>' % price(p['price']) if p.get('price') else ''

    return (
        '<article class="pcard">'
        '<div class="pimg">%s</div>'
        '<div class="pbody">'
        '<h3 class="pname"><a class="pcard-link" href="%s">%s</a></h3>'
        '<div class="pprice">%s<span class="pprice-col">%s%s</span></div>'
        '</div>'
        '</article>'
    ) % (img, e(p['href']), e(p['title']), disc, now, old)


def product_rail(rail_id, items, eager_first=False):
    cards = ''.join(product_card(p, eager=(eager_first and i < 5))
                    for i, p in enumerate(items))
    return (
        '<div class="prod-rail-wrap" data-rail>'
        '<button class="rail-nav rail-prev" data-rail-prev aria-label="قبلی" hidden>%s</button>'
        '<button class="rail-nav rail-next" data-rail-next aria-label="بعدی">%s</button>'
        '<div class="prod-rail" id="%s" data-rail-track>%s</div>'
        '</div>'
    ) % (icon('chev_r', 'icon-sm'), icon('chev_l', 'icon-sm'), rail_id, cards)


def section(title_plain, title_em, body, sec_id=None, more=None):
    hd_more = ('<a class="sec-more" href="%s">%s%s</a>'
               % (e(more['href']), e(more['text']), icon('chev_l', 'icon-sm'))) if more else ''
    return (
        '<section class="sec"%s>'
        '<div class="cont">'
        '<div class="sec-hd"><h2>%s <em>%s</em></h2>%s</div>'
        '%s'
        '</div>'
        '</section>'
    ) % (' id="%s"' % e(sec_id) if sec_id else '', e(title_plain), e(title_em), hd_more, body)


def promo_banner(title, sub, cta_text, cta_href, countdown=None):
    timer = ''
    if countdown:
        unit = ('<div class="timer-unit"><span class="timer-num ltr" data-cd-%s>--</span>'
                '<span class="timer-lbl">%s</span></div>')
        timer = (
            '<div class="promo-timer" data-countdown="%s" role="timer" aria-label="زمان باقی‌مانده">'
            '%s<span class="timer-sep">:</span>%s<span class="timer-sep">:</span>%s'
            '</div>'
        ) % (e(str(countdown)), unit % ('s', 'ثانیه'), unit % ('m', 'دقیقه'), unit % ('h', 'ساعت'))

    return (
        '<div class="promo">'
        '<div class="promo-txt"><h2>%s</h2><p>%s</p></div>'
        '%s'
        '<a class="btn btn-on-orange" href="%s">%s%s</a>'
        '</div>'
    ) % (e(title), e(sub), timer, e(cta_href), e(cta_text), icon('arrow_l', 'icon-sm'))


# ---------------------------------------------------------------------------
# Page
# ---------------------------------------------------------------------------

def build():
    d = DATA
    out = []
    w = out.append

    # -- head ---------------------------------------------------------------
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
    w(TOMAN_SYMBOL)
    w('<a class="skip-link" href="#main">رفتن به محتوای اصلی</a>')

    # -- row 1: full-width announcement -------------------------------------
    ann = d['announcement']
    if ann.get('img'):
        href = ann.get('href') or (BASE + '/fa/flash-sale')
        w('<a class="ann" href="%s"><img src="%s" alt="%s" fetchpriority="high" width="1440" height="90"></a>'
          % (e(href), e(ann['img']), e(ann['alt'])))

    # -- row 2: header ------------------------------------------------------
    w('<header class="hdr">')
    w('<div class="cont hdr-main">')
    w('<a class="logo" href="%s/fa" aria-label="هپیک — صفحه اصلی">'
      '<img src="assets/img/hapeec-wordmark.png" alt="HAPEEC" width="433" height="73"></a>' % BASE)

    w('<button class="hdr-cats" data-drawer-open aria-expanded="false" aria-controls="drawer">'
      '%s<span class="hdr-cats-text">دسته‌بندی‌ها</span></button>' % icon('menu'))

    # search, with the camera as its own control immediately beside the field
    w('<div class="hdr-search">')
    w('<form class="srch" action="%s/fa/products" method="get" role="search">' % BASE)
    w('<button class="srch-btn" type="submit" aria-label="جستجو">%s</button>' % icon('search'))
    w('<input class="srch-inp" type="search" name="q" placeholder="جستجو در هپیک" '
      'aria-label="جستجو در محصولات" autocomplete="off">')
    w('</form>')
    w('<form class="srch-img" action="%s/fa/products" method="post" enctype="multipart/form-data" hidden>'
      '<input type="file" name="image" accept="image/*" data-image-search-input hidden></form>' % BASE)
    w('<button class="cam-btn" type="button" data-image-search="%s/fa/products" '
      'aria-label="جستجو با عکس" title="جستجو با عکس">%s</button>' % (BASE, icon('camera')))
    w('</div>')

    # account actions
    w('<div class="hdr-acts">')
    w('<a class="ha" href="%s/fa/notifications" aria-label="اعلان‌ها">'
      '<span class="ha-ico">%s</span></a>' % (BASE, icon('bell')))
    w('<a class="ha ha-login" href="%s/fa/login">%s<span class="ha-txt">ورود / ثبت‌نام</span></a>'
      % (BASE, icon('user')))
    w('<a class="ha" href="%s/fa/cart" aria-label="سبد خرید">'
      '<span class="ha-ico">%s<span class="ha-badge" hidden>0</span></span>'
      '<span class="ha-txt">سبد</span></a>' % (BASE, icon('cart')))
    w('</div>')
    w('</div>')
    w('</header>')

    # -- row 3: navigation --------------------------------------------------
    w('<nav class="nav" aria-label="میان‌برها">')
    w('<div class="cont nav-in">')
    w('<ul class="nav-list">')
    w('<li><button class="nav-link" data-drawer-open aria-expanded="false" aria-controls="drawer">'
      '%s<span>دسته‌بندی کالاها</span></button></li>' % icon('menu'))
    for item in d['subnav']:
        name = FA_MAP.get(item['icon'], 'tag')
        w('<li><a class="nav-link" href="%s">%s<span>%s</span></a></li>'
          % (e(item['href']), icon(name), e(item['text'])))
    w('</ul>')
    if d.get('sell_cta'):
        w('<span class="nav-divider" aria-hidden="true"></span>')
        w('<a class="nav-sell" href="%s">%s<span>%s</span></a>'
          % (e(d['sell_cta']['href']), icon('store'), e(d['sell_cta']['text'])))
    w('</div>')
    w('</nav>')

    w('<main id="main">')

    # -- hero, full-bleed ---------------------------------------------------
    if d['hero']:
        w('<section class="hero" data-hero aria-label="بنر اصلی">')
        w('<div class="hero-track">')
        for i, s in enumerate(d['hero']):
            w('<div class="hero-slide" aria-hidden="%s"><img src="%s" alt="%s" %s '
              'width="1440" height="420" decoding="async"></div>'
              % ('false' if i == 0 else 'true', e(s['img']), e(s['alt']),
                 'fetchpriority="high"' if i == 0 else 'loading="lazy"'))
        w('</div>')
        w('<button class="hero-nav hero-prev" aria-label="اسلاید قبلی">%s</button>' % icon('chev_r'))
        w('<button class="hero-nav hero-next" aria-label="اسلاید بعدی">%s</button>' % icon('chev_l'))
        w('<div class="hero-dots" role="tablist" aria-label="اسلایدها">')
        for i in range(len(d['hero'])):
            w('<button class="hero-dot" aria-current="%s" aria-label="اسلاید %d"></button>'
              % ('true' if i == 0 else 'false', i + 1))
        w('</div>')
        w('</section>')

    # -- story circles: 8 visible + «بیشتر» ---------------------------------
    stories = d['stories']
    VISIBLE = 8
    w('<section class="sec stories" aria-label="هایلایت‌ها"><div class="cont">')
    w('<div class="story-rail">')
    # Buttons, not links: the catalogue has no per-story URL — the theme's
    # existing highlight viewer opens these from the same data attributes.
    for i, s in enumerate(stories):
        hidden = ' hidden data-story-hidden' if i >= VISIBLE else ''
        w('<button type="button" class="story" data-story-id="%s" '
          'data-slides="%s"%s>'
          '<span class="story-ring"><span class="story-img">'
          '<img src="%s" alt="" loading="lazy" width="88" height="88"></span></span>'
          '<span class="story-label">%s</span></button>'
          % (e(s['id']), e(json.dumps(s['slides'], ensure_ascii=False)), hidden,
             e(s['img']), e(s['label'])))
    if len(stories) > VISIBLE:
        w('<button class="story story-more" data-stories-more aria-label="نمایش هایلایت‌های بیشتر">'
          '<span class="story-ring"><span class="story-img">%s</span></span>'
          '<span class="story-label">بیشتر</span></button>' % icon('plus'))
    w('</div>')
    w('</div></section>')

    # -- flash sale ---------------------------------------------------------
    fs = d['flash']
    w('<section class="sec" id="flash-sale"><div class="cont">')
    w(promo_banner(fs['title'], fs['sub'], fs['cta'], fs['cta_href'], countdown=fs.get('end')))
    w('</div>')
    w('<div class="cont" style="margin-block-start:var(--s-6)">')
    w(product_rail('flashGrid', d['grids']['flashGrid'], eager_first=True))
    w('</div></section>')

    # -- promotional banner block (four-up grid, fed by the banner position) --
    banners = d['mid_banners']
    if banners:
        w('<section class="sec" aria-label="بنرهای تبلیغاتی"><div class="cont">')
        w('<div class="banner-grid" data-count="%d" data-banner-position="home_middle">' % min(len(banners), 4))
        for b in banners[:4]:
            w('<a class="banner-card" href="%s" rel="nofollow sponsored">'
              '<img src="%s" alt="%s" loading="lazy"></a>'
              % (e(b['href']), e(b['img']), e(b['alt'])))
        w('</div>')
        w('</div></section>')

    # -- second promotional product section (same banner + card system) -----
    motor = d['grids']['motorGrid']
    w('<section class="sec" id="motorcycles"><div class="cont">')
    w(promo_banner('خرید موتورسیکلت',
                   'ارسال سراسری، پرداخت امن و ضمانت ۷ روزه بازگشت وجه',
                   'مشاهده همه موتورسیکلت‌ها', BASE + '/fa/products?type=motorcycle'))
    w('</div>')
    w('<div class="cont" style="margin-block-start:var(--s-6)">')
    w(product_rail('motorGrid', motor['items']))
    w('</div></section>')

    # -- compatible-motorcycle chips ---------------------------------------
    w('<section class="sec"><div class="cont">')
    w('<div class="sec-hd"><div><h2>خرید بر اساس <em>موتور شما</em></h2>'
      '<p style="margin:var(--s-2) 0 0;font-size:var(--fs-13);color:var(--c-steel)">'
      'موتور خود را انتخاب کنید تا قطعات سازگار را اول ببینید</p></div></div>')
    w('<div class="moto-rail">')
    for m in d['moto']:
        cc = '<span class="moto-cc">%s</span>' % e(m['cc']) if m['cc'] else ''
        ico = icon('layers', 'icon-sm') if not m['cc'] else icon('moto', 'icon-sm')
        w('<a class="moto-chip" href="%s">%s<span>%s</span>%s</a>'
          % (e(m['href']), ico, e(m['name']), cc))
    w('</div>')
    w('</div></section>')

    # -- trust strip --------------------------------------------------------
    w('<section class="trust"><div class="cont"><div class="trust-row">')
    for ti in d['trust']:
        w('<div class="ti"><img src="%s" alt="" loading="lazy" width="32" height="32">'
          '<span>%s</span></div>' % (e(ti['img']), e(ti['text'])))
    w('</div></div></section>')

    # -- parts row ----------------------------------------------------------
    parts = d['grids']['partGrid']
    w(section('قطعات و', 'لوازم جانبی',
              product_rail('partGrid', parts['items']),
              sec_id='parts',
              more={'text': 'مشاهده همه', 'href': BASE + '/fa/products?type=parts'}))

    # -- categories ---------------------------------------------------------
    cats = d['categories'][:10]
    grid = '<div class="cat-grid">' + ''.join(
        '<a class="ccard" href="%s"><span class="ccard-img">'
        '<img src="%s" alt="" loading="lazy" width="120" height="120"></span>'
        '<h3>%s</h3></a>' % (e(c['href']), e(c['img']), e(c['name'])) for c in cats
    ) + '</div>'
    w(section('خرید بر اساس', 'دسته‌بندی', grid,
              more={'text': 'همه دسته‌بندی‌ها', 'href': BASE + '/fa/products'}))

    # -- weekly offers ------------------------------------------------------
    offers = d['grids']['prodGrid']
    w(section('پیشنهادات', 'این هفته',
              product_rail('prodGrid', offers['items']),
              more={'text': 'مشاهده همه', 'href': BASE + '/fa/products'}))

    # -- brands -------------------------------------------------------------
    brand_items = []
    for b in d['brands']:
        inner = ('<img src="%s" alt="%s" loading="lazy">' % (e(b['logo']), e(b['name']))
                 if b.get('logo')
                 else '<span class="brand-wordmark ltr">%s</span>' % e(b['name']))
        brand_items.append('<a class="brand" href="%s" aria-label="%s">%s</a>'
                           % (e(b['href']), e(b['name']), inner))
    w(section('محبوب‌ترین', 'برندها',
              '<div class="brand-rail">%s</div>' % ''.join(brand_items)))

    # -- magazine -----------------------------------------------------------
    blog = ''.join(
        '<article class="blcard">'
        '<a href="%s"><img src="%s" alt="" loading="lazy" width="320" height="200">'
        '<h3 class="bltitle">%s</h3></a>'
        '<div class="blmeta">%s</div>'
        '</article>' % (e(p['href']), e(p['img']), e(p['title']), e(p['date']))
        for p in d['blog'][:8]
    )
    w(section('مجله', 'موتور',
              '<div class="blog-rail">%s</div>' % blog,
              more={'text': 'همه مطالب', 'href': BASE + '/fa/blogs'}))

    w('</main>')

    # -- footer -------------------------------------------------------------
    f = d['footer']
    w('<footer class="ft"><div class="cont">')
    w('<div class="ft-top">')
    w('<div><div class="ft-logo">'
      '<img src="assets/img/hapeec-wordmark-lockup.png" alt="HAPEEC — Motorcycle Platform" '
      'width="434" height="121"></div>')
    w('<p class="ft-desc">%s</p>' % e(f['desc']))
    w('<div class="ft-socials">')
    for s in f['socials']:
        w('<a class="fsoc" href="%s" aria-label="%s">%s</a>'
          % (e(s['href']), e(s['title']), icon(SOCIAL_MAP.get(s['icon'], 'tag'))))
    w('</div></div>')

    half = (len(f['links']) + 1) // 2
    for col, links in (('اطلاعات', f['links'][:half]), ('خدمات', f['links'][half:])):
        w('<div class="ft-col"><h3>%s</h3><nav class="ft-links">' % e(col))
        for l in links:
            w('<a href="%s">%s</a>' % (e(l['href']), e(l['text'])))
        w('</nav></div>')
    w('</div>')

    badge_icons = ['lock', 'award', 'rotate', 'headset']
    w('<div class="ft-bot"><span>%s</span><div class="ft-badges">%s</div></div>'
      % (e(f['copy']),
         ''.join('<span class="ftbadge">%s%s</span>' % (icon(badge_icons[i % 4], 'icon-sm'), e(b))
                 for i, b in enumerate(f['badges']))))
    w('</div></footer>')

    # -- mobile drawer ------------------------------------------------------
    w('<div class="scrim" data-scrim data-open="false"></div>')
    w('<nav class="drawer" id="drawer" data-drawer data-open="false" aria-label="منوی موبایل">')
    w('<div class="drawer-head">'
      '<img src="assets/img/hapeec-wordmark.png" alt="HAPEEC" width="433" height="73">'
      '<button data-drawer-close aria-label="بستن منو">%s</button></div>' % icon('close'))
    w('<div class="drawer-body">')
    w('<div class="drawer-label">دسته‌بندی</div>')
    for i, g in enumerate(d['mega']):
        sid = 'drw-sub-%d' % i
        w('<button class="drawer-link" data-drawer-group aria-expanded="false" aria-controls="%s">'
          '%s<span>%s</span><span class="drawer-chev">%s</span></button>'
          % (sid, icon('layers', 'icon-sm'), e(g['title']), icon('chev_l', 'icon-sm')))
        w('<div class="drawer-sub" id="%s" data-open="false">' % sid)
        w('<a href="%s">مشاهده همه %s</a>' % (e(g['href']), e(g['title'])))
        for l in g['links']:
            w('<a href="%s">%s</a>' % (e(l['href']), e(l['text'])))
        w('</div>')
    w('<div class="drawer-label">میان‌برها</div>')
    for item in d['subnav']:
        w('<a class="drawer-link" href="%s">%s<span>%s</span></a>'
          % (e(item['href']), icon(FA_MAP.get(item['icon'], 'tag'), 'icon-sm'), e(item['text'])))
    w('<div class="drawer-label">اطلاعات</div>')
    for l in d['footer']['links']:
        w('<a class="drawer-link" href="%s">%s</a>' % (e(l['href']), e(l['text'])))
    w('</div></nav>')

    w('<script src="assets/js/home.js" defer></script>')
    w('</body>')
    w('</html>')

    return '\n'.join(out)


if __name__ == '__main__':
    path = os.path.join(HERE, 'index.html')
    with open(path, 'w', encoding='utf-8') as fh:
        fh.write(build())
    print('wrote', path, os.path.getsize(path), 'bytes')
