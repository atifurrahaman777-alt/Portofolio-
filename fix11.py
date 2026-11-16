import os, re, json, shutil

# ================= 1. API =================
API = r'''const cheerio = require('cheerio')

const BASE = 'https://generator.email'
const TIMEOUT = 8000
const RETRIES = 1
const RETRYABLE = new Set([403, 408, 425, 429, 500, 502, 503, 504])
const UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
const EMAIL_RE = /^[a-z0-9._-]{1,64}@[a-z0-9.-]{3,100}$/i
const ID_RE = /^[\w.=-]{1,200}$/
const sleep = (ms) => new Promise((r) => setTimeout(r, ms))

function makeClient() {
  const cookies = new Map()
  const setCookie = (k, v) => cookies.set(k, v)
  const ck = () => [...cookies].map(([k, v]) => `${k}=${v}`).join('; ')

  async function req(url, { method = 'GET', body, headers = {}, noRetry = false } = {}) {
    let lastErr
    for (let i = 0; i <= RETRIES; i++) {
      const ac = new AbortController()
      const t = setTimeout(() => ac.abort(), TIMEOUT)
      try {
        const res = await fetch(url, {
          method,
          headers: { 'User-Agent': UA, Accept: 'text/html,application/json;q=0.9,*/*;q=0.8', Cookie: ck(), ...headers },
          body,
          signal: ac.signal,
          redirect: 'follow'
        })
        for (const c of res.headers.getSetCookie?.() ?? []) {
          const [p] = c.split(';')
          const idx = p.indexOf('=')
          if (idx > 0) setCookie(p.slice(0, idx).trim(), p.slice(idx + 1).trim())
        }
        const txt = await res.text()
        if (!noRetry && RETRYABLE.has(res.status) && i < RETRIES) {
          await sleep(700)
          lastErr = new Error(`HTTP ${res.status}`)
          continue
        }
        return { res, txt }
      } catch (e) {
        lastErr = e
        if (e.name !== 'AbortError' && !(e instanceof TypeError)) break
        await sleep(500)
      } finally {
        clearTimeout(t)
      }
    }
    throw lastErr || new Error('Gagal menghubungi layanan email.')
  }
  return { req, setCookie }
}

const pathTo = (email) => {
  const [user, domain] = email.split('@')
  return `${domain}/${user.replace(/[^a-zA-Z0-9._-]/g, '')}`
}

function parseSiteData(html) {
  const m = html.match(/SITE_DATA\s*=\s*({[\s\S]*?});?\s*<\/script>/)
  if (!m) return {}
  try {
    return JSON.parse(m[1].replace(/,(\s*[}\]])/g, '$1'))
  } catch {
    const g = (k) => html.match(new RegExp(`${k}:"([^"]*)"`))?.[1] ?? null
    const n = (k) => Number(html.match(new RegExp(`${k}:(\\d+)`))?.[1] ?? 0)
    return { num_mess: n('num_mess'), secret_del_mess: g('secret_del_mess') }
  }
}

async function newEmail(c) {
  const { txt } = await c.req(`${BASE}/email-generator`)
  const $ = cheerio.load(txt)
  const user = $('#userName').attr('value') || $('#userName').val()
  const domain = $('#domainName2').attr('value') || $('#domainName2').val()
  if (!user || !domain) throw new Error('Gagal membuat email, coba lagi.')
  const email = `${user}@${domain}`.toLowerCase()
  c.setCookie('surl', pathTo(email))
  c.setCookie('embx', encodeURIComponent(JSON.stringify([email])))
  await c.req(`${BASE}/check_adres_validation3.php`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest' },
    body: `usr=${encodeURIComponent(user)}&dmn=${encodeURIComponent(domain)}`
  }).catch(() => {})
  return { email }
}

async function fetchInbox(c, email) {
  const [user, domain] = email.split('@')
  c.setCookie('inbox_ctx', encodeURIComponent(`${domain}/${user}/`))
  const { txt } = await c.req(`${BASE}/${domain}/${user}`)
  const $ = cheerio.load(txt)
  const sd = parseSiteData(txt)
  const messages = []
  $('#email-table .list-group-item').each((_, el) => {
    const $el = $(el)
    const click = $el.attr('onclick') || ''
    const id = click.match(/loadInboxClientSide\('([^']+)'\)/)?.[1]?.replace(/\/$/, '').split('/').pop() || null
    const from = $el.find('[class*="from_div"]').first().text().trim()
    const subj = $el.find('[class*="subj_div"]').first().text().trim()
    const date = $el.find('[class*="time_div"]').first().text().trim()
    if (id || (from && from !== 'From')) messages.push({ id, from: from || null, subject: subj || null, date: date || null })
  })
  const count = parseInt($('#mess_number').text(), 10) || (sd.num_mess ?? messages.length)
  return { email, count, messages }
}

async function getRawSource(c, email, id) {
  const [user, domain] = email.split('@')
  c.setCookie('inbox_ctx', encodeURIComponent(`${domain}/${user}/${id}`))
  let { res, txt } = await c.req(`${BASE}/inbox4/?src=${encodeURIComponent(id)}`, { noRetry: true })
  if (res.status !== 403) {
    if (!res.ok) throw new Error(`Raw gagal: HTTP ${res.status}`)
    return txt
  }
  const capRes = await c.req(`${BASE}/inbox4/?src_captcha=1`, { noRetry: true })
  const cap = JSON.parse(capRes.txt)
  const code = String(cap.svg || '').replace(/<[^>]+>/g, '').replace(/\s+/g, '')
  ;({ res, txt } = await c.req(`${BASE}/inbox4/?src=${encodeURIComponent(id)}&cap=${encodeURIComponent(code)}&capt=${encodeURIComponent(cap.token)}`, { noRetry: true }))
  if (!res.ok) throw new Error(`Captcha gagal (HTTP ${res.status})`)
  return txt
}

async function readMessage(c, email, id, wantRaw) {
  const [user, domain] = email.split('@')
  c.setCookie('inbox_ctx', encodeURIComponent(`${domain}/${user}/${id}`))
  const { txt } = await c.req(`${BASE}/inbox4/`)
  const $ = cheerio.load(txt)
  const from = $('#mail-summary-head [class*="from_div"]').first().text().trim() || null
  const subject = $('#mail-summary-head [class*="subj_div"] h1, #mail-summary-head [class*="subj_div"]').first().text().trim() || null
  const date = $('#mail-summary-head [class*="time_div"]').first().text().trim() || null
  let bodyHtml = null
  for (const sel of ['.mess_bodiyy', '#mail-summary-body', '.mailsrc-body']) {
    const el = $(sel).first()
    if (el.length) {
      bodyHtml = el.html()?.trim() || null
      break
    }
  }
  let bodyText = null
  if (bodyHtml) {
    const $b = cheerio.load('<div>' + bodyHtml + '</div>')
    $b('script,style').remove()
    bodyText = $b('div').text().split('\n').map((l) => l.trim()).join('\n').replace(/\n{3,}/g, '\n\n').trim().slice(0, 20000)
  }
  let raw = null
  if (wantRaw) raw = (await getRawSource(c, email, id)).slice(0, 200000)
  return { id, from, subject, date, bodyText, raw }
}

async function deleteAll(c, email) {
  const [user, domain] = email.split('@')
  c.setCookie('inbox_ctx', encodeURIComponent(`${domain}/${user}/`))
  const { txt } = await c.req(`${BASE}/inbox4/`)
  const sd = parseSiteData(txt)
  if (!sd.secret_del_mess) throw new Error('Inbox sudah kosong.')
  const out = await c.req(`${BASE}/mark_remove.php`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: `delete_all=${encodeURIComponent(sd.secret_del_mess)}`
  })
  if (String(out.txt).trim() !== 'Messages deleted successfully') throw new Error('Gagal menghapus pesan.')
  return { message: 'Semua pesan dihapus.' }
}

module.exports = async (req, res) => {
  res.setHeader('Cache-Control', 'no-store')
  const q = req.query || {}
  const action = String(q.action || '')
  try {
    const c = makeClient()
    let data
    if (action === 'new') {
      data = await newEmail(c)
    } else if (['inbox', 'read', 'delete'].includes(action)) {
      const email = String(q.email || '').trim().toLowerCase()
      if (!EMAIL_RE.test(email)) throw new Error('Alamat email tidak valid.')
      if (action === 'inbox') data = await fetchInbox(c, email)
      else if (action === 'delete') data = await deleteAll(c, email)
      else {
        const id = String(q.id || '')
        if (!ID_RE.test(id)) throw new Error('ID pesan tidak valid.')
        data = await readMessage(c, email, id, q.raw === '1')
      }
    } else {
      throw new Error('Aksi tidak dikenal.')
    }
    res.status(200).json({ success: true, ...data })
  } catch (e) {
    res.status(400).json({ success: false, message: e.message || 'Terjadi kesalahan.' })
  }
}
'''

