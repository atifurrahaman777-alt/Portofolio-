import shutil

f = 'chat.js'
s = open(f, encoding='utf-8', errors='surrogateescape').read()
if 'openComposer' in s:
    print('Sudah pernah dipasang.')
    raise SystemExit

a = s.find('  async function addStory() {')
b = s.find('  function storyItem(')
if a < 0 or b < 0 or b < a or "prompt('Tulis story" not in s[a:b]:
    print('GAGAL: fungsi story tidak ketemu. Tidak ada yang diubah.')
    raise SystemExit

NEW = r"""  function openComposer(o) {
    const old = $('gc-sheet');
    if (old) old.remove();
    if (!$('gc-sheet-css')) {
      const st = document.createElement('style');
      st.id = 'gc-sheet-css';
      st.textContent = '#gc-sheet textarea::placeholder{color:rgba(255,255,255,.7)}#gc-sheet button{font:inherit;cursor:pointer}';
      document.head.appendChild(st);
    }
    const p0 = profile();
    const light = root.classList.contains('light');
    const C = light
      ? { bg: '#ffffff', fg: '#111b21', mu: '#667781', ln: '#d9dee1', fi: '#f0f2f5' }
      : { bg: '#1f2c33', fg: '#e9edef', mu: '#8696a0', ln: '#2f3f47', fi: '#2a3942' };
    let bg = Math.floor(Math.random() * bgs.length);

    const wrap = el('div');
    wrap.id = 'gc-sheet';
    wrap.style.cssText = 'position:fixed;left:0;right:0;top:0;bottom:0;z-index:60;display:flex;align-items:flex-end;justify-content:center;background:rgba(0,0,0,.55);overscroll-behavior:contain';
    const panel = el('div');
    panel.style.cssText = 'width:100%;max-width:520px;box-sizing:border-box;background:' + C.bg + ';color:' + C.fg + ';border-radius:18px 18px 0 0;padding:16px;max-height:90vh;overflow-y:auto;display:flex;flex-direction:column;gap:12px';

    const head = el('div');
    head.style.cssText = 'display:flex;justify-content:space-between;align-items:center';
    const title = el('b', '', o.title);
    title.style.fontSize = '1.05rem';
    const x = el('button', '', 'Tutup');
    x.type = 'button';
    x.style.cssText = 'background:none;border:none;color:' + C.mu + ';font-weight:700';
    head.append(title, x);
    panel.appendChild(head);

    let nameIn = null;
    if (!p0.name) {
      nameIn = el('input');
      nameIn.type = 'text';
      nameIn.maxLength = 20;
      nameIn.placeholder = 'Nama kamu (maks 20 huruf)';
      nameIn.style.cssText = 'padding:12px;border-radius:12px;border:1px solid ' + C.ln + ';background:' + C.fi + ';color:' + C.fg + ';font:inherit';
      panel.appendChild(nameIn);
    }

    const ta = el('textarea');
    ta.maxLength = o.max;
    ta.rows = o.colors ? 4 : 3;
    ta.placeholder = o.placeholder;
    ta.value = o.initial || '';
    let box = ta;
    if (o.colors) {
      box = el('div');
      box.style.cssText = 'border-radius:16px;padding:18px;min-height:130px;display:flex;align-items:center;justify-content:center;transition:background .2s';
      ta.style.cssText = 'width:100%;box-sizing:border-box;background:transparent;border:none;outline:none;resize:none;color:#fff;text-align:center;font:inherit;font-size:1.25rem;font-weight:700;text-shadow:0 1px 3px rgba(0,0,0,.35)';
      box.appendChild(ta);
      box.style.background = bgs[bg];
    } else {
      ta.style.cssText = 'width:100%;box-sizing:border-box;padding:12px;border-radius:12px;border:1px solid ' + C.ln + ';background:' + C.fi + ';color:' + C.fg + ';font:inherit;resize:none;outline:none';
    }
    panel.appendChild(box);

    const cnt = el('div', '', ta.value.length + '/' + o.max);
    cnt.style.cssText = 'text-align:right;font-size:.78rem;color:' + C.mu;
    ta.addEventListener('input', () => { cnt.textContent = ta.value.length + '/' + o.max; });
    panel.appendChild(cnt);

    if (o.colors) {
      const row = el('div');
      row.style.cssText = 'display:flex;gap:10px;justify-content:center;flex-wrap:wrap';
      const dots = [];
      const mark = () => dots.forEach((d, i) => { d.style.borderColor = i === bg ? C.fg : 'transparent'; });
      bgs.forEach((c, i) => {
        const d = el('button');
        d.type = 'button';
        d.setAttribute('aria-label', 'Warna ' + (i + 1));
        d.style.cssText = 'width:32px;height:32px;border-radius:50%;border:3px solid transparent;background:' + c;
        d.addEventListener('click', () => { bg = i; box.style.background = c; mark(); });
        row.appendChild(d);
        dots.push(d);
      });
      mark();
      panel.appendChild(row);
    }

    const hint = el('div');
    hint.style.cssText = 'min-height:1.2em;font-size:.82rem;color:#ef4444';
    panel.appendChild(hint);

    const acts = el('div');
    acts.style.cssText = 'display:flex;gap:10px';
    const go = el('button', '', o.cta);
    go.type = 'button';
    go.style.cssText = 'flex:1;padding:13px;border-radius:12px;border:none;background:#25d366;color:#052e16;font-weight:800';

    let busy = false;
    const close = () => { wrap.remove(); };
    const submit = async remove => {
      if (busy) return;
      const t = remove ? '' : ta.value.trim();
      let name = p0.name;
      if (!name) {
        name = ((nameIn && nameIn.value) || '').trim().slice(0, 20);
        if (!name) { hint.textContent = 'Isi namamu dulu.'; return; }
      }
      if (!t && !o.allowEmpty) { hint.textContent = 'Tulisannya masih kosong.'; return; }
      busy = true;
      go.disabled = true;
      hint.textContent = '';
      if (!p0.name) ls.set('chat_name', name);
      const ok = await o.send(name, p0.avatar, t, bg);
      busy = false;
      go.disabled = false;
      if (ok) { close(); renderMe(); }
      else hint.textContent = status.textContent || 'Gagal, coba lagi.';
    };

    if (o.removable) {
      const rm = el('button', '', 'Hapus');
      rm.type = 'button';
      rm.style.cssText = 'padding:13px 18px;border-radius:12px;border:1px solid ' + C.ln + ';background:none;color:#ef4444;font-weight:800';
      rm.addEventListener('click', () => submit(true));
      acts.appendChild(rm);
    }
    go.addEventListener('click', () => submit(false));
    acts.appendChild(go);
    panel.appendChild(acts);

    x.addEventListener('click', close);
    wrap.addEventListener('click', e => { if (e.target === wrap) close(); });
    wrap.addEventListener('keydown', e => { if (e.key === 'Escape') close(); });
    ta.addEventListener('keydown', e => {
      if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); submit(false); }
    });
    wrap.appendChild(panel);
    document.body.appendChild(wrap);
    ta.focus();
  }

  function addStory() {
    openComposer({
      title: 'Story baru', cta: 'Kirim story', max: 140, colors: true,
      placeholder: 'Apa yang lagi kamu pikirin?',
      send: async (name, avatar, text, bg) => {
        const ok = await post({ type: 'story', name, avatar, text, bg });
        if (ok) { storySig = null; load(); }
        return ok;
      }
    });
  }
  function addNote(current) {
    openComposer({
      title: 'Catatan', cta: 'Simpan', max: 60, initial: current || '',
      allowEmpty: true, removable: !!current, placeholder: 'Tulis catatan singkat...',
      send: async (name, avatar, text) => {
        const ok = await post({ type: 'note', name, avatar, text });
        if (ok) { noteSig = null; load(); }
        return ok;
      }
    });
  }

"""

shutil.copy(f, f + '.bak39')
s = s[:a] + NEW + s[b:]
open(f, 'w', encoding='utf-8', errors='surrogateescape').write(s)
print('Story dan catatan tanpa pop-up : OK')
