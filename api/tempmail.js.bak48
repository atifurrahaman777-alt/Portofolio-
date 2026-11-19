const cheerio = require('cheerio')

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