os.makedirs('api', exist_ok=True)
open('api/tempmail.js', 'w', encoding='utf-8').write(API)
print('api/tempmail.js :', 'OK')

# ================= 2. package.json (cheerio) =================
pk = 'package.json'
d = json.load(open(pk, encoding='utf-8')) if os.path.exists(pk) else {'name': 'portofolio', 'private': True}
d.setdefault('dependencies', {})
d['dependencies'].setdefault('cheerio', '1.0.0')
json.dump(d, open(pk, 'w', encoding='utf-8'), indent=2)
print('package.json    :', 'OK')
if d.get('type') == 'module':
    print('PERINGATAN: package.json punya "type":"module", api/tempmail.js perlu diubah ke ESM. Kirim hasil ini ke gw.')

# ================= 3. Tema (sama kayak halaman lain) =================
P = 'html body:is(.light-mode,:not(.light-mode))'
rules = [
 ('.card', 'background:var(--card)!important;border:1px solid var(--line)!important;box-shadow:0 4px 18px var(--shadow)!important;border-radius:14px!important'),
 ('.tm-mail,.tm-item,.tm-body,.tm-raw', 'background:var(--bg)!important;color:var(--text)!important;border:1px solid var(--line)!important;border-radius:12px!important;box-shadow:none!important'),
 ('.btn', 'background:var(--accent)!important;color:var(--on)!important;border:1px solid var(--line)!important;box-shadow:0 4px 18px var(--shadow)!important;text-shadow:none!important;border-radius:10px!important'),
 ('.btn.ghost', 'background:var(--card)!important;color:var(--text)!important;box-shadow:none!important'),
 ('h1,h2,h3,.brand', 'color:var(--text)!important;text-shadow:none!important'),
 ('.accent,.eyebrow', 'color:var(--accent)!important;text-shadow:none!important'),
 ('.sub,.tm-muted,.tm-label,footer', 'color:var(--muted)!important;text-shadow:none!important'),
 ('#theme-toggle', 'background:var(--card)!important;border:1px solid var(--line)!important;color:var(--text)!important;border-radius:8px!important;box-shadow:none!important'),
]
css = ('html body:not(.light-mode){--bg:#0a0a0a;--card:#141414;--line:#2a2a2a;--text:#f5f5f5;--muted:#9ca3af;--shadow:rgba(0,0,0,.5);--gold:#f5f5f5;--purple:#f5f5f5;--accent:#f5f5f5;--on:#0a0a0a}\n'
       'html body.light-mode{--bg:#ffffff;--card:#f7f7f8;--line:#e5e5e5;--text:#0a0a0a;--muted:#6b7280;--shadow:rgba(0,0,0,.12);--gold:#0a0a0a;--purple:#0a0a0a;--accent:#0a0a0a;--on:#fff}\n')
