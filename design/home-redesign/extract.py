import json, re
from bs4 import BeautifulSoup

SRC = '/home/user/mojtaba-pourasghar/hapeec_template/tools/site-capture/captures/test.happenengrave.com/pages/001-fa/page.html'
soup = BeautifulSoup(open(SRC, encoding='utf-8').read(), 'lxml')
BASE = 'https://test.happenengrave.com'
def t(el): return re.sub(r'\s+', ' ', el.get_text(' ', strip=True)) if el else ''

D = {}

# ---- top announcement banner
top = soup.select_one('.banner-section img, header ~ * img')
first_img = soup.find('img', src=re.compile(r'/uploads/banners/'))
ann = first_img.find_parent('a') if first_img else None
D['announcement'] = {'href': ann['href'] if ann and ann.has_attr('href') else None,
                     'img': first_img['src'] if first_img else None,
                     'alt': first_img.get('alt','') if first_img else ''}

# ---- subnav
D['subnav'] = [{'text': t(a), 'href': a['href'], 'icon': (a.i.get('class')[-1] if a.i else ''),
                'hot': 'hsub-hot' in a.get('class', [])}
               for a in soup.select('.hsub-list .hsub-link')]
sell = soup.select_one('.hsub-sell, .hdr-sub a[href*="seller"]')
D['sell_cta'] = {'text': t(sell), 'href': sell['href']} if sell else None

# ---- mega menu
D['mega'] = []
for panel in soup.select('.mega-panel'):
    title = panel.select_one('.mega-panel-title')
    D['mega'].append({
        'title': title.contents[0].strip() if title else '',
        'href': title['href'] if title else '',
        'links': [{'text': t(a), 'href': a['href']} for a in panel.select('.mega-links a')]
    })

# ---- stories
D['stories'] = []
for it in soup.select('.hl-item'):
    img = it.select_one('img')
    D['stories'].append({'id': it.get('data-story-id'), 'label': it.get('data-label'),
                         'img': img['src'] if img else None,
                         'slides': json.loads(it.get('data-slides') or '[]')})

# ---- hero slides
D['hero'] = [{'img': s.img['src'], 'alt': s.img.get('alt','')} for s in soup.select('.hero-slider .slide') if s.img]

# ---- moto chips
D['moto'] = [{'name': t(c.select_one('.moto-chip-name')), 'cc': t(c.select_one('.moto-chip-cc')),
              'href': c['href']} for c in soup.select('.moto-chip')]

# ---- trust
D['trust'] = [{'img': i.img['src'], 'text': t(i.span)} for i in soup.select('.trust-items .ti')]

# ---- categories
D['categories'] = [{'name': t(c.h4), 'href': c['href'], 'img': c.select_one('.ccard-ico')['src']}
                   for c in soup.select('.ccard')]

# ---- flash sale meta
fs = soup.select_one('.flash-sale')
cd = fs.select_one('.fs-countdown') if fs else None
D['flash'] = {'title': t(fs.select_one('.fs-title h2')) if fs else '',
              'sub': t(fs.select_one('.fs-title p')) if fs else '',
              'end': cd.get('data-end') if cd else None,
              'cta': t(fs.select_one('.btn-flash')) if fs else '',
              'cta_href': fs.select_one('.btn-flash')['href'] if fs else ''}

# ---- products, per grid
def parse_card(c):
    link = c.select_one('.pname a')
    img = c.select_one('.pimg-w img')
    disc = c.select_one('.pdisc-simple, .pdisc')
    price = c.select_one('.pprice .price-num')
    old = c.select_one('.pold .price-num')
    btn = c.select_one('.btn-cart')
    return {'title': t(link), 'href': link['href'] if link else None,
            'img': img['src'] if img else None,
            'discount': t(disc) or None, 'price': t(price) or None, 'old': t(old) or None,
            'pid': btn.get('data-id') if btn else None}

D['grids'] = {}
for gid in ['flashGrid']:
    g = soup.select_one('#' + gid)
    if g: D['grids'][gid] = [parse_card(c) for c in g.select('.pcard')]
for sec in soup.select('section.sec'):
    g = sec.select_one('.prod-grid')
    if not g: continue
    h2 = sec.select_one('.sec-hd h2')
    more = sec.select_one('.sec-hd a, .sec-more')
    key = g.get('id') or sec.get('id') or t(h2)
    if key in D['grids']: continue
    D['grids'][key] = {'title': t(h2), 'id': sec.get('id'),
                       'more': {'text': t(more), 'href': more['href']} if more and more.has_attr('href') else None,
                       'items': [parse_card(c) for c in g.select('.pcard')]}

# ---- mid banner
mb = soup.select_one('[data-banner-position="home_middle"]')
D['mid_banners'] = [{'href': a['href'], 'img': a.img['src'], 'alt': a.img.get('alt','')}
                    for a in mb.select('a.banner-card')] if mb else []

# ---- videos
D['videos'] = [{'cover': a.img['src'], 'title': t(a.select_one('.vc-title')),
                'video': a.get('data-video'), 'views': t(a.select_one('.vc-views'))}
               for a in soup.select('.vc-card')]

# ---- brands
D['brands'] = []
for b in soup.select('.brand-item .brand-link'):
    logo = b.select_one('img')
    D['brands'].append({'name': t(b.select_one('.brand-name')) or b.get('title'),
                        'href': b['href'], 'logo': logo['src'] if logo else None})

# ---- blog
D['blog'] = [{'title': t(a.select_one('.bltitle')), 'href': a.select_one('.bltitle a')['href'],
              'img': a.select_one('.blimg')['src'], 'tag': t(a.select_one('.bltag')),
              'date': t(a.select_one('.bldate'))} for a in soup.select('.blcard')]

# ---- footer
ft = soup.select_one('footer')
D['footer'] = {'desc': t(ft.select_one('.ft-desc')),
               'links': [{'text': t(a), 'href': a['href']} for a in ft.select('.ft-links a')],
               'socials': [{'title': a.get('title'), 'icon': a.i.get('class')[-1], 'href': a['href']} for a in ft.select('.fsoc')],
               'copy': t(ft.select_one('.ft-bot span')),
               'badges': [t(s) for s in ft.select('.ftbadge')]}

# ---- mobile bottom nav
D['mobnav'] = [{'text': t(x), 'href': (x.get('href') or (x.find_parent('a').get('href') if x.find_parent('a') else None))}
               for x in soup.select('.mob-nav .mn')]

json.dump(D, open('home-data.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for k, v in D.items():
    print(k, '->', len(v) if isinstance(v, (list, dict)) else v)
print('grids:', {k: (len(v) if isinstance(v, list) else len(v['items'])) for k, v in D['grids'].items()})