css += P + '{background:var(--bg)!important;color:var(--text)!important}\n'
css += P + '::before,' + P + '::after{background:none!important}\n'
for sels, decl in rules:
    css += ','.join(P + ' ' + x for x in sels.split(',')) + '{' + decl + '}\n'
THEME = '<style id="mz-theme">\n' + css + '</style>\n'

SYNC = '''<script>
(function(){
  function sync(){
    try{
      var pb = window.parent !== window ? window.parent.document.body : null;
      if(pb) document.body.classList.toggle('light-mode', pb.classList.contains('light-mode'));
    }catch(e){}
  }
  sync();
  window.addEventListener('load', sync);
  try{
    new MutationObserver(sync).observe(window.parent.document.body, {attributes:true, attributeFilter:['class']});
  }catch(e){}
})();
</script>
'''

# ================= 4. Halaman =================
PAGE = r'''<!doctype html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#080811">
<meta name="description" content="Temp Mail — email sementara tanpa daftar, oleh Mann'zz">
<title>Temp Mail | Mann'zz Tools</title>
<link rel="stylesheet" href="style.css">
<link rel="icon" type="image/png" href="favicon.png">
<style>
.tm-box{max-width:640px;margin:0 auto;display:flex;flex-direction:column;gap:16px}
.tm-label{font-size:.78rem;font-weight:700;margin-bottom:8px}
.tm-mail{padding:14px;font-weight:800;font-size:1.02rem;overflow-wrap:anywhere}
.tm-row{display:flex;gap:10px;flex-wrap:wrap;margin-top:12px}
.tm-row .btn{flex:1;min-width:130px;text-align:center}
.tm-head{display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap;margin-bottom:12px}
.tm-head h3{margin:0}
.tm-head .btn{padding:8px 12px;font-size:.8rem}
.tm-item{display:block;width:100%;text-align:left;padding:12px;margin-bottom:8px;font:inherit;cursor:pointer}
.tm-item b{display:block;overflow-wrap:anywhere}
.tm-item small{display:block;margin-top:2px}
.tm-muted{font-size:.85rem}
.tm-body{padding:14px;white-space:pre-wrap;overflow-wrap:anywhere;font-size:.92rem;line-height:1.7;max-height:55vh;overflow:auto;margin:12px 0}
.tm-raw{padding:12px;white-space:pre-wrap;overflow-wrap:anywhere;font-size:.75rem;max-height:40vh;overflow:auto;margin-top:12px;font-family:monospace}
.tm-error{font-size:.85rem;color:#ff6b6b;display:none}
.tm-error.show{display:block}
.tm-loading{font-size:.85rem;text-align:center;display:none}
.tm-loading.show{display:block}
[hidden]{display:none!important}
</style>
%%THEME%%<link rel="manifest" href="/manifest.json"><link rel="apple-touch-icon" href="/icon-192.png">
</head>
<body>
<main class="wrap">

<header>
<div class="brand"><svg viewBox="0 0 24 24" style="width:1em;height:1em;display:inline-block;vertical-align:-0.15em;stroke:currentColor;fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/></svg> Temp Mail <span class="accent">Mann'zz</span></div>
<div style="display:flex;align-items:center;gap:10px">
<button id="theme-toggle" type="button" aria-label="Ganti mode terang/gelap" title="Ganti mode terang/gelap"><svg viewBox="0 0 24 24" style="width:1em;height:1em;display:inline-block;vertical-align:-0.15em;stroke:currentColor;fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round"><circle cx="12" cy="12" r="4"/><line x1="12" y1="2" x2="12" y2="4"/><line x1="12" y1="20" x2="12" y2="22"/><line x1="4" y1="12" x2="2" y2="12"/><line x1="22" y1="12" x2="20" y2="12"/><line x1="5" y1="5" x2="6.4" y2="6.4"/><line x1="17.6" y1="17.6" x2="19" y2="19"/><line x1="5" y1="19" x2="6.4" y2="17.6"/><line x1="17.6" y1="6.4" x2="19" y2="5"/></svg></button>
</div>
</header>

<section class="hero">
<div class="eyebrow">EMAIL SEMENTARA</div>
<h1>Email sekali pakai,<br><span class="accent">tanpa daftar.</span></h1>
<p class="sub">Buat alamat email sementara, lalu baca pesan yang masuk langsung di sini.</p>
</section>

<section class="tm-box">
<div class="card">
<div class="tm-label">Alamat email kamu</div>
<div class="tm-mail" id="tm-mail">Belum ada email</div>
<div class="tm-row">
<button class="btn" id="tm-new" type="button">Buat Email Baru</button>
<button class="btn ghost" id="tm-copy" type="button" hidden>Salin</button>
</div>
<p class="tm-muted tm-label" style="margin:12px 0 0">Email sementara bersifat publik: siapa pun yang tahu alamatnya bisa membaca pesannya. Jangan dipakai untuk data penting.</p>
</div>

<p class="tm-loading" id="tm-loading">Memproses...</p>
<p class="tm-error" id="tm-error"></p>

<div class="card" id="tm-inbox-card" hidden>
<div class="tm-head">
<h3>Kotak Masuk</h3>
<div style="display:flex;gap:8px">
<button class="btn ghost" id="tm-refresh" type="button">Refresh</button>
<button class="btn ghost" id="tm-delete" type="button">Hapus Semua</button>
</div>
</div>
<div id="tm-list"></div>
</div>

<div class="card" id="tm-read-card" hidden>
<div class="tm-head">
<button class="btn ghost" id="tm-back" type="button">Kembali</button>
<button class="btn ghost" id="tm-rawbtn" type="button">Lihat Raw</button>
</div>
<h3 id="tm-subject"></h3>
<p class="tm-muted" id="tm-meta"></p>
<div class="tm-body" id="tm-body"></div>
<div class="tm-raw" id="tm-raw" hidden></div>
</div>
</section>

</main>
<footer>© Mann'zz Tools</footer>
<script src="app.js"></script>
<script>
(function(){
  var KEY = 'mz_tempmail';
  var $ = function(id){ return document.getElementById(id); };
  var email = '', ids = [], openId = null;
  try { email = localStorage.getItem(KEY) || ''; } catch(e) {}

  function setLoading(on){ $('tm-loading').classList.toggle('show', on); }
  function setError(msg){
    var el = $('tm-error');
    el.textContent = msg || '';
    el.classList.toggle('show', !!msg);
  }

  async function api(params){
    var res = await fetch('/api/tempmail?' + new URLSearchParams(params), { cache: 'no-store' });
    var data;
    try { data = JSON.parse(await res.text()); } catch(e) { throw new Error('Respons server tidak valid.'); }
    if (!res.ok || !data.success) throw new Error(data.message || 'Gagal memproses.');
    return data;
  }

  function renderAddress(){
    $('tm-mail').textContent = email || 'Belum ada email';
    $('tm-copy').hidden = !email;
    $('tm-inbox-card').hidden = !email || !!openId;
    $('tm-new').textContent = email ? 'Ganti Email Baru' : 'Buat Email Baru';
  }

  function renderList(messages){
    var list = $('tm-list');
    list.replaceChildren();
    ids = messages.map(function(m){ return m.id; });
    if (!messages.length) {
      var p = document.createElement('p');
      p.className = 'tm-muted';
      p.textContent = 'Belum ada pesan. Inbox dicek otomatis tiap 20 detik.';
      list.appendChild(p);
      return;
    }
    messages.forEach(function(m, i){
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'tm-item';
      var t = document.createElement('b');
      t.textContent = m.subject || '(tanpa subjek)';
      var f = document.createElement('small');
      f.className = 'tm-muted';
      f.textContent = (m.from || '-') + ' • ' + (m.date || '-');
      b.append(t, f);
      if (m.id) b.addEventListener('click', function(){ openMessage(i); });
      else b.disabled = true;
      list.appendChild(b);
    });
  }

  async function loadInbox(silent){
    if (!email) return;
    if (!silent) { setError(''); setLoading(true); }
    try {
      var d = await api({ action: 'inbox', email: email });
      renderList(d.messages || []);
    } catch(e) {
      if (!silent) setError(e.message);
    } finally {
      if (!silent) setLoading(false);
    }
  }

  async function newMail(){
    setError(''); setLoading(true);
    $('tm-new').disabled = true;
    try {
      var d = await api({ action: 'new' });
      email = d.email;
      try { localStorage.setItem(KEY, email); } catch(e) {}
      openId = null;
      $('tm-read-card').hidden = true;
      renderAddress();
      renderList([]);
    } catch(e) {
      setError(e.message);
    } finally {
      setLoading(false);
      $('tm-new').disabled = false;
    }
  }

  async function openMessage(i){
    var id = ids[i];
    if (!id) return;
    setError(''); setLoading(true);
    try {
      var d = await api({ action: 'read', email: email, id: id });
      openId = id;
      $('tm-subject').textContent = d.subject || '(tanpa subjek)';
      $('tm-meta').textContent = (d.from || '-') + ' • ' + (d.date || '-');
      $('tm-body').textContent = d.bodyText || '(isi kosong)';
      $('tm-raw').hidden = true;
      $('tm-raw').textContent = '';
      $('tm-rawbtn').textContent = 'Lihat Raw';
      $('tm-inbox-card').hidden = true;
      $('tm-read-card').hidden = false;
    } catch(e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  async function toggleRaw(){
    var box = $('tm-raw');
    if (!box.hidden) { box.hidden = true; $('tm-rawbtn').textContent = 'Lihat Raw'; return; }
    if (!box.textContent) {
      setError(''); setLoading(true);
      try {
        var d = await api({ action: 'read', email: email, id: openId, raw: '1' });
        box.textContent = d.raw || '(raw kosong)';
      } catch(e) {
        setError(e.message);
        setLoading(false);
        return;
      }
      setLoading(false);
    }
    box.hidden = false;
    $('tm-rawbtn').textContent = 'Sembunyikan Raw';
  }

  async function removeAll(){
    if (!confirm('Hapus semua pesan di inbox ini?')) return;
    setError(''); setLoading(true);
    try {
      await api({ action: 'delete', email: email });
      renderList([]);
    } catch(e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  function copyMail(){
    if (!email) return;
    var done = function(){
      $('tm-copy').textContent = 'Tersalin';
      setTimeout(function(){ $('tm-copy').textContent = 'Salin'; }, 1500);
    };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(email).then(done, function(){ setError('Gagal menyalin.'); });
    } else {
      var t = document.createElement('textarea');
      t.value = email;
      document.body.appendChild(t);
      t.select();
      try { document.execCommand('copy'); done(); } catch(e) { setError('Gagal menyalin.'); }
      t.remove();
    }
  }

  $('tm-new').addEventListener('click', newMail);
  $('tm-copy').addEventListener('click', copyMail);
  $('tm-refresh').addEventListener('click', function(){ loadInbox(false); });
  $('tm-delete').addEventListener('click', removeAll);
  $('tm-rawbtn').addEventListener('click', toggleRaw);
  $('tm-back').addEventListener('click', function(){
    openId = null;
    $('tm-read-card').hidden = true;
    $('tm-inbox-card').hidden = false;
    loadInbox(true);
  });

  renderAddress();
  if (email) loadInbox(false);
  setInterval(function(){ if (!document.hidden && email && !openId) loadInbox(true); }, 20000);
})();
</script>
%%SYNC%%<script>if('serviceWorker' in navigator)addEventListener('load',()=>navigator.serviceWorker.register('/sw.js'))</script>
</body>
</html>
'''
PAGE = PAGE.replace('%%THEME%%', THEME).replace('%%SYNC%%', SYNC)
open('tempmail.html', 'w', encoding='utf-8').write(PAGE)
print('tempmail.html   :', 'OK')

# ================= 5. Tambah ke menu Alat =================
f = 'index.html'
s = open(f, encoding='utf-8').read()
if 'data-tool="tempmail.html"' in s:
    print('index.html      : sudah pernah')
else:
    shutil.copy(f, f + '.bak11')
    card = ('<div class="tool-card" data-tool="tempmail.html" role="button" tabindex="0"><span class="tool-icon">'
            '<svg viewBox="0 0 24 24" class="icon"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/></svg>'
            '</span><div><h3>Temp Mail</h3><p>Email sementara, baca pesan masuk tanpa daftar.</p></div></div>')
    m = re.search(r'<div class="tool-card" data-tool="reactch\.html".*?</p></div></div>', s, re.S)
    if m:
        s = s[:m.end()] + '\n  ' + card + s[m.end():]
        s = s.replace('<b>4</b><span>Tools</span>', '<b>5</b><span>Tools</span>')
        open(f, 'w', encoding='utf-8').write(s)
        print('index.html      : OK')
    else:
        print('index.html      : GAGAL (kartu React Channel tidak ketemu)')
